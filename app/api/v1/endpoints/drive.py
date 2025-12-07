from typing import Any, List
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from app.api import deps
from app.models import user as models
from app.services.google_service import google_drive_service
from app.services.rag_service import rag_service
from app.services.pgvector_store import pgvector_store

router = APIRouter()

@router.post("/sync")
def sync_drive_files(
    db: Session = Depends(deps.get_db),
    current_user: models.User = Depends(deps.get_current_active_user),
) -> Any:
    """
    Sync Google Drive files (list and ingest).
    """
    if not current_user.google_drive_connected:
        raise HTTPException(status_code=400, detail="Google Drive not connected")

    try:
        # 1. List files
        files = google_drive_service.list_files(current_user)
        
        # 2. Ingest each file
        count = 0
        skipped = 0
        for file in files:
            # Check if file is already ingested (Incremental Sync)
            if pgvector_store.has_document(current_user.id, file['id']):
                print(f"Skipping existing file: {file['name']}")
                skipped += 1
                continue
                
            rag_service.ingest_file(current_user, file['id'], file['mimeType'], file['name'])
            count += 1
            
        return {"message": f"Synced {count} new files (Skipped {skipped} existing)"}
        
    except Exception as e:
        # Log error
        print(f"Sync error: {e}")
        raise HTTPException(status_code=500, detail=f"Sync failed: {str(e)}")

@router.get("/files")
def list_drive_files(
    db: Session = Depends(deps.get_db),
    current_user: models.User = Depends(deps.get_current_active_user),
) -> Any:
    """
    List connected Google Drive files.
    """
    if not current_user.google_drive_connected:
        raise HTTPException(status_code=400, detail="Google Drive not connected")
        
    try:
        files = google_drive_service.list_files(current_user)
        return files
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to list files: {str(e)}")
