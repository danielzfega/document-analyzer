# AI Document Analyzer

An intelligent document processing service that extracts text from PDF and DOCX files, analyzes content using Large Language Models (LLMs) via OpenRouter, and provides structured metadata extraction.

## Features

- **Document Upload**: Support for PDF and DOCX files.
- **Secure Storage**: Files are stored securely in Minio/S3.
- **Text Extraction**: Automatic extraction of text content from uploaded documents.
- **AI Analysis**:
  - Concise Summaries.
  - Document Type Detection (Invoice, CV, Report, etc.).
  - Metadata Extraction (Date, Sender, Amount, etc.).
- **REST API**: Built with FastAPI for high performance and easy integration.

## Tech Stack

- **Backend**: FastAPI
- **Database**: PostgreSQL
- **Storage**: Minio (S3 Compatible)
- **AI/LLM**: OpenRouter (GPT-4o-mini or compatible)
- **ORM**: SQLAlchemy
- **Dependencies**: `boto3`, `pdfplumber`, `python-docx`, `python-multipart`

## Prerequisites

- Python 3.9+
- PostgreSQL
- Minio Server (or S3 access)
- OpenRouter API Key

## Installation

1. **Clone the repository**
   ```bash
   git clone https://github.com/danielzfega/document-analyzer
   cd document-analyzer
   ```

2. **Create a virtual environment**
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```

3. **Install dependencies**
   ```bash
   pip install -r requirements.txt
   ```

4. **Configuration**
   Create a `.env` file in the root directory (ensure it is UTF-8 encoded):
   ```env
   DATABASE_URL=postgresql://user:password@localhost:5432/document_analyzer
   
   MINIO_ENDPOINT=http://localhost:9000
   MINIO_ACCESS_KEY=minioadmin
   MINIO_SECRET_KEY=minioadmin123
   MINIO_BUCKET_NAME=document-analyzer
   
   OPENROUTER_API_KEY=your_openrouter_api_key_here
   ```

5. **Run the Application**
   ```bash
   uvicorn main:app --reload
   ```

## API Usage

### 1. Upload Document
**POST** `/documents/upload`
- **Body**: `multipart/form-data` with `file` field.
- **Response**:
  ```json
  {
      "id": "1",
      "file_name": "resume.pdf"
  }
  ```

### 2. Analyze Document
**POST** `/documents/{id}/analyze`
- **Response**:
  ```json
  {
      "message": "Analysis complete"
  }
  ```

### 3. Get Document Details
**GET** `/documents/{id}`
- **Response**:
  ```json
  {
      "id": "1",
      "file_name": "resume.pdf",
      "text": "Extracted text content...",
      "summary": "This is a resume for...",
      "detected_type": "CV",
      "attributes": {
          "name": "John Doe",
          "email": "john@example.com"
      }
  }
  ```

## Testing

Run the test suite using pytest:
```bash
pytest
```
*Note: Ensure your `.env` is configured for testing (e.g., using a test database or SQLite).*
