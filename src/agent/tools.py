"""工具模块"""

from .tool.base import ToolRegistry
from .tool.astronomy_tools import register_astronomy_tools
from .tool.analysis_tools import register_analysis_tools

# 创建全局工具注册表实例
tool_registry = ToolRegistry()

# 注册所有工具
register_astronomy_tools(tool_registry)
register_analysis_tools(tool_registry)

__all__ = ["tool_registry"]
