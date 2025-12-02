import requests
import os
import sys

# Add parent directory to path to import from app
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# Simple .env parser
def load_env():
    env_path = os.path.join(os.path.dirname(os.path.dirname(__file__)), '.env')
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
    print("\n--- Checking LLM Connectivity ---")
    api_key = os.environ.get("HUGGINGFACE_API_KEY")
    model_id = os.environ.get("HUGGINGFACE_MODEL", "openai/gpt-oss-120b") # Default to free model
    
    if not api_key:
        print("❌ HUGGINGFACE_API_KEY not found in environment variables.")
        return

    masked_key = api_key[:4] + "*" * (len(api_key) - 8) + api_key[-4:] if len(api_key) > 8 else "****"
    print(f"ℹ️  Loaded API Key: {masked_key}")
    print(f"ℹ️  Using Model: {model_id}")
    
    try:
        from huggingface_hub import InferenceClient
        
        client = InferenceClient(token=api_key)
        
        print("   Sending request to Hugging Face (InferenceClient)...")
        completion = client.chat.completions.create(
            model=model_id,
            messages=[
                {
                    "role": "user",
                    "content": "Hello, are you working?"
                }
            ],
            max_tokens=20
        )
        
        response_text = completion.choices[0].message.content
        print("✅ LLM API is ACCESSIBLE")
        print(f"   Response: {response_text}")
            
    except Exception as e:
        print(f"❌ Failed to connect to LLM API: {e}")
if __name__ == "__main__":
    load_env()
    server_up = check_server_health()
    if server_up:
        check_llm_connectivity()
    else:
        print("\n⚠️  Skipping LLM check because backend server is down.")
