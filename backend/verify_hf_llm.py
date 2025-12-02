import sys
import os
# Add backend directory to path so we can import app
sys.path.append(os.path.join(os.getcwd(), 'backend'))

from app.services.ai_core.llm_generator import llm_generator
from unittest.mock import MagicMock, patch

def test_hf_llm():
    print("Testing Hugging Face LLM Generator...")
    
    # Mock requests.post
    with patch('requests.post') as mock_post:
        mock_response = MagicMock()
        mock_response.json.return_value = [{"generated_text": " This is a test response from HF."}]
        mock_response.raise_for_status.return_value = None
        mock_post.return_value = mock_response
        
        # Test with mock key if not set
        if not llm_generator.api_key:
            llm_generator.api_key = "mock_key"
            
        response = llm_generator.generate_response(
            query="Hello",
            context=[{"text": "Context 1", "source_metadata": {"source_app": "test"}}],
            history=[]
        )
        
        print(f"Response: {response}")
        assert "This is a test response" in response
        print("HF LLM Test Passed!")

if __name__ == "__main__":
    test_hf_llm()
