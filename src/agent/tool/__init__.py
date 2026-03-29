from .base import tool_registry

from . import astronomy_tools
from . import analysis_tools

# 【修改】：直接在这里给整个文件里的工具打上分类标签！
tool_registry.register_module(astronomy_tools, category="🔭 天文数据查询工具")
tool_registry.register_module(analysis_tools, category="📊 数据分析处理工具")

print("✨ Tool Hub: 所有工具模块 (天文、分析) 已自动扫描并挂载完毕！")

__all__ = ["tool_registry"]