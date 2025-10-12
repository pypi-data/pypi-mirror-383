"""Main module to support 'python -m moon_cloud_coder' command."""

from moon_cloud_coder.main import app

if __name__ == "__main__":
    # 当通过 python -m moon_cloud_coder 调用时
    app()