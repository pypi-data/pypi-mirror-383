"""
PDF Report Generator
A flexible and powerful PDF generation library with JSON configuration support.

Basic Usage:
    >>> from pdf_generator import PDFReportGenerator
    >>> generator = PDFReportGenerator(config_dict=config)
    >>> generator.generate("output.pdf")

API Server Usage:
    >>> from pdf_generator import start_api_server
    >>> start_api_server(host="localhost", port=8080)
"""

from pdf_generator.core.generator import PDFReportGenerator

__version__ = "0.1.0"

# 主要导出
__all__ = ["PDFReportGenerator"]

# 尝试导入 API 服务器功能（可选依赖）
try:
    from pdf_generator.api_server import start_api_server, create_app
    __all__.extend(["start_api_server", "create_app"])
except ImportError:
    # API 依赖未安装时不导出这些功能
    pass

