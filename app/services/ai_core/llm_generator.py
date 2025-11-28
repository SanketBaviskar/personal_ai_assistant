import os
import google.generativeai as genai
from typing import List, Dict

class LLMGenerator:
    def __init__(self):
        # In a real app, we would load this from config/env
        # For now, we'll check if the env var is set, otherwise use a mock
        self.api_key = os.getenv("GEMINI_API_KEY")
        if self.api_key:
            genai.configure(api_key=self.api_key)
            self.model = genai.GenerativeModel('gemini-pro')
        else:
            self.model = None
            print("WARNING: GEMINI_API_KEY not set. Using Mock LLM.")

    def generate_response(self, query: str, context: List[Dict], history: List[Dict]) -> str:
        """
        Generates a response using Gemini or a Mock if no key is present.
        """
        
        # 1. Construct Context String
        context_str = "\n\n".join([f"Source ({c['source_metadata'].get('source_app', 'unknown')}): {c['text']}" for c in context])
        
        # 2. Construct System Prompt
        system_prompt = f"""You are a helpful Personal AI Assistant.
Your goal is to answer the user's question using ONLY the provided context.
If the answer is not in the context, politely state that you cannot find the information.
Do not hallucinate or invent facts.

Context:
{context_str}
"""

        # 3. Call LLM
        if self.model:
            try:
                # Gemini ChatSession handles history, but we are managing it manually for control
                # We will construct a full prompt or use chat history object if we want
                # For simplicity and strict control, we'll just append history to prompt or use start_chat
                
                chat = self.model.start_chat(history=[
                    {"role": "user" if h["role"] == "user" else "model", "parts": [h["content"]]} 
                    for h in history
                ])
                
                response = chat.send_message(f"{system_prompt}\n\nUser Question: {query}")
                return response.text
            except Exception as e:
                return f"Error generating response: {str(e)}"
        else:
            # Mock Response
            return f"Mock AI Response to '{query}' based on {len(context)} context items."

llm_generator = LLMGenerator()
