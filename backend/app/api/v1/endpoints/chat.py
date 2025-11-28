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
