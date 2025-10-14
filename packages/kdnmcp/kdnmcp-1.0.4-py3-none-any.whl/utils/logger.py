"""日志配置工具"""

import sys
from loguru import logger
from typing import Optional
from settings import config


def setup_logger(log_level: Optional[str] = None, log_format: Optional[str] = None) -> None:
    """配置日志系统
    
    Args:
        log_level: 日志级别，默认从配置文件读取
        log_format: 日志格式，默认从配置文件读取
    """
    # 移除默认的日志处理器
    logger.remove()
    
    # 使用配置文件中的设置或传入的参数
    level = log_level or config.log.level
    format_type = log_format or config.log.format
    
    # 根据格式类型选择日志格式
    if format_type.lower() == 'json':
        # 对于JSON格式，使用简单的格式字符串，让serialize参数处理JSON转换
        log_format_str = "{time:YYYY-MM-DD HH:mm:ss.SSS} | {level} | {name}:{function}:{line} - {message}"
    else:
        log_format_str = (
            "<green>{time:YYYY-MM-DD HH:mm:ss.SSS}</green> | "
            "<level>{level: <8}</level> | "
            "<cyan>{name}</cyan>:<cyan>{function}</cyan>:<cyan>{line}</cyan> - "
            "<level>{message}</level>"
        )
    
    # 添加控制台处理器
    logger.add(
        sys.stdout,
        format=log_format_str,
        level=level,
        colorize=format_type.lower() != 'json',
        serialize=format_type.lower() == 'json'
    )
    
    # 添加文件处理器
    logger.add(
        "logs/kdniao_mcp_{time:YYYY-MM-DD}.log",
        format=log_format_str,
        level=level,
        rotation="1 day",
        retention="30 days",
        compression="zip",
        serialize=format_type.lower() == 'json'
    )
    
    # 添加错误日志文件处理器
    logger.add(
        "logs/kdniao_mcp_error_{time:YYYY-MM-DD}.log",
        format=log_format_str,
        level="ERROR",
        rotation="1 day",
        retention="30 days",
        compression="zip",
        serialize=format_type.lower() == 'json'
    )
    
    logger.info(f"Logger initialized with level: {level}, format: {format_type}")


def get_logger():
    """获取日志记录器实例
    
    Returns:
        配置好的日志记录器
    """
    return logger


# 创建全局日志记录器实例
app_logger = get_logger()