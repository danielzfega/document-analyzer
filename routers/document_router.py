from fastapi import APIRouter, UploadFile, HTTPException
from app.services.document_service import handle_upload
from app.services.analysis_service import analyze_document
from app.database.session import db
from app.database.models.document import Document

router = APIRouter()

@router.post("/upload")
async def upload_document(file: UploadFile):
    doc = await handle_upload(file)
    return {"id": str(doc.id), "file_name": doc.file_name}


@router.post("/{id}/analyze")
async def analyze_doc(id: str):
    result = await analyze_document(id)
    if not result:
        raise HTTPException(status_code=404, detail="Document not found")
    return {"message": "Analysis complete"}


@router.get("/{id}")
async def get_doc(id: str):
    doc = db.query(Document).filter_by(id=id).first()
    if not doc:
        raise HTTPException(status_code=404, detail="Not Found")
    
    response = {
        "id": str(doc.id),
        "file_name": doc.file_name,
        "text": doc.text
    }

    if doc.analysis:
        response.update({
            "summary": doc.analysis.summary,
            "detected_type": doc.analysis.detected_type,
            "attributes": doc.analysis.attributes
        })

    return response
