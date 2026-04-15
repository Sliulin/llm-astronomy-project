import json
import os
from datetime import datetime
from typing import Any, Dict
from urllib.parse import urlparse

import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
import requests

from src.agent.tool.base import tool

# 配置统一下载目录
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
    # 1. 从本地 JSON 文件加载完整数据
    # ==========================================
    if not file_path or not os.path.exists(file_path):
        return {"status": "error", "error": f"找不到指定的文件路径: {file_path}"}
        
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            file_content = json.load(f)
            # 兼容不同的数据保存结构
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
        # 获取 G 波段视星等
        g_mag = row.get('phot_g_mean_mag') or row.get('PHOT_G_MEAN_MAG')
        if g_mag is None:
            continue
        
        # 计算绝对星等
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
    # 3. 绘制图像
    # ==========================================
    plt.figure(figsize=(8, 10))
    # 动态调整点的大小，防止重叠
    point_size = max(1, 10 - len(colors) // 1000) 
    plt.scatter(colors, magnitudes, s=point_size, c=colors, cmap='RdYlBu_r', alpha=0.7)
    
    # 天文学惯例：Y轴视星等越小越亮，需翻转Y轴
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

@tool(description="读取本地 FITS 格式深空图像文件，自动提取并定位图像中的恒星/天体源。必须传入包含 .fits 或 .fits.gz 文件的绝对路径。返回图像中天体的像素坐标、亮度，并生成标注后的预览图。")
def extract_sources_from_fits(file_path: str) -> Dict[str, Any]:
    """
    对天文 FITS 图像进行自动源提取 (Source Extraction)。
    Args:
        file_path (str): 本地 FITS 文件的绝对路径。
    """
    if not file_path or not os.path.exists(file_path):
        return {"status": "error", "error": f"找不到指定的 FITS 文件: {file_path}"}

    try:
        from astropy.io import fits
        from astropy.stats import sigma_clipped_stats
        from matplotlib.colors import LogNorm
        from photutils.aperture import CircularAperture
        from photutils.detection import DAOStarFinder
    except ImportError:
        return {"status": "error", "error": "缺少必要的库，请先执行: pip install astropy photutils"}

    try:
        # ==========================================
        # 1. 智能读取 FITS 数据
        # ==========================================
        data = None
        with fits.open(file_path) as hdul:
            # 寻找二维图像数据层
            for hdu in hdul:
                if hdu.is_image and hdu.data is not None and len(hdu.data.shape) >= 2:
                    data = hdu.data
                    break
            
            if data is None:
                return {"status": "error", "error": "在 FITS 文件中未找到有效的二维图像数据。"}

        # 确保是 2D 数据
        if len(data.shape) > 2:
            data = data[0]

        data = data.astype(float)
        data[np.isnan(data)] = np.nanmedian(data)

        # ==========================================
        # 2. 背景估算与源提取
        # ==========================================
        mean, median, std = sigma_clipped_stats(data, sigma=3.0)

        # 初始化 DAOStarFinder
        daofind = DAOStarFinder(fwhm=3.0, threshold=5.*std)
        sources = daofind(data - median)

        if sources is None or len(sources) == 0:
            return {"status": "success", "message": "未在图像中检测到明显亮于背景的恒星源。", "count": 0}

        # ==========================================
        # 3. 提取高亮源信息
        # ==========================================
        sources.sort('flux')
        sources.reverse()
        
        top_sources = []
        for i, row in enumerate(sources[:10]):
            top_sources.append({
                "rank": i + 1,
                "x_pixel": round(row['xcentroid'], 2),
                "y_pixel": round(row['ycentroid'], 2),
                "relative_flux": round(row['flux'], 2)
            })

        # ==========================================
        # 4. 生成可视化预览图
        # ==========================================
        plt.figure(figsize=(10, 8))
        
        # 使用对数拉伸 (LogNorm) 显示图片
        plt.imshow(data, cmap='Greys_r', origin='lower', norm=LogNorm(vmin=median, vmax=median+10*std))
        
        # 在检测到的坐标上画红色圆圈
        positions = np.transpose((sources['xcentroid'], sources['ycentroid']))
        apertures = CircularAperture(positions, r=6.)
        apertures.plot(color='red', lw=1.5, alpha=0.6)

        plt.title(f"Source Extraction: Found {len(sources)} objects")
        plt.colorbar(label='Pixel Value (Flux)')

        # 保存图片
        tool_dir = os.path.join(SAVE_DIR, "图像源提取")
        os.makedirs(tool_dir, exist_ok=True)
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"Extracted_Sources_{timestamp}.png"
        saved_image_path = os.path.join(tool_dir, filename)
        
        plt.savefig(saved_image_path, dpi=150, bbox_inches='tight')
        plt.close()

        return {
            "status": "success",
            "message": f"成功分析 FITS 图像，总共提取了 {len(sources)} 个天体源。此处列出最亮的前 {len(top_sources)} 个的坐标信息。",
            "total_count": len(sources),
            "background_noise_std": round(std, 2),
            "top_10_brightest": top_sources,
            "saved_image_path": saved_image_path
        }

    except Exception as e:
        return {"status": "error", "error": f"FITS源提取分析失败: {str(e)}"}

extract_sources_from_fits.title = "FITS源提取分析"
extract_sources_from_fits.icon = "📊"

@tool(description="根据外网 URL 下载天文 FITS/GZ 图像文件到本地，并返回绝对路径。专门用于接收 get_images 和 get_spectra 提供的图像链接。")
def download_fits_file(url: str) -> Dict[str, Any]:
    """
    下载外网 FITS 数据到本地磁盘。
    Args:
        url (str): FITS 文件的完整下载链接 (必须以 http 或 https 开头)。
    """
    if not url.startswith(('http://', 'https://')):
        return {"status": "error", "error": "无效的 URL，必须是包含 http/https 的链接。"}

    try:
        # 1. 准备专属的下载目录
        tool_dir = os.path.join(SAVE_DIR, "文件下载")
        os.makedirs(tool_dir, exist_ok=True)

        # 2. 从 URL 中提取文件名并进行清理
        parsed_url = urlparse(url)
        raw_filename = os.path.basename(parsed_url.path)
        
        # 替换 Windows 严禁的特殊字符
        safe_filename = raw_filename.replace(":", "_").replace("?", "_").replace("&", "_")
        
        if not safe_filename.endswith(('.fits', '.fits.gz', '.gz')):
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            safe_filename = f"image_{timestamp}.fits.gz"

        file_path = os.path.join(tool_dir, safe_filename)

        # 3. 开始流式下载
        print(f"📥 开始下载 FITS 文件: {url}")
        response = requests.get(url, stream=True, timeout=60)
        response.raise_for_status()
        
        with open(file_path, 'wb') as f:
            for chunk in response.iter_content(chunk_size=8192):
                if chunk:
                    f.write(chunk)
                    
        print(f"✅ 下载完成，已保存至: {file_path}")

        # 4. 返回本地绝对路径
        return {
            "status": "success",
            "message": "文件已成功下载到本地。",
            "saved_path": file_path
        }

    except requests.exceptions.RequestException as e:
        return {"status": "error", "error": f"网络下载失败: {str(e)}"}
    except Exception as e:
        return {"status": "error", "error": f"保存文件失败: {str(e)}"}

download_fits_file.title = "FITS文件下载"
download_fits_file.icon = "📥"

@tool(description="读取包含时间和亮度数据的本地 CSV/TXT 文件，使用 Lomb-Scargle 算法搜索天体光变周期。必须传入文件的绝对路径。")
def analyze_lightcurve_period(file_path: str) -> Dict[str, Any]:
    """
    对时序数据进行 Lomb-Scargle 周期搜索。
    """
    if not file_path or not os.path.exists(file_path):
        return {"status": "error", "error": f"找不到指定的数据文件: {file_path}"}

    try:
        from astropy.timeseries import LombScargle
        
        # 1. 尝试读取数据
        try:
            df = pd.read_csv(file_path, comment='#')
            if len(df.columns) < 2:
                df = pd.read_csv(file_path, delim_whitespace=True, comment='#')
        except Exception:
            return {"status": "error", "error": "无法解析文件，请确保前两列分别是时间(Time)和亮度(Flux/Mag)数据。"}

        t = df.iloc[:, 0].values
        y = df.iloc[:, 1].values

        # 2. 计算 Lomb-Scargle 周期图
        print(f"正在分析 {len(t)} 个数据点的光变周期...")
        frequency, power = LombScargle(t, y).autopower(minimum_frequency=1/50.0, maximum_frequency=1/0.1)
        
        # 提取最佳主周期
        best_freq = frequency[np.argmax(power)]
        best_period = 1.0 / best_freq
        
        # 3. 绘制折叠光变曲线图
        phase = (t % best_period) / best_period
        
        plt.figure(figsize=(10, 6))
        plt.scatter(phase, y, s=15, color='#1f77b4', alpha=0.7, edgecolors='none', label='Phase 0-1')
        plt.scatter(phase + 1, y, s=15, color='#ff7f0e', alpha=0.7, edgecolors='none', label='Phase 1-2')
        
        plt.title(f"Phase-Folded Light Curve\nBest Period = {best_period:.4f} Days", fontsize=14, fontweight='bold')
        plt.xlabel("Phase (Cycles)", fontsize=12)
        plt.ylabel("Observation Value (Flux/Mag)", fontsize=12)
        
        # 智能判断：如果均值小于 30，大概率是星等，翻转 Y 轴
        if np.mean(y) < 30:
            plt.gca().invert_yaxis()
            plt.ylabel("Apparent Magnitude (mag)", fontsize=12)
            
        plt.grid(True, alpha=0.3, linestyle='--')
        plt.legend()
        
        # 4. 保存图片并返回给大模型
        tool_dir = os.path.join(SAVE_DIR, "周期分析")
        os.makedirs(tool_dir, exist_ok=True)
        filename = f"LS_Periodogram_{datetime.now().strftime('%Y%m%d_%H%M%S')}.png"
        saved_image_path = os.path.join(tool_dir, filename)
        
        plt.savefig(saved_image_path, dpi=150, bbox_inches='tight')
        plt.close()

        return {
            "status": "success",
            "message": f"周期搜索计算完成！在数据中发现了显著的周期性变化，最佳拟合周期为 {best_period:.4f} 天。",
            "best_period_days": round(best_period, 4),
            "data_points": len(t),
            "saved_image_path": saved_image_path
        }

    except ImportError:
        return {"status": "error", "error": "缺少 astropy 库，请执行: pip install astropy"}
    except Exception as e:
        return {"status": "error", "error": f"周期分析失败: {str(e)}"}

analyze_lightcurve_period.title = "周期分析"
analyze_lightcurve_period.icon = "📊"