import os
import sys
import json
import traceback

# ==========================================
# 目录路径修正
# ==========================================
# 当前文件在 test/test_tools.py
# 需要获取上一级目录（项目根目录）并加入到 sys.path
PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, PROJECT_ROOT)

# 现在可以正常导入同级的 src 模块了
from src.agent.tool import tool_registry
import src.agent.tool.astronomy_tools
import src.agent.tool.analysis_tools

# ==========================================
# 预设测试用例字典
# ==========================================
TEST_CASES = {
    "get_astronomy_object": [
        {"object_name": "M31"},          # 正常测试：仙女座星系
        {"object_name": "InvalidNameX"}  # 异常测试：不存在的天体
    ],
    "query_region_by_name": [
        {"object_name": "M31", "radius": 0.05}
    ],
    "query_region_by_coordinates": [
        {"ra": 10.684, "dec": 41.269, "radius": 0.05} # M31 坐标
    ],
    "get_images": [
        {"object_name": "M31", "max_images": 2}
    ],
    "get_spectra": [
        {"object_name": "3C 273", "max_spectra": 2} # 著名类星体
    ],
    "query_adql": [
        # 测试自动注入 TOP 2000 的功能
        {"query": "SELECT source_id, ra, dec, phot_g_mean_mag FROM gaiadr3.gaia_source WHERE ra BETWEEN 10 AND 11 AND dec BETWEEN 41 AND 42"}
    ],
    "get_ephemeris": [
        {"target_name": "Mars"},
        {"target_name": "Halley"}
    ],
    "cross_match_catalogs": [
        {"ra": 10.684, "dec": 41.269, "radius_arcmin": 1.0, "base_catalog": "gaia", "target_catalog": "2mass"}
    ]
}

def print_separator(title=""):
    print(f"\n{'='*20} {title} {'='*20}")

def run_test_case(tool_name, kwargs):
    """执行单个测试用例并格式化输出"""
    print_separator(f"正在执行: {tool_name}")
    print(f"传入参数: {json.dumps(kwargs, ensure_ascii=False)}")
    
    try:
        # 直接调用底层的工具执行器
        result = tool_registry.execute_tool(tool_name, **kwargs)
        
        # 结果截断保护，防止控制台卡死
        result_str = json.dumps(result, ensure_ascii=False, indent=2, default=str)
        if len(result_str) > 1500:
            print("返回结果 (部分截断):")
            print(result_str[:1500] + "\n... [数据过长，已省略剩余部分]")
        else:
            print("返回结果:")
            print(result_str)
            
    except Exception as e:
        print(f"❌ 执行发生异常:")
        traceback.print_exc()

def test_all_tools():
    """自动化测试所有预设用例"""
    print_separator("开始全量自动测试")
    for tool_name, cases in TEST_CASES.items():
        if tool_name not in tool_registry.tools:
            print(f"⚠️ 警告: 工具 {tool_name} 未在注册表中找到，已跳过。")
            continue
            
        for case in cases:
            run_test_case(tool_name, case)
    print_separator("全量自动测试结束")

def interactive_single_tool():
    """交互式测试单个工具"""
    tools = list(tool_registry.tools.keys())
    if not tools:
        print("❌ 未加载任何工具，请检查导入路径！")
        return

    while True:
        print_separator("请选择要测试的工具")
        for i, t in enumerate(tools):
            print(f"[{i}] {t}")
        print("[q] 返回上级菜单")
        
        choice = input("\n请输入工具编号: ").strip()
        if choice.lower() == 'q':
            break
            
        if not choice.isdigit() or int(choice) < 0 or int(choice) >= len(tools):
            print("❌ 无效的输入，请重试。")
            continue
            
        selected_tool = tools[int(choice)]
        tool_info = tool_registry.tools[selected_tool]
        
        print_separator(f"测试工具: {selected_tool}")
        print(f"描述: {tool_info.get('description', '无')}")
        
        print("\n请选择参数输入方式:")
        print("1. 使用预设测试用例")
        print("2. 手动输入自定义参数 (JSON 格式)")
        print("3. 返回上级菜单")
        
        mode = input("请输入选项 [1/2/3]: ").strip()
        
        if mode == '1':
            cases = TEST_CASES.get(selected_tool, [])
            if not cases:
                print(f"⚠️ 工具 {selected_tool} 暂无预设用例，请选择手动输入。")
                continue
                
            print("\n可用的预设用例:")
            for i, case in enumerate(cases):
                print(f"[{i}] {case}")
                
            case_idx = input(f"请选择用例编号 [0-{len(cases)-1}]: ").strip()
            if case_idx.isdigit() and 0 <= int(case_idx) < len(cases):
                run_test_case(selected_tool, cases[int(case_idx)])
            else:
                print("❌ 无效选择。")
                
        elif mode == '2':
            print("\n请输入 JSON 格式的参数字典")
            print("例如: {\"object_name\": \"Sirius\"}")
            json_input = input(">> ").strip()
            if not json_input:
                continue
                
            try:
                custom_kwargs = json.loads(json_input)
                if not isinstance(custom_kwargs, dict):
                    print("❌ 输入必须是 JSON 字典格式！")
                    continue
                run_test_case(selected_tool, custom_kwargs)
            except json.JSONDecodeError:
                print("❌ JSON 解析失败，请检查语法 (注意使用双引号)。")
                
        elif mode == '3':
            continue

def main():
    while True:
        print_separator("天文智能体 - 工具测试器")
        print("1. 测试全部预设工具用例 (一键跑通)")
        print("2. 测试单个指定工具 (支持预设 / 自定义传参)")
        print("3. 退出")
        
        choice = input("\n请选择 [1/2/3]: ").strip()
        
        if choice == '1':
            test_all_tools()
        elif choice == '2':
            interactive_single_tool()
        elif choice == '3':
            print("退出测试程序。")
            break
        else:
            print("❌ 无效输入。")

if __name__ == "__main__":
    main()