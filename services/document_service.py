from fastapi import UploadFile
from sqlalchemy.orm import Session
from models.document import Document
from core.minio_client import upload_file_to_minio
from core.text_extractor import extract_pdf_text, extract_docx_text
from db.database import SessionLocal
import shutil
import os
import uuid

from fastapi import UploadFile, HTTPException

async def handle_upload(file: UploadFile) -> Document:
    # 0. Validate file type
    SUPPORTED_EXTENSIONS = {"pdf", "docx", "doc"}
    SUPPORTED_MIME_TYPES = {
        "application/pdf": "pdf",
        "application/vnd.openxmlformats-officedocument.wordprocessingml.document": "docx",
        "application/msword": "doc"
    }

    file_ext = file.filename.split('.')[-1].lower() if '.' in file.filename else ""
    
    if file_ext not in SUPPORTED_EXTENSIONS:
        raise HTTPException(
            status_code=400, 
            detail=f"Unsupported file extension: .{file_ext}. Supported: {', '.join(SUPPORTED_EXTENSIONS)}"
        )
    
    if file.content_type not in SUPPORTED_MIME_TYPES:
         # Optional: relaxed check if content-type is missing or generic, but strict is safer
         # For now, let's trust extension if content-type is application/octet-stream, 
         # but ideally we want strict MIME check.
         # Let's stick to strict validation as requested.
         raise HTTPException(
            status_code=400, 
            detail=f"Unsupported content type: {file.content_type}"
         )

    # 1. Generate unique filename/key
    unique_filename = f"{uuid.uuid4()}.{file_ext}"
    
    # 2. Upload to Minio (we can do this directly from file.file)
    # 2. Save directly to temp file to avoid seek/closed file issues
    temp_path = f"temp_{unique_filename}"
    extracted_text = ""
    
    try:
        await file.seek(0)
        with open(temp_path, "wb") as buffer:
            shutil.copyfileobj(file.file, buffer)
    
        # 3. Upload to Minio from temp file
        try:
            with open(temp_path, "rb") as f_data:
                storage_url = upload_file_to_minio(f_data, unique_filename)
            if not storage_url:
                raise Exception("Upload returned None")
        except Exception as e:
             raise HTTPException(status_code=502, detail=f"Failed to upload file to storage: {str(e)}")
        
        # 4. Extract text
        try:
            if file_ext == "pdf":
                extracted_text = extract_pdf_text(temp_path)
            elif file_ext in ["docx", "doc"]:
                extracted_text = extract_docx_text(temp_path)
        except Exception as e:
            # If extraction fails, it's likely a corrupt file or incompatible format
            raise HTTPException(status_code=400, detail=f"Failed to extract text from document. File might be corrupt or encrypted. Error: {str(e)}")
            
    finally:
        if os.path.exists(temp_path):
            os.remove(temp_path)

    # 4. Save to DB
    db: Session = SessionLocal()
    try:
        new_doc = Document(
            file_name=file.filename,
            s3_key=unique_filename, # or storage_url if valid
            text=extracted_text
        )
        db.add(new_doc)
        db.commit()
        db.refresh(new_doc)
        return new_doc
    finally:
        db.close()
