"""AI client for interacting with Qwen models using OAuth access tokens."""

import dashscope
from typing import Dict, Any, Optional
from dashscope import Generation
import os
import logging
import requests
from moon_cloud_coder.utils.logger import get_logger
from openai import OpenAI
from pathlib import Path
import json
from moon_cloud_coder.auth.qwen_oauth import QwenOAuth2Client, get_or_init_qwen_oauth_client


class QwenClient:
    def __init__(self, api_key: str = None, model_name: str = "qwen3-coder-plus", auth_method: str = "api_key"):
        """
        初始化 Qwen 客户端
        
        Args:
            api_key: DashScope API Key (可选，如果使用OAuth则不需要)
            model_name: 使用的模型名称，默认为 qwen3-coder-plus
            auth_method: 认证方式 ("api_key" 或 "qwen_oauth")
        """
        self.model_name = model_name
        self.auth_method = auth_method
        self.logger = get_logger(__name__)
        
        if auth_method == "qwen_oauth":
            # 使用 Qwen OAuth 认证 - 通过Qwen API端点
            self.oauth_client = get_or_init_qwen_oauth_client()
            self.access_token = self.oauth_client.get_access_token()
            if not self.access_token:
                raise Exception("无法获取有效的 Qwen OAuth 访问令牌")
            
            self.logger.debug(f"QwenClient 使用 Qwen OAuth 初始化，模型: {model_name}")
            
            # 对于OAuth认证，我们仍保留OpenAI客户端以便在必要时使用DashScope
            # 但主要使用Qwen API端点
            # 注意：即使使用OAuth令牌，OpenAI客户端仍然会连接到DashScope兼容端点
            # 但我们主要通过 _generate_with_qwen_api 方法直接调用Qwen端点
            self.qwen_api_base = "https://dashscope.aliyuncs.com/compatible-mode/v1"
            self.openai_client = OpenAI(
                api_key=self.access_token,
                base_url=self.qwen_api_base,
            )
            
            # Store the current resource URL from credentials
            current_credentials = self.oauth_client.token_manager.get_current_credentials()
            if current_credentials and hasattr(current_credentials, 'resource_url'):
                self.resource_url = current_credentials.resource_url
                self.logger.info(f"初始化QwenClient，使用 resource_url: {self.resource_url}")
            else:
                self.resource_url = "chat.qwen.ai"  # fallback to default
                self.logger.warning(f"无法从凭证中获取 resource_url，使用默认值: {self.resource_url}")
            
        else:
            # 使用 API Key 认证
            if not api_key:
                # 如果没有提供api_key参数，尝试从环境变量获取
                api_key = os.getenv('DASHSCOPE_API_KEY')
                if not api_key:
                    raise ValueError("使用 API Key 认证时必须提供 api_key 或设置 DASHSCOPE_API_KEY 环境变量")
                else:
                    self.logger.debug("从 DASHSCOPE_API_KEY 环境变量获取API Key")
            
            self.api_key = api_key
            dashscope.api_key = api_key
            
            # 初始化 OpenAI 兼容客户端
            self.openai_client = OpenAI(
                api_key=api_key,
                base_url="https://dashscope.aliyuncs.com/compatible-mode/v1",
            )
            self.logger.debug(f"QwenClient 使用 API Key 初始化，模型: {model_name}")
            self.logger.debug(f"API Key (前20位): {api_key[:20]}..." if api_key else "No API Key")
            self.logger.debug(f"使用API端点: https://dashscope.aliyuncs.com/compatible-mode/v1")
        
        # 检查并加载 MoonCloud.md 配置
        self.mooncloud_config = self._load_mooncloud_config()
    
    def _load_mooncloud_config(self) -> dict:
        """加载 MoonCloud.md 配置文件"""
        config = {
            'custom_instructions': '',
            'file_extensions': ['.py', '.js', '.ts', '.java', '.cpp', '.c', '.html', '.css', '.json', '.md'],
            'max_file_size': 1000000  # 1MB
        }
        
        mooncloud_file = Path("MoonCloud.md")
        if mooncloud_file.exists():
            try:
                with open(mooncloud_file, 'r', encoding='utf-8') as f:
                    content = f.read()
                    # 提取自定义指令部分（如果存在）
                    if '## Custom Instructions' in content:
                        start = content.find('## Custom Instructions') + len('## Custom Instructions')
                        end = content.find('\n## ', start)  # 查找下一个标题
                        if end == -1:  # 如果没有下一个标题，则取到文件末尾
                            end = len(content)
                        config['custom_instructions'] = content[start:end].strip()
                self.logger.info("成功加载 MoonCloud.md 配置")
            except Exception as e:
                self.logger.error(f"加载 MoonCloud.md 配置时出错: {e}")
        
        return config
    
    def _enhance_prompt_with_context(self, prompt: str) -> str:
        """根据配置增强提示词"""
        enhanced_prompt = prompt
        
        # 添加自定义指令（如果存在）
        if self.mooncloud_config.get('custom_instructions'):
            enhanced_prompt = f"{self.mooncloud_config['custom_instructions']}\n\n用户问题: {prompt}"
        
        return enhanced_prompt
    
    def _build_api_url(self) -> str:
        """
        构建API端点URL
        原因：统一处理URL构建逻辑，避免重复代码
        """
        if self.resource_url.startswith(('http://', 'https://')):
            base_url = self.resource_url
        else:
            base_url = f"https://{self.resource_url}"
        
        if base_url.endswith('/v1'):
            normalized_base_url = base_url
        else:
            if base_url.endswith('/'):
                normalized_base_url = f"{base_url}v1"
            else:
                normalized_base_url = f"{base_url}/v1"
        
        return f"{normalized_base_url}/chat/completions"

    def _parse_api_response(self, response_data: dict) -> str:
        """
        解析API响应数据
        原因：统一处理不同格式的API响应，避免重复解析逻辑
        """
        if 'choices' in response_data and len(response_data['choices']) > 0:
            return response_data['choices'][0]['message']['content']
        elif 'result' in response_data and 'choices' in response_data['result']:
            return response_data['result']['choices'][0]['message']['content']
        elif 'message' in response_data:
            return response_data['message']
        else:
            return response_data.get('response', str(response_data))

    def _make_qwen_api_request(self, headers: dict, data: dict) -> str:
        """
        执行Qwen API请求并返回结果
        原因：统一处理API请求逻辑，避免重复代码
        """
        # 使用公共函数构建API URL
        url = self._build_api_url()
        self.logger.debug(f"使用OpenAI兼容API端点: {url}")
        
        # 记录实际使用的URL
        self.logger.debug(f"实际使用的API端点: {url}")
        
        try:
            self.logger.debug(f"发送请求到: {url}")
            self.logger.debug(f"请求头: {headers}")
            response = requests.post(url, headers=headers, json=data)
            self.logger.debug(f"响应状态码: {response.status_code}")
            self.logger.debug(f"响应内容: {response.text}")
            response.raise_for_status()
            
            response_data = response.json()
            self.logger.debug(f"Qwen API 响应: {response_data}")
            
            # 使用公共函数解析响应
            result = self._parse_api_response(response_data)
            
            return result
        except Exception as e:
            self.logger.error(f"Qwen API 请求过程中发生异常: {str(e)}")
            raise e

    def generate(self, prompt: str) -> str:
        """
        生成模型响应
        
        Args:
            prompt: 输入提示
            
        Returns:
            模型生成的文本
        """
        self.logger.info(f"开始生成响应，认证方式: {self.auth_method}, 模型名称: {self.model_name}")
        self.logger.debug(f"原始提示: {prompt[:100]}..." if len(prompt) > 100 else f"原始提示: {prompt}")
        
        # 增强提示词
        enhanced_prompt = self._enhance_prompt_with_context(prompt)
        
        self.logger.debug(f"增强后提示: {enhanced_prompt[:100]}..." if len(enhanced_prompt) > 100 else f"增强后提示: {enhanced_prompt}")
        
        # 如果是OAuth认证，始终使用Qwen的API端点
        if self.auth_method == "qwen_oauth":
            self.logger.debug(f"generate方法: auth_method为qwen_oauth，调用 _generate_with_qwen_api")
            return self._generate_with_qwen_api(enhanced_prompt)
        elif self.auth_method == "api_key":
            self.logger.debug(f"generate方法: auth_method为api_key，model_name为{self.model_name}，调用 _generate_with_openai_api")
            return self._generate_with_openai_api(enhanced_prompt)
        elif self.model_name in ["qwen3-coder-plus", "qwen-turbo", "qwen-plus", "qwen-max", "qwen2.5-72b-instruct"]:
            self.logger.debug(f"generate方法: auth_method为{self.auth_method}，model_name在兼容列表中，调用 _generate_with_openai_api")
            return self._generate_with_openai_api(enhanced_prompt)
        else:
            self.logger.debug(f"generate方法: auth_method为{self.auth_method}，model_name不在兼容列表中，调用 _generate_with_dashscope_api")
            # 对于其他模型，尝试使用旧的 Generation API
            return self._generate_with_dashscope_api(enhanced_prompt)
    
    def _generate_with_qwen_api(self, prompt: str) -> str:
        """
        使用 Qwen API 生成模型响应（通过OAuth访问令牌）
        
        Args:
            prompt: 输入提示
            
        Returns:
            模型生成的文本
        """
        # Update access token from credentials to ensure we have the latest one
        self.access_token = self.oauth_client.get_access_token()
        if not self.access_token:
            raise Exception("无法获取有效的 Qwen OAuth 访问令牌")
        
        # Update resource URL from credentials to ensure we have the latest one
        current_credentials = self.oauth_client.token_manager.get_current_credentials()
        if current_credentials and hasattr(current_credentials, 'resource_url') and current_credentials.resource_url:
            self.resource_url = current_credentials.resource_url
            self.logger.info(f"更新 resource_url 从凭证: {self.resource_url}")
        else:
            self.logger.warning(f"无法从凭证获取新的 resource_url，保持当前值: {self.resource_url}")
        
        self.logger.info(f"使用 Qwen API 向模型 {self.model_name} 发送请求（OAuth认证）: {prompt}")
        
        # 尝试构造一个直接的API请求，使用OAuth访问令牌
        headers = {
            'Authorization': f'Bearer {self.access_token}',
            'Content-Type': 'application/json',
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
        }
        
        # 使用公共函数构建API URL
        url = self._build_api_url()
        self.logger.debug(f"使用OpenAI兼容API端点: {url}")
        
        # 记录实际使用的URL
        self.logger.debug(f"实际使用的API端点: {url}")
        
        # 根据参考代码使用更标准的API格式
        data = {
            'model': self.model_name,
            'messages': [
                {'role': 'user', 'content': prompt}
            ],
            'temperature': 0.7,
            'max_tokens': 2000
        }
        
        self.logger.debug(f"Qwen API 请求数据: {data}")
        self.logger.debug(f"当前访问令牌: {self.access_token[:20]}..." if self.access_token else 'No token')
        
        try:
            self.logger.debug(f"发送请求到: {url}")
            self.logger.debug(f"请求头: {headers}")
            response = requests.post(url, headers=headers, json=data)
            self.logger.debug(f"响应状态码: {response.status_code}")
            self.logger.debug(f"响应内容: {response.text}")
            response.raise_for_status()
            
            response_data = response.json()
            self.logger.debug(f"Qwen API 响应: {response_data}")
            
            # 使用公共函数解析响应
            result = self._parse_api_response(response_data)
            
            if result:
                result_length = len(result) if result is not None else 0
                self.logger.info(f"成功获取模型响应，长度: {result_length} 字符")
                self.logger.debug(f"模型响应内容: {result}")
                return result
            else:
                error_msg = f"Qwen API 响应中的文本字段为 None"
                self.logger.error(error_msg)
                raise Exception(error_msg)
                
        except requests.exceptions.HTTPError as e:
            if response.status_code in [401, 403]:  # 认证错误
                self.logger.info("检测到认证错误，尝试刷新OAuth令牌...")
                
                # 如果是OAuth认证方式，尝试刷新令牌
                if self.auth_method == "qwen_oauth":
                    try:
                        # 强制刷新令牌
                        new_credentials = self.oauth_client.token_manager.get_valid_credentials(self.oauth_client, force_refresh=True)
                        if new_credentials:
                            self.access_token = new_credentials.access_token
                            # Also update resource_url from refreshed credentials
                            if hasattr(new_credentials, 'resource_url') and new_credentials.resource_url:
                                self.resource_url = new_credentials.resource_url
                                self.logger.info(f"同时更新 resource_url 从刷新的凭证: {self.resource_url}")
                            
                            self.logger.info("OAuth令牌已成功刷新，重试请求...")
                            
                            # 更新headers中的认证令牌
                            headers['Authorization'] = f'Bearer {self.access_token}'
                            
                            # 使用公共方法重试请求
                            result = self._make_qwen_api_request(headers, data)
                            
                            if result:
                                result_length = len(result) if result is not None else 0
                                self.logger.info(f"重试成功，获取模型响应，长度: {result_length} 字符")
                                return result
                            else:
                                error_msg = f"重试后，Qwen API 响应中的文本字段仍为 None"
                                self.logger.error(error_msg)
                                raise Exception(error_msg)
                                
                    except Exception as refresh_error:
                        self.logger.error(f"刷新OAuth令牌失败: {refresh_error}")
                        # 尝试重新初始化OAuth客户端来获取新令牌
                        try:
                            self.logger.info("尝试重新初始化OAuth客户端...")
                            self.oauth_client = get_or_init_qwen_oauth_client()
                            new_access_token = self.oauth_client.get_access_token()
                            if new_access_token:
                                self.access_token = new_access_token
                                # Also update resource_url after re-initialization
                                current_credentials = self.oauth_client.token_manager.get_current_credentials()
                                if current_credentials and hasattr(current_credentials, 'resource_url') and current_credentials.resource_url:
                                    self.resource_url = current_credentials.resource_url
                                    self.logger.info(f"重新初始化后更新 resource_url: {self.resource_url}")
                                
                                # 更新headers中的认证令牌
                                headers['Authorization'] = f'Bearer {self.access_token}'
                                
                                # 使用公共方法重试请求
                                result = self._make_qwen_api_request(headers, data)
                                
                                if result:
                                    result_length = len(result) if result is not None else 0
                                    self.logger.info(f"重试成功，获取模型响应，长度: {result_length} 字符")
                                    return result
                                else:
                                    error_msg = f"重试后，Qwen API 响应中的文本字段仍为 None"
                                    self.logger.error(error_msg)
                                    raise Exception(error_msg)
                        except Exception as reauth_error:
                            self.logger.error(f"重新认证也失败了: {reauth_error}")
                        
                        # 如果上述方法都失败了，抛出原始错误
                        raise e
                else:
                    raise e
            else:
                self.logger.error(f"Qwen API 请求失败: {response.status_code} - {response.text}")
                # 详细记录错误响应
                try:
                    error_response = response.json()
                    self.logger.error(f"详细错误信息: {error_response}")
                except:
                    self.logger.error(f"无法解析错误响应为JSON: {response.text}")
                raise e
        except Exception as e:
            self.logger.error(f"Qwen API 生成过程中发生异常: {str(e)}")
            raise e

    def _generate_with_openai_api(self, prompt: str) -> str:
        """
        使用 OpenAI 兼容 API 生成模型响应
        """
        self.logger.info(f"使用 OpenAI 兼容 API 向模型 {self.model_name} 发送请求: {prompt}")
        
        self.logger.debug(f"当前方法: _generate_with_openai_api，auth_method为{self.auth_method}，使用OpenAI客户端")
        self.logger.debug(f"OpenAI客户端base_url: {self.openai_client.base_url}")
        self.logger.debug(f"API Key (前20位): {self.api_key[:20]}..." if self.api_key else "No API Key")
        
        try:
            self.logger.debug(f"准备调用OpenAI客户端，模型: {self.model_name}")
            response = self.openai_client.chat.completions.create(
                model=self.model_name,
                messages=[
                    {'role': 'system', 'content': 'You are a helpful assistant.'},
                    {'role': 'user', 'content': prompt}
                ]
            )
            
            self.logger.debug(f"OpenAI API 响应: {response}")
            
            if response.choices and len(response.choices) > 0:
                result = response.choices[0].message.content
                if result:
                    result_length = len(result) if result is not None else 0
                    self.logger.info(f"成功获取模型响应，长度: {result_length} 字符")
                    self.logger.debug(f"模型响应内容: {result}")
                    return result
                else:
                    error_msg = f"OpenAI API 响应中的文本字段为 None"
                    self.logger.error(error_msg)
                    raise Exception(error_msg)
            else:
                error_msg = f"OpenAI API 响应中没有 choices 或 choices 为空"
                self.logger.error(error_msg)
                raise Exception(error_msg)
                
        except Exception as e:
            self.logger.error(f"OpenAI API 调用异常: {str(e)}")
            # 检查是否是认证错误
            error_str = str(e).lower()
            if ('unauthorized' in error_str or 
                'forbidden' in error_str or 
                'invalid api key' in error_str or 
                'invalid access token' in error_str or
                '401' in error_str or
                '403' in error_str):
                
                self.logger.info("检测到可能是认证错误...")
                
                # 对于API Key认证方式，尝试检查API Key有效性
                if self.auth_method == "api_key":
                    self.logger.info("检测到API Key认证方式，重新检查API Key...")
                    # Note: We can't directly refresh an API key like OAuth, but we can log the issue
                    self.logger.error("API Key认证失败，请检查DASHSCOPE_API_KEY环境变量是否正确设置")
                    raise e
                else:
                    # 对于其他认证方式，直接重新抛出异常
                    raise e
            else:
                # 非认证错误，重新抛出异常
                self.logger.error(f"非认证错误，重新抛出异常: {str(e)}")
                raise e
    
    def _generate_with_dashscope_api(self, prompt: str) -> str:
        """
        使用 DashScope API 生成模型响应（旧方法）
        
        Args:
            prompt: 输入提示
            
        Returns:
            模型生成的文本
        """
        self.logger.info(f"使用 DashScope API 向模型 {self.model_name} 发送请求: {prompt}")
        if self.api_key:
            self.logger.debug(f"API Key (前20位): {self.api_key[:20]}...")
        
        try:
            # 记录模型调用请求
            self.logger.debug(f"调用模型 {self.model_name}")
            response = Generation.call(
                model=self.model_name,
                prompt=prompt
            )
            self.logger.debug(f"模型响应: {response}")
            # 记录 API 响应
            self.logger.debug(f"API 响应状态码: {response.status_code}")
            if hasattr(response, 'code'):
                self.logger.debug(f"API 响应代码: {response.code}")
            if hasattr(response, 'message'):
                self.logger.debug(f"API 响应消息: {response.message}")
            
            # 记录响应输出
            if hasattr(response, 'output'):
                self.logger.debug(f"API 响应输出: {response.output}")
            
            if response.status_code == 200:
                self.logger.debug("API 调用成功")
                
                # 检查响应结构并提取文本
                if hasattr(response, 'output') and response.output is not None:
                    if hasattr(response.output, 'text') and response.output.text is not None:
                        result = response.output.text
                        result_length = len(result) if result is not None else 0
                        self.logger.info(f"成功获取模型响应，长度: {result_length} 字符")
                        self.logger.debug(f"模型响应内容: {result}")
                        return result
                    elif isinstance(response.output, dict) and 'text' in response.output:  # 某些响应可能是字典格式
                        result = response.output['text']
                        if result is not None:
                            result_length = len(result) if result is not None else 0
                            self.logger.info(f"成功获取模型响应，长度: {result_length} 字符")
                            self.logger.debug(f"模型响应内容: {result}")
                            return result
                        else:
                            error_msg = f"API 响应中的文本字段为 None"
                            self.logger.error(error_msg)
                            # 记录完整的响应内容用于调试
                            self.logger.debug(f"完整响应对象: {response}")
                            if hasattr(response, 'output'):
                                self.logger.debug(f"响应输出对象: {response.output}")
                            raise Exception(error_msg)
                    else:
                        error_msg = f"API 响应格式错误: 缺少 'text' 字段或字段值为 None"
                        self.logger.error(error_msg)
                        # 记录完整的响应内容用于调试
                        self.logger.debug(f"完整响应对象: {response}")
                        if hasattr(response, 'output'):
                            self.logger.debug(f"响应输出对象: {response.output}")
                        raise Exception(error_msg)
                else:
                    error_msg = f"API 响应格式错误: 缺少 'output' 字段或为 None"
                    self.logger.error(error_msg)
                    # 记录完整的响应内容用于调试
                    self.logger.debug(f"完整响应对象: {response}")
                    raise Exception(error_msg)
            else:
                # 如果 API 调用失败，提供详细错误信息
                error_msg = f"API 调用失败: {response.code} - {response.message}"
                self.logger.error(error_msg)
                
                if response.code == "InvalidParameter.ModelNotFound":
                    error_msg += f"\n提示: 模型 '{self.model_name}' 可能不可用，请检查模型名称是否正确"
                    self.logger.warning(f"模型 {self.model_name} 未找到")
                
                raise Exception(error_msg)
                
        except Exception as e:
            # 捕获并重新抛出异常，提供更友好的错误信息
            self.logger.error(f"DashScope API 生成过程中发生异常: {str(e)}")
            raise e