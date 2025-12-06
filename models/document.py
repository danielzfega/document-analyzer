from sqlalchemy import Column, String, Text, DateTime, JSON, ForeignKey
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship
import uuid
from datetime import datetime

from app.database.base import Base


class Document(Base):
    __tablename__ = "documents"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    file_name = Column(String)
    s3_key = Column(String)
    text = Column(Text)
    uploaded_at = Column(DateTime, default=datetime.utcnow)

    analysis = relationship("DocumentAnalysis", back_populates="document", uselist=False)


class DocumentAnalysis(Base):
    __tablename__ = "document_analysis"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    summary = Column(Text)
    detected_type = Column(String)
    attributes = Column(JSON)
    analyzed_at = Column(DateTime, default=datetime.utcnow)

    document_id = Column(UUID(as_uuid=True), ForeignKey("documents.id"))
    document = relationship("Document", back_populates="analysis")
