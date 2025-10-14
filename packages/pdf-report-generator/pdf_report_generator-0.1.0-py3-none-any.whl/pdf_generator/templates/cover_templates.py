"""封面预设模板"""

from typing import Dict, Any


class CoverTemplates:
    """封面预设模板集合"""
    
    @staticmethod
    def simple(title: str, subtitle: str = None, author: str = None) -> Dict[str, Any]:
        """简约封面模板
        
        Args:
            title: 标题
            subtitle: 副标题（可选）
            author: 作者（可选）
        """
        elements = [
            {
                "type": "text",
                "content": title,
                "style": "Title",
                "position": {"x": "center", "y": 500}
            }
        ]
        
        if subtitle:
            elements.append({
                "type": "text",
                "content": subtitle,
                "style": "Heading2",
                "position": {"x": "center", "y": 450}
            })
        
        if author:
            elements.append({
                "type": "text",
                "content": f"作者：{author}",
                "style": "Normal",
                "position": {"x": "center", "y": 200}
            })
        
        return {
            "enabled": True,
            "background": {
                "type": "color",
                "color": "#FFFFFF"
            },
            "elements": elements
        }
    
    @staticmethod
    def business(title: str, company: str = None, logo_path: str = None) -> Dict[str, Any]:
        """商务封面模板
        
        Args:
            title: 报告标题
            company: 公司名称（可选）
            logo_path: Logo路径（可选）
        """
        elements = []
        
        # Logo
        if logo_path:
            elements.append({
                "type": "image",
                "path": logo_path,
                "position": {"x": "center", "y": 650},
                "width": 150
            })
        
        # 标题
        elements.append({
            "type": "text",
            "content": title,
            "style": "Title",
            "position": {"x": "center", "y": 400}
        })
        
        # 公司名称
        if company:
            elements.append({
                "type": "text",
                "content": company,
                "style": "Heading2",
                "position": {"x": "center", "y": 150}
            })
        
        return {
            "enabled": True,
            "background": {
                "type": "gradient",
                "colorStart": "#F5F5F5",
                "colorEnd": "#FFFFFF"
            },
            "elements": elements
        }
    
    @staticmethod
    def tech(title: str, subtitle: str = None, bg_image: str = None) -> Dict[str, Any]:
        """科技风格封面模板
        
        Args:
            title: 标题
            subtitle: 副标题（可选）
            bg_image: 背景图片路径（可选）
        """
        background = {
            "type": "color",
            "color": "#1a1a1a"
        }
        
        if bg_image:
            background = {
                "type": "image",
                "path": bg_image,
                "opacity": 0.3
            }
        
        elements = [
            {
                "type": "text",
                "content": title,
                "style": "Title",
                "position": {"x": "center", "y": 450}
            }
        ]
        
        if subtitle:
            elements.append({
                "type": "text",
                "content": subtitle,
                "style": "Heading1",
                "position": {"x": "center", "y": 350}
            })
        
        return {
            "enabled": True,
            "background": background,
            "elements": elements
        }
    
    @staticmethod
    def formal(
        title: str,
        subtitle: str = None,
        author: str = None,
        date: str = "{{date}}"
    ) -> Dict[str, Any]:
        """正式报告封面模板
        
        Args:
            title: 报告标题
            subtitle: 副标题（可选）
            author: 作者（可选）
            date: 日期（默认使用当前日期）
        """
        elements = [
            # 标题
            {
                "type": "text",
                "content": title,
                "style": "Title",
                "position": {"x": "center", "y": 550}
            }
        ]
        
        if subtitle:
            elements.append({
                "type": "text",
                "content": subtitle,
                "style": "Heading1",
                "position": {"x": "center", "y": 480}
            })
        
        # 底部信息
        y_pos = 200
        if author:
            elements.append({
                "type": "text",
                "content": f"编制：{author}",
                "style": "Normal",
                "position": {"x": "center", "y": y_pos}
            })
            y_pos -= 30
        
        elements.append({
            "type": "text",
            "content": date,
            "style": "Normal",
            "position": {"x": "center", "y": y_pos}
        })
        
        return {
            "enabled": True,
            "background": {
                "type": "color",
                "color": "#FFFFFF"
            },
            "elements": elements
        }
    
    @staticmethod
    def get_template(template_name: str, **kwargs) -> Dict[str, Any]:
        """获取指定的预设模板
        
        Args:
            template_name: 模板名称 (simple, business, tech, formal)
            **kwargs: 模板参数
        
        Returns:
            封面配置字典
        """
        templates = {
            'simple': CoverTemplates.simple,
            'business': CoverTemplates.business,
            'tech': CoverTemplates.tech,
            'formal': CoverTemplates.formal,
        }
        
        if template_name not in templates:
            raise ValueError(
                f"Unknown template: {template_name}. "
                f"Available templates: {list(templates.keys())}"
            )
        
        return templates[template_name](**kwargs)


