#!/usr/bin/env python3
"""
测试天文工具功能
"""

import sys
import os

# 添加项目根目录到Python路径
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from src.agent.tools import tool_registry


def test_astronomy_tools():
    """测试天文工具"""
    print("=== 测试天文工具 ===")
    
    # 使用已创建的工具注册表
    registry = tool_registry
    
    # 测试工具注册
    tools = registry.get_all_tools()
    print(f"\n已注册工具数量: {len(tools)}")
    for tool in tools:
        print(f"- {tool.name}: {tool.description}")
    
    # 测试天文对象查询工具
    print("\n=== 测试天文对象查询工具 ===")
    result = registry.execute_tool("get_astronomy_object", object_name="M 31")
    print(f"状态: {result.get('message', '未知')}")
    if result.get('ResultCode') == 3:
        print(f"对象类型: {result.get('object_type_full')}")
        print(f"位置: {result.get('position_str')}")
        print(f"红移: {result.get('redshift_value')}")
    
    # 测试区域查询工具（按名称）
    print("\n=== 测试区域查询工具（按名称）===")
    result = registry.execute_tool("query_region_by_name", object_name="M 31", radius=0.05)
    print(f"找到 {result.get('count', 0)} 个对象")
    for i, obj in enumerate(result.get('results', [])[:3]):
        print(f"  {i+1}. {obj['name']} - {obj['type']}")
    
    # 测试图像查询工具
    print("\n=== 测试图像查询工具 ===")
    result = registry.execute_tool("get_images", object_name="M 1", max_images=3)
    print(f"找到 {result.get('count', 0)} 个图像")
    for i, image in enumerate(result.get('images', [])[:3]):
        print(f"  {i+1}. {image}")
    
    # 测试光谱查询工具
    print("\n=== 测试光谱查询工具 ===")
    result = registry.execute_tool("get_spectra", object_name="3C 273", max_spectra=3)
    print(f"找到 {result.get('count', 0)} 个光谱")
    for i, spectrum in enumerate(result.get('spectra', [])[:3]):
        print(f"  {i+1}. {spectrum}")
    
    # 测试数据表查询工具
    print("\n=== 测试数据表查询工具 ===")
    result = registry.execute_tool("get_table", object_name="M 31", table_type="positions")
    print(f"找到 {result.get('count', 0)} 条记录")
    print(f"列名: {result.get('columns', [])}")
    
    # 测试缓存清理工具
    print("\n=== 测试缓存清理工具 ===")
    result = registry.execute_tool("clear_cache")
    print(f"状态: {result.get('message', '未知')}")
    
    print("\n=== 测试完成 ===")


if __name__ == "__main__":
    test_astronomy_tools()
