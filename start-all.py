import subprocess
import webbrowser
import time
import sys
import os

def start_services():
    print("🚀 正在启动天文智能体项目...\n")
    
    root_dir = os.path.dirname(os.path.abspath(__file__))
    frontend_dir = os.path.join(root_dir, "frontend")
    
    print("▶️ 启动后端 (FastAPI)...")
    backend_process = subprocess.Popen(
        [sys.executable, "server.py"], 
        cwd=root_dir,
    )
    
    time.sleep(2)
    
    print("▶️ 启动前端 (Vite)...")
    is_windows = sys.platform.startswith('win')
    npm_cmd = "npm.cmd" if is_windows else "npm"
    
    frontend_process = subprocess.Popen(
        [npm_cmd, "run", "dev"], 
        cwd=frontend_dir,
    )
    
    print("\n⏳ 等待服务就绪...")
    time.sleep(3)
    
    target_url = "http://localhost:3000"
    print(f"🌐 正在浏览器中打开: {target_url}")
    webbrowser.open(target_url)
    
    print("\n✅ 所有服务已启动！")
    print("💡 提示: 按 Ctrl+C 可以同时关闭前后端服务。\n")
    
    try:
        backend_process.wait()
        frontend_process.wait()
    except KeyboardInterrupt:
        print("\n🛑 收到退出指令，正在关闭服务...")
        backend_process.terminate()
        frontend_process.terminate()
        print("👋 服务已安全关闭。")

if __name__ == "__main__":
    start_services()