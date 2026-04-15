import asyncio
import json
import os
import re
import sys
import uuid
import time
import csv
from datetime import datetime
from dotenv import load_dotenv
from openai import AsyncOpenAI

# 添加项目根目录到 Python 路径
BASE_DIR = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
sys.path.insert(0, BASE_DIR)

from src.agent.tool import tool_registry

METRICS_FILE = os.path.join(BASE_DIR, "metrics.csv")
def log_metric(context_label: str, step_type: str, name: str, cost_seconds: float):
    """将耗时指标追加到 CSV 文件中，专用于后期统计"""
    file_exists = os.path.exists(METRICS_FILE)
    try:
        with open(METRICS_FILE, mode='a', newline='', encoding='utf-8') as f:
            # 🟢 核心修复：如果文件是新建的，先写入一个 BOM 头 (\ufeff)
            if not file_exists:
                f.write('\ufeff') 
                
            writer = csv.writer(f)
            if not file_exists:
                writer.writerow(["Timestamp", "Context", "StepType", "Name", "CostSeconds"])
            
            safe_context = str(context_label).replace('\n', '').replace('\r', '')[:10]
            writer.writerow([datetime.now().strftime("%Y-%m-%d %H:%M:%S"), safe_context, step_type, name, f"{cost_seconds:.3f}"])
    except Exception as e:
        print(f"⚠️ 写入性能指标失败: {e}")


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
3. 数据整理：请从工具返回的复杂数据中提取核心信息（如名称、坐标、红移、数量等），并整理成自然的 Markdown 表格。
4. 链接渲染：当遇到 .fits 或 .fits.gz 图像链接时，必须将其转化为标准的 Markdown 链接。
   - 格式：[文字描述](链接地址)
   - 示例：[点击下载 M31 的 FITS 图像](https://ned.ipac.caltech.edu/...)
   - 注意：方括号 [] 和 圆括号 () 之间严禁有任何空格。
5. 如果收到图像链接saved_image_path，不要输出任何链接，系统会自动在你的回答末尾生成正确的下载卡片，你只需在正文中用文字告知用户“文件已成功生成”即可。
【当前环境】：
所有的图像存储在本地 download/ 目录下，或指向远程 NED 数据库。如果是本地路径，请确保链接正确。"""

# 全局会话记忆
session_memory = {}

async def query(question: str, session_id: str = "default", max_turns: int = 5, on_output=None):
    global session_memory
    
    total_start_time = time.perf_counter()  # 🟢 记录整个问题处理的总起点

    if session_id not in session_memory:
        session_memory[session_id] = [{"role": "system", "content": SYSTEM_PROMPT}]
    
    messages = session_memory[session_id]
    
    # 截断历史记录以控制上下文长度
    if len(messages) > 10:
        session_memory[session_id] = [messages[0]] + messages[-6:]
        messages = session_memory[session_id]
    
    messages.append({"role": "user", "content": question})
    tools = tool_registry.get_openai_tools()
    
    # 收集被拦截的本地文件下载链接
    bypassed_links = []
    
    turn = 0
    while turn < max_turns:
        turn += 1
        print(f"\n--- 第 {turn} 轮思考 (Session: {session_id[:8]}) ---")
        
        llm_start_time = time.perf_counter() # 🟢 开始计时

        try:
            response = await client.chat.completions.create(
                model="hunyuan-lite", 
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
        
        llm_cost_time = time.perf_counter() - llm_start_time # 🟢 结束计时
        print(f"⏱️ [性能指标] 大模型思考耗时: {llm_cost_time:.2f}s")
        log_metric(question, "LLM", "hunyuan-turbo", llm_cost_time)# 🟢 落盘统计
        
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
                        "content": f"正在调用工具：{func_name}({func_args})", 
                        "is_append": False, "session_id": session_id
                    })

                await asyncio.sleep(0.01)
                
                tool_start_time = time.perf_counter() # 🟢 开始计时
                # 执行本地天文工具
                observation = await asyncio.to_thread(tool_registry.execute_tool, func_name, **func_args)
                
                tool_cost_time = time.perf_counter() - tool_start_time # 🟢 结束计时
                print(f"⏱️ [性能指标] 工具 ({func_name}) 执行耗时: {tool_cost_time:.2f}s")
                log_metric(func_name, "Tool", func_name, tool_cost_time) # 🟢 落盘统计
                
                # 提取路径生成前端可访问的下载链接，保留原字段供模型调用
                def extract_and_hide_paths(obj):
                    if isinstance(obj, dict):
                        for k, v in obj.items():
                            if isinstance(v, str) and ('\\download\\' in v or '/download/' in v):
                                normalized = v.replace('\\', '/')
                                rel_path = normalized.split('/download/')[-1]
                                url = f"http://localhost:8000/downloads/{rel_path}"
                                # 保存前端下载链接至全局列表，稍后附加到最终回答末尾
                                bypassed_links.append(f"\n\n**[原始数据已下载到downloads目录<br><span style='margin-left: 1.2em;'>点击查看原始数据 ({k})</span>]({url})**")
                                
                            elif isinstance(v, (dict, list)):
                                extract_and_hide_paths(v)
                                
                    elif isinstance(obj, list):
                        for item in obj:
                            extract_and_hide_paths(item)

                # 执行拦截
                extract_and_hide_paths(observation)

                obs_str = json.dumps(observation, ensure_ascii=False, cls=NumpyEncoder)
                
                MAX_OBS_LENGTH = 500 
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
            # 拼接最终回答内容
            final_answer = message.content or "未返回内容"
            
            final_answer = re.sub(r'\[[^\]]*\]\((sandbox:|file:|\./|\.\\)[^\)]*\)', '', final_answer)
            final_answer = final_answer.strip() # 清理残留的空行
            
            # 将拦截到的文件链接附加到回答末尾
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
                
            total_cost_time = time.perf_counter() - total_start_time  # 🟢 计算并记录端到端总耗时
            log_metric(question, "Total", "End-to-End", total_cost_time)
            print(f"🏁 [性能指标] 问题端到端总耗时: {total_cost_time:.2f}s\n")

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