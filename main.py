from fastapi import FastAPI
from routers import document_router
from db.database import engine, Base

# Create tables
Base.metadata.create_all(bind=engine)

app = FastAPI(title="Document Analyzer")

app.include_router(document_router.router, prefix="/documents", tags=["documents"])

@app.get("/")
def read_root():
    return {"message": "Welcome to Document Analyzer API"}
