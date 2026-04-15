import json
import os
import re
from datetime import datetime
from typing import Any, Dict, List

import astropy.units as u
import numpy as np
from astropy.coordinates import SkyCoord
from astropy.time import Time
from astroquery.ipac.ned import Ned
from astroquery.jplhorizons import Horizons
from astroquery.vizier import Vizier
from astroquery.xmatch import XMatch

from src.agent.tool.base import tool

# ==========================================
# 全局配置与客户端初始化
# ==========================================
ned = Ned()
vizier = Vizier()
vizier.ROW_LIMIT = 10 

# 配置统一下载目录
SAVE_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), "../../../download"))

# ==========================================
# 内部辅助函数
# ==========================================
def _save_result(tool_name: str, result: Dict[str, Any]) -> str:
    """保存工具结果到本地 JSON 文件"""
    try:
        tool_dir = os.path.join(SAVE_DIR, tool_name)
        os.makedirs(tool_dir, exist_ok=True)
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"{timestamp}.json"
        file_path = os.path.join(tool_dir, filename)
        
        with open(file_path, 'w', encoding='utf-8') as f:
            json.dump(result, f, ensure_ascii=False, indent=2, default=str)
        
        print(f"结果已保存到: {file_path}")
        return file_path
    except Exception as e:
        print(f"保存结果失败: {str(e)}")
        return ""

def _get_astronomy_object_vizier(object_name: str) -> Dict[str, Any]:
    """使用 Vizier 查询天体对象的基础信息 (NED 失败时的降级方案)"""
    try:
        catalogs = ['I/259/glade2', 'V/139/sdss12', 'I/355/gaiadr3']
        for catalog in catalogs:
            try:
                result = vizier.query_object(object_name, catalog=catalog)
                if result and len(result) > 0:
                    table = list(result.values())[0]
                    if len(table) > 0:
                        row = table[0]
                        return {
                            "message": "成功找到对象",
                            "StatusCode": 100,
                            "ResultCode": 3,
                            "preferred_name": object_name,
                            "position": {
                                "RA": float(row['RAJ2000']) if 'RAJ2000' in row.colnames else float(row['RA']) if 'RA' in row.colnames else 0,
                                "Dec": float(row['DEJ2000']) if 'DEJ2000' in row.colnames else float(row['DEC']) if 'DEC' in row.colnames else 0
                            },
                            "object_type": row['Type'] if 'Type' in row.colnames else 'Unknown'
                        }
            except:
                continue
        return {"message": "未找到对象", "StatusCode": 100, "ResultCode": 2}
    except Exception as e:
        return {"error": str(e), "StatusCode": -1}

def _query_region_by_coordinates_vizier(ra: float, dec: float, radius: float = 0.01) -> Dict[str, Any]:
    """使用 Vizier 按坐标查询区域 (NED 失败时的降级方案)"""
    try:
        co = SkyCoord(ra=ra, dec=dec, unit=(u.deg, u.deg), frame='fk5')
        catalogs = ['I/259/glade2', 'V/139/sdss12', 'I/355/gaiadr3']
        all_results = []
        for catalog in catalogs:
            try:
                res = vizier.query_region(co, radius=radius * u.deg, catalog=catalog)
                if res and len(res) > 0:
                    table = list(res.values())[0]
                    for i, row in enumerate(table[:5]):
                        all_results.append({
                            "name": row['Name'] if 'Name' in row.colnames else f"Object {i+1}",
                            "ra": float(row['RAJ2000']) if 'RAJ2000' in row.colnames else float(row['RA']) if 'RA' in row.colnames else 0,
                            "dec": float(row['DEJ2000']) if 'DEJ2000' in row.colnames else float(row['DEC']) if 'DEC' in row.colnames else 0
                        })
            except:
                continue
        return {"message": f"找到 {len(all_results)} 个对象", "count": len(all_results), "results": all_results[:5]}
    except Exception as e:
        return {"error": str(e), "StatusCode": -1}

