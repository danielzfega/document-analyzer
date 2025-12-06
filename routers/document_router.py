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
    # Ensure ID is integer if DB uses integer PK, or handle str/int conversion
    # The Document model uses Integer PK. But the router takes 'id: str'.
    # We should convert.
    try:
        doc_id = int(id)
    except ValueError:
         raise HTTPException(status_code=400, detail="Invalid ID format, must be integer")

    result = await analyze_document(doc_id)
    if not result:
        raise HTTPException(status_code=404, detail="Document not found or analysis failed")
    return {"message": "Analysis complete"}


@router.get("/{id}")
async def get_doc(id: str, db: Session = Depends(get_db)):
    try:
        doc_id = int(id)
    except ValueError:
         raise HTTPException(status_code=400, detail="Invalid ID format, must be integer")

    doc = db.query(Document).filter(Document.id == doc_id).first()
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
