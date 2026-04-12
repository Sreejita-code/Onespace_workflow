import json
from app.shared.llm import client

SYSTEM_PROMPT = """You are an API documentation extractor.
Extract API endpoints from the user's raw text and return ONLY a valid JSON object with an "endpoints" array.
Each endpoint must match this exact schema:
{
  "endpoints": [
    {
      "method": "GET|POST|PUT|PATCH|DELETE",
      "url": "string",
      "description": "string",
      "request_body": {} or null,
      "response_body": {} or null
    }
  ]
}
Output raw JSON only. Do not use markdown blocks. If no endpoints are found, return {"endpoints": []}.
"""

async def parse_raw_text(text: str) -> list[dict]:
    # We use a smaller token limit here since we are just extracting, not building logic
    raw_json = await client.complete_with_retry(SYSTEM_PROMPT, text, retries=2)
    try:
        data = json.loads(raw_json)
        return data.get("endpoints", [])
    except json.JSONDecodeError:
        raise ValueError("Failed to parse extracted endpoints into valid JSON.")