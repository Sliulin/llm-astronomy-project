#!/usr/bin/env python3
"""
测试astroquery库的基本功能
"""

import sys
import os
# 添加项目根目录到Python路径
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))


def test_query_object():
    """测试按名称查询对象"""
    print("=== 测试1：按名称查询对象 ===")
    
    try:
        from astroquery.ipac.ned import Ned
        
        # 查询M 31（仙女座星系）
        print("查询M 31...")
        result_table = Ned.query_object("M 31")
        
        print(f"查询成功！找到 {len(result_table)} 个结果")
        print(f"结果类型: {type(result_table)}")
        print(f"列名: {result_table.colnames}")
        
        if len(result_table) > 0:
            row = result_table[0]
            print(f"\n第一个结果:")
            print(f"  对象名称: {row['Object Name']}")
            print(f"  赤经(RA): {row['RA']}")
            print(f"  赤纬(DEC): {row['DEC']}")
            print(f"  红移: {row['Redshift']}")
            print(f"  红移标志: {row['Redshift Flag']}")
            print(f"  直径点数: {row['Diameter Points']}")
            print(f"  关联对象数: {row['Associations']}")
            
        print("✅ 测试通过\n")
        return True
        
    except Exception as e:
        print(f"❌ 测试失败: {e}\n")
        return False


def test_query_region_by_name():
    """测试按名称查询区域"""
    print("=== 测试2：按名称查询区域 ===")
    
    try:
        from astroquery.ipac.ned import Ned
        import astropy.units as u
        
        # 查询3c 273周围0.05度的区域
        print("查询3c 273周围0.05度的区域...")
        result_table = Ned.query_region("3c 273", radius=0.05 * u.deg)
        
        print(f"查询成功！找到 {len(result_table)} 个结果")
        print(f"结果类型: {type(result_table)}")
        
        if len(result_table) > 0:
            print(f"\n前5个结果:")
            for i, row in enumerate(result_table[:5], 1):
                print(f"  {i}. {row['Object Name']}")
                print(f"     RA: {row['RA']}, DEC: {row['DEC']}")
                print(f"     红移: {row['Redshift']}")
        
        print("✅ 测试通过\n")
        return True
        
    except Exception as e:
        print(f"❌ 测试失败: {e}\n")
        return False


def test_query_region_by_coordinates():
    """测试按坐标查询区域"""
    print("=== 测试3：按坐标查询区域 ===")
    
    try:
        from astroquery.ipac.ned import Ned
        import astropy.units as u
        from astropy import coordinates
        
        # 使用坐标查询
        print("使用坐标查询区域...")
        co = coordinates.SkyCoord(
            ra=56.38, dec=38.43,
            unit=(u.deg, u.deg), 
            frame='fk4'
        )
        result_table = Ned.query_region(co, radius=0.1 * u.deg, equinox='B1950.0')
        
        print(f"查询成功！找到 {len(result_table)} 个结果")
        print(f"结果类型: {type(result_table)}")
        
        if len(result_table) > 0:
            print(f"\n前5个结果:")
            for i, row in enumerate(result_table[:5], 1):
                print(f"  {i}. {row['Object Name']}")
                print(f"     RA: {row['RA']}, DEC: {row['DEC']}")
        
        print("✅ 测试通过\n")
        return True
        
    except Exception as e:
        print(f"❌ 测试失败: {e}\n")
        return False


def test_query_region_iau():
    """测试IAU格式坐标查询"""
    print("=== 测试4：IAU格式坐标查询 ===")
    
    try:
        from astroquery.ipac.ned import Ned
        
        # 使用IAU格式查询
        print("使用IAU格式'1234-423'查询...")
        result_table = Ned.query_region_iau('1234-423', frame='SuperGalactic', equinox='J2000.0')
        
        print(f"查询成功！找到 {len(result_table)} 个结果")
        print(f"结果类型: {type(result_table)}")
        
        if len(result_table) > 0:
            print(f"\n前5个结果:")
            for i, row in enumerate(result_table[:5], 1):
                print(f"  {i}. {row['Object Name']}")
                print(f"     RA: {row['RA']}, DEC: {row['DEC']}")
        
        print("✅ 测试通过\n")
        return True
        
    except Exception as e:
        print(f"❌ 测试失败: {e}\n")
        return False


def test_query_refcode():
    """测试按参考代码查询"""
    print("=== 测试5：按参考代码查询 ===")
    
    try:
        from astroquery.ipac.ned import Ned
        
        # 按参考代码查询
        print("按参考代码'1997A&A...323...31K'查询...")
        result_table = Ned.query_refcode('1997A&A...323...31K')
        
        print(f"查询成功！找到 {len(result_table)} 个结果")
        print(f"结果类型: {type(result_table)}")
        
        if len(result_table) > 0:
            print(f"\n前5个结果:")
            for i, row in enumerate(result_table[:5], 1):
                print(f"  {i}. {row['Object Name']}")
                print(f"     RA: {row['RA']}, DEC: {row['DEC']}")
                print(f"     红移: {row['Redshift']}")
        
        print("✅ 测试通过\n")
        return True
        
    except Exception as e:
        print(f"❌ 测试失败: {e}\n")
        return False


