import requests
import os

API_URL = "http://localhost:8001/api/v1"

def verify_file_limit():
    # 1. Login
    email = "test@example.com"
    password = "password123"
    
    print(f"Logging in as {email}...")
    response = requests.post(f"{API_URL}/auth/login/access-token", data={"username": email, "password": password})
    if response.status_code != 200:
        print(f"Login failed: {response.text}")
        return
    token = response.json()["access_token"]
    headers = {"Authorization": f"Bearer {token}"}
    
    # 2. Create large file (11MB)
    print("Creating large file...")
    with open("large_file.pdf", "wb") as f:
        f.write(b"0" * (11 * 1024 * 1024))
        
    try:
        # 3. Upload large file
        print("Uploading large file...")
        files = {'file': ('large_file.pdf', open("large_file.pdf", "rb"), 'application/pdf')}
        
        response = requests.post(f"{API_URL}/documents/upload/pdf", headers=headers, files=files)
        
        if response.status_code == 413:
            print("SUCCESS: Backend rejected large file (413 Payload Too Large).")
        else:
            print(f"FAILURE: Backend returned {response.status_code}: {response.text}")
            
    finally:
        # Cleanup
        if os.path.exists("large_file.pdf"):
            os.remove("large_file.pdf")

if __name__ == "__main__":
    verify_file_limit()
