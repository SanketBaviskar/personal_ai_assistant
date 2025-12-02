import requests
import os
import sys

# Simple .env parser
def load_env():
    env_path = os.path.join(os.path.dirname(__file__), '.env')
    if os.path.exists(env_path):
        with open(env_path, 'r') as f:
            for line in f:
                line = line.strip()
                if not line or line.startswith('#'):
                    continue
                if '=' in line:
                    key, value = line.split('=', 1)
                    os.environ[key.strip()] = value.strip()

def check_server_health():
    print("\n--- Checking Backend Server Health ---")
    try:
        response = requests.get("http://localhost:8001/")
        if response.status_code == 200:
            print("✅ Backend Server is RUNNING at http://localhost:8001/")
            print(f"   Response: {response.json()}")
            return True
        else:
            print(f"❌ Backend Server returned status code: {response.status_code}")
            return False
    except requests.exceptions.ConnectionError:
        print("❌ Backend Server is NOT RUNNING (Connection Refused)")
        print("   Please start the server with: uvicorn app.main:app --reload --port 8001")
        return False

def check_llm_connectivity():
    print("\n--- Checking LLM Connectivity (Gemini) ---")
    api_key = os.environ.get("GOOGLE_API_KEY")
    
    if not api_key:
        print("❌ GOOGLE_API_KEY not found in environment variables.")
        return

    masked_key = api_key[:4] + "*" * (len(api_key) - 8) + api_key[-4:] if len(api_key) > 8 else "****"
    print(f"ℹ️  Loaded API Key: {masked_key}")
    
    try:
        import google.generativeai as genai
        genai.configure(api_key=api_key)
        model = genai.GenerativeModel('gemini-pro')
        
        print("   Sending request to Gemini...")
        response = model.generate_content("Hello, are you working?")
        
        if response.text:
            print("✅ LLM API is ACCESSIBLE")
            print(f"   Response: {response.text}")
        else:
            print("❌ LLM API returned empty response.")
            
    except Exception as e:
        print(f"❌ Failed to connect to LLM API: {e}")
if __name__ == "__main__":
    load_env()
    server_up = check_server_health()
    if server_up:
        check_llm_connectivity()
    else:
        print("\n⚠️  Skipping LLM check because backend server is down.")
