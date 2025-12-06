import os
from fastapi import UploadFile
from app.core.s3_client import s3
from app.core.text_extractor import extract_pdf_text, extract_docx_text
from app.database.session import db
from app.database.models.document import Document
from app.utils.file_validation import validate_file_size, validate_file_type
from app.utils.uuid_generator import generate_s3_key

async def handle_upload(file: UploadFile):
    validate_file_size(file)
    validate_file_type(file)

    s3_key = generate_s3_key(file.filename)
    local_path = f"/tmp/{s3_key}"

    with open(local_path, "wb") as f:
        f.write(await file.read())

    s3.upload_file(local_path, "documents", s3_key)

    # extract
    if file.filename.endswith(".pdf"):
        text = extract_pdf_text(local_path)
    else:
        text = extract_docx_text(local_path)

    doc = Document(file_name=file.filename, s3_key=s3_key, text=text)
    db.add(doc)
    db.commit()
    db.refresh(doc)

    os.remove(local_path)
    return doc
