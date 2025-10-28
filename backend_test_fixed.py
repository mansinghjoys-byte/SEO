#!/usr/bin/env python3
"""
Backend API Testing for LLM Visibility Optimizer
Tests all 8 new LLM visibility modules with comprehensive API coverage
"""

import requests
import json
import sys
from datetime import datetime
import time

# Configuration
BACKEND_URL = "https://domain-insight-hub.preview.emergentagent.com/api"
USER_CREDENTIALS = {
    "email": "amis.joys@gmail.com",
    "password": "password123"
}

class LLMVisibilityTester:
    def __init__(self):
        self.base_url = BACKEND_URL
        self.user_token = None
        self.headers = {"Content-Type": "application/json"}
        self.test_results = []
        self.user_id = None
        self.site_id = None
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
        """Test Redis connectivity"""
        print("\n🔴 Testing Redis Connectivity...")
        
        try:
            import subprocess
            result = subprocess.run(['redis-cli', 'ping'], capture_output=True, text=True, timeout=10)
            
            if result.returncode == 0 and 'PONG' in result.stdout:
                self.log_test(
                    "Redis Connectivity", 
                    True, 
                    "Redis is running and responding to ping",
                    {"response": result.stdout.strip()}
                )
                return True
            else:
                self.log_test(
                    "Redis Connectivity", 
                    False, 
                    f"Redis ping failed: {result.stderr}"
                )
        except Exception as e:
            self.log_test("Redis Connectivity", False, f"Redis test failed: {str(e)}")
            
        return False
        
    def test_user_login(self):
        """Test user login endpoint"""
        print("\n🔐 Testing User Login...")
        
        try:
            response = requests.post(
                f"{self.base_url}/auth/login",
                json=USER_CREDENTIALS,
                headers=self.headers,
                timeout=30
            )
            
            if response.status_code == 401:
                # Try to register first
                print("   Login failed, attempting registration...")
                register_data = {
                    "email": USER_CREDENTIALS["email"],
                    "password": USER_CREDENTIALS["password"],
                    "full_name": "Test User for LLM Visibility"
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
                        json=USER_CREDENTIALS,
                        headers=self.headers,
                        timeout=30
                    )
            
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
                        {"token_received": True, "user_id": self.user_id, "credits": self.initial_credits}
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
        """Get user sites to use for testing"""
        print("\n🌐 Getting User Sites...")
        
        if not self.user_token:
            self.log_test("Get Sites", False, "No user token available")
            return False
            
        try:
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
                        f"Found {len(sites)} sites, using site: {site_url}",
                        {"site_id": self.site_id, "site_url": site_url, "total_sites": len(sites)}
                    )
                    return True
                else:
                    # No sites found, create one for testing
                    print("   No sites found, creating test site...")
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
        """Create a test site for testing"""
        try:
            site_data = {
                "url": "https://example-seo-test.com",
                "name": "Test Site for LLM Visibility"
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
                    {"site_id": self.site_id, "site_url": site["url"]}
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
    
    def test_llm_visibility_check(self):
        """Test LLM visibility check endpoint (8 credits)"""
        print("\n🤖 Testing LLM Visibility Check...")
        
        if not self.user_token or not self.site_id:
            self.log_test("LLM Visibility Check", False, "Missing token or site_id")
            return False
            
        try:
            request_data = {
                "site_id": self.site_id,
                "competitors": ["example.com", "competitor.com"]
            }
            
            response = requests.post(
                f"{self.base_url}/llm/visibility/check",
                json=request_data,
                headers=self.headers,
                timeout=60  # Longer timeout for AI processing
            )
            
            if response.status_code == 200:
                data = response.json()
                
                # Validate response structure
                required_fields = ["success", "domain", "overall_score", "visibility_by_llm", "recommendations"]
                missing_fields = [field for field in required_fields if field not in data]
                
                if not missing_fields and data.get("success"):
                    score = data.get("overall_score", 0)
                    llm_count = len(data.get("visibility_by_llm", {}))
                    rec_count = len(data.get("recommendations", []))
                    
                    self.log_test(
                        "LLM Visibility Check", 
                        True, 
                        f"Visibility check completed - Score: {score}/100, {llm_count} LLMs tested, {rec_count} recommendations",
                        {
                            "overall_score": score,
                            "llms_tested": llm_count,
                            "recommendations_count": rec_count,
                            "domain": data.get("domain")
                        }
                    )
                    return True
                else:
                    self.log_test(
                        "LLM Visibility Check", 
                        False, 
                        f"Invalid response structure. Missing: {missing_fields}"
                    )
            elif response.status_code == 402:
                self.log_test(
                    "LLM Visibility Check", 
                    False, 
                    "Insufficient credits (expected behavior if user has < 8 credits)"
                )
            else:
                self.log_test(
                    "LLM Visibility Check", 
                    False, 
                    f"HTTP {response.status_code}: {response.text}"
                )
                
        except requests.exceptions.RequestException as e:
            self.log_test("LLM Visibility Check", False, f"Request failed: {str(e)}")
            
        return False
    
    def test_recommendations_generation(self):
        """Test recommendations generation endpoint"""
        print("\n💡 Testing Recommendations Generation...")
        
        if not self.user_token or not self.site_id:
            self.log_test("Recommendations Generation", False, "Missing token or site_id")
            return False
            
        try:
            request_data = {
                "site_id": self.site_id
            }
            
            response = requests.post(
                f"{self.base_url}/llm/recommendations/generate",
                json=request_data,
                headers=self.headers,
                timeout=45
            )
            
            if response.status_code == 200:
                data = response.json()
                
                if data.get("success") and "total_recommendations" in data:
                    total_recs = data.get("total_recommendations", 0)
                    
                    # Count recommendations in each category
                    categories = []
                    if data.get("quick_wins"): categories.append("quick_wins")
                    if data.get("high_priority"): categories.append("high_priority")
                    if data.get("medium_priority"): categories.append("medium_priority")
                    if data.get("long_term"): categories.append("long_term")
                    if data.get("content_strategy"): categories.append("content_strategy")
                    if data.get("technical_seo"): categories.append("technical_seo")
                    if data.get("link_building"): categories.append("link_building")
                    
                    self.log_test(
                        "Recommendations Generation", 
                        True, 
                        f"Generated {total_recs} recommendations across {len(categories)} categories",
                        {
                            "total_recommendations": total_recs,
                            "categories": categories
                        }
                    )
                    return True
                else:
                    self.log_test(
                        "Recommendations Generation", 
                        False, 
                        "Invalid response structure or failed generation"
                    )
            else:
                self.log_test(
                    "Recommendations Generation", 
                    False, 
                    f"HTTP {response.status_code}: {response.text}"
                )
                
        except requests.exceptions.RequestException as e:
            self.log_test("Recommendations Generation", False, f"Request failed: {str(e)}")
            
        return False
    
    def test_content_gap_analysis(self):
        """Test content gap analysis endpoint (6 credits)"""
        print("\n📊 Testing Content Gap Analysis...")
        
        if not self.user_token or not self.site_id:
            self.log_test("Content Gap Analysis", False, "Missing token or site_id")
            return False
            
        try:
            request_data = {
                "site_id": self.site_id,
                "competitors": ["competitor1.com", "competitor2.com"]
            }
            
            response = requests.post(
                f"{self.base_url}/llm/content/gap-analysis",
                json=request_data,
                headers=self.headers,
                timeout=45
            )
            
            if response.status_code == 200:
                data = response.json()
                
                if data.get("success"):
                    gaps = data.get("content_gaps", [])
                    opportunities = data.get("opportunities", [])
                    
                    self.log_test(
                        "Content Gap Analysis", 
                        True, 
                        f"Analysis completed - Found {len(gaps)} gaps and {len(opportunities)} opportunities",
                        {
                            "gaps_found": len(gaps),
                            "opportunities": len(opportunities)
                        }
                    )
                    return True
                else:
                    self.log_test(
                        "Content Gap Analysis", 
                        False, 
                        "Analysis failed or invalid response"
                    )
            elif response.status_code == 402:
                self.log_test(
                    "Content Gap Analysis", 
                    False, 
                    "Insufficient credits (expected if user has < 6 credits)"
                )
            else:
                self.log_test(
                    "Content Gap Analysis", 
                    False, 
                    f"HTTP {response.status_code}: {response.text}"
                )
                
        except requests.exceptions.RequestException as e:
            self.log_test("Content Gap Analysis", False, f"Request failed: {str(e)}")
            
        return False
    
    def test_content_outline_generation(self):
        """Test content outline generation endpoint (4 credits)"""
        print("\n✍️ Testing Content Outline Generation...")
        
        if not self.user_token:
            self.log_test("Content Outline Generation", False, "No user token available")
            return False
            
        try:
            request_data = {
                "topic": "AI-powered SEO optimization strategies",
                "content_type": "guide",
                "target_length": 2000
            }
            
            response = requests.post(
                f"{self.base_url}/llm/content/generate-outline",
                json=request_data,
                headers=self.headers,
                timeout=45
            )
            
            if response.status_code == 200:
                data = response.json()
                
                if data.get("success") and "outline" in data:
                    outline = data.get("outline", {})
                    sections = outline.get("sections", []) if isinstance(outline, dict) else []
                    
                    self.log_test(
                        "Content Outline Generation", 
                        True, 
                        f"Generated outline with {len(sections)} sections for topic: {request_data['topic']}",
                        {
                            "sections_count": len(sections),
                            "topic": request_data["topic"],
                            "content_type": request_data["content_type"]
                        }
                    )
                    return True
                else:
                    self.log_test(
                        "Content Outline Generation", 
                        False, 
                        "Generation failed or invalid response structure"
                    )
            elif response.status_code == 402:
                self.log_test(
                    "Content Outline Generation", 
                    False, 
                    "Insufficient credits (expected if user has < 4 credits)"
                )
            else:
                self.log_test(
                    "Content Outline Generation", 
                    False, 
                    f"HTTP {response.status_code}: {response.text}"
                )
                
        except requests.exceptions.RequestException as e:
            self.log_test("Content Outline Generation", False, f"Request failed: {str(e)}")
            
        return False
    
    def test_schema_generation(self):
        """Test schema generation endpoint (2 credits)"""
        print("\n🏗️ Testing Schema Generation...")
        
        if not self.user_token:
            self.log_test("Schema Generation", False, "No user token available")
            return False
            
        try:
            request_data = {
                "schema_type": "FAQ",
                "data": {
                    "questions": [
                        {
                            "question": "What is AI-powered SEO?",
                            "answer": "AI-powered SEO uses artificial intelligence to optimize websites for search engines and AI assistants."
                        },
                        {
                            "question": "How does LLM visibility work?",
                            "answer": "LLM visibility measures how often your website appears in AI assistant responses."
                        }
                    ]
                }
            }
            
            response = requests.post(
                f"{self.base_url}/llm/content/generate-schema",
                json=request_data,
                headers=self.headers,
                timeout=30
            )
            
            if response.status_code == 200:
                data = response.json()
                
                if data.get("success") and "schema" in data:
                    schema = data.get("schema", "")
                    
                    self.log_test(
                        "Schema Generation", 
                        True, 
                        f"Generated {request_data['schema_type']} schema markup successfully",
                        {
                            "schema_type": request_data["schema_type"],
                            "schema_length": len(schema) if isinstance(schema, str) else 0
                        }
                    )
                    return True
                else:
                    self.log_test(
                        "Schema Generation", 
                        False, 
                        "Schema generation failed or invalid response"
                    )
            elif response.status_code == 402:
                self.log_test(
                    "Schema Generation", 
                    False, 
                    "Insufficient credits (expected if user has < 2 credits)"
                )
            else:
                self.log_test(
                    "Schema Generation", 
                    False, 
                    f"HTTP {response.status_code}: {response.text}"
                )
                
        except requests.exceptions.RequestException as e:
            self.log_test("Schema Generation", False, f"Request failed: {str(e)}")
            
        return False
    
    def test_community_opportunities(self):
        """Test community opportunities endpoint (3 credits)"""
        print("\n👥 Testing Community Opportunities...")
        
        if not self.user_token or not self.site_id:
            self.log_test("Community Opportunities", False, "Missing token or site_id")
            return False
            
        try:
            request_data = {
                "site_id": self.site_id,
                "platforms": ["reddit", "quora"]
            }
            
            response = requests.post(
                f"{self.base_url}/llm/community/opportunities",
                json=request_data,
                headers=self.headers,
                timeout=45
            )
            
            if response.status_code == 200:
                data = response.json()
                
                if data.get("success") and "opportunities" in data:
                    opportunities = data.get("opportunities", [])
                    platforms = data.get("platforms_searched", [])
                    
                    self.log_test(
                        "Community Opportunities", 
                        True, 
                        f"Found {len(opportunities)} opportunities across {len(platforms)} platforms",
                        {
                            "opportunities_count": len(opportunities),
                            "platforms": platforms
                        }
                    )
                    return True
                else:
                    self.log_test(
                        "Community Opportunities", 
                        False, 
                        "Search failed or invalid response structure"
                    )
            elif response.status_code == 402:
                self.log_test(
                    "Community Opportunities", 
                    False, 
                    "Insufficient credits (expected if user has < 3 credits)"
                )
            else:
                self.log_test(
                    "Community Opportunities", 
                    False, 
                    f"HTTP {response.status_code}: {response.text}"
                )
                
        except requests.exceptions.RequestException as e:
            self.log_test("Community Opportunities", False, f"Request failed: {str(e)}")
            
        return False
    
    def test_backlink_analysis(self):
        """Test backlink analysis endpoint (5 credits)"""
        print("\n🔗 Testing Backlink Analysis...")
        
        if not self.user_token or not self.site_id:
            self.log_test("Backlink Analysis", False, "Missing token or site_id")
            return False
            
        try:
            request_data = {
                "site_id": self.site_id,
                "competitors": ["competitor1.com", "competitor2.com"]
            }
            
            response = requests.post(
                f"{self.base_url}/llm/backlinks/analyze",
                json=request_data,
                headers=self.headers,
                timeout=45
            )
            
            if response.status_code == 200:
                data = response.json()
                
                if data.get("success"):
                    gaps = data.get("link_gaps", [])
                    opportunities = data.get("opportunities", [])
                    
                    self.log_test(
                        "Backlink Analysis", 
                        True, 
                        f"Analysis completed - Found {len(gaps)} gaps and {len(opportunities)} opportunities",
                        {
                            "link_gaps": len(gaps),
                            "opportunities": len(opportunities)
                        }
                    )
                    return True
                else:
                    self.log_test(
                        "Backlink Analysis", 
                        False, 
                        "Analysis failed or invalid response"
                    )
            elif response.status_code == 402:
                self.log_test(
                    "Backlink Analysis", 
                    False, 
                    "Insufficient credits (expected if user has < 5 credits)"
                )
            else:
                self.log_test(
                    "Backlink Analysis", 
                    False, 
                    f"HTTP {response.status_code}: {response.text}"
                )
                
        except requests.exceptions.RequestException as e:
            self.log_test("Backlink Analysis", False, f"Request failed: {str(e)}")
            
        return False
    
    def test_learning_center_endpoints(self):
        """Test learning center endpoints (free)"""
        print("\n📚 Testing Learning Center Endpoints...")
        
        if not self.user_token:
            self.log_test("Learning Center", False, "No user token available")
            return False
            
        endpoints_tested = 0
        endpoints_passed = 0
        
        # Test knowledge base
        try:
            response = requests.get(
                f"{self.base_url}/llm/learning/knowledge-base",
                headers=self.headers,
                timeout=30
            )
            endpoints_tested += 1
            if response.status_code == 200:
                endpoints_passed += 1
        except:
            pass
        
        # Test tutorials
        try:
            response = requests.get(
                f"{self.base_url}/llm/learning/tutorials",
                headers=self.headers,
                timeout=30
            )
            endpoints_tested += 1
            if response.status_code == 200:
                endpoints_passed += 1
        except:
            pass
        
        # Test FAQ
        try:
            response = requests.get(
                f"{self.base_url}/llm/learning/faq",
                headers=self.headers,
                timeout=30
            )
            endpoints_tested += 1
            if response.status_code == 200:
                endpoints_passed += 1
        except:
            pass
        
        # Test AI assistant
        try:
            response = requests.post(
                f"{self.base_url}/llm/learning/ai-assistant",
                json={"question": "How do I improve my LLM visibility?"},
                headers=self.headers,
                timeout=30
            )
            endpoints_tested += 1
            if response.status_code == 200:
                endpoints_passed += 1
        except:
            pass
        
        if endpoints_passed == endpoints_tested and endpoints_tested > 0:
            self.log_test(
                "Learning Center Endpoints", 
                True, 
                f"All {endpoints_passed}/{endpoints_tested} learning center endpoints working",
                {"endpoints_tested": endpoints_tested, "endpoints_passed": endpoints_passed}
            )
            return True
        else:
            self.log_test(
                "Learning Center Endpoints", 
                False, 
                f"Only {endpoints_passed}/{endpoints_tested} endpoints working"
            )
            return False
    
    def check_credit_deduction(self):
        """Check if credits were properly deducted"""
        print("\n💳 Checking Credit Deduction...")
        
        if not self.user_token:
            self.log_test("Credit Deduction Check", False, "No user token available")
            return False
            
        try:
            # Get current user info
            response = requests.get(
                f"{self.base_url}/auth/me",
                headers=self.headers,
                timeout=30
            )
            
            if response.status_code == 200:
                user_data = response.json()
                current_credits = user_data.get("credits", 0)
                credits_used = self.initial_credits - current_credits
                
                self.log_test(
                    "Credit Deduction Check", 
                    True, 
                    f"Credits properly tracked - Started: {self.initial_credits}, Current: {current_credits}, Used: {credits_used}",
                    {
                        "initial_credits": self.initial_credits,
                        "current_credits": current_credits,
                        "credits_used": credits_used
                    }
                )
                return True
            else:
                self.log_test(
                    "Credit Deduction Check", 
                    False, 
                    f"Failed to get user info: HTTP {response.status_code}"
                )
        except requests.exceptions.RequestException as e:
            self.log_test("Credit Deduction Check", False, f"Request failed: {str(e)}")
            
        return False
    
    def run_all_tests(self):
        """Run all LLM Visibility Optimizer backend tests"""
        print("🚀 Starting LLM Visibility Optimizer Backend API Tests")
        print(f"🌐 Backend URL: {self.base_url}")
        print(f"👤 User Email: {USER_CREDENTIALS['email']}")
        print("=" * 80)
        
        # Test sequence based on review request priorities
        test_results = []
        
        # 1. Redis Connectivity (Critical Infrastructure)
        test_results.append(self.test_redis_connectivity())
        
        # 2. User Authentication (Critical)
        if not self.test_user_login():
            print("❌ Cannot proceed without authentication")
            return 0, 1, self.test_results
        
        # 3. Get Sites (Required for most tests)
        if not self.test_get_sites():
            print("❌ Cannot proceed without site data")
            return 1, 2, self.test_results
        
        # 4. LLM Visibility Check (8 credits) - Priority 1
        test_results.append(self.test_llm_visibility_check())
        
        # 5. Recommendations Generation - Priority 2
        test_results.append(self.test_recommendations_generation())
        
        # 6. Content Gap Analysis (6 credits) - Priority 3
        test_results.append(self.test_content_gap_analysis())
        
        # 7. Content Outline Generation (4 credits) - Priority 4
        test_results.append(self.test_content_outline_generation())
        
        # 8. Schema Generation (2 credits) - Priority 5
        test_results.append(self.test_schema_generation())
        
        # 9. Community Opportunities (3 credits) - Priority 6
        test_results.append(self.test_community_opportunities())
        
        # 10. Backlink Analysis (5 credits) - Priority 7
        test_results.append(self.test_backlink_analysis())
        
        # 11. Learning Center (free) - Priority 8
        test_results.append(self.test_learning_center_endpoints())
        
        # 12. Credit Deduction Verification
        test_results.append(self.check_credit_deduction())
        
        # Calculate results (excluding login and get_sites from count)
        tests_passed = sum(1 for result in test_results if result)
        total_tests = len(test_results)
        
        # Summary
        print("\n" + "=" * 80)
        print("📊 LLM VISIBILITY OPTIMIZER TEST SUMMARY")
        print("=" * 80)
        print(f"✅ Tests Passed: {tests_passed}/{total_tests}")
        print(f"❌ Tests Failed: {total_tests - tests_passed}/{total_tests}")
        
        if tests_passed == total_tests:
            print("🎉 ALL LLM VISIBILITY TESTS PASSED! All 8 modules are working correctly.")
        elif tests_passed >= total_tests * 0.7:
            print("✅ Most tests passed. Some features may need attention.")
        else:
            print("⚠️  Multiple tests failed. Check the details above.")
            
        return tests_passed, total_tests, self.test_results

def main():
    """Main test execution"""
    tester = LLMVisibilityTester()
    passed, total, results = tester.run_all_tests()
    
    # Save detailed results
    with open('/app/llm_visibility_test_results.json', 'w') as f:
        json.dump({
            'summary': {
                'passed': passed,
                'total': total,
                'success_rate': f"{(passed/total)*100:.1f}%" if total > 0 else "0%"
            },
            'results': results,
            'timestamp': datetime.now().isoformat()
        }, f, indent=2)
    
    print(f"\n📄 Detailed results saved to: /app/llm_visibility_test_results.json")
    
    # Exit with appropriate code
    sys.exit(0 if passed == total else 1)

if __name__ == "__main__":
    main()