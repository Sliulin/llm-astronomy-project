import subprocess
import webbrowser
import time
import sys
import os

def start_services():
    print("🚀 正在启动天文智能体项目...\n")
    
    # 确保我们在项目根目录
    root_dir = os.path.dirname(os.path.abspath(__file__))
    frontend_dir = os.path.join(root_dir, "frontend")
    
    # 1. 启动后端服务
    print("▶️ 启动后端 (FastAPI)...")
    # 这里我们不用 uvicorn 命令，而是直接用当前环境的 python 运行 server.py
    # 这样能保证它使用的是你 .venv 里的 Python 解释器
    backend_process = subprocess.Popen(
        [sys.executable, "server.py"], 
        cwd=root_dir,
        # stdout=subprocess.PIPE, # 取消注释以隐藏后端普通日志
    )
    
    # 给后端一点启动时间
    time.sleep(2)
    
    # 2. 启动前端服务
    print("▶️ 启动前端 (Vite)...")
    # Windows 下使用 npm 需要带上 shell=True，macOS/Linux 不需要
    is_windows = sys.platform.startswith('win')
    npm_cmd = "npm.cmd" if is_windows else "npm"
    
    frontend_process = subprocess.Popen(
        [npm_cmd, "run", "dev"], 
        cwd=frontend_dir,
        # stdout=subprocess.PIPE, # 取消注释以隐藏前端普通日志
    )
    
    # 给前端打包和启动一点时间
    print("\n⏳ 等待服务就绪...")
    time.sleep(3)
    
    # 3. 自动打开浏览器
    target_url = "http://localhost:3000"
    print(f"🌐 正在浏览器中打开: {target_url}")
    webbrowser.open(target_url)
    
    print("\n✅ 所有服务已启动！")
    print("💡 提示: 按 Ctrl+C 可以同时关闭前后端服务。\n")
    
    try:
        # 保持主进程不死，并等待子进程
        backend_process.wait()
        frontend_process.wait()
    except KeyboardInterrupt:
        print("\n🛑 收到退出指令，正在关闭服务...")
        backend_process.terminate()
        frontend_process.terminate()
        print("👋 服务已安全关闭。")

if __name__ == "__main__":
    start_services()