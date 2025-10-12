"""基础使用示例"""
import sys
import os

# 添加src到Python路径
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))

from moon_cloud_coder.ai.client import QwenClient
from moon_cloud_coder.utils.config import get_api_key

def basic_example():
    """基础使用示例"""
    print("Moon-Cloud-Coder 基础使用示例")
    
    # 获取API Key
    api_key = get_api_key()
    if not api_key:
        print("未找到API Key，请先设置DASHSCOPE_API_KEY环境变量")
        return
    
    # 创建客户端
    client = QwenClient(api_key=api_key, model_name="qwen3-coder-plus")
    
    # 发送请求
    prompt = "用Python写一个快速排序算法"
    print(f"请求: {prompt}")
    
    try:
        response = client.generate(prompt)
        print(f"响应: {response}")
    except Exception as e:
        print(f"错误: {e}")

if __name__ == "__main__":
    basic_example()