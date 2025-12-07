from typing import Any
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from app.api import deps
from app.models import user as models
from app.services.google_service import google_drive_service
from app.services.pgvector_store import pgvector_store

router = APIRouter()

@router.post("/sync/google")
async def sync_google_calendar(
    db: Session = Depends(deps.get_db),
    current_user: models.User = Depends(deps.get_current_active_user),
) -> Any:
    """
    Sync Google Calendar events (Async).
    """
    if not current_user.google_drive_connected:
        raise HTTPException(status_code=400, detail="Google Account not connected")

    try:
        from starlette.concurrency import run_in_threadpool
        
        # 0. Clear existing calendar events to avoid duplicates
        # delete_user_documents is sync
        await run_in_threadpool(pgvector_store.delete_user_documents, current_user.id, "google_calendar")

        # 1. Fetch events (Sync -> Thread)
        events = await run_in_threadpool(google_drive_service.list_calendar_events, current_user)
        
        # 2. Ingest
        count = 0
        for event in events:
            # Format as text
            start = event['start'].get('dateTime', event['start'].get('date'))
            summary = event.get('summary', 'No Title')
            description = event.get('description', '')
            location = event.get('location', '')
            
            content = f"Calendar Event: {summary}\nTime: {start}\nLocation: {location}\nDetails: {description}"
            
            # Create a unique ID for the event
            event_id = f"gcal_{event['id']}"
            
            # Metadata
            metadata = {
                "source_app": "google_calendar",
                "source_url": event.get('htmlLink', ''),
                "file_id": event_id,
                "file_name": f"Event: {summary}",
                "mime_type": "application/vnd.google-apps.event",
                "chunk_index": 0
            }
            
            # Ingest (Async)
            await pgvector_store.index_document(current_user.id, content, metadata)
            count += 1
            
        return {"message": f"Synced {count} calendar events"}
        
    except Exception as e:
        print(f"Calendar Sync error: {e}")
        raise HTTPException(status_code=500, detail=f"Sync failed: {str(e)}")
