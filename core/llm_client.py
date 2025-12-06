import httpx
from app.config import settings

async def analyze_text_with_llm(text: str) -> dict:
    prompt = f"""
    You are an AI document analyzer.
    Analyze the following document and return JSON:
    - summary: concise summary
    - type: invoice, cv, report, letter, etc.
    - attributes: key-value metadata
    
    Document text:
    {text}
    """

    headers = {
        "Authorization": f"Bearer {settings.OPENROUTER_API_KEY}",
        "Content-Type": "application/json",
    }

    async with httpx.AsyncClient() as client:
        response = await client.post(
            "https://openrouter.ai/api/v1/chat/completions",
            json={
                "model": "gpt-4o-mini",
                "messages": [
                    {"role": "system", "content": "Return JSON only."},
                    {"role": "user", "content": prompt},
                ],
            },
            headers=headers,
            timeout=60,
        )
    
    result = response.json()["choices"][0]["message"]["content"]
    return result
