import sys
import os

# 添加项目根目录到Python路径
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from src.agent.tools import tool_registry

def test_analyze_objects():
    """
    测试天文对象统计分析工具
    """
    print("\n=== 测试天文对象统计分析工具 ===")
    
    try:
        # 测试对象列表
        test_objects = ["M 31", "NGC 4565", "ARP 319"]
        
        # 执行分析
        result = tool_registry.execute_tool("analyze_objects", object_names=test_objects)
        
        print(f"✓ 分析对象数量: {result.get('total_objects')}")
        print(f"✓ 成功分析对象: {result.get('successful_objects')}")
        print(f"✓ 分析失败对象: {result.get('error_objects')}")
        print(f"✓ 对象类型分布: {result.get('type_distribution')}")
        print(f"✓ 红移分析结果: {result.get('redshift_analysis')}")
        
        return True
    except Exception as e:
        print(f"✗ 测试失败: {e}")
        return False

def test_compare_objects():
    """
    测试多对象比较工具
    """
    print("\n=== 测试多对象比较工具 ===")
    
    try:
        # 测试对象列表
        test_objects = ["M 31", "NGC 4565"]
        
        # 执行比较
        result = tool_registry.execute_tool("compare_objects", object_names=test_objects)
        
        print(f"✓ 比较对象数量: {len(result.get('objects', []))}")
        print(f"✓ 比较点数量: {len(result.get('comparison_points', []))}")
        
        # 打印比较结果
        for obj in result.get('objects', []):
            print(f"  - {obj.get('name')}: {obj.get('type')}, 红移: {obj.get('redshift')}")
        
        return True
    except Exception as e:
        print(f"✗ 测试失败: {e}")
        return False

def test_calculate_distance():
    """
    测试距离计算工具
    """
    print("\n=== 测试距离计算工具 ===")
    
    try:
        # 测试对象
        object1 = "M 31"
        object2 = "NGC 4565"
        
        # 执行距离计算
        result = tool_registry.execute_tool("calculate_distance", 
                                               object_name1=object1, 
                                               object_name2=object2)
        
        if "error" in result:
            print(f"✗ 计算失败: {result['error']}")
            return False
        else:
            print(f"✓ 计算 {result['object1']} 和 {result['object2']} 之间的距离")
            print(f"  - 角度距离: {result['distance_degrees']} 度")
            print(f"  - 弧分距离: {result['distance_arcminutes']} 弧分")
            print(f"  - 弧秒距离: {result['distance_arcseconds']} 弧秒")
            print(f"  - 位置1: {result['position1']}")
            print(f"  - 位置2: {result['position2']}")
            
            return True
    except Exception as e:
        print(f"✗ 测试失败: {e}")
        return False

def test_analyze_redshift():
    """
    测试红移分析工具
    """
    print("\n=== 测试红移分析工具 ===")
    
    try:
        # 测试对象列表
        test_objects = ["M 31", "NGC 4565", "ARP 319"]
        
        # 执行红移分析
        result = tool_registry.execute_tool("analyze_redshift", object_names=test_objects)
        
        print(f"✓ 分析对象数量: {result.get('objects_analyzed')}")
        print(f"✓ 总对象数量: {result.get('total_objects')}")
        
        # 打印分析结果
        for obj in result.get('objects_with_redshift', []):
            print(f"  - {obj.get('name')}: 红移={obj.get('redshift')}, 类型={obj.get('type')}, 估算距离={obj.get('estimated_distance_mpc'):.2f} Mpc")
        
        if 'redshift_stats' in result:
            print(f"✓ 红移统计: 最小={result['redshift_stats'].get('min')}, 最大={result['redshift_stats'].get('max')}, 平均={result['redshift_stats'].get('average'):.4f}")
        
        if 'distance_stats' in result:
            print(f"✓ 距离统计: 最小={result['distance_stats'].get('min'):.2f}, 最大={result['distance_stats'].get('max'):.2f}, 平均={result['distance_stats'].get('average'):.2f} Mpc")
        
        return True
    except Exception as e:
        print(f"✗ 测试失败: {e}")
        return False

def main():
    """
    主测试函数
    """
    print("开始测试数据分析工具...")
    
    # 运行所有测试
    tests = [
        ("天文对象统计分析", test_analyze_objects),
        ("多对象比较", test_compare_objects),
        ("距离计算", test_calculate_distance),
        ("红移分析", test_analyze_redshift)
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
        print("🎉 所有数据分析工具测试通过！")
    else:
        print("⚠️  部分测试失败，需要进一步检查。")

if __name__ == "__main__":
    main()
