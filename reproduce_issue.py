import requests
import sys

API_URL = "http://localhost:8001/api/v1"

def reproduce():
    # 1. Signup/Login
    email = "test@example.com"
    password = "password123"
    
    print(f"Attempting to login with {email}...")
    response = requests.post(f"{API_URL}/auth/login/access-token", data={"username": email, "password": password})
    
    if response.status_code != 200:
        print("Login failed, attempting signup...")
        response = requests.post(f"{API_URL}/auth/signup", json={"email": email, "password": password, "full_name": "Test User"})
        if response.status_code != 200:
            print(f"Signup failed: {response.text}")
            return
        print("Signup successful, logging in...")
        response = requests.post(f"{API_URL}/auth/login/access-token", data={"username": email, "password": password})
        if response.status_code != 200:
            print(f"Login failed after signup: {response.text}")
            return

    token = response.json()["access_token"]
    headers = {"Authorization": f"Bearer {token}"}
    print("Login successful.")

    # 2. Create Conversation (or get existing)
    print("Fetching conversations...")
    response = requests.get(f"{API_URL}/chat/conversations", headers=headers)
    if response.status_code != 200:
        print(f"Failed to fetch conversations: {response.text}")
        return
    
    conversations = response.json()
    conversation_id = None
    if conversations:
        conversation_id = conversations[0]["id"]
        print(f"Using existing conversation {conversation_id}")
    else:
        print("No conversations found, will create one with first message.")

    # 3. Send Message
    print("Sending message...")
    message_data = {"query": "Hello, this is a test message."}
    if conversation_id:
        message_data["conversation_id"] = conversation_id
    
    response = requests.post(f"{API_URL}/chat/", json=message_data, headers=headers)
    if response.status_code != 200:
        print(f"Failed to send message: {response.text}")
        return
    
    response_data = response.json()
    conversation_id = response_data["conversation_id"]
    print(f"Message sent. Conversation ID: {conversation_id}")
    print(f"Response: {response_data['answer']}")

    # 4. Get Messages
    print(f"Fetching messages for conversation {conversation_id}...")
    response = requests.get(f"{API_URL}/chat/{conversation_id}/messages", headers=headers)
    if response.status_code != 200:
        print(f"Failed to fetch messages: {response.text}")
        return
    
    messages = response.json()
    with open("reproduce_output.txt", "w") as f:
        f.write(f"Messages ({len(messages)}):\n")
        for msg in messages:
            f.write(f"- [{msg['role']}] {msg['content']}\n")
    print("Output written to reproduce_output.txt")

if __name__ == "__main__":
    reproduce()
