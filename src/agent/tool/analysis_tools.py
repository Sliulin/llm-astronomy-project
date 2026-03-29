import os
import json
import numpy as np
from datetime import datetime
from typing import Dict, Any

import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt

# 引入项目自带的工具注册装饰器
from src.agent.tool.base import tool

# 配置统一下载目录（与 astronomy_tools.py 保持一致）
SAVE_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), "../../../download"))

@tool(description="根据本地数据文件绘制赫罗图 (HR Diagram)。必须传入包含星表数据的本地 JSON 文件绝对路径 (如 saved_path)。")
def plot_hr_diagram(file_path: str) -> Dict[str, Any]:
    """
    绘制恒星赫罗图 / 颜色-星等图。
    Args:
        file_path (str): 包含完整星表数据的本地 JSON 文件绝对路径。
    """
    data_to_plot = []

    # ==========================================
    # 1. 强制从本地 JSON 文件加载完整数据
    # ==========================================
    if not file_path or not os.path.exists(file_path):
        return {"status": "error", "error": f"找不到指定的文件路径: {file_path}"}
        
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            file_content = json.load(f)
            # 兼容不同的数据保存结构：支持从 'results' 或 'data' 字段读取，或者直接读取列表
            if isinstance(file_content, dict):
                data_to_plot = file_content.get("results", file_content.get("data", []))
            elif isinstance(file_content, list):
                data_to_plot = file_content
    except Exception as e:
        return {"status": "error", "error": f"读取本地文件失败: {str(e)}"}

    if not data_to_plot or len(data_to_plot) == 0:
        return {"status": "error", "error": "文件数据为空或格式不正确，无法绘制。"}

    # ==========================================
    # 2. 解析和清洗数据
    # ==========================================
    colors = []
    magnitudes = []
    has_parallax = False

    for row in data_to_plot:
        # 获取 G 波段视星等 (兼容大小写)
        g_mag = row.get('phot_g_mean_mag') or row.get('PHOT_G_MEAN_MAG')
        if g_mag is None:
            continue
        
        # 尝试计算绝对星等
        parallax = row.get('parallax') or row.get('PARALLAX')
        abs_mag = None
        if parallax and float(parallax) > 0:
            has_parallax = True
            abs_mag = float(g_mag) + 5 + 5 * np.log10(float(parallax) / 1000.0)

        # 获取颜色指数 (BP - RP)
        bp_rp = row.get('bp_rp') or row.get('BP_RP')
        if bp_rp is None:
            bp = row.get('phot_bp_mean_mag') or row.get('PHOT_BP_MEAN_MAG')
            rp = row.get('phot_rp_mean_mag') or row.get('PHOT_RP_MEAN_MAG')
            if bp is not None and rp is not None:
                bp_rp = float(bp) - float(rp)

        if bp_rp is not None:
            colors.append(float(bp_rp))
            magnitudes.append(float(abs_mag) if abs_mag is not None else float(g_mag))

    if not colors:
        return {"status": "error", "error": "数据中缺乏必要的测光字段（如 G星等 和 BP/RP 颜色）。"}

    # ==========================================
    # 3. 开始绘图
    # ==========================================
    plt.figure(figsize=(8, 10))
    # 动态调整点的大小，数据越多点越小，防止重叠成一团糊
    point_size = max(1, 10 - len(colors) // 1000) 
    plt.scatter(colors, magnitudes, s=point_size, c=colors, cmap='RdYlBu_r', alpha=0.7)
    
    # 核心：天文学惯例，Y轴视星等越小越亮，需翻转Y轴
    plt.gca().invert_yaxis()
    
    plt.xlabel('Color Index (BP - RP)')
    plt.ylabel('Absolute G Magnitude' if has_parallax else 'Apparent G Magnitude')
    plt.title(f'Color-Magnitude Diagram ({len(colors)} stars)')
    plt.grid(True, linestyle='--', alpha=0.3)

    # ==========================================
    # 4. 图像保存与路径返回
    # ==========================================
    tool_dir = os.path.join(SAVE_DIR, "绘制赫罗图")
    os.makedirs(tool_dir, exist_ok=True)
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    filename = f"HR_Diagram_{timestamp}.png"
    filepath = os.path.join(tool_dir, filename)
    
    plt.savefig(filepath, dpi=300, bbox_inches='tight')
    plt.close()

    return {
        "status": "success",
        "message": f"成功绘制了包含 {len(colors)} 颗恒星的赫罗图。",
        "saved_image_path": filepath 
    }
plot_hr_diagram.title = "绘制赫罗图"
plot_hr_diagram.icon = "📊"
