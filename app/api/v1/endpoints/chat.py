from typing import Any, List, Optional
from pydantic import BaseModel
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from starlette.concurrency import run_in_threadpool

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
async def chat(
    request: ChatRequest,
    db: Session = Depends(deps.get_db),
    current_user: models.User = Depends(deps.get_current_active_user),
) -> Any:
    """
    Chat with the Personal AI (Async).
    1. Retrieve Context (Async)
    2. Get/Create Conversation History (Sync -> Thread)
    3. Generate Answer (Async)
    4. Save to Memory (Sync -> Thread)
    """
    # 1. Retrieve Context
    try:
        print(f"Retrieving context for query: {request.query} (Conversation: {request.conversation_id})")
        retrieval_result = await retriever.retrieve_context(current_user.id, request.query, conversation_id=request.conversation_id)
        context_docs = retrieval_result["chunks"]
        context_stats = retrieval_result["stats"]
        print(f"Retrieved {len(context_docs)} docs")
    except Exception as e:
        print(f"Error retrieving context: {e}")
        # Continue without context rather than crashing
        context_docs = []
        context_stats = {}
    
    # 2. Get/Create Conversation (DB Op)
    conversation = await run_in_threadpool(
        memory_service.get_or_create_conversation, db, current_user.id, request.conversation_id
    )
    
    # 3. Get History (DB Op)
    history = await run_in_threadpool(
        memory_service.get_history, db, conversation.id
    )
    
    # 4. Generate Answer (Async / IO Bound)
    try:
        print("Generating LLM response...")
        # Passing stats to LLM generator
        answer = await llm_generator.generate_response(request.query, context_docs, history, context_stats)
        print("LLM response generated")
    except Exception as e:
        print(f"Error generating LLM response: {e}")
        raise HTTPException(status_code=500, detail=f"LLM Generation failed: {str(e)}")
    
    # 5. Save to Memory (DB Op)
    await run_in_threadpool(memory_service.add_message, db, conversation.id, "user", request.query)
    await run_in_threadpool(memory_service.add_message, db, conversation.id, "assistant", answer)
    
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
async def get_conversations(
    db: Session = Depends(deps.get_db),
    current_user: models.User = Depends(deps.get_current_active_user),
) -> Any:
    """
    Get all conversations for the current user (Async).
    """
    conversations = await run_in_threadpool(memory_service.get_user_conversations, db, current_user.id)
    return conversations

@router.get("/{conversation_id}/messages", response_model=List[dict])
async def get_conversation_messages(
    conversation_id: int,
    db: Session = Depends(deps.get_db),
    current_user: models.User = Depends(deps.get_current_active_user),
) -> Any:
    """
    Get messages for a specific conversation (Async).
    """
    # Verify ownership
    conversation = await run_in_threadpool(memory_service.get_or_create_conversation, db, current_user.id, conversation_id)
    if conversation.user_id != current_user.id:
        raise HTTPException(status_code=403, detail="Not authorized")
    
    history = await run_in_threadpool(memory_service.get_history, db, conversation_id, limit=100)
    return history
@router.delete("/{conversation_id}", response_model=dict)
async def delete_conversation(
    conversation_id: int,
    db: Session = Depends(deps.get_db),
    current_user: models.User = Depends(deps.get_current_active_user),
) -> Any:
    """Delete a conversation and its messages for the current user."""
    await run_in_threadpool(memory_service.delete_conversation, db, conversation_id, current_user.id)
    return {"detail": "Conversation deleted"}

