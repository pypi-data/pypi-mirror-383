"""CLI application logic for Moon-Cloud-Coder."""

import typer
from typing import Optional
import os
from pathlib import Path
from rich.console import Console
from rich.panel import Panel
from rich.text import Text
from rich.prompt import Prompt
from rich import print as rprint
from moon_cloud_coder.ai.client import QwenClient
from moon_cloud_coder.auth.auth_handler import authenticate
from moon_cloud_coder.utils.config import validate_api_key, get_api_key, validate_auth_config
from moon_cloud_coder.utils.logger import get_logger, LoggerConfig

# LoggerConfig 现在会自动根据环境变量设置日志级别
LoggerConfig()

app = typer.Typer()
logger = get_logger(__name__)
console = Console()

def show_welcome(model: str):
    """显示欢迎界面"""
    # 获取当前工作目录和 API Key
    current_dir = Path.cwd()
    api_key = get_api_key()
    if api_key and len(api_key) > 8:
        masked_api_key = api_key[:5] + "..." + api_key[-4:]
    else:
        masked_api_key = "未配置"
    
    # 创建欢迎信息面板
    welcome_content = Text()
    welcome_content.append("🚀 欢迎使用 Moon Cloud Coder! v0.0.1\n", style="bold #6699FF")
    welcome_content.append(f"当前目录：{current_dir}\n") 
    dir_content = f"当前目录：{current_dir}"
    welcome_content.append("─" * (len(dir_content)+5)+ "\n")
    welcome_content.append("环境变量配置:\n")
    welcome_content.append(f"• API Key: {masked_api_key}\n")
    welcome_content.append("• API Base URL: https://dashscope.aliyuncs.com/compatible-mode/v1\n")
    welcome_content.append("\n输入 /help 获取帮助，/exit 退出")
    
    console.print(Panel(welcome_content,expand=False))

def show_tips():
    """显示小贴士"""
    tips_content = Text()
    tips_content.append("💡 小贴士:\n", style="bold #6699FF")
    tips_content.append("• 多行输入: Ctrl + Enter\n", style="white")
    tips_content.append("• 自定义交互: 创建 ", style="white")
    tips_content.append("MoonCloud.md", style="bold #6699FF")
    tips_content.append(" 文件\n", style="white")
    tips_content.append("• 获取帮助: 输入 /docs", style="white")
    
    console.print(Panel(tips_content, expand=False))

def is_command(text: str) -> bool:
    """检查输入是否为命令"""
    return text.startswith('/')

def handle_command(command: str, model: str) -> bool:
    global client
    """处理命令，返回是否应退出"""
    command = command.strip().lower()
    
    if command in ['/exit', '/quit', 'quit', 'exit']:
        console.print("[bold #6699FF]感谢使用 Moon-Cloud-Coder！再见！[/bold #6699FF]")
        return True
    elif command == '/help':
        help_text = Text()
        help_text.append("可用命令：\n", style="bold yellow")
        help_text.append("  /help - 显示此帮助\n", style="white")
        help_text.append("  /auth - 更改认证方式\n", style="white")
        help_text.append("  /exit - 退出程序\n", style="white")
        help_text.append("  /docs - 获取文档\n", style="white")
        help_text.append("  /config - 显示配置信息\n", style="white")
        console.print(Panel(help_text, title="帮助", border_style="cyan"))
    elif command == '/auth':
        console.print("[bold yellow] auth 正在启动认证流程...[/bold yellow]")
        auth_result = authenticate()
        console.print(f"[bold yellow] auth 认证结果: {auth_result} [/bold yellow]")
        if auth_result:
            client = QwenClient(auth_method=auth_result, model_name=model)
            console.print(f"[green]认证成功！当前使用认证方式: {auth_result}[/green]")
        else:
            console.print("[red]认证失败或已取消[/red]")   
    elif command == '/docs':
        console.print(Panel("📖 文档: https://github.com/your-repo/moon-cloud-coder/docs", title="文档", border_style="blue"))
    elif command == '/config':
        current_dir = Path.cwd()
        api_key = get_api_key()
        if api_key and len(api_key) > 8:
            masked_api_key = api_key[:5] + "..." + api_key[-4:]
        else:
            masked_api_key = "未配置"
        
        config_content = Text()
        config_content.append(f"当前目录: {current_dir}\n", style="white")
        config_content.append(f"API Key: {masked_api_key}\n", style="white")
        config_content.append(f"模型: {model}\n", style="white")
        console.print(Panel(config_content, title="配置信息", border_style="magenta"))
    else:
        console.print(f"[yellow]未知命令: {command}，输入 /help 查看帮助[/yellow]")
    
    return False

