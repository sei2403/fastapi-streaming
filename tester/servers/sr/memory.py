# 載入相關套件
from fastapi import FastAPI, Request
from fastapi.responses import StreamingResponse
from starlette.middleware.base import BaseHTTPMiddleware
import uvicorn
import json
import aiofiles
import psutil
from time import sleep

# 創建一個 FastAPI 應用實例
app = FastAPI()

# 非同步事件生成器函數
async def event_generator(file_path: str, process):
    # 開啟檔案，並以utf-8的方式讀取
    async with aiofiles.open(f"chunks/chunk_{file_path}.txt", mode='r', encoding='utf-8') as f:
        # 檔案中以每行讀取
        async for line in f:
            # 將每行以每個文字切割(轉成list就完成)
            for word in list(line):
                # 計算使用的記憶體大小
                memory_info = process.memory_info().rss  
                # 建立發送訊息
                message = {"msg": word, "memory_usage": memory_info}
                # 整理返回訊息
                yield f"{json.dumps(message)}\n"

# 定義 StreamingResponse 路由端點，處理 GET 請求
@app.get("/")
async def stream_endpoint(id: str):
    # 獲取當前進程對象
    process = psutil.Process()
    # StreamingResponse用來實現流式傳輸
    return StreamingResponse(event_generator(id, process), media_type="text/event-stream")

# 主函數，用 uvicorn 啟動應用，監聽 0.0.0.0 主機上的 8001 埠
if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8001)
