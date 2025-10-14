"""页面模板和自定义Canvas"""

from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import A4
from typing import Optional, Dict, Any

from pdf_generator.core.header_footer import HeaderFooterHandler


class NumberedCanvas(canvas.Canvas):
    """带页码的自定义Canvas"""
    
    def __init__(self, *args, **kwargs):
        # 提取自定义参数
        self.header_footer_handler: Optional[HeaderFooterHandler] = kwargs.pop('header_footer_handler', None)
        
        canvas.Canvas.__init__(self, *args, **kwargs)
        self._saved_page_states = []
    
    def showPage(self):
        """保存页面状态"""
        self._saved_page_states.append(dict(self.__dict__))
        self._startPage()
    
    def save(self):
        """添加页眉页脚并保存"""
        num_pages = len(self._saved_page_states)
        
        for page_num, state in enumerate(self._saved_page_states, start=1):
            self.__dict__.update(state)
            
            # 绘制页眉页脚
            if self.header_footer_handler:
                self.header_footer_handler.draw_header(self, page_num, num_pages)
                self.header_footer_handler.draw_footer(self, page_num, num_pages)
            
            canvas.Canvas.showPage(self)
        
        canvas.Canvas.save(self)


class PageTemplateManager:
    """页面模板管理器"""
    
    def __init__(self, config: Dict[str, Any], style_manager, context: Dict[str, Any] = None):
        """
        初始化页面模板管理器
        
        Args:
            config: 页面模板配置
            style_manager: 样式管理器
            context: 上下文数据
        """
        self.config = config
        self.style_manager = style_manager
        self.context = context or {}
        
        # 创建页眉页脚处理器
        self.header_footer_handler = None
        if config:
            self.header_footer_handler = HeaderFooterHandler(config, style_manager, context)
    
    def create_canvas(self, filename, pagesize=A4):
        """创建自定义Canvas
        
        Args:
            filename: 输出文件名或字节流
            pagesize: 页面大小
        
        Returns:
            NumberedCanvas对象
        """
        return NumberedCanvas(
            filename,
            pagesize=pagesize,
            header_footer_handler=self.header_footer_handler
        )
    
    def get_content_margins(self, page_height: float) -> Dict[str, float]:
        """获取内容区域的最小边距要求
        
        考虑页眉页脚占用的空间，返回建议的最小边距
        
        Args:
            page_height: 页面高度
        
        Returns:
            包含top和bottom最小边距的字典
        """
        margins = {}
        
        if self.header_footer_handler:
            # 页眉占用空间 + 额外间距（建议的最小上边距）
            header_space = self.header_footer_handler.get_header_height()
            if header_space > 0:
                # 页眉高度 + 20点缓冲空间
                margins['top'] = header_space + 20
            
            # 页脚占用空间 + 额外间距（建议的最小下边距）
            footer_space = self.header_footer_handler.get_footer_height()
            if footer_space > 0:
                # 页脚高度 + 20点缓冲空间
                margins['bottom'] = footer_space + 20
        
        return margins

