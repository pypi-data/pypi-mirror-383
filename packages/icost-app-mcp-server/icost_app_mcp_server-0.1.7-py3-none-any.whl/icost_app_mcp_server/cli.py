"""
Command Line Interface for iCost App MCP Server
"""

import argparse
import json
import logging
import os
import sys
from pathlib import Path
from typing import Dict, Optional, Any

from . import __version__
from .server import mcp


def setup_logging(level: str = "INFO", log_file: Optional[str] = None) -> logging.Logger:
    """设置日志配置
    
    Args:
        level: 日志级别
        log_file: 日志文件路径，如果为None则不写入文件
        
    Returns:
        配置好的logger实例
    """
    logger = logging.getLogger("icost_mcp_server")
    logger.setLevel(getattr(logging, level.upper()))
    
    # 清除现有的处理器
    logger.handlers.clear()
    
    # 创建格式化器
    formatter = logging.Formatter(
        '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    )
    
    # 控制台处理器
    console_handler = logging.StreamHandler()
    console_handler.setFormatter(formatter)
    logger.addHandler(console_handler)
    
    # 文件处理器（如果指定了日志文件）
    if log_file:
        try:
            # 确保日志目录存在
            log_path = Path(log_file)
            log_path.parent.mkdir(parents=True, exist_ok=True)
            
            file_handler = logging.FileHandler(log_file)
            file_handler.setFormatter(formatter)
            logger.addHandler(file_handler)
        except Exception as e:
            logger.warning(f"无法创建日志文件 {log_file}: {e}")
    
    return logger


def load_config_file(config_path: str) -> Dict[str, Any]:
    """加载配置文件
    
    Args:
        config_path: 配置文件路径
        
    Returns:
        配置字典
        
    Raises:
        FileNotFoundError: 配置文件不存在
        json.JSONDecodeError: 配置文件格式错误
    """
    config_file = Path(config_path)
    if not config_file.exists():
        raise FileNotFoundError(f"配置文件不存在: {config_path}")
    
    try:
        with open(config_file, 'r', encoding='utf-8') as f:
            return json.load(f)
    except json.JSONDecodeError as e:
        raise json.JSONDecodeError(f"配置文件格式错误: {e}", e.doc, e.pos)


def get_env_config() -> Dict[str, Any]:
    """从环境变量获取配置
    
    Returns:
        环境变量配置字典
    """
    env_config = {}
    
    # 支持的环境变量映射
    env_mappings = {
        'ICOST_MCP_TRANSPORT': 'transport',
        'ICOST_MCP_HOST': 'host',
        'ICOST_MCP_PORT': 'port',
        'ICOST_MCP_LOG_LEVEL': 'log_level',
        'ICOST_MCP_LOG_FILE': 'log_file',
        'ICOST_MCP_DEBUG': 'debug',
    }
    
    for env_var, config_key in env_mappings.items():
        value = os.getenv(env_var)
        if value is not None:
            # 特殊处理布尔值
            if config_key == 'debug':
                env_config[config_key] = value.lower() in ('true', '1', 'yes', 'on')
            # 特殊处理端口号
            elif config_key == 'port':
                try:
                    env_config[config_key] = int(value)
                except ValueError:
                    pass  # 忽略无效的端口号
            else:
                env_config[config_key] = value
    
    return env_config


def validate_args(args: argparse.Namespace) -> None:
    """验证命令行参数
    
    Args:
        args: 解析后的命令行参数
        
    Raises:
        ValueError: 参数验证失败
    """
    # 验证端口范围
    if not (1 <= args.port <= 65535):
        raise ValueError(f"端口号必须在 1-65535 范围内，当前值: {args.port}")
    
    # 验证主机地址
    if not args.host.strip():
        raise ValueError("主机地址不能为空")
    
    # 验证日志文件路径（如果指定）
    if args.log_file:
        log_path = Path(args.log_file)
        try:
            # 检查父目录是否可写
            log_path.parent.mkdir(parents=True, exist_ok=True)
            # 尝试创建临时文件测试写权限
            test_file = log_path.parent / f".test_write_{os.getpid()}"
            test_file.touch()
            test_file.unlink()
        except Exception as e:
            raise ValueError(f"无法写入日志文件 {args.log_file}: {e}")


def create_parser() -> argparse.ArgumentParser:
    """创建命令行参数解析器"""
    parser = argparse.ArgumentParser(
        description="iCost App MCP Server - A Model Context Protocol server for iCost application",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
示例用法:
  %(prog)s                          # 使用默认 stdio 模式
  %(prog)s --transport http         # 使用 HTTP 模式，默认端口 9000
  %(prog)s --transport http --port 8080 --host 0.0.0.0  # 自定义 HTTP 配置
  %(prog)s --config config.json     # 使用配置文件
  %(prog)s --debug --log-level DEBUG  # 启用调试模式

环境变量支持:
  ICOST_MCP_TRANSPORT    传输模式 (stdio/http)
  ICOST_MCP_HOST         主机地址
  ICOST_MCP_PORT         端口号
  ICOST_MCP_LOG_LEVEL    日志级别
  ICOST_MCP_LOG_FILE     日志文件路径
  ICOST_MCP_DEBUG        调试模式 (true/false)
        """
    )
    
    # 版本信息
    parser.add_argument(
        "--version", "-v",
        action="version",
        version=f"%(prog)s {__version__}"
    )
    
    # 配置文件
    parser.add_argument(
        "--config", "-c",
        help="配置文件路径 (JSON 格式)"
    )
    
    # 传输模式
    parser.add_argument(
        "--transport",
        choices=["stdio", "http"],
        default="stdio",
        help="传输模式: stdio 用于 MCP 客户端，http 用于测试 (默认: stdio)"
    )
    
    # 网络配置
    parser.add_argument(
        "--host",
        default="localhost",
        help="服务器绑定的主机地址 (默认: localhost，仅 HTTP 模式有效)"
    )
    
    parser.add_argument(
        "--port",
        type=int,
        default=9000,
        help="服务器绑定的端口 (默认: 9000，仅 HTTP 模式有效)"
    )
    
    # 日志配置
    parser.add_argument(
        "--log-level",
        choices=["DEBUG", "INFO", "WARNING", "ERROR", "CRITICAL"],
        default="INFO",
        help="设置日志级别 (默认: INFO)"
    )
    
    parser.add_argument(
        "--log-file",
        help="日志文件路径 (如果不指定，仅输出到控制台)"
    )
    
    # 调试模式
    parser.add_argument(
        "--debug",
        action="store_true",
        help="启用调试模式 (等同于 --log-level DEBUG)"
    )
    
    # 静默模式
    parser.add_argument(
        "--quiet", "-q",
        action="store_true",
        help="静默模式，减少输出信息"
    )
    
    return parser


def merge_configs(args: argparse.Namespace, file_config: Dict[str, Any], env_config: Dict[str, Any]) -> argparse.Namespace:
    """合并配置，优先级: 命令行参数 > 环境变量 > 配置文件 > 默认值
    
    Args:
        args: 命令行参数
        file_config: 配置文件内容
        env_config: 环境变量配置
        
    Returns:
        合并后的配置
    """
    # 创建配置字典，按优先级合并
    merged_config = {}
    
    # 1. 默认值（已在 argparse 中设置）
    # 2. 配置文件
    merged_config.update(file_config)
    # 3. 环境变量
    merged_config.update(env_config)
    # 4. 命令行参数（最高优先级）
    for key, value in vars(args).items():
        if value is not None:
            # 对于布尔值，只有显式设置才覆盖
            if isinstance(value, bool) and key in ['debug', 'quiet']:
                if getattr(args, key):  # 只有为 True 时才覆盖
                    merged_config[key] = value
            else:
                merged_config[key] = value
    
    # 更新 args 对象
    for key, value in merged_config.items():
        if hasattr(args, key):
            setattr(args, key, value)
    
    return args


def main() -> None:
    """主入口函数"""
    parser = create_parser()
    args = parser.parse_args()
    
    logger = None
    
    try:
        # 加载配置文件
        file_config = {}
        if args.config:
            try:
                file_config = load_config_file(args.config)
            except (FileNotFoundError, json.JSONDecodeError) as e:
                print(f"配置文件错误: {e}", file=sys.stderr)
                sys.exit(1)
        
        # 获取环境变量配置
        env_config = get_env_config()
        
        # 合并配置
        args = merge_configs(args, file_config, env_config)
        
        # 调试模式自动设置日志级别
        if args.debug:
            args.log_level = "DEBUG"
        
        # 静默模式设置
        if args.quiet and args.log_level == "INFO":
            args.log_level = "WARNING"
        
        # 验证参数
        validate_args(args)
        
        # 设置日志
        log_file = None
        if args.transport == "http" or args.log_file:
            log_file = args.log_file or "icost_mcp_server.log"
        
        logger = setup_logging(args.log_level, log_file)
        
        # 启动信息
        if not args.quiet:
            logger.info(f"iCost MCP Server v{__version__} 启动中...")
            logger.info(f"传输模式: {args.transport}")
            if args.transport == "http":
                logger.info(f"服务地址: http://{args.host}:{args.port}")
            logger.info(f"日志级别: {args.log_level}")
        
        # 启动服务器
        if args.transport == "stdio":
            # STDIO模式 - 用于MCP客户端
            if logger and not args.quiet:
                logger.info("启动 STDIO 模式服务器...")
            mcp.run()
        else:
            # HTTP模式 - 用于测试和调试
            if logger and not args.quiet:
                logger.info(f"启动 HTTP 服务器在 {args.host}:{args.port}...")
            mcp.run(transport="http", host=args.host, port=args.port)
            
    except KeyboardInterrupt:
        if logger and not args.quiet:
            logger.info("服务器被用户中断")
        sys.exit(0)
    except ValueError as e:
        error_msg = f"参数错误: {e}"
        if logger:
            logger.error(error_msg)
        else:
            print(error_msg, file=sys.stderr)
        sys.exit(1)
    except Exception as e:
        error_msg = f"服务器错误: {e}"
        if logger:
            logger.error(error_msg, exc_info=args.debug if 'args' in locals() else False)
        else:
            print(error_msg, file=sys.stderr)
        sys.exit(1)


if __name__ == "__main__":
    main()