from fastapi import APIRouter, UploadFile, HTTPException, Depends
from sqlalchemy.orm import Session
from services.document_service import handle_upload
from services.analysis_service import analyze_document
from db.database import SessionLocal
from models.document import Document

router = APIRouter()

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

@router.post("/upload")
async def upload_document(file: UploadFile):
    doc = await handle_upload(file)
    return {"id": str(doc.id), "file_name": doc.file_name}


@router.post("/{id}/analyze")
async def analyze_doc(id: str):
    # ID is now a UUID string, no integer conversion needed.
    # Service now raises HTTPExceptions for errors (404, 400, 500, 502)
    # We just await the result.
    await analyze_document(id)
    
    return {"message": "Analysis complete"}


@router.get("/{id}")
async def get_doc(id: str, db: Session = Depends(get_db)):
    # ID is now a UUID string
    doc = db.query(Document).filter(Document.id == id).first()
    if not doc:
        raise HTTPException(status_code=404, detail="Not Found")
    
    response = {
        "id": str(doc.id),
        "file_name": doc.file_name,
        "text": doc.text
    }

    if doc.summary or doc.detected_type or doc.attributes:
         response.update({
            "summary": doc.summary,
            "detected_type": doc.detected_type,
            "attributes": doc.attributes
        })

    return response