def _query_region_by_name_vizier(object_name: str, radius: float = 0.01) -> Dict[str, Any]:
    """使用 Vizier 按名称查询区域 (NED 失败时的降级方案)"""
    obj_info = _get_astronomy_object_vizier(object_name)
    if "error" in obj_info or obj_info.get("ResultCode") != 3:
        return obj_info
    position = obj_info.get("position")
    return _query_region_by_coordinates_vizier(position["RA"], position["Dec"], radius)

# ==========================================
# 天文数据查询工具
# ==========================================

@tool(description="查询天文对象的核心基础信息，包括坐标(RA/Dec)、类型和红移等")
def get_astronomy_object(object_name: str) -> Dict[str, Any]:
    """
    获取天文对象信息
    Args:
        object_name (str): 天文对象的标准名称（如 M31, NGC 224 等）
    """
    try:
        result_table = ned.query_object(object_name)
        if len(result_table) == 0:
            return _get_astronomy_object_vizier(object_name)
        
        row = result_table[0]
        info = {
            "message": "成功找到对象",
            "StatusCode": 100,
            "ResultCode": 3,
            "supplied_name": object_name,
            "preferred_name": row['Object Name'],
            "position": {"RA": row['RA'], "Dec": row['DEC']},
            "object_type": row['Type'] if 'Type' in row.colnames else 'Unknown',
            "redshift": {"Value": row['Redshift'] if 'Redshift' in row.colnames else 0}
        }
        return info
    except Exception as e:
        return _get_astronomy_object_vizier(object_name)

get_astronomy_object.title = "天文对象查询"
get_astronomy_object.icon = " 🔍"

@tool(description="锥形搜索：按名称查询以目标为中心，指定半径内的周边天文对象集合")
def query_region_by_name(object_name: str, radius: float = 0.01) -> Dict[str, Any]:
    """
    按名称查询区域
    Args:
        object_name (str): 中心天体名称
        radius (float): 搜索半径（度），默认0.01
    """
    try:
        result_table = ned.query_region(object_name, radius=radius * u.deg)
        full_results = [{"name": row['Object Name'], "ra": row['RA'], "dec": row['DEC']} for row in result_table]
        
        result = {"message": f"找到 {len(result_table)} 个对象", "count": len(result_table), "results": full_results[:5]}
        save_result = {"message": f"找到 {len(result_table)} 个对象", "count": len(result_table), "results": full_results}
        
        result["saved_path"] = _save_result("按名称查询区域", save_result)
        return result
    except Exception as e:
        result = _query_region_by_name_vizier(object_name, radius)
        result["saved_path"] = _save_result("按名称查询区域", result)
        return result

query_region_by_name.title = "按名称查询区域"
query_region_by_name.icon = "🔍"

@tool(description="按绝对赤道坐标(RA, Dec)查询区域内的天文对象集合")
def query_region_by_coordinates(ra: float, dec: float, radius: float = 0.01) -> Dict[str, Any]:
    """
    按坐标查询区域
    Args:
        ra (float): 赤经（度）
        dec (float): 赤纬（度）
        radius (float): 搜索半径（度）
    """
    try:
        co = SkyCoord(ra=ra, dec=dec, unit=(u.deg, u.deg), frame='fk5')
        result_table = ned.query_region(co, radius=radius * u.deg)
        full_results = [{"name": row['Object Name'], "ra": row['RA'], "dec": row['DEC']} for row in result_table]
        
        result = {"message": f"找到 {len(result_table)} 个对象", "count": len(result_table), "results": full_results[:5]}
        save_result = {"message": f"找到 {len(result_table)} 个对象", "count": len(result_table), "results": full_results}
        
        result["saved_path"] = _save_result("按坐标查询区域", save_result)
        return result
    except Exception as e:
        result = _query_region_by_coordinates_vizier(ra, dec, radius)
        result["saved_path"] = _save_result("按坐标查询区域", result)
        return result

