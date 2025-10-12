"""Main entry point for Moon-Cloud-Coder CLI."""

from moon_cloud_coder.cli.app import app
from moon_cloud_coder.utils.logger import LoggerConfig

if __name__ == "__main__":
    # 初始化日志系统（自动根据环境变量配置）
    LoggerConfig()
    app()