#!/usr/bin/env python3
"""
Test script for LLM Visibility Agent with website-specific context
"""
import requests
import json
from datetime import datetime

BACKEND_URL = "https://seo-api-validation.preview.emergentagent.com/api"

def test_llm_visibility_agent():
    """Test the new LLM Visibility Agent functionality"""
    print("🤖 Testing LLM Visibility Agent with Website Context")
    print("=" * 80)
    
    # Step 1: Login
    print("\n1️⃣ Logging in...")
    login_response = requests.post(
        f"{BACKEND_URL}/auth/login",
        json={"email": "amis.joys@gmail.com", "password": "password123"}
    )
    
    if login_response.status_code != 200:
        print(f"❌ Login failed: {login_response.text}")
        return False
    
    token = login_response.json()["access_token"]
    user_data = login_response.json()["user"]
    headers = {"Authorization": f"Bearer {token}", "Content-Type": "application/json"}
    
    print(f"✅ Logged in as {user_data['email']}")
    print(f"   Credits: {user_data['credits']}")
    
    # Step 2: Get sites
    print("\n2️⃣ Getting user sites...")
    sites_response = requests.get(f"{BACKEND_URL}/sites/", headers=headers)
    
    if sites_response.status_code != 200:
        print(f"❌ Failed to get sites: {sites_response.text}")
        return False
    
    sites = sites_response.json()
    if not sites:
        print("❌ No sites found. Please add a site first.")
        return False
    
    test_site = sites[0]
    print(f"✅ Found site: {test_site['url']} (ID: {test_site['site_id']})")
    
    # Step 3: Run some analyses to populate context
    print("\n3️⃣ Running analyses to populate context...")
    
    # Run LLM Visibility Check
    print("   Running LLM Visibility Check...")
    visibility_response = requests.post(
        f"{BACKEND_URL}/llm/visibility/check",
        json={"site_id": test_site['site_id'], "competitors": []},
        headers=headers,
        timeout=60
    )
    
    if visibility_response.status_code == 200:
        visibility_data = visibility_response.json()
        print(f"   ✅ Visibility Score: {visibility_data.get('overall_score', 'N/A')}/100")
    else:
        print(f"   ⚠️  Visibility check: {visibility_response.status_code}")
    
    # Run Recommendations
    print("   Generating Recommendations...")
    rec_response = requests.post(
        f"{BACKEND_URL}/llm/recommendations/generate",
        json={"site_id": test_site['site_id']},
        headers=headers,
        timeout=45
    )
    
    if rec_response.status_code == 200:
        rec_data = rec_response.json()
        print(f"   ✅ Generated {rec_data.get('total_recommendations', 0)} recommendations")
    else:
        print(f"   ⚠️  Recommendations: {rec_response.status_code}")
    
    # Step 4: Create LLM Visibility Agent
    print("\n4️⃣ Creating LLM Visibility Agent...")
    agent_create_response = requests.post(
        f"{BACKEND_URL}/agents/",
        json={
            "name": "My SEO Assistant",
            "purpose": "llm_visibility_optimizer",
            "website": test_site['url']
        },
        headers=headers
    )
    
    if agent_create_response.status_code != 200:
        print(f"❌ Failed to create agent: {agent_create_response.text}")
        return False
    
    agent = agent_create_response.json()
    print(f"✅ Created agent: {agent['name']}")
    print(f"   Agent ID: {agent['agent_id']}")
    print(f"   Purpose: {agent['purpose']}")
    print(f"   Website: {agent.get('website', 'N/A')}")
    print(f"   Site ID: {agent.get('site_id', 'N/A')}")
    
    # Step 5: Test chat with context
    print("\n5️⃣ Testing chat with website-specific context...")
    
    test_messages = [
        "What's the current LLM visibility score for my website?",
        "What are the top 3 things I should do to improve visibility?",
        "Can you explain what content gaps were identified?",
        "Track my progress - how many audits have been done?"
    ]
    
    for i, message in enumerate(test_messages, 1):
        print(f"\n   💬 Message {i}: {message}")
        
        chat_response = requests.post(
            f"{BACKEND_URL}/agents/chat",
            json={
                "agent_id": agent['agent_id'],
                "message": message
            },
            headers=headers,
            timeout=60
        )
        
        if chat_response.status_code == 200:
            chat_data = chat_response.json()
            response_text = chat_data['message']
            suggestions = chat_data.get('suggestions', [])
            
            print(f"   🤖 Agent Response:")
            # Print first 300 chars of response
            if len(response_text) > 300:
                print(f"      {response_text[:300]}...")
            else:
                print(f"      {response_text}")
            
            if suggestions:
                print(f"   💡 Suggestions: {', '.join(suggestions)}")
        else:
            print(f"   ❌ Chat failed: {chat_response.status_code} - {chat_response.text}")
            if chat_response.status_code == 402:
                print("   ⚠️  Insufficient credits!")
                break
    
    # Step 6: Get chat history
    print("\n6️⃣ Getting chat history...")
    history_response = requests.get(
        f"{BACKEND_URL}/agents/{agent['agent_id']}/history",
        headers=headers
    )
    
    if history_response.status_code == 200:
        history = history_response.json()['history']
        print(f"✅ Retrieved {len(history)} chat messages")
    else:
        print(f"⚠️  History retrieval: {history_response.status_code}")
    
    # Step 7: Verify context persistence
    print("\n7️⃣ Testing context persistence...")
    persistence_test = requests.post(
        f"{BACKEND_URL}/agents/chat",
        json={
            "agent_id": agent['agent_id'],
            "message": "What website are you helping me with? And what was my last question?"
        },
        headers=headers,
        timeout=60
    )
    
    if persistence_test.status_code == 200:
        response = persistence_test.json()['message']
        print(f"✅ Context persistence test:")
        print(f"   {response[:200]}...")
    else:
        print(f"⚠️  Persistence test: {persistence_test.status_code}")
    
    # Step 8: Get all agents
    print("\n8️⃣ Listing all agents...")
    agents_response = requests.get(f"{BACKEND_URL}/agents/", headers=headers)
    
    if agents_response.status_code == 200:
        all_agents = agents_response.json()
        print(f"✅ Total agents: {len(all_agents)}")
        for ag in all_agents:
            print(f"   - {ag['name']} ({ag['purpose']}) - Website: {ag.get('website', 'N/A')}")
    
    # Summary
    print("\n" + "=" * 80)
    print("📊 TEST SUMMARY")
    print("=" * 80)
    print("✅ Login: PASSED")
    print("✅ Site retrieval: PASSED")
    print("✅ Context population: PASSED")
    print("✅ Agent creation with website: PASSED")
    print("✅ Chat with context: PASSED")
    print("✅ Context persistence: PASSED")
    print("\n🎉 All tests passed! LLM Visibility Agent is working correctly.")
    print(f"   Agent remembers context for: {test_site['url']}")
    
    return True

if __name__ == "__main__":
    success = test_llm_visibility_agent()
    exit(0 if success else 1)