query_region_by_coordinates.title = "按坐标查询区域"
query_region_by_coordinates.icon = "🔍"

@tool(description="获取指定天文对象的深空图像下载链接 (FITS/GZ格式)")
def get_images(object_name: str, max_images: int = 5) -> Dict[str, Any]:
    """
    获取天体图像
    Args:
        object_name (str): 天体名称
        max_images (int): 最大返回的图像链接数量
    """
    try:
        image_list = ned.get_image_list(object_name)
        full_image_list = image_list.copy()
        if max_images: image_list = image_list[:max_images]
        
        result = {"message": f"找到 {len(full_image_list)} 个图像", "count": len(full_image_list), "images": image_list}
        save_result = {"message": f"找到 {len(full_image_list)} 个图像", "count": len(full_image_list), "images": full_image_list}
        
        result["saved_path"] = _save_result("获取天体图像", save_result)
        return result
    except Exception as e:
        return {"error": str(e), "StatusCode": -1}

get_images.title = "获取天体图像"
get_images.icon = "🖼️"

@tool(description="获取指定天文对象的一维光谱数据链接")
def get_spectra(object_name: str, max_spectra: int = 5) -> Dict[str, Any]:
    """
    获取天体光谱
    Args:
        object_name (str): 天体名称
        max_spectra (int): 最大光谱数量
    """
    try:
        spectra_list = ned.get_image_list(object_name, item='spectra')
        full_spectra_list = spectra_list.copy()
        if max_spectra: spectra_list = spectra_list[:max_spectra]
        
        result = {"message": f"找到 {len(full_spectra_list)} 个光谱", "count": len(full_spectra_list), "spectra": spectra_list}
        save_result = {"message": f"找到 {len(full_spectra_list)} 个光谱", "count": len(full_spectra_list), "spectra": full_spectra_list}
        
        result["saved_path"] = _save_result("获取天体光谱", save_result)
        return result
    except Exception as e:
        return {"error": str(e), "StatusCode": -1}

get_spectra.title = "获取天体光谱"
get_spectra.icon = "🌈"

@tool(description="直接执行标准 ADQL 语句，对 Gaia 星表进行高阶自定义查询。注意：最多返回2000条数据以保证性能。")
def query_adql(query: str) -> Dict[str, Any]:
    """
    执行ADQL查询
    Args:
        query (str): 符合规范的 ADQL 查询语句
    """
    print(f"原始ADQL查询: {query}")
    
    # ==========================================
    # 安全拦截：强制注入或修改 TOP 限制
    # ==========================================
    try:
        query_upper = query.upper()
        if "TOP" not in query_upper:
            query = re.sub(r'(?i)^\s*SELECT\s+', 'SELECT TOP 2000 ', query)
        else:
            match = re.search(r'(?i)TOP\s+(\d+)', query)
            if match and int(match.group(1)) > 2000:
                query = re.sub(r'(?i)(TOP\s+)\d+', r'\g<1>2000', query)
                
        print(f"安全拦截后执行的ADQL: {query}")
    except Exception as e:
        print(f"ADQL正则拦截失败，将尝试执行原语句: {e}")

    try:
        from astroquery.gaia import Gaia
        job = Gaia.launch_job_async(query)
        result_table = job.get_results()
        
        # ==========================================
        # 提取并清理完整数据
        # ==========================================
        all_raw_results = []
        for row in result_table:
            row_dict = {}
            for col in result_table.colnames:
                val = row[col]
                if np.ma.is_masked(val):
                    row_dict[col] = None
                elif isinstance(val, (np.floating, float)):
                    row_dict[col] = round(float(val), 5) if not np.isnan(val) else None
                elif isinstance(val, (np.integer, int)):
                    row_dict[col] = int(val)
                elif isinstance(val, bytes):
                    row_dict[col] = val.decode('utf-8')
                else:
                    row_dict[col] = str(val)
            all_raw_results.append(row_dict)
        
        save_result = {
            "message": f"ADQL查询成功，找到 {len(result_table)} 条记录",
            "count": len(result_table),
            "columns": result_table.colnames,
            "results": all_raw_results
        }
        saved_path = _save_result("执行ADQL查询", save_result)
        
        # ==========================================
        # 提取精简数据供大模型使用
        # ==========================================
        important_fields = [
            'source_id', 'designation', 'ra', 'dec', 'parallax', 
            'phot_g_mean_mag', 'bp_rp', 'phot_bp_mean_mag', 'phot_rp_mean_mag'
        ]
        
        filtered_columns = [col for col in result_table.colnames if col in important_fields]
        
        preview_results = []
        for row in all_raw_results[:5]:
            preview_row = {col: row[col] for col in filtered_columns}
            preview_results.append(preview_row)
        
        result = {
            "message": f"ADQL查询成功，总共找到 {len(result_table)} 条记录。为节省上下文，此处仅展示前 {len(preview_results)} 条及部分核心列。",
            "count": len(result_table),
            "columns": filtered_columns,
            "results": preview_results,
            "saved_path": saved_path
        }
        return result
        
    except Exception as e:
        error_result = {"error": str(e), "status": "error"}
        error_result["saved_path"] = _save_result("执行ADQL查询_失败", error_result)
        return error_result

