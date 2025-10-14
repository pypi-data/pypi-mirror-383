"""封面页处理器"""

from typing import Dict, Any, List
from pathlib import Path
from reportlab.platypus import PageBreak, Spacer
from reportlab.platypus.flowables import Flowable
from reportlab.lib.units import inch
from reportlab.lib import colors
from PIL import Image as PILImage


class CoverPageElement(Flowable):
    """封面页元素基类"""
    
    def __init__(self, width, height):
        Flowable.__init__(self)
        self.width = width
        self.height = height


class CoverBackground(CoverPageElement):
    """封面背景"""
    
    def __init__(self, width, height, config: Dict[str, Any]):
        super().__init__(width, height)
        self.config = config
        self.bg_type = config.get('type', 'color')
    
    def wrap(self, aW, aH):
        """占用极小空间，背景将使用绝对定位绘制"""
        return (0, 1)
    
    def draw(self):
        """绘制背景"""
        if self.bg_type == 'color':
            self._draw_color_background()
        elif self.bg_type == 'image':
            self._draw_image_background()
        elif self.bg_type == 'gradient':
            self._draw_gradient_background()
    
    def _draw_color_background(self):
        """绘制纯色背景"""
        color = self.config.get('color', '#FFFFFF')
        opacity = self.config.get('opacity', 1.0)
        
        # 保存当前状态
        self.canv.saveState()
        
        # 设置颜色
        r, g, b = self._parse_color(color)
        self.canv.setFillColorRGB(r, g, b, alpha=opacity)
        
        # 获取当前绘制位置相对于页面的偏移
        # 然后移动到页面左下角(0, 0)绘制整页背景
        x, y = self.canv.absolutePosition(0, 0)
        # 平移回页面原点
        self.canv.translate(-x, -y)
        # 绘制整页背景
        self.canv.rect(0, 0, self.width, self.height, fill=1, stroke=0)
        
        # 恢复状态
        self.canv.restoreState()
    
    def _draw_image_background(self):
        """绘制图片背景"""
        path = self.config.get('path')
        if not path or not Path(path).exists():
            return
        
        opacity = self.config.get('opacity', 1.0)
        
        # 保存状态
        self.canv.saveState()
        
        try:
            # 移动到页面原点
            x, y = self.canv.absolutePosition(0, 0)
            self.canv.translate(-x, -y)
            
            # 如果需要透明度，使用PIL处理
            if opacity < 1.0:
                img = PILImage.open(path)
                img = img.convert('RGBA')
                # 调整透明度
                alpha = img.split()[3]
                alpha = alpha.point(lambda p: int(p * opacity))
                img.putalpha(alpha)
                
                # 保存临时文件
                import tempfile
                with tempfile.NamedTemporaryFile(suffix='.png', delete=False) as tmp:
                    img.save(tmp.name, 'PNG')
                    self.canv.drawImage(tmp.name, 0, 0, width=self.width, height=self.height)
            else:
                self.canv.drawImage(path, 0, 0, width=self.width, height=self.height)
        except Exception as e:
            print(f"Warning: Failed to draw cover background image: {e}")
        finally:
            # 恢复状态
            self.canv.restoreState()
    
    def _draw_gradient_background(self):
        """绘制渐变背景（简单实现）"""
        color1 = self.config.get('colorStart', '#FFFFFF')
        color2 = self.config.get('colorEnd', '#CCCCCC')
        
        # 保存状态
        self.canv.saveState()
        
        # 移动到页面原点
        x, y_pos = self.canv.absolutePosition(0, 0)
        self.canv.translate(-x, -y_pos)
        
        # 简单的垂直渐变
        steps = 100
        for i in range(steps):
            y = (i / steps) * self.height
            h = self.height / steps
            
            # 计算中间颜色
            ratio = i / steps
            r1, g1, b1 = self._parse_color(color1)
            r2, g2, b2 = self._parse_color(color2)
            
            r = r1 + (r2 - r1) * ratio
            g = g1 + (g2 - g1) * ratio
            b = b1 + (b2 - b1) * ratio
            
            self.canv.setFillColorRGB(r, g, b)
            self.canv.rect(0, y, self.width, h, fill=1, stroke=0)
        
        # 恢复状态
        self.canv.restoreState()
    
    def _parse_color(self, color_str: str) -> tuple:
        """解析颜色"""
        if color_str.startswith('#'):
            color_str = color_str[1:]
            r = int(color_str[0:2], 16) / 255.0
            g = int(color_str[2:4], 16) / 255.0
            b = int(color_str[4:6], 16) / 255.0
            return (r, g, b)
        return (1, 1, 1)


