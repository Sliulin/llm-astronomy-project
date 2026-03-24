from typing import Dict, Any
from src.astronomy import AstronomyDataManager
import math


def register_analysis_tools(registry):
    """
    注册数据分析工具

    Args:
        registry: 工具注册表实例
    """
    # 创建天文数据管理器实例
    astronomy_manager = AstronomyDataManager()

    # 注册天文对象统计分析工具
    registry.register_tool(
        name="analyze_objects",
        description="分析多个天文对象的统计信息，包括类型分布、红移分布等",
        func=lambda object_names: _analyze_objects(astronomy_manager, object_names),
        parameters={
            "object_names": {
                "type": "array",
                "description": "天文对象名称列表，如 ['M 31', 'NGC 4565', 'ARP 319']",
            }
        },
        returns="包含统计分析结果的字典",
    )

    # 注册多对象比较工具
    registry.register_tool(
        name="compare_objects",
        description="比较多个天文对象的属性",
        func=lambda object_names: _compare_objects(astronomy_manager, object_names),
        parameters={
            "object_names": {
                "type": "array",
                "description": "天文对象名称列表，如 ['M 31', 'NGC 4565']",
            }
        },
        returns="包含比较结果的字典",
    )

    # 注册距离计算工具
    registry.register_tool(
        name="calculate_distance",
        description="计算两个天文对象之间的角距离",
        func=lambda object_name1, object_name2: _calculate_distance(astronomy_manager, object_name1, object_name2),
        parameters={
            "object_name1": {
                "type": "string",
                "description": "第一个天文对象名称",
            },
            "object_name2": {
                "type": "string",
                "description": "第二个天文对象名称",
            }
        },
        returns="包含距离信息的字典",
    )

    # 注册红移分析工具
    registry.register_tool(
        name="analyze_redshift",
        description="分析天文对象的红移与距离关系",
        func=lambda object_names: _analyze_redshift(astronomy_manager, object_names),
        parameters={
            "object_names": {
                "type": "array",
                "description": "天文对象名称列表，如 ['M 31', 'NGC 4565', 'ARP 319']",
            }
        },
        returns="包含红移分析结果的字典",
    )

    # 注册数据统计工具
    registry.register_tool(
        name="analyze_data",
        description="对天文数据进行统计分析，计算基本统计量和分布",
        func=lambda data, methods=None: _analyze_data(data, methods),
        parameters={
            "data": {
                "type": "array",
                "description": "要分析的数据数组，如 [1.2, 3.4, 5.6, 7.8] 或天文对象名称列表",
            },
            "methods": {
                "type": "array",
                "description": "统计方法列表，如 ['mean', 'median', 'std', 'histogram']",
                "default": ["mean", "median", "std", "histogram"]
            }
        },
        returns="包含统计分析结果的字典",
    )


def _analyze_objects(astronomy_manager, object_names: list) -> Dict[str, Any]:
    """
    分析多个天文对象的统计信息

    Args:
        astronomy_manager: 天文数据管理器实例
        object_names: 天文对象名称列表

    Returns:
        包含统计分析结果的字典
    """
    results = []
    type_counts = {}
    redshift_values = []

    # 获取每个对象的信息
    for name in object_names:
        info = astronomy_manager.get_astronomy_object(name)
        results.append(info)

        # 统计对象类型
        if info.get("ResultCode") == 3:
            obj_type = info.get("object_type_full", info.get("object_type"))
            if obj_type:
                type_counts[obj_type] = type_counts.get(obj_type, 0) + 1

            # 收集红移值
            if "redshift_value" in info:
                redshift_values.append({
                    "name": name,
                    "redshift": info["redshift_value"]
                })

    # 计算统计信息
    total_objects = len(object_names)
    successful_objects = sum(1 for info in results if info.get("ResultCode") == 3)
    error_objects = total_objects - successful_objects

    # 生成分析结果
    analysis = {
        "total_objects": total_objects,
        "successful_objects": successful_objects,
        "error_objects": error_objects,
        "type_distribution": type_counts,
        "redshift_analysis": redshift_values,
        "objects_info": results
    }

    return analysis


