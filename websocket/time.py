
from fastapi import FastAPI, WebSocket, Request
import time
import json
import uvicorn



# 創建 FastAPI 應用實例
app = FastAPI()

class ConnectionManager:
    def __init__(self):
        self.active_connections: list[WebSocket] = []
    
    async def connect(self, websocket: WebSocket):
        await websocket.accept()
        self.active_connections.append(websocket)
    def disconnect(self, websocket: WebSocket):
        self.active_connections.remove(websocket)
    
    async def send_text(self, message: str, websocket: WebSocket):
        await websocket.send_text(message)


manager = ConnectionManager()

# 定義 WebSocket 路由
@app.websocket("/")
async def websocket_endpoint(websocket: WebSocket):
    
    # 接受 WebSocket 連接
    await manager.connect(websocket)

    start_time = time.time()

    try:
        # 接收來自客戶端的文本消息並將其轉換為整數文件代號
        data = await websocket.receive_text()
        file_id = int(data)
        
        # 打開指定文件
        with open(f"chunks/chunks_{file_id}.txt", 'r', encoding='utf-8') as f:
            content = f.read()
        
        # 按單詞分割文件內容
        words = list(content)
        
        # 逐個單詞回傳給客戶端
        for word in words:
            # 獲取當前時間
            
            response = {
                "msg": word,
            }

            # 將字典轉換為 JSON 字符串
            response_str = json.dumps(response)
            
            # 回傳消息給客戶端
            await manager.send_text(response_str, websocket)
        
        end_time = time.time()
        
        end_message = {
            "server_time": f"{(end_time-start_time):.10f}",
            "msg": "\\END"
        }
        await manager.send_text(json.dumps(end_message), websocket)
        
        await websocket.close()
    
    except Exception as e:
        # 處理可能的錯誤
        manager.disconnect(websocket)
        await websocket.send_text(f"Error: {str(e)}")
        await websocket.close()


uvicorn.run(app, host="0.0.0.0", port=8000)