import os
import requests
import json
from sqlalchemy.orm import Session
from models.document import Document
from db.database import SessionLocal
from config import settings

async def analyze_document(doc_id: str):
    db: Session = SessionLocal()
    doc = db.query(Document).filter(Document.id == doc_id).first()
    if not doc or not doc.text:
        db.close()
        return None

    # Call OpenRouter
    prompt = f"""
    Analyze the following text from a document:
    {doc.text[:10000]} 

    Please provide:
    1. A concise summary.
    2. The detected document type (e.g., invoice, CV, report, letter).
    3. Key attributes/metadata extracted (date, sender, amount, etc.) in JSON format.

    Return the output STRICTLY in the following JSON format:
    {{
        "summary": "...",
        "detected_type": "...",
        "attributes": {{ ... }}
    }}
    """
    
    headers = {
        "Authorization": f"Bearer {settings.OPENROUTER_API_KEY}",
        "Content-Type": "application/json"
    }
    
    data = {
        "model": "openai/gpt-4o-mini", # or any free model on OpenRouter
        "messages": [
            {"role": "user", "content": prompt}
        ]
    }
    
    try:
        response = requests.post(
            "https://openrouter.ai/api/v1/chat/completions",
            headers=headers,
            data=json.dumps(data)
        )
        response.raise_for_status()
        result = response.json()
        
        content = result['choices'][0]['message']['content']
        # Parse JSON from content (it might be wrapped in ```json ... ```)
        if "```json" in content:
            content = content.split("```json")[1].split("```")[0].strip()
        elif "```" in content:
            content = content.split("```")[1].strip()
            
        analysis_data = json.loads(content)
        
        doc.summary = analysis_data.get("summary")
        doc.detected_type = analysis_data.get("detected_type")
        doc.attributes = analysis_data.get("attributes")
        
        db.commit()
        return True
        
    except Exception as e:
        print(f"Error analyzing document: {e}")
        return False
    finally:
        db.close()
