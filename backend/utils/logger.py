"""日志配置模块"""
import sys
from pathlib import Path
from loguru import logger
from .config import config


def setup_logger():
    """配置日志系统"""
    # 移除默认处理器
    logger.remove()
    
    # 获取日志配置
    log_config = config.logging
    log_level = log_config.get('level', 'INFO')
    log_format = log_config.get('format')
    log_path = log_config.get('path', './data/logs/app.log')
    rotation = log_config.get('rotation', '100 MB')
    retention = log_config.get('retention', '30 days')
    
    # 确保日志目录存在
    log_file = Path(log_path)
    log_file.parent.mkdir(parents=True, exist_ok=True)
    
    # 控制台输出
    logger.add(
        sys.stdout,
        format=log_format,
        level=log_level,
        colorize=True
    )
    
    # 文件输出
    logger.add(
        log_path,
        format=log_format,
        level=log_level,
        rotation=rotation,
        retention=retention,
        encoding='utf-8',
        enqueue=True  # 异步写入
    )
    
    logger.info("日志系统初始化完成")
    return logger


# 全局日志实例
app_logger = setup_logger()
