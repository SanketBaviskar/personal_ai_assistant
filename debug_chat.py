import requests
import os

# 1. Login to get token (using a fake Google token for now, assuming backend accepts it if configured loosely, 
# OR use the signup endpoint if available. 
# Actually, the backend auth/google endpoint verifies the token.
# So we need a valid token OR we can use the signup endpoint if it exists.
# Let's check auth.py again. It has /signup.

BASE_URL = "http://localhost:8001/api/v1"

def debug_chat():
    # 1. Signup/Login
    email = "testuser@example.com"
    password = "testpassword"
    
    # Try login first
    print("Attempting login...")
    response = requests.post(f"{BASE_URL}/auth/login/access-token", data={"username": email, "password": password})
    
    if response.status_code != 200:
        print("Login failed, attempting signup...")
        # Try signup
        response = requests.post(f"{BASE_URL}/auth/signup", json={"email": email, "password": password})
        if response.status_code != 200:
            print(f"Signup failed: {response.text}")
            return
        
        # Login again
        response = requests.post(f"{BASE_URL}/auth/login/access-token", data={"username": email, "password": password})
        if response.status_code != 200:
            print(f"Login failed after signup: {response.text}")
            return

    token = response.json()["access_token"]
    print(f"Got token: {token[:10]}...")

    # 2. Send Chat Request
    print("Sending chat request...")
    headers = {"Authorization": f"Bearer {token}"}
    data = {
        "query": "Hello, who are you?",
        "conversation_id": None
    }
    
    try:
        response = requests.post(f"{BASE_URL}/chat/", json=data, headers=headers)
        print(f"Status Code: {response.status_code}")
        print(f"Response: {response.text}")
    except Exception as e:
        print(f"Request failed: {e}")

if __name__ == "__main__":
    debug_chat()
