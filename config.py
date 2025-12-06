import os
from dotenv import load_dotenv

load_dotenv()

class Settings:
    OPENROUTER_API_KEY: str = os.getenv("OPENROUTER_API_KEY")
    S3_BUCKET: str = os.getenv("S3_BUCKET")
    S3_ENDPOINT: str = os.getenv("S3_ENDPOINT")
    S3_ACCESS_KEY: str = os.getenv("S3_ACCESS_KEY")
    S3_SECRET_KEY: str = os.getenv("S3_SECRET_KEY")
    
    DATABASE_URL: str = os.getenv("DATABASE_URL")
    MAX_FILE_SIZE_MB = 5

settings = Settings()
