import asyncio
import json
import os
import sys
import time

# ==========================================
# 1. 环境配置
# ==========================================
PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, PROJECT_ROOT)

from src.agent.core import query

# 测试用例文件路径
CASES_FILE = os.path.join(PROJECT_ROOT, "test", "test_cases.json")

def load_cases():
    if not os.path.exists(CASES_FILE):
        print(f"❌ 错误: 找不到测试集文件 {CASES_FILE}")
        sys.exit(1)
    with open(CASES_FILE, 'r', encoding='utf-8') as f:
        return json.load(f)

async def run_test(case_id, question):
    """运行单个测试并打印简报"""
    print(f"\n测试编号: {case_id}")
    print(f"用户提问: {question}")
    
    start_time = time.perf_counter()
    try:
        # 直接调用 core.py 的 query 函数
        # 注意：这里会自动触发你之前写的 log_metric 耗时统计
        result = await query(question, session_id=f"benchmark_{case_id}")
        
        elapsed = time.perf_counter() - start_time
        print(f"✅ 完成! 耗时: {elapsed:.2f}s | 交互轮数: {result.get('turns', 1)}")
        return True
    except Exception as e:
        print(f"❌ 测试失败: {e}")
        return False

def print_menu():
    print(f"\n{'='*20} AstroAgent 性能与路由基准测试器 {'='*20}")
    print("1. 运行【全部】简单用例 (60项)")
    print("2. 运行【全部】复杂用例 (10项)")
    print("3. 运行【全量】测试集 (70项)")
    print("4. 运行单个指定 ID 测试 (如 C01 或 S05)")
    print("q. 退出")

async def main():
    data = load_cases()
    simple_cases = data.get("simple_cases", [])
    complex_cases = data.get("complex_cases", [])

    while True:
        print_menu()
        choice = input("\n请选择功能: ").strip().lower()

        target_cases = []
        if choice == '1':
            target_cases = simple_cases
        elif choice == '2':
            target_cases = complex_cases
        elif choice == '3':
            target_cases = complex_cases + simple_cases
        elif choice == '4':
            tid = input("请输入测试 ID: ").strip().upper()
            target_cases = [c for c in (simple_cases + complex_cases) if c['id'] == tid]
            if not target_cases:
                print("❌ 未找到该 ID。")
                continue
        elif choice == 'q':
            break
        else:
            continue

        print(f"\n🚀 准备执行 {len(target_cases)} 个任务...")
        success_count = 0
        
        for case in target_cases:
            # 执行测试
            if await run_test(case['id'], case['query']):
                success_count += 1
            
            # 适当限速，保护 API 额度
            await asyncio.sleep(1)

        print(f"\n{'='*50}")
        print(f"📊 本轮测试结束: 成功 {success_count}/{len(target_cases)}")
        print(f"💡 详细耗时指标已存入项目根目录的 metrics.csv")
        print(f"{'='*50}\n")

if __name__ == "__main__":
    asyncio.run(main())