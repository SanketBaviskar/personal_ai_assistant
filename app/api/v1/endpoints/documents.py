from typing import Any, List
from fastapi import APIRouter, Depends, HTTPException, UploadFile, File, BackgroundTasks
from sqlalchemy.orm import Session

from app.api import deps
from app.models import user as models
from app.models.document import Document
from app.services.processing.pdf_processor import pdf_processor
from app.services.pgvector_store import pgvector_store
from app.db.session import SessionLocal

router = APIRouter()

def process_pdf_background(document_id: int, file_content: bytes):
    db = SessionLocal()
    try:
        doc = db.query(Document).filter(Document.id == document_id).first()
        if not doc:
            return
        
        doc.status = "processing"
        db.commit()
        
        text = pdf_processor.extract_text(file_content)
        if not text:
            doc.status = "failed"
            doc.error_message = "Could not extract text"
            db.commit()
            return

        chunk_size = 1000
        overlap = 100
        chunks = []
        
        for i in range(0, len(text), chunk_size - overlap):
            chunks.append(text[i:i + chunk_size])
            
        for i, chunk in enumerate(chunks):
            pgvector_store.index_document(
                user_id=doc.user_id,
                content=chunk,
                source_metadata={
                    "source_app": "pdf_upload",
                    "source_url": f"{doc.filename}_part_{i}"
                }
            )
            
        doc.status = "completed"
        db.commit()
        
    except Exception as e:
        print(f"Error processing PDF {document_id}: {e}")
        doc.status = "failed"
        doc.error_message = str(e)
        db.commit()
    finally:
        db.close()

@router.post("/upload/pdf")
async def upload_pdf(
    background_tasks: BackgroundTasks,
    file: UploadFile = File(...),
    db: Session = Depends(deps.get_db),
    current_user: models.User = Depends(deps.get_current_active_user),
) -> Any:
    """
    Upload a PDF file, extract text, and index it for RAG (Background).
    """
    if not file.filename.lower().endswith('.pdf'):
        raise HTTPException(status_code=400, detail="File must be a PDF")

    try:
        contents = await file.read()
        
        if len(contents) > 10 * 1024 * 1024:
            raise HTTPException(status_code=413, detail="File too large. Limit is 10MB.")

        # Create Document record immediately
        doc = Document(
            user_id=current_user.id,
            filename=file.filename,
            file_size=len(contents),
            status="pending"
        )
        db.add(doc)
        db.commit()
        db.refresh(doc)
        
        # Enqueue background task
        background_tasks.add_task(process_pdf_background, doc.id, contents)

        return {"message": "File uploaded. Processing in background.", "document_id": doc.id, "status": "pending"}

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to initiate upload: {str(e)}")

@router.get("/", response_model=List[dict])
def get_documents(
    db: Session = Depends(deps.get_db),
    current_user: models.User = Depends(deps.get_current_active_user),
) -> Any:
    """
    Get all uploaded documents for the current user.
    """
    documents = db.query(Document).filter(Document.user_id == current_user.id).order_by(Document.created_at.desc()).all()
    return [{"id": d.id, "filename": d.filename, "created_at": d.created_at, "file_size": d.file_size, "status": d.status, "error_message": d.error_message} for d in documents]
