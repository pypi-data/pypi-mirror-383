#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
数据标准化模块
提供数据清洗、列名标准化、指标名称统一等功能
"""
import logging
import pandas as pd
import numpy as np
from typing import Dict, List, Tuple, Optional

logger = logging.getLogger(__name__)

class DataStandardizer:
    """数据标准化器类"""
    
    def __init__(self):
        """初始化数据标准化器"""
        # 列名映射表
        self.column_mapping = {
            # 经度列名
            'lon': 'longitude',
            'lng': 'longitude', 
            '经度': 'longitude',
            
            # 纬度列名
            'lat': 'latitude',
            '纬度': 'latitude',
            
            # 索引列名
            'id': 'index',
            'ID': 'index',
            '编号': 'index',
            '序号': 'index',
            '点位': 'index',
        }
        
        # 水质指标映射表
        self.indicator_mapping = {
            # COD
            'cod': 'cod',
            'COD': 'cod',
            '化学需氧量': 'cod',
            'chemical_oxygen_demand': 'cod',
            'codmn': 'cod_mn',  # 高锰酸盐指数
            
            # 氨氮
            'nh3n': 'nh3n',
            'NH3-N': 'nh3n',
            'NH3_N': 'nh3n',
            '氨氮': 'nh3n',
            'ammonia_nitrogen': 'nh3n',
            
            # 总磷
            'tp': 'tp',
            'TP': 'tp',
            '总磷': 'tp',
            'total_phosphorus': 'tp',
            
            # 总氮
            'tn': 'tn',
            'TN': 'tn',
            '总氮': 'tn',
            'total_nitrogen': 'tn',
            
            # 溶解氧
            'do': 'do',
            'DO': 'do',
            '溶解氧': 'do',
            'dissolved_oxygen': 'do',
            
            # pH值
            'ph': 'ph',
            'pH': 'ph',
            'PH': 'ph',
            'acidity': 'ph',
            
            # 浊度
            'turbidity': 'turbidity',
            'TURBIDITY': 'turbidity',
            '浊度': 'turbidity',
            'ntu': 'turbidity',
            
            # 叶绿素a
            'chla': 'chla',
            'chl-a': 'chla',
            'chlorophyll_a': 'chla',
            '叶绿素a': 'chla',
            '叶绿素A': 'chla',
            'CHLa': 'chla',
            
            # 总悬浮物
            'ss': 'ss',
            'SS': 'ss',
            'TSS': 'ss',
            
            # 蓝绿藻
            'bga': 'bga',
            'Bga': 'bga',
            'BGA': 'bga',
        }
    
    def standardize_dataframe(self, df: pd.DataFrame) -> Tuple[pd.DataFrame, Dict[str, str]]:
        """标准化DataFrame
        
        Args:
            df: 原始DataFrame
            
        Returns:
            (标准化后的DataFrame, 列名映射字典)
        """
        try:
            logger.info("开始标准化DataFrame")
            
            df_standardized = df.copy()
            applied_mapping = {}
            
            # 标准化列名
            df_standardized, column_map = self._standardize_column_names(df_standardized)
            applied_mapping.update(column_map)
            
            # 标准化指标名称
            df_standardized, indicator_map = self._standardize_indicator_names(df_standardized)
            applied_mapping.update(indicator_map)
            
            # 清洗数据
            df_standardized = self._clean_data(df_standardized)
            
            # 验证必要列
            df_standardized = self._validate_required_columns(df_standardized)
            
            logger.info(f"数据标准化完成，应用映射: {applied_mapping}")
            
            return df_standardized, applied_mapping
            
        except Exception as e:
            logger.error(f"数据标准化失败: {str(e)}")
            return df, {}
    
    def _standardize_column_names(self, df: pd.DataFrame) -> Tuple[pd.DataFrame, Dict[str, str]]:
        """标准化列名
        
        Args:
            df: DataFrame
            
        Returns:
            (标准化后的DataFrame, 列名映射字典)
        """
        applied_mapping = {}
        
        # 创建新的列名映射
        new_columns = {}
        for col in df.columns:
            col_lower = col.lower().strip()
            
            # 直接匹配
            if col_lower in self.column_mapping:
                new_col = self.column_mapping[col_lower]
                new_columns[col] = new_col
                applied_mapping[col] = new_col
            # 包含匹配
            else:
                for old_name, new_name in self.column_mapping.items():
                    if old_name in col_lower:
                        new_columns[col] = new_name
                        applied_mapping[col] = new_name
                        break
        
        # 应用列名更改
        if new_columns:
            df = df.rename(columns=new_columns)
            logger.info(f"标准化列名: {new_columns}")
        
        return df, applied_mapping
    
    def _standardize_indicator_names(self, df: pd.DataFrame) -> Tuple[pd.DataFrame, Dict[str, str]]:
        """标准化指标名称
        
        Args:
            df: DataFrame
            
        Returns:
            (标准化后的DataFrame, 指标映射字典)
        """
        applied_mapping = {}
        
        # 排除坐标列
        coord_columns = ['index', 'longitude', 'latitude']
        indicator_columns = [col for col in df.columns if col not in coord_columns]
        
        # 创建新的指标名映射
        new_columns = {}
        for col in indicator_columns:
            col_lower = col.lower().strip()
            
            # 直接匹配
            if col_lower in self.indicator_mapping:
                new_col = self.indicator_mapping[col_lower]
                new_columns[col] = new_col
                applied_mapping[col] = new_col
            # 包含匹配
            else:
                for old_name, new_name in self.indicator_mapping.items():
                    if old_name in col_lower:
                        new_columns[col] = new_name
                        applied_mapping[col] = new_name
                        break
        
        # 应用指标名更改
        if new_columns:
            df = df.rename(columns=new_columns)
            logger.info(f"标准化指标名: {new_columns}")
        
        return df, applied_mapping
    
    def _clean_data(self, df: pd.DataFrame) -> pd.DataFrame:
        """清洗数据
        
        Args:
            df: DataFrame
            
        Returns:
            清洗后的DataFrame
        """
        try:
            initial_count = len(df)
            
            # 转换数据类型
            if 'longitude' in df.columns:
                df['longitude'] = pd.to_numeric(df['longitude'], errors='coerce')
            
            if 'latitude' in df.columns:
                df['latitude'] = pd.to_numeric(df['latitude'], errors='coerce')
            
            if 'index' in df.columns:
                df['index'] = pd.to_numeric(df['index'], errors='coerce').astype('Int64')
            
            # 转换指标列为数值型
            coord_columns = ['index', 'longitude', 'latitude']
            for col in df.columns:
                if col not in coord_columns:
                    df[col] = pd.to_numeric(df[col], errors='coerce')
            
            # 删除无效的坐标数据
            if 'longitude' in df.columns and 'latitude' in df.columns:
                df = df.dropna(subset=['longitude', 'latitude'])
                
                # 验证坐标范围
                df = df[
                    (df['longitude'] >= -180) & (df['longitude'] <= 180) &
                    (df['latitude'] >= -90) & (df['latitude'] <= 90)
                ]
            
            # 删除全部为NaN的行
            df = df.dropna(how='all')
            
            final_count = len(df)
            if initial_count != final_count:
                logger.info(f"数据清洗：删除 {initial_count - final_count} 条无效记录")
            
            return df
            
        except Exception as e:
            logger.warning(f"数据清洗失败: {str(e)}")
            return df
    
    def _validate_required_columns(self, df: pd.DataFrame) -> pd.DataFrame:
        """验证必要列是否存在
        
        Args:
            df: DataFrame
            
        Returns:
            验证后的DataFrame
        """
        required_columns = ['longitude', 'latitude']
        missing_columns = [col for col in required_columns if col not in df.columns]
        
        if missing_columns:
            logger.error(f"缺少必要列: {missing_columns}")
            # 如果缺少必要列，尝试从原列名恢复
            if 'longitude' not in df.columns:
                for col in df.columns:
                    if any(name in col.lower() for name in ['lon', '经度', 'x']):
                        df = df.rename(columns={col: 'longitude'})
                        logger.info(f"从 {col} 恢复 longitude 列")
                        break
            
            if 'latitude' not in df.columns:
                for col in df.columns:
                    if any(name in col.lower() for name in ['lat', '纬度', 'y']):
                        df = df.rename(columns={col: 'latitude'})
                        logger.info(f"从 {col} 恢复 latitude 列")
                        break
        
        # 确保有索引列
        if 'index' not in df.columns:
            df['index'] = range(len(df))
            logger.info("添加索引列")
        
        return df
    
    def get_data_summary(self, df: pd.DataFrame) -> Dict:
        """获取数据摘要信息
        
        Args:
            df: DataFrame
            
        Returns:
            数据摘要字典
        """
        try:
            coord_columns = ['index', 'longitude', 'latitude']
            indicator_columns = [col for col in df.columns if col not in coord_columns]
            
            summary = {
                'total_records': len(df),
                'indicator_count': len(indicator_columns),
                'indicators': indicator_columns,
                'coordinate_range': {},
                'indicator_stats': {}
            }
            
            # 坐标范围
            if 'longitude' in df.columns and 'latitude' in df.columns:
                summary['coordinate_range'] = {
                    'longitude': {
                        'min': float(df['longitude'].min()),
                        'max': float(df['longitude'].max())
                    },
                    'latitude': {
                        'min': float(df['latitude'].min()),
                        'max': float(df['latitude'].max())
                    }
                }
            
            # 指标统计
            for col in indicator_columns:
                if df[col].notna().any():
                    summary['indicator_stats'][col] = {
                        'min': float(df[col].min()),
                        'max': float(df[col].max()),
                        'mean': float(df[col].mean()),
                        'valid_count': int(df[col].notna().sum())
                    }
            
            logger.info(f"数据摘要: {summary['total_records']}条记录, {summary['indicator_count']}个指标")
            
            return summary
            
        except Exception as e:
            logger.error(f"生成数据摘要失败: {str(e)}")
            return {}