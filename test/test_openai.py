import sys
import os

# 添加项目根目录到Python路径
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from src.agent.tools import tool_registry

def test_astronomy_tools():
    """
    测试天文数据工具
    """
    print("=== 测试天文数据工具 ===")
    print("可用工具:")
    
    # 获取所有工具
    tools = tool_registry.get_all_tools()
    for i, tool in enumerate(tools, 1):
        print(f"{i}. {tool.name}: {tool.description}")
    
    print()
    print("输入工具编号选择测试，输入 'exit' 或 'quit' 退出")
    print()
    
    while True:
        # 获取用户输入
        user_input = input("选择工具编号: ")
        
        # 处理特殊命令
        if user_input.lower() in ["exit", "quit"]:
            print("测试完成！")
            break
        
        # 处理工具选择
        try:
            tool_index = int(user_input) - 1
            if 0 <= tool_index < len(tools):
                selected_tool = tools[tool_index]
                print(f"\n=== 测试工具: {selected_tool.name} ===")
                print(f"描述: {selected_tool.description}")
                
                # 根据工具类型获取参数
                if selected_tool.name == "get_astronomy_object":
                    object_name = input("请输入天文对象名称: ")
                    result = tool_registry.execute_tool(selected_tool.name, object_name=object_name)
                elif selected_tool.name == "search_knowledge":
                    query = input("请输入搜索查询: ")
                    result = tool_registry.execute_tool(selected_tool.name, query=query)
                elif selected_tool.name == "get_term_definition":
                    term = input("请输入术语: ")
                    result = tool_registry.execute_tool(selected_tool.name, term=term)
                elif selected_tool.name == "get_entity_info":
                    entity = input("请输入实体名称: ")
                    result = tool_registry.execute_tool(selected_tool.name, entity=entity)
                elif selected_tool.name in ["analyze_objects", "compare_objects", "analyze_redshift"]:
                    objects = input("请输入天文对象名称，用逗号分隔: ")
                    object_list = [obj.strip() for obj in objects.split(",")]
                    result = tool_registry.execute_tool(selected_tool.name, object_names=object_list)
                elif selected_tool.name == "calculate_distance":
                    object1 = input("请输入第一个天文对象名称: ")
                    object2 = input("请输入第二个天文对象名称: ")
                    result = tool_registry.execute_tool(selected_tool.name, object_name1=object1, object_name2=object2)
                else:
                    print("该工具暂不支持交互式测试")
                    continue
                
                # 打印结果
                print("\n测试结果:")
                if isinstance(result, dict):
                    for key, value in result.items():
                        print(f"{key}: {value}")
                else:
                    print(result)
                
            else:
                print("无效的工具编号，请重新输入")
        except ValueError:
            print("请输入有效的数字")
        except Exception as e:
            print(f"测试失败: {e}")
        
        print()

if __name__ == "__main__":
    test_astronomy_tools()
