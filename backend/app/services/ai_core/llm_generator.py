import os
from openai import OpenAI
from typing import List, Dict
from app.core.config import settings

class LLMGenerator:
    def __init__(self):
        self.api_key = settings.HUGGINGFACE_API_KEY
        self.model_id = settings.HUGGINGFACE_MODEL
        
        if not self.api_key:
            print("WARNING: HUGGINGFACE_API_KEY not set. Using Mock LLM.")
            self.client = None
        else:
            # Use OpenAI client with HF router (OpenAI-compatible API)
            self.client = OpenAI(
                base_url="https://router.huggingface.co/v1",
                api_key=self.api_key
            )

    def generate_response(self, query: str, context: List[Dict], history: List[Dict]) -> str:
        """
        Generates a response using Hugging Face Inference API (OpenAI-compatible).
        """
        if not self.client:
             return f"Mock AI Response to '{query}' based on {len(context)} context items. (Set HUGGINGFACE_API_KEY to use real model)"

        # 1. Construct Context String
        context_str = "\n\n".join([f"Source ({c['source_metadata'].get('source_app', 'unknown')}): {c['text']}" for c in context])
        
        # 2. Construct System Message
        system_message = f"""You are a helpful Personal AI Assistant.
Your goal is to answer the user's question using ONLY the provided context.
If the answer is not in the context, politely state that you cannot find the information.
Do not hallucinate or invent facts.

Context:
{context_str}"""

        # 3. Build message list (OpenAI chat format)
        messages = [{"role": "system", "content": system_message}]
        
        # Add conversation history
        for msg in history:
            messages.append({
                "role": msg["role"],
                "content": msg["content"]
            })
        
        # Add current query
        messages.append({
            "role": "user",
            "content": query
        })

        # 4. Call HF API via OpenAI client
        try:
            completion = self.client.chat.completions.create(
                model=self.model_id,
                messages=messages,
                max_tokens=512,
                temperature=0.7,
                top_p=0.95
            )
            
            return completion.choices[0].message.content.strip()
                
        except Exception as e:
            return f"Error generating response: {str(e)}"

llm_generator = LLMGenerator()
