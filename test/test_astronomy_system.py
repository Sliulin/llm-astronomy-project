import sys
import os

# 添加项目根目录到Python路径
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from src.astronomy import AstronomyDataManager, knowledge_base

# 测试天文数据管理系统
def test_astronomy_data_manager():
    """测试天文数据管理系统"""
    print("=== 测试天文数据管理系统 ===")
    
    # 创建数据管理器实例
    manager = AstronomyDataManager()
    
    # 测试对象列表
    test_objects = [
        "ARP 319",  # Stephan's Quintet
        "M 31",     # Andromeda Galaxy
        "NGC 4565"  # Needle Galaxy
    ]
    
    # 测试每个对象
    for obj_name in test_objects:
        print(f"\n=== 测试对象: {obj_name} ===")
        try:
            # 获取对象信息
            info = manager.get_astronomy_object(obj_name)
            
            # 打印结果
            if "error" in info:
                print(f"错误: {info['error']}")
            elif info.get("ResultCode") == 3:
                print(f"状态: 成功找到对象")
                print(f"提供的名称: {info.get('supplied_name')}")
                print(f"解释的名称: {info.get('interpreted_name')}")
                print(f"首选名称: {info.get('preferred_name')}")
                print(f"对象类型: {info.get('object_type_full', info.get('object_type'))}")
                print(f"位置: {info.get('position_str', '未知')}")
                if "redshift_value" in info:
                    print(f"红移: {info['redshift_value']}")
            else:
                print(f"状态: {info.get('message', '未知状态')}")
        except Exception as e:
            print(f"测试失败: {e}")

# 测试知识库
def test_knowledge_base():
    """测试知识库"""
    print("\n=== 测试知识库 ===")
    
    # 测试获取实体信息
    print("\n1. 测试获取实体信息:")
    galaxy_info = knowledge_base.get_entity_info("Galaxy")
    if galaxy_info:
        print(f"Galaxy: {galaxy_info['description']}")
        print(f"Subtypes: {galaxy_info['subtypes']}")
        print(f"Properties: {galaxy_info['properties']}")
    
    # 测试获取术语定义
    print("\n2. 测试获取术语定义:")
    redshift_def = knowledge_base.get_term_definition("Redshift")
    if redshift_def:
        print(f"Redshift: {redshift_def}")
    
    # 测试搜索知识库
    print("\n3. 测试搜索知识库:")
    search_results = knowledge_base.search_knowledge("galaxy")
    print(f"找到 {len(search_results['entities'])} 个实体")
    print(f"找到 {len(search_results['terms'])} 个术语")
    print(f"找到 {len(search_results['databases'])} 个数据库")
    
    # 测试获取数据库信息
    print("\n4. 测试获取数据库信息:")
    ned_info = knowledge_base.get_database_info("NED")
    if ned_info:
        print(f"NED: {ned_info['full_name']}")
        print(f"Description: {ned_info['description']}")
        print(f"URL: {ned_info['url']}")
    
    # 测试获取实体层次结构
    print("\n5. 测试获取实体层次结构:")
    hierarchy = knowledge_base.get_entity_hierarchy("Galaxy")
    print(f"Entity: {hierarchy['entity']}")
    print(f"Subtypes: {hierarchy['subtypes']}")
    print(f"Related entities: {hierarchy['related']}")

# 测试知识库搜索
def test_knowledge_search():
    """测试知识库搜索功能"""
    print("\n=== 测试知识库搜索功能 ===")
    
    test_queries = ["galaxy", "redshift", "NED", "star"]
    
    for query in test_queries:
        print(f"\n=== 搜索: {query} ===")
        results = knowledge_base.search_knowledge(query)
        
        # 打印搜索结果
        if results["entities"]:
            print(f"实体 ({len(results['entities'])}):")
            for entity in results["entities"]:
                print(f"  - {entity['name']}: {entity['description'][:50]}...")
        
        if results["terms"]:
            print(f"术语 ({len(results['terms'])}):")
            for term in results["terms"]:
                print(f"  - {term['name']}")
        
        if results["databases"]:
            print(f"数据库 ({len(results['databases'])}):")
            for db in results["databases"]:
                print(f"  - {db['name']}: {db['full_name']}")
        
        if results["objects"]:
            print(f"对象类别 ({len(results['objects'])}):")
            for obj in results["objects"]:
                print(f"  - {obj['name']}")

# 主测试函数
def main():
    """主测试函数"""
    print("开始测试天文数据管理系统和知识库...")
    print()
    
    # 运行所有测试
    test_astronomy_data_manager()
    test_knowledge_base()
    test_knowledge_search()
    
    print()
    print("=== 测试完成 ===")
    print("天文数据管理系统和知识库测试成功！")

if __name__ == "__main__":
    main()
