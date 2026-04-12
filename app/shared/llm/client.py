import asyncio
from openai import AsyncOpenAI
from app.config import settings

_client = AsyncOpenAI(api_key=settings.openai_api_key)

class LLMError(Exception):
    pass

async def complete(system: str, user: str, max_tokens: int = 2500) -> str:
    response = await _client.chat.completions.create(
        model=settings.openai_model,
        max_completion_tokens=max_tokens, # <--- CHANGED THIS LINE
        temperature=0.1, 
        response_format={"type": "json_object"}, 
        messages=[
            {"role": "system", "content": system},
            {"role": "user",   "content": user},
        ],
    )
    return response.choices[0].message.content

async def complete_with_retry(system: str, user: str, retries: int = 2) -> str:
    for attempt in range(retries):
        try:
            return await complete(system, user)
        except Exception as e:
            if attempt == retries - 1:
                raise LLMError(f"LLM failed after {retries} attempts: {str(e)}") from e
            await asyncio.sleep(1.5 ** attempt)