import requests
import urllib.request
import json
import httpx
import time

# NED ObjectLookup API 配置
NED_API_URL = "https://ned.ipac.caltech.edu/srs/ObjectLookup"  # NED ObjectLookup API URL

# 测试数据 - 天文对象名称
TEST_OBJECTS = [
    "ARP 319",  # 已知对象
    "abc",      # 不是对象名称
    "M 31",     # 仙女座星系
    "NGC 4565"  # 铅笔星系
]

def test_requests_post():
    """使用requests库发送POST请求"""
    print("=== 测试 requests POST 请求 ===")
    total_time = 0
    try:
        # 对每个测试对象进行测试
        for obj_name in TEST_OBJECTS:
            print(f"\n测试对象: {obj_name}")
            # 构建请求数据
            data = {
                "json": json.dumps({"name": {"v": obj_name}})
            }
            # 记录开始时间
            start_time = time.time()
            # 发送POST请求
            response = requests.post(NED_API_URL, data=data, timeout=10)
            # 计算响应时间
            response_time = time.time() - start_time
            total_time += response_time
            # 打印响应结果
            print(f"状态码: {response.status_code}")
            print(f"响应时间: {response_time:.4f} 秒")
            print(f"响应内容: {response.json()}")
        # 计算平均响应时间
        avg_time = total_time / len(TEST_OBJECTS)
        print(f"\n平均响应时间: {avg_time:.4f} 秒")
        return True, avg_time
    except Exception as e:
        print(f"错误: {e}")
        return False, 0

def test_urllib_post():
    """使用urllib库发送POST请求"""
    print("\n=== 测试 urllib POST 请求 ===")
    total_time = 0
    try:
        # 对每个测试对象进行测试
        for obj_name in TEST_OBJECTS:
            print(f"\n测试对象: {obj_name}")
            # 构建请求数据
            data = json.dumps({"name": {"v": obj_name}})
            post_data = f"json={data}".encode('utf-8')
            # 创建请求对象并添加请求头
            req = urllib.request.Request(NED_API_URL, method='POST')
            req.add_header("Content-Type", "application/x-www-form-urlencoded")
            req.add_header("Content-Length", str(len(post_data)))
            # 记录开始时间
            start_time = time.time()
            # 发送请求
            with urllib.request.urlopen(req, data=post_data, timeout=10) as response:
                # 读取响应内容
                response_data = response.read().decode('utf-8')
                # 计算响应时间
                response_time = time.time() - start_time
                total_time += response_time
                # 打印响应结果
                print(f"状态码: {response.getcode()}")
                print(f"响应时间: {response_time:.4f} 秒")
                print(f"响应内容: {json.loads(response_data)}")
        # 计算平均响应时间
        avg_time = total_time / len(TEST_OBJECTS)
        print(f"\n平均响应时间: {avg_time:.4f} 秒")
        return True, avg_time
    except Exception as e:
        print(f"错误: {e}")
        return False, 0

def test_httpx_post():
    """使用httpx库发送POST请求"""
    print("\n=== 测试 httpx POST 请求 ===")
    total_time = 0
    try:
        # 对每个测试对象进行测试
        for obj_name in TEST_OBJECTS:
            print(f"\n测试对象: {obj_name}")
            # 构建请求数据
            data = {
                "json": json.dumps({"name": {"v": obj_name}})
            }
            # 记录开始时间
            start_time = time.time()
            # 发送POST请求
            with httpx.Client() as client:
                response = client.post(NED_API_URL, data=data, timeout=10.0)
            # 计算响应时间
            response_time = time.time() - start_time
            total_time += response_time
            # 打印响应结果
            print(f"状态码: {response.status_code}")
            print(f"响应时间: {response_time:.4f} 秒")
            print(f"响应内容: {response.json()}")
        # 计算平均响应时间
        avg_time = total_time / len(TEST_OBJECTS)
        print(f"\n平均响应时间: {avg_time:.4f} 秒")
        return True, avg_time
    except Exception as e:
        print(f"错误: {e}")
        return False, 0

def main():
    """主测试函数"""
    print("开始测试 NED ObjectLookup API 调用...")
    print(f"API URL: {NED_API_URL}")
    print(f"测试对象: {', '.join(TEST_OBJECTS)}")
    print()
    
    # 运行所有测试
    results = {}
    response_times = {}
    
    # 测试 requests POST
    success, avg_time = test_requests_post()
    results["requests POST"] = success
    if success:
        response_times["requests POST"] = avg_time
    
    # 测试 urllib POST
    success, avg_time = test_urllib_post()
    results["urllib POST"] = success
    if success:
        response_times["urllib POST"] = avg_time
    
    # 测试 httpx POST
    success, avg_time = test_httpx_post()
    results["httpx POST"] = success
    if success:
        response_times["httpx POST"] = avg_time
    
    # 打印测试结果汇总
    print("\n=== 测试结果汇总 ===")
    for test_name, result in results.items():
        status = "✓ 成功" if result else "✗ 失败"
        if result:
            time_str = f" ({response_times[test_name]:.4f} 秒)"
        else:
            time_str = ""
        print(f"{test_name}: {status}{time_str}")
    
    # 统计成功的测试数量
    success_count = sum(results.values())
    total_count = len(results)
    print(f"\n总测试数: {total_count}, 成功数: {success_count}")
    
    # 找出响应时间最短的测试方法
    if response_times:
        fastest_method = min(response_times, key=response_times.get)
        fastest_time = response_times[fastest_method]
        print(f"\n响应时间最短的方法: {fastest_method}")
        print(f"最短响应时间: {fastest_time:.4f} 秒")
    else:
        print("\n没有成功的测试方法，无法比较响应时间")

if __name__ == "__main__":
    main()
