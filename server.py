from fastapi import FastAPI, Request
from fastapi.responses import StreamingResponse
from fastapi.middleware.cors import CORSMiddleware
import asyncio
import json
import time
import uuid
from typing import Dict, Any, AsyncGenerator, Set

# 导入Agent模块
from src.agent.core import query

app = FastAPI()

# 配置CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000"],  # 前端地址
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# 连接管理：存储每个连接的信息
class ConnectionManager:
    def __init__(self):
        # 存储连接ID到队列和消息历史的映射
        self.connections: Dict[str, Dict[str, Any]] = {}
    
    def add_connection(self, connection_id: str, message_queue: asyncio.Queue):
        """添加新连接"""
        self.connections[connection_id] = {
            "queue": message_queue,
            "messages": []  # 每个连接的消息历史
        }
    
    def remove_connection(self, connection_id: str):
        """移除连接"""
        if connection_id in self.connections:
            del self.connections[connection_id]
    
    def get_messages(self, connection_id: str) -> list:
        """获取连接的消息历史"""
        if connection_id in self.connections:
            return self.connections[connection_id]["messages"]
        return []
    
    def add_message(self, connection_id: str, message: Dict[str, Any]):
        """添加消息到连接的历史"""
        if connection_id in self.connections:
            self.connections[connection_id]["messages"].append(message)
    
    async def send_message(self, connection_id: str, message: Dict[str, Any]):
        """发送消息到指定连接"""
        if connection_id in self.connections:
            try:
                await self.connections[connection_id]["queue"].put(message)
            except Exception:
                # 连接已关闭，从集合中移除
                self.remove_connection(connection_id)

# 创建连接管理器实例
manager = ConnectionManager()

# SSE端点
@app.get("/sse")
async def sse_endpoint():
    """SSE端点，用于实时推送消息"""
    # 生成唯一连接ID
    connection_id = str(uuid.uuid4())
    # 创建一个队列用于接收消息
    message_queue = asyncio.Queue()
    # 添加到连接管理器
    manager.add_connection(connection_id, message_queue)
    
    async def event_generator():
        try:
            # 发送连接ID消息
            connection_msg = {
                "type": "connection",
                "content": "Connected",
                "connectionId": connection_id,
                "role": "system",
                "timestamp": time.time()
            }
            yield "data: " + json.dumps(connection_msg) + "\n\n"
            
            # 发送历史消息
            for msg in manager.get_messages(connection_id):
                yield "data: " + json.dumps(msg) + "\n\n"
            
            # 持续监听消息
            while True:
                # 等待消息
                message = await message_queue.get()
                yield "data: " + json.dumps(message) + "\n\n"
                
                # 处理心跳
                if message.get("type") == "heartbeat":
                    await asyncio.sleep(30)
        finally:
            # 连接关闭时移除
            manager.remove_connection(connection_id)
    
    return StreamingResponse(
        event_generator(),
        media_type="text/event-stream",
        headers={
            "X-Connection-ID": connection_id  # 在响应头中返回连接ID
        }
    )

