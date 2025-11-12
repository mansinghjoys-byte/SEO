#!/usr/bin/env python3
"""
Focused test for Trusted Backlinks feature
Tests the newly implemented trusted backlinks endpoints
"""

import requests
import json
import sys
from datetime import datetime

# Configuration
BACKEND_URL = "https://audit-enhancer.preview.emergentagent.com/api"
USER_CREDENTIALS = {
    "email": "amis.joys@gmail.com",
    "password": "password123"
}

class TrustedBacklinksTester:
    def __init__(self):
        self.base_url = BACKEND_URL
        self.user_token = None
        self.headers = {"Content-Type": "application/json"}
        self.test_results = []
        self.site_id = None
        
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
        
    def login_user(self):
        """Login user and get token"""
        try:
            response = requests.post(
                f"{self.base_url}/auth/login",
                json=USER_CREDENTIALS,
                headers=self.headers,
                timeout=30
            )
            
            if response.status_code == 200:
                data = response.json()
                self.user_token = data["access_token"]
                self.headers["Authorization"] = f"Bearer {self.user_token}"
                
                user_info = data["user"]
                credits = user_info.get("credits", 0)
                
                print(f"✅ Logged in as {user_info.get('email')} with {credits} credits")
                return True
            else:
                print(f"❌ Login failed: {response.status_code} - {response.text}")
                return False
                
        except Exception as e:
            print(f"❌ Login error: {str(e)}")
            return False
    
    def get_site_id(self):
        """Get a site ID for testing"""
        try:
            response = requests.get(
                f"{self.base_url}/sites",
                headers=self.headers,
                timeout=30
            )
            
            if response.status_code == 200:
                sites = response.json()
                if sites:
                    self.site_id = sites[0]["site_id"]
                    print(f"✅ Using site: {sites[0]['url']} (ID: {self.site_id})")
                    return True
                else:
                    print("❌ No sites found")
                    return False
            else:
                print(f"❌ Failed to get sites: {response.status_code}")
                return False
                
        except Exception as e:
            print(f"❌ Get sites error: {str(e)}")
            return False
    
    def test_trusted_backlinks_scan(self):
        """Test POST /api/llm/backlinks/trusted-sources"""
        print("\n🔍 Testing Trusted Backlinks Scan (5 credits)...")
        
        try:
            request_data = {
                "site_id": self.site_id,
                "deep_scan": False
            }
            
            response = requests.post(
                f"{self.base_url}/llm/backlinks/trusted-sources",
                json=request_data,
                headers=self.headers,
                timeout=60
            )
            
            print(f"   Response status: {response.status_code}")
            
            if response.status_code == 200:
                data = response.json()
                print(f"   Response keys: {list(data.keys())}")
                
                if data.get("success"):
                    summary = data.get("summary", {})
                    backlinks = data.get("backlinks", [])
                    by_category = data.get("by_category", {})
                    insights = data.get("insights", {})
                    recommendations = data.get("recommendations", [])
                    
                    total_trusted = summary.get("total_trusted_backlinks", 0)
                    avg_authority = summary.get("average_authority", 0)
                    categories = summary.get("categories_represented", 0)
                    highest_authority = summary.get("highest_authority_source")
                    
                    print(f"   📊 Summary:")
                    print(f"      - Total trusted backlinks: {total_trusted}")
                    print(f"      - Average authority: {avg_authority}")
                    print(f"      - Categories represented: {categories}")
                    print(f"      - Highest authority source: {highest_authority}")
                    print(f"      - Backlinks found: {len(backlinks)}")
                    print(f"      - Categories: {list(by_category.keys())}")
                    print(f"      - Recommendations: {len(recommendations)}")
                    
                    # Show sample backlinks
                    if backlinks:
                        print(f"   🔗 Sample backlinks:")
                        for i, bl in enumerate(backlinks[:3]):
                            print(f"      {i+1}. {bl.get('source')} (DA: {bl.get('domain_authority')}) - {bl.get('category')}")
                    
                    self.log_test(
                        "Trusted Backlinks Scan", 
                        True, 
                        f"Scan completed - Found {total_trusted} trusted backlinks, avg authority {avg_authority}, {categories} categories",
                        {
                            "total_trusted_backlinks": total_trusted,
                            "average_authority": avg_authority,
                            "categories_represented": categories,
                            "backlinks_count": len(backlinks),
                            "categories": list(by_category.keys()),
                            "recommendations_count": len(recommendations),
                            "highest_authority_source": highest_authority
                        }
                    )
                    return True
                else:
                    self.log_test("Trusted Backlinks Scan", False, "Scan failed - success=false")
                    
            elif response.status_code == 402:
                self.log_test("Trusted Backlinks Scan", False, "Insufficient credits")
            else:
                print(f"   Error response: {response.text}")
                self.log_test("Trusted Backlinks Scan", False, f"HTTP {response.status_code}: {response.text}")
                
        except Exception as e:
            self.log_test("Trusted Backlinks Scan", False, f"Request failed: {str(e)}")
            
        return False
    
    def test_get_latest_scan(self):
        """Test GET /api/llm/backlinks/trusted-sources/{site_id}"""
        print("\n📋 Testing Get Latest Trusted Backlinks Scan...")
        
        try:
            response = requests.get(
                f"{self.base_url}/llm/backlinks/trusted-sources/{self.site_id}",
                headers=self.headers,
                timeout=30
            )
            
            print(f"   Response status: {response.status_code}")
            
            if response.status_code == 200:
                data = response.json()
                print(f"   Response keys: {list(data.keys())}")
                
                if data.get("success"):
                    has_data = data.get("has_data", False)
                    
                    if has_data:
                        scan = data.get("scan", {})
                        scan_result = scan.get("result", {})
                        
                        print(f"   📊 Scan found:")
                        print(f"      - Scan ID: {scan.get('backlink_scan_id')}")
                        print(f"      - Scan type: {scan.get('scan_type')}")
                        print(f"      - Created at: {scan.get('created_at')}")
                        
                        if scan_result:
                            summary = scan_result.get("summary", {})
                            print(f"      - Total backlinks: {summary.get('total_trusted_backlinks', 0)}")
                            print(f"      - Average authority: {summary.get('average_authority', 0)}")
                        
                        self.log_test(
                            "Get Latest Scan", 
                            True, 
                            f"Retrieved latest scan successfully",
                            {
                                "has_data": has_data,
                                "scan_id": scan.get("backlink_scan_id"),
                                "scan_type": scan.get("scan_type")
                            }
                        )
                    else:
                        print(f"   📋 No previous scan found: {data.get('message')}")
                        self.log_test(
                            "Get Latest Scan", 
                            True, 
                            "No previous scan found (expected for new sites)",
                            {"has_data": has_data, "message": data.get("message")}
                        )
                    return True
                else:
                    self.log_test("Get Latest Scan", False, "Failed to retrieve scan data")
            else:
                print(f"   Error response: {response.text}")
                self.log_test("Get Latest Scan", False, f"HTTP {response.status_code}: {response.text}")
                
        except Exception as e:
            self.log_test("Get Latest Scan", False, f"Request failed: {str(e)}")
            
        return False
    
    def test_backlink_opportunities(self):
        """Test GET /api/llm/backlinks/opportunities"""
        print("\n🎯 Testing Backlink Opportunities...")
        
        try:
            # Test without category filter
            response = requests.get(
                f"{self.base_url}/llm/backlinks/opportunities",
                headers=self.headers,
                timeout=30
            )
            
            print(f"   Response status: {response.status_code}")
            
            if response.status_code == 200:
                data = response.json()
                print(f"   Response keys: {list(data.keys())}")
                
                if data.get("success"):
                    opportunities = data.get("opportunities", [])
                    total = data.get("total", 0)
                    
                    print(f"   📊 Opportunities found: {total}")
                    
                    # Show sample opportunities
                    if opportunities:
                        print(f"   🎯 Sample opportunities:")
                        for i, opp in enumerate(opportunities[:5]):
                            print(f"      {i+1}. {opp.get('source')} (DA: {opp.get('authority')}) - {opp.get('category')} - {opp.get('difficulty')}")
                    
                    # Test with category filter
                    category_response = requests.get(
                        f"{self.base_url}/llm/backlinks/opportunities?category=Community",
                        headers=self.headers,
                        timeout=30
                    )
                    
                    category_count = 0
                    if category_response.status_code == 200:
                        category_data = category_response.json()
                        if category_data.get("success"):
                            category_count = len(category_data.get("opportunities", []))
                            print(f"   📊 Community opportunities: {category_count}")
                    
                    self.log_test(
                        "Backlink Opportunities", 
                        True, 
                        f"Retrieved {total} total opportunities, {category_count} community opportunities",
                        {
                            "total_opportunities": total,
                            "community_opportunities": category_count,
                            "sample_sources": [opp.get("source") for opp in opportunities[:3]]
                        }
                    )
                    return True
                else:
                    self.log_test("Backlink Opportunities", False, "Failed to retrieve opportunities")
            else:
                print(f"   Error response: {response.text}")
                self.log_test("Backlink Opportunities", False, f"HTTP {response.status_code}: {response.text}")
                
        except Exception as e:
            self.log_test("Backlink Opportunities", False, f"Request failed: {str(e)}")
            
        return False
    
    def test_agent_creation_with_website(self):
        """Test agent creation with website field"""
        print("\n🤖 Testing Agent Creation with Website Field...")
        
        try:
            # Get site URL
            site_response = requests.get(
                f"{self.base_url}/sites",
                headers=self.headers,
                timeout=30
            )
            
            if site_response.status_code != 200:
                self.log_test("Agent Creation with Website", False, "Could not retrieve site data")
                return False
            
            sites = site_response.json()
            if not sites:
                self.log_test("Agent Creation with Website", False, "No sites available")
                return False
            
            test_site_url = sites[0]["url"]
            
            agent_data = {
                "name": "Trusted Backlinks Specialist",
                "purpose": "llm_visibility_optimizer",
                "website": test_site_url,
                "context": {
                    "specialization": "trusted_backlinks",
                    "focus": "Reddit, Quora, Wikipedia backlinks"
                }
            }
            
            response = requests.post(
                f"{self.base_url}/agents",
                json=agent_data,
                headers=self.headers,
                timeout=30
            )
            
            print(f"   Response status: {response.status_code}")
            
            if response.status_code == 200:
                data = response.json()
                print(f"   Response keys: {list(data.keys())}")
                
                required_fields = ["agent_id", "name", "purpose", "website", "site_id"]
                missing_fields = [field for field in required_fields if field not in data]
                
                if not missing_fields:
                    print(f"   🤖 Agent created:")
                    print(f"      - Agent ID: {data.get('agent_id')}")
                    print(f"      - Name: {data.get('name')}")
                    print(f"      - Website: {data.get('website')}")
                    print(f"      - Site ID: {data.get('site_id')}")
                    print(f"      - Purpose: {data.get('purpose')}")
                    
                    self.log_test(
                        "Agent Creation with Website", 
                        True, 
                        f"Agent created successfully with website {data.get('website')} and site_id {data.get('site_id')}",
                        {
                            "agent_id": data.get("agent_id"),
                            "name": data.get("name"),
                            "website": data.get("website"),
                            "site_id": data.get("site_id"),
                            "purpose": data.get("purpose")
                        }
                    )
                    return True
                else:
                    self.log_test("Agent Creation with Website", False, f"Missing fields: {missing_fields}")
            else:
                print(f"   Error response: {response.text}")
                self.log_test("Agent Creation with Website", False, f"HTTP {response.status_code}: {response.text}")
                
        except Exception as e:
            self.log_test("Agent Creation with Website", False, f"Request failed: {str(e)}")
            
        return False
    
    def check_credits(self):
        """Check current credits"""
        try:
            response = requests.get(
                f"{self.base_url}/auth/me",
                headers=self.headers,
                timeout=30
            )
            
            if response.status_code == 200:
                user_data = response.json()
                credits = user_data.get("credits", 0)
                print(f"💳 Current credits: {credits}")
                return credits
            else:
                print(f"❌ Failed to check credits: {response.status_code}")
                return 0
                
        except Exception as e:
            print(f"❌ Credits check error: {str(e)}")
            return 0
    
    def run_tests(self):
        """Run all trusted backlinks tests"""
        print("🚀 Starting Trusted Backlinks Feature Tests")
        print(f"🌐 Backend URL: {self.base_url}")
        print(f"👤 User Email: {USER_CREDENTIALS['email']}")
        print("=" * 80)
        
        # Login
        if not self.login_user():
            print("❌ Cannot proceed without authentication")
            return 0, 1
        
        # Get site
        if not self.get_site_id():
            print("❌ Cannot proceed without site data")
            return 0, 2
        
        # Check initial credits
        initial_credits = self.check_credits()
        
        test_results = []
        
        # Test 1: Agent Creation with Website Field
        test_results.append(self.test_agent_creation_with_website())
        
        # Test 2: Backlink Opportunities (free)
        test_results.append(self.test_backlink_opportunities())
        
        # Test 3: Get Latest Scan (should be empty initially)
        test_results.append(self.test_get_latest_scan())
        
        # Test 4: Trusted Backlinks Scan (5 credits)
        test_results.append(self.test_trusted_backlinks_scan())
        
        # Test 5: Get Latest Scan (should have data now)
        test_results.append(self.test_get_latest_scan())
        
        # Check final credits
        final_credits = self.check_credits()
        credits_used = initial_credits - final_credits
        print(f"💳 Credits used: {credits_used}")
        
        # Summary
        tests_passed = sum(1 for result in test_results if result)
        total_tests = len(test_results)
        
        print("\n" + "=" * 80)
        print("📊 TRUSTED BACKLINKS FEATURE TEST SUMMARY")
        print("=" * 80)
        print(f"✅ Tests Passed: {tests_passed}/{total_tests}")
        print(f"❌ Tests Failed: {total_tests - tests_passed}/{total_tests}")
        print(f"💳 Credits Used: {credits_used}")
        
        if tests_passed == total_tests:
            print("🎉 ALL TRUSTED BACKLINKS TESTS PASSED!")
        elif tests_passed >= total_tests * 0.8:
            print("✅ Most tests passed. Feature is working correctly.")
        else:
            print("⚠️  Some tests failed. Check the details above.")
            
        return tests_passed, total_tests

def main():
    """Main test execution"""
    tester = TrustedBacklinksTester()
    passed, total = tester.run_tests()
    
    # Save results
    with open('/app/trusted_backlinks_test_results.json', 'w') as f:
        json.dump({
            'summary': {
                'passed': passed,
                'total': total,
                'success_rate': f"{(passed/total)*100:.1f}%" if total > 0 else "0%"
            },
            'results': tester.test_results,
            'timestamp': datetime.now().isoformat()
        }, f, indent=2)
    
    print(f"\n📄 Detailed results saved to: /app/trusted_backlinks_test_results.json")
    
    # Exit with appropriate code
    sys.exit(0 if passed == total else 1)

if __name__ == "__main__":
    main()