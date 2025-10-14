#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
基础功能测试
验证核心功能的正确性
"""

import os
import sys
import unittest
import tempfile
import pandas as pd
import numpy as np
from pathlib import Path

# 添加src目录到Python路径
sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

from svg_water_quality_generator.src.core.generator import SVGGenerator
from svg_water_quality_generator.src.data.parser import DataParser
from svg_water_quality_generator.src.data.standardizer import DataStandardizer
from svg_water_quality_generator.src.data.validator import DataValidator

class TestBasicFunctionality(unittest.TestCase):
    """基础功能测试类"""
    
    def setUp(self):
        """测试前设置"""
        self.temp_dir = tempfile.mkdtemp()
        self.test_data = self.create_test_data()
    
    def tearDown(self):
        """测试后清理"""
        import shutil
        if os.path.exists(self.temp_dir):
            shutil.rmtree(self.temp_dir)
    
    def create_test_data(self) -> pd.DataFrame:
        """创建测试数据"""
        np.random.seed(42)
        
        data = []
        for i in range(20):
            record = {
                'index': i,
                'longitude': 120.2 + np.random.uniform(-0.1, 0.1),
                'latitude': 31.3 + np.random.uniform(-0.1, 0.1),
                'cod': np.random.uniform(10, 30),
                'nh3n': np.random.uniform(0.5, 2.0),
                'tp': np.random.uniform(0.1, 0.5),
                'turbidity': np.random.uniform(5, 20)
            }
            data.append(record)
        
        return pd.DataFrame(data)
    
    def test_data_parser(self):
        """测试数据解析器"""
        parser = DataParser()
        
        # 保存测试CSV文件
        csv_path = os.path.join(self.temp_dir, "test_data.csv")
        self.test_data.to_csv(csv_path, index=False)
        
        # 测试CSV解析
        df = parser.parse_csv_file(csv_path)
        self.assertIsNotNone(df)
        self.assertEqual(len(df), len(self.test_data))
    
    def test_data_standardizer(self):
        """测试数据标准化器"""
        standardizer = DataStandardizer()
        
        # 测试数据标准化
        standardized_data, mapping = standardizer.standardize_dataframe(self.test_data)
        
        self.assertIsNotNone(standardized_data)
        self.assertIn('longitude', standardized_data.columns)
        self.assertIn('latitude', standardized_data.columns)
        
        # 测试数据摘要
        summary = standardizer.get_data_summary(standardized_data)
        self.assertIn('total_records', summary)
        self.assertEqual(summary['total_records'], len(self.test_data))
    
    def test_data_validator(self):
        """测试数据验证器"""
        validator = DataValidator()
        
        # 测试数据验证
        validation_result = validator.validate_dataframe(self.test_data)
        
        self.assertIsNotNone(validation_result)
        self.assertIn('is_valid', validation_result)
        self.assertIn('statistics', validation_result)
        
        # 测试坐标验证
        self.assertTrue(validator.validate_coordinates_only(120.2, 31.3))
        self.assertFalse(validator.validate_coordinates_only(999, 31.3))
    
    def test_svg_generator_basic(self):
        """测试SVG生成器基础功能"""
        generator = SVGGenerator(
            output_dir=self.temp_dir,
            log_level="ERROR"  # 减少测试日志
        )
        
        try:
            # 测试从DataFrame生成SVG
            svg_path = generator.generate_from_dataframe(
                df=self.test_data,
                indicator="cod",
                output_filename="test_cod.svg",
                grid_resolution=100  # 使用低分辨率加快测试
            )
            
            if svg_path:
                self.assertTrue(os.path.exists(svg_path))
                self.assertTrue(svg_path.endswith('.svg'))
            
        finally:
            generator.cleanup()
    
    def test_interpolation_algorithms(self):
        """测试插值算法"""
        from svg_water_quality_generator.src.interpolation.enhanced_interpolation import enhanced_interpolation_with_boundary
        
        # 测试增强插值
        result = enhanced_interpolation_with_boundary(
            data=self.test_data,
            indicator_col='cod',
            grid_resolution=50,  # 小网格快速测试
            boundary_method='convex_hull'
        )
        
        if result[0] is not None:
            grid_values, grid_x, grid_y, boundary_mask, boundary_points = result
            
            self.assertIsNotNone(grid_values)
            self.assertIsNotNone(grid_x)
            self.assertIsNotNone(grid_y)
            self.assertEqual(grid_values.shape, grid_x.shape)
            self.assertEqual(grid_values.shape, grid_y.shape)
    
    def test_colormap_creation(self):
        """测试颜色映射创建"""
        from svg_water_quality_generator.src.visualization.color_mapper import create_colormap, validate_colormap
        
        # 测试标准颜色映射
        cmap = create_colormap('jet')
        self.assertTrue(validate_colormap(cmap))
        
        # 测试自定义颜色映射
        cmap_custom = create_colormap('water_quality')
        self.assertTrue(validate_colormap(cmap_custom))
    
    def test_indicator_config(self):
        """测试指标配置"""
        from svg_water_quality_generator.src.config.indicators import get_indicator_info, validate_indicator_value
        
        # 测试获取指标信息
        cod_info = get_indicator_info('cod')
        self.assertIsNotNone(cod_info)
        self.assertEqual(cod_info['name'], '化学需氧量')
        self.assertEqual(cod_info['unit'], 'mg/L')
        
        # 测试指标值验证
        validation = validate_indicator_value('cod', 15.0)
        self.assertTrue(validation['is_valid'])
        self.assertIn('level', validation)
    
    def test_grading_standards(self):
        """测试国标分级"""
        from svg_water_quality_generator.src.config.grading_standards import classify_value, get_supported_indicators
        
        # 测试获取支持的指标
        supported = get_supported_indicators()
        self.assertIn('cod', supported)
        self.assertIn('nh3n', supported)
        
        # 测试分级
        classification = classify_value('cod', 15.0)
        self.assertTrue(classification['supported'])
        self.assertIn('grade', classification)
        self.assertEqual(classification['indicator'], 'cod')

class TestErrorHandling(unittest.TestCase):
    """错误处理测试类"""
    
    def test_empty_data_handling(self):
        """测试空数据处理"""
        from svg_water_quality_generator.src.data.validator import DataValidator
        
        validator = DataValidator()
        
        # 测试空DataFrame
        empty_df = pd.DataFrame()
        result = validator.validate_dataframe(empty_df)
        self.assertFalse(result['is_valid'])
        self.assertIn('DataFrame为空', result['errors'])
    
    def test_invalid_coordinates(self):
        """测试无效坐标处理"""
        from svg_water_quality_generator.src.data.validator import DataValidator
        
        validator = DataValidator()
        
        # 测试无效坐标
        invalid_data = pd.DataFrame({
            'longitude': [999, 120.2],  # 第一个坐标无效
            'latitude': [31.3, 31.3],
            'cod': [15.0, 20.0]
        })
        
        result = validator.validate_dataframe(invalid_data)
        self.assertIn('warnings', result)

def run_tests():
    """运行所有测试"""
    # 创建测试套件
    loader = unittest.TestLoader()
    suite = unittest.TestSuite()
    
    # 添加测试类
    suite.addTests(loader.loadTestsFromTestCase(TestBasicFunctionality))
    suite.addTests(loader.loadTestsFromTestCase(TestErrorHandling))
    
    # 运行测试
    runner = unittest.TextTestRunner(verbosity=2)
    result = runner.run(suite)
    
    return result.wasSuccessful()

if __name__ == '__main__':
    print("🧪 运行SVG Water Quality Generator基础功能测试")
    print("=" * 60)
    
    success = run_tests()
    
    if success:
        print("\n✅ 所有测试通过！")
    else:
        print("\n❌ 部分测试失败！")
        sys.exit(1)