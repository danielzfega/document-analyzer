import json
from app.core.llm_client import analyze_text_with_llm
from app.database.session import db
from app.database.models.document import Document, DocumentAnalysis

async def analyze_document(doc_id: str):
    doc = db.query(Document).filter_by(id=doc_id).first()
    if not doc:
        return None

    result = await analyze_text_with_llm(doc.text)

    parsed = json.loads(result)

    analysis = DocumentAnalysis(
        summary=parsed.get("summary"),
        detected_type=parsed.get("type"),
        attributes=parsed.get("attributes"),
        document=doc
    )

    db.add(analysis)
    db.commit()
    return analysis