query_adql.title = "执行ADQL查询"
query_adql.icon = "🔍"

# ==========================================
# 太阳系天体星历表工具
# ==========================================
@tool(description="查询太阳系内天体（如行星、矮行星、彗星）的星历表，获取其当前的赤经、赤纬、地月距离和视星等。")
def get_ephemeris(target_name: str) -> Dict[str, Any]:
    """
    查询太阳系天体的实时星历表数据。
    Args:
        target_name (str): 太阳系天体名称，如 'Mars', '火星', 'Halley'。
    """
    
    # JPL Horizons 名称映射
    mapping = {
        "mars": "499", "火星": "499",
        "jupiter": "599", "木星": "599",
        "saturn": "699", "土星": "699",
        "venus": "299", "金星": "299",
        "mercury": "199", "水星": "199",
        "uranus": "799", "天王星": "799",
        "neptune": "899", "海王星": "899",
        "pluto": "999", "冥王星": "999",
        "moon": "301", "月球": "301",
        "sun": "10", "太阳": "10"
    }
    
    search_id = mapping.get(target_name.lower().strip(), target_name)
    
    try:
        now = Time.now()
        obj = Horizons(id=search_id, location='500', epochs=now.jd)
        eph = obj.ephemerides()
        
        if len(eph) == 0:
            return {"status": "error", "error": f"未查询到 {target_name} 的数据。"}
            
        result = {
            "target_name": str(eph['targetname'][0]),
            "datetime_utc": str(eph['datetime_str'][0]),
            "ra": round(float(eph['RA'][0]), 5),
            "dec": round(float(eph['DEC'][0]), 5),
            "distance_earth_au": round(float(eph['delta'][0]), 4),
            "distance_sun_au": round(float(eph['r'][0]), 4) if 'r' in eph.columns else None,
            "visual_magnitude": round(float(eph['V'][0]), 2) if 'V' in eph.columns else "N/A"
        }
        return {"status": "success", "data": result}
        
    except Exception as e:
        return {"status": "error", "error": f"星历查询失败，可能天体名称存在歧义或无法识别。错误详情: {str(e)}"}

get_ephemeris.title = "太阳系星历查询"
get_ephemeris.icon = "🪐"

