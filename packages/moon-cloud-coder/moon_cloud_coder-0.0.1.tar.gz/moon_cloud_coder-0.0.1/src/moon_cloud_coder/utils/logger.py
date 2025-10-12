"""统一日志系统模块."""

import logging
import sys
import os
from typing import Optional

# 全局日志配置
class LoggerConfig:
    """日志配置类"""
    _instance = None
    _configured = False
    
    def __new__(cls):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
        return cls._instance
    
    def __init__(self):
        if not LoggerConfig._configured:
            # 根据环境变量设置默认日志级别
            default_level = logging.INFO
            if self._is_debug_mode():
                default_level = logging.DEBUG
            elif self._is_disabled_mode():
                default_level = logging.CRITICAL + 1  # 完全禁用日志
            
            self.setup_logging(level=default_level)
            LoggerConfig._configured = True
    
    def _get_log_level_from_env(self) -> int:
        """从环境变量获取日志级别"""
        level_name = os.getenv("MOON_CLOUD_CODER_LOG_LEVEL", "").upper()
        if level_name == "DEBUG":
            return logging.DEBUG
        elif level_name == "INFO":
            return logging.INFO
        elif level_name == "WARNING":
            return logging.WARNING
        elif level_name == "ERROR":
            return logging.ERROR
        elif level_name == "CRITICAL":
            return logging.CRITICAL
        else:
            # 默认行为：检查是否为调试模式
            if self._is_debug_mode():
                return logging.DEBUG
            elif self._is_disabled_mode():
                return logging.CRITICAL + 1  # 完全禁用日志
            else:
                return logging.INFO
    
    def _is_debug_mode(self) -> bool:
        """检查是否启用调试模式"""
        return os.getenv("MOON_CLOUD_CODER_DEBUG", "").lower() in ("1", "true", "yes", "on", "debug")
    
    def _is_disabled_mode(self) -> bool:
        """检查是否禁用日志记录"""
        return os.getenv("MOON_CLOUD_CODER_LOG_DISABLED", "").lower() in ("1", "true", "yes", "on")

    def setup_logging(self, level: int = logging.INFO, enable_console: bool = True):
        """设置日志记录器配置"""
        # 设置根日志记录器
        root_logger = logging.getLogger()
        root_logger.setLevel(level)
        
        # 清除现有的处理器
        for handler in root_logger.handlers[:]:
            root_logger.removeHandler(handler)
        
        # 创建格式器
        formatter = logging.Formatter(
            '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
        )
        
        if enable_console:
            # 创建控制台处理器
            console_handler = logging.StreamHandler(sys.stdout)
            console_handler.setFormatter(formatter)
            root_logger.addHandler(console_handler)
    
    def set_level(self, level: int):
        """设置日志级别"""
        logging.getLogger().setLevel(level)
    
    def enable_logging(self):
        """启用日志记录"""
        self.set_level(logging.INFO)
    
    def disable_logging(self):
        """禁用日志记录"""
        self.set_level(logging.CRITICAL + 1)  # 高于CRITICAL的级别，实际上不记录任何日志
    
    def debug_logging(self):
        """启用调试日志记录"""
        self.set_level(logging.DEBUG)


def get_logger(name: str) -> logging.Logger:
    """获取日志记录器实例"""
    return logging.getLogger(name)


def setup_logger(name: str, level: Optional[int] = None) -> logging.Logger:
    """设置并返回一个日志记录器
    
    Args:
        name: 日志记录器名称
        level: 日志级别，默认为 INFO
        
    Returns:
        配置好的日志记录器
    """
    logger = get_logger(name)
    
    if level is not None:
        logger.setLevel(level)
    else:
        # 从环境变量获取默认级别
        config = LoggerConfig()
        logger.setLevel(config._get_log_level_from_env())
    
    # 避免重复添加处理器
    if not logger.handlers:
        # 使用与全局配置相同的格式
        formatter = logging.Formatter(
            '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
        )
        handler = logging.StreamHandler(sys.stdout)
        handler.setFormatter(formatter)
        logger.addHandler(handler)
    
    return logger