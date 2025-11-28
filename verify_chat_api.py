import requests
import sys

BASE_URL = "http://localhost:8000/api/v1"

def get_auth_token():
    payload = {
        "username": "test@example.com",
        "password": "password123"
    }
    response = requests.post(f"{BASE_URL}/auth/login/access-token", data=payload)
    if response.status_code == 200:
        return response.json()["access_token"]
    else:
        print("Login Failed:", response.text)
        return None

def test_chat(token):
    print("\nTesting Chat API...")
    headers = {"Authorization": f"Bearer {token}"}
    
    # 1. First Query
    print("Sending Query 1: 'What is in the project plan?'")
    payload = {"query": "What is in the project plan?"}
    resp = requests.post(f"{BASE_URL}/chat/", json=payload, headers=headers)
    
    if resp.status_code != 200:
        print(f"Chat Request Failed: {resp.text}")
        return False
        
    data = resp.json()
    print("Response:", data['answer'])
    print("Sources:", len(data['sources']))
    conversation_id = data['conversation_id']
    print(f"Conversation ID: {conversation_id}")
    
    assert conversation_id is not None
    
    # 2. Follow-up Query (Testing Memory)
    print("\nSending Query 2 (Follow-up): 'Who is working on it?'")
    payload = {"query": "Who is working on it?", "conversation_id": conversation_id}
    resp = requests.post(f"{BASE_URL}/chat/", json=payload, headers=headers)
    
    if resp.status_code != 200:
        print(f"Follow-up Request Failed: {resp.text}")
        return False
        
    data = resp.json()
    print("Response:", data['answer'])
    assert data['conversation_id'] == conversation_id
    
    print("\nChat API Test Passed!")
    return True

if __name__ == "__main__":
    token = get_auth_token()
    if not token:
        sys.exit(1)

    if not test_chat(token):
        sys.exit(1)
