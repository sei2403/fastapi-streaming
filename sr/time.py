from fastapi import FastAPI, Request
from fastapi.responses import StreamingResponse
from starlette.middleware.base import BaseHTTPMiddleware
import asyncio
import uvicorn
import time
import json
import aiofiles
import tracemalloc
import psutil
from time import sleep

app = FastAPI()

async def event_generator(file_path: str, starttime: float):
    async with aiofiles.open(f"chunks/chunks_{file_path}.txt", mode='r', encoding='utf-8') as f:
        async for line in f:
            for word in list(line):
                timestamp = time.time()
                message = {"msg": word, "server_time": f"{(timestamp - starttime):.10f}"}
                yield f"{json.dumps(message)}\n"

@app.get("/")
async def stream_endpoint(id: str):
    starttime = time.time()
    # StreamingResponse用來實現流式傳輸
    return StreamingResponse(event_generator(id, starttime), media_type="text/event-stream")
    #return StreamingResponse(event_generator(id), media_type="application/json")

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)
