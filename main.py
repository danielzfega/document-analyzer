from fastapi import FastAPI
from app.routers.documents_router import router as documents_router

app = FastAPI(title="AI Document Analyzer")

app.include_router(documents_router, prefix="/documents", tags=["Documents"])


