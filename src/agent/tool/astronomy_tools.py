from typing import Dict, Any
from src.astronomy import AstronomyDataManager, knowledge_base


def register_astronomy_tools(registry):
    """
    注册天文相关工具

    Args:
        registry: 工具注册表实例
    """
    # 创建天文数据管理器实例
    astronomy_manager = AstronomyDataManager()

    # 注册天文对象查询工具
    registry.register_tool(
        name="get_astronomy_object",
        description="查询天文对象信息，包括位置、类型、红移等",
        func=lambda object_name: _get_astronomy_object(astronomy_manager, object_name),
        parameters={
            "object_name": {
                "type": "string",
                "description": "天文对象名称",
            }
        },
        returns="包含天文对象详细信息的字典",
    )

    # 注册区域查询工具（按名称）
    registry.register_tool(
        name="query_region_by_name",
        description="按名称查询指定区域内的天文对象",
        func=lambda object_name, radius: _query_region_by_name(astronomy_manager, object_name, radius),
        parameters={
            "object_name": {
                "type": "string",
                "description": "天文对象名称",
            },
            "radius": {
                "type": "number",
                "description": "搜索半径（度），默认为0.1度",
                "default": 0.1
            }
        },
        returns="包含区域查询结果的字典",
    )

    # 注册区域查询工具（按坐标）
    registry.register_tool(
        name="query_region_by_coordinates",
        description="按坐标查询指定区域内的天文对象",
        func=lambda ra, dec, radius: _query_region_by_coordinates(astronomy_manager, ra, dec, radius),
        parameters={
            "ra": {
                "type": "number",
                "description": "赤经（度）",
            },
            "dec": {
                "type": "number",
                "description": "赤纬（度）",
            },
            "radius": {
                "type": "number",
                "description": "搜索半径（度），默认为0.1度",
                "default": 0.1
            }
        },
        returns="包含区域查询结果的字典",
    )

    # 注册图像查询工具
    registry.register_tool(
        name="get_images",
        description="获取天文对象的图像",
        func=lambda object_name, max_images: _get_images(astronomy_manager, object_name, max_images),
        parameters={
            "object_name": {
                "type": "string",
                "description": "天文对象名称",
            },
            "max_images": {
                "type": "integer",
                "description": "最大图像数量，默认为5",
                "default": 5
            }
        },
        returns="包含图像信息的字典",
    )

    # 注册光谱查询工具
    registry.register_tool(
        name="get_spectra",
        description="获取天文对象的光谱",
        func=lambda object_name, max_spectra: _get_spectra(astronomy_manager, object_name, max_spectra),
        parameters={
            "object_name": {
                "type": "string",
                "description": "天文对象名称",
            },
            "max_spectra": {
                "type": "integer",
                "description": "最大光谱数量，默认为5",
                "default": 5
            }
        },
        returns="包含光谱信息的字典",
    )

    # 注册ADQL查询工具
    registry.register_tool(
        name="query_adql",
        description="执行ADQL查询获取天文数据，使用Gaia数据库",
        func=lambda query: _query_adql(astronomy_manager, query),
        parameters={
            "query": {
                "type": "string",
                "description": "ADQL查询语句",
            }
        },
        returns="包含ADQL查询结果的字典",
    )


def _get_astronomy_object(astronomy_manager, object_name: str) -> Dict[str, Any]:
    """
    查询天文对象信息

    Args:
        astronomy_manager: 天文数据管理器实例
        object_name: 天文对象名称

    Returns:
        天文对象信息
    """
    print(f"查询天文对象: {object_name}")
    return astronomy_manager.get_astronomy_object(object_name)


def _query_region_by_name(astronomy_manager, object_name: str, radius: float = 0.1) -> Dict[str, Any]:
    """
    按名称查询区域

    Args:
        astronomy_manager: 天文数据管理器实例
        object_name: 天文对象名称
        radius: 搜索半径（度）

    Returns:
        区域查询结果
    """
    print(f"查询区域: {object_name}, 半径: {radius}度")
    return astronomy_manager.query_region_by_name(object_name, radius)


def _query_region_by_coordinates(astronomy_manager, ra: float, dec: float, radius: float = 0.1) -> Dict[str, Any]:
    """
    按坐标查询区域

    Args:
        astronomy_manager: 天文数据管理器实例
        ra: 赤经（度）
        dec: 赤纬（度）
        radius: 搜索半径（度）

    Returns:
        区域查询结果
    """
    print(f"查询区域: RA={ra}, Dec={dec}, 半径: {radius}度")
    return astronomy_manager.query_region_by_coordinates(ra, dec, radius)


def _get_images(astronomy_manager, object_name: str, max_images: int = 5) -> Dict[str, Any]:
    """
    获取天体图像

    Args:
        astronomy_manager: 天文数据管理器实例
        object_name: 天文对象名称
        max_images: 最大图像数量

    Returns:
        图像信息
    """
    print(f"获取图像: {object_name}, 最大数量: {max_images}")
    return astronomy_manager.get_images(object_name, max_images)


def _get_spectra(astronomy_manager, object_name: str, max_spectra: int = 5) -> Dict[str, Any]:
    """
    获取天体光谱

    Args:
        astronomy_manager: 天文数据管理器实例
        object_name: 天文对象名称
        max_spectra: 最大光谱数量

    Returns:
        光谱信息
    """
    print(f"获取光谱: {object_name}, 最大数量: {max_spectra}")
    return astronomy_manager.get_spectra(object_name, max_spectra)


def _query_adql(astronomy_manager, query: str) -> Dict[str, Any]:
    """
    执行ADQL查询

    Args:
        astronomy_manager: 天文数据管理器实例
        query: ADQL查询语句

    Returns:
        ADQL查询结果
    """
    print(f"执行ADQL查询: {query}")
    return astronomy_manager.query_adql(query)
