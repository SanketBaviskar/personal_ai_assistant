import sys
import os
# Add backend directory to path so we can import app
sys.path.append(os.path.join(os.getcwd(), 'backend'))

from app.services.ai_core.llm_generator import llm_generator

def test_real_hf():
    print("Testing Real Hugging Face API...")
    
    if not llm_generator.api_key:
        print("Error: API Key not found in settings.")
        return

    # Override for testing
    llm_generator.model_id = "google/gemma-2-9b-it"
    llm_generator.api_url = f"https://api-inference.huggingface.co/models/{llm_generator.model_id}"
    print(f"Using Model: {llm_generator.model_id}")
    
    try:
        response = llm_generator.generate_response(
            query="What is the capital of France?",
            context=[],
            history=[]
        )
        print("\nResponse from API:")
        print(response)
        
        if "Paris" in response or "paris" in response:
            print("\nSUCCESS: Real API call worked!")
        else:
            print("\nWARNING: API call worked but response was unexpected.")
            
    except Exception as e:
        print(f"\nFAILED: {e}")

if __name__ == "__main__":
    test_real_hf()
