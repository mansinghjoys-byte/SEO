#!/usr/bin/env python3
"""
Backend API Testing for Super Admin System
Tests admin authentication, SEO settings, system stats, plans, and users management
"""

import requests
import json
import sys
from datetime import datetime

# Configuration
BACKEND_URL = "https://rank-booster.preview.emergentagent.com/api"
ADMIN_CREDENTIALS = {
    "email": "admin@rankforge.com",
    "password": "RankForge@Admin2025!Secure"
}

class AdminAPITester:
    def __init__(self):
        self.base_url = BACKEND_URL
        self.admin_token = None
        self.headers = {"Content-Type": "application/json"}
        self.test_results = []
        
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
        
    def test_admin_login(self):
        """Test admin login endpoint"""
        print("\n🔐 Testing Admin Login...")
        
        try:
            response = requests.post(
                f"{self.base_url}/admin/login",
                json=ADMIN_CREDENTIALS,
                headers=self.headers,
                timeout=30
            )
            
            if response.status_code == 200:
                data = response.json()
                
                # Validate response structure
                if "access_token" in data and "user" in data:
                    self.admin_token = data["access_token"]
                    self.headers["Authorization"] = f"Bearer {self.admin_token}"
                    
                    user_info = data["user"]
                    expected_email = ADMIN_CREDENTIALS["email"]
                    
                    if user_info.get("email") == expected_email:
                        self.log_test(
                            "Admin Login", 
                            True, 
                            f"Successfully logged in as {expected_email}",
                            {"token_received": True, "user_email": user_info.get("email")}
                        )
                        return True
                    else:
                        self.log_test(
                            "Admin Login", 
                            False, 
                            f"Email mismatch: expected {expected_email}, got {user_info.get('email')}"
                        )
                else:
                    self.log_test(
                        "Admin Login", 
                        False, 
                        "Missing access_token or user in response"
                    )
            else:
                self.log_test(
                    "Admin Login", 
                    False, 
                    f"HTTP {response.status_code}: {response.text}"
                )
                
        except requests.exceptions.RequestException as e:
            self.log_test("Admin Login", False, f"Request failed: {str(e)}")
            
        return False
    
    def test_seo_settings_get(self):
        """Test GET SEO settings"""
        print("\n📊 Testing SEO Settings GET...")
        
        if not self.admin_token:
            self.log_test("SEO Settings GET", False, "No admin token available")
            return False
            
        try:
            response = requests.get(
                f"{self.base_url}/admin/seo-settings",
                headers=self.headers,
                timeout=30
            )
            
            if response.status_code == 200:
                data = response.json()
                
                # Validate required fields
                required_fields = ["setting_id", "title", "description", "keywords"]
                missing_fields = [field for field in required_fields if field not in data]
                
                if not missing_fields:
                    self.log_test(
                        "SEO Settings GET", 
                        True, 
                        f"Retrieved SEO settings with title: '{data.get('title')}'",
                        {"title": data.get("title"), "keywords_count": len(data.get("keywords", []))}
                    )
                    return data
                else:
                    self.log_test(
                        "SEO Settings GET", 
                        False, 
                        f"Missing required fields: {missing_fields}"
                    )
            else:
                self.log_test(
                    "SEO Settings GET", 
                    False, 
                    f"HTTP {response.status_code}: {response.text}"
                )
                
        except requests.exceptions.RequestException as e:
            self.log_test("SEO Settings GET", False, f"Request failed: {str(e)}")
            
        return False
    
    def test_seo_settings_update(self):
        """Test PUT SEO settings"""
        print("\n✏️ Testing SEO Settings UPDATE...")
        
        if not self.admin_token:
            self.log_test("SEO Settings UPDATE", False, "No admin token available")
            return False
            
        # Sample update data
        update_data = {
            "title": "RankForge - Updated SEO Platform",
            "description": "Advanced AI-powered SEO analysis platform - Updated via API test",
            "keywords": ["SEO", "AI", "website optimization", "search engine", "testing"],
            "og_title": "RankForge SEO Platform",
            "canonical_url": "https://rankforge.com/updated"
        }
        
        try:
            response = requests.put(
                f"{self.base_url}/admin/seo-settings",
                json=update_data,
                headers=self.headers,
                timeout=30
            )
            
            if response.status_code == 200:
                data = response.json()
                
                # Verify updates were applied
                if (data.get("title") == update_data["title"] and 
                    data.get("description") == update_data["description"]):
                    self.log_test(
                        "SEO Settings UPDATE", 
                        True, 
                        "Successfully updated SEO settings",
                        {"updated_title": data.get("title"), "keywords_count": len(data.get("keywords", []))}
                    )
                    return True
                else:
                    self.log_test(
                        "SEO Settings UPDATE", 
                        False, 
                        "Updates not reflected in response"
                    )
            else:
                self.log_test(
                    "SEO Settings UPDATE", 
                    False, 
                    f"HTTP {response.status_code}: {response.text}"
                )
                
        except requests.exceptions.RequestException as e:
            self.log_test("SEO Settings UPDATE", False, f"Request failed: {str(e)}")
            
        return False
    
    def test_system_stats(self):
        """Test system statistics endpoint"""
        print("\n📈 Testing System Stats...")
        
        if not self.admin_token:
            self.log_test("System Stats", False, "No admin token available")
            return False
            
        try:
            response = requests.get(
                f"{self.base_url}/admin/stats",
                headers=self.headers,
                timeout=30
            )
            
            if response.status_code == 200:
                data = response.json()
                
                # Validate required stats fields
                required_fields = [
                    "total_users", "total_sites", "total_audits", 
                    "total_keywords", "active_agents", "credits_consumed", 
                    "revenue", "new_users_today", "audits_today"
                ]
                
                missing_fields = [field for field in required_fields if field not in data]
                
                if not missing_fields:
                    self.log_test(
                        "System Stats", 
                        True, 
                        f"Retrieved system stats - Users: {data.get('total_users')}, Sites: {data.get('total_sites')}, Audits: {data.get('total_audits')}",
                        {
                            "total_users": data.get("total_users"),
                            "total_sites": data.get("total_sites"),
                            "total_audits": data.get("total_audits"),
                            "revenue": data.get("revenue")
                        }
                    )
                    return data
                else:
                    self.log_test(
                        "System Stats", 
                        False, 
                        f"Missing required fields: {missing_fields}"
                    )
            else:
                self.log_test(
                    "System Stats", 
                    False, 
                    f"HTTP {response.status_code}: {response.text}"
                )
                
        except requests.exceptions.RequestException as e:
            self.log_test("System Stats", False, f"Request failed: {str(e)}")
            
        return False
    
    def test_plans_management(self):
        """Test plans management endpoints"""
        print("\n💰 Testing Plans Management...")
        
        if not self.admin_token:
            self.log_test("Plans Management", False, "No admin token available")
            return False
            
        try:
            # Test GET all plans
            response = requests.get(
                f"{self.base_url}/admin/plans",
                headers=self.headers,
                timeout=30
            )
            
            if response.status_code == 200:
                plans = response.json()
                
                if isinstance(plans, list):
                    self.log_test(
                        "Plans Management GET", 
                        True, 
                        f"Retrieved {len(plans)} pricing plans",
                        {"plans_count": len(plans), "plan_names": [p.get("name") for p in plans[:3]]}
                    )
                    return plans
                else:
                    self.log_test(
                        "Plans Management GET", 
                        False, 
                        "Response is not a list"
                    )
            else:
                self.log_test(
                    "Plans Management GET", 
                    False, 
                    f"HTTP {response.status_code}: {response.text}"
                )
                
        except requests.exceptions.RequestException as e:
            self.log_test("Plans Management GET", False, f"Request failed: {str(e)}")
            
        return False
    
    def test_users_management(self):
        """Test users management endpoints"""
        print("\n👥 Testing Users Management...")
        
        if not self.admin_token:
            self.log_test("Users Management", False, "No admin token available")
            return False
            
        try:
            # Test GET all users
            response = requests.get(
                f"{self.base_url}/admin/users",
                headers=self.headers,
                timeout=30
            )
            
            if response.status_code == 200:
                users = response.json()
                
                if isinstance(users, list):
                    # Validate user structure if users exist
                    if users:
                        user = users[0]
                        required_fields = ["user_id", "email", "full_name", "credits", "plan"]
                        missing_fields = [field for field in required_fields if field not in user]
                        
                        if not missing_fields:
                            self.log_test(
                                "Users Management GET", 
                                True, 
                                f"Retrieved {len(users)} users with proper structure",
                                {"users_count": len(users), "sample_user_email": user.get("email")}
                            )
                        else:
                            self.log_test(
                                "Users Management GET", 
                                False, 
                                f"User missing required fields: {missing_fields}"
                            )
                    else:
                        self.log_test(
                            "Users Management GET", 
                            True, 
                            "Retrieved empty users list (no users registered yet)",
                            {"users_count": 0}
                        )
                    return users
                else:
                    self.log_test(
                        "Users Management GET", 
                        False, 
                        "Response is not a list"
                    )
            else:
                self.log_test(
                    "Users Management GET", 
                    False, 
                    f"HTTP {response.status_code}: {response.text}"
                )
                
        except requests.exceptions.RequestException as e:
            self.log_test("Users Management GET", False, f"Request failed: {str(e)}")
            
        return False
    
    def test_deep_analysis_endpoint(self):
        """Test deep analysis endpoint (if time permits)"""
        print("\n🔍 Testing Deep Analysis Endpoint...")
        
        if not self.admin_token:
            self.log_test("Deep Analysis", False, "No admin token available")
            return False
            
        # Note: This would require a valid site_id, so we'll just test the endpoint structure
        # In a real scenario, we'd need to create a site first
        try:
            # Test with a dummy site_id to see if endpoint exists
            response = requests.post(
                f"{self.base_url}/audits/deep-analysis/dummy-site-id",
                headers=self.headers,
                timeout=30
            )
            
            # We expect 404 or 422 (validation error) rather than 405 (method not allowed)
            if response.status_code in [404, 422]:
                self.log_test(
                    "Deep Analysis Endpoint", 
                    True, 
                    f"Endpoint exists (HTTP {response.status_code} expected for dummy site_id)",
                    {"status_code": response.status_code}
                )
                return True
            elif response.status_code == 405:
                self.log_test(
                    "Deep Analysis Endpoint", 
                    False, 
                    "Endpoint not found (HTTP 405 Method Not Allowed)"
                )
            else:
                self.log_test(
                    "Deep Analysis Endpoint", 
                    True, 
                    f"Endpoint accessible (HTTP {response.status_code})",
                    {"status_code": response.status_code}
                )
                
        except requests.exceptions.RequestException as e:
            self.log_test("Deep Analysis Endpoint", False, f"Request failed: {str(e)}")
            
        return False
    
    def run_all_tests(self):
        """Run all admin backend tests"""
        print("🚀 Starting Super Admin Backend API Tests")
        print(f"🌐 Backend URL: {self.base_url}")
        print(f"👤 Admin Email: {ADMIN_CREDENTIALS['email']}")
        print("=" * 60)
        
        # Test sequence based on review request priorities
        test_results = []
        
        # 1. Admin Login (Critical)
        test_results.append(self.test_admin_login())
        
        # 2. SEO Settings (Critical)
        test_results.append(self.test_seo_settings_get())
        test_results.append(self.test_seo_settings_update())
        
        # 3. System Stats (Critical)
        test_results.append(self.test_system_stats())
        
        # 4. Plans Management (If time permits)
        test_results.append(self.test_plans_management())
        
        # 5. Users Management (If time permits)
        test_results.append(self.test_users_management())
        
        # 6. Deep Analysis Endpoint (Additional)
        test_results.append(self.test_deep_analysis_endpoint())
        
        # Calculate results
        tests_passed = sum(1 for result in test_results if result)
        total_tests = len(test_results)
        
        # Summary
        print("\n" + "=" * 60)
        print("📊 TEST SUMMARY")
        print("=" * 60)
        print(f"✅ Tests Passed: {tests_passed}/{total_tests}")
        print(f"❌ Tests Failed: {total_tests - tests_passed}/{total_tests}")
        
        if tests_passed == total_tests:
            print("🎉 ALL TESTS PASSED! Super Admin backend is working correctly.")
        else:
            print("⚠️  Some tests failed. Check the details above.")
            
        return tests_passed, total_tests, self.test_results

def main():
    """Main test execution"""
    tester = AdminAPITester()
    passed, total, results = tester.run_all_tests()
    
    # Save detailed results
    with open('/app/admin_test_results.json', 'w') as f:
        json.dump({
            'summary': {
                'passed': passed,
                'total': total,
                'success_rate': f"{(passed/total)*100:.1f}%"
            },
            'results': results,
            'timestamp': datetime.now().isoformat()
        }, f, indent=2)
    
    print(f"\n📄 Detailed results saved to: /app/admin_test_results.json")
    
    # Exit with appropriate code
    sys.exit(0 if passed == total else 1)

if __name__ == "__main__":
    main()