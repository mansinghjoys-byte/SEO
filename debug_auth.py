#!/usr/bin/env python3
"""
Debug authentication flow
"""

import requests
import json

BACKEND_URL = "https://seo-rival-scan.preview.emergentagent.com/api"
TEST_USER_CREDENTIALS = {
    "email": "test@rankforge.com",
    "password": "Test@123"
}

def debug_auth():
    headers = {"Content-Type": "application/json"}
    
    # Test login
    print("🔐 Testing login...")
    response = requests.post(
        f"{BACKEND_URL}/auth/login",
        json=TEST_USER_CREDENTIALS,
        headers=headers,
        timeout=30
    )
    
    print(f"Login Status: {response.status_code}")
    print(f"Login Response: {response.text}")
    
    if response.status_code == 200:
        data = response.json()
        token = data.get("access_token")
        print(f"Token: {token[:50]}..." if token else "No token")
        
        # Test with token
        auth_headers = {
            "Content-Type": "application/json",
            "Authorization": f"Bearer {token}"
        }
        
        print("\n🌐 Testing sites endpoint with token...")
        sites_response = requests.get(
            f"{BACKEND_URL}/sites",
            headers=auth_headers,
            timeout=30
        )
        
        print(f"Sites Status: {sites_response.status_code}")
        print(f"Sites Response: {sites_response.text}")
        
        # Test auth/me endpoint
        print("\n👤 Testing auth/me endpoint...")
        me_response = requests.get(
            f"{BACKEND_URL}/auth/me",
            headers=auth_headers,
            timeout=30
        )
        
        print(f"Me Status: {me_response.status_code}")
        print(f"Me Response: {me_response.text}")

if __name__ == "__main__":
    debug_auth()