"""
PDF Report Generator 命令行工具
"""

import argparse
import sys


def run_api():
    """
    命令行启动 API 服务器
    
    这个函数作为控制台脚本的入口点
    使用方式: pdf-report-api --host 0.0.0.0 --port 8000
    """
    parser = argparse.ArgumentParser(
        description="PDF Report Generator API Server",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
示例:
  # 启动服务器（默认配置）
  pdf-report-api
  
  # 指定主机和端口
  pdf-report-api --host localhost --port 8080
  
  # 开发模式（热重载）
  pdf-report-api --reload
  
  # 生产模式（多进程）
  pdf-report-api --workers 4
        """
    )
    
    parser.add_argument(
        "--host",
        type=str,
        default="0.0.0.0",
        help="服务器主机地址 (默认: 0.0.0.0)"
    )
    
    parser.add_argument(
        "--port",
        type=int,
        default=8000,
        help="服务器端口 (默认: 8000)"
    )
    
    parser.add_argument(
        "--reload",
        action="store_true",
        help="启用热重载（开发模式）"
    )
    
    parser.add_argument(
        "--workers",
        type=int,
        default=1,
        help="工作进程数量（生产模式，默认: 1）"
    )
    
    parser.add_argument(
        "--log-level",
        type=str,
        default="info",
        choices=["critical", "error", "warning", "info", "debug", "trace"],
        help="日志级别 (默认: info)"
    )
    
    args = parser.parse_args()
    
    # 导入并启动服务器
    try:
        from pdf_generator.api_server import start_api_server
        
        start_api_server(
            host=args.host,
            port=args.port,
            reload=args.reload,
            log_level=args.log_level,
            workers=args.workers,
        )
    except KeyboardInterrupt:
        print("\n👋 服务器已停止")
        sys.exit(0)
    except Exception as e:
        print(f"❌ 启动失败: {e}", file=sys.stderr)
        sys.exit(1)


if __name__ == "__main__":
    run_api()