client = None
def interactive_mode(model: str):
    """启动交互式对话模式."""
    logger.info(f"启动交互式对话模式，模型: {model}")
    global client  # 声明使用全局变量 client
    
    # 验证认证配置
    try:
        auth_method, auth_value = validate_auth_config()
        
        if auth_method == 'qwen_oauth':
            # 使用 OAuth 认证
            client = QwenClient(model_name=model, auth_method='qwen_oauth')
        else:
            # 使用 API Key 认证
            client = QwenClient(auth_value, model, auth_method='api_key')
    except SystemExit:
        # 当没有有效的认证配置时，仍启动交互模式，但显示提醒
        console.print("[yellow]⚠ 未检测到有效的认证配置。请使用 /auth 命令进行认证设置。[/yellow]")
        # 创建一个临时客户端，仅用于处理命令（如 /auth）
        # 但在尝试生成内容时会提示用户先进行认证
        class DummyClient:
            def generate(self, prompt: str):
                raise Exception("请先使用 /auth 命令配置认证信息")
        
        client = DummyClient()
    
    # 显示界面元素
    show_welcome(model)
    show_tips()
    
    while True:
        try:
            # 使用 Rich 的提示输入 - 简化界面，合并输入提示
            user_input = Prompt.ask("[bold blue]>  输入您的消息 或 @路径/文件[/bold blue]")
            logger.debug(f"收到用户输入: {user_input[:30]}...")
            
            # 检查是否为命令
            if is_command(user_input):
                if handle_command(user_input, model):
                    break
                continue
            
            # 检查是否包含文件引用
            if user_input.strip().startswith('@'):
                # 处理文件引用逻辑
                file_path = user_input.strip()[1:]  # 去掉 '@' 符号
                try:
                    with open(file_path, 'r', encoding='utf-8') as f:
                        file_content = f.read()
                    user_input = f"请分析以下文件内容:\n文件路径: {file_path}\n文件内容:\n{file_content}"
                    console.print(f"[cyan]已加载文件: {file_path}[/cyan]")
                except FileNotFoundError:
                    console.print(f"[red]文件未找到: {file_path}[/red]")
                    continue
                except Exception as e:
                    console.print(f"[red]读取文件时出错: {str(e)}[/red]")
                    continue
            
            # 使用粗边框面板显示用户输入
            console.print(Panel(user_input, title="[bold green]User[/bold green]", border_style="bright_green", style="bold"))
            
            logger.info(f"向模型发送请求: {user_input[:50]}...")
            try:
                response = client.generate(user_input)
                logger.info("收到模型响应")
                
                # 使用粗边框面板显示 AI 响应
                console.print(Panel(response, title="[bold cyan]Moon-Cloud-Coder[/bold cyan]", border_style="bright_cyan", style="bold"))
            except Exception as e:
                error_msg = str(e)
                if "请先使用 /auth 命令配置认证信息" in error_msg:
                    console.print(f"[red]请先使用 /auth 命令配置认证信息[/red]")
                else:
                    console.print(f"[red]错误: {str(e)}[/red]")
            
        except KeyboardInterrupt:
            console.print("\n[bold green]再见![/bold green]")
            logger.info("用户中断操作")
            break
        except Exception as e:
            error_msg = f"交互模式中发生错误: {str(e)}"
            console.print(f"[red]错误: {str(e)}[/red]")
            logger.error(error_msg)
            break

@app.command()
def run(
    prompt: Optional[str] = typer.Option(None, "-p", "--prompt", help="非交互式模式下的提示语"),
    model: str = typer.Option("qwen3-coder-plus", "--model", "-m", help="使用的模型名称")
):
    """
    Moon-Cloud-Coder - AI-powered command line tool for developers
    """
    logger.info(f"启动 Moon-Cloud-Coder，模型: {model}")
    
    if prompt:
        # 非交互模式
        logger.debug(f"运行在非交互模式，提示: {prompt[:50]}...")
        
        try:
            # 验证认证配置
            auth_method, auth_value = validate_auth_config()
            
            if auth_method == 'qwen_oauth':
                # 使用 OAuth 认证
                client = QwenClient(model_name=model, auth_method='qwen_oauth')
            else:
                # 使用 API Key 认证
                client = QwenClient(auth_value, model, auth_method='api_key')
            
            try:
                response = client.generate(prompt)
                rprint(response)  # 使用 Rich 打印
            except Exception as e:
                error_msg = f"非交互模式中发生错误: {str(e)}"
                rprint(f"[red]错误: {str(e)}[/red]")
                logger.error(error_msg)
                raise typer.Exit(code=1)
        except SystemExit:
            # 当没有有效的认证配置时，提示用户并退出
            console.print("[red]错误: 未找到有效的认证配置[/red]")
            console.print("[yellow]请按以下方式之一进行配置:[/yellow]")
            console.print("[yellow]  1. 设置 DASHSCOPE_API_KEY 环境变量:[/yellow]")
            console.print("[yellow]     export DASHSCOPE_API_KEY='your-api-key'[/yellow]")
            console.print("[yellow]  2. 或运行 'moon-cloud-coder' 进入交互模式，然后使用 /auth 命令进行 Qwen OAuth 认证[/yellow]")
            raise typer.Exit(code=1)
    else:
        # 交互模式
        logger.debug("运行在交互模式")
        interactive_mode(model)