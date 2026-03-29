import os
import json
from datetime import datetime
from tracemalloc import get_object_traceback
from typing import Dict, Any, List
from astroquery.ipac.ned import Ned
from astroquery.vizier import Vizier
import astropy.units as u
from astropy.coordinates import SkyCoord

# 引入基座的魔法装饰器
from src.agent.tool.base import tool

# ==========================================
# 1. 全局配置与客户端初始化
# ==========================================
ned = Ned()
vizier = Vizier()
vizier.ROW_LIMIT = 10 

# 自动定位到项目根目录下的 download 文件夹
SAVE_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), "../../../download"))

# ==========================================
# 2. 内部辅助函数 (大模型不可见)
# ==========================================
def _save_result(tool_name: str, result: Dict[str, Any]) -> str:
    """保存工具结果到文件"""
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
# 3. 对外暴露的业务工具 (全部装配 @tool)
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

@tool(description="直接执行标准 ADQL 语句，对 Gaia 星表进行高阶自定义查询")
def query_adql(query: str) -> Dict[str, Any]:
    """
    执行ADQL查询
    Args:
        query (str): 符合规范的 ADQL 查询语句
    """
    print(f"执行ADQL查询: {query}")
    try:
        from astroquery.gaia import Gaia
        job = Gaia.launch_job_async(query)
        result_table = job.get_results()
        
        important_fields = ['source_id', 'designation', 'ra', 'dec', 'parallax', 'phot_g_mean_mag']
        full_results = []
        for row in result_table:
            row_dict = {col: row[col] for col in result_table.colnames if col in important_fields}
            full_results.append(row_dict)
        
        results = full_results[:10] if len(full_results) > 10 else full_results
        filtered_columns = [col for col in result_table.colnames if col in important_fields]
        
        result = {"message": f"ADQL查询成功，找到 {len(result_table)} 条记录", "count": len(result_table), "results": results, "columns": filtered_columns}
        save_result = {"message": f"ADQL查询成功，找到 {len(result_table)} 条记录", "count": len(result_table), "results": full_results, "columns": filtered_columns}
        
        result["saved_path"] = _save_result("执行ADQL查询", save_result)
        return result
    except Exception as e:
        result = {"error": str(e), "status": "error"}
        result["saved_path"] = _save_result("执行ADQL查询", result)
        return result

if __name__ == "__main__":
    get_astronomy_object("M31")
   