"""页码格式化工具"""

from typing import Optional


class PageNumberFormatter:
    """页码格式化器"""
    
    # 中文数字映射
    CHINESE_NUMBERS = ['零', '一', '二', '三', '四', '五', '六', '七', '八', '九']
    CHINESE_UNITS = ['', '十', '百', '千']
    
    @staticmethod
    def to_arabic(page_num: int) -> str:
        """转换为阿拉伯数字"""
        return str(page_num)
    
    @staticmethod
    def to_roman(page_num: int, upper: bool = True) -> str:
        """转换为罗马数字
        
        Args:
            page_num: 页码
            upper: 是否大写（默认True）
        """
        val = [
            1000, 900, 500, 400,
            100, 90, 50, 40,
            10, 9, 5, 4,
            1
        ]
        syms = [
            "M", "CM", "D", "CD",
            "C", "XC", "L", "XL",
            "X", "IX", "V", "IV",
            "I"
        ]
        roman_num = ''
        i = 0
        while page_num > 0:
            for _ in range(page_num // val[i]):
                roman_num += syms[i]
                page_num -= val[i]
            i += 1
        
        return roman_num if upper else roman_num.lower()
    
    @staticmethod
    def to_chinese(page_num: int) -> str:
        """转换为中文数字"""
        if page_num == 0:
            return PageNumberFormatter.CHINESE_NUMBERS[0]
        
        result = ''
        str_num = str(page_num)
        length = len(str_num)
        
        for i, digit in enumerate(str_num):
            digit_int = int(digit)
            if digit_int != 0:
                result += PageNumberFormatter.CHINESE_NUMBERS[digit_int]
                unit_index = length - i - 1
                if unit_index < len(PageNumberFormatter.CHINESE_UNITS):
                    result += PageNumberFormatter.CHINESE_UNITS[unit_index]
        
        # 处理特殊情况（如"一十"简化为"十"）
        if result.startswith('一十'):
            result = result[1:]
        
        return result
    
    @staticmethod
    def format_page_number(
        page_num: int, 
        total_pages: Optional[int] = None,
        format_str: str = "{page}"
    ) -> str:
        """格式化页码
        
        Args:
            page_num: 当前页码
            total_pages: 总页数（可选）
            format_str: 格式字符串，支持：
                - {page} 或 {page:arabic} - 阿拉伯数字
                - {page:roman} - 罗马数字（大写）
                - {page:roman_lower} - 罗马数字（小写）
                - {page:chinese} - 中文数字
                - {total} - 总页数
        
        Examples:
            "第{page}页" -> "第1页"
            "Page {page} of {total}" -> "Page 1 of 10"
            "{page:roman}" -> "I"
            "第{page:chinese}页" -> "第一页"
        """
        # 替换页码
        result = format_str
        
        # 处理不同格式的页码
        if '{page:roman}' in result:
            result = result.replace('{page:roman}', PageNumberFormatter.to_roman(page_num, True))
        elif '{page:roman_lower}' in result:
            result = result.replace('{page:roman_lower}', PageNumberFormatter.to_roman(page_num, False))
        elif '{page:chinese}' in result:
            result = result.replace('{page:chinese}', PageNumberFormatter.to_chinese(page_num))
        elif '{page:arabic}' in result:
            result = result.replace('{page:arabic}', PageNumberFormatter.to_arabic(page_num))
        elif '{page}' in result:
            result = result.replace('{page}', PageNumberFormatter.to_arabic(page_num))
        
        # 替换总页数
        if total_pages is not None and '{total}' in result:
            result = result.replace('{total}', str(total_pages))
        
        return result


# 便捷函数
def format_page(page_num: int, total_pages: Optional[int] = None, format_str: str = "{page}") -> str:
    """格式化页码的便捷函数"""
    return PageNumberFormatter.format_page_number(page_num, total_pages, format_str)


