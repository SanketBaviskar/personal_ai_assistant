import os
import google.generativeai as genai
from typing import List, Dict
from app.core.config import settings

class LLMGenerator:
    def __init__(self):
        self.api_key = settings.GOOGLE_API_KEY
        
        if not self.api_key:
            print("WARNING: GOOGLE_API_KEY not set. Using Mock LLM.")
            self.model = None
        else:
            genai.configure(api_key=self.api_key)
            self.model = genai.GenerativeModel('gemini-pro')

    def generate_response(self, query: str, context: List[Dict], history: List[Dict]) -> str:
        """
        Generates a response using Google Gemini API.
        """
        if not self.model:
             return f"Mock AI Response to '{query}' based on {len(context)} context items. (Set GOOGLE_API_KEY to use real model)"

        # 1. Construct Context String
        context_str = "\n\n".join([f"Source ({c['source_metadata'].get('source_app', 'unknown')}): {c['text']}" for c in context])
        
        # 2. Construct Prompt
        system_prompt = f"""You are a helpful Personal AI Assistant.
Your goal is to answer the user's question using ONLY the provided context.
If the answer is not in the context, politely state that you cannot find the information.
Do not hallucinate or invent facts.

Context:
{context_str}"""

        # 3. Build Chat History for Gemini
        # Gemini expects history as a list of Content objects or dicts: {'role': 'user'|'model', 'parts': [text]}
        chat_history = []
        
        # Add system prompt as the first user message (common pattern for models without system role)
        # Or we can just prepend it to the first message. Let's prepend to current query for simplicity 
        # or keep it as a separate context block if using chat.
        
        # We will use the generate_content method which is stateless-ish if we provide full history manually,
        # or we can use start_chat. Let's use generate_content with full history constructed manually 
        # to match the previous stateless design of this class.
        
        # Actually, for RAG, it's often better to just construct a single big prompt with history included
        # to ensure the context is attended to correctly.
        
        full_prompt = f"{system_prompt}\n\n"
        
        for msg in history:
            role = "User" if msg["role"] == "user" else "Model"
            full_prompt += f"{role}: {msg['content']}\n"
            
        full_prompt += f"User: {query}\nModel:"
        
        try:
            response = self.model.generate_content(full_prompt)
            return response.text
                
        except Exception as e:
            return f"Error generating response: {str(e)}"

llm_generator = LLMGenerator()
