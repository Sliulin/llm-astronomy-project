import inspect
from typing import Any, Callable, Dict, List, get_type_hints

def tool(description: str):
    """
    魔法装饰器：只需在函数上挂上 @tool("描述")，
    即可将其一键暴露给大模型使用！
    """
    def decorator(func):
        func._is_tool = True
        func._tool_description = description
        return func
    return decorator

class ToolRegistry:
    def __init__(self):
        self.tools: Dict[str, Dict[str, Any]] = {}

    def register_instance(self, instance: Any):
        """扫描类实例中所有带有 @tool 装饰器的方法"""
        for name, method in inspect.getmembers(instance, predicate=inspect.ismethod):
            if getattr(method, '_is_tool', False):
                self._auto_register_method(name, getattr(method, '_tool_description', ""), method)

    def register_module(self, module: Any, category: str = "其他工具"):
        """扫描整个文件时，给所有工具打上 category 标签"""
        for name, func in inspect.getmembers(module, predicate=inspect.isfunction):
            if getattr(func, '_is_tool', False):
                self._auto_register_method(name, getattr(func, '_tool_description', ""), func, category)

    def _auto_register_method(self, name: str, description: str, method: Callable, category: str = "其他工具"):
        """接收并保存 category"""
        sig = inspect.signature(method)
        type_hints = get_type_hints(method)
        
        docstring = inspect.getdoc(method) or ""
        param_descriptions = {}
        in_args = False
        for line in docstring.split('\n'):
            line = line.strip()
            if line.startswith('Args:') or line.startswith('Parameters:'):
                in_args = True
                continue
            if in_args and line.startswith(('Returns:', 'Return:', 'Raises:')):
                break
            if in_args and ':' in line:
                parts = line.split(':', 1)
                clean_param_name = parts[0].strip().split()[0].strip()
                param_descriptions[clean_param_name] = parts[1].strip()

        properties = {}
        required = []

        for param_name, param in sig.parameters.items():
            if param_name == 'self': continue
            param_type = "string"
            hint = type_hints.get(param_name, str)
            if hint == int: param_type = "integer"
            elif hint == float: param_type = "number"
            elif hint == bool: param_type = "boolean"
                
            properties[param_name] = {
                "type": param_type,
                "description": param_descriptions.get(param_name, f"参数 {param_name}")
            }
            if param.default == inspect.Parameter.empty: required.append(param_name)

        self.tools[name] = {
            "name": name,
            "description": description,
            "parameters": {"type": "object", "properties": properties, "required": required},
            "func": method,
            "category": category  # 保存分类信息
        }
        print(f"🔧 自动注册工具成功: [{category}] {name}")

    def get_frontend_tools(self) -> List[Dict[str, Any]]:
        """专门为前端生成的工具列表，动态提取函数对象上的元数据"""
        return [
            {
                "name": info["name"],
                "description": info["description"],
                "parameters": info["parameters"],
                "category": info["category"],  # 直接用字典里已经存好的分类
                "title": getattr(info["func"], 'title', info["name"]),
                "icon": getattr(info["func"], 'icon', '🔧')
            }
            for info in self.tools.values()
        ]

    def get_openai_tools(self) -> List[Dict[str, Any]]:
        openai_tools = []
        for tool_info in self.tools.values():
            openai_tools.append({
                "type": "function",
                "function": {
                    "name": tool_info["name"],
                    "description": tool_info["description"],
                    "parameters": tool_info["parameters"]
                }
            })
        return openai_tools

    def execute_tool(self, name: str, **kwargs) -> Any:
        tool_info = self.tools.get(name)
        if not tool_info:
            return {"error": f"工具 {name} 不存在", "status": "error"}

        print("-" * 50)
        print(f"🔧 执行工具: {name}, 参数: {kwargs}")
        
        try:
            sig = inspect.signature(tool_info["func"])
            for param_name, param in sig.parameters.items():
                if param_name != 'self' and param_name not in kwargs:
                    if param.default != inspect.Parameter.empty:
                        kwargs[param_name] = param.default
                    else:
                        raise ValueError(f"缺少必要参数: {param_name}")

            result = tool_info["func"](**kwargs)
            
            if isinstance(result, dict) and 'results' in result and isinstance(result['results'], list):
                if len(result['results']) > 5:
                    result['results'] = result['results'][:5]
                    result['message'] = f"找到 {result.get('count', len(result['results']))} 个对象，仅显示前5个"
            
            return result
        except Exception as e:
            return {"error": str(e), "status": "error"}

# 暴露出全局注册表实例
tool_registry = ToolRegistry()