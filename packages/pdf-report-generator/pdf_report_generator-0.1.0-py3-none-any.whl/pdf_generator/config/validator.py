"""配置文件验证器"""

from typing import Dict, Any, List, Optional


class ConfigValidator:
    """验证JSON配置文件的结构和内容"""
    
    VALID_PAGE_SIZES = ['A4', 'A3', 'A5', 'LETTER', 'LEGAL']
    VALID_ORIENTATIONS = ['portrait', 'landscape']
    VALID_ELEMENT_TYPES = ['text', 'heading', 'table', 'chart', 'image', 'spacer', 'pagebreak', 'list']
    VALID_CHART_TYPES = ['bar', 'line', 'pie', 'scatter', 'area']
    VALID_DATA_SOURCE_TYPES = ['json', 'csv', 'excel', 'database', 'api', 'inline']
    
    def __init__(self):
        self.errors: List[str] = []
        self.warnings: List[str] = []
    
    def validate(self, config: Dict[str, Any]) -> bool:
        """验证配置文件
        
        Returns:
            bool: 配置是否有效
        """
        self.errors = []
        self.warnings = []
        
        self._validate_metadata(config.get('metadata', {}))
        self._validate_styles(config.get('styles', {}))
        self._validate_data_sources(config.get('dataSources', []))
        self._validate_elements(config.get('elements', []))
        
        # 验证新增的高级功能
        if 'pageTemplate' in config:
            self._validate_page_template(config['pageTemplate'])
        if 'toc' in config:
            self._validate_toc(config['toc'])
        if 'coverPage' in config:
            self._validate_cover_page(config['coverPage'])
        
        return len(self.errors) == 0
    
    def _validate_metadata(self, metadata: Dict[str, Any]):
        """验证元数据配置"""
        if not metadata:
            self.warnings.append("No metadata section found")
            return
        
        # 页面大小
        page_size = metadata.get('pageSize', 'A4')
        if page_size not in self.VALID_PAGE_SIZES:
            self.errors.append(
                f"Invalid pageSize '{page_size}'. Must be one of {self.VALID_PAGE_SIZES}"
            )
        
        # 页面方向
        orientation = metadata.get('orientation', 'portrait')
        if orientation not in self.VALID_ORIENTATIONS:
            self.errors.append(
                f"Invalid orientation '{orientation}'. Must be one of {self.VALID_ORIENTATIONS}"
            )
    
    def _validate_styles(self, styles: Dict[str, Any]):
        """验证样式配置"""
        for style_name, style_config in styles.items():
            if not isinstance(style_config, dict):
                self.errors.append(f"Style '{style_name}' must be a dictionary")
                continue
            
            # 验证颜色格式
            for color_key in ['textColor', 'headerBackground', 'gridColor']:
                if color_key in style_config:
                    color = style_config[color_key]
                    if not self._is_valid_color(color):
                        self.errors.append(
                            f"Invalid color format '{color}' in style '{style_name}'"
                        )
            
            # 验证对齐方式
            if 'alignment' in style_config:
                alignment = style_config['alignment']
                if alignment not in ['left', 'center', 'right', 'justify']:
                    self.errors.append(
                        f"Invalid alignment '{alignment}' in style '{style_name}'"
                    )
    
    def _validate_data_sources(self, data_sources: List[Dict[str, Any]]):
        """验证数据源配置"""
        source_names = set()
        
        for idx, source in enumerate(data_sources):
            if not isinstance(source, dict):
                self.errors.append(f"Data source at index {idx} must be a dictionary")
                continue
            
            # 名称必填
            if 'name' not in source:
                self.errors.append(f"Data source at index {idx} missing required field 'name'")
                continue
            
            name = source['name']
            if name in source_names:
                self.errors.append(f"Duplicate data source name '{name}'")
            source_names.add(name)
            
            # 类型必填
            if 'type' not in source:
                self.errors.append(f"Data source '{name}' missing required field 'type'")
                continue
            
            source_type = source['type']
            if source_type not in self.VALID_DATA_SOURCE_TYPES:
                self.errors.append(
                    f"Invalid data source type '{source_type}' for '{name}'. "
                    f"Must be one of {self.VALID_DATA_SOURCE_TYPES}"
                )
            
            # 根据类型验证必需字段
            if source_type in ['json', 'csv', 'excel'] and 'path' not in source:
                self.errors.append(
                    f"Data source '{name}' of type '{source_type}' requires 'path' field"
                )
            
            if source_type == 'api' and 'url' not in source:
                self.errors.append(
                    f"Data source '{name}' of type 'api' requires 'url' field"
                )
            
            if source_type == 'database' and 'query' not in source:
                self.errors.append(
                    f"Data source '{name}' of type 'database' requires 'query' field"
                )
    
    def _validate_elements(self, elements: List[Dict[str, Any]]):
        """验证PDF元素配置"""
        if not elements:
            self.warnings.append("No elements defined in configuration")
            return
        
        for idx, element in enumerate(elements):
            if not isinstance(element, dict):
                self.errors.append(f"Element at index {idx} must be a dictionary")
                continue
            
            # 类型必填
            if 'type' not in element:
                self.errors.append(f"Element at index {idx} missing required field 'type'")
                continue
            
            element_type = element['type']
            if element_type not in self.VALID_ELEMENT_TYPES:
                self.errors.append(
                    f"Invalid element type '{element_type}' at index {idx}. "
                    f"Must be one of {self.VALID_ELEMENT_TYPES}"
                )
                continue
            
            # 根据元素类型验证必需字段
            if element_type == 'text' and 'content' not in element:
                self.errors.append(f"Text element at index {idx} requires 'content' field")
            
            if element_type == 'table':
                # 表格需要dataSource或data其中之一
                if 'dataSource' not in element and 'data' not in element:
                    self.errors.append(
                        f"Table element at index {idx} requires either 'dataSource' or 'data' field"
                    )
                
                # 验证mergedCells格式
                if 'mergedCells' in element:
                    merged_cells = element['mergedCells']
                    if not isinstance(merged_cells, list):
                        self.errors.append(
                            f"Table element at index {idx}: 'mergedCells' must be a list"
                        )
                    else:
                        for i, merge in enumerate(merged_cells):
                            if not isinstance(merge, list) or len(merge) != 4:
                                self.errors.append(
                                    f"Table element at index {idx}: mergedCells[{i}] must be "
                                    f"[startRow, startCol, endRow, endCol]"
                                )
            
            if element_type == 'chart':
                if 'chartType' not in element:
                    self.errors.append(f"Chart element at index {idx} requires 'chartType' field")
                elif element['chartType'] not in self.VALID_CHART_TYPES:
                    self.errors.append(
                        f"Invalid chart type '{element['chartType']}' at index {idx}. "
                        f"Must be one of {self.VALID_CHART_TYPES}"
                    )
                
                if 'dataSource' not in element:
                    self.errors.append(f"Chart element at index {idx} requires 'dataSource' field")
            
            if element_type == 'image' and 'path' not in element:
                self.errors.append(f"Image element at index {idx} requires 'path' field")
    
    def _validate_page_template(self, page_template: Dict[str, Any]):
        """验证页面模板配置（页眉页脚）"""
        if not isinstance(page_template, dict):
            self.errors.append("pageTemplate must be a dictionary")
            return
        
        # 验证页眉
        if 'header' in page_template:
            self._validate_header_footer_section(page_template['header'], 'header')
        
        # 验证页脚
        if 'footer' in page_template:
            self._validate_header_footer_section(page_template['footer'], 'footer')
    
    def _validate_header_footer_section(self, section: Dict[str, Any], section_name: str):
        """验证页眉或页脚配置"""
        if not isinstance(section, dict):
            self.errors.append(f"{section_name} must be a dictionary")
            return
        
        # 验证左中右区域
        for position in ['left', 'center', 'right']:
            if position in section:
                pos_config = section[position]
                if not isinstance(pos_config, dict):
                    self.errors.append(f"{section_name}.{position} must be a dictionary")
                    continue
                
                pos_type = pos_config.get('type')
                if pos_type and pos_type not in ['text', 'image', 'pageNumber']:
                    self.errors.append(
                        f"Invalid type '{pos_type}' in {section_name}.{position}. "
                        f"Must be 'text', 'image', or 'pageNumber'"
                    )
    
    def _validate_toc(self, toc: Dict[str, Any]):
        """验证目录配置"""
        if not isinstance(toc, dict):
            self.errors.append("toc must be a dictionary")
            return
        
        # 验证手动条目
        if 'entries' in toc:
            entries = toc['entries']
            if not isinstance(entries, list):
                self.errors.append("toc.entries must be a list")
            else:
                for idx, entry in enumerate(entries):
                    if not isinstance(entry, dict):
                        self.errors.append(f"toc.entries[{idx}] must be a dictionary")
                        continue
                    
                    if 'title' not in entry:
                        self.errors.append(f"toc.entries[{idx}] requires 'title' field")
                    
                    if 'level' in entry and not isinstance(entry['level'], int):
                        self.errors.append(f"toc.entries[{idx}].level must be an integer")
    
    def _validate_cover_page(self, cover_page: Dict[str, Any]):
        """验证封面配置"""
        if not isinstance(cover_page, dict):
            self.errors.append("coverPage must be a dictionary")
            return
        
        # 验证背景
        if 'background' in cover_page:
            bg = cover_page['background']
            if not isinstance(bg, dict):
                self.errors.append("coverPage.background must be a dictionary")
            else:
                bg_type = bg.get('type')
                if bg_type and bg_type not in ['color', 'image', 'gradient']:
                    self.errors.append(
                        f"Invalid background type '{bg_type}'. "
                        f"Must be 'color', 'image', or 'gradient'"
                    )
        
        # 验证元素
        if 'elements' in cover_page:
            elements = cover_page['elements']
            if not isinstance(elements, list):
                self.errors.append("coverPage.elements must be a list")
            else:
                for idx, elem in enumerate(elements):
                    if not isinstance(elem, dict):
                        self.errors.append(f"coverPage.elements[{idx}] must be a dictionary")
                        continue
                    
                    elem_type = elem.get('type')
                    if not elem_type:
                        self.errors.append(f"coverPage.elements[{idx}] requires 'type' field")
                    elif elem_type not in ['text', 'image']:
                        self.errors.append(
                            f"Invalid cover element type '{elem_type}' at index {idx}. "
                            f"Must be 'text' or 'image'"
                        )
                    
                    if elem_type == 'text' and 'content' not in elem:
                        self.errors.append(f"coverPage.elements[{idx}] (text) requires 'content' field")
                    
                    if elem_type == 'image' and 'path' not in elem:
                        self.errors.append(f"coverPage.elements[{idx}] (image) requires 'path' field")
    
    def _is_valid_color(self, color: str) -> bool:
        """验证颜色格式（支持#RRGGBB）"""
        if not isinstance(color, str):
            return False
        
        if color.startswith('#'):
            color = color[1:]
            if len(color) == 6:
                try:
                    int(color, 16)
                    return True
                except ValueError:
                    return False
        
        return False
    
    def get_errors(self) -> List[str]:
        """获取所有错误"""
        return self.errors
    
    def get_warnings(self) -> List[str]:
        """获取所有警告"""
        return self.warnings

