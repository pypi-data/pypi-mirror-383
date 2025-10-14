"""API数据源"""

import requests
from typing import Dict, Any
import pandas as pd

from pdf_generator.data_sources.base import DataSource


class APIDataSource(DataSource):
    """从HTTP API获取数据"""
    
    def fetch(self) -> pd.DataFrame:
        """从API获取数据"""
        if 'url' not in self.config:
            raise ValueError(f"API data source '{self.name}' requires 'url' field")
        
        url = self.config['url']
        method = self.config.get('method', 'GET').upper()
        headers = self.config.get('headers', {})
        params = self.config.get('params', {})
        data = self.config.get('data', None)
        timeout = self.config.get('timeout', 30)
        
        try:
            if method == 'GET':
                response = requests.get(url, headers=headers, params=params, timeout=timeout)
            elif method == 'POST':
                response = requests.post(url, headers=headers, json=data, timeout=timeout)
            else:
                raise ValueError(f"Unsupported HTTP method: {method}")
            
            response.raise_for_status()
            json_data = response.json()
            
            # 处理响应数据
            if isinstance(json_data, list):
                return pd.DataFrame(json_data)
            elif isinstance(json_data, dict):
                # 支持指定数据路径
                data_path = self.config.get('dataPath', 'data')
                if data_path in json_data:
                    return pd.DataFrame(json_data[data_path])
                else:
                    return pd.DataFrame(json_data)
            else:
                raise ValueError(f"Unsupported API response format")
        
        except requests.exceptions.RequestException as e:
            raise RuntimeError(f"Failed to fetch data from API '{url}': {e}")

