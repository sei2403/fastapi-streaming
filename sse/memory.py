from fastapi import FastAPI, Request
from fastapi.responses import Response
import time
import aiofiles
import asyncio
import json
from sse_starlette.sse import EventSourceResponse
import psutil

# 創建一個 FastAPI 應用實例
app = FastAPI()

# 非同步事件生成器函數
async def event_generator(file_path: str, process):
    # 非同步打開文件，路徑是 'chunks/chunks_<file_path>.txt'
    async with aiofiles.open(f"chunks/chunk_{file_path}.txt", encoding='utf-8', mode='r') as f:
        # 非同步逐行讀取文件
        async for line in f:
            # 逐行分割為單詞
            for word in list(line):
                # 獲取進程的內存使用量，單位為 MB
                memory_info = process.memory_info().rss
                # 構建消息字典，包含單詞和內存使用量
                message = {"msg": word, "memory_usage":memory_info}
                # SSE格式: 'data: <消息>\n\n'
                yield json.dumps(message)

# 定義 SSE 路由端點，處理 GET 請求
@app.get("/")
async def sse(id: str):
    # 獲取當前進程對象
    process = psutil.Process()
    # 返回一個 EventSourceResponse，將生成器傳遞給它，並指定媒體類型為 'text/event-stream'
    return EventSourceResponse(event_generator(id,process))

# 主函數，用 uvicorn 啟動應用，監聽 0.0.0.0 主機上的 8001 埠
if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8001)