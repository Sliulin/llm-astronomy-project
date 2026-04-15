# AstroAgent 智能天文数据引擎

AstroAgent 是一个集成了大语言模型（LLM）与专业天文工具的智能交互系统。通过自然语言对话，用户可以轻松完成复杂的星表查询、天体图像下载、多波段交叉证认以及时域周期分析。

## ✨ 核心特性

* **星表挖掘 (Data Miner)**：支持将自然语言转化为 ADQL 语句，对 Gaia 等大规模星表进行高阶查询。内置最大返回 2000 条数据的安全拦截机制以保证性能。
* **时域分析 (Time-Domain)**：针对不均匀采样数据，提供 Lomb-Scargle 周期搜索，并可自动绘制折叠光变曲线。
* **多波段交叉证认**：支持在光学 (Gaia)、近红外 (2MASS) 和中红外 (WISE) 星表之间进行以目标为中心、指定半径内的坐标交叉匹配。
* **太阳系星历查询**：对接 JPL Horizons 数据库，实时获取行星、彗星的赤经、赤纬、地月距离及视星等星历表数据。
* **FITS 图像与数据提取**：通过 NED 数据库获取深空图像，自动拦截本地下载路径并在前端生成带有 📥 图标的下载卡片。

## 🏗️ 系统架构

* **后端**：基于 Python 和 FastAPI 构建，负责多会话持久化管理 (`sessions.json`)、SSE 流式通信及天文数据文件的本地存储管理。
* **前端**：基于 Vue 3 + Vite，提供沉浸式对话界面，支持 Markdown/KaTeX 渲染、拖拽上传文件以及本地 JSON 数据的美化预览弹窗。
* **智能代理核心**：基于 `hunyuan-turbo` 大模型，通过自定义的 `@tool` 装饰器实现自然语言到本地 Python 函数的自动映射与调用。

## 🚀 快速启动

### 1. 环境准备
* Python >= 3.14
* Node.js (用于运行 Vite 前端服务)

### 2. 依赖安装
安装后端依赖（基于 `pyproject.toml`）：
```bash
pip install fastapi httpx langchain langchain-openai matplotlib pandas photutils python-dotenv requests astropy astroquery uvicorn
```
进入前端目录并安装依赖：
```bash
cd frontend
npm install
```
### 3. 环境变量配置
在 assets/openai.env 文件中配置大模型 API 密钥信息：

```bash
HUNYUAN_API_KEY=your_api_key_here
OPENAI_API_BASE=[https://api.hunyuan.cloud.tencent.com/v1](https://api.hunyuan.cloud.tencent.com/v1)
```
### 4. 一键运行
回到项目根目录，执行一键启动脚本：

```bash
python start-all.py
```
该脚本会自动拉起后端 FastAPI 服务与前端 Vite 开发服务器，并在浏览器中自动打开 http://localhost:3000 页面。

## 📁 核心目录结构
```Plaintext
.
├── assets/             # 存放环境变量配置 (openai.env)
├── download/           # 工具生成的 JSON 原始数据、图像与光谱文件的统一下载目录
├── frontend/           # Vue 3 前端工程代码
├── src/
│   └── agent/
│       ├── core.py               # 大模型代理核心循环与路径拦截器
│       ├── tool/
│       │   ├── astronomy_tools.py # 天文数据库检索与星表交叉工具
│       │   ├── analysis_tools.py  # 数据可视化与周期分析工具
│       │   └── base.py            # 工具注册表与装饰器基类
├── pyproject.toml      # 项目依赖声明文件
├── server.py           # FastAPI 后端主服务入口
└── start-all.py        # 前后端一键启动与浏览器唤醒脚本
```