def _compare_objects(astronomy_manager, object_names: list) -> Dict[str, Any]:
    """
    比较多个天文对象的属性

    Args:
        astronomy_manager: 天文数据管理器实例
        object_names: 天文对象名称列表

    Returns:
        包含比较结果的字典
    """
    objects_info = []

    # 获取每个对象的信息
    for name in object_names:
        info = astronomy_manager.get_astronomy_object(name)
        objects_info.append(info)

    # 提取可比较的属性
    comparison = {
        "objects": [],
        "comparison_points": []
    }

    # 构建比较数据
    for info in objects_info:
        if info.get("ResultCode") == 3:
            obj_data = {
                "name": info.get("preferred_name", info.get("supplied_name")),
                "type": info.get("object_type_full", info.get("object_type")),
                "position": info.get("position_str"),
                "redshift": info.get("redshift_value")
            }
            comparison["objects"].append(obj_data)

    # 生成比较点
    if len(comparison["objects"]) > 1:
        # 比较红移
        redshifts = [obj.get("redshift") for obj in comparison["objects"] if obj.get("redshift") is not None]
        if redshifts:
            comparison["comparison_points"].append({
                "type": "redshift",
                "highest": max(redshifts) if redshifts else None,
                "lowest": min(redshifts) if redshifts else None,
                "average": sum(redshifts) / len(redshifts) if redshifts else None
            })

    return comparison


def _calculate_distance(astronomy_manager, object_name1: str, object_name2: str) -> Dict[str, Any]:
    """
    计算两个天文对象之间的角距离

    Args:
        astronomy_manager: 天文数据管理器实例
        object_name1: 第一个天文对象名称
        object_name2: 第二个天文对象名称

    Returns:
        包含距离信息的字典
    """
    # 获取两个对象的信息
    info1 = astronomy_manager.get_astronomy_object(object_name1)
    info2 = astronomy_manager.get_astronomy_object(object_name2)

    # 检查是否成功获取信息
    if info1.get("ResultCode") != 3 or info2.get("ResultCode") != 3:
        return {
            "error": "无法获取两个对象的位置信息",
            "object1_status": info1.get("ResultCode"),
            "object2_status": info2.get("ResultCode")
        }

    # 获取位置信息
    pos1 = info1.get("position")
    pos2 = info2.get("position")

    if not pos1 or not pos2:
        return {
            "error": "无法获取位置信息"
        }

    # 提取坐标
    ra1, dec1 = pos1.get("RA"), pos1.get("Dec")
    ra2, dec2 = pos2.get("RA"), pos2.get("Dec")

    if ra1 is None or dec1 is None or ra2 is None or dec2 is None:
        return {
            "error": "位置信息不完整"
        }

    # 计算角距离（使用简化的公式，单位为度）
    # 将角度转换为弧度
    ra1_rad = math.radians(ra1)
    dec1_rad = math.radians(dec1)
    ra2_rad = math.radians(ra2)
    dec2_rad = math.radians(dec2)

    # 使用球面距离公式（Haversine公式）
    delta_ra = ra2_rad - ra1_rad
    delta_dec = dec2_rad - dec1_rad

    a = math.sin(delta_dec/2)**2 + math.cos(dec1_rad) * math.cos(dec2_rad) * math.sin(delta_ra/2)**2
    c = 2 * math.atan2(math.sqrt(a), math.sqrt(1-a))

    # 转换回度
    distance_deg = math.degrees(c)
    # 转换为弧分
    distance_arcmin = distance_deg * 60
    # 转换为弧秒
    distance_arcsec = distance_arcmin * 60

    return {
        "object1": info1.get("preferred_name", object_name1),
        "object2": info2.get("preferred_name", object_name2),
        "distance_degrees": round(distance_deg, 6),
        "distance_arcminutes": round(distance_arcmin, 4),
        "distance_arcseconds": round(distance_arcsec, 2),
        "position1": info1.get("position_str"),
        "position2": info2.get("position_str")
    }


