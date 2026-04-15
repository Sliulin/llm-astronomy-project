import asyncio
import json
import os
import sys

# 设置路径映射
PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, PROJECT_ROOT)

from src.agent.core import client, SYSTEM_PROMPT
from src.agent.tool import tool_registry
import src.agent.tool.astronomy_tools
import src.agent.tool.analysis_tools

# ==========================================
# 语义路由测试用例 (覆盖全量工具)
# expected_args_subset 里的值如果是一个列表，则表示“命中列表中任意一个即算成功”
# ==========================================
ROUTING_CASES = [
    {
        "query": "帮我查一下仙女座星系(M31)的具体坐标和红移是多少？",
        "expected_tool": "get_astronomy_object",
        "expected_args_subset": {"object_name": ["M31", "仙女座星系"]}
    },
    {
        "query": "我想看看猎户座大星云（M42）的深空照片，给我返回几张链接。",
        "expected_tool": "get_images",
        "expected_args_subset": {"object_name": ["M42", "猎户座大星云"]}
    },
    {
        "query": "获取类星体 3C 273 的光谱数据，最多返回3条。",
        "expected_tool": "get_spectra",
        "expected_args_subset": {"object_name": "3C 273", "max_spectra": [3, "3"]}
    },
    {
        "query": "以天狼星为中心，0.05度半径内查一下周边有哪些天体。",
        "expected_tool": "query_region_by_name",
        "expected_args_subset": {"object_name": ["天狼星", "Sirius"], "radius": [0.05, "0.05"]}
    },
    {
        "query": "赤经10.68度，赤纬41.26度，这个坐标周边0.1度内有什么天体？",
        "expected_tool": "query_region_by_coordinates",
        "expected_args_subset": {"ra": [10.68, "10.68"], "dec": [41.26, "41.26"]}
    },
    {
        "query": "今晚火星距离地球有多远？视星等是多少？",
        "expected_tool": "get_ephemeris",
        "expected_args_subset": {"target_name": ["火星", "mars", "Mars"]}
    },
    {
        "query": "写一段ADQL，帮我在Gaia DR3星表中查询赤经在10到11度之间的源。",
        "expected_tool": "query_adql",
        "expected_args_subset": {} 
    },
    {
        "query": "以赤经10.68，赤纬41.26为中心，半径1角分，帮我把Gaia和2MASS星表做个交叉匹配。",
        "expected_tool": "cross_match_catalogs",
        "expected_args_subset": {"base_catalog": "gaia", "target_catalog": "2mass"}
    },
    {
        "query": "帮我把这个图像链接下载到本地：https://ned.ipac.caltech.edu/uri/m31.fits",
        "expected_tool": "download_fits_file",
        "expected_args_subset": {"url": ["https://ned.ipac.caltech.edu/uri/m31.fits"]}
    },
    {
        "query": "请对这张下载好的深空图像 m31_deepsky.fits 进行天体源提取，寻找高亮恒星。",
        "expected_tool": "extract_sources_from_fits", 
        "expected_args_subset": {}
    },
    {
        "query": "使用刚刚保存的 mock_gaia_123.json 星表数据帮我画一张赫罗图。",
        "expected_tool": "plot_hr_diagram",
        "expected_args_subset": {}
    },
    {
        "query": "对这份光变曲线数据 lc_data_001.json 进行 Lomb-Scargle 周期分析。",
        "expected_tool": "analyze_lightcurve_period", 
        "expected_args_subset": {}
    }
]

async def test_single_routing(case, tools):
    """测试单条语料的路由准确性"""
    query = case["query"]
    expected_tool = case["expected_tool"]
    
    print(f"\n🗣️ 用户提问: {query}")
    
    messages = [
        {"role": "system", "content": SYSTEM_PROMPT},
        {"role": "user", "content": query}
    ]
    
    try:
        # 请求大模型，限制 temperature 以保证路由结果的稳定性
        response = await client.chat.completions.create(
            model="hunyuan-turbo", 
            messages=messages,
            tools=tools,
            tool_choice="auto",
            temperature=0.1 
        )
        
        message = response.choices[0].message
        
        if not message.tool_calls:
            print(f"❌ 失败: 模型没有调用任何工具，直接回答了: {message.content}")
            return False
            
        tool_call = message.tool_calls[0]
        actual_tool = tool_call.function.name
        
        try:
            actual_args = json.loads(tool_call.function.arguments)
        except json.JSONDecodeError:
            actual_args = {}
            
        print(f"🤖 模型调用: {actual_tool}")
        print(f"📦 提取参数: {actual_args}")
        
        if actual_tool != expected_tool:
            print(f"❌ 失败: 期望调用 '{expected_tool}'，实际调用了 '{actual_tool}'")
            return False
            
        # 兼容性参数校验逻辑 (支持单值或列表)
        for expected_key, expected_val in case.get("expected_args_subset", {}).items():
            if expected_key not in actual_args:
                print(f"❌ 失败: 遗漏了关键参数 '{expected_key}'")
                return False
                
            actual_val = str(actual_args[expected_key]).lower()
            
            # 如果期望值是一个列表，只要实际值在列表内就判定成功
            if isinstance(expected_val, list):
                allowed_vals = [str(x).lower() for x in expected_val]
                if actual_val not in allowed_vals:
                    print(f"❌ 失败: 参数 '{expected_key}' 提取错误。期望之一: {allowed_vals}, 实际: {actual_val}")
                    return False
            else:
                # 兼容老的单值情况
                if actual_val != str(expected_val).lower():
                    print(f"❌ 失败: 参数 '{expected_key}' 提取错误。期望: {expected_val}, 实际: {actual_val}")
                    return False
                    
        print("✅ 路由成功！")
        return True
        
    except Exception as e:
        print(f"⚠️ API 请求异常: {e}")
        return False

async def main():
    print("="*60)
    print("🚀 开始执行大模型意图路由测试 (全量工具版)")
    print("="*60)
    
    tools = tool_registry.get_openai_tools()
    if not tools:
        print("❌ 未加载到任何工具描述，请检查 tool_registry。")
        return
        
    success_count = 0
    total_count = len(ROUTING_CASES)
    
    for case in ROUTING_CASES:
        is_success = await test_single_routing(case, tools)
        if is_success:
            success_count += 1
        # 添加轻微延迟，避免触碰 API 速率限制
        await asyncio.sleep(0.5)
            
    print("="*60)
    print(f"📊 测试结果: 成功 {success_count}/{total_count} (准确率: {success_count/total_count*100:.1f}%)")
    
    if success_count == total_count:
        print("🎉 恭喜！大模型完美识别了所有工具场景！")
    else:
        print("⚠️ 模型在部分场景下路由失败，请根据报错日志调整 @tool 的描述文案。")

if __name__ == "__main__":
    asyncio.run(main())