import os
from dotenv import load_dotenv

load_dotenv()

class Settings:
    OPENROUTER_API_KEY: str = os.getenv("OPENROUTER_API_KEY")
    MINIO_BUCKET_NAME: str = os.getenv("MINIO_BUCKET_NAME", "document-analyzer")
    MINIO_ENDPOINT: str = os.getenv("MINIO_ENDPOINT", "http://localhost:9000")
    MINIO_ACCESS_KEY: str = os.getenv("MINIO_ACCESS_KEY", "minioadmin")
    MINIO_SECRET_KEY: str = os.getenv("MINIO_SECRET_KEY", "minioadmin123")
    
    DATABASE_URL: str = os.getenv("DATABASE_URL")
    MAX_FILE_SIZE_MB = 5

settings = Settings()
