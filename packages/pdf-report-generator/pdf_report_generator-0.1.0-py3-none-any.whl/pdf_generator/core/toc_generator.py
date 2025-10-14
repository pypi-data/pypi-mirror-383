"""目录（TOC）生成器"""

from typing import Dict, Any, List, Optional
from reportlab.platypus import Paragraph, PageBreak, Spacer
from reportlab.platypus.tableofcontents import TableOfContents
from reportlab.lib.styles import ParagraphStyle
from reportlab.lib.units import inch
from reportlab.lib.enums import TA_LEFT, TA_RIGHT


class HeadingParagraph(Paragraph):
    """带目录通知功能的标题段落"""
    
    def __init__(self, text, style, key=None, level=0, toc_notify_func=None):
        Paragraph.__init__(self, text, style)
        self.key = key
        self.level = level
        self.toc_notify_func = toc_notify_func
        # 保存纯文本用于TOC
        self.heading_text = text
    
    def draw(self):
        # 绘制段落
        Paragraph.draw(self)
        
        # 如果有key，添加书签
        if self.key:
            # 添加书签
            self.canv.bookmarkPage(self.key)
            # 添加PDF大纲条目
            self.canv.addOutlineEntry(
                self.heading_text,
                self.key,
                self.level,
                0
            )
            
            # 通知TableOfContents
            # multiBuild机制会自动将这个通知转发给所有注册的TableOfContents对象
            if hasattr(self.canv, '_doctemplate') and self.canv._doctemplate:
                self.canv._doctemplate.notify('TOCEntry', (self.level, self.heading_text, self.canv.getPageNumber(), self.key))


class TOCEntry:
    """目录条目"""
    
    def __init__(self, level: int, title: str, page_num: int = 0, key: str = None):
        self.level = level
        self.title = title
        self.page_num = page_num
        self.key = key or f"toc_{id(self)}"


class EnhancedTableOfContents(TableOfContents):
    """增强的目录类"""
    
    def __init__(self, config: Dict[str, Any], style_manager):
        """
        初始化目录
        
        Args:
            config: TOC配置
            style_manager: 样式管理器
        """
        TableOfContents.__init__(self)
        
        self.config = config
        self.style_manager = style_manager
        self.max_level = config.get('maxLevel', 3)
        
        # 设置目录样式
        self._setup_level_styles()
    
    def notify(self, kind, stuff):
        """接收来自文档的通知
        
        Args:
            kind: 通知类型 ('TOCEntry')
            stuff: 通知数据 (level, text, pageNum, key)
        """
        if kind == 'TOCEntry':
            level, text, pageNum, key = stuff
            self.addEntry(level, text, pageNum, key)
    
    def _setup_level_styles(self):
        """设置各级目录样式"""
        self.levelStyles = []
        
        # 确定使用的字体
        font_name = 'Helvetica'  # 默认字体
        if 'SimHei' in self.style_manager.registered_fonts:
            font_name = 'SimHei'
        elif 'SimSun' in self.style_manager.registered_fonts:
            font_name = 'SimSun'
        
        # 为每个级别创建样式
        for level in range(self.max_level):
            indent = level * 20  # 每级缩进20点
            
            style = ParagraphStyle(
                name=f'TOCLevel{level}',
                fontName=font_name,
                fontSize=12 - level,  # 级别越高字号越小
                leftIndent=indent,
                firstLineIndent=0,
                spaceBefore=3,
                spaceAfter=3,
                leading=14 - level,
            )
            
            self.levelStyles.append(style)


