from fastapi import FastAPI, Request
from fastapi.responses import StreamingResponse
from starlette.middleware.base import BaseHTTPMiddleware
import uvicorn
import json
import aiofiles
import psutil
from time import sleep

app = FastAPI()


async def event_generator(file_path: str, process):
    async with aiofiles.open(f"chunks/chunks_{file_path}.txt", mode='r', encoding='utf-8') as f:
        async for line in f:
            for word in list(line):
                memory_info = process.memory_info().rss  # 以 MB 为单位
                message = {"msg": word, "memory_usage": memory_info}
                yield f"{json.dumps(message)}\n"

@app.get("/")
async def stream_endpoint(id: str):
    # StreamingResponse用來實現流式傳輸
    process = psutil.Process()
    return StreamingResponse(event_generator(id, process), media_type="text/event-stream")
    #return StreamingResponse(event_generator(id), media_type="application/json")

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8001)