def test_get_image_list():
    """测试获取图像列表"""
    print("=== 测试6：获取图像列表 ===")
    
    try:
        from astroquery.ipac.ned import Ned
        
        # 获取图像列表
        print("获取M 1的图像列表...")
        image_list = Ned.get_image_list("m1")
        
        print(f"查询成功！找到 {len(image_list)} 个图像")
        print(f"结果类型: {type(image_list)}")
        
        if len(image_list) > 0:
            print(f"\n前3个图像URL:")
            for i, url in enumerate(image_list[:3], 1):
                print(f"  {i}. {url}")
        
        print("✅ 测试通过\n")
        return True
        
    except Exception as e:
        print(f"❌ 测试失败: {e}\n")
        return False


def test_get_spectra_list():
    """测试获取光谱列表"""
    print("=== 测试7：获取光谱列表 ===")
    
    try:
        from astroquery.ipac.ned import Ned
        
        # 获取光谱列表
        print("获取3c 273的光谱列表...")
        spectra_list = Ned.get_image_list("3c 273", item='spectra')
        
        print(f"查询成功！找到 {len(spectra_list)} 个光谱")
        print(f"结果类型: {type(spectra_list)}")
        
        if len(spectra_list) > 0:
            print(f"\n前3个光谱URL:")
            for i, url in enumerate(spectra_list[:3], 1):
                print(f"  {i}. {url}")
        
        print("✅ 测试通过\n")
        return True
        
    except Exception as e:
        print(f"❌ 测试失败: {e}\n")
        return False


def test_get_table():
    """测试获取详细数据表"""
    print("=== 测试8：获取详细数据表 ===")
    
    try:
        from astroquery.ipac.ned import Ned
        
        # 获取位置数据表
        print("获取3C 273的位置数据表...")
        result_table = Ned.get_table("3C 273", table='positions')
        
        print(f"查询成功！找到 {len(result_table)} 条位置记录")
        print(f"结果类型: {type(result_table)}")
        print(f"列名: {result_table.colnames}")
        
        if len(result_table) > 0:
            print(f"\n前5条位置记录:")
            for i, row in enumerate(result_table[:5], 1):
                print(f"  {i}. RA: {row['RA']}")
                print(f"     DEC: {row['DEC']}")
                print(f"     Published Name: {row['Published Name']}")
                print(f"     Refcode: {row['Refcode']}")
        
        print("✅ 测试通过\n")
        return True
        
    except Exception as e:
        print(f"❌ 测试失败: {e}\n")
        return False


def test_clear_cache():
    """测试清除缓存"""
    print("=== 测试9：清除缓存 ===")
    
    try:
        from astroquery.ipac.ned import Ned
        
        print("清除NED缓存...")
        Ned.clear_cache()
        
        print("✅ 测试通过\n")
        return True
        
    except Exception as e:
        print(f"❌ 测试失败: {e}\n")
        return False


def test_fits_file_handling():
    """测试FITS文件处理"""
    print("=== 测试10：FITS文件处理 ===")
    
    try:
        from astroquery.ipac.ned import Ned
        from astropy.io import fits
        import gzip
        import tempfile
        import os
        
        # 测试1：下载并处理图像
        print("1. 下载并处理图像...")
        images = Ned.get_images("m1")  # 返回HDUList对象列表
        
        print(f"下载成功！获得 {len(images)} 个图像")
        print(f"结果类型: {type(images)}")
        
        if len(images) > 0:
            # 查看第一个图像
            hdu_list = images[0]
            print(f"\n第一个图像信息:")
            print(f"  HDU数量: {len(hdu_list)}")
            print(f"  主HDU数据形状: {hdu_list[0].data.shape if hdu_list[0].data is not None else '无数据'}")
            print(f"  主HDU头部关键字数量: {len(hdu_list[0].header)}")
            
        # 测试2：保存图像到临时文件并读取
        print("\n2. 保存和读取FITS文件...")
        if len(images) > 0:
            # 保存为临时文件
            with tempfile.NamedTemporaryFile(suffix='.fits.gz', delete=False) as tmp_file:
                tmp_filename = tmp_file.name
                
            # 保存第一个图像
            hdu_list = images[0]
            hdu_list.writeto(tmp_filename, overwrite=True)
            print(f"  图像保存到: {tmp_filename}")
            
            #直接读取压缩文件
            print("  方法1：直接读取压缩文件...")
            with gzip.open(tmp_filename, 'rb') as f:
                hdul = fits.open(f)
                data = hdul[0].data
                header = hdul[0].header
                print(f"    数据形状: {data.shape}")
                print(f"    头部信息关键字: {list(header.keys())[:5]}...")
            
            # 清理临时文件
            os.unlink(tmp_filename)
            print("  临时文件已清理")
        
        print("✅ 测试通过\n")
        return True
        
    except Exception as e:
        print(f"❌ 测试失败: {e}\n")
        return False


