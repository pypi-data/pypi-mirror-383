"""数据源基类"""

from abc import ABC, abstractmethod
from typing import Any, Dict, Optional
import pandas as pd


class DataSource(ABC):
    """数据源抽象基类"""
    
    def __init__(self, config: Dict[str, Any]):
        """
        初始化数据源
        
        Args:
            config: 数据源配置字典
        """
        self.config = config
        self.name = config.get('name', 'unnamed')
        self._data: Optional[pd.DataFrame] = None
        self._cache_enabled = config.get('cache', True)
    
    @abstractmethod
    def fetch(self) -> pd.DataFrame:
        """获取数据
        
        Returns:
            pandas DataFrame
        """
        pass
    
    def get_data(self, force_refresh: bool = False) -> pd.DataFrame:
        """获取数据（带缓存）
        
        Args:
            force_refresh: 是否强制刷新数据
        
        Returns:
            pandas DataFrame
        """
        if self._cache_enabled and self._data is not None and not force_refresh:
            return self._data
        
        self._data = self.fetch()
        return self._data
    
    def clear_cache(self):
        """清除缓存"""
        self._data = None
    
    def filter_columns(self, columns: Optional[list] = None) -> pd.DataFrame:
        """筛选指定列
        
        Args:
            columns: 要筛选的列名列表，None表示返回所有列
        
        Returns:
            筛选后的DataFrame
        """
        data = self.get_data()
        if columns is None:
            return data
        
        available_columns = [col for col in columns if col in data.columns]
        return data[available_columns]
    
    def get_summary(self) -> Dict[str, Any]:
        """获取数据摘要信息"""
        data = self.get_data()
        return {
            'name': self.name,
            'rows': len(data),
            'columns': list(data.columns),
            'dtypes': {col: str(dtype) for col, dtype in data.dtypes.items()},
        }

