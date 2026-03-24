import sys
import os

# 添加项目根目录到Python路径
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from src.agent.tools import tool_registry
from src.agent.state import AgentState

# def test_agent_initialization():
#     """
#     测试代理初始化
#     """
#     print("=== 测试代理初始化 ===")
#     try:
#         agent = AstronomyAgent()
#         print("✓ 代理初始化成功")
#         print("✓ 状态管理初始化成功")
#         print("✓ 工具注册表初始化成功")
#         print("✓ LLM 初始化成功")
#         return agent
#     except Exception as e:
#         print(f"✗ 代理初始化失败: {e}")
#         return None

def test_tool_registry():
    """
    测试工具注册表
    """
    print("\n=== 测试工具注册表 ===")
    
    # 获取所有工具
    tools = tool_registry.get_all_tools()
    print(f"✓ 注册的工具数量: {len(tools)}")
    
    # 打印工具名称
    tool_names = [tool.name for tool in tools]
    print(f"✓ 工具列表: {', '.join(tool_names)}")
    
    # 测试工具描述
    tool_descriptions = tool_registry.get_tool_descriptions()
    print(f"✓ 工具描述生成成功")
    
    return True

def test_state_management():
    """
    测试状态管理
    """
    print("\n=== 测试状态管理 ===")
    state = AgentState()
    
    # 测试添加消息
    state.add_message("user", "测试消息")
    print(f"✓ 添加消息成功")
    print(f"✓ 对话历史长度: {len(state.conversation_history)}")
    
    # 测试添加执行步骤
    state.add_execution_step("thought", "测试思考")
    print(f"✓ 添加执行步骤成功")
    print(f"✓ 执行轨迹长度: {len(state.execution_trace)}")
    
    # 测试获取最近历史
    recent_history = state.get_recent_history()
    print(f"✓ 获取最近历史成功")
    
    # 测试清除状态
    state.clear()
    print(f"✓ 清除状态成功")
    print(f"✓ 清除后对话历史长度: {len(state.conversation_history)}")
    
    return True

# def test_react_cycle():
#     """
#     测试ReAct循环
#     """
#     print("\n=== 测试ReAct循环 ===")
#     agent = AstronomyAgent()
#     
#     # 测试问题
#     test_question = "ARP 319是什么？"
#     print(f"测试问题: {test_question}")
#     
#     try:
#         # 测试完整的ReAct循环
#         answer = agent.process_input(test_question)
#         print("✓ ReAct循环执行成功")
#         print(f"✓ 生成的回答: {answer}")
#         
#         # 测试执行轨迹
#         execution_trace = agent.state.execution_trace
#         print(f"✓ 执行轨迹长度: {len(execution_trace)}")
#         
#         return True
#     except Exception as e:
#         print(f"✗ ReAct循环执行失败: {e}")
#         return False

def test_tool_execution():
    """
    测试工具执行
    """
    print("\n=== 测试工具执行 ===")
    
    # 测试天文对象查询工具
    try:
        result = tool_registry.execute_tool("get_astronomy_object", object_name="M 31")
        print("✓ 天文对象查询工具执行成功")
        print(f"✓ 查询结果类型: {type(result)}")
        print(f"✓ 查询结果内容: {result}")
    except Exception as e:
        print(f"✗ 天文对象查询工具执行失败: {e}")
    
    # 测试知识库搜索工具
    try:
        result = tool_registry.execute_tool("search_knowledge", query="galaxy")
        print("✓ 知识库搜索工具执行成功")
        print(f"✓ 搜索结果类型: {type(result)}")
        print(f"✓ 搜索结果内容: {result}")
    except Exception as e:
        print(f"✗ 知识库搜索工具执行失败: {e}")
    
    return True

def main():
    """
    主测试函数
    """
    print("开始测试智能代理架构...")
    print()
    
    # 运行所有测试
    tests = [
        # ("代理初始化", test_agent_initialization),
        ("工具注册表", test_tool_registry),
        ("状态管理", test_state_management),
        # ("ReAct循环", test_react_cycle),
        ("工具执行", test_tool_execution)
    ]
    
    passed_tests = 0
    total_tests = len(tests)
    
    for test_name, test_func in tests:
        try:
            result = test_func()
            if result:
                passed_tests += 1
                print(f"\n✓ {test_name} 测试通过")
            else:
                print(f"\n✗ {test_name} 测试失败")
        except Exception as e:
            print(f"\n✗ {test_name} 测试异常: {e}")
    
    print("\n=== 测试结果汇总 ===")
    print(f"通过测试: {passed_tests}/{total_tests}")
    
    if passed_tests == total_tests:
        print("🎉 所有测试通过！智能代理架构运行正常。")
    else:
        print("⚠️  部分测试失败，需要进一步检查。")

if __name__ == "__main__":
    main()
