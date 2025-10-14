"""JSON数据源"""

import json
from pathlib import Path
from typing import Dict, Any
import pandas as pd

from pdf_generator.data_sources.base import DataSource


class JSONDataSource(DataSource):
    """从JSON文件或字典加载数据"""
    
    def fetch(self) -> pd.DataFrame:
        """从JSON获取数据"""
        # 支持直接传入数据
        if 'data' in self.config:
            data = self.config['data']
            return pd.DataFrame(data)
        
        # 从文件加载
        if 'path' not in self.config:
            raise ValueError(f"JSON data source '{self.name}' requires 'path' or 'data' field")
        
        path = Path(self.config['path'])
        if not path.exists():
            raise FileNotFoundError(f"JSON file not found: {path}")
        
        with open(path, 'r', encoding='utf-8') as f:
            data = json.load(f)
        
        # 处理不同的JSON结构
        if isinstance(data, list):
            # 列表形式：[{...}, {...}]
            return pd.DataFrame(data)
        elif isinstance(data, dict):
            # 字典形式：{"key": [...], "key2": [...]}
            # 或者嵌套结构：{"data": [{...}, {...}]}
            if 'data' in data:
                return pd.DataFrame(data['data'])
            else:
                return pd.DataFrame(data)
        else:
            raise ValueError(f"Unsupported JSON structure in '{path}'")

