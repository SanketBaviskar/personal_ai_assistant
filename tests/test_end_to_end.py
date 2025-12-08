
import asyncio
import sys
import os
import json
from unittest.mock import MagicMock, patch

# Add backend to path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app.db.session import SessionLocal
from app.models.user import User
from app.models.credential import UserCredential
from app.models.chat import Conversation, Message
from app.models.document import Document
from app.api.v1.endpoints.chat import ChatRequest

# Mock dependencies
mock_llm = MagicMock()
mock_llm.generate_response.return_value = "This is a mock AI response with citations."

async def run_end_to_end_test():
    print("--- Starting End-to-End Chat API Test ---")
    
    # 1. Setup
    db = SessionLocal()
    try:
        user = db.query(User).filter(User.email == "test_sanity@example.com").first()
        if not user:
            print("Creating test user...")
            user = User(email="test_sanity@example.com", is_active=True)
            db.add(user)
            db.commit()
            db.refresh(user)
        print(f"User ID: {user.id}")
        
        # 2. Mock Services and Call Endpoint Logic
        # We invoke the logic inside the endpoint function conceptually, or import the router?
        # Directly invoking the service logic is easier and tests the core flow.
        
        from app.services.ai_core.memory_service import memory_service
        from app.services.ai_core.retriever import retriever
        
        # Mock LLM generator
        with patch("app.api.v1.endpoints.chat.llm_generator", mock_llm):
            # Simulate the steps in the chat endpoint
            
            query = "What is in the sanity check doc?"
            print(f"\nQuery: {query}")
            
            # A. Retrieve
            print("Retrieving context...")
            retrieval_result = await retriever.retrieve_context(user.id, query)
            context_docs = retrieval_result["chunks"]
            print(f"Retrieved {len(context_docs)} chunks.")
            if len(context_docs) > 0:
                print(f"Top chunk: {context_docs[0]['text'][:50]}...")
            
            # B. Get Conversation
            conv = memory_service.get_or_create_conversation(db, user.id, conversation_id=None)
            print(f"Conversation ID: {conv.id}")
            
            # C. Generate Response (Mocked)
            answer = "This is a verified response from the sanity check."
            
            # D. Save Messages (The critical part we fixed)
            print("Saving API messages...")
            msg_user = memory_service.add_message(db, conv.id, user.id, "user", query)
            msg_asst = memory_service.add_message(db, conv.id, user.id, "assistant", answer)
            
            print(f"User Message Saved: ID {msg_user.id}, UserID {msg_user.user_id}")
            print(f"Asst Message Saved: ID {msg_asst.id}, UserID {msg_asst.user_id}")
            
            if msg_user.user_id != user.id or msg_asst.user_id != user.id:
                 raise Exception(f"FAILED: user_id mismatch! User: {user.id}, MsgUser: {msg_user.user_id}, MsgAsst: {msg_asst.user_id}")
            else:
                 print("SUCCESS: user_id correctly saved in messages.")
                 
    except Exception as e:
        print(f"Test Failed: {e}")
        import traceback
        traceback.print_exc()
    finally:
        db.close()

if __name__ == "__main__":
    asyncio.run(run_end_to_end_test())
