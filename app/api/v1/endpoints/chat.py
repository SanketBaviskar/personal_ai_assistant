from typing import Any, List, Optional
from pydantic import BaseModel
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.api import deps
from app.models import user as models
from app.services.ai_core.retriever import retriever
from app.services.ai_core.memory_service import memory_service
from app.services.ai_core.llm_generator import llm_generator

router = APIRouter()

class ChatRequest(BaseModel):
    query: str
    conversation_id: Optional[int] = None

class SourceMetadata(BaseModel):
    source_app: str
    source_url: Optional[str] = None
    # Add other metadata fields as needed

class Source(BaseModel):
    text: str
    metadata: SourceMetadata

class ChatResponse(BaseModel):
    answer: str
    sources: List[Source]
    conversation_id: int

@router.post("/", response_model=ChatResponse)
def chat(
    request: ChatRequest,
    db: Session = Depends(deps.get_db),
    current_user: models.User = Depends(deps.get_current_active_user),
) -> Any:
    """
    Chat with the Personal AI.
    1. Retrieve Context
    2. Get/Create Conversation History
    3. Generate Answer
    4. Save to Memory
    """
    # 1. Retrieve Context
    context_docs = retriever.retrieve_context(current_user.id, request.query)
    
    # 2. Get/Create Conversation
    conversation = memory_service.get_or_create_conversation(db, current_user.id, request.conversation_id)
    
    # 3. Get History
    history = memory_service.get_history(db, conversation.id)
    
    # 4. Generate Answer
    answer = llm_generator.generate_response(request.query, context_docs, history)
    
    # 5. Save to Memory
    memory_service.add_message(db, conversation.id, "user", request.query)
    memory_service.add_message(db, conversation.id, "assistant", answer)
    
    # Format Sources
    sources = []
    for doc in context_docs:
        sources.append(Source(
            text=doc['text'][:200] + "...", # Snippet
            metadata=SourceMetadata(**doc['source_metadata'])
        ))
        
    return ChatResponse(
        answer=answer,
        sources=sources,
        conversation_id=conversation.id
    )

@router.get("/conversations", response_model=List[dict])
def get_conversations(
    db: Session = Depends(deps.get_db),
    current_user: models.User = Depends(deps.get_current_active_user),
) -> Any:
    """
    Get all conversations for the current user.
    """
    # We need to add a method to memory_service to list conversations
    # For now, we'll do a direct query here or add it to memory_service
    # Let's add it to memory_service first.
    # Wait, I can't modify memory_service in this same tool call.
    # I'll do a direct query for now to save time, or better, add it to memory_service in next step.
    # Actually, I'll add the endpoint definition here and implement the service method in the next step.
    conversations = memory_service.get_user_conversations(db, current_user.id)
    return conversations

@router.get("/{conversation_id}/messages", response_model=List[dict])
def get_conversation_messages(
    conversation_id: int,
    db: Session = Depends(deps.get_db),
    current_user: models.User = Depends(deps.get_current_active_user),
) -> Any:
    """
    Get messages for a specific conversation.
    """
    # Verify ownership
    conversation = memory_service.get_or_create_conversation(db, current_user.id, conversation_id)
    if conversation.user_id != current_user.id:
        raise HTTPException(status_code=403, detail="Not authorized")
    
    history = memory_service.get_history(db, conversation_id, limit=100)
    return history

