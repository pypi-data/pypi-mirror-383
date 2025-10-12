"""Configuration and utility functions for Moon-Cloud-Coder."""

import os
from typing import Optional
from pathlib import Path
import json
from moon_cloud_coder.auth.qwen_oauth import QwenCredentials

def get_api_key() -> Optional[str]:
    """从环境变量获取 API Key"""
    return os.getenv("DASHSCOPE_API_KEY")

def validate_api_key() -> str:
    """验证 API Key 是否存在，不存在则提示用户"""
    api_key = get_api_key()
    if not api_key:
        print("错误: 未找到 DASHSCOPE_API_KEY 环境变量")
        print("请按以下方式设置:")
        print("  export DASHSCOPE_API_KEY='your-api-key'")
        print("或者在 ~/.bashrc 或 ~/.zshrc 中添加该环境变量")
        exit(1)
    return api_key

def has_valid_auth_config() -> bool:
    """检查是否有有效的认证配置 OAuth """
    
    # 检查是否有有效的 OAuth 凭据
    oauth_creds_path = Path.home() / '.moon-cloud-coder' / 'oauth_creds.json'
    if oauth_creds_path.exists():
        try:
            with open(oauth_creds_path, 'r', encoding='utf-8') as f:
                data = json.load(f)
                credentials = QwenCredentials.from_dict(data)
                # 检查凭据是否仍然有效
                return credentials.is_valid()
        except Exception:
            # 如果文件格式错误或无法读取，认为没有有效配置
            return False
    
    return False

def validate_auth_config() -> tuple[str, str]:
    """
    验证认证配置，返回 (auth_method, auth_value)
    auth_method: 'api_key' 或 'qwen_oauth'
    auth_value: API Key 或 OAuth 访问令牌
    """
    # 首先检查环境变量指定的认证方法
    auth_method = os.getenv('MOON_CLOUD_CODER_AUTH_METHOD', 'auto')
    
    if auth_method == 'api_key':
        # 强制使用 API Key
        api_key = get_api_key()
        if not api_key:
            print("错误: 选择了 API Key 认证方式，但未找到 DASHSCOPE_API_KEY 环境变量")
            print("请按以下方式设置:")
            print("  export DASHSCOPE_API_KEY='your-api-key'")
            print("或者在 ~/.bashrc 或 ~/.zshrc 中添加该环境变量")
            exit(1)
        return 'api_key', api_key
        
    elif auth_method == 'qwen_oauth':
        # 强制使用 Qwen OAuth
        oauth_creds_path = Path.home() / '.moon-cloud-coder' / 'oauth_creds.json'
        if not oauth_creds_path.exists():
            print("错误: 选择了 Qwen OAuth 认证方式，但未找到 OAuth 凭据")
            print("请运行 '/auth' 命令进行认证配置")
            exit(1)
        
        try:
            with open(oauth_creds_path, 'r', encoding='utf-8') as f:
                data = json.load(f)
                credentials = QwenCredentials.from_dict(data)
                if not credentials.is_valid():
                    print("错误: Qwen OAuth 凭据已过期或无效")
                    print("请运行 '/auth' 命令重新认证")
                    exit(1)
                return 'qwen_oauth', credentials.access_token
        except Exception as e:
            print(f"错误: 读取或验证 OAuth 凭据时出错: {e}")
            exit(1)
    
    else:  # auto 或其他值
        # 自动检测：如果 OAuth 凭据有效则使用 OAuth，否则检查 API Key
        oauth_creds_path = Path.home() / '.moon-cloud-coder' / 'oauth_creds.json'
        
        if oauth_creds_path.exists():
            try:
                with open(oauth_creds_path, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                    credentials = QwenCredentials.from_dict(data)
                    if credentials.is_valid():
                        return 'qwen_oauth', credentials.access_token
            except Exception:
                # 如果 OAuth 凭据文件有问题，继续检查 API Key
                pass
        
        # 如果 OAuth 无效或不存在，则检查 API Key
        api_key = get_api_key()
        if api_key:
            return 'api_key', api_key
        
        # 如果两种认证方式都无效
        print("错误: 未找到有效的认证配置")
        print("请按以下方式之一进行配置:")
        print("  1. 设置 DASHSCOPE_API_KEY 环境变量:")
        print("     export DASHSCOPE_API_KEY='your-api-key'")
        print("  2. 或运行 '/auth' 命令进行 Qwen OAuth 认证")
        exit(1)

def get_log_level() -> str:
    """从环境变量获取日志级别"""
    return os.getenv("MOON_CLOUD_CODER_LOG_LEVEL", "INFO").upper()

def is_debug_mode() -> bool:
    """检查是否启用调试模式"""
    return os.getenv("MOON_CLOUD_CODER_DEBUG", "").lower() in ("1", "true", "yes", "on")