"""图表生成工具"""

import io
from typing import Dict, Any, Optional
from pathlib import Path
import pandas as pd
import matplotlib
matplotlib.use('Agg')  # 使用非交互式后端
import matplotlib.pyplot as plt
from matplotlib.figure import Figure
import matplotlib.font_manager as fm


class ChartGenerator:
    """生成各种类型的图表"""
    
    def __init__(self):
        # 设置中文字体支持
        self._setup_chinese_fonts()
        plt.rcParams['axes.unicode_minus'] = False
    
    def _setup_chinese_fonts(self):
        """设置matplotlib中文字体支持"""
        # 获取项目根目录下的fonts文件夹
        project_root = Path(__file__).parent.parent.parent
        fonts_dir = project_root / "fonts"
        
        chinese_fonts = []
        
        if fonts_dir.exists():
            # 注册项目中的字体
            font_files = {
                'SimHei': ['SimHei.ttf', 'SimHei.TTF'],
                'SimSun': ['SimSun.ttf', 'SimSun.TTF'],
                'GB2312': ['GB2312.ttf', 'GB2312.TTF'],
            }
            
            for font_name, font_file_list in font_files.items():
                for font_file in font_file_list:
                    font_path = fonts_dir / font_file
                    if font_path.exists():
                        try:
                            fm.fontManager.addfont(str(font_path))
                            chinese_fonts.append(font_name)
                            print(f"Matplotlib: Registered font {font_name} from {font_file}")
                        except Exception as e:
                            print(f"Warning: Failed to register {font_name} for matplotlib: {e}")
                        break
        
        # 设置字体优先级
        if chinese_fonts:
            plt.rcParams['font.sans-serif'] = chinese_fonts + ['DejaVu Sans']
            print(f"Matplotlib: Chinese fonts set to {chinese_fonts}")
        else:
            # 尝试使用系统字体
            plt.rcParams['font.sans-serif'] = ['SimHei', 'Microsoft YaHei', 'SimSun', 'DejaVu Sans']
            print("Warning: Using system fonts for Chinese support")
    
    def generate_chart(
        self,
        chart_type: str,
        data: pd.DataFrame,
        config: Dict[str, Any]
    ) -> bytes:
        """生成图表并返回PNG字节流
        
        Args:
            chart_type: 图表类型（bar/line/pie/scatter/area）
            data: 数据DataFrame
            config: 图表配置
        
        Returns:
            PNG图表的字节流
        """
        fig = self._create_figure(config)
        ax = fig.add_subplot(111)
        
        # 根据类型生成图表
        if chart_type == 'bar':
            self._create_bar_chart(ax, data, config)
        elif chart_type == 'line':
            self._create_line_chart(ax, data, config)
        elif chart_type == 'pie':
            self._create_pie_chart(ax, data, config)
        elif chart_type == 'scatter':
            self._create_scatter_chart(ax, data, config)
        elif chart_type == 'area':
            self._create_area_chart(ax, data, config)
        else:
            raise ValueError(f"Unsupported chart type: {chart_type}")
        
        # 设置标题
        title = config.get('title', '')
        if title:
            ax.set_title(title, fontsize=config.get('titleFontSize', 14), pad=10)
        
        # 设置图例
        if config.get('showLegend', True):
            ax.legend(loc=config.get('legendPosition', 'best'))
        
        # 调整布局
        fig.tight_layout()
        
        # 转换为字节流
        buf = io.BytesIO()
        fig.savefig(buf, format='png', dpi=config.get('dpi', 100), bbox_inches='tight')
        plt.close(fig)
        buf.seek(0)
        
        return buf.read()
    
    def _create_figure(self, config: Dict[str, Any]) -> Figure:
        """创建图表画布"""
        width = config.get('width', 8)
        height = config.get('height', 5)
        fig = plt.figure(figsize=(width, height))
        
        # 设置背景色
        if 'backgroundColor' in config:
            fig.patch.set_facecolor(config['backgroundColor'])
        
        return fig
    
    def _create_bar_chart(self, ax, data: pd.DataFrame, config: Dict[str, Any]):
        """创建柱状图"""
        x_col = config.get('xAxis')
        y_cols = config.get('yAxis')
        
        if not x_col or not y_cols:
            raise ValueError("Bar chart requires 'xAxis' and 'yAxis' in config")
        
        # 支持单列或多列y轴
        if isinstance(y_cols, str):
            y_cols = [y_cols]
        
        x_data = data[x_col]
        bar_width = config.get('barWidth', 0.35)
        
        if len(y_cols) == 1:
            # 单一柱状图
            ax.bar(x_data, data[y_cols[0]], width=bar_width, label=y_cols[0])
        else:
            # 多组柱状图
            x_pos = range(len(x_data))
            offset = -(len(y_cols) - 1) * bar_width / 2
            
            for idx, y_col in enumerate(y_cols):
                pos = [p + offset + idx * bar_width for p in x_pos]
                ax.bar(pos, data[y_col], width=bar_width, label=y_col)
            
            ax.set_xticks(x_pos)
            ax.set_xticklabels(x_data)
        
        ax.set_xlabel(config.get('xLabel', x_col))
        ax.set_ylabel(config.get('yLabel', 'Value'))
        
        if config.get('grid', True):
            ax.grid(axis='y', alpha=0.3)
    
    def _create_line_chart(self, ax, data: pd.DataFrame, config: Dict[str, Any]):
        """创建折线图"""
        x_col = config.get('xAxis')
        y_cols = config.get('yAxis')
        
        if not x_col or not y_cols:
            raise ValueError("Line chart requires 'xAxis' and 'yAxis' in config")
        
        if isinstance(y_cols, str):
            y_cols = [y_cols]
        
        x_data = data[x_col]
        
        for y_col in y_cols:
            ax.plot(x_data, data[y_col], marker='o', label=y_col, linewidth=2)
        
        ax.set_xlabel(config.get('xLabel', x_col))
        ax.set_ylabel(config.get('yLabel', 'Value'))
        
        if config.get('grid', True):
            ax.grid(alpha=0.3)
    
    def _create_pie_chart(self, ax, data: pd.DataFrame, config: Dict[str, Any]):
        """创建饼图"""
        labels_col = config.get('labels')
        values_col = config.get('values')
        
        if not labels_col or not values_col:
            raise ValueError("Pie chart requires 'labels' and 'values' in config")
        
        labels = data[labels_col]
        values = data[values_col]
        
        # 饼图配置
        autopct = config.get('showPercentage', True)
        if autopct:
            autopct = '%1.1f%%'
        
        colors = config.get('colors', None)
        explode = config.get('explode', None)
        
        ax.pie(
            values,
            labels=labels,
            autopct=autopct,
            colors=colors,
            explode=explode,
            startangle=config.get('startAngle', 90)
        )
        
        ax.axis('equal')  # 确保饼图是圆的
    
    def _create_scatter_chart(self, ax, data: pd.DataFrame, config: Dict[str, Any]):
        """创建散点图"""
        x_col = config.get('xAxis')
        y_col = config.get('yAxis')
        
        if not x_col or not y_col:
            raise ValueError("Scatter chart requires 'xAxis' and 'yAxis' in config")
        
        size_col = config.get('sizeColumn')
        color_col = config.get('colorColumn')
        
        x_data = data[x_col]
        y_data = data[y_col]
        
        kwargs = {}
        if size_col and size_col in data.columns:
            kwargs['s'] = data[size_col]
        else:
            kwargs['s'] = config.get('markerSize', 50)
        
        if color_col and color_col in data.columns:
            kwargs['c'] = data[color_col]
            kwargs['cmap'] = config.get('colormap', 'viridis')
        
        ax.scatter(x_data, y_data, alpha=config.get('alpha', 0.6), **kwargs)
        
        ax.set_xlabel(config.get('xLabel', x_col))
        ax.set_ylabel(config.get('yLabel', y_col))
        
        if config.get('grid', True):
            ax.grid(alpha=0.3)
    
    def _create_area_chart(self, ax, data: pd.DataFrame, config: Dict[str, Any]):
        """创建面积图"""
        x_col = config.get('xAxis')
        y_cols = config.get('yAxis')
        
        if not x_col or not y_cols:
            raise ValueError("Area chart requires 'xAxis' and 'yAxis' in config")
        
        if isinstance(y_cols, str):
            y_cols = [y_cols]
        
        x_data = data[x_col]
        
        if config.get('stacked', False):
            # 堆叠面积图
            ax.stackplot(x_data, *[data[col] for col in y_cols], labels=y_cols, alpha=0.7)
        else:
            # 普通面积图
            for y_col in y_cols:
                ax.fill_between(x_data, data[y_col], alpha=0.5, label=y_col)
        
        ax.set_xlabel(config.get('xLabel', x_col))
        ax.set_ylabel(config.get('yLabel', 'Value'))
        
        if config.get('grid', True):
            ax.grid(alpha=0.3)

