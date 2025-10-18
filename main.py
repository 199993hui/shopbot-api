from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from openai import AsyncOpenAI
from typing import Optional
import os
import asyncio
import time

OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
if not OPENAI_API_KEY:
    raise RuntimeError("Missing OPENAI_API_KEY")

MODEL = os.getenv("ASSISTANT_MODEL", "gpt-4o-mini")
client = AsyncOpenAI(api_key=OPENAI_API_KEY)

SYSTEM_PROMPT = (
    "You are ShopBot, a customer support bot for an e-commerce store. "
    "Help with product queries, shipping, returns, and general support. "
    "For returns: unopened items can be returned within 30 days via account dashboard, "
    "we provide prepaid labels, refunds process in 5-7 business days. "
    "For shipping: free on orders over $50, takes 2-5 business days domestically. "
    "Be concise and helpful."
)

app = FastAPI(title="ShopBot API", version="1.0.0")

# Cache for assistant ID
_assistant_id = None

async def get_assistant_id():
    global _assistant_id
    if not _assistant_id:
        assistant = await client.beta.assistants.create(
            name="ShopBot",
            instructions=SYSTEM_PROMPT,
            model=MODEL,
        )
        _assistant_id = assistant.id
    return _assistant_id

class ChatRequest(BaseModel):
    message: str
    thread_id: Optional[str] = None

class ChatResponse(BaseModel):
    response: str
    thread_id: str

@app.get("/health")
async def health():
    return {"status": "healthy", "model": MODEL}

@app.post("/threads")
async def create_thread():
    thread = await client.beta.threads.create()
    return {"thread_id": thread.id}

@app.post("/chat", response_model=ChatResponse)
async def chat(request: ChatRequest):
    try:
        # Get assistant ID
        assistant_id = await get_assistant_id()
        
        # Create or reuse existing thread
        if request.thread_id:
            thread_id = request.thread_id
        else:
            thread = await client.beta.threads.create()
            thread_id = thread.id
        
        # Add user message to thread
        await client.beta.threads.messages.create(
            thread_id=thread_id,
            role="user",
            content=request.message
        )
        
        # Run assistant
        run = await client.beta.threads.runs.create(
            thread_id=thread_id,
            assistant_id=assistant_id
        )
        
        # Poll with backoff and timeout & wait for completion
        start = time.time()
        delay = 0.5
        while run.status in {"queued", "in_progress"}:
            await asyncio.sleep(delay)
            run = await client.beta.threads.runs.retrieve(
                thread_id=thread_id, run_id=run.id
            )
            delay = min(delay * 1.5, 2.0)
            if time.time() - start > 60:  # 60s safety timeout
                raise TimeoutError("Assistant run timed out")
            
        if run.status != "completed":
            raise RuntimeError(f"Run ended with status: {run.status}")
        
        # Get response
        messages = await client.beta.threads.messages.list(thread_id=thread_id, order="desc")
        response = messages.data[0].content[0].text.value
        
        return ChatResponse(response=response, thread_id=thread_id)
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))