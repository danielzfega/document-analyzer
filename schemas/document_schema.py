from pydantic import BaseModel
from typing import Optional, Dict

class DocumentResponse(BaseModel):
    id: str
    file_name: str
    text: Optional[str] = None
    summary: Optional[str] = None
    detected_type: Optional[str] = None
    attributes: Optional[Dict] = None
