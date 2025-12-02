from typing import Any
from fastapi import APIRouter, Depends, HTTPException, UploadFile, File
from sqlalchemy.orm import Session

from app.api import deps
from app.models import user as models
from app.services.processing.pdf_processor import pdf_processor
from app.services.vector_db import vector_db

router = APIRouter()

@router.post("/upload/pdf")
async def upload_pdf(
    file: UploadFile = File(...),
    db: Session = Depends(deps.get_db),
    current_user: models.User = Depends(deps.get_current_active_user),
) -> Any:
    """
    Upload a PDF file, extract text, and index it for RAG.
    """
    if not file.filename.lower().endswith('.pdf'):
        raise HTTPException(status_code=400, detail="File must be a PDF")

    try:
        contents = await file.read()
        text = pdf_processor.extract_text(contents)
        
        if not text:
             raise HTTPException(status_code=400, detail="Could not extract text from PDF")

        # Indexing
        # For better RAG, we should chunk the text. 
        # For this MVP, we'll do simple chunking by character count if it's too large, 
        # or rely on the vector DB to handle it (though Chroma has limits).
        # Let's do a simple split for now.
        
        chunk_size = 1000
        overlap = 100
        chunks = []
        
        for i in range(0, len(text), chunk_size - overlap):
            chunks.append(text[i:i + chunk_size])
            
        for i, chunk in enumerate(chunks):
            vector_db.index_document(
                user_id=current_user.id,
                text=chunk,
                source_metadata={
                    "source_app": "pdf_upload",
                    "source_url": f"{file.filename}_part_{i}"
                }
            )
            
        return {"message": f"Successfully processed {file.filename}. Indexed {len(chunks)} chunks."}

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to process PDF: {str(e)}")
