"""数据库数据源"""

from typing import Dict, Any
import pandas as pd
from sqlalchemy import create_engine, text

from pdf_generator.data_sources.base import DataSource


class DatabaseDataSource(DataSource):
    """从数据库查询数据"""
    
    def fetch(self) -> pd.DataFrame:
        """从数据库获取数据"""
        if 'query' not in self.config:
            raise ValueError(f"Database data source '{self.name}' requires 'query' field")
        
        # 连接字符串
        connection_string = self.config.get('connectionString')
        if not connection_string:
            # 从各个参数构建连接字符串
            db_type = self.config.get('dbType', 'sqlite')
            host = self.config.get('host', 'localhost')
            port = self.config.get('port')
            database = self.config.get('database')
            username = self.config.get('username')
            password = self.config.get('password')
            
            if db_type == 'sqlite':
                connection_string = f"sqlite:///{database}"
            elif db_type == 'postgresql':
                port = port or 5432
                connection_string = f"postgresql://{username}:{password}@{host}:{port}/{database}"
            elif db_type == 'mysql':
                port = port or 3306
                connection_string = f"mysql+pymysql://{username}:{password}@{host}:{port}/{database}"
            else:
                raise ValueError(f"Unsupported database type: {db_type}")
        
        # 创建引擎并查询
        try:
            engine = create_engine(connection_string)
            query = self.config['query']
            
            # 支持查询参数
            params = self.config.get('params', {})
            
            with engine.connect() as conn:
                df = pd.read_sql(text(query), conn, params=params)
            
            return df
        
        except Exception as e:
            raise RuntimeError(f"Database query failed for '{self.name}': {e}")

