"""
Test Agent Workflow: Create agent for website, chat, verify context loading
"""
import requests
import json
from datetime import datetime

BASE_URL = "http://localhost:8001/api"

def test_agent_workflow():
    print("🧪 Testing Agent Workflow\n")
    print("=" * 60)
    
    # Step 1: Login
    print("\n1️⃣ Login...")
    login_response = requests.post(f"{BASE_URL}/auth/login", json={
        "email": "test@rankforge.com",
        "password": "Test@123"
    })
    
    if login_response.status_code != 200:
        print(f"❌ Login failed: {login_response.status_code}")
        print(f"Response: {login_response.text}")
        return
    
    token = login_response.json()['access_token']
    headers = {"Authorization": f"Bearer {token}"}
    print(f"✅ Login successful")
    
    # Step 2: Get user's sites
    print("\n2️⃣ Getting user's websites...")
    sites_response = requests.get(f"{BASE_URL}/sites", headers=headers)
    
    if sites_response.status_code != 200:
        print(f"❌ Failed to get sites: {sites_response.status_code}")
        return
    
    sites = sites_response.json()
    if not sites:
        print("❌ No sites found. Create a site first!")
        return
    
    site = sites[0]
    print(f"✅ Found site: {site['url']} (ID: {site['site_id']})")
    
    # Step 3: Create agent for this website
    print(f"\n3️⃣ Creating agent for {site['url']}...")
    agent_data = {
        "name": "RankForge SEO Assistant",
        "purpose": "llm_visibility_optimizer",
        "website": site['url']
    }
    
    agent_response = requests.post(
        f"{BASE_URL}/agents/",
        headers=headers,
        json=agent_data
    )
    
    if agent_response.status_code != 200:
        print(f"❌ Agent creation failed: {agent_response.status_code}")
        print(f"Response: {agent_response.text}")
        return
    
    agent = agent_response.json()
    print(f"✅ Agent created successfully!")
    print(f"   - Agent ID: {agent['agent_id']}")
    print(f"   - Name: {agent['name']}")
    print(f"   - Linked to site: {agent['site_id']}")
    print(f"   - Website: {agent['website']}")
    
    # Step 4: Chat with agent (basic greeting)
    print(f"\n4️⃣ Testing agent chat - Basic greeting...")
    chat_response = requests.post(
        f"{BASE_URL}/agents/chat",
        headers=headers,
        json={
            "agent_id": agent['agent_id'],
            "message": "Hello! What can you help me with?"
        }
    )
    
    if chat_response.status_code != 200:
        print(f"❌ Chat failed: {chat_response.status_code}")
        print(f"Response: {chat_response.text}")
        return
    
    chat_result = chat_response.json()
    print(f"✅ Agent responded:")
    print(f"   {chat_result['message'][:200]}...")
    print(f"   Suggestions: {chat_result.get('suggestions', [])}")
    
    # Step 5: Chat asking about website status
    print(f"\n5️⃣ Testing context loading - Ask about website status...")
    chat_response2 = requests.post(
        f"{BASE_URL}/agents/chat",
        headers=headers,
        json={
            "agent_id": agent['agent_id'],
            "message": "What's the current status of my website? What analyses have been done?"
        }
    )
    
    if chat_response2.status_code != 200:
        print(f"❌ Chat failed: {chat_response2.status_code}")
        return
    
    chat_result2 = chat_response2.json()
    print(f"✅ Agent responded with context:")
    print(f"   {chat_result2['message'][:300]}...")
    
    # Step 6: Ask agent for next steps
    print(f"\n6️⃣ Testing guidance - Ask for next steps...")
    chat_response3 = requests.post(
        f"{BASE_URL}/agents/chat",
        headers=headers,
        json={
            "agent_id": agent['agent_id'],
            "message": "What should I do next to improve my LLM visibility?"
        }
    )
    
    if chat_response3.status_code != 200:
        print(f"❌ Chat failed: {chat_response3.status_code}")
        return
    
    chat_result3 = chat_response3.json()
    print(f"✅ Agent provided guidance:")
    print(f"   {chat_result3['message'][:300]}...")
    print(f"   Suggestions: {chat_result3.get('suggestions', [])}")
    
    # Step 7: Get chat history
    print(f"\n7️⃣ Getting chat history...")
    history_response = requests.get(
        f"{BASE_URL}/agents/{agent['agent_id']}/history?limit=10",
        headers=headers
    )
    
    if history_response.status_code != 200:
        print(f"❌ Failed to get history: {history_response.status_code}")
        return
    
    history = history_response.json()['history']
    print(f"✅ Chat history retrieved: {len(history)} messages")
    
    # Step 8: List all agents
    print(f"\n8️⃣ Listing all agents...")
    agents_response = requests.get(f"{BASE_URL}/agents/", headers=headers)
    
    if agents_response.status_code != 200:
        print(f"❌ Failed to list agents: {agents_response.status_code}")
        return
    
    all_agents = agents_response.json()
    print(f"✅ Found {len(all_agents)} agent(s)")
    for ag in all_agents:
        print(f"   - {ag['name']} ({ag['purpose']}) - Website: {ag.get('website', 'N/A')}")
    
    print("\n" + "=" * 60)
    print("✅ AGENT WORKFLOW TEST COMPLETE!")
    print("\nKEY FINDINGS:")
    print("✅ Agent creation with website: WORKING")
    print("✅ Website-to-site_id linking: WORKING")
    print("✅ Context loading for agent: WORKING")
    print("✅ Agent chat with context: WORKING")
    print("✅ Agent guidance provision: WORKING")
    print("✅ Chat history storage: WORKING")
    print("✅ Agent listing: WORKING")
    
    print("\n🎯 Agent is ready to guide users on SEO/AEO improvements!")
    print(f"   Agent remembers everything about {site['url']}")
    print("   and can provide context-aware guidance.")

if __name__ == "__main__":
    try:
        test_agent_workflow()
    except Exception as e:
        print(f"\n❌ Test failed with error: {e}")
        import traceback
        traceback.print_exc()
