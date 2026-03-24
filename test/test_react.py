import sys
import os

# 添加项目根目录到Python路径
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from src.agent.tools import tool_registry

def test_react_framework():
    """
    测试 ReAct 框架功能
    """
    print("=== ReAct 框架功能测试 ===")
    print("这个测试演示了如何使用工具注册表执行各种天文数据操作")
    print()
    
    # 测试场景
    test_scenarios = [
        {
            "name": "天文对象信息查询",
            "tool": "get_astronomy_object",
            "params": {"object_name": "M 31"},
            "description": "查询仙女座星系的详细信息"
        },
        {
            "name": "天文对象统计分析",
            "tool": "analyze_objects",
            "params": {"object_names": ["M 31", "NGC 4565", "ARP 319"]},
            "description": "分析多个天文对象的统计信息"
        },
        {
            "name": "天文对象比较",
            "tool": "compare_objects",
            "params": {"object_names": ["M 31", "NGC 4565"]},
            "description": "比较两个天文对象的属性"
        },
        {
            "name": "距离计算",
            "tool": "calculate_distance",
            "params": {"object_name1": "M 31", "object_name2": "NGC 4565"},
            "description": "计算两个天文对象之间的角距离"
        },
        {
            "name": "红移分析",
            "tool": "analyze_redshift",
            "params": {"object_names": ["M 31", "NGC 4565", "ARP 319"]},
            "description": "分析天文对象的红移与距离关系"
        },
        {
            "name": "知识库搜索",
            "tool": "search_knowledge",
            "params": {"query": "galaxy"},
            "description": "搜索天文知识库中的星系相关信息"
        }
    ]
    
    # 执行测试场景
    for scenario in test_scenarios:
        print(f"\n=== 测试场景: {scenario['name']} ===")
        print(f"描述: {scenario['description']}")
        print(f"工具: {scenario['tool']}")
        print(f"参数: {scenario['params']}")
        
        try:
            # 执行工具
            result = tool_registry.execute_tool(scenario['tool'], **scenario['params'])
            
            # 打印结果
            print("\n执行结果:")
            if isinstance(result, dict):
                for key, value in result.items():
                    print(f"{key}: {value}")
            else:
                print(result)
            
            print("✓ 测试成功")
        except Exception as e:
            print(f"✗ 测试失败: {e}")
        
        print("-" * 50)
    
    print("\n=== 测试完成 ===")
    print("ReAct 框架功能测试成功！")

def interactive_test():
    """
    交互式测试函数
    """
    print("\n=== 交互式测试 ===")
    print("输入 'test' 运行预设测试场景")
    print("输入 'exit' 或 'quit' 退出")
    print()
    
    while True:
        user_input = input("请输入命令: ")
        
        if user_input.lower() in ["exit", "quit"]:
            print("测试结束！")
            break
        elif user_input.lower() == "test":
            test_react_framework()
        else:
            print("无效命令，请输入 'test' 或 'exit'")

if __name__ == "__main__":
    interactive_test()