def _analyze_redshift(astronomy_manager, object_names: list) -> Dict[str, Any]:
    """
    分析天文对象的红移与距离关系

    Args:
        astronomy_manager: 天文数据管理器实例
        object_names: 天文对象名称列表

    Returns:
        包含红移分析结果的字典
    """
    objects_with_redshift = []

    # 获取每个对象的信息
    for name in object_names:
        info = astronomy_manager.get_astronomy_object(name)
        if info.get("ResultCode") == 3 and "redshift_value" in info:
            obj_data = {
                "name": info.get("preferred_name", info.get("supplied_name")),
                "redshift": info["redshift_value"],
                "type": info.get("object_type_full", info.get("object_type"))
            }
            # 估算距离（使用哈勃定律，简化计算）
            # 哈勃常数 H0 = 70 km/s/Mpc
            # 距离 = 红移 * 光速 / 哈勃常数
            c = 3e5  # 光速，单位 km/s
            H0 = 70  # 哈勃常数，单位 km/s/Mpc
            estimated_distance = (obj_data["redshift"] * c) / H0
            obj_data["estimated_distance_mpc"] = estimated_distance
            objects_with_redshift.append(obj_data)

    # 分析结果
    if objects_with_redshift:
        redshifts = [obj["redshift"] for obj in objects_with_redshift]
        distances = [obj["estimated_distance_mpc"] for obj in objects_with_redshift]

        analysis = {
            "objects_analyzed": len(objects_with_redshift),
            "total_objects": len(object_names),
            "objects_with_redshift": objects_with_redshift,
            "redshift_stats": {
                "min": min(redshifts),
                "max": max(redshifts),
                "average": sum(redshifts) / len(redshifts)
            },
            "distance_stats": {
                "min": min(distances),
                "max": max(distances),
                "average": sum(distances) / len(distances)
            }
        }
    else:
        analysis = {
            "objects_analyzed": 0,
            "total_objects": len(object_names),
            "error": "没有找到带有红移信息的对象"
        }

    return analysis


def _analyze_data(data: list, methods: list = None) -> Dict[str, Any]:
    """
    对天文数据进行统计分析

    Args:
        data: 要分析的数据数组
        methods: 统计方法列表

    Returns:
        包含统计分析结果的字典
    """
    print(f"执行数据统计分析")
    print(f"数据: {data}")
    print(f"方法: {methods}")
    
    if methods is None:
        methods = ["mean", "median", "std", "histogram"]
    
    try:
        # 检查数据是否为数值数组
        numeric_data = []
        is_object_names = False
        
        # 检查是否为天文对象名称列表
        if all(isinstance(item, str) for item in data):
            is_object_names = True
            # 导入天文数据管理器
            from src.astronomy import AstronomyDataManager
            astronomy_manager = AstronomyDataManager()
            
            # 获取每个对象的红移值
            for name in data:
                info = astronomy_manager.get_astronomy_object(name)
                if info.get("ResultCode") == 3 and "redshift_value" in info:
                    numeric_data.append(info["redshift_value"])
        else:
            # 尝试转换为数值
            for item in data:
                try:
                    numeric_data.append(float(item))
                except (ValueError, TypeError):
                    pass
        
        if not numeric_data:
            return {
                "error": "没有有效的数值数据可分析",
                "status": "error"
            }
        
        # 计算统计量
        analysis = {
            "data_count": len(numeric_data),
            "methods": methods,
            "results": {}
        }
        
        # 计算平均值
        if "mean" in methods:
            mean_value = sum(numeric_data) / len(numeric_data)
            analysis["results"]["mean"] = mean_value
        
        # 计算中位数
        if "median" in methods:
            sorted_data = sorted(numeric_data)
            n = len(sorted_data)
            if n % 2 == 0:
                median_value = (sorted_data[n//2 - 1] + sorted_data[n//2]) / 2
            else:
                median_value = sorted_data[n//2]
            analysis["results"]["median"] = median_value
        
        # 计算标准差
        if "std" in methods:
            mean_value = sum(numeric_data) / len(numeric_data)
            variance = sum((x - mean_value) ** 2 for x in numeric_data) / len(numeric_data)
            std_value = variance ** 0.5
            analysis["results"]["std"] = std_value
        
        # 计算最大值和最小值
        if "min" in methods or "max" in methods:
            min_value = min(numeric_data)
            max_value = max(numeric_data)
            if "min" in methods:
                analysis["results"]["min"] = min_value
            if "max" in methods:
                analysis["results"]["max"] = max_value
        
        # 计算分布（直方图）
        if "histogram" in methods:
            import numpy as np
            hist, bins = np.histogram(numeric_data, bins=10)
            histogram_data = {
                "bins": bins.tolist(),
                "counts": hist.tolist()
            }
            analysis["results"]["histogram"] = histogram_data
        
        return analysis
    except Exception as e:
        return {
            "error": str(e),
            "status": "error"
        }
