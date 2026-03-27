from typing import Dict, Optional, Any, List
import os
import json
from datetime import datetime
from astroquery.ipac.ned import Ned
from astroquery.vizier import Vizier
import astropy.units as u
from astropy.coordinates import SkyCoord

class AstronomyDataManager:
    """天文数据管理系统（使用astroquery）"""
    
    def __init__(self):
        self.ned = Ned()
        self.vizier = Vizier()
        # 配置Vizier返回更多字段
        self.vizier.ROW_LIMIT = 10  # 不限制返回行数
        self.object_type_mapping = {
            "G": "Galaxy",
            "GGroup": "Galaxy Group",
            "GClstr": "Galaxy Cluster",
            "Star": "Star",
            "QSO": "Quasar",
            "AGN": "Active Galactic Nucleus",
            "PN": "Planetary Nebula",
            "HII": "HII Region",
            "SNR": "Supernova Remnant",
            "GlobClust": "Globular Cluster",
            "OpenClust": "Open Cluster"
        }
        # 保存目录
        self.save_dir = "d:\\Users\\27036\\Documents\\trae_projects\\llm_project_1\\download"
    
    def get_astronomy_object(self, object_name: str) -> Dict[str, Any]:
        """
        获取天文对象信息
        
        Args:
            object_name (str): 天文对象名称
            
        Returns:
            dict: 处理后的天文对象信息
        """
        # 首先尝试使用NED数据库
        try:
            # 使用astroquery查询对象
            result_table = self.ned.query_object(object_name)
            
            if len(result_table) == 0:
                # NED未找到，尝试使用Vizier
                return self._get_astronomy_object_vizier(object_name)
            
            # 处理第一个结果
            row = result_table[0]
            
            # 构建详细信息
            info = {
                "message": "成功找到对象",
                "StatusCode": 100,
                "ResultCode": 3,
                "supplied_name": object_name,
                "preferred_name": row['Object Name'],
                "position": {
                    "RA": row['RA'],
                    "Dec": row['DEC']
                },
                "object_type": row['Type'] if 'Type' in row.colnames else 'Unknown',
                "redshift": {
                    "Value": row['Redshift'] if 'Redshift' in row.colnames else 0,
                    "RefCode": row['References'] if 'References' in row.colnames else '',
                    "QualityFlag": row['Redshift Flag'] if 'Redshift Flag' in row.colnames else ''
                }
            }
            
            # 标准化对象类型
            object_type = info.get("object_type")
            if object_type:
                info["object_type_full"] = self.object_type_mapping.get(object_type, object_type)
            
            # 标准化位置信息
            position = info.get("position")
            if position:
                info["position_str"] = self._format_position(position)
            
            # 标准化红移信息
            redshift = info.get("redshift")
            if redshift and "Value" in redshift:
                info["redshift_value"] = redshift["Value"]
            
            return info
            
        except Exception as e:
            # NED出错，尝试使用Vizier
            print(f"NED查询失败: {str(e)}")
            return self._get_astronomy_object_vizier(object_name)
    
    def _get_astronomy_object_vizier(self, object_name: str) -> Dict[str, Any]:
        """
        使用Vizier获取天文对象信息
        
        Args:
            object_name (str): 天文对象名称
            
        Returns:
            dict: 处理后的天文对象信息
        """
        try:
            # 使用Vizier查询对象
            # 尝试多个目录
            catalogs = ['I/259/glade2', 'V/139/sdss12', 'I/355/gaiadr3']
            
            for catalog in catalogs:
                try:
                    result = self.vizier.query_object(object_name, catalog=catalog)
                    if result and len(result) > 0:
                        # 获取第一个目录的结果
                        table = list(result.values())[0]
                        if len(table) > 0:
                            row = table[0]
                            
                            # 构建详细信息
                            info = {
                                "message": "成功找到对象",
                                "StatusCode": 100,
                                "ResultCode": 3,
                                "supplied_name": object_name,
                                "preferred_name": object_name,
                                "position": {
                                    "RA": float(row['RAJ2000']) if 'RAJ2000' in row.colnames else float(row['RA']) if 'RA' in row.colnames else 0,
                                    "Dec": float(row['DEJ2000']) if 'DEJ2000' in row.colnames else float(row['DEC']) if 'DEC' in row.colnames else 0
                                },
                                "object_type": row['Type'] if 'Type' in row.colnames else 'Unknown',
                                "redshift": {
                                    "Value": float(row['z']) if 'z' in row.colnames else float(row['Redshift']) if 'Redshift' in row.colnames else 0,
                                    "RefCode": "",
                                    "QualityFlag": ""
                                }
                            }
                            
                            # 标准化对象类型
                            object_type = info.get("object_type")
                            if object_type:
                                info["object_type_full"] = self.object_type_mapping.get(object_type, object_type)
                            
                            # 标准化位置信息
                            position = info.get("position")
                            if position:
                                info["position_str"] = self._format_position(position)
                            
                            # 标准化红移信息
                            redshift = info.get("redshift")
                            if redshift and "Value" in redshift:
                                info["redshift_value"] = redshift["Value"]
                            
                            # 添加Vizier特有的字段
                            if 'Plx' in row.colnames and row['Plx']:
                                info['parallax'] = float(row['Plx'])
                            if 'pmRA' in row.colnames and row['pmRA']:
                                info['proper_motion'] = {
                                    "ra": float(row['pmRA']),
                                    "dec": float(row['pmDE']) if 'pmDE' in row.colnames and row['pmDE'] else 0
                                }
                            
                            return info
                except Exception as e:
                    print(f"Vizier目录 {catalog} 查询失败: {str(e)}")
                    continue
            
            return {
                "message": "未找到对象",
                "StatusCode": 100,
                "ResultCode": 2
            }
            
        except Exception as e:
            return {
                "error": str(e),
                "StatusCode": -1
            }
    
    def _format_position(self, position: Dict[str, Any]) -> str:
        """
        格式化位置信息
        
        Args:
            position (dict): 位置信息字典
            
        Returns:
            str: 格式化后的位置字符串
        """
        ra = position.get("RA")
        dec = position.get("Dec")
        if ra is not None and dec is not None:
            return f"RA: {ra:.6f}, Dec: {dec:.6f}"
        return "未知位置"
    
    def _save_result(self, tool_name: str, result: Dict[str, Any]) -> str:
        """
        保存工具结果到文件
        
        Args:
            tool_name: 工具名称（中文）
            result: 工具执行结果
            
        Returns:
            str: 保存的文件路径
        """
        try:
            # 创建工具子目录（使用工具中文名）
            tool_dir = os.path.join(self.save_dir, tool_name)
            os.makedirs(tool_dir, exist_ok=True)
            
            # 生成文件名（日期时间）
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            filename = f"{timestamp}.json"
            file_path = os.path.join(tool_dir, filename)
            
            # 保存结果为JSON文件
            with open(file_path, 'w', encoding='utf-8') as f:
                json.dump(result, f, ensure_ascii=False, indent=2, default=str)
            
            print(f"结果已保存到: {file_path}")
            return file_path
        except Exception as e:
            print(f"保存结果失败: {str(e)}")
            return ""
    

    
    def query_region_by_name(self, object_name: str, radius: float = 0.01) -> Dict[str, Any]:
        """
        按名称查询区域
        
        Args:
            object_name (str): 天体名称
            radius (float): 搜索半径（度）
            
        Returns:
            dict: 区域查询结果
        """
        # 首先尝试使用NED数据库
        try:
            result_table = self.ned.query_region(
                object_name, 
                radius=radius * u.deg
            )
            
            # 保存完整结果
            full_results = []
            for i, row in enumerate(result_table):  # 保存所有结果
                full_results.append({
                    "name": row['Object Name'],
                    "ra": row['RA'],
                    "dec": row['DEC'],
                    "type": row['Type'] if 'Type' in row.colnames else 'Unknown',
                    "redshift": row['Redshift'] if 'Redshift' in row.colnames else 0
                })
            
            # 只返回前5个结果给用户
            results = full_results[:5] if len(full_results) > 5 else full_results
            
            # 构建结果字典（保存完整结果，返回前5个）
            result = {
                "message": f"找到 {len(result_table)} 个对象",
                "count": len(result_table),
                "results": results  # 返回前5个结果
            }
            
            # 构建保存用的结果字典（包含完整结果）
            save_result = {
                "message": f"找到 {len(result_table)} 个对象",
                "count": len(result_table),
                "results": full_results  # 保存完整结果
            }
            
            # 保存结果
            self._save_result("按名称查询区域", save_result)
            return result
            
        except Exception as e:
            # NED出错，尝试使用Vizier
            print(f"NED区域查询失败: {str(e)}")
            result = self._query_region_by_name_vizier(object_name, radius)
            # 保存结果
            self._save_result("按名称查询区域", result)
            return result
    
    def _query_region_by_name_vizier(self, object_name: str, radius: float = 0.01) -> Dict[str, Any]:
        """
        使用Vizier按名称查询区域
        
        Args:
            object_name (str): 天体名称
            radius (float): 搜索半径（度）
            
        Returns:
            dict: 区域查询结果
        """
        try:
            # 首先获取对象的坐标
            obj_info = self._get_astronomy_object_vizier(object_name)
            if "error" in obj_info or obj_info.get("ResultCode") != 3:
                return obj_info
            
            # 使用坐标进行区域查询
            position = obj_info.get("position")
            if not position:
                return {
                    "error": "无法获取对象坐标",
                    "StatusCode": -1
                }
            
            return self._query_region_by_coordinates_vizier(
                position["RA"], 
                position["Dec"], 
                radius
            )
            
        except Exception as e:
            return {
                "error": str(e),
                "StatusCode": -1
            }
    
    def query_region_by_coordinates(self, ra: float, dec: float, radius: float = 0.01) -> Dict[str, Any]:
        """
        按坐标查询区域
        
        Args:
            ra (float): 赤经（度）
            dec (float): 赤纬（度）
            radius (float): 搜索半径（度）
            
        Returns:
            dict: 区域查询结果
        """
        # 首先尝试使用NED数据库
        try:
            co = SkyCoord(ra=ra, dec=dec, unit=(u.deg, u.deg), frame='fk5')
            result_table = self.ned.query_region(
                co, 
                radius=radius * u.deg
            )
            
            # 保存完整结果
            full_results = []
            for i, row in enumerate(result_table):  # 保存所有结果
                full_results.append({
                    "name": row['Object Name'],
                    "ra": row['RA'],
                    "dec": row['DEC'],
                    "type": row['Type'] if 'Type' in row.colnames else 'Unknown',
                    "redshift": row['Redshift'] if 'Redshift' in row.colnames else 0
                })
            
            # 只返回前5个结果给用户
            results = full_results[:5] if len(full_results) > 5 else full_results
            
            # 构建结果字典（保存完整结果，返回前5个）
            result = {
                "message": f"找到 {len(result_table)} 个对象",
                "count": len(result_table),
                "results": results  # 返回前5个结果
            }
            
            # 构建保存用的结果字典（包含完整结果）
            save_result = {
                "message": f"找到 {len(result_table)} 个对象",
                "count": len(result_table),
                "results": full_results  # 保存完整结果
            }
            
            # 保存结果
            self._save_result("按坐标查询区域", save_result)
            return result
            
        except Exception as e:
            # NED出错，尝试使用Vizier
            print(f"NED坐标查询失败: {str(e)}")
            result = self._query_region_by_coordinates_vizier(ra, dec, radius)
            # 保存结果
            self._save_result("按坐标查询区域", result)
            return result
    
    def _query_region_by_coordinates_vizier(self, ra: float, dec: float, radius: float = 0.01) -> Dict[str, Any]:
        """
        使用Vizier按坐标查询区域
        
        Args:
            ra (float): 赤经（度）
            dec (float): 赤纬（度）
            radius (float): 搜索半径（度）
            
        Returns:
            dict: 区域查询结果
        """
        try:
            co = SkyCoord(ra=ra, dec=dec, unit=(u.deg, u.deg), frame='fk5')
            
            # 尝试多个目录
            catalogs = ['I/259/glade2', 'V/139/sdss12', 'I/355/gaiadr3']
            all_results = []
            
            for catalog in catalogs:
                try:
                    result = self.vizier.query_region(co, radius=radius * u.deg, catalog=catalog)
                    if result and len(result) > 0:
                        # 获取第一个目录的结果
                        table = list(result.values())[0]
                        for i, row in enumerate(table[:5]):  # 每个目录最多取5个结果
                            all_results.append({
                                "name": row['Name'] if 'Name' in row.colnames else f"Object {i+1}",
                                "ra": float(row['RAJ2000']) if 'RAJ2000' in row.colnames else float(row['RA']) if 'RA' in row.colnames else 0,
                                "dec": float(row['DEJ2000']) if 'DEJ2000' in row.colnames else float(row['DEC']) if 'DEC' in row.colnames else 0,
                                "type": row['Type'] if 'Type' in row.colnames else 'Unknown',
                                "redshift": float(row['z']) if 'z' in row.colnames else float(row['Redshift']) if 'Redshift' in row.colnames else 0
                            })
                except Exception as e:
                    print(f"Vizier目录 {catalog} 查询失败: {str(e)}")
                    continue
            
            # 去重并限制总数
            seen = set()
            unique_results = []
            for item in all_results:
                key = (item['ra'], item['dec'])
                if key not in seen:
                    seen.add(key)
                    unique_results.append(item)
                    if len(unique_results) >= 5:
                        break
            
            return {
                "message": f"找到 {len(unique_results)} 个对象",
                "count": len(unique_results),
                "results": unique_results
            }
            
        except Exception as e:
            return {
                "error": str(e),
                "StatusCode": -1
            }
    
    def get_images(self, object_name: str, max_images: int = 5) -> Dict[str, Any]:
        """
        获取天体图像
        
        Args:
            object_name (str): 天体名称
            max_images (int): 最大图像数量
            
        Returns:
            dict: 图像信息
        """
        try:
            # 获取图像列表
            image_list = self.ned.get_image_list(object_name)
            
            # 保存完整结果
            full_image_list = image_list.copy()
            
            # 只返回指定数量的结果给用户
            if max_images:
                image_list = image_list[:max_images]
            
            # 构建结果字典（保存完整结果，返回指定数量）
            result = {
                "message": f"找到 {len(full_image_list)} 个图像",
                "count": len(full_image_list),
                "images": image_list  # 返回指定数量的结果
            }
            
            # 构建保存用的结果字典（包含完整结果）
            save_result = {
                "message": f"找到 {len(full_image_list)} 个图像",
                "count": len(full_image_list),
                "images": full_image_list  # 保存完整结果
            }
            
            # 保存结果
            self._save_result("获取天体图像", save_result)
            return result
            
        except Exception as e:
            print(f"NED图像查询失败: {str(e)}")
            # 尝试使用对象的首选名称重新查询
            try:
                obj_info = self.get_astronomy_object(object_name)
                if obj_info.get("ResultCode") == 3:
                    preferred_name = obj_info.get("preferred_name")
                    if preferred_name and preferred_name != object_name:
                        print(f"尝试使用首选名称 {preferred_name} 查询图像")
                        image_list = self.ned.get_image_list(preferred_name)
                        if max_images:
                            image_list = image_list[:max_images]
                        result = {
                            "message": f"找到 {len(image_list)} 个图像",
                            "count": len(image_list),
                            "images": image_list
                        }
                        # 保存结果
                        self._save_result("获取天体图像", result)
                        return result
            except Exception as e2:
                print(f"重试失败: {str(e2)}")
            
            result = {
                "error": str(e),
                "StatusCode": -1
            }
            # 保存结果
            self._save_result("获取天体图像", result)
            return result
    
    def get_spectra(self, object_name: str, max_spectra: int = 5) -> Dict[str, Any]:
        """
        获取天体光谱
        
        Args:
            object_name (str): 天体名称
            max_spectra (int): 最大光谱数量
            
        Returns:
            dict: 光谱信息
        """
        try:
            # 获取光谱列表
            spectra_list = self.ned.get_image_list(object_name, item='spectra')
            
            # 保存完整结果
            full_spectra_list = spectra_list.copy()
            
            # 只返回指定数量的结果给用户
            if max_spectra:
                spectra_list = spectra_list[:max_spectra]
            
            # 构建结果字典（保存完整结果，返回指定数量）
            result = {
                "message": f"找到 {len(full_spectra_list)} 个光谱",
                "count": len(full_spectra_list),
                "spectra": spectra_list  # 返回指定数量的结果
            }
            
            # 构建保存用的结果字典（包含完整结果）
            save_result = {
                "message": f"找到 {len(full_spectra_list)} 个光谱",
                "count": len(full_spectra_list),
                "spectra": full_spectra_list  # 保存完整结果
            }
            
            # 保存结果
            self._save_result("获取天体光谱", save_result)
            return result
            
        except Exception as e:
            print(f"NED光谱查询失败: {str(e)}")
            # 尝试使用对象的首选名称重新查询
            try:
                obj_info = self.get_astronomy_object(object_name)
                if obj_info.get("ResultCode") == 3:
                    preferred_name = obj_info.get("preferred_name")
                    if preferred_name and preferred_name != object_name:
                        print(f"尝试使用首选名称 {preferred_name} 查询光谱")
                        spectra_list = self.ned.get_image_list(preferred_name, item='spectra')
                        if max_spectra:
                            spectra_list = spectra_list[:max_spectra]
                        result = {
                            "message": f"找到 {len(spectra_list)} 个光谱",
                            "count": len(spectra_list),
                            "spectra": spectra_list
                        }
                        # 保存结果
                        self._save_result("获取天体光谱", result)
                        return result
            except Exception as e2:
                print(f"重试失败: {str(e2)}")
            
            result = {
                "error": str(e),
                "StatusCode": -1
            }
            # 保存结果
            self._save_result("获取天体光谱", result)
            return result
    

    
    def clear_cache(self) -> Dict[str, Any]:
        """
        清除缓存
        
        Returns:
            dict: 操作结果
        """
        try:
            self.ned.clear_cache()
            result = {
                "message": "缓存已清除",
                "StatusCode": 100
            }
            return result
        except Exception as e:
            result = {
                "error": str(e),
                "StatusCode": -1
            }
            return result
    
    def query_adql(self, query: str) -> Dict[str, Any]:
        """
        执行ADQL查询

        Args:
            query: ADQL查询语句

        Returns:
            ADQL查询结果
        """
        print(f"执行ADQL查询: {query}")
        
        # 只使用Gaia查询
        try:
            # 导入Gaia查询模块
            from astroquery.gaia import Gaia
            
            # 执行查询
            job = Gaia.launch_job_async(query)
            result = job.get_results()
            
            # 转换结果为字典，筛选重要的键（保存完整结果）
            full_results = []
            # 定义需要保留的重要字段
            important_fields = ['source_id', 'designation', 'ra', 'dec', 'parallax', 'parallax_error', 
                              'pmra', 'pmra_error', 'pmdec', 'pmdec_error', 
                              'phot_g_mean_mag', 'phot_bp_mean_mag', 'phot_rp_mean_mag']
            
            # 保存完整结果
            for i, row in enumerate(result):  # 保存所有结果
                row_dict = {}
                for col in result.colnames:
                    # 只保留重要字段
                    if col in important_fields:
                        row_dict[col] = row[col]
                full_results.append(row_dict)
            
            # 只返回前10个结果给用户
            results = full_results[:10] if len(full_results) > 10 else full_results
            
            # 只返回重要字段的列名
            filtered_columns = [col for col in result.colnames if col in important_fields]
            
            # 构建结果字典（保存完整结果，返回前10个）
            result = {
                "message": f"ADQL查询成功，找到 {len(result)} 条记录",
                "count": len(result),
                "results": results,  # 返回前10个结果
                "columns": filtered_columns
            }
            
            # 构建保存用的结果字典（包含完整结果）
            save_result = {
                "message": f"ADQL查询成功，找到 {len(result)} 条记录",
                "count": len(result),
                "results": full_results,  # 保存完整结果
                "columns": filtered_columns
            }
            
            # 保存结果
            self._save_result("执行ADQL查询", save_result)
            return result
        except Exception as e:
            result = {
                "error": str(e),
                "status": "error"
            }
            # 保存结果
            self._save_result("执行ADQL查询", result)
            return result

