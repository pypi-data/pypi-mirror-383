"""CSV/Excel数据源"""

from pathlib import Path
import pandas as pd

from pdf_generator.data_sources.base import DataSource


class CSVDataSource(DataSource):
    """从CSV或Excel文件加载数据"""
    
    def fetch(self) -> pd.DataFrame:
        """从CSV/Excel获取数据"""
        if 'path' not in self.config:
            raise ValueError(f"CSV/Excel data source '{self.name}' requires 'path' field")
        
        path = Path(self.config['path'])
        if not path.exists():
            raise FileNotFoundError(f"File not found: {path}")
        
        file_type = self.config.get('fileType', path.suffix.lower())
        
        # 读取参数
        encoding = self.config.get('encoding', 'utf-8')
        sheet_name = self.config.get('sheetName', 0)  # Excel专用
        delimiter = self.config.get('delimiter', ',')  # CSV专用
        
        if file_type in ['.csv', 'csv']:
            return pd.read_csv(path, encoding=encoding, delimiter=delimiter)
        elif file_type in ['.xlsx', '.xls', 'excel']:
            return pd.read_excel(path, sheet_name=sheet_name)
        else:
            # 尝试根据扩展名自动判断
            if path.suffix in ['.xlsx', '.xls']:
                return pd.read_excel(path, sheet_name=sheet_name)
            else:
                return pd.read_csv(path, encoding=encoding, delimiter=delimiter)

