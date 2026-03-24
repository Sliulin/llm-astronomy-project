import subprocess
import time
import os

# 项目路径
PROJECT_ROOT = r"D:\Users\27036\Documents\trae_projects\llm"
FRONTEND_DIR = os.path.join(PROJECT_ROOT, "frontend")

# 启动后端服务器
def start_backend():
    print("启动后端服务器...")
    backend_process = subprocess.Popen(
        ["python", "server.py"],
        cwd=PROJECT_ROOT,
        shell=True,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE
    )
    return backend_process

# 启动前端服务器
def start_frontend():
    print("启动前端服务器...")
    frontend_process = subprocess.Popen(
        ["npm", "run", "dev"],
        cwd=FRONTEND_DIR,
        shell=True,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE
    )
    return frontend_process

if __name__ == "__main__":
    print("开始启动服务器...")
    
    # 启动后端服务器
    backend = start_backend()
    
    # 等待2秒让后端服务器启动
    print("等待后端服务器启动...")
    time.sleep(2)
    
    # 启动前端服务器
    frontend = start_frontend()
    
    print("服务器已启动，请打开浏览器访问前端页面")
    print("前端地址: http://localhost:3000")
    print("后端地址: http://localhost:8000")
    print("\n按 Ctrl+C 停止所有服务器")
    
    try:
        # 保持脚本运行
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        print("\n正在停止服务器...")
        # 停止前端服务器
        frontend.terminate()
        # 停止后端服务器
        backend.terminate()
        print("服务器已停止")
