"""PDF元素生成器"""

from typing import Dict, Any, List, Optional
import io
from pathlib import Path

from reportlab.lib.units import inch
from reportlab.platypus import (
    Paragraph, Table, Image, Spacer, PageBreak, 
    KeepTogether, ListFlowable, ListItem
)
from reportlab.lib import colors
import pandas as pd

from pdf_generator.core.styles import StyleManager
from pdf_generator.utils.chart_generator import ChartGenerator


class ElementFactory:
    """PDF元素工厂类"""
    
    def __init__(self, style_manager: StyleManager):
        self.style_manager = style_manager
        self.chart_generator = ChartGenerator()
    
    def create_element(
        self,
        element_type: str,
        config: Dict[str, Any],
        data_sources: Optional[Dict[str, pd.DataFrame]] = None
    ):
        """根据配置创建PDF元素
        
        Args:
            element_type: 元素类型
            config: 元素配置
            data_sources: 数据源字典
        
        Returns:
            ReportLab flowable对象
        """
        if element_type == 'text':
            return self.create_text(config)
        elif element_type == 'heading':
            return self.create_heading(config)
        elif element_type == 'table':
            return self.create_table(config, data_sources)
        elif element_type == 'chart':
            return self.create_chart(config, data_sources)
        elif element_type == 'image':
            return self.create_image(config)
        elif element_type == 'spacer':
            return self.create_spacer(config)
        elif element_type == 'pagebreak':
            return PageBreak()
        elif element_type == 'list':
            return self.create_list(config)
        else:
            raise ValueError(f"Unsupported element type: {element_type}")
    
    def create_text(self, config: Dict[str, Any]) -> Paragraph:
        """创建文本段落
        
        Config keys:
            - content: 文本内容（必填）
            - style: 样式名称
        """
        content = config.get('content', '')
        style_name = config.get('style', 'Normal')
        style = self.style_manager.get_style(style_name)
        
        return Paragraph(content, style)
    
    def create_heading(self, config: Dict[str, Any]) -> Paragraph:
        """创建标题
        
        Config keys:
            - text: 标题文本（必填）
            - level: 标题级别 (1-6)，默认为1
            - style: 样式名称（可选，默认为Heading{level}）
        """
        text = config.get('text', '')
        level = config.get('level', 1)
        style_name = config.get('style', f'Heading{level}')
        style = self.style_manager.get_style(style_name)
        
        return Paragraph(text, style)
    
    def create_table(
        self,
        config: Dict[str, Any],
        data_sources: Optional[Dict[str, pd.DataFrame]] = None
    ) -> Table:
        """创建表格
        
        Config keys:
            - dataSource: 数据源名称（可选，如果提供data则不需要）
            - data: 直接提供的表格数据（二维数组）
            - columns: 要显示的列（可选，默认显示所有列）
            - headers: 自定义表头（可选）
            - style: 表格样式名称
            - columnWidths: 列宽列表
            - mergedCells: 合并单元格配置，格式：[[startRow, startCol, endRow, endCol], ...]
            - rowHeights: 行高列表（可选）
        """
        # 获取表格数据
        table_data = None
        
        # 方式1: 直接提供数据
        if 'data' in config:
            table_data = config['data']
        # 方式2: 从数据源获取
        elif 'dataSource' in config:
            data_source_name = config['dataSource']
            if not data_sources or data_source_name not in data_sources:
                raise ValueError(f"Data source '{data_source_name}' not found")
            
            df = data_sources[data_source_name]
            
            # 筛选列
            columns = config.get('columns')
            if columns:
                df = df[columns]
            
            # 准备表格数据
            headers = config.get('headers', list(df.columns))
            table_data = [headers]
            
            # 添加数据行
            for _, row in df.iterrows():
                table_data.append([str(val) for val in row.values])
        else:
            raise ValueError("Table element requires either 'dataSource' or 'data'")
        
        # 列宽
        column_widths = config.get('columnWidths')
        if column_widths:
            column_widths = [w * inch if isinstance(w, (int, float)) else w for w in column_widths]
        
        # 行高
        row_heights = config.get('rowHeights')
        if row_heights:
            row_heights = [h * inch if isinstance(h, (int, float)) else h for h in row_heights]
        
        # 创建表格
        table = Table(
            table_data, 
            colWidths=column_widths, 
            rowHeights=row_heights,
            repeatRows=config.get('repeatRows', 1)
        )
        
        # 应用样式
        style_name = config.get('style', 'default')
        table_style = self.style_manager.get_table_style(style_name)
        
        # 获取基础样式命令
        if not table_style:
            # 使用默认样式
            table_style = self.style_manager.create_table_style('default', {
                'gridColor': '#CCCCCC',
                'headerBackground': '#4472C4',
                'headerTextColor': '#FFFFFF',
                'fontSize': 9,
            })
        
        # 先应用基础样式
        table.setStyle(table_style)
        
        # 处理单元格合并
        merged_cells = config.get('mergedCells', [])
        if merged_cells:
            # 创建合并样式命令列表
            merge_commands = []
            
            for merge in merged_cells:
                if len(merge) == 4:
                    start_row, start_col, end_row, end_col = merge
                    # 添加SPAN命令
                    merge_commands.append(
                        ('SPAN', (start_col, start_row), (end_col, end_row))
                    )
                    # 为合并的单元格添加居中对齐
                    merge_commands.append(
                        ('ALIGN', (start_col, start_row), (end_col, end_row), 'CENTER')
                    )
                    merge_commands.append(
                        ('VALIGN', (start_col, start_row), (end_col, end_row), 'MIDDLE')
                    )
            
            # 应用合并样式
            if merge_commands:
                from reportlab.platypus import TableStyle
                merge_style = TableStyle(merge_commands)
                table.setStyle(merge_style)
        
        return table
    
    def create_chart(
        self,
        config: Dict[str, Any],
        data_sources: Optional[Dict[str, pd.DataFrame]] = None
    ) -> Image:
        """创建图表（作为图片）
        
        Config keys:
            - chartType: 图表类型（bar/line/pie/scatter/area）
            - dataSource: 数据源名称
            - xAxis: X轴列名
            - yAxis: Y轴列名（可以是列名或列名列表）
            - title: 图表标题
            - width: 图表宽度（英寸）
            - height: 图表高度（英寸）
        """
        chart_type = config.get('chartType')
        if not chart_type:
            raise ValueError("Chart element requires 'chartType'")
        
        # 获取数据
        data_source_name = config.get('dataSource')
        if not data_source_name:
            raise ValueError("Chart element requires 'dataSource'")
        
        if not data_sources or data_source_name not in data_sources:
            raise ValueError(f"Data source '{data_source_name}' not found")
        
        df = data_sources[data_source_name]
        
        # 生成图表
        chart_bytes = self.chart_generator.generate_chart(chart_type, df, config)
        
        # 转换为ReportLab Image
        chart_image = Image(io.BytesIO(chart_bytes))
        
        # 设置大小
        width = config.get('width', 6) * inch
        height = config.get('height', 4) * inch
        chart_image.drawWidth = width
        chart_image.drawHeight = height
        
        # 对齐方式
        alignment = config.get('alignment', 'center')
        if alignment == 'center':
            chart_image.hAlign = 'CENTER'
        elif alignment == 'right':
            chart_image.hAlign = 'RIGHT'
        else:
            chart_image.hAlign = 'LEFT'
        
        return chart_image
    
    def create_image(self, config: Dict[str, Any]) -> Image:
        """创建图片
        
        Config keys:
            - path: 图片路径（必填）
            - width: 宽度（英寸或像素）
            - height: 高度（英寸或像素）
            - alignment: 对齐方式（left/center/right）
            - keepAspectRatio: 保持宽高比（默认True）
        """
        path = config.get('path')
        if not path:
            raise ValueError("Image element requires 'path'")
        
        img_path = Path(path)
        if not img_path.exists():
            raise FileNotFoundError(f"Image not found: {path}")
        
        img = Image(str(img_path))
        
        # 设置大小（将像素值视为点，1像素约等于1点）
        width = config.get('width')
        height = config.get('height')
        keep_aspect = config.get('keepAspectRatio', True)
        
        if width and height:
            # 同时指定宽高
            img.drawWidth = float(width)
            img.drawHeight = float(height)
        elif width:
            # 只指定宽度
            img.drawWidth = float(width)
            if keep_aspect:
                aspect = img.imageHeight / img.imageWidth
                img.drawHeight = img.drawWidth * aspect
        elif height:
            # 只指定高度
            img.drawHeight = float(height)
            if keep_aspect:
                aspect = img.imageWidth / img.imageHeight
                img.drawWidth = img.drawHeight * aspect
        else:
            # 都不指定，使用原始大小（限制最大宽度）
            max_width = 400  # 默认最大宽度400点
            if img.imageWidth > max_width:
                img.drawWidth = max_width
                aspect = img.imageHeight / img.imageWidth
                img.drawHeight = img.drawWidth * aspect
            else:
                img.drawWidth = img.imageWidth
                img.drawHeight = img.imageHeight
        
        # 对齐方式
        alignment = config.get('alignment', 'left')
        if alignment == 'center':
            img.hAlign = 'CENTER'
        elif alignment == 'right':
            img.hAlign = 'RIGHT'
        else:
            img.hAlign = 'LEFT'
        
        return img
    
    def create_spacer(self, config: Dict[str, Any]) -> Spacer:
        """创建空白间隔
        
        Config keys:
            - height: 高度（英寸）
        """
        height = config.get('height', 0.5) * inch
        return Spacer(1, height)
    
    def create_list(self, config: Dict[str, Any]) -> ListFlowable:
        """创建列表
        
        Config keys:
            - items: 列表项（字符串列表）
            - bulletType: 项目符号类型（bullet/number）
            - style: 文本样式
        """
        items = config.get('items', [])
        bullet_type = config.get('bulletType', 'bullet')
        style_name = config.get('style', 'Normal')
        style = self.style_manager.get_style(style_name)
        
        list_items = []
        for item in items:
            list_items.append(ListItem(Paragraph(item, style)))
        
        if bullet_type == 'number':
            return ListFlowable(list_items, bulletType='1')
        else:
            return ListFlowable(list_items, bulletType='bullet')

