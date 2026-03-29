import os
import sys
import json
import uuid
import asyncio
from dotenv import load_dotenv
from openai import AsyncOpenAI
from src.agent.tool import tool_registry

# 添加项目根目录到Python路径
BASE_DIR = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
sys.path.insert(0, BASE_DIR)



# 加载环境变量
env_path = os.path.join(BASE_DIR, "assets", "openai.env")
load_dotenv(env_path)

api_key = os.getenv("HUNYUAN_API_KEY", "dummy-key")
base_url = os.getenv("OPENAI_API_BASE", "https://api.hunyuan.cloud.tencent.com/v1")

client = AsyncOpenAI(api_key=api_key, base_url=base_url)

class NumpyEncoder(json.JSONEncoder):
    def default(self, obj):
        if hasattr(obj, 'item'):
            return obj.item()
        elif hasattr(obj, 'tolist'):
            return obj.tolist()
        return super().default(obj)

SYSTEM_PROMPT = """你是一个专业的天文数据智能助手。
你能够调用工具查询天文数据库。

【输出规范 - 必须严格遵守】：
1. 语言：始终使用中文回答。
2. 严禁原文：绝对禁止直接输出工具返回的 JSON 源代码或 Python 字典格式。
3. 数据整理：请从工具返回的复杂数据中提取核心信息（如名称、坐标、红移、数量等），并整理成自然的中文句子或 Markdown 表格。
4. 链接渲染：当遇到 .fits 或 .fits.gz 图像链接时，必须将其转化为标准的 Markdown 链接。
   - 格式：[文字描述](链接地址)
   - 示例：[点击下载 M31 的 FITS 图像](https://ned.ipac.caltech.edu/...)
   - 注意：方括号 [] 和 圆括号 () 之间严禁有任何空格。

【当前环境】：
所有的图像存储在本地 download/ 目录下，或指向远程 NED 数据库。如果是本地路径，请确保链接正确。"""

# 初始化全局记忆
session_memory = {}

async def query(question: str, session_id: str = "default", max_turns: int = 5, on_output=None):
    global session_memory
    
    if session_id not in session_memory:
        session_memory[session_id] = [{"role": "system", "content": SYSTEM_PROMPT}]
    
    messages = session_memory[session_id]
    
    if len(messages) > 10:
        session_memory[session_id] = [messages[0]] + messages[-6:]
        messages = session_memory[session_id]
    
    messages.append({"role": "user", "content": question})
    tools = tool_registry.get_openai_tools()
    
    # ==========================================
    # 【新增】：创建一个列表，悄悄攒着从工具里拦截下来的本地文件链接
    # ==========================================
    bypassed_links = []
    
    turn = 0
    while turn < max_turns:
        turn += 1
        print(f"\n--- 第 {turn} 轮思考 (Session: {session_id[:8]}) ---")
        
        try:
            response = await client.chat.completions.create(
                model="hunyuan-turbo", 
                messages=messages,
                tools=tools if tools else None,
                tool_choice="auto" if tools else "none",
            )
        except Exception as e:
            error_msg = f"大模型请求失败: {str(e)}"
            print(error_msg)
            if on_output:
                await on_output({"id": str(uuid.uuid4()), "type": "error", "content": error_msg, "is_append": False, "session_id": session_id})
            return {"question": question, "final_answer": error_msg, "turns": turn}
        
        message = response.choices[0].message
        messages.append(message.model_dump(exclude_none=True))
        
        if message.tool_calls:
            for tool_call in message.tool_calls:
                func_name = tool_call.function.name
                try:
                    func_args = json.loads(tool_call.function.arguments)
                except json.JSONDecodeError:
                    func_args = {}
                
                if on_output:
                    await on_output({
                        "id": str(uuid.uuid4()), "type": "action", 
                        "content": f"正在查询天文数据库：{func_name}({func_args})", 
                        "is_append": False, "session_id": session_id
                    })
                
                # 执行本地天文工具
                observation = tool_registry.execute_tool(func_name, **func_args)
                
                # ==========================================
                # 【核心拦截逻辑】：提取路径并对大模型隐身
                # ==========================================
                def extract_and_hide_paths(obj):
                    if isinstance(obj, dict):
                        keys_to_delete = []
                        for k, v in obj.items():
                            if isinstance(v, str) and ('\\download\\' in v or '/download/' in v):
                                normalized = v.replace('\\', '/')
                                rel_path = normalized.split('/download/')[-1]
                                url = f"http://localhost:8000/downloads/{rel_path}"
                                # 把生成的前端 URL 存到我们自己的列表里
                                bypassed_links.append(f"\n\n**[原始数据已下载到downloads目录<br><span style='margin-left: 1.2em;'>点击查看原始数据 ({k})</span>]({url})**")
                                keys_to_delete.append(k) 
                            elif isinstance(v, (dict, list)):
                                extract_and_hide_paths(v)
                                
                        for k in keys_to_delete:
                            del obj[k]
                    elif isinstance(obj, list):
                        for item in obj:
                            extract_and_hide_paths(item)

                # 执行拦截
                extract_and_hide_paths(observation)
                # ==========================================

                obs_str = json.dumps(observation, ensure_ascii=False, cls=NumpyEncoder)
                
                MAX_OBS_LENGTH = 1500 
                if len(obs_str) > MAX_OBS_LENGTH:
                    obs_str = obs_str[:MAX_OBS_LENGTH] + '...[数据过长已截断，请基于当前截断信息进行回答]'
                
                if on_output:
                    status_content = f"工具调用失败：{observation.get('error')}，正在尝试修复..." if isinstance(observation, dict) and observation.get("status") == "error" else "获取到数据，正在解析核心信息..."
                    await on_output({"id": str(uuid.uuid4()), "type": "observation", "content": status_content, "is_append": False, "session_id": session_id})
                
                messages.append({
                    "role": "tool",
                    "tool_call_id": tool_call.id,
                    "name": func_name,
                    "content": obs_str
                })
            continue 
            
        else:
            # ==========================================
            # 【最后一步】：物理拼接
            # ==========================================
            final_answer = message.content or "未返回内容"
            
            # 无论大模型说了啥，我们强制把刚才拦截到的链接贴在它回答的最下面！
            if bypassed_links:
                unique_links = list(set(bypassed_links)) # 去重
                final_answer += "".join(unique_links)
            
            print(f"最终回答: {final_answer}")
            
            if on_output:
                await on_output({
                    "id": str(uuid.uuid4()),
                    "type": "answer",
                    "content": final_answer,
                    "is_append": False,
                    "session_id": session_id
                })
                
            return {"question": question, "final_answer": final_answer, "turns": turn}

    return {"question": question, "final_answer": "抱歉，经过多次查询未能得出最终结论。", "turns": turn}

if __name__ == "__main__":
    async def main():
        print("=== 天文数据智能代理 (Native Async 版) ===")
        while True:
            user_input = input("\n你: ")
            if user_input.lower() in ["exit", "quit"]:
                break
            
            async def dummy_output(msg):
                print(f"[{msg['type'].upper()}] {msg['content']}")
                
            await query(user_input, on_output=dummy_output)

    asyncio.run(main())