# 聊天端点
@app.post("/chat")
async def chat_endpoint(request: Request):
    """处理聊天消息"""
    try:
        data = await request.json()
        message = data.get("message", "")
        connection_id = data.get("connectionId")
        
        print(f"收到消息: {message}")
        print(f"连接ID: {connection_id}")
        print(f"数据: {data}")
        
        if not message:
            print("错误: 消息为空")
            return {"error": "Message is required"}
        
        if not connection_id:
            print("错误: 连接ID为空")
            return {"error": "Connection ID is required"}
        
        # 检查连接是否存在
        if connection_id not in manager.connections:
            print(f"错误: 连接ID不存在: {connection_id}")
            return {"error": "Connection ID not found"}
        
        # 发送思考状态
        thinking_msg = {
            "id": str(len(manager.get_messages(connection_id)) + 1),
            "type": "thinking",
            "content": "AI正在思考...",
            "role": "assistant",
            "timestamp": time.time()
        }
        manager.add_message(connection_id, thinking_msg)
        await manager.send_message(connection_id, thinking_msg)
        
        # 调用Agent处理消息
        try:
            # 重定向标准输出，捕获Agent的打印内容
            import sys
            import io
            from contextlib import redirect_stdout
            
            # 创建一个字符串IO对象来捕获输出
            f = io.StringIO()
            
            # 流式输出回调函数
            async def on_output(output):
                # 构建消息
                msg = {
                    "id": output.get("id", str(len(manager.get_messages(connection_id)) + 1)),
                    "type": output["type"],
                    "content": output["content"],
                    "role": "assistant",
                    "timestamp": time.time(),
                    "is_append": output.get("is_append", False)
                }
                # 添加数据（如果有）
                if "data" in output:
                    msg["data"] = output["data"]
                
                # 直接发送消息，不做额外处理
                # 前端会根据is_append字段和消息ID来处理消息的累积显示
                await manager.send_message(connection_id, msg)
                
                # 同时更新消息历史
                if not output.get("is_append", False):
                    # 对于新消息，添加到历史
                    manager.add_message(connection_id, msg)
                else:
                    # 对于追加消息，更新历史中的对应消息
                    messages = manager.get_messages(connection_id)
                    existing_msg = None
                    for m in messages:
                        if m.get("id") == msg["id"]:
                            existing_msg = m
                            break
                    
                    if existing_msg:
                        existing_msg["content"] += msg["content"]
                        existing_msg["timestamp"] = time.time()
            
            # 在后台线程中执行Agent处理，避免阻塞事件循环
            import concurrent.futures
            with concurrent.futures.ThreadPoolExecutor() as executor:
                # 使用redirect_stdout捕获输出
                def query_with_output_capture(msg):
                    with redirect_stdout(f):
                        # 定义一个同步回调，内部调用异步函数
                        def sync_on_output(output):
                            # 在后台线程中创建一个新的事件循环并运行回调
                            loop = asyncio.new_event_loop()
                            asyncio.set_event_loop(loop)
                            try:
                                loop.run_until_complete(on_output(output))
                            finally:
                                loop.close()
                        return query(msg, on_output=sync_on_output)
                
                ai_response = await asyncio.get_event_loop().run_in_executor(
                    executor, query_with_output_capture, message
                )
            
            # 获取并打印捕获的输出
            captured_output = f.getvalue()
            if captured_output:
                print("=== Agent 输出 ===")
                print(captured_output)
                print("=== 捕获输出结束 ================")
            
            print(f"Agent 原始响应: {ai_response}")

            # 处理Agent返回的完整过程（作为备份，以防流式输出有遗漏）
            # if isinstance(ai_response, dict) and "steps" in ai_response:
            #     # 检查是否已经有回答消息
            #     has_answer = any(step.get("answer") for step in ai_response["steps"])
            #     if not has_answer:
            #         # 如果没有回答消息，发送最终回答
            #         for step in ai_response["steps"]:
            #             if step.get("answer"):
            #                 answer_msg = {
            #                     "id": str(len(manager.get_messages(connection_id)) + 1),
            #                     "type": "answer",
            #                     "content": step["answer"],
            #                     "role": "assistant",
            #                     "timestamp": time.time()
            #                 }
            #                 manager.add_message(connection_id, answer_msg)
            #                 await manager.send_message(connection_id, answer_msg)
            #                 break
            # else:
            #     # 兼容旧格式，直接发送响应
            #     # 检查是否已经发送过消息
            #     recent_messages = manager.get_messages(connection_id)
            #     has_recent_answer = any(msg.get("type") == "answer" for msg in recent_messages[-5:])
            #     if not has_recent_answer:
            #         ai_msg = {
            #             "id": str(len(manager.get_messages(connection_id)) + 1),
            #             "type": "answer",
            #             "content": str(ai_response),
            #             "role": "assistant",
            #             "timestamp": time.time()
            #         }
            #         manager.add_message(connection_id, ai_msg)
            #         await manager.send_message(connection_id, ai_msg)
            
            return {"success": True, "message": "Message received"}
            
        except Exception as e:
            # 发送错误消息
            error_msg = {
                "id": str(len(manager.get_messages(connection_id)) + 1),
                "type": "error",
                "content": f"处理消息时出错: {str(e)}",
                "role": "assistant",
                "timestamp": time.time()
            }
            manager.add_message(connection_id, error_msg)
            await manager.send_message(connection_id, error_msg)
            
            return {"error": str(e)}
        
    except Exception as e:
        return {"error": str(e)}

# 健康检查端点
@app.get("/health")
async def health_check():
    """健康检查"""
    return {"status": "healthy"}

# 根路径
@app.get("/")
async def root():
    """根路径"""
    return {"message": "AI Agent API"}

# 心跳任务
async def heartbeat_task():
    """定期发送心跳"""
    while True:
        await asyncio.sleep(30)
        # 为每个连接单独发送心跳
        for connection_id in list(manager.connections.keys()):
            heartbeat = {
                "type": "heartbeat",
                "content": "pong",
                "role": "system",
                "timestamp": time.time()
            }
            await manager.send_message(connection_id, heartbeat)

# 启动心跳任务
@app.on_event("startup")
async def startup_event():
    """启动事件"""
    asyncio.create_task(heartbeat_task())

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        "server:app",
        host="localhost",
        port=8000,
        reload=True
    )
