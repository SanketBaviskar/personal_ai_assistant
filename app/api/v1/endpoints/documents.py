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
        print(f"DEBUG: Document {document_id} extracted text length: {len(text) if text else 0}")
        if not text:
            print("DEBUG: Text extraction failed (empty)")
            doc.status = "failed"
            doc.error_message = "Could not extract text"
            db.commit()
            return

        from app.services.processing.chunker import chunker
        chunks = chunker.chunk_text(text)
        print(f"DEBUG: Generated {len(chunks)} chunks")
            
        for i, chunk in enumerate(chunks):
            pgvector_store.index_document(
                user_id=doc.user_id,
                content=chunk,
                source_metadata={
                    "source_app": "pdf_upload",
                    "source_url": f"uploaded_pdf://{doc.id}",
                    "file_id": f"upload_{doc.id}",
                    "file_name": doc.filename,
                    "mime_type": "application/pdf",
                    "chunk_index": i,
                    "conversation_id": doc.conversation_id
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

from fastapi import Form

@router.post("/upload/pdf")
async def upload_pdf(
    background_tasks: BackgroundTasks,
    file: UploadFile = File(...),
    conversation_id: int = Form(None), # Must use Form for multipart
    db: Session = Depends(deps.get_db),
    current_user: models.User = Depends(deps.get_current_active_user),
) -> Any:
    """
    Upload a PDF file, extract text, and index it for RAG (Background).
    Supports scoping to a conversation.
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
            status="pending",
            conversation_id=conversation_id
        )
        db.add(doc)
        db.commit()
        db.refresh(doc)
        
        # Enqueue background task
        background_tasks.add_task(process_pdf_background, doc.id, contents)

        return {"message": "File uploaded. Processing in background.", "document_id": doc.id, "status": "pending"}

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to initiate upload: {str(e)}")

@router.delete("/{document_id}")
def delete_document(
    document_id: int,
    db: Session = Depends(deps.get_db),
    current_user: models.User = Depends(deps.get_current_active_user),
) -> Any:
    """
    Delete a document and its embeddings.
    """
    doc = db.query(Document).filter(Document.id == document_id, Document.user_id == current_user.id).first()
    if not doc:
        raise HTTPException(status_code=404, detail="Document not found")
        
    try:
        # Delete from Vector Store first
        file_id = f"upload_{doc.id}"
        pgvector_store.delete_document_by_file_id(current_user.id, file_id)
        
        # Delete from DB
        db.delete(doc)
        db.commit()
        
        return {"message": "Document deleted"}
    except Exception as e:
        print(f"Error deleting document {document_id}: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to delete document: {str(e)}")

@router.get("/", response_model=List[dict])
def get_documents(
    conversation_id: int = None,
    db: Session = Depends(deps.get_db),
    current_user: models.User = Depends(deps.get_current_active_user),
) -> Any:
    """
    Get all uploaded documents for the current user, optionally filtered by conversation.
    """
    query = db.query(Document).filter(Document.user_id == current_user.id)
    if conversation_id:
        query = query.filter((Document.conversation_id == conversation_id) | (Document.conversation_id == None))
    
    documents = query.order_by(Document.created_at.desc()).all()
    return [{"id": d.id, "filename": d.filename, "created_at": d.created_at, "file_size": d.file_size, "status": d.status, "error_message": d.error_message, "conversation_id": d.conversation_id} for d in documents]
