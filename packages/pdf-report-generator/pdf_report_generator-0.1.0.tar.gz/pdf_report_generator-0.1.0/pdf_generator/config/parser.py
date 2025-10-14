"""配置文件解析器"""

import json
from typing import Dict, Any, Optional
from pathlib import Path
from jinja2 import Template

from pdf_generator.config.validator import ConfigValidator


class ConfigParser:
    """解析和处理JSON配置文件"""
    
    def __init__(self, config_path: Optional[str] = None, config_dict: Optional[Dict[str, Any]] = None):
        """
        初始化配置解析器
        
        Args:
            config_path: JSON配置文件路径
            config_dict: 配置字典（直接传入配置）
        """
        self.config: Dict[str, Any] = {}
        self.validator = ConfigValidator()
        
        if config_path:
            self.load_from_file(config_path)
        elif config_dict:
            self.load_from_dict(config_dict)
    
    def load_from_file(self, config_path: str):
        """从文件加载配置"""
        path = Path(config_path)
        if not path.exists():
            raise FileNotFoundError(f"Configuration file not found: {config_path}")
        
        with open(path, 'r', encoding='utf-8') as f:
            self.config = json.load(f)
        
        self._validate_config()
    
    def load_from_dict(self, config_dict: Dict[str, Any]):
        """从字典加载配置"""
        self.config = config_dict
        self._validate_config()
    
    def _validate_config(self):
        """验证配置"""
        if not self.validator.validate(self.config):
            errors = self.validator.get_errors()
            raise ValueError(f"Configuration validation failed:\n" + "\n".join(errors))
        
        # 输出警告（如果有）
        warnings = self.validator.get_warnings()
        if warnings:
            print("Configuration warnings:")
            for warning in warnings:
                print(f"  - {warning}")
    
    def get_metadata(self) -> Dict[str, Any]:
        """获取元数据配置"""
        return self.config.get('metadata', {
            'title': 'Report',
            'author': 'PDF Generator',
            'pageSize': 'A4',
            'orientation': 'portrait',
        })
    
    def get_styles(self) -> Dict[str, Dict[str, Any]]:
        """获取样式配置"""
        return self.config.get('styles', {})
    
    def get_data_sources(self) -> list:
        """获取数据源配置"""
        return self.config.get('dataSources', [])
    
    def get_elements(self) -> list:
        """获取元素配置"""
        return self.config.get('elements', [])
    
    def render_template(self, text: str, context: Dict[str, Any]) -> str:
        """使用Jinja2渲染模板字符串
        
        Args:
            text: 包含模板变量的文本
            context: 上下文数据
        
        Returns:
            渲染后的文本
        """
        try:
            template = Template(text)
            return template.render(context)
        except Exception as e:
            print(f"Warning: Failed to render template '{text}': {e}")
            return text
    
    def process_element_content(self, element: Dict[str, Any], context: Dict[str, Any]) -> Dict[str, Any]:
        """处理元素内容，渲染模板变量
        
        Args:
            element: 元素配置
            context: 上下文数据（包括metadata、dataSources等）
        
        Returns:
            处理后的元素配置
        """
        processed = element.copy()
        
        # 渲染文本内容
        if 'content' in processed and isinstance(processed['content'], str):
            processed['content'] = self.render_template(processed['content'], context)
        
        # 渲染标题
        if 'title' in processed and isinstance(processed['title'], str):
            processed['title'] = self.render_template(processed['title'], context)
        
        return processed
    
    def get_full_config(self) -> Dict[str, Any]:
        """获取完整配置"""
        return self.config

