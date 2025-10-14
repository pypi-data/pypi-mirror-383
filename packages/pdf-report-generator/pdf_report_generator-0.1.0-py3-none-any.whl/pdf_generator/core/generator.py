"""PDF报告生成器主引擎"""

from typing import Dict, Any, Optional, Union, BinaryIO
from pathlib import Path
import io

from reportlab.lib.pagesizes import A4, A3, A5, LETTER, LEGAL, landscape
from reportlab.platypus import SimpleDocTemplate, Paragraph, BaseDocTemplate, PageTemplate, Frame
from reportlab.lib.units import inch
import pandas as pd

from pdf_generator.config.parser import ConfigParser
from pdf_generator.core.styles import StyleManager
from pdf_generator.core.elements import ElementFactory
from pdf_generator.data_sources.base import DataSource
from pdf_generator.data_sources.json_source import JSONDataSource
from pdf_generator.data_sources.csv_source import CSVDataSource
from pdf_generator.data_sources.api_source import APIDataSource
from pdf_generator.data_sources.database import DatabaseDataSource
from pdf_generator.core.page_template import PageTemplateManager, NumberedCanvas
from pdf_generator.core.toc_generator import TOCGenerator
from pdf_generator.core.cover_page import CoverPageGenerator


class PDFReportGenerator:
    """PDF报告生成器主类"""
    
    PAGE_SIZES = {
        'A4': A4,
        'A3': A3,
        'A5': A5,
        'LETTER': LETTER,
        'LEGAL': LEGAL,
    }
    
    def __init__(
        self,
        config_path: Optional[str] = None,
        config_dict: Optional[Dict[str, Any]] = None,
        font_dirs: Optional[list] = None
    ):
        """
        初始化PDF生成器
        
        Args:
            config_path: JSON配置文件路径
            config_dict: 配置字典（直接传入）
            font_dirs: 字体文件目录列表，用于查找中文字体
                      示例: ['/path/to/fonts', 'C:\\Windows\\Fonts']
                      如果不提供，会自动在以下位置查找：
                      1. 当前工作目录下的 fonts 目录
                      2. 用户主目录下的 .fonts 或 fonts 目录
        """
        # 解析配置
        self.config_parser = ConfigParser(config_path, config_dict)
        
        # 从配置中获取字体目录（如果有的话）
        metadata = self.config_parser.get_metadata()
        config_font_dirs = metadata.get('fontDirs') if metadata else None
        
        # 合并字体目录：参数优先，然后是配置文件
        all_font_dirs = []
        if font_dirs:
            all_font_dirs.extend(font_dirs)
        if config_font_dirs:
            if isinstance(config_font_dirs, str):
                all_font_dirs.append(config_font_dirs)
            elif isinstance(config_font_dirs, list):
                all_font_dirs.extend(config_font_dirs)
        
        # 初始化组件
        self.style_manager = StyleManager(font_dirs=all_font_dirs if all_font_dirs else None)
        self.element_factory = ElementFactory(self.style_manager)
        
        # 数据源
        self.data_sources: Dict[str, pd.DataFrame] = {}
        self.data_source_objects: Dict[str, DataSource] = {}
        
        # 加载样式
        styles_config = self.config_parser.get_styles()
        if styles_config:
            self.style_manager.load_styles_from_config(styles_config)
        
        # 加载数据源
        self._load_data_sources()
        
        # 初始化高级功能组件
        metadata = self.config_parser.get_metadata()
        
        # 页面模板管理器（页眉页脚）
        page_template_config = self.config_parser.config.get('pageTemplate')
        # 准备上下文：包含metadata和其他变量
        template_context = {
            'metadata': metadata,
            'dataSources': self.data_sources
        }
        self.page_template_manager = PageTemplateManager(
            page_template_config, 
            self.style_manager,
            template_context
        ) if page_template_config else None
        
        # 目录生成器
        toc_config = self.config_parser.config.get('toc', {})
        self.toc_generator = TOCGenerator(toc_config, self.style_manager)
        
        # 封面生成器
        cover_config = self.config_parser.config.get('coverPage', {})
        self.cover_generator = CoverPageGenerator(cover_config, self.style_manager, self.config_parser)
    
    def _load_data_sources(self):
        """从配置加载数据源"""
        data_sources_config = self.config_parser.get_data_sources()
        
        for ds_config in data_sources_config:
            name = ds_config['name']
            ds_type = ds_config['type']
            
            # 创建数据源对象
            if ds_type in ['json', 'inline']:
                data_source = JSONDataSource(ds_config)
            elif ds_type in ['csv', 'excel']:
                data_source = CSVDataSource(ds_config)
            elif ds_type == 'api':
                data_source = APIDataSource(ds_config)
            elif ds_type == 'database':
                data_source = DatabaseDataSource(ds_config)
            else:
                print(f"Warning: Unsupported data source type '{ds_type}' for '{name}'")
                continue
            
            self.data_source_objects[name] = data_source
            
            # 预加载数据
            try:
                self.data_sources[name] = data_source.get_data()
                print(f"Loaded data source '{name}': {len(self.data_sources[name])} rows")
            except Exception as e:
                print(f"Warning: Failed to load data source '{name}': {e}")
    
    def add_data_source(self, name: str, data: Union[pd.DataFrame, dict, list]):
        """手动添加数据源
        
        Args:
            name: 数据源名称
            data: 数据（DataFrame、字典或列表）
        """
        if isinstance(data, pd.DataFrame):
            self.data_sources[name] = data
        elif isinstance(data, (dict, list)):
            self.data_sources[name] = pd.DataFrame(data)
        else:
            raise ValueError(f"Unsupported data type: {type(data)}")
    
    def _get_page_size(self):
        """获取页面大小"""
        metadata = self.config_parser.get_metadata()
        page_size_name = metadata.get('pageSize', 'A4')
        orientation = metadata.get('orientation', 'portrait')
        
        page_size = self.PAGE_SIZES.get(page_size_name, A4)
        
        if orientation == 'landscape':
            page_size = landscape(page_size)
        
        return page_size
    
    def _build_story(self, page_size: tuple) -> list:
        """构建PDF内容流
        
        Args:
            page_size: 页面大小 (width, height)
        """
        story = []
        
        # 准备模板上下文
        metadata = self.config_parser.get_metadata()
        context = {
            'metadata': metadata,
            'dataSources': self.data_sources,
        }
        
        # 1. 添加封面页（如果启用）
        if self.cover_generator and self.cover_generator.is_enabled():
            cover_elements = self.cover_generator.generate(page_size, context)
            story.extend(cover_elements)
        
        # 2. 添加目录（如果启用）
        if self.toc_generator and self.toc_generator.is_enabled():
            toc_elements = self.toc_generator.generate_toc_elements()
            story.extend(toc_elements)
        
        # 3. 获取元素配置
        elements_config = self.config_parser.get_elements()
        
        # 4. 生成每个元素
        for element_config in elements_config:
            try:
                # 处理模板变量
                processed_config = self.config_parser.process_element_content(
                    element_config, context
                )
                
                # 创建PDF元素
                element_type = processed_config['type']
                
                # 特殊处理：如果是heading且启用了TOC自动生成
                if element_type == 'heading' and self.toc_generator and self.toc_generator.is_auto_generate():
                    level = processed_config.get('level', 1)
                    text = processed_config.get('text', '')
                    style_name = processed_config.get('style', f'Heading{level}')
                    
                    # 使用TOC生成器创建带书签的标题
                    pdf_element = self.toc_generator.create_heading_with_bookmark(
                        text, level, style_name
                    )
                else:
                    # 普通元素
                    pdf_element = self.element_factory.create_element(
                        element_type,
                        processed_config,
                        self.data_sources
                    )
                
                story.append(pdf_element)
            
            except Exception as e:
                # 错误处理：添加错误信息到PDF
                error_text = f"Error creating element: {e}"
                print(f"Warning: {error_text}")
                error_para = Paragraph(
                    f"<font color='red'>{error_text}</font>",
                    self.style_manager.get_style('Normal')
                )
                story.append(error_para)
        
        return story
    
    def generate(
        self,
        output_path: Optional[str] = None,
        return_bytes: bool = False
    ) -> Optional[bytes]:
        """生成PDF报告
        
        Args:
            output_path: 输出文件路径（可选）
            return_bytes: 是否返回PDF字节流
        
        Returns:
            如果return_bytes为True，返回PDF字节流；否则返回None
        """
        # 获取元数据
        metadata = self.config_parser.get_metadata()
        
        # 创建PDF文档
        if output_path:
            output = output_path
        else:
            output = io.BytesIO()
        
        page_size = self._get_page_size()
        
        # 页边距
        margin = metadata.get('margin', 1) * inch
        top_margin = metadata.get('topMargin', margin)
        bottom_margin = metadata.get('bottomMargin', margin)
        left_margin = metadata.get('leftMargin', margin)
        right_margin = metadata.get('rightMargin', margin)
        
        # 如果有页眉页脚，确保边距足够容纳它们
        if self.page_template_manager:
            margins = self.page_template_manager.get_content_margins(page_size[1])
            if 'top' in margins:
                # 确保上边距至少等于建议的最小值
                top_margin = max(top_margin, margins['top'])
            if 'bottom' in margins:
                # 确保下边距至少等于建议的最小值
                bottom_margin = max(bottom_margin, margins['bottom'])
        
        # 使用带页眉页脚的自定义Canvas
        if self.page_template_manager:
            # 使用BaseDocTemplate + 自定义Canvas
            doc = BaseDocTemplate(
                output,
                pagesize=page_size,
                topMargin=top_margin,
                bottomMargin=bottom_margin,
                leftMargin=left_margin,
                rightMargin=right_margin,
                title=metadata.get('title', 'Report'),
                author=metadata.get('author', 'PDF Generator'),
            )
            
            # 创建Frame
            frame = Frame(
                left_margin,
                bottom_margin,
                page_size[0] - left_margin - right_margin,
                page_size[1] - top_margin - bottom_margin,
                id='normal'
            )
            
            # 创建PageTemplate
            template = PageTemplate(id='main', frames=[frame])
            doc.addPageTemplates([template])
            
            # 构建内容
            story = self._build_story(page_size)
            
            # 使用自定义Canvas生成PDF
            # 如果有目录，使用multiBuild进行两次构建
            page_mgr = self.page_template_manager  # 保存引用避免类型检查错误
            if self.toc_generator and self.toc_generator.is_enabled() and self.toc_generator.is_auto_generate():
                doc.multiBuild(
                    story,
                    canvasmaker=lambda *args, **kwargs: page_mgr.create_canvas(
                        args[0], 
                        page_size
                    )
                )
            else:
                doc.build(
                    story,
                    canvasmaker=lambda *args, **kwargs: page_mgr.create_canvas(
                        args[0], 
                        page_size
                    )
                )
        else:
            # 使用简单模板
            doc = SimpleDocTemplate(
                output,
                pagesize=page_size,
                topMargin=top_margin,
                bottomMargin=bottom_margin,
                leftMargin=left_margin,
                rightMargin=right_margin,
                title=metadata.get('title', 'Report'),
                author=metadata.get('author', 'PDF Generator'),
            )
            
            # 构建内容
            story = self._build_story(page_size)
            
            # 生成PDF
            # 如果有目录，使用multiBuild进行两次构建
            if self.toc_generator and self.toc_generator.is_enabled() and self.toc_generator.is_auto_generate():
                doc.multiBuild(story)
            else:
                doc.build(story)
        
        # 返回结果
        if return_bytes:
            if isinstance(output, io.BytesIO):
                return output.getvalue()
            elif output_path:
                with open(output_path, 'rb') as f:
                    return f.read()
            else:
                raise ValueError("Cannot return bytes without output")
        elif output_path:
            print(f"PDF generated successfully: {output_path}")
            return None
        else:
            # 如果既没有指定路径，也没有要求返回字节流，使用默认路径
            default_path = "output.pdf"
            if isinstance(output, io.BytesIO):
                with open(default_path, 'wb') as f:
                    f.write(output.getvalue())
                print(f"PDF generated successfully: {default_path}")
            return None
    
    def save(self, output_path: str):
        """保存PDF到指定路径
        
        Args:
            output_path: 输出文件路径
        """
        self.generate(output_path=output_path)
    
    def to_bytes(self) -> bytes:
        """生成PDF并返回字节流
        
        Returns:
            PDF字节流
        """
        result = self.generate(return_bytes=True)
        if result is None:
            raise ValueError("Failed to generate PDF bytes")
        return result
    
    def get_data_source_summary(self) -> Dict[str, Any]:
        """获取所有数据源的摘要信息"""
        summary = {}
        for name, ds in self.data_source_objects.items():
            summary[name] = ds.get_summary()
        return summary

