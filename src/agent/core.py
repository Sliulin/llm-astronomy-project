import sys
import os
import re
import uuid
# 添加项目根目录到Python路径
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))
from typing import Dict, List, Any, Optional
from dotenv import load_dotenv
from openai import OpenAI
from src.agent.tools import tool_registry


class Agent:
    def __init__(self, system=""):
        load_dotenv("./assets/openai.env")
        api_key = os.getenv("HUNYUAN_API_KEY")
        base_url = os.getenv("OPENAI_API_BASE")
        self.client = OpenAI(
            api_key=api_key,
            base_url=base_url
        )
        self.system = system
        self.messages = []
        if self.system:
            self.messages.append({"role": "system", "content": self.system})
        self.dialogue_history = []
    
    def __call__(self, message, step=None):
        # 注意：用户消息已经在query函数中添加，这里不再重复添加
        result = self.execute(step=step)
        # 注意：assistant消息已经在query函数中添加，这里不再重复添加
        return result
    
    def execute(self, step=None):
        response = self.client.chat.completions.create(
            model="hunyuan-turbo",
            messages=self.messages,
            stream=True
        )
        full_response = ""
        for chunk in response:
            if chunk.choices[0].delta.content:
                content = chunk.choices[0].delta.content
                print(content, end="", flush=True)
                full_response += content
        print()
        return full_response
    
    def get_dialogue_history(self):
        return self.dialogue_history


def get_known_actions():
    return tool_registry.get_all_tools()

action_re = re.compile(r'^行动：(\w+): (.*)$')

def get_tool_descriptions():
    return tool_registry.get_tool_descriptions()

