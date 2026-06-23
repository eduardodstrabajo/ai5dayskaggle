from fastapi import FastAPI, HTTPException
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel
import os
import httpx

app = FastAPI()

# Serve the pre-built static client from `dist`
app.mount("/", StaticFiles(directory="dist", html=True), name="static")

OPENROUTER_URL = "https://api.openrouter.ai/v1/chat/completions"

class ChatRequest(BaseModel):
    model: str = None
    messages: list


@app.post("/api/chat")
async def chat(req: ChatRequest):
    api_key = os.getenv("OPENROUTER_API_KEY")
    if not api_key:
        raise HTTPException(status_code=500, detail="OPENROUTER_API_KEY not set in environment")

    payload = {"model": req.model or os.getenv("OPENROUTER_MODEL"), "messages": req.messages}

    async with httpx.AsyncClient(timeout=60.0) as client:
        headers = {"Authorization": f"Bearer {api_key}", "Content-Type": "application/json"}
        resp = await client.post(OPENROUTER_URL, json=payload, headers=headers)
        try:
            resp.raise_for_status()
        except httpx.HTTPStatusError as e:
            # surface the remote API error
            raise HTTPException(status_code=502, detail=f"OpenRouter error: {e.response.text}")
        return resp.json()


if __name__ == "__main__":
    # Run with: python3 server.py OR: uvicorn server:app --host 0.0.0.0 --port 3000
    import uvicorn
    uvicorn.run("server:app", host="0.0.0.0", port=3000, log_level="info")
