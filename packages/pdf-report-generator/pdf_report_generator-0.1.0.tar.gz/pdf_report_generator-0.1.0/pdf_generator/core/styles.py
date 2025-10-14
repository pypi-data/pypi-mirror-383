"""PDF样式管理器"""

from typing import Dict, Any, Optional
from pathlib import Path
from reportlab.lib import colors
from reportlab.lib.styles import ParagraphStyle, getSampleStyleSheet
from reportlab.lib.enums import TA_LEFT, TA_CENTER, TA_RIGHT, TA_JUSTIFY
from reportlab.lib.units import inch
from reportlab.platypus import TableStyle
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont


class StyleManager:
    """管理PDF文档的样式"""
    
    def __init__(self, font_dirs: Optional[list] = None):
        """
        初始化样式管理器
        
        Args:
            font_dirs: 字体目录列表，会按顺序查找字体文件
                      如果不提供，会尝试查找常见位置
        """
        self.styles = getSampleStyleSheet()
        self.custom_styles: Dict[str, ParagraphStyle] = {}
        self.table_styles: Dict[str, TableStyle] = {}
        self.registered_fonts = set()
        
        # 自动注册中文字体
        self._register_chinese_fonts(font_dirs)
    
    def _get_font_search_paths(self, custom_dirs: Optional[list] = None) -> list:
        """
        获取字体搜索路径
        
        Args:
            custom_dirs: 用户自定义的字体目录列表
            
        Returns:
            字体搜索路径列表
        """
        paths = []
        
        # 1. 用户指定的目录（优先级最高）
        if custom_dirs:
            for d in custom_dirs:
                path = Path(d)
                if path.exists() and path.is_dir():
                    paths.append(path)
        
        # 2. 当前工作目录下的 fonts 目录
        cwd_fonts = Path.cwd() / "fonts"
        if cwd_fonts.exists() and cwd_fonts.is_dir():
            paths.append(cwd_fonts)
        
        # 3. 用户主目录下的 .fonts 或 fonts
        home = Path.home()
        for font_dir_name in ['.fonts', 'fonts', '.local/share/fonts']:
            home_fonts = home / font_dir_name
            if home_fonts.exists() and home_fonts.is_dir():
                paths.append(home_fonts)
        
        return paths
    
    def _register_chinese_fonts(self, font_dirs: Optional[list] = None):
        """
        自动注册中文字体
        
        Args:
            font_dirs: 字体目录列表
        """
        # 获取字体搜索路径
        search_paths = self._get_font_search_paths(font_dirs)
        
        if not search_paths:
            # print("Info: No font directories found. Using system default fonts.")
            return
        
        # 定义字体映射
        font_mappings = {
            'SimSun': ['SimSun.ttf', 'SimSun.TTF', 'simsun.ttf', 'simsun.ttc'],
            'SimHei': ['SimHei.ttf', 'SimHei.TTF', 'simhei.ttf', 'simhei.ttc'],
            'GB2312': ['GB2312.ttf', 'GB2312.TTF', 'gb2312.ttf'],
        }
        
        # 在所有搜索路径中查找并注册字体
        for font_name, font_files in font_mappings.items():
            if font_name in self.registered_fonts:
                continue
                
            for search_path in search_paths:
                for font_file in font_files:
                    font_path = search_path / font_file
                    if font_path.exists():
                        try:
                            pdfmetrics.registerFont(TTFont(font_name, str(font_path)))
                            self.registered_fonts.add(font_name)
                            # print(f"Info: Registered font '{font_name}' from {font_path}")
                            break
                        except Exception as e:
                            pass  # 静默失败，继续尝试其他路径
                
                if font_name in self.registered_fonts:
                    break
        
        # 如果成功注册了字体，设置默认字体
        if self.registered_fonts:
            # 优先使用SimHei（黑体），其次SimSun（宋体）
            default_font = 'SimHei' if 'SimHei' in self.registered_fonts else (
                'SimSun' if 'SimSun' in self.registered_fonts else 
                next(iter(self.registered_fonts))
            )
            # print(f"Info: Default Chinese font set to '{default_font}'")
            
            # 更新默认样式使用中文字体
            for style_name in ['Normal', 'BodyText', 'Title', 'Heading1', 'Heading2']:
                if style_name in self.styles:
                    self.styles[style_name].fontName = default_font
    
    def register_font(self, font_name: str, font_path: str):
        """手动注册字体
        
        Args:
            font_name: 字体名称
            font_path: 字体文件路径
        """
        try:
            pdfmetrics.registerFont(TTFont(font_name, font_path))
            self.registered_fonts.add(font_name)
            print(f"Font '{font_name}' registered successfully")
        except Exception as e:
            print(f"Error registering font '{font_name}': {e}")
        
    def _parse_color(self, color_str: str) -> colors.Color:
        """解析颜色字符串（支持#RRGGBB格式）"""
        if color_str.startswith('#'):
            color_str = color_str[1:]
            r = int(color_str[0:2], 16) / 255.0
            g = int(color_str[2:4], 16) / 255.0
            b = int(color_str[4:6], 16) / 255.0
            return colors.Color(r, g, b)
        return colors.black
    
    def _parse_alignment(self, alignment: str) -> int:
        """解析对齐方式"""
        alignment_map = {
            'left': TA_LEFT,
            'center': TA_CENTER,
            'right': TA_RIGHT,
            'justify': TA_JUSTIFY,
        }
        return alignment_map.get(alignment.lower(), TA_LEFT)
    
    def create_paragraph_style(self, name: str, config: Dict[str, Any]) -> ParagraphStyle:
        """根据配置创建段落样式
        
        Args:
            name: 样式名称
            config: 样式配置字典，支持的键：
                - fontSize: 字体大小
                - textColor: 文本颜色（#RRGGBB格式）
                - alignment: 对齐方式（left/center/right/justify）
                - fontName: 字体名称
                - leading: 行间距
                - spaceBefore: 段前间距
                - spaceAfter: 段后间距
                - leftIndent: 左缩进
                - rightIndent: 右缩进
                - bold: 是否加粗
        """
        base_style = self.styles['Normal']
        
        style_kwargs = {
            'name': name,
            'parent': base_style,
        }
        
        if 'fontSize' in config:
            style_kwargs['fontSize'] = config['fontSize']
            style_kwargs['leading'] = config.get('leading', config['fontSize'] * 1.2)
        
        if 'textColor' in config:
            style_kwargs['textColor'] = self._parse_color(config['textColor'])
        
        if 'alignment' in config:
            style_kwargs['alignment'] = self._parse_alignment(config['alignment'])
        
        if 'fontName' in config:
            style_kwargs['fontName'] = config['fontName']
        elif config.get('bold'):
            # 如果有中文字体，优先使用中文字体
            if 'SimHei' in self.registered_fonts:
                style_kwargs['fontName'] = 'SimHei'
            elif 'SimSun' in self.registered_fonts:
                style_kwargs['fontName'] = 'SimSun'
            elif self.registered_fonts:
                style_kwargs['fontName'] = next(iter(self.registered_fonts))
            else:
                style_kwargs['fontName'] = 'Helvetica-Bold'
        elif not style_kwargs.get('fontName'):
            # 设置默认中文字体
            if 'SimHei' in self.registered_fonts:
                style_kwargs['fontName'] = 'SimHei'
            elif 'SimSun' in self.registered_fonts:
                style_kwargs['fontName'] = 'SimSun'
            elif self.registered_fonts:
                style_kwargs['fontName'] = next(iter(self.registered_fonts))
        
        if 'spaceBefore' in config:
            style_kwargs['spaceBefore'] = config['spaceBefore']
        
        if 'spaceAfter' in config:
            style_kwargs['spaceAfter'] = config['spaceAfter']
        
        if 'leftIndent' in config:
            style_kwargs['leftIndent'] = config['leftIndent']
        
        if 'rightIndent' in config:
            style_kwargs['rightIndent'] = config['rightIndent']
        
        style = ParagraphStyle(**style_kwargs)
        self.custom_styles[name] = style
        return style
    
    def get_style(self, name: str) -> Optional[ParagraphStyle]:
        """获取样式"""
        if name in self.custom_styles:
            return self.custom_styles[name]
        if name in self.styles:
            return self.styles[name]
        return self.styles['Normal']
    
    def create_table_style(self, name: str, config: Dict[str, Any]) -> TableStyle:
        """创建表格样式
        
        Args:
            name: 样式名称
            config: 样式配置字典，支持的键：
                - headerBackground: 表头背景色
                - headerTextColor: 表头文字颜色
                - gridColor: 网格线颜色
                - gridWidth: 网格线宽度
                - rowBackground: 行背景色（可以是单一颜色或交替颜色列表）
                - fontSize: 字体大小
                - padding: 单元格内边距
        """
        commands = []
        
        # 基础网格
        grid_color = self._parse_color(config.get('gridColor', '#CCCCCC'))
        grid_width = config.get('gridWidth', 0.5)
        commands.append(('GRID', (0, 0), (-1, -1), grid_width, grid_color))
        
        # 表头样式
        if 'headerBackground' in config:
            header_bg = self._parse_color(config['headerBackground'])
            commands.append(('BACKGROUND', (0, 0), (-1, 0), header_bg))
        
        if 'headerTextColor' in config:
            header_text = self._parse_color(config['headerTextColor'])
            commands.append(('TEXTCOLOR', (0, 0), (-1, 0), header_text))
        
        # 表头加粗 - 使用中文字体
        header_font = 'SimHei' if 'SimHei' in self.registered_fonts else (
            'SimSun' if 'SimSun' in self.registered_fonts else (
                next(iter(self.registered_fonts)) if self.registered_fonts else 'Helvetica-Bold'
            )
        )
        commands.append(('FONTNAME', (0, 0), (-1, 0), header_font))
        
        # 表格内容字体
        content_font = 'SimSun' if 'SimSun' in self.registered_fonts else (
            'SimHei' if 'SimHei' in self.registered_fonts else (
                next(iter(self.registered_fonts)) if self.registered_fonts else 'Helvetica'
            )
        )
        commands.append(('FONTNAME', (0, 1), (-1, -1), content_font))
        
        # 行背景色
        if 'rowBackground' in config:
            row_bg = config['rowBackground']
            if isinstance(row_bg, list):
                # 交替行颜色
                for i, color in enumerate(row_bg):
                    bg_color = self._parse_color(color)
                    commands.append(('BACKGROUND', (0, i+1), (-1, i+1), bg_color))
            else:
                bg_color = self._parse_color(row_bg)
                commands.append(('BACKGROUND', (0, 1), (-1, -1), bg_color))
        
        # 字体大小
        if 'fontSize' in config:
            commands.append(('FONTSIZE', (0, 0), (-1, -1), config['fontSize']))
        
        # 内边距
        padding = config.get('padding', 6)
        commands.append(('LEFTPADDING', (0, 0), (-1, -1), padding))
        commands.append(('RIGHTPADDING', (0, 0), (-1, -1), padding))
        commands.append(('TOPPADDING', (0, 0), (-1, -1), padding))
        commands.append(('BOTTOMPADDING', (0, 0), (-1, -1), padding))
        
        # 垂直居中
        commands.append(('VALIGN', (0, 0), (-1, -1), 'MIDDLE'))
        
        table_style = TableStyle(commands)
        self.table_styles[name] = table_style
        return table_style
    
    def get_table_style(self, name: str) -> Optional[TableStyle]:
        """获取表格样式"""
        if name in self.table_styles:
            return self.table_styles[name]
        return None
    
    def load_styles_from_config(self, styles_config: Dict[str, Dict[str, Any]]):
        """从配置字典加载所有样式"""
        for style_name, style_config in styles_config.items():
            if 'gridColor' in style_config or 'headerBackground' in style_config:
                # 表格样式
                self.create_table_style(style_name, style_config)
            else:
                # 段落样式
                self.create_paragraph_style(style_name, style_config)

