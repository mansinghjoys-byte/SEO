#!/usr/bin/env python3
import requests
import json

class DebugTester:
    def __init__(self):
        self.base_url = "https://seo-audit-sync.preview.emergentagent.com/api"
        self.headers = {"Content-Type": "application/json"}
        self.user_token = None
        self.site_id = None
    
    def test_login(self):
        print("Testing login...")
        try:
            response = requests.post(
                f"{self.base_url}/auth/login",
                json={"email": "amis.joys@gmail.com", "password": "password123"},
                headers=self.headers,
                timeout=30
            )
            
            print(f"Login response: {response.status_code}")
            
            if response.status_code == 200:
                data = response.json()
                self.user_token = data["access_token"]
                self.headers["Authorization"] = f"Bearer {self.user_token}"
                print("✅ Login successful")
                print(f"Token: {self.user_token[:20]}...")
                return True
            else:
                print(f"❌ Login failed: {response.text}")
                return False
        except Exception as e:
            print(f"❌ Login exception: {e}")
            return False
    
    def test_sites(self):
        print("Testing sites...")
        print(f"Headers: {self.headers}")
        
        try:
            response = requests.get(
                f"{self.base_url}/sites/",
                headers=self.headers,
                timeout=30
            )
            
            print(f"Sites response: {response.status_code}")
            
            if response.status_code == 200:
                sites = response.json()
                print(f"✅ Sites found: {len(sites)}")
                if sites:
                    self.site_id = sites[0]["site_id"]
                    print(f"Using site: {sites[0]['url']}")
                return True
            else:
                print(f"❌ Sites failed: {response.text}")
                return False
        except Exception as e:
            print(f"❌ Sites exception: {e}")
            return False

# Run test
tester = DebugTester()
if tester.test_login():
    tester.test_sites()