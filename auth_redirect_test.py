#!/usr/bin/env python3
"""
Authentication and Routing Fix Testing
Tests the critical FastAPI 307 redirect fixes for sites and agents endpoints
"""

import requests
import json
import sys
from datetime import datetime
import time

# Configuration
BACKEND_URL = "https://seo-rival-scan.preview.emergentagent.com/api"
TEST_USER_CREDENTIALS = {
    "email": "tester@test.com",
    "password": "Test123!@#",
    "full_name": "Test User"
}

class AuthRedirectTester:
    def __init__(self):
        self.base_url = BACKEND_URL
        self.user_token = None
        self.headers = {"Content-Type": "application/json"}
        self.test_results = []
        self.user_id = None
        self.site_id = None
        self.agent_id = None
        
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
        
    def check_for_redirects(self, response):
        """Check if response contains any redirect status codes"""
        if response.status_code == 307:
            return True, "307 Temporary Redirect detected"
        elif response.status_code in [301, 302, 303, 308]:
            return True, f"{response.status_code} redirect detected"
        elif response.history:
            redirect_codes = [r.status_code for r in response.history]
            if any(code in [301, 302, 303, 307, 308] for code in redirect_codes):
                return True, f"Redirect chain detected: {redirect_codes}"
        return False, "No redirects"
        
    def test_user_register_and_login(self):
        """Test 1: Register and login a test user"""
        print("\n🔐 Test 1: User Registration and Login...")
        
        # First try to register the user
        try:
            register_data = {
                "email": TEST_USER_CREDENTIALS["email"],
                "password": TEST_USER_CREDENTIALS["password"],
                "full_name": TEST_USER_CREDENTIALS["full_name"]
            }
            
            response = requests.post(
                f"{self.base_url}/auth/register",
                json=register_data,
                headers=self.headers,
                timeout=30,
                allow_redirects=False  # Don't follow redirects automatically
            )
            
            # Check for redirects
            has_redirect, redirect_msg = self.check_for_redirects(response)
            if has_redirect:
                self.log_test(
                    "User Registration", 
                    False, 
                    f"Registration failed due to redirect: {redirect_msg}"
                )
                return False
            
            if response.status_code == 400:
                # User might already exist, try login
                print("   User already exists, attempting login...")
                
                login_response = requests.post(
                    f"{self.base_url}/auth/login",
                    json={
                        "email": TEST_USER_CREDENTIALS["email"],
                        "password": TEST_USER_CREDENTIALS["password"]
                    },
                    headers=self.headers,
                    timeout=30,
                    allow_redirects=False
                )
                
                # Check for redirects in login
                has_redirect, redirect_msg = self.check_for_redirects(login_response)
                if has_redirect:
                    self.log_test(
                        "User Login", 
                        False, 
                        f"Login failed due to redirect: {redirect_msg}"
                    )
                    return False
                
                response = login_response
            
            if response.status_code == 200:
                data = response.json()
                
                if "access_token" in data and "user" in data:
                    self.user_token = data["access_token"]
                    self.headers["Authorization"] = f"Bearer {self.user_token}"
                    
                    user_info = data["user"]
                    self.user_id = user_info.get("user_id")
                    
                    self.log_test(
                        "User Registration/Login", 
                        True, 
                        f"Successfully authenticated as {user_info.get('email')} with token",
                        {"token_received": True, "user_id": self.user_id}
                    )
                    return True
                else:
                    self.log_test(
                        "User Registration/Login", 
                        False, 
                        "Missing access_token or user in response"
                    )
            else:
                self.log_test(
                    "User Registration/Login", 
                    False, 
                    f"HTTP {response.status_code}: {response.text}"
                )
                
        except requests.exceptions.RequestException as e:
            self.log_test("User Registration/Login", False, f"Request failed: {str(e)}")
            
        return False
    
    def test_auth_me_endpoint(self):
        """Test 2: Test /api/auth/me endpoint"""
        print("\n👤 Test 2: Auth Me Endpoint...")
        
        if not self.user_token:
            self.log_test("Auth Me Endpoint", False, "No user token available")
            return False
            
        try:
            response = requests.get(
                f"{self.base_url}/auth/me",
                headers=self.headers,
                timeout=30,
                allow_redirects=False
            )
            
            # Check for redirects
            has_redirect, redirect_msg = self.check_for_redirects(response)
            if has_redirect:
                self.log_test(
                    "Auth Me Endpoint", 
                    False, 
                    f"Auth me failed due to redirect: {redirect_msg}"
                )
                return False
            
            if response.status_code == 200:
                user_data = response.json()
                
                if "user_id" in user_data and "email" in user_data:
                    self.log_test(
                        "Auth Me Endpoint", 
                        True, 
                        f"Successfully retrieved user data for {user_data.get('email')}",
                        {"user_data": user_data}
                    )
                    return True
                else:
                    self.log_test(
                        "Auth Me Endpoint", 
                        False, 
                        "Invalid user data structure in response"
                    )
            else:
                self.log_test(
                    "Auth Me Endpoint", 
                    False, 
                    f"HTTP {response.status_code}: {response.text}"
                )
                
        except requests.exceptions.RequestException as e:
            self.log_test("Auth Me Endpoint", False, f"Request failed: {str(e)}")
            
        return False
    
    def test_sites_without_trailing_slash(self):
        """Test 3: Test /api/sites WITHOUT trailing slash (MAIN ISSUE)"""
        print("\n🌐 Test 3: Sites WITHOUT Trailing Slash (CRITICAL)...")
        
        if not self.user_token:
            self.log_test("Sites Without Trailing Slash", False, "No user token available")
            return False
            
        try:
            response = requests.get(
                f"{self.base_url}/sites",  # NO trailing slash
                headers=self.headers,
                timeout=30,
                allow_redirects=False  # Critical: don't follow redirects
            )
            
            # Check for redirects - this was the MAIN ISSUE
            has_redirect, redirect_msg = self.check_for_redirects(response)
            if has_redirect:
                self.log_test(
                    "Sites Without Trailing Slash", 
                    False, 
                    f"❌ CRITICAL: 307 redirect still occurring! {redirect_msg}"
                )
                return False
            
            if response.status_code == 200:
                sites = response.json()
                
                self.log_test(
                    "Sites Without Trailing Slash", 
                    True, 
                    f"✅ SUCCESS: No 307 redirect! Returned {len(sites)} sites",
                    {"sites_count": len(sites), "no_redirect": True}
                )
                return True
            else:
                self.log_test(
                    "Sites Without Trailing Slash", 
                    False, 
                    f"HTTP {response.status_code}: {response.text}"
                )
                
        except requests.exceptions.RequestException as e:
            self.log_test("Sites Without Trailing Slash", False, f"Request failed: {str(e)}")
            
        return False
    
    def test_sites_with_trailing_slash(self):
        """Test 4: Test /api/sites WITH trailing slash"""
        print("\n🌐 Test 4: Sites WITH Trailing Slash...")
        
        if not self.user_token:
            self.log_test("Sites With Trailing Slash", False, "No user token available")
            return False
            
        try:
            response = requests.get(
                f"{self.base_url}/sites/",  # WITH trailing slash
                headers=self.headers,
                timeout=30,
                allow_redirects=False
            )
            
            # Check for redirects
            has_redirect, redirect_msg = self.check_for_redirects(response)
            if has_redirect:
                self.log_test(
                    "Sites With Trailing Slash", 
                    False, 
                    f"Unexpected redirect: {redirect_msg}"
                )
                return False
            
            if response.status_code == 200:
                sites = response.json()
                
                self.log_test(
                    "Sites With Trailing Slash", 
                    True, 
                    f"Successfully returned {len(sites)} sites with trailing slash",
                    {"sites_count": len(sites), "no_redirect": True}
                )
                return True
            else:
                self.log_test(
                    "Sites With Trailing Slash", 
                    False, 
                    f"HTTP {response.status_code}: {response.text}"
                )
                
        except requests.exceptions.RequestException as e:
            self.log_test("Sites With Trailing Slash", False, f"Request failed: {str(e)}")
            
        return False
    
    def test_create_site(self):
        """Test 5: Create a site"""
        print("\n🏗️ Test 5: Create Site...")
        
        if not self.user_token:
            self.log_test("Create Site", False, "No user token available")
            return False
            
        try:
            site_data = {
                "url": "https://example.com",
                "name": "Test Site"
            }
            
            response = requests.post(
                f"{self.base_url}/sites",  # Test without trailing slash
                json=site_data,
                headers=self.headers,
                timeout=30,
                allow_redirects=False
            )
            
            # Check for redirects
            has_redirect, redirect_msg = self.check_for_redirects(response)
            if has_redirect:
                self.log_test(
                    "Create Site", 
                    False, 
                    f"Site creation failed due to redirect: {redirect_msg}"
                )
                return False
            
            if response.status_code == 200:
                site = response.json()
                self.site_id = site.get("site_id")
                
                self.log_test(
                    "Create Site", 
                    True, 
                    f"Successfully created site: {site.get('url')}",
                    {"site_id": self.site_id, "site_url": site.get("url")}
                )
                return True
            elif response.status_code == 400 and "already added" in response.text:
                # Site already exists, get existing sites
                sites_response = requests.get(
                    f"{self.base_url}/sites",
                    headers=self.headers,
                    timeout=30,
                    allow_redirects=False
                )
                
                if sites_response.status_code == 200:
                    sites = sites_response.json()
                    if sites:
                        self.site_id = sites[0]["site_id"]
                        self.log_test(
                            "Create Site", 
                            True, 
                            f"Site already exists, using existing site: {sites[0]['url']}",
                            {"site_id": self.site_id, "site_url": sites[0]["url"]}
                        )
                        return True
                
                self.log_test(
                    "Create Site", 
                    False, 
                    "Site already exists but couldn't retrieve existing sites"
                )
            else:
                self.log_test(
                    "Create Site", 
                    False, 
                    f"HTTP {response.status_code}: {response.text}"
                )
                
        except requests.exceptions.RequestException as e:
            self.log_test("Create Site", False, f"Request failed: {str(e)}")
            
        return False
    
    def test_agents_without_trailing_slash(self):
        """Test 6: Test /api/agents WITHOUT trailing slash"""
        print("\n🤖 Test 6: Agents WITHOUT Trailing Slash...")
        
        if not self.user_token:
            self.log_test("Agents Without Trailing Slash", False, "No user token available")
            return False
            
        try:
            response = requests.get(
                f"{self.base_url}/agents",  # NO trailing slash
                headers=self.headers,
                timeout=30,
                allow_redirects=False
            )
            
            # Check for redirects
            has_redirect, redirect_msg = self.check_for_redirects(response)
            if has_redirect:
                self.log_test(
                    "Agents Without Trailing Slash", 
                    False, 
                    f"Agents endpoint failed due to redirect: {redirect_msg}"
                )
                return False
            
            if response.status_code == 200:
                agents = response.json()
                
                self.log_test(
                    "Agents Without Trailing Slash", 
                    True, 
                    f"Successfully returned {len(agents)} agents without trailing slash",
                    {"agents_count": len(agents), "no_redirect": True}
                )
                return True
            else:
                self.log_test(
                    "Agents Without Trailing Slash", 
                    False, 
                    f"HTTP {response.status_code}: {response.text}"
                )
                
        except requests.exceptions.RequestException as e:
            self.log_test("Agents Without Trailing Slash", False, f"Request failed: {str(e)}")
            
        return False
    
    def test_agents_with_trailing_slash(self):
        """Test 7: Test /api/agents WITH trailing slash"""
        print("\n🤖 Test 7: Agents WITH Trailing Slash...")
        
        if not self.user_token:
            self.log_test("Agents With Trailing Slash", False, "No user token available")
            return False
            
        try:
            response = requests.get(
                f"{self.base_url}/agents/",  # WITH trailing slash
                headers=self.headers,
                timeout=30,
                allow_redirects=False
            )
            
            # Check for redirects
            has_redirect, redirect_msg = self.check_for_redirects(response)
            if has_redirect:
                self.log_test(
                    "Agents With Trailing Slash", 
                    False, 
                    f"Agents endpoint failed due to redirect: {redirect_msg}"
                )
                return False
            
            if response.status_code == 200:
                agents = response.json()
                
                self.log_test(
                    "Agents With Trailing Slash", 
                    True, 
                    f"Successfully returned {len(agents)} agents with trailing slash",
                    {"agents_count": len(agents), "no_redirect": True}
                )
                return True
            else:
                self.log_test(
                    "Agents With Trailing Slash", 
                    False, 
                    f"HTTP {response.status_code}: {response.text}"
                )
                
        except requests.exceptions.RequestException as e:
            self.log_test("Agents With Trailing Slash", False, f"Request failed: {str(e)}")
            
        return False
    
    def test_create_agent(self):
        """Test 8: Create agent for the test site"""
        print("\n🤖 Test 8: Create Agent...")
        
        if not self.user_token or not self.site_id:
            self.log_test("Create Agent", False, "Missing token or site_id")
            return False
            
        try:
            agent_data = {
                "name": "Test Agent",
                "purpose": "llm_visibility_optimizer",
                "website": "https://example.com"
            }
            
            response = requests.post(
                f"{self.base_url}/agents",  # Test without trailing slash
                json=agent_data,
                headers=self.headers,
                timeout=30,
                allow_redirects=False
            )
            
            # Check for redirects
            has_redirect, redirect_msg = self.check_for_redirects(response)
            if has_redirect:
                self.log_test(
                    "Create Agent", 
                    False, 
                    f"Agent creation failed due to redirect: {redirect_msg}"
                )
                return False
            
            if response.status_code == 200:
                agent = response.json()
                self.agent_id = agent.get("agent_id")
                
                self.log_test(
                    "Create Agent", 
                    True, 
                    f"Successfully created agent: {agent.get('name')} for {agent.get('website')}",
                    {"agent_id": self.agent_id, "agent_name": agent.get("name")}
                )
                return True
            else:
                self.log_test(
                    "Create Agent", 
                    False, 
                    f"HTTP {response.status_code}: {response.text}"
                )
                
        except requests.exceptions.RequestException as e:
            self.log_test("Create Agent", False, f"Request failed: {str(e)}")
            
        return False
    
    def test_agent_chat_endpoint(self):
        """Test 9: Test agent chat endpoint"""
        print("\n💬 Test 9: Agent Chat Endpoint...")
        
        if not self.user_token or not self.agent_id:
            self.log_test("Agent Chat Endpoint", False, "Missing token or agent_id")
            return False
            
        try:
            chat_data = {
                "agent_id": self.agent_id,
                "message": "Hello, what can you help me with?"
            }
            
            response = requests.post(
                f"{self.base_url}/agents/chat",
                json=chat_data,
                headers=self.headers,
                timeout=60,  # Longer timeout for AI processing
                allow_redirects=False
            )
            
            # Check for redirects
            has_redirect, redirect_msg = self.check_for_redirects(response)
            if has_redirect:
                self.log_test(
                    "Agent Chat Endpoint", 
                    False, 
                    f"Agent chat failed due to redirect: {redirect_msg}"
                )
                return False
            
            if response.status_code == 200:
                chat_response = response.json()
                
                if "message" in chat_response:
                    self.log_test(
                        "Agent Chat Endpoint", 
                        True, 
                        f"Successfully received chat response from agent",
                        {
                            "agent_id": self.agent_id,
                            "response_received": True,
                            "has_suggestions": "suggestions" in chat_response
                        }
                    )
                    return True
                else:
                    self.log_test(
                        "Agent Chat Endpoint", 
                        False, 
                        "Invalid chat response structure"
                    )
            elif response.status_code == 402:
                self.log_test(
                    "Agent Chat Endpoint", 
                    False, 
                    "Insufficient credits for chat (expected if user has no credits)"
                )
            else:
                self.log_test(
                    "Agent Chat Endpoint", 
                    False, 
                    f"HTTP {response.status_code}: {response.text}"
                )
                
        except requests.exceptions.RequestException as e:
            self.log_test("Agent Chat Endpoint", False, f"Request failed: {str(e)}")
            
        return False
    
    def verify_no_redirects_summary(self):
        """Test 10: Confirm no redirects in responses"""
        print("\n🔍 Test 10: Verify No 307 Redirects Summary...")
        
        # Count tests that had redirects
        redirect_failures = [
            result for result in self.test_results 
            if not result["success"] and ("redirect" in result["message"].lower() or "307" in result["message"])
        ]
        
        total_tests = len(self.test_results)
        redirect_count = len(redirect_failures)
        
        if redirect_count == 0:
            self.log_test(
                "No 307 Redirects Verification", 
                True, 
                f"✅ SUCCESS: No 307 redirects detected in any of the {total_tests} tests",
                {"total_tests": total_tests, "redirect_failures": 0}
            )
            return True
        else:
            failed_tests = [f["test"] for f in redirect_failures]
            self.log_test(
                "No 307 Redirects Verification", 
                False, 
                f"❌ FAILED: {redirect_count} tests still have redirect issues: {failed_tests}",
                {"total_tests": total_tests, "redirect_failures": redirect_count, "failed_tests": failed_tests}
            )
            return False
    
    def run_all_tests(self):
        """Run all authentication and routing fix tests"""
        print("🚀 Starting Authentication & Routing Fix Tests")
        print(f"🌐 Backend URL: {self.base_url}")
        print(f"👤 Test User: {TEST_USER_CREDENTIALS['email']}")
        print("🎯 Focus: Testing FastAPI 307 redirect fixes")
        print("=" * 80)
        
        # Test sequence based on review request priorities
        test_results = []
        
        # Priority 1: Authentication Tests
        if not self.test_user_register_and_login():
            print("❌ Cannot proceed without authentication")
            return 0, 1, self.test_results
        
        test_results.append(self.test_auth_me_endpoint())
        
        # Priority 2: Sites API Tests (MAIN ISSUE)
        test_results.append(self.test_sites_without_trailing_slash())  # CRITICAL TEST
        test_results.append(self.test_sites_with_trailing_slash())
        test_results.append(self.test_create_site())
        
        # Priority 3: Agents API Tests
        test_results.append(self.test_agents_without_trailing_slash())
        test_results.append(self.test_agents_with_trailing_slash())
        test_results.append(self.test_create_agent())
        test_results.append(self.test_agent_chat_endpoint())
        
        # Priority 4: Verification
        test_results.append(self.verify_no_redirects_summary())
        
        # Calculate results
        tests_passed = sum(1 for result in test_results if result)
        total_tests = len(test_results)
        
        # Summary
        print("\n" + "=" * 80)
        print("📊 AUTHENTICATION & ROUTING FIX TEST SUMMARY")
        print("=" * 80)
        print(f"✅ Tests Passed: {tests_passed}/{total_tests}")
        print(f"❌ Tests Failed: {total_tests - tests_passed}/{total_tests}")
        
        if tests_passed == total_tests:
            print("🎉 ALL TESTS PASSED! FastAPI 307 redirect fixes are working correctly.")
            print("✅ Authentication headers are preserved")
            print("✅ No 307 redirects occurring")
            print("✅ Both trailing slash variants work")
        elif tests_passed >= total_tests * 0.8:
            print("✅ Most tests passed. Minor issues may need attention.")
        else:
            print("⚠️  Multiple tests failed. 307 redirect issues may still exist.")
            
        return tests_passed, total_tests, self.test_results

def main():
    """Main test execution"""
    tester = AuthRedirectTester()
    passed, total, results = tester.run_all_tests()
    
    # Save detailed results
    with open('/app/auth_redirect_test_results.json', 'w') as f:
        json.dump({
            'summary': {
                'passed': passed,
                'total': total,
                'success_rate': f"{(passed/total)*100:.1f}%" if total > 0 else "0%",
                'focus': 'FastAPI 307 redirect fixes for sites and agents endpoints'
            },
            'results': results,
            'timestamp': datetime.now().isoformat()
        }, f, indent=2)
    
    print(f"\n📄 Detailed results saved to: /app/auth_redirect_test_results.json")
    
    # Exit with appropriate code
    sys.exit(0 if passed == total else 1)

if __name__ == "__main__":
    main()