class CoverText(CoverPageElement):
    """封面文本元素"""
    
    def __init__(self, width, height, content: str, style, position: Dict[str, Any]):
        super().__init__(width, height)
        self.content = content
        self.style = style
        self.position = position
    
    def wrap(self, aW, aH):
        """占用极小的空间以推进布局"""
        return (0, 1)
    
    def draw(self):
        """绘制文本"""
        # 保存状态
        self.canv.saveState()
        
        # 移动到页面坐标系
        curr_x, curr_y = self.canv.absolutePosition(0, 0)
        self.canv.translate(-curr_x, -curr_y)
        
        # 计算位置（现在是页面绝对坐标）
        x = self._calculate_x()
        y = self._calculate_y()
        
        # 设置字体
        self.canv.setFont(self.style.fontName, self.style.fontSize)
        self.canv.setFillColor(self.style.textColor)
        
        # 绘制文本
        if self.position.get('x') == 'center':
            self.canv.drawCentredString(x, y, self.content)
        elif self.position.get('x') == 'right':
            self.canv.drawRightString(x, y, self.content)
        else:
            self.canv.drawString(x, y, self.content)
        
        # 恢复状态
        self.canv.restoreState()
    
    def _calculate_x(self) -> float:
        """计算X坐标"""
        x_config = self.position.get('x', 'center')
        
        if x_config == 'center':
            return self.width / 2
        elif x_config == 'right':
            return self.width - 0.75 * inch
        elif x_config == 'left':
            return 0.75 * inch
        elif isinstance(x_config, (int, float)):
            return x_config
        else:
            return self.width / 2
    
    def _calculate_y(self) -> float:
        """计算Y坐标"""
        y_config = self.position.get('y', self.height / 2)
        
        if isinstance(y_config, (int, float)):
            return y_config
        elif y_config == 'top':
            return self.height - inch
        elif y_config == 'bottom':
            return inch
        elif y_config == 'center':
            return self.height / 2
        else:
            return self.height / 2


class CoverImage(CoverPageElement):
    """封面图片元素"""
    
    def __init__(self, width, height, path: str, position: Dict[str, Any], img_width: float, img_height: float = None):
        super().__init__(width, height)
        self.image_path = path
        self.position = position
        self.img_width = img_width
        self.img_height = img_height
    
    def wrap(self, aW, aH):
        """占用极小的空间以推进布局"""
        return (0, 1)
    
    def draw(self):
        """绘制图片"""
        if not Path(self.image_path).exists():
            return
        
        # 保存状态
        self.canv.saveState()
        
        # 移动到页面坐标系
        curr_x, curr_y = self.canv.absolutePosition(0, 0)
        self.canv.translate(-curr_x, -curr_y)
        
        x = self._calculate_x()
        y = self._calculate_y()
        
        # 调整坐标使图片居中于指定位置
        x = x - self.img_width / 2
        if self.img_height:
            y = y - self.img_height / 2
        
        try:
            if self.img_height:
                self.canv.drawImage(
                    self.image_path, x, y, 
                    width=self.img_width, height=self.img_height,
                    preserveAspectRatio=False
                )
            else:
                self.canv.drawImage(
                    self.image_path, x, y, 
                    width=self.img_width,
                    preserveAspectRatio=True
                )
        except Exception as e:
            print(f"Warning: Failed to draw cover image: {e}")
        finally:
            # 恢复状态
            self.canv.restoreState()
    
    def _calculate_x(self) -> float:
        """计算X坐标"""
        x_config = self.position.get('x', 'center')
        
        if x_config == 'center':
            return self.width / 2
        elif isinstance(x_config, (int, float)):
            return x_config
        else:
            return self.width / 2
    
    def _calculate_y(self) -> float:
        """计算Y坐标"""
        y_config = self.position.get('y', self.height / 2)
        
        if isinstance(y_config, (int, float)):
            return y_config
        else:
            return self.height / 2


class CoverPageGenerator:
    """封面页生成器"""
    
    def __init__(self, config: Dict[str, Any], style_manager, config_parser):
        """
        初始化封面页生成器
        
        Args:
            config: 封面配置
            style_manager: 样式管理器
            config_parser: 配置解析器（用于变量替换）
        """
        self.config = config
        self.style_manager = style_manager
        self.config_parser = config_parser
    
    def is_enabled(self) -> bool:
        """是否启用封面"""
        return self.config.get('enabled', False)
    
    def generate(self, page_size: tuple, context: Dict[str, Any]) -> List[Flowable]:
        """生成封面页元素
        
        Args:
            page_size: 页面大小 (width, height)
            context: 上下文数据
        
        Returns:
            Flowable元素列表
        """
        if not self.is_enabled():
            return []
        
        elements = []
        width, height = page_size
        
        # 添加背景（如果有）
        if 'background' in self.config:
            bg = CoverBackground(width, height, self.config['background'])
            elements.append(bg)
        
        # 添加封面元素
        cover_elements = self.config.get('elements', [])
        
        for elem_config in cover_elements:
            elem_type = elem_config.get('type', 'text')
            
            if elem_type == 'text':
                # 渲染模板变量
                content = elem_config.get('content', '')
                content = self.config_parser.render_template(content, context)
                
                # 获取样式
                style_name = elem_config.get('style', 'Normal')
                style = self.style_manager.get_style(style_name)
                
                # 创建文本元素
                position = elem_config.get('position', {'x': 'center', 'y': height / 2})
                text_elem = CoverText(width, height, content, style, position)
                elements.append(text_elem)
            
            elif elem_type == 'image':
                path = elem_config.get('path', '')
                position = elem_config.get('position', {'x': 'center', 'y': height / 2})
                img_width = elem_config.get('width', 200)
                img_height = elem_config.get('height')
                
                img_elem = CoverImage(width, height, path, position, img_width, img_height)
                elements.append(img_elem)
        
        # 添加分页符
        elements.append(PageBreak())
        
        return elements


