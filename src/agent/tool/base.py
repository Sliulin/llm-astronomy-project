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

    def register_tool(
        self,
        name: str,
        description: str,
        func: Callable,
        parameters: Dict[str, Any],
        returns: str,
    ) -> None:
        """
        注册工具

        Args:
            name: 工具名称
            description: 工具描述
            func: 工具函数
            parameters: 参数定义
            returns: 返回值描述
        """
        tool = Tool(
            name=name,
            description=description,
            func=func,
            parameters=parameters,
            returns=returns,
        )
        self.tools[name] = tool

    def get_tool(self, name: str) -> Optional[Tool]:
        """
        获取工具

        Args:
            name: 工具名称

        Returns:
            工具对象，如果不存在则返回 None
        """
        return self.tools.get(name)

    def get_all_tools(self) -> List[Tool]:
        """
        获取所有工具

        Returns:
            工具列表
        """
        return list(self.tools.values())

    def get_tool_descriptions(self) -> str:
        """
        获取工具描述

        Returns:
            工具描述字符串
        """
        descriptions = []
        for tool in self.tools.values():
            param_desc = ", ".join(
                [
                    f"{name}: {info['description']}"
                    for name, info in tool.parameters.items()
                ]
            )
            descriptions.append(
                f"{tool.name}: {tool.description}。参数: {param_desc}。返回: {tool.returns}"
            )
        return "\n".join(descriptions)

    def execute_tool(self, name: str, **kwargs) -> Any:
        """
        执行工具

        Args:
            name: 工具名称
            **kwargs: 工具参数

        Returns:
            工具执行结果
        """
        tool = self.get_tool(name)
        if not tool:
            raise ValueError(f"工具 {name} 不存在")

        # 打印工具执行信息
        print("-----------------------------------------------")
        print(f"执行工具: {name}, 参数: {kwargs}")

        try:
            # 验证参数
            for param_name in tool.parameters:
                if param_name not in kwargs:
                    raise ValueError(f"缺少必要参数: {param_name}")

            # 执行工具
            result = tool.func(**kwargs)
            # 如果结果包含多个星体信息，只保留前5个
            if isinstance(result, dict) and 'results' in result and isinstance(result['results'], list):
                if len(result['results']) > 5:
                    result['results'] = result['results'][:5]
                    result['message'] = f"找到 {result.get('count', len(result['results']))} 个对象，显示前5个"
            
            return result
        except Exception as e:
            return {"error": str(e), "status": "error"}
