from typing import Dict, List, Any, Callable, Optional
from dataclasses import dataclass

@dataclass
class Tool:
    """工具类"""
    name: str
    description: str
    func: Callable
    parameters: Dict[str, Any]
    returns: str

class ToolRegistry:
    """工具注册表"""

    def __init__(self):
        """初始化工具注册表"""
        self.tools: Dict[str, Tool] = {}

    def register_tool(self, name: str, description: str, func: Callable, parameters: Dict[str, Any], returns: str) -> None:
        """注册工具"""
        tool = Tool(
            name=name,
            description=description,
            func=func,
            parameters=parameters,
            returns=returns,
        )
        self.tools[name] = tool

    def get_tool(self, name: str) -> Optional[Tool]:
        return self.tools.get(name)

    def get_all_tools(self) -> List[Tool]:
        return list(self.tools.values())

    # ==========================================
    # 核心改造：生成原生的 OpenAI Tools 格式
    # ==========================================
    def get_openai_tools(self) -> List[Dict[str, Any]]:
        """获取兼容 OpenAI Function Calling 格式的工具列表"""
        openai_tools = []
        for tool in self.tools.values():
            properties = {}
            required = []
            
            for param_name, info in tool.parameters.items():
                properties[param_name] = {
                    "type": info.get("type", "string"),
                    "description": info.get("description", "")
                }
                # 【修复 1】只有没有 default 默认值的参数，才强制要求大模型必填
                if "default" not in info:
                    required.append(param_name)
                
            openai_tool = {
                "type": "function",
                "function": {
                    "name": tool.name,
                    "description": tool.description,
                    "parameters": {
                        "type": "object",
                        "properties": properties,
                        "required": required
                    }
                }
            }
            openai_tools.append(openai_tool)
            
        return openai_tools

    def execute_tool(self, name: str, **kwargs) -> Any:
        """执行工具"""
        tool = self.get_tool(name)
        if not tool:
            return {"error": f"工具 {name} 不存在", "status": "error"}

        print("-----------------------------------------------")
        print(f"🔧 执行工具: {name}, 参数: {kwargs}")

        try:
            # 【修复 2】如果大模型没传可选参数，自动补全默认值
            for param_name, info in tool.parameters.items():
                if param_name not in kwargs:
                    if "default" in info:
                        kwargs[param_name] = info["default"]
                    else:
                        raise ValueError(f"缺少必要参数: {param_name}")

            result = tool.func(**kwargs)
            
            if isinstance(result, dict) and 'images' in result:
                return {
                    "status": "success",
                    "data_type": "images_list",
                    "count": len(result['images']),
                    "links": result['images'][:3], # 只给它前三个，节省 Token
                    "note": "请将上述 links 转换为 Markdown 下载链接展示给用户"
                }
            
            return result
        except Exception as e:
            # 返回明确的错误结构
            return {"error": str(e), "status": "error"}