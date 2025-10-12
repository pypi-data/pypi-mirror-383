"""Moon-Cloud-Coder: AI-powered command line tool for developers."""

__version__ = "0.0.1"
__author__ = "Moon Cloud Coder Team"
__description__ = "AI-powered command line tool for developers using Qwen models"

# 导入主要模块
from .ai.client import QwenClient
from .cli.app import app
from .auth.auth_handler import authenticate
from .utils.config import validate_api_key, get_api_key
from .utils.logger import LoggerConfig, get_logger

__all__ = [
    "QwenClient",
    "app",
    "authenticate",
    "validate_api_key",
    "get_api_key",
    "LoggerConfig",
    "get_logger"
]