class TOCGenerator:
    """目录生成器"""
    
    def __init__(self, config: Dict[str, Any], style_manager):
        """
        初始化目录生成器
        
        Args:
            config: TOC配置
            style_manager: 样式管理器
        """
        self.config = config
        self.style_manager = style_manager
        self.entries: List[TOCEntry] = []
    
    def is_enabled(self) -> bool:
        """是否启用目录"""
        return self.config.get('enabled', False)
    
    def is_auto_generate(self) -> bool:
        """是否自动生成目录"""
        return self.config.get('autoGenerate', True)
    
    def add_entry(self, level: int, title: str, key: str = None):
        """添加目录条目
        
        Args:
            level: 标题级别 (1, 2, 3...)
            title: 标题文本
            key: 唯一标识符
        """
        entry = TOCEntry(level, title, key=key)
        self.entries.append(entry)
    
    def generate_toc_elements(self) -> List:
        """生成目录元素
        
        Returns:
            包含目录标题、目录和分页符的元素列表
        """
        if not self.is_enabled():
            return []
        
        elements = []
        
        # 添加目录标题
        title = self.config.get('title', '目录')
        title_style = self.style_manager.get_style('Heading1')
        elements.append(Paragraph(title, title_style))
        elements.append(Spacer(1, 0.2 * inch))
        
        # 添加目录
        if self.is_auto_generate():
            # 使用自动生成的目录
            toc = EnhancedTableOfContents(self.config, self.style_manager)
            elements.append(toc)
        else:
            # 使用手动配置的条目
            manual_entries = self.config.get('entries', [])
            for entry_config in manual_entries:
                level = entry_config.get('level', 1)
                title = entry_config.get('title', '')
                page_num = entry_config.get('pageNum', 0)
                
                # 创建目录条目段落
                entry_para = self._create_toc_entry_paragraph(level, title, page_num)
                elements.append(entry_para)
        
        # 添加分页符
        elements.append(PageBreak())
        
        return elements
    
    def _create_toc_entry_paragraph(self, level: int, title: str, page_num: int) -> Paragraph:
        """创建目录条目段落
        
        Args:
            level: 级别
            title: 标题
            page_num: 页码
        
        Returns:
            Paragraph对象
        """
        # 计算缩进
        indent = (level - 1) * 20
        
        # 确定使用的字体
        font_name = 'Helvetica'  # 默认字体
        if 'SimSun' in self.style_manager.registered_fonts:
            font_name = 'SimSun'
        elif 'SimHei' in self.style_manager.registered_fonts:
            font_name = 'SimHei'
        
        # 创建样式
        style = ParagraphStyle(
            name=f'TOCEntry{level}',
            fontName=font_name,
            fontSize=11 - level,
            leftIndent=indent,
            spaceBefore=2,
            spaceAfter=2,
        )
        
        # 创建带点线的条目
        dots = '.' * 50
        text = f'{title} <font color="gray">{dots}</font> {page_num}'
        
        return Paragraph(text, style)
    
    def create_heading_with_bookmark(
        self, 
        text: str, 
        level: int, 
        style_name: str = None
    ) -> Paragraph:
        """创建带书签的标题
        
        Args:
            text: 标题文本
            level: 标题级别 (1, 2, 3...)
            style_name: 样式名称
        
        Returns:
            带书签的Paragraph对象
        """
        # 默认样式
        if not style_name:
            style_name = f'Heading{level}'
        
        style = self.style_manager.get_style(style_name)
        
        # 生成唯一key
        key = f"heading_{len(self.entries)}_{id(text)}"
        
        # 添加到目录
        if self.is_auto_generate():
            self.add_entry(level, text, key)
        
        # 创建使用HeadingParagraph而不是普通Paragraph
        # HeadingParagraph会在绘制时自动添加书签
        para = HeadingParagraph(text, style, key=key, level=level-1)
        
        return para


class BookmarkHelper:
    """书签辅助工具"""
    
    @staticmethod
    def create_bookmark(key: str, text: str) -> str:
        """创建书签标记
        
        Args:
            key: 书签唯一标识
            text: 显示文本
        
        Returns:
            带书签的HTML文本
        """
        return f'<a name="{key}"/>{text}'
    
    @staticmethod
    def create_link(key: str, text: str) -> str:
        """创建跳转链接
        
        Args:
            key: 目标书签标识
            text: 链接文本
        
        Returns:
            带链接的HTML文本
        """
        return f'<a href="#{key}" color="blue">{text}</a>'

