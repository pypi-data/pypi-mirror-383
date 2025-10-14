#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
SVG Water Quality Generator 统一接口

这是水质数据处理和SVG生成的统一入口点，提供命令行和编程接口。
"""

import os
import sys
import logging
import argparse
import tempfile
import shutil
from pathlib import Path
from typing import Dict, List, Tuple, Optional, Any
import pandas as pd
import numpy as np
import json

# 尝试相对导入，失败则使用绝对导入
try:
    from .core.downloader import ResourceDownloader
    from .core.extractor import ZipExtractor
    from .data.parser import DataParser
    from .data.standardizer import DataStandardizer
    from .data.validator import DataValidator
    from .interpolation.enhanced_interpolation import enhanced_interpolation_with_boundary
    from .visualization.svg_generator import create_clean_interpolation_svg
    from .config.indicators import WATER_QUALITY_INDICATORS
    from .utils.logger import setup_logging
except ImportError:
    # 开发模式下的绝对导入
    from core.downloader import ResourceDownloader
    from core.extractor import ZipExtractor
    from data.parser import DataParser
    from data.standardizer import DataStandardizer
    from data.validator import DataValidator
    from interpolation.enhanced_interpolation import enhanced_interpolation_with_boundary
    from visualization.svg_generator import create_clean_interpolation_svg
    from config.indicators import WATER_QUALITY_INDICATORS
    from utils.logger import setup_logging

logger = logging.getLogger(__name__)

class WaterQualityProcessor:
    """水质数据处理器"""
    
    def __init__(self, 
                 output_dir: str = "./outputs",
                 temp_dir: Optional[str] = None,
                 grid_resolution: int = 400,
                 log_level: str = "INFO"):
        """
        初始化水质数据处理器
        
        Args:
            output_dir: 输出目录
            temp_dir: 临时目录
            grid_resolution: 网格分辨率
            log_level: 日志级别
        """
        self.output_dir = Path(output_dir)
        self.output_dir.mkdir(parents=True, exist_ok=True)
        
        if temp_dir is None:
            self.temp_dir = Path(tempfile.mkdtemp(prefix='water_quality_'))
        else:
            self.temp_dir = Path(temp_dir)
            self.temp_dir.mkdir(parents=True, exist_ok=True)
        
        self.grid_resolution = grid_resolution
        
        # 初始化组件
        self.downloader = ResourceDownloader(str(self.temp_dir))
        self.extractor = ZipExtractor(str(self.temp_dir))
        self.parser = DataParser()
        self.standardizer = DataStandardizer()
        self.validator = DataValidator()
        
        # 设置日志
        setup_logging(log_level)
        logger.info(f"水质数据处理器已初始化，输出目录: {self.output_dir}")
    
    def process_from_oss_zip(self, 
                           zip_url: str,
                           colormap: str = "jet",
                           boundary_method: str = "alpha_shape",
                           interpolation_method: str = "linear",
                           transparent_bg: bool = True,
                           figsize: Tuple[float, float] = (10, 8)) -> Dict[str, Any]:
        """
        从OSS ZIP文件处理水质数据并生成SVG
        
        Args:
            zip_url: OSS ZIP文件URL
            colormap: 颜色映射方案
            boundary_method: 边界检测方法
            interpolation_method: 插值方法
            transparent_bg: 是否使用透明背景
            figsize: 图形尺寸
            
        Returns:
            处理结果字典，包含SVG文件路径和经纬度边界信息
        """
        try:
            logger.info(f"开始处理OSS ZIP文件: {zip_url}")
            
            # 1. 下载ZIP文件
            zip_path = self.downloader.download(zip_url)
            if not zip_path:
                raise ValueError("ZIP文件下载失败")
            
            # 2. 解压文件
            extract_dir = self.extractor.extract(zip_path)
            if not extract_dir:
                raise ValueError("ZIP文件解压失败")
            
            # 3. 解析数据
            df = self.parser.parse_uav_data(extract_dir)
            if df is None:
                raise ValueError("数据解析失败")
            
            # 4. 标准化数据
            df, mapping_info = self.standardizer.standardize_dataframe(df)
            
            # 5. 验证数据
            validation_result = self.validator.validate_dataframe(df)
            if not validation_result['is_valid']:
                logger.warning(f"数据验证警告: {validation_result['warnings']}")
            
            # 6. 获取所有可用指标
            available_indicators = self._get_available_indicators(df)
            logger.info(f"可用指标: {available_indicators}")
            
            # 7. 为每个指标生成SVG
            results = {}
            for indicator in available_indicators:
                svg_result = self._generate_svg_for_indicator(
                    df, indicator, colormap, boundary_method, 
                    interpolation_method, transparent_bg, figsize
                )
                results[indicator] = svg_result
            
            logger.info(f"完成处理，共生成{len(results)}个SVG文件")
            return results
            
        except Exception as e:
            logger.error(f"处理过程中发生错误: {str(e)}")
            raise
        finally:
            # 清理临时文件
            if self.temp_dir.exists():
                shutil.rmtree(self.temp_dir)
    
    def _get_available_indicators(self, df: pd.DataFrame) -> List[str]:
        """获取数据中可用的水质指标"""
        available = []
        for indicator in WATER_QUALITY_INDICATORS.keys():
            if indicator in df.columns:
                # 检查是否有有效数据
                has_valid_data = not df[indicator].isna().all()
                if has_valid_data:
                    available.append(indicator)
        return available
    
    def _generate_svg_for_indicator(self, 
                                  df: pd.DataFrame,
                                  indicator: str,
                                  colormap: str,
                                  boundary_method: str,
                                  interpolation_method: str,
                                  transparent_bg: bool,
                                  figsize: Tuple[float, float]) -> Dict[str, Any]:
        """为单个指标生成SVG"""
        try:
            logger.info(f"开始为指标 {indicator} 生成SVG")
            
            # 过滤有效数据
            valid_data = df[['longitude', 'latitude', indicator]].dropna()
            if len(valid_data) < 3:
                logger.warning(f"指标 {indicator} 的有效数据点不足3个，跳过")
                return None
            
            # 增强插值
            interpolated_data, grid_x, grid_y, mask, boundary_points = enhanced_interpolation_with_boundary(
                data=valid_data,
                indicator_col=indicator,
                grid_resolution=self.grid_resolution,
                method=interpolation_method,
                boundary_method=boundary_method
            )
            
            # 计算经纬度边界信息
            bounds_info = self._calculate_bounds_info(grid_x, grid_y, mask)
            
            # 生成SVG文件
            svg_filename = f"{indicator}_heatmap.svg"
            svg_path = self.output_dir / svg_filename
            
            success = create_clean_interpolation_svg(
                grid_values=interpolated_data,
                grid_x=grid_x,
                grid_y=grid_y,
                save_path=str(svg_path),
                title=f"{WATER_QUALITY_INDICATORS[indicator]['name']} 分布图",
                colormap=colormap,
                figsize=figsize,
                transparent_bg=transparent_bg
            )
            
            if not success:
                logger.error(f"SVG生成失败: {indicator}")
                return None
            
            # 生成边界信息文件
            bounds_filename = f"{indicator}_bounds.json"
            bounds_path = self.output_dir / bounds_filename
            with open(bounds_path, 'w', encoding='utf-8') as f:
                json.dump(bounds_info, f, indent=2, ensure_ascii=False)
            
            result = {
                'svg_path': str(svg_path),
                'bounds_path': str(bounds_path),
                'bounds_info': bounds_info,
                'indicator_name': WATER_QUALITY_INDICATORS[indicator]['name'],
                'unit': WATER_QUALITY_INDICATORS[indicator]['unit'],
                'data_points': len(valid_data),
                'min_value': float(valid_data[indicator].min()),
                'max_value': float(valid_data[indicator].max()),
                'mean_value': float(valid_data[indicator].mean())
            }
            
            logger.info(f"指标 {indicator} 的SVG生成完成: {svg_path}")
            return result
            
        except Exception as e:
            logger.error(f"生成指标 {indicator} 的SVG时发生错误: {str(e)}")
            return None
    
    def _calculate_bounds_info(self, 
                             grid_x: np.ndarray, 
                             grid_y: np.ndarray, 
                             mask: np.ndarray) -> Dict[str, Any]:
        """计算经纬度边界信息用于地图叠加"""
        # 找到有效区域的边界
        valid_indices = np.where(mask)
        
        if len(valid_indices[0]) == 0:
            # 如果没有有效区域，使用整个网格
            min_lat, max_lat = grid_y.min(), grid_y.max()
            min_lon, max_lon = grid_x.min(), grid_x.max()
        else:
            # 使用有效区域计算边界
            valid_y_coords = grid_y[valid_indices]
            valid_x_coords = grid_x[valid_indices]
            
            min_lat = float(valid_y_coords.min())
            max_lat = float(valid_y_coords.max())
            min_lon = float(valid_x_coords.min())
            max_lon = float(valid_x_coords.max())
        
        # 计算中心点
        center_lat = (min_lat + max_lat) / 2
        center_lon = (min_lon + max_lon) / 2
        
        # 计算范围
        lat_range = max_lat - min_lat
        lon_range = max_lon - min_lon
        
        bounds_info = {
            'geographic_bounds': {
                'min_longitude': min_lon,
                'max_longitude': max_lon,
                'min_latitude': min_lat,
                'max_latitude': max_lat,
                'center_longitude': center_lon,
                'center_latitude': center_lat,
                'longitude_range': lon_range,
                'latitude_range': lat_range
            },
            'grid_info': {
                'grid_resolution': self.grid_resolution,
                'grid_width': grid_x.shape[1],
                'grid_height': grid_y.shape[0],
                'valid_pixels': int(np.sum(mask))
            },
            'projection_info': {
                'coordinate_system': 'WGS84',
                'units': 'degrees',
                'note': '经纬度坐标，适用于Web地图叠加'
            }
        }
        
        return bounds_info
    
    def __enter__(self):
        """上下文管理器入口"""
        return self
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        """上下文管理器出口，清理临时文件"""
        if hasattr(self, 'temp_dir') and self.temp_dir.exists():
            shutil.rmtree(self.temp_dir)

def parse_arguments():
    """解析命令行参数"""
    parser = argparse.ArgumentParser(
        description='SVG Water Quality Generator - 水质数据SVG热力图生成器',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog='''
使用示例:
  python interface.py --zip-url "https://example.com/data.zip" --output-dir "./outputs"
  python interface.py --zip-url "https://example.com/data.zip" --colormap "water_quality" --resolution 600
        '''
    )
    
    # 必需参数
    parser.add_argument(
        '--zip-url', 
        required=True,
        help='OSS ZIP文件下载URL'
    )
    
    # 可选参数
    parser.add_argument(
        '--output-dir', 
        default='./outputs',
        help='输出目录 (默认: ./outputs)'
    )
    
    parser.add_argument(
        '--resolution', 
        type=int, 
        default=400,
        help='网格分辨率 (默认: 400)'
    )
    
    parser.add_argument(
        '--colormap', 
        default='jet',
        choices=['jet', 'water_quality', 'viridis', 'RdYlBu_r'],
        help='颜色映射方案 (默认: jet)'
    )
    
    parser.add_argument(
        '--boundary-method', 
        default='alpha_shape',
        choices=['alpha_shape', 'convex_hull', 'density_based'],
        help='边界检测方法 (默认: alpha_shape)'
    )
    
    parser.add_argument(
        '--interpolation-method', 
        default='linear',
        choices=['linear', 'cubic', 'nearest'],
        help='插值方法 (默认: linear)'
    )
    
    parser.add_argument(
        '--figsize', 
        nargs=2, 
        type=float, 
        default=[12, 10],
        help='图形尺寸 width height (默认: 12 10)'
    )
    
    parser.add_argument(
        '--log-level', 
        default='INFO',
        choices=['DEBUG', 'INFO', 'WARNING', 'ERROR'],
        help='日志级别 (默认: INFO)'
    )
    
    parser.add_argument(
        '--no-transparent', 
        action='store_true',
        help='禁用透明背景'
    )
    
    return parser.parse_args()

def print_results(results: Dict[str, Any]):
    """打印处理结果"""
    print("\n=== 处理结果 ===")
    
    if not results:
        print("没有生成任何结果")
        return
    
    for indicator, result in results.items():
        if result:
            print(f"\n📊 指标: {result['indicator_name']} ({indicator})")
            print(f"   SVG文件: {result['svg_path']}")
            print(f"   边界文件: {result['bounds_path']}")
            print(f"   数据点数: {result['data_points']}")
            print(f"   数值范围: {result['min_value']:.2f} - {result['max_value']:.2f} {result['unit']}")
            print(f"   平均值: {result['mean_value']:.2f} {result['unit']}")
            
            bounds = result['bounds_info']['geographic_bounds']
            print(f"   📍 经度范围: {bounds['min_longitude']:.6f} - {bounds['max_longitude']:.6f}")
            print(f"   📍 纬度范围: {bounds['min_latitude']:.6f} - {bounds['max_latitude']:.6f}")
            print(f"   📍 中心点: ({bounds['center_longitude']:.6f}, {bounds['center_latitude']:.6f})")
        else:
            print(f"\n❌ 指标 {indicator} 处理失败")

def main():
    """主入口函数"""
    try:
        # 解析命令行参数
        args = parse_arguments()
        
        # 使用水质数据处理器
        with WaterQualityProcessor(
            output_dir=args.output_dir,
            grid_resolution=args.resolution,
            log_level=args.log_level
        ) as processor:
            
            # 处理数据
            results = processor.process_from_oss_zip(
                zip_url=args.zip_url,
                colormap=args.colormap,
                boundary_method=args.boundary_method,
                interpolation_method=args.interpolation_method,
                transparent_bg=not args.no_transparent,
                figsize=tuple(args.figsize)
            )
            
            # 打印结果
            print_results(results)
            
            # 返回成功状态
            return 0
            
    except KeyboardInterrupt:
        print("\n用户中断处理")
        return 1
    except Exception as e:
        print(f"\n处理失败: {str(e)}")
        return 1

if __name__ == "__main__":
    sys.exit(main())