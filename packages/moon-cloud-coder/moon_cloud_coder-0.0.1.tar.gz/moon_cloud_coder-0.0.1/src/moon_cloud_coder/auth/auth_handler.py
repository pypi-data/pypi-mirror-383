"""Authentication command handler for Moon-Cloud-Coder."""
import os
import sys
import threading
import time
from typing import Optional
from .qwen_oauth import get_or_init_qwen_oauth_client, QwenOAuth2Client
from .oauth_progress import QwenOAuthProgress


class AuthHandler:
    """Handler for authentication commands"""
    
    def __init__(self):
        self.oauth_client: Optional[QwenOAuth2Client] = None
    
    def select_auth_method(self):
        """Display authentication method selection interface"""
        print("\n=== Moon-Cloud-Coder 认证 ===")
        print("请选择认证方式：\n")
        print("  1. Qwen OAuth (推荐)")
        print("  2. 通过DASHSCOPE_API_KEY环境变量 (会消耗自己的token)\n")
        
        while True:
            try:
                choice = input("请输入选项 (1 或 2): ").strip()
                
                if choice == '1':
                    return self.handle_qwen_oauth()
                elif choice == '2':
                    return self.handle_api_key()
                else:
                    print("无效选项，请输入 1 或 2")
            except KeyboardInterrupt:
                print("\n认证已取消")
                sys.exit(0)
    
    def handle_qwen_oauth(self):
        """Handle Qwen OAuth authentication"""
        print("\n正在启动 Qwen OAuth 认证流程...")
        print("配置说明：")
        print(" · 每天2,000次请求，无Token限制")
        print(" · 每分钟60次请求速率限制")
        print(" · Token使用说明：Moon-Cloud-Coder 可能在每个周期内发出多个API调用，")
        print("   导致高的Token使用量（类似Claude Code）")
        
        # Create progress indicator
        progress = QwenOAuthProgress()
        
        try:
            # Initialize OAuth client which will handle the authentication process
            # We'll run this in a separate thread to allow for progress display
            auth_result = {'success': False, 'client': None}
            
            def auth_thread():
                try:
                    client = get_or_init_qwen_oauth_client()
                    auth_result['success'] = True
                    auth_result['client'] = client
                except Exception as e:
                    auth_result['success'] = False
                    auth_result['error'] = str(e)
            
            # Start authentication in background thread
            auth_thread_worker = threading.Thread(target=auth_thread)
            auth_thread_worker.start()
            
            # Monitor authentication progress
            while auth_thread_worker.is_alive():
                if progress.display_progress() == False:
                    # User has pressed enter to return to auth selection
                    break
                time.sleep(0.5)  # Update display every 0.5 seconds
            
            # Wait for auth thread to complete
            auth_thread_worker.join(timeout=1)  # Wait max 1 second
            
            if auth_result['success']:
                self.oauth_client = auth_result['client']
                print("\n✓ Qwen OAuth 认证成功！")
                print("认证凭据已保存，后续运行时将自动使用。\n")
                # Set environment variable or save configuration to indicate selected auth method
                os.environ['MOON_CLOUD_CODER_AUTH_METHOD'] = 'qwen_oauth'
                return 'qwen_oauth'
            else:
                print(f"\n✗ Qwen OAuth 认证失败: {auth_result.get('error', 'Unknown error')}")
                return None
        
        except KeyboardInterrupt:
            print("\n认证已取消")
            return None
        except Exception as e:
            print(f"\n✗ Qwen OAuth 认证过程中出现错误: {e}")
            return None
    
    def handle_api_key(self):
        """Handle API key authentication"""
        # Check if environment variable is already set
        api_key = os.getenv('DASHSCOPE_API_KEY')
        
        if api_key:
            print("\n✓ 检测到已配置的 DASHSCOPE_API_KEY 环境变量")
            print("认证成功！\n")
            os.environ['MOON_CLOUD_CODER_AUTH_METHOD'] = 'api_key'
            return 'api_key'
        else:
            print("\n未找到 DASHSCOPE_API_KEY 环境变量")
            print("请按以下方式设置:")
            print("  export DASHSCOPE_API_KEY='your-api-key'")
            print("或者在 ~/.bashrc 或 ~/.zshrc 中添加该环境变量")
            
            setup = input("\n是否现在设置? (y/n): ").strip().lower()
            if setup == 'y':
                api_key = input("请输入您的 DASHSCOPE_API_KEY: ").strip()
                if api_key:
                    os.environ['DASHSCOPE_API_KEY'] = api_key
                    print("\n✓ DASHSCOPE_API_KEY 已设置")
                    print("认证成功！\n")
                    os.environ['MOON_CLOUD_CODER_AUTH_METHOD'] = 'api_key'
                    return 'api_key'
                else:
                    print("\n未输入有效的 API Key")
                    return None
            else:
                print("\n认证已取消")
                return None


def authenticate():
    """Main authentication function"""
    handler = AuthHandler()
    return handler.select_auth_method()