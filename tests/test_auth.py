import requests
import sys

# Update port to 8001 as per current configuration
BASE_URL = "http://localhost:8001/api/v1"

def test_signup():
    print("Testing Signup...")
    payload = {
        "email": "test@example.com",
        "password": "password123"
    }
    response = requests.post(f"{BASE_URL}/auth/signup", json=payload)
    if response.status_code == 200:
        print("Signup Successful:", response.json())
        return True
    elif response.status_code == 400 and "already exists" in response.text:
        print("User already exists, proceeding...")
        return True
    else:
        print("Signup Failed:", response.text)
        return False

def test_login():
    print("Testing Login...")
    payload = {
        "username": "test@example.com",
        "password": "password123"
    }
    response = requests.post(f"{BASE_URL}/auth/login/access-token", data=payload)
    if response.status_code == 200:
        token = response.json()["access_token"]
        print("Login Successful. Token obtained.")
        return token
    else:
        print("Login Failed:", response.text)
        return None

def test_me(token):
    print("Testing /users/me...")
    headers = {"Authorization": f"Bearer {token}"}
    response = requests.get(f"{BASE_URL}/users/me", headers=headers)
    if response.status_code == 200:
        print("User Info Retrieved:", response.json())
        return True
    else:
        print("Failed to get user info:", response.text)
        return False

if __name__ == "__main__":
    # Ensure server is running before running this script
    try:
        if not test_signup():
            sys.exit(1)
        token = test_login()
        if not token:
            sys.exit(1)
        if not test_me(token):
            sys.exit(1)
        print("\nAll tests passed!")
    except requests.exceptions.ConnectionError:
        print(f"\nError: Could not connect to server. Is it running on port 8001?")
