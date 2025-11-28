from sqlalchemy.orm import Session
from app.models.chat import Conversation, Message
from typing import List, Dict, Any

class MemoryService:
    def get_or_create_conversation(self, db: Session, user_id: int, conversation_id: int = None) -> Conversation:
        if conversation_id:
            conversation = db.query(Conversation).filter(Conversation.id == conversation_id, Conversation.user_id == user_id).first()
            if conversation:
                return conversation
        
        # Create new if not found or not provided
        new_conversation = Conversation(user_id=user_id, title="New Conversation")
        db.add(new_conversation)
        db.commit()
        db.refresh(new_conversation)
        return new_conversation

    def add_message(self, db: Session, conversation_id: int, role: str, content: str) -> Message:
        message = Message(conversation_id=conversation_id, role=role, content=content)
        db.add(message)
        db.commit()
        db.refresh(message)
        return message

    def get_history(self, db: Session, conversation_id: int, limit: int = 10) -> List[Dict[str, str]]:
        messages = db.query(Message).filter(Message.conversation_id == conversation_id).order_by(Message.created_at.asc()).limit(limit).all()
        return [{"role": m.role, "content": m.content} for m in messages]

memory_service = MemoryService()
