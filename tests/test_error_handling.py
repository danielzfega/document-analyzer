import pytest
from fastapi.testclient import TestClient
from unittest.mock import patch, MagicMock
from main import app
from models.document import Document
import uuid

client = TestClient(app)

def test_upload_unsupported_file_extension():
    # Create a dummy file with .txt extension
    files = {'file': ('test.txt', b'some content', 'text/plain')}
    response = client.post("/documents/upload", files=files)
    assert response.status_code == 400
    assert "Unsupported file extension" in response.json()['detail']

def test_upload_unsupported_content_type():
    # Create a dummy file with .pdf extension but wrong content type
    files = {'file': ('test.pdf', b'some content', 'image/png')}
    response = client.post("/documents/upload", files=files)
    assert response.status_code == 400
    assert "Unsupported content type" in response.json()['detail']

@patch("services.document_service.upload_file_to_minio")
@patch("services.document_service.SessionLocal")
@patch("services.document_service.extract_pdf_text")
def test_upload_success(mock_extract, mock_db_cls, mock_minio):
    # Mock DB
    mock_db = MagicMock()
    mock_db_cls.return_value = mock_db
    
    # Mock Minio
    mock_minio.return_value = "s3://bucket/test.pdf"
    
    # Mock extraction
    mock_extract.return_value = "Extracted text"

    files = {'file': ('test.pdf', b'%PDF-1.4...', 'application/pdf')}
    response = client.post("/documents/upload", files=files)
    
    assert response.status_code == 200
    assert "id" in response.json()
    assert response.json()["file_name"] == "test.pdf"

@patch("routers.document_router.analyze_document")
def test_analyze_not_found(mock_analyze):
    # Mock the service to raise 404 (simulating the behavior of analysis_service)
    from fastapi import HTTPException
    mock_analyze.side_effect = HTTPException(status_code=404, detail="Document not found")
    
    # Use a dummy UUID
    doc_id = str(uuid.uuid4())
    response = client.post(f"/documents/{doc_id}/analyze")
    assert response.status_code == 404
    assert response.json()["detail"] == "Document not found"

@patch("routers.document_router.analyze_document")
def test_analyze_empty_text(mock_analyze):
    from fastapi import HTTPException
    mock_analyze.side_effect = HTTPException(status_code=400, detail="Document has no text to analyze")
    
    # Use a dummy UUID
    doc_id = str(uuid.uuid4())
    response = client.post(f"/documents/{doc_id}/analyze")
    assert response.status_code == 400
    assert response.json()["detail"] == "Document has no text to analyze"
