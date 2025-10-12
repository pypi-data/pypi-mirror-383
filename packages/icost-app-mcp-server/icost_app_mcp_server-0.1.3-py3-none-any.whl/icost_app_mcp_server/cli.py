"""Command Line Interface for iCost App MCP Server
"""

import argparse
import logging
import sys
from typing import Optional

from .server import mcp


def setup_logging(level: str = "INFO") -> None:
    """设置日志配置"""
    logging.basicConfig(
        level=getattr(logging, level.upper()),
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        handlers=[
            logging.StreamHandler(),
            logging.FileHandler('icost_mcp_server.log')
        ]
    )


def create_parser() -> argparse.ArgumentParser:
    """创建命令行参数解析器"""
    parser = argparse.ArgumentParser(
        description="iCost App MCP Server - A Model Context Protocol server for iCost application"
    )
    
    parser.add_argument(
        "--transport",
        choices=["stdio", "http"],
        default="stdio",
        help="Transport mode: stdio for MCP clients, http for testing (default: stdio)"
    )
    
    parser.add_argument(
        "--host",
        default="localhost",
        help="Host to bind the server to (default: localhost, only for HTTP mode)"
    )
    
    parser.add_argument(
        "--port",
        type=int,
        default=9000,
        help="Port to bind the server to (default: 9000, only for HTTP mode)"
    )
    
    parser.add_argument(
        "--debug",
        action="store_true",
        help="Enable debug mode"
    )
    
    parser.add_argument(
        "--log-level",
        choices=["DEBUG", "INFO", "WARNING", "ERROR"],
        default="INFO",
        help="Set the logging level (default: INFO)"
    )
    
    return parser


def main() -> None:
    """主入口函数"""
    parser = create_parser()
    args = parser.parse_args()
    
    # 设置日志 - 只在HTTP模式下启用文件日志
    if args.transport == "http":
        setup_logging(args.log_level)
        logger = logging.getLogger(__name__)
        logger.info(f"Starting iCost MCP Server on {args.host}:{args.port}")
    
    try:
        if args.transport == "stdio":
            # STDIO模式 - 用于MCP客户端
            mcp.run()
        else:
            # HTTP模式 - 用于测试和调试
            mcp.run(transport="http", host=args.host, port=args.port)
    except KeyboardInterrupt:
        if args.transport == "http":
            logger.info("Server stopped by user")
        sys.exit(0)
    except Exception as e:
        if args.transport == "http":
            logger.error(f"Server error: {e}")
        else:
            # STDIO模式下的错误输出到stderr
            print(f"Server error: {e}", file=sys.stderr)
        sys.exit(1)


if __name__ == "__main__":
    main()