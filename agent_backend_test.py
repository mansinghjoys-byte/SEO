#!/usr/bin/env python3
"""
Agent Backend Testing for Production Readiness
Tests Redis connectivity and complete agent workflow as requested in review
"""

import requests
import json
import sys
import subprocess
from datetime import datetime
import time

# Configuration from review request
BACKEND_URL = "https://auth-redirect-fix-3.preview.emergentagent.com/api"
TEST_USER_CREDENTIALS = {
    "email": "test@rankforge.com",
    "password": "Test@123"
}

class AgentBackendTester:
    def __init__(self):
        self.base_url = BACKEND_URL
        self.user_token = None
        self.headers = {"Content-Type": "application/json"}
        self.test_results = []
        self.user_id = None
        self.site_id = None
        self.agent_id = None
        self.initial_credits = 0
        
    def log_test(self, test_name, success, message, response_data=None):
        """Log test results"""
        status = "✅ PASS" if success else "❌ FAIL"
        print(f"{status} {test_name}: {message}")
        
        self.test_results.append({
            "test": test_name,
            "success": success,
            "message": message,
            "response_data": response_data,
            "timestamp": datetime.now().isoformat()
        })
        
    def test_redis_connectivity(self):
        """Test Redis connectivity and PING"""
        print("\n🔴 Testing Redis Connectivity...")
        
        try:
            # Test Redis PING
            result = subprocess.run(['redis-cli', 'ping'], capture_output=True, text=True, timeout=10)
            
            if result.returncode == 0 and 'PONG' in result.stdout:
                self.log_test(
                    "Redis PING", 
                    True, 
                    "Redis server responding to PING command",
                    {"response": result.stdout.strip()}
                )
                
                # Test Redis queue operations
                try:
                    # Test basic Redis operations
                    set_result = subprocess.run(['redis-cli', 'set', 'test_key', 'test_value'], 
                                              capture_output=True, text=True, timeout=5)
                    get_result = subprocess.run(['redis-cli', 'get', 'test_key'], 
                                              capture_output=True, text=True, timeout=5)
                    del_result = subprocess.run(['redis-cli', 'del', 'test_key'], 
                                              capture_output=True, text=True, timeout=5)
                    
                    if (set_result.returncode == 0 and get_result.returncode == 0 and 
                        'test_value' in get_result.stdout):
                        self.log_test(
                            "Redis Queue Operations", 
                            True, 
                            "Redis SET/GET/DEL operations working correctly"
                        )
                        return True
                    else:
                        self.log_test(
                            "Redis Queue Operations", 
                            False, 
                            "Redis operations failed"
                        )
                except Exception as e:
                    self.log_test("Redis Queue Operations", False, f"Redis operations error: {str(e)}")
                    
            else:
                self.log_test(
                    "Redis PING", 
                    False, 
                    f"Redis PING failed: {result.stderr}"
                )
        except Exception as e:
            self.log_test("Redis Connectivity", False, f"Redis test failed: {str(e)}")
            
        return False
    
    def test_user_login(self):
        """Test user login with specified credentials"""
        print("\n🔐 Testing User Login...")
        
        try:
            response = requests.post(
                f"{self.base_url}/auth/login",
                json=TEST_USER_CREDENTIALS,
                headers=self.headers,
                timeout=30
            )
            
            if response.status_code == 401:
                # Try to register the test user first
                print("   Test user not found, attempting registration...")
                register_data = {
                    "email": TEST_USER_CREDENTIALS["email"],
                    "password": TEST_USER_CREDENTIALS["password"],
                    "full_name": "Test User for Agent Testing"
                }
                
                reg_response = requests.post(
                    f"{self.base_url}/auth/register",
                    json=register_data,
                    headers=self.headers,
                    timeout=30
                )
                
                if reg_response.status_code == 200:
                    print("   Registration successful, now logging in...")
                    # Try login again
                    response = requests.post(
                        f"{self.base_url}/auth/login",
                        json=TEST_USER_CREDENTIALS,
                        headers=self.headers,
                        timeout=30
                    )
                else:
                    print(f"   Registration failed: {reg_response.status_code} - {reg_response.text}")
        
            if response.status_code == 200:
                data = response.json()
                
                if "access_token" in data and "user" in data:
                    self.user_token = data["access_token"]
                    self.headers["Authorization"] = f"Bearer {self.user_token}"
                    
                    user_info = data["user"]
                    self.user_id = user_info.get("user_id")
                    self.initial_credits = user_info.get("credits", 0)
                    
                    self.log_test(
                        "User Login", 
                        True, 
                        f"Successfully logged in as {user_info.get('email')} with {self.initial_credits} credits",
                        {"user_id": self.user_id, "credits": self.initial_credits}
                    )
                    return True
                else:
                    self.log_test(
                        "User Login", 
                        False, 
                        "Missing access_token or user in response"
                    )
            else:
                self.log_test(
                    "User Login", 
                    False, 
                    f"HTTP {response.status_code}: {response.text}"
                )
                
        except requests.exceptions.RequestException as e:
            self.log_test("User Login", False, f"Request failed: {str(e)}")
            
        return False
    
    def test_get_sites(self):
        """Get or create a site for agent testing"""
        print("\n🌐 Getting/Creating Test Site...")
        
        if not self.user_token:
            self.log_test("Get Sites", False, "No user token available")
            return False
            
        try:
            # First try to get existing sites
            response = requests.get(
                f"{self.base_url}/sites/",
                headers=self.headers,
                timeout=30
            )
            
            if response.status_code == 200:
                sites = response.json()
                
                if sites and len(sites) > 0:
                    self.site_id = sites[0]["site_id"]
                    site_url = sites[0]["url"]
                    
                    self.log_test(
                        "Get Sites", 
                        True, 
                        f"Found {len(sites)} sites, using: {site_url}",
                        {"site_id": self.site_id, "site_url": site_url}
                    )
                    return True
                else:
                    # Create a test site
                    return self.create_test_site()
            else:
                self.log_test(
                    "Get Sites", 
                    False, 
                    f"HTTP {response.status_code}: {response.text}"
                )
                
        except requests.exceptions.RequestException as e:
            self.log_test("Get Sites", False, f"Request failed: {str(e)}")
            
        return False
    
    def create_test_site(self):
        """Create a test site for agent testing"""
        try:
            site_data = {
                "url": "https://example-agent-test.com",
                "name": "Test Site for Agent Testing"
            }
            
            response = requests.post(
                f"{self.base_url}/sites/",
                json=site_data,
                headers=self.headers,
                timeout=30
            )
            
            if response.status_code == 200:
                site = response.json()
                self.site_id = site["site_id"]
                
                self.log_test(
                    "Create Test Site", 
                    True, 
                    f"Created test site: {site['url']}",
                    {"site_id": self.site_id}
                )
                return True
            else:
                self.log_test(
                    "Create Test Site", 
                    False, 
                    f"HTTP {response.status_code}: {response.text}"
                )
                
        except requests.exceptions.RequestException as e:
            self.log_test("Create Test Site", False, f"Request failed: {str(e)}")
            
        return False
    
    def test_create_agent(self):
        """Test POST /api/agents/ - Create agent with website"""
        print("\n🤖 Testing Agent Creation...")
        
        if not self.user_token or not self.site_id:
            self.log_test("Create Agent", False, "Missing token or site_id")
            return False
            
        try:
            agent_data = {
                "name": "SEO Assistant for Testing",
                "purpose": "llm_visibility_optimizer",
                "website": "https://example-agent-test.com",
                "context": {
                    "focus_area": "LLM visibility optimization",
                    "testing_mode": True
                }
            }
            
            response = requests.post(
                f"{self.base_url}/agents/",
                json=agent_data,
                headers=self.headers,
                timeout=30
            )
            
            if response.status_code == 200:
                agent = response.json()
                
                required_fields = ["agent_id", "name", "purpose", "website", "active"]
                missing_fields = [field for field in required_fields if field not in agent]
                
                if not missing_fields:
                    self.agent_id = agent["agent_id"]
                    
                    self.log_test(
                        "Create Agent", 
                        True, 
                        f"Created agent '{agent['name']}' for website {agent['website']}",
                        {
                            "agent_id": self.agent_id,
                            "name": agent["name"],
                            "purpose": agent["purpose"],
                            "website": agent["website"]
                        }
                    )
                    return True
                else:
                    self.log_test(
                        "Create Agent", 
                        False, 
                        f"Missing required fields: {missing_fields}"
                    )
            else:
                self.log_test(
                    "Create Agent", 
                    False, 
                    f"HTTP {response.status_code}: {response.text}"
                )
                
        except requests.exceptions.RequestException as e:
            self.log_test("Create Agent", False, f"Request failed: {str(e)}")
            
        return False
    
    def test_agent_chat(self):
        """Test POST /api/agents/chat - Chat with agent (test context loading)"""
        print("\n💬 Testing Agent Chat...")
        
        if not self.user_token or not self.agent_id:
            self.log_test("Agent Chat", False, "Missing token or agent_id")
            return False
            
        try:
            chat_data = {
                "agent_id": self.agent_id,
                "message": "Hello! Can you help me understand my website's current SEO status and provide some recommendations for improving LLM visibility?"
            }
            
            response = requests.post(
                f"{self.base_url}/agents/chat",
                json=chat_data,
                headers=self.headers,
                timeout=60  # Longer timeout for AI processing
            )
            
            if response.status_code == 200:
                chat_response = response.json()
                
                required_fields = ["agent_id", "message"]
                missing_fields = [field for field in required_fields if field not in chat_response]
                
                if not missing_fields and chat_response.get("message"):
                    message_length = len(chat_response["message"])
                    suggestions = chat_response.get("suggestions", [])
                    
                    self.log_test(
                        "Agent Chat", 
                        True, 
                        f"Agent responded with {message_length} characters and {len(suggestions)} suggestions",
                        {
                            "agent_id": chat_response["agent_id"],
                            "message_length": message_length,
                            "suggestions_count": len(suggestions),
                            "has_context": "website" in chat_response["message"].lower() or "seo" in chat_response["message"].lower()
                        }
                    )
                    return True
                else:
                    self.log_test(
                        "Agent Chat", 
                        False, 
                        f"Invalid response structure. Missing: {missing_fields}"
                    )
            elif response.status_code == 402:
                self.log_test(
                    "Agent Chat", 
                    False, 
                    "Insufficient credits for agent chat"
                )
            else:
                self.log_test(
                    "Agent Chat", 
                    False, 
                    f"HTTP {response.status_code}: {response.text}"
                )
                
        except requests.exceptions.RequestException as e:
            self.log_test("Agent Chat", False, f"Request failed: {str(e)}")
            
        return False
    
    def test_agent_history(self):
        """Test GET /api/agents/{agent_id}/history - Get chat history"""
        print("\n📜 Testing Agent History...")
        
        if not self.user_token or not self.agent_id:
            self.log_test("Agent History", False, "Missing token or agent_id")
            return False
            
        try:
            response = requests.get(
                f"{self.base_url}/agents/{self.agent_id}/history",
                headers=self.headers,
                timeout=30
            )
            
            if response.status_code == 200:
                history_data = response.json()
                
                if "history" in history_data:
                    history = history_data["history"]
                    
                    self.log_test(
                        "Agent History", 
                        True, 
                        f"Retrieved chat history with {len(history)} messages",
                        {
                            "history_count": len(history),
                            "has_messages": len(history) > 0
                        }
                    )
                    return True
                else:
                    self.log_test(
                        "Agent History", 
                        False, 
                        "Missing 'history' field in response"
                    )
            else:
                self.log_test(
                    "Agent History", 
                    False, 
                    f"HTTP {response.status_code}: {response.text}"
                )
                
        except requests.exceptions.RequestException as e:
            self.log_test("Agent History", False, f"Request failed: {str(e)}")
            
        return False
    
    def test_list_agents(self):
        """Test GET /api/agents/ - List all agents"""
        print("\n📋 Testing List Agents...")
        
        if not self.user_token:
            self.log_test("List Agents", False, "No user token available")
            return False
            
        try:
            response = requests.get(
                f"{self.base_url}/agents/",
                headers=self.headers,
                timeout=30
            )
            
            if response.status_code == 200:
                agents = response.json()
                
                if isinstance(agents, list):
                    # Find our created agent
                    our_agent = None
                    if self.agent_id:
                        our_agent = next((a for a in agents if a.get("agent_id") == self.agent_id), None)
                    
                    self.log_test(
                        "List Agents", 
                        True, 
                        f"Retrieved {len(agents)} agents, our agent found: {our_agent is not None}",
                        {
                            "total_agents": len(agents),
                            "our_agent_found": our_agent is not None
                        }
                    )
                    return True
                else:
                    self.log_test(
                        "List Agents", 
                        False, 
                        "Response is not a list"
                    )
            else:
                self.log_test(
                    "List Agents", 
                    False, 
                    f"HTTP {response.status_code}: {response.text}"
                )
                
        except requests.exceptions.RequestException as e:
            self.log_test("List Agents", False, f"Request failed: {str(e)}")
            
        return False
    
    def test_core_seo_endpoints(self):
        """Quick sanity check of core SEO endpoints"""
        print("\n🔍 Testing Core SEO Endpoints (Sanity Check)...")
        
        if not self.user_token:
            self.log_test("Core SEO Endpoints", False, "No user token available")
            return False
        
        endpoints_tested = 0
        endpoints_passed = 0
        
        # Test GET /api/sites/
        try:
            response = requests.get(f"{self.base_url}/sites/", headers=self.headers, timeout=30)
            endpoints_tested += 1
            if response.status_code == 200:
                endpoints_passed += 1
        except:
            endpoints_tested += 1
        
        # Test GET /api/audits/
        try:
            response = requests.get(f"{self.base_url}/audits/", headers=self.headers, timeout=30)
            endpoints_tested += 1
            if response.status_code == 200:
                endpoints_passed += 1
        except:
            endpoints_tested += 1
        
        if endpoints_passed >= endpoints_tested * 0.5:  # At least 50% should work
            self.log_test(
                "Core SEO Endpoints", 
                True, 
                f"Core endpoints working: {endpoints_passed}/{endpoints_tested}",
                {"endpoints_passed": endpoints_passed, "endpoints_tested": endpoints_tested}
            )
            return True
        else:
            self.log_test(
                "Core SEO Endpoints", 
                False, 
                f"Too many core endpoints failing: {endpoints_passed}/{endpoints_tested}"
            )
            return False
    
    def test_delete_agent(self):
        """Test DELETE /api/agents/{agent_id} - Delete agent"""
        print("\n🗑️ Testing Agent Deletion...")
        
        if not self.user_token or not self.agent_id:
            self.log_test("Delete Agent", False, "Missing token or agent_id")
            return False
            
        try:
            response = requests.delete(
                f"{self.base_url}/agents/{self.agent_id}",
                headers=self.headers,
                timeout=30
            )
            
            if response.status_code == 200:
                result = response.json()
                
                if "message" in result:
                    self.log_test(
                        "Delete Agent", 
                        True, 
                        f"Agent deleted successfully: {result['message']}",
                        {"agent_id": self.agent_id}
                    )
                    return True
                else:
                    self.log_test(
                        "Delete Agent", 
                        False, 
                        "Missing success message in response"
                    )
            else:
                self.log_test(
                    "Delete Agent", 
                    False, 
                    f"HTTP {response.status_code}: {response.text}"
                )
                
        except requests.exceptions.RequestException as e:
            self.log_test("Delete Agent", False, f"Request failed: {str(e)}")
            
        return False
    
    def check_backend_logs(self):
        """Check backend logs for any errors"""
        print("\n📋 Checking Backend Logs...")
        
        try:
            # Check supervisor backend logs
            result = subprocess.run(
                ['tail', '-n', '50', '/var/log/supervisor/backend.err.log'], 
                capture_output=True, text=True, timeout=10
            )
            
            if result.returncode == 0:
                error_lines = [line for line in result.stdout.split('\n') if 'ERROR' in line.upper() or 'EXCEPTION' in line.upper()]
                
                if len(error_lines) == 0:
                    self.log_test(
                        "Backend Logs Check", 
                        True, 
                        "No recent errors found in backend logs"
                    )
                    return True
                else:
                    self.log_test(
                        "Backend Logs Check", 
                        False, 
                        f"Found {len(error_lines)} error lines in recent logs"
                    )
            else:
                self.log_test(
                    "Backend Logs Check", 
                    False, 
                    "Could not read backend logs"
                )
                
        except Exception as e:
            self.log_test("Backend Logs Check", False, f"Log check failed: {str(e)}")
            
        return False
    
    def run_all_tests(self):
        """Run all agent backend tests as specified in review request"""
        print("🚀 Starting Agent Backend Production Readiness Tests")
        print(f"🌐 Backend URL: {self.base_url}")
        print(f"👤 Test User: {TEST_USER_CREDENTIALS['email']}")
        print("=" * 80)
        
        test_results = []
        
        # 1. Redis Connectivity (Critical Infrastructure)
        test_results.append(self.test_redis_connectivity())
        
        # 2. User Authentication (Required for all other tests)
        if not self.test_user_login():
            print("❌ Cannot proceed without authentication")
            return 0, 1, self.test_results
        
        # 3. Get/Create Sites (Required for agent testing)
        if not self.test_get_sites():
            print("❌ Cannot proceed without site data")
            return 1, 2, self.test_results
        
        # 4. Core SEO Endpoints (Quick sanity check)
        test_results.append(self.test_core_seo_endpoints())
        
        # 5. Agent Endpoints (Main focus of review)
        test_results.append(self.test_create_agent())
        test_results.append(self.test_agent_chat())
        test_results.append(self.test_agent_history())
        test_results.append(self.test_list_agents())
        test_results.append(self.test_delete_agent())
        
        # 6. Backend Health Check
        test_results.append(self.check_backend_logs())
        
        # Calculate results
        tests_passed = sum(1 for result in test_results if result)
        total_tests = len(test_results)
        
        # Summary
        print("\n" + "=" * 80)
        print("📊 AGENT BACKEND PRODUCTION READINESS TEST SUMMARY")
        print("=" * 80)
        print(f"✅ Tests Passed: {tests_passed}/{total_tests}")
        print(f"❌ Tests Failed: {total_tests - tests_passed}/{total_tests}")
        
        if tests_passed == total_tests:
            print("🎉 ALL AGENT TESTS PASSED! System is production ready.")
        elif tests_passed >= total_tests * 0.8:
            print("✅ Most tests passed. Minor issues may need attention.")
        else:
            print("⚠️  Multiple tests failed. System needs attention before production.")
            
        return tests_passed, total_tests, self.test_results

def main():
    """Main test execution"""
    tester = AgentBackendTester()
    passed, total, results = tester.run_all_tests()
    
    # Save detailed results
    with open('/app/agent_test_results.json', 'w') as f:
        json.dump({
            'summary': {
                'passed': passed,
                'total': total,
                'success_rate': f"{(passed/total)*100:.1f}%" if total > 0 else "0%"
            },
            'results': results,
            'timestamp': datetime.now().isoformat()
        }, f, indent=2)
    
    print(f"\n📄 Detailed results saved to: /app/agent_test_results.json")
    
    # Exit with appropriate code
    sys.exit(0 if passed == total else 1)

if __name__ == "__main__":
    main()