if __name__ == "__main__":
    # 创建天文数据管理器实例
    manager = AstronomyDataManager()
    
    # 测试对象
    object_name = "M31"
    
    print("=== 测试工具功能和结果保存 ===")
    print("=" * 60)
    
    # 1. 测试按名称查询区域
    print("\n1. 测试按名称查询区域:")
    region_result = manager.query_region_by_name(object_name)
    print(f"结果: {region_result}")
    
    # 2. 测试按坐标查询区域
    print("\n2. 测试按坐标查询区域:")
    # 使用M31的大致坐标
    ra, dec = 10.68470833, 41.26875
    coord_result = manager.query_region_by_coordinates(ra, dec)
    print(f"结果: {coord_result}")
    
    # 3. 测试获取天体图像
    print("\n3. 测试获取天体图像:")
    images_result = manager.get_images(object_name, max_images=3)
    print(f"结果: {images_result}")
    
    # 4. 测试获取天体光谱
    print("\n4. 测试获取天体光谱:")
    spectra_result = manager.get_spectra(object_name, max_spectra=3)
    print(f"结果: {spectra_result}")
    
    print("\n5. 测试获取天文对象查询:")
    object_result = manager.get_astronomy_object(object_name)
    print(f"结果: {object_result}")

    # 5. 测试执行ADQL查询
    # print("\n5. 测试执行ADQL查询:")
    # adql_query = """
    # SELECT TOP 5
    #    source_id, ra, dec, parallax, phot_g_mean_mag
    # FROM gaiadr3.gaia_source
    # WHERE phot_g_mean_mag < 14
    # ORDER BY phot_g_mean_mag
    # """
    # adql_result = manager.query_adql(adql_query)
    # print(f"结果: {adql_result}")
    

    print("\n" + "=" * 60)
    print("测试完成！所有结果已保存到 download 目录")
