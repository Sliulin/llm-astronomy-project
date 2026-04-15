import asyncio
import json
import os
import shutil
import time
import uuid
from contextlib import asynccontextmanager

from fastapi import FastAPI, Request, File, UploadFile
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import StreamingResponse
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel

from src.agent.core import query
from src.agent.tool import tool_registry

# ==========================================
# 会话持久化管理
# ==========================================
message_queue = asyncio.Queue()
SESSIONS_FILE = "sessions.json"
sessions_data = {} 

def load_sessions():
    global sessions_data
    if os.path.exists(SESSIONS_FILE):
        try:
            with open(SESSIONS_FILE, "r", encoding="utf-8") as f:
                sessions_data = json.load(f)
                print(f"✅ 已加载 {len(sessions_data)} 个历史会话")
        except Exception as e:
            print(f"❌ 加载会话失败: {e}")
            sessions_data = {}
    
    # 无现有会话时初始化默认会话
    if not sessions_data:
        create_new_session_data()

def create_new_session_data():
    new_id = str(uuid.uuid4())
    sessions_data[new_id] = {
        "id": new_id,
        "title": "新观测任务",
        "updated_at": time.time(),
        "messages": []
    }
    save_sessions()
    return new_id

def save_sessions():
    try:
        with open(SESSIONS_FILE, "w", encoding="utf-8") as f:
            json.dump(sessions_data, f, ensure_ascii=False, indent=2)
    except Exception as e:
        print(f"❌ 保存会话失败: {e}")

@asynccontextmanager
async def lifespan(app: FastAPI):
    load_sessions()
    yield

app = FastAPI(lifespan=lifespan)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000", "http://127.0.0.1:3000"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

os.makedirs("download", exist_ok=True)
app.mount("/downloads", StaticFiles(directory="download"), name="downloads")

# ==========================================
# RESTful API：会话与工具管理
# ==========================================
@app.get("/api/sessions")
async def get_sessions():
    """获取所有会话列表（按时间倒序）"""
    sorted_sessions = sorted(sessions_data.values(), key=lambda x: x["updated_at"], reverse=True)
    return [{"id": s["id"], "title": s["title"], "updated_at": s["updated_at"]} for s in sorted_sessions]

@app.get("/api/sessions/{session_id}")
async def get_session_messages(session_id: str):
    """获取指定会话的历史消息"""
    if session_id in sessions_data:
        return sessions_data[session_id]["messages"]
    return []

@app.post("/api/sessions")
async def create_session():
    """新建会话"""
    new_id = create_new_session_data()
    return {"id": new_id}

@app.delete("/api/sessions/{session_id}")
async def delete_session(session_id: str):
    """删除指定会话"""
    if session_id in sessions_data:
        del sessions_data[session_id]
        save_sessions()
        # 确保系统至少保留一个会话
        if not sessions_data:
            create_new_session_data() 
    return {"success": True}

class SessionUpdate(BaseModel):
    title: str

@app.put("/api/sessions/{session_id}")
async def update_session_title(session_id: str, payload: SessionUpdate):
    """更新指定会话的标题"""
    try:
        if session_id in sessions_data:
            # 更新内存数据并落盘
            sessions_data[session_id]["title"] = payload.title
            save_sessions()
            return {"success": True, "message": "标题更新成功"}
        else:
            return {"success": False, "error": "会话不存在"}
            
    except Exception as e:
        print(f"更新会话标题失败: {e}")
        return {"success": False, "error": str(e)}

@app.get("/api/tools")
async def get_tools_list():
    """动态获取后端注册的工具集，供前端分类展示"""
    return tool_registry.get_frontend_tools()
    
UPLOAD_DIR = os.path.abspath("upload")
os.makedirs(UPLOAD_DIR, exist_ok=True)

@app.post("/api/upload")
async def upload_file(file: UploadFile = File(...)):
    """接收前端上传文件并保存到本地"""
    try:
        # 添加时间戳前缀以防止同名文件覆盖
        timestamp = time.strftime("%Y%m%d_%H%M%S")
        safe_filename = f"{timestamp}_{file.filename}"
        file_path = os.path.join(UPLOAD_DIR, safe_filename)
        
        with open(file_path, "wb") as buffer:
            shutil.copyfileobj(file.file, buffer)
            
        print(f"✅ 文件已成功上传至: {file_path}")
        
        return {
            "success": True,
            "message": "文件上传成功",
            "filename": file.filename,
            "file_path": file_path 
        }
    except Exception as e:
        print(f"❌ 上传文件失败: {e}")
        return {"success": False, "error": str(e)}

# ==========================================
# 对话核心 API
# ==========================================
@app.get("/sse")
async def sse_endpoint():
    """实时流数据推送"""
    async def event_generator():
        yield f"data: {json.dumps({'type': 'connection', 'connectionId': 'local-agent'})}\n\n"
        while True:
            message = await message_queue.get()
            yield f"data: {json.dumps(message)}\n\n"
            
    return StreamingResponse(
        event_generator(),
        media_type="text/event-stream",
        headers={"Cache-Control": "no-cache", "Connection": "keep-alive"}
    )

@app.post("/chat")
async def chat_endpoint(request: Request):
    """处理用户对话请求"""
    try:
        data = await request.json()
        message = data.get("message", "")
        session_id = data.get("session_id", "")
        
        if not message or session_id not in sessions_data:
            return {"error": "Invalid request"}
        
        # 记录用户消息
        user_msg = {
            "id": str(uuid.uuid4()),
            "type": "answer",
            "content": message,
            "role": "user",
            "timestamp": time.time()
        }
        sessions_data[session_id]["messages"].append(user_msg)
        
        # 首条消息自动重命名会话标题
        if sessions_data[session_id]["title"] == "新观测任务":
            sessions_data[session_id]["title"] = message[:12] + ("..." if len(message) > 12 else "")
        
        sessions_data[session_id]["updated_at"] = time.time()
        
        # 推送 AI 思考状态占位符
        thinking_msg = {
            "id": str(uuid.uuid4()),
            "type": "thinking",
            "content": "AI正在思考并调用工具...",
            "role": "assistant",
            "timestamp": time.time(),
            "session_id": session_id 
        }
        sessions_data[session_id]["messages"].append(thinking_msg)
        await message_queue.put(thinking_msg)
        
        # 消息流回调处理
        async def on_output(output):
            msg = {
                "id": output.get("id", str(uuid.uuid4())),
                "type": output["type"],
                "content": output["content"],
                "role": "assistant",
                "timestamp": time.time(),
                "is_append": output.get("is_append", False),
                "session_id": session_id
            }
            await message_queue.put(msg)
            
            # 更新本地状态
            if not msg["is_append"]:
                sessions_data[session_id]["messages"].append(msg)
            else:
                for m in sessions_data[session_id]["messages"]:
                    if m.get("id") == msg["id"]:
                        m["content"] += msg["content"]
                        break
            
            sessions_data[session_id]["updated_at"] = time.time()
            save_sessions()

        # 调度核心查询逻辑
        await query(message, session_id=session_id, on_output=on_output)
        return {"success": True}
        
    except Exception as e:
        print(f"❌ 发生错误: {e}")
        return {"error": str(e)}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("server:app", host="localhost", port=8000, reload=True)