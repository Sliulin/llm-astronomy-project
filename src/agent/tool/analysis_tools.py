from typing import Dict, Any, List
from src.agent.tool.base import tool

@tool(description="对一组天文数据（如通量、星等）进行平均值计算")
def calculate_average(numbers: List[float]) -> Dict[str, Any]:
    """
    计算平均值
    Args:
        numbers (list): 需要计算平均值的浮点数列表
    """
    if not numbers:
        return {"error": "列表不能为空", "status": "error"}
    
    avg = sum(numbers) / len(numbers)
    return {
        "status": "success",
        "result": avg,
        "message": f"计算完成，这组数据的平均值为 {avg:.4f}"
    }

@tool(description="计算赤经或赤纬数据的最大值与最小值差异 (极差)")
def calculate_range(numbers: List[float]) -> Dict[str, Any]:
    """
    计算数据极差
    Args:
        numbers (list): 浮点数列表
    """
    if not numbers:
        return {"error": "列表不能为空", "status": "error"}
        
    data_range = max(numbers) - min(numbers)
    return {
        "status": "success",
        "result": data_range,
        "message": f"数据的极差为 {data_range:.4f}"
    }