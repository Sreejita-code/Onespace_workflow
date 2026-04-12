import json

def _try_json(text: str) -> dict | None:
    if not text or not isinstance(text, str):
        return None
    try:
        return json.loads(text.strip())
    except json.JSONDecodeError:
        return {"raw_text": text.strip()} # Graceful fallback for messy data