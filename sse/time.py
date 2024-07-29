from fastapi import FastAPI, Request
from fastapi.responses import Response
import time
import aiofiles
import asyncio
import json
from sse_starlette.sse import EventSourceResponse

# 創建一個 FastAPI 應用實例
app = FastAPI()

# 非同步事件生成器函數
async def event_generator(file_path: str, start_time:float):
    # 非同步打開文件，路徑是 'chunks/chunks_<file_path>.txt'
    async with aiofiles.open(f"chunks/chunk_{file_path}.txt", encoding="utf-8", mode='r') as f:
        # 非同步逐行讀取文件
        async for line in f:
            # 逐行分割為單詞
            for word in list(line):
                # 獲取當前 UTC 時間戳
                timestamp = time.time()
                # 構建消息字典，包含單詞和服務器運行時間
                message = {"msg": word, "server_time": f"{(timestamp - start_time):.10f}"}
                # SSE格式: 'data: <消息>\n\n'
                yield json.dumps(message)

# 定義 SSE 路由端點，處理 GET 請求
@app.get("/")
async def sse(id: str):
    # 獲取接收到請求的時間戳
    start_time = time.time()
    # 返回一個 EventSourceResponse，將生成器傳遞給它
    return EventSourceResponse(event_generator(id, start_time))

# 主函數，用 uvicorn 啟動應用，監聽 0.0.0.0 主機上的 8000 埠
if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)