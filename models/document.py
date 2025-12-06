from sqlalchemy import Column, Integer, String, Text, DateTime, JSON
from datetime import datetime
from db.database import Base

class Document(Base):
    __tablename__ = "documents"

    id = Column(Integer, primary_key=True, index=True)
    file_name = Column(String, index=True)
    s3_key = Column(String)
    text = Column(Text, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    
    # Analysis results
    summary = Column(Text, nullable=True)
    detected_type = Column(String, nullable=True)
    attributes = Column(JSON, nullable=True)