# ==========================================
# 空间多波段：星表交叉证认 (Cross-Matching)
# ==========================================
@tool(description="在指定天区内对两大天文星表进行交叉匹配（Cross-Match），寻找同一天体在不同波段（如光学和红外）的数据。")
def cross_match_catalogs(ra: float, dec: float, radius_arcmin: float, base_catalog: str, target_catalog: str) -> Dict[str, Any]:
    """
    跨星表交叉证认工具。
    Args:
        ra (float): 中心点赤经 (度)
        dec (float): 中心点赤纬 (度)
        radius_arcmin (float): 搜索半径 (角分)，必须小于等于 5.0
        base_catalog (str): 基础星表，支持 'gaia' (光学), '2mass' (近红外), 'wise' (中红外)
        target_catalog (str): 目标匹配星表，支持 'gaia', '2mass', 'wise'
    """

    radius_arcmin = min(float(radius_arcmin), 5.0)
    
    cat_map = {
        "gaia": "I/355/gaiadr3",   
        "2mass": "II/246/out",     
        "wise": "II/328/allwise",  
        "sdss": "V/147/sdss12"     
    }
    
    cat1_vizier = cat_map.get(base_catalog.lower())
    cat2_vizier = cat_map.get(target_catalog.lower())
    
    if not cat1_vizier or not cat2_vizier:
        return {"status": "error", "error": f"暂不支持所选星表。目前支持: {list(cat_map.keys())}"}
        
    try:
        coord = SkyCoord(ra=ra, dec=dec, unit=(u.deg, u.deg), frame='icrs')
        v = Vizier(columns=["**"], row_limit=5000) 
        tables = v.query_region(coord, radius=radius_arcmin * u.arcmin, catalog=cat1_vizier)
        
        if len(tables) == 0:
            return {"status": "error", "error": f"在基础星表 {base_catalog} 中该区域未发现天体。"}
            
        base_table = tables[0]
        
        ra_col, dec_col = 'ra', 'dec'
        for col in base_table.colnames:
            col_up = col.upper()
            if col_up in ['RA', 'RAJ2000', 'RA_ICRS']: ra_col = col
            if col_up in ['DEC', 'DEJ2000', 'DE_ICRS']: dec_col = col
            
        xmatched_table = XMatch.query(
            cat1=base_table, 
            cat2=f"vizier:{cat2_vizier}", 
            max_distance=3 * u.arcsec,
            colRA1=ra_col,      
            colDec1=dec_col     
        )
        
        if len(xmatched_table) == 0:
            return {
                "status": "success", 
                "message": f"找到了 {len(base_table)} 个 {base_catalog} 目标，但在 3 角秒误差内没有找到 {target_catalog} 的匹配数据。"
            }
            
        full_results = []
        for row in xmatched_table:
            row_dict = {}
            for col in xmatched_table.colnames:
                val = row[col]
                if np.ma.is_masked(val):
                    row_dict[col] = None
                elif isinstance(val, (np.floating, float)):
                    row_dict[col] = round(float(val), 4) if not np.isnan(val) else None
                elif isinstance(val, (np.integer, int)):
                    row_dict[col] = int(val)
                elif isinstance(val, bytes):
                    row_dict[col] = val.decode('utf-8')
                else:
                    row_dict[col] = str(val)
            full_results.append(row_dict)
            
        save_data = {
            "status": "success", 
            "message": f"成功完成交叉证认！在 {radius_arcmin} 角分内，找到 {len(full_results)} 个匹配天体。",
            "matched_count": len(full_results),
            "data": full_results
        }
        
        saved_path = _save_result("交叉匹配", save_data)
        
        preview_results = []
        for row in full_results[:5]:
            preview_row = {k: row[k] for k in list(row.keys())[:5]}
            preview_results.append(preview_row)

        return {
            "status": "success", 
            "message": (
                f"成功完成交叉证认！在 {radius_arcmin} 角分内，共找到 {len(full_results)} 个匹配天体。"
            ),
            "matched_count": len(full_results),
            "data": preview_results, 
            "saved_path": saved_path
        }

    except Exception as e:
        error_result = {"status": "error", "error": f"交叉证认失败: {str(e)}"}
        error_result["saved_path"] = _save_result("交叉匹配", error_result)
        return error_result

cross_match_catalogs.title = "跨星表交叉证认工具"
cross_match_catalogs.icon = "🔍"

if __name__ == "__main__":
    get_astronomy_object("M31")