def test_download_and_visualize():
    """测试下载和可视化图像（FITS用临时文件，图像保存到项目目录）"""
    print("=== 测试11：下载和可视化图像 ===")
    
    try:
        from astroquery.ipac.ned import Ned
        from astropy.io import fits
        import requests
        import gzip
        import io
        import os
        import tempfile
        
        # 1. 获取图像列表
        print("1. 获取M 1的图像列表...")
        image_list = Ned.get_image_list("m1")
        
        if not image_list:
            print("未找到图像")
            return False
        
        print(f"找到 {len(image_list)} 个图像")
        
        # 2. 下载第一个图像到临时文件
        print("\n2. 下载第一个图像到临时文件...")
        url = image_list[0]
        
        response = requests.get(url, timeout=60)
        response.raise_for_status()
        
        # 尝试解压
        try:
            with gzip.GzipFile(fileobj=io.BytesIO(response.content)) as gz:
                content = gz.read()
        except gzip.BadGzipFile:
            content = response.content
        
        # 保存到临时文件
        with tempfile.NamedTemporaryFile(suffix='.fits', delete=False) as tmp_fits:
            tmp_fits_path = tmp_fits.name
            tmp_fits.write(content)
        
        file_size = os.path.getsize(tmp_fits_path) / (1024 * 1024)
        print(f"✅ 下载成功: 临时FITS文件 ({file_size:.2f} MB)")
        
        # 3. 可视化图像（保存到项目目录）
        print("\n3. 可视化图像...")
        try:
            import matplotlib.pyplot as plt
            import numpy as np
            
            # 创建可视化目录
            viz_dir = os.path.join(os.path.dirname(os.path.dirname(__file__)), "visualizations")
            os.makedirs(viz_dir, exist_ok=True)
            
            # 读取FITS数据
            hdul = fits.open(tmp_fits_path)
            data = hdul[0].data
            hdul.close()  # 立即关闭文件
            
            if data is not None:
                # 创建简单可视化
                fig, axes = plt.subplots(1, 2, figsize=(10, 4))
                
                # 线性缩放
                axes[0].imshow(data, cmap='gray', origin='lower')
                axes[0].set_title('Linear Scale')
                axes[0].axis('off')
                
                # 对数缩放
                data_pos = np.where(data > 0, data, 1)
                axes[1].imshow(data_pos, cmap='gray', origin='lower', 
                              norm=plt.matplotlib.colors.LogNorm())
                axes[1].set_title('Log Scale')
                axes[1].axis('off')
                
                plt.tight_layout()
                
                # 保存可视化到项目目录
                viz_path = os.path.join(viz_dir, 'm1_visualization.png')
                plt.savefig(viz_path, dpi=150, bbox_inches='tight')
                plt.close()
                
                viz_size = os.path.getsize(viz_path) / 1024  # KB
                print(f"✅ 可视化已保存: {viz_path} ({viz_size:.1f} KB)")
                print(f"  数据形状: {data.shape}")
                print(f"  像素范围: {np.min(data):.0f} - {np.max(data):.0f}")
            else:
                print("警告: 文件没有数据")
                    
        except ImportError:
            print("跳过可视化（matplotlib未安装）")
        
        # 清理临时FITS文件
        try:
            os.unlink(tmp_fits_path)
            print(f"  临时FITS文件已清理")
        except Exception as e:
            print(f"  警告: 清理临时文件失败: {e}")
        
        print("✅ 测试通过\n")
        return True
        
    except Exception as e:
        print(f"❌ 测试失败: {e}\n")
        return False


def run_all_tests():
    """运行所有测试"""
    print("=" * 60)
    print("开始测试astroquery库的基本功能")
    print("=" * 60)
    print()
    
    # 运行所有测试
    tests = [
        test_query_object,
        test_query_region_by_name,
        test_query_region_by_coordinates,
        test_query_region_iau,
        test_query_refcode,
        test_get_image_list,
        test_get_spectra_list,
        test_get_table,
        test_clear_cache,
        test_fits_file_handling,
        test_download_and_visualize
    ]
    
    results = []
    for test_func in tests:
        try:
            result = test_func()
            results.append(result)
        except Exception as e:
            print(f"测试执行出错: {e}\n")
            results.append(False)
    
    # 统计结果
    print("=" * 60)
    print("测试结果统计")
    print("=" * 60)
    passed = sum(results)
    total = len(results)
    print(f"通过: {passed}/{total}")
    print(f"失败: {total - passed}/{total}")
    
    if passed == total:
        print("\n🎉 所有测试通过！")
    else:
        print(f"\n⚠️  有 {total - passed} 个测试失败")
    
    return passed == total


if __name__ == "__main__":
    run_all_tests()
