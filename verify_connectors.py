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

def test_connector(token, provider, credentials):
    print(f"\nTesting {provider} Connector...")
    headers = {"Authorization": f"Bearer {token}"}
    
    # 1. Store Credentials
    print(f"Storing credentials for {provider}...")
    resp = requests.post(f"{BASE_URL}/connectors/{provider}", json=credentials, headers=headers)
    if resp.status_code != 200:
        print(f"Failed to store credentials: {resp.text}")
        return False
    print("Credentials stored.")

    # 2. Sync Data
    print(f"Syncing data from {provider}...")
    resp = requests.post(f"{BASE_URL}/connectors/{provider}/sync", headers=headers)
    if resp.status_code == 200:
        data = resp.json()
        print(f"Sync Successful. Fetched {len(data['data'])} items.")
        print("Sample Item:", data['data'][0])
        return True
    else:
        print(f"Sync Failed: {resp.text}")
        return False

if __name__ == "__main__":
    token = get_auth_token()
    if not token:
        sys.exit(1)

    # Test Notion
    if not test_connector(token, "notion", {"api_key": "secret_notion_123"}):
        sys.exit(1)

    # Test Jira
    if not test_connector(token, "jira", {"domain": "jira.example.com", "email": "user@example.com", "api_token": "token123"}):
        sys.exit(1)

    # Test Email
    if not test_connector(token, "email", {"access_token": "mock_token"}):
        sys.exit(1)

    print("\nAll Connector Tests Passed!")