def query(question, max_turns=5, on_output=None):
    i = 0
    tools = get_known_actions()
    known_actions = {tool.name: tool for tool in tools}
    system_prompt = f"""
    你需要按照以下循环进行思考和行动：思考、行动、PAUSE、观察。
    循环结束后，你需要输出最终答案。
    使用"思考"描述你对问题的思考过程。
    使用"行动"执行可用的操作之一，然后返回"PAUSE"。
    "观察"是执行操作的结果。

    你可用的操作：

    {get_tool_descriptions()}

    示例会话：

    问题：查询M 31的信息
    思考：我需要使用get_astronomy_object工具查询M 31的信息
    行动：get_astronomy_object: {{"object_name": "M31"}}
    PAUSE

    你将收到以下信息：

    观察：{{"message": "成功找到对象", "StatusCode": 100, "ResultCode": 3, ...}}

    然后你输出：

    思考：根据工具返回的数据，M31的详细信息已经获取到了，可以直接输出答案。
    行动：回答：M31（仙女座星系）是一个螺旋星系，距离地球约254万光年，位于仙女座方向。
            - **名称**：MESSIER 031
            - **位置**：RA: 10.684790, Dec: 41.269060
            - **类型**：Galaxy
            - **红移**：-0.000991
        完整结果已保存到 download 目录
    如果有多个对象，回答：
    1. 第一个对象的信息
    2. 第二个对象的信息
    ...
    
    重要提示：
    1. 在"回答"部分，必须包含观察结果中的具体信息
    2. 如果查询到多个对象，请列出前3-5个对象的名称和关键信息
    3. 半径参数设为0.01度，最大数量设为5

    """
    
    class StreamingAgent(Agent):
        def __init__(self, system=""):
            super().__init__(system)
            self.current_mode = "none"  # none, thinking, answer
            self.thinking_buffer = ""
            self.answer_buffer = ""
            # 初始化消息ID字典
            self.message_ids = {
                "stream": str(uuid.uuid4()),
                "thinking": str(uuid.uuid4()),
                "action": str(uuid.uuid4()),
                "observation": str(uuid.uuid4()),
                "answer": str(uuid.uuid4())
            }
        
        def execute(self, step=None):
            # 根据step生成唯一的消息ID，确保每一轮的消息都分开显示
            message_ids = {
                "stream": str(uuid.uuid4()),
                "thinking": f"thinking_{step}_{str(uuid.uuid4())}",
                "action": f"action_{step}_{str(uuid.uuid4())}",
                "observation": f"observation_{step}_{str(uuid.uuid4())}",
                "answer": f"answer_{step}_{str(uuid.uuid4())}"
            }
            # 更新实例的message_ids，确保其他地方也能使用
            self.message_ids = message_ids
            
            # 确保消息历史不为空，并且格式正确
            if not self.messages:
                # 如果消息历史为空，添加一个默认的系统消息
                self.messages.append({"role": "system", "content": self.system})
            
            response = self.client.chat.completions.create(
                model="hunyuan-turbo",
                messages=self.messages,
                stream=True
            )
            full_response = ""
            buffer = ""  # 用于累积可能被分割的前缀
            filterflag = False

            for chunk in response:
                if chunk.choices[0].delta.content:
                    content = chunk.choices[0].delta.content
                    print(content, end="", flush=True)
                    full_response += content
                    
                    # 累积内容，处理可能被分割的前缀
                    buffer += content
                    
                    # 检测模式切换
                    if "思考：" in buffer:
                        # 提取"思考："后面的内容
                        index = buffer.index("思考：")
                        thinking_content = buffer[index + 3:]
                        # 过滤掉思考内容中的行动和PAUSE
                        if "行动：" in thinking_content:
                            thinking_content = thinking_content.split("行动：")[0].strip()
                        if "PAUSE" in thinking_content:
                            thinking_content = thinking_content.replace("PAUSE", "").strip()
                        self.current_mode = "thinking"
                        self.thinking_buffer = thinking_content
                        
                        if on_output and thinking_content:
                            on_output({
                                "id": message_ids["thinking"],
                                "type": "thinking",
                                "content": thinking_content,
                                "is_append": False,
                                "step": step
                            })
                        
                        filterflag = True
                        # 清空缓冲区
                        buffer = ""
                    elif "回答：" in buffer:
                        # 提取"回答："后面的内容
                        index = buffer.index("回答：")
                        answer_content = buffer[index + 3:]
                        self.current_mode = "answer"
                        self.answer_buffer = answer_content
                        
                        if on_output and answer_content:
                            on_output({
                                "id": message_ids["answer"],
                                "type": "answer",
                                "content": answer_content,
                                "is_append": False,
                                "step": step
                            })
                        
                        filterflag = True
                        # 清空缓冲区
                        buffer = ""
                    elif self.current_mode == "thinking" and content:
                        filtered_content = content                       
                        # 过滤掉思考内容中的行动
                        if "行动" in filtered_content:
                            filterflag = False

                        # 发送思考内容的追加
                        if filtered_content and filterflag:
                            self.thinking_buffer += filtered_content
                            if on_output:
                                on_output({
                                    "id": message_ids["thinking"],
                                    "type": "thinking",
                                    "content": filtered_content,
                                    "is_append": True,
                                    "step": step
                                })
                    elif self.current_mode == "answer" and content:
                        filtered_content = content
                        # 发送回答内容的追加
                        if filtered_content:
                            self.answer_buffer += filtered_content
                            if on_output:
                                on_output({
                                    "id": message_ids["answer"],
                                    "type": "answer",
                                    "content": filtered_content,
                                    "is_append": True,
                                    "step": step
                                })
            print()
            return full_response
    
    bot = StreamingAgent(system_prompt)
    next_prompt = question
    process = {
        "question": question,
        "steps": [],
        "final_answer": ""
    }
    
    # 首先添加用户的初始问题
    user_message = {
        "role": "user",
        "content": question
    }
    bot.messages.append(user_message)
    
    while i < max_turns:
        i += 1
        # 执行AI推理
        result = bot.execute(step=i)
        thinking = ""
        action = ""
        action_input = ""
        lines = result.split('\n')
        for line in lines:
            if line.strip().startswith('思考：'):
                thinking = line.strip()[3:]
            elif line.strip().startswith('行动：'):
                match = action_re.match(line.strip())
                if match:
                    action, action_input = match.groups()
        
        actions = [
            action_re.match(a) 
            for a in result.split('\n') 
            if action_re.match(a)
        ]
        
        # 将AI的响应添加到消息历史中
        assistant_message = {
            "role": "assistant",
            "content": result
        }
        bot.messages.append(assistant_message)
        
        if actions:
            action, action_input = actions[0].groups()
            
            # 处理"回答"行动
            if action == "回答":
                # 提取回答内容
                answer_lines = []
                capture_answer = True
                for line in lines:
                    if line.strip().startswith('回答：'):
                        answer_content = line.strip()[3:]
                        # 过滤掉PAUSE
                        if 'PAUSE' not in answer_content:
                            answer_lines.append(answer_content)
                    elif capture_answer:
                        if line.strip().startswith('思考：') or (line.strip().startswith('行动：') and not '回答' in line):
                            break
                        # 过滤掉PAUSE
                        if 'PAUSE' not in line:
                            answer_lines.append(line)
                
                if answer_lines:
                    final_answer = '\n'.join(answer_lines).strip()
                    process["final_answer"] = final_answer
                    
                    # 发送最终回答到前端
                    # if on_output:
                    #     on_output({
                    #         "id": bot.message_ids["answer"],
                    #         "type": "answer",
                    #         "content": final_answer,
                    #         "is_append": False,
                    #         "step": i
                    #     })
                    
                    process["steps"].append({
                        "step": i,
                        "thinking": thinking,
                        "action": action,
                        "action_input": action_input,
                        "observation": "",
                        "answer": final_answer
                    })
                
                return process
            
            if action not in known_actions:
                raise Exception(f"未知行动: {action}: {action_input}")
            
            print(f" -- 执行 {action} {action_input}")
            if on_output:
                on_output({
                    "id": bot.message_ids["action"],
                    "type": "action",
                    "content": f"执行工具: {action}\n参数: {action_input}",
                    # "data": {
                    #     "action": action,
                    #     "input": action_input
                    # },
                    "is_append": False
                })
            
            import json
            params_dict = json.loads(action_input)
            observation = tool_registry.execute_tool(action, **params_dict)
            
            print("观察:", observation)
            if on_output:
                on_output({
                    "id": bot.message_ids["observation"],
                    "type": "observation",
                    "content": f"观察结果: {str(observation)}",
                    "is_append": False
                })
            
            observation_str = str(observation)
            
            # 为下一轮对话添加用户消息，包含观察结果
            user_message = {
                "role": "user",
                "content": f"观察: {observation_str}"
            }
            bot.messages.append(user_message)
            
            process["steps"].append({
                "step": i,
                "thinking": thinking,
                "action": action,
                "action_input": action_input,
                "observation": observation_str
            })
        else:
            answer_lines = []
            capture_answer = False
            for line in lines:
                if line.strip().startswith('回答：'):
                    capture_answer = True
                    answer_content = line.strip()[3:]
                    # 过滤掉PAUSE
                    if 'PAUSE' not in answer_content:
                        answer_lines.append(answer_content)
                elif line.strip().startswith('行动：回答'):
                    # 处理"行动：回答 PAUSE"的情况
                    capture_answer = True
                elif capture_answer:
                    if line.strip().startswith('思考：') or (line.strip().startswith('行动：') and not '回答' in line):
                        break
                    # 过滤掉PAUSE
                    if 'PAUSE' not in line:
                        answer_lines.append(line)
            
            if answer_lines:
                final_answer = '\n'.join(answer_lines).strip()
                process["final_answer"] = final_answer
                
                # 发送最终回答到前端
                # if on_output:
                #     on_output({
                #         "id": bot.message_ids["answer"],
                #         "type": "answer",
                #         "content": final_answer,
                #         "is_append": False,
                #         "step": i
                #     })
                
                process["steps"].append({
                    "step": i,
                    "thinking": thinking,
                    "action": "",
                    "action_input": "",
                    "observation": "",
                    "answer": final_answer
                })
                
                return process
            
            if result.strip():
                if "PAUSE" in result:
                    pass
                else:
                    process["final_answer"] = result
            
            return process
    
    return process

def run_interactive():
    print("=== 天文数据智能代理 ===")
    print("输入 'exit' 或 'quit' 退出对话")
    print("输入 'reset' 重置对话状态")
    print()
    
    while True:
        try:
            user_input = input("你: ")
            if user_input.lower() in ["exit", "quit"]:
                print("对话结束！")
                break
            if user_input.lower() == "reset":
                print("对话状态已重置！")
                continue
            if not user_input.strip():
                print("请输入内容，不能为空")
                continue
            print()
            query(user_input)
            print()
        except KeyboardInterrupt:
            print("\n对话被中断！")
            break
        except Exception as e:
            print(f"错误: {e}")
            continue
if __name__ == "__main__":
    run_interactive()
