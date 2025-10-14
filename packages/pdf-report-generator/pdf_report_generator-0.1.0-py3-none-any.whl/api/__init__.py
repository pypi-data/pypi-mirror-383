"""
FastAPI web service for PDF generation.

使用方式:
    方式1 - 使用库函数:
        >>> from pdf_generator import start_api_server
        >>> start_api_server(host="localhost", port=8080)
    
    方式2 - 使用命令行:
        $ pdf-report-api --host localhost --port 8080
    
    方式3 - 使用 Python 脚本:
        $ python -m api.main
"""

__version__ = "0.1.0"

__all__ = ["__version__"]

