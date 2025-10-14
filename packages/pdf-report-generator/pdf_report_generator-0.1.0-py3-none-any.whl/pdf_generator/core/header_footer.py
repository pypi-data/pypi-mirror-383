"""页眉页脚处理器"""

from typing import Dict, Any, Optional
from pathlib import Path
from reportlab.lib.units import inch
from reportlab.pdfgen import canvas
from reportlab.lib import colors
from datetime import datetime

from pdf_generator.utils.page_numbers import PageNumberFormatter


class HeaderFooterHandler:
    """页眉页脚处理器"""
    
    def __init__(self, config: Dict[str, Any], style_manager, context: Dict[str, Any] = None):
        """
        初始化页眉页脚处理器
        
        Args:
            config: 页面模板配置
            style_manager: 样式管理器
            context: 上下文数据（用于变量替换）
        """
        self.config = config
        self.style_manager = style_manager
        self.context = context or {}
        
        # 获取页眉页脚配置
        self.header_config = config.get('header', {})
        self.footer_config = config.get('footer', {})
        
        # 默认高度（英寸）
        self.header_height = self.header_config.get('height', 0.8) * inch
        self.footer_height = self.footer_config.get('height', 0.6) * inch
    
    def has_header(self) -> bool:
        """是否启用页眉"""
        return self.header_config.get('enabled', False)
    
    def has_footer(self) -> bool:
        """是否启用页脚"""
        return self.footer_config.get('enabled', False)
    
    def get_header_height(self) -> float:
        """获取页眉高度"""
        return self.header_height if self.has_header() else 0
    
    def get_footer_height(self) -> float:
        """获取页脚高度"""
        return self.footer_height if self.has_footer() else 0
    
    def draw_header(self, canvas_obj: canvas.Canvas, page_num: int, total_pages: int):
        """绘制页眉
        
        Args:
            canvas_obj: Canvas对象
            page_num: 当前页码
            total_pages: 总页数
        """
        if not self.has_header():
            return
        
        page_width, page_height = canvas_obj._pagesize
        y_position = page_height - self.header_height / 2
        
        # 绘制左中右三个区域
        self._draw_section(
            canvas_obj, 
            self.header_config.get('left'), 
            'left', 
            y_position, 
            page_width,
            page_num,
            total_pages
        )
        
        self._draw_section(
            canvas_obj, 
            self.header_config.get('center'), 
            'center', 
            y_position, 
            page_width,
            page_num,
            total_pages
        )
        
        self._draw_section(
            canvas_obj, 
            self.header_config.get('right'), 
            'right', 
            y_position, 
            page_width,
            page_num,
            total_pages
        )
        
        # 绘制分隔线（如果启用）
        if self.header_config.get('showLine', False):
            self._draw_line(canvas_obj, page_height - self.header_height, page_width)
    
    def draw_footer(self, canvas_obj: canvas.Canvas, page_num: int, total_pages: int):
        """绘制页脚
        
        Args:
            canvas_obj: Canvas对象
            page_num: 当前页码
            total_pages: 总页数
        """
        if not self.has_footer():
            return
        
        page_width, _ = canvas_obj._pagesize
        y_position = self.footer_height / 2
        
        # 绘制左中右三个区域
        self._draw_section(
            canvas_obj, 
            self.footer_config.get('left'), 
            'left', 
            y_position, 
            page_width,
            page_num,
            total_pages
        )
        
        self._draw_section(
            canvas_obj, 
            self.footer_config.get('center'), 
            'center', 
            y_position, 
            page_width,
            page_num,
            total_pages
        )
        
        self._draw_section(
            canvas_obj, 
            self.footer_config.get('right'), 
            'right', 
            y_position, 
            page_width,
            page_num,
            total_pages
        )
        
        # 绘制分隔线（如果启用）
        if self.footer_config.get('showLine', False):
            self._draw_line(canvas_obj, self.footer_height, page_width)
    
    def _draw_section(
        self, 
        canvas_obj: canvas.Canvas, 
        section_config: Optional[Dict[str, Any]], 
        align: str, 
        y: float, 
        page_width: float,
        page_num: int,
        total_pages: int
    ):
        """绘制一个区域（左/中/右）
        
        Args:
            canvas_obj: Canvas对象
            section_config: 区域配置
            align: 对齐方式 (left/center/right)
            y: Y坐标
            page_width: 页面宽度
            page_num: 当前页码
            total_pages: 总页数
        """
        if not section_config:
            return
        
        section_type = section_config.get('type', 'text')
        
        # 计算X坐标
        margin = 0.75 * inch
        if align == 'left':
            x = margin
        elif align == 'center':
            x = page_width / 2
        else:  # right
            x = page_width - margin
        
        if section_type == 'text':
            self._draw_text(canvas_obj, section_config, x, y, align, page_num, total_pages)
        elif section_type == 'image':
            self._draw_image(canvas_obj, section_config, x, y, align)
        elif section_type == 'pageNumber':
            self._draw_page_number(canvas_obj, section_config, x, y, align, page_num, total_pages)
    
    def _draw_text(
        self, 
        canvas_obj: canvas.Canvas, 
        config: Dict[str, Any], 
        x: float, 
        y: float, 
        align: str,
        page_num: int,
        total_pages: int
    ):
        """绘制文本"""
        content = config.get('content', '')
        
        # 变量替换
        content = self._replace_variables(content, page_num, total_pages)
        
        # 设置字体和大小
        font_name = config.get('fontName', 'SimHei')
        font_size = config.get('fontSize', 9)
        
        # 注册中文字体（如果需要）
        if 'SimHei' in self.style_manager.registered_fonts:
            font_name = 'SimHei'
        elif 'SimSun' in self.style_manager.registered_fonts:
            font_name = 'SimSun'
        
        canvas_obj.setFont(font_name, font_size)
        
        # 设置颜色
        color = config.get('color', '#000000')
        r, g, b = self._parse_color(color)
        canvas_obj.setFillColorRGB(r, g, b)
        
        # 绘制文本
        if align == 'center':
            canvas_obj.drawCentredString(x, y, content)
        elif align == 'right':
            canvas_obj.drawRightString(x, y, content)
        else:
            canvas_obj.drawString(x, y, content)
    
    def _draw_image(
        self, 
        canvas_obj: canvas.Canvas, 
        config: Dict[str, Any], 
        x: float, 
        y: float, 
        align: str
    ):
        """绘制图片"""
        path = config.get('path')
        if not path or not Path(path).exists():
            return
        
        width = config.get('width', 50)
        height = config.get('height', 30)
        
        # 根据对齐方式调整x坐标
        if align == 'center':
            x = x - width / 2
        elif align == 'right':
            x = x - width
        
        # 调整y坐标使图片居中
        y = y - height / 2
        
        try:
            canvas_obj.drawImage(path, x, y, width=width, height=height, preserveAspectRatio=True)
        except Exception as e:
            print(f"Warning: Failed to draw header/footer image: {e}")
    
    def _draw_page_number(
        self, 
        canvas_obj: canvas.Canvas, 
        config: Dict[str, Any], 
        x: float, 
        y: float, 
        align: str,
        page_num: int,
        total_pages: int
    ):
        """绘制页码"""
        format_str = config.get('format', '{page}')
        formatted = PageNumberFormatter.format_page_number(page_num, total_pages, format_str)
        
        # 使用文本绘制方式
        text_config = {
            'content': formatted,
            'fontName': config.get('fontName', 'SimHei'),
            'fontSize': config.get('fontSize', 9),
            'color': config.get('color', '#000000')
        }
        
        self._draw_text(canvas_obj, text_config, x, y, align, page_num, total_pages)
    
    def _draw_line(self, canvas_obj: canvas.Canvas, y: float, page_width: float):
        """绘制分隔线"""
        margin = 0.75 * inch
        canvas_obj.setStrokeColorRGB(0.7, 0.7, 0.7)
        canvas_obj.setLineWidth(0.5)
        canvas_obj.line(margin, y, page_width - margin, y)
    
    def _replace_variables(self, text: str, page_num: int, total_pages: int) -> str:
        """替换变量"""
        import re
        
        # 替换日期
        if '{{date}}' in text:
            text = text.replace('{{date}}', datetime.now().strftime('%Y-%m-%d'))
        
        if '{{datetime}}' in text:
            text = text.replace('{{datetime}}', datetime.now().strftime('%Y-%m-%d %H:%M'))
        
        if '{{year}}' in text:
            text = text.replace('{{year}}', str(datetime.now().year))
        
        # 替换页码
        if '{{page}}' in text:
            text = text.replace('{{page}}', str(page_num))
        
        if '{{total}}' in text:
            text = text.replace('{{total}}', str(total_pages))
        
        # 替换上下文变量（支持嵌套访问，如 {{metadata.title}}）
        pattern = r'\{\{([^}]+)\}\}'
        
        def replace_func(match):
            var_path = match.group(1).strip()
            # 分割路径（如 "metadata.title" -> ["metadata", "title"]）
            parts = var_path.split('.')
            
            # 从context中获取值
            value = self.context
            try:
                for part in parts:
                    if isinstance(value, dict):
                        value = value.get(part, '')
                    else:
                        value = getattr(value, part, '')
                        
                return str(value) if value else match.group(0)
            except:
                # 如果获取失败，返回原始占位符
                return match.group(0)
        
        text = re.sub(pattern, replace_func, text)
        
        return text
    
    def _parse_color(self, color_str: str) -> tuple:
        """解析颜色"""
        if color_str.startswith('#'):
            color_str = color_str[1:]
            r = int(color_str[0:2], 16) / 255.0
            g = int(color_str[2:4], 16) / 255.0
            b = int(color_str[4:6], 16) / 255.0
            return (r, g, b)
        return (0, 0, 0)


