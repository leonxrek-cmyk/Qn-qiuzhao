from openai import OpenAI
import requests
import json
import datetime
import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from config import Config

class AIService:
    def __init__(self):
        # 初始化配置
        self.base_url = Config.QINIU_AI_BASE_URL
        self.api_key = Config.QINIU_AI_API_KEY
        self.default_model = Config.DEFAULT_MODEL
        
        # 加载代理配置（如果有）
        self.proxies = {
            'http': os.getenv('HTTP_PROXY'),
            'https': os.getenv('HTTPS_PROXY')
        }
        # 移除空代理配置
        self.proxies = {k: v for k, v in self.proxies.items() if v is not None}
        
        # 方法开始日志
        current_time = datetime.datetime.now().strftime('%Y%m%d/%H:%M')
        if self.proxies:
            print(f"[{current_time}--AIService-[Info]: 已加载代理配置: {self.proxies}")
        else:
            print(f"[{current_time}--AIService-[Info]: 未使用代理")

    def list_models(self):
        """获取所有可用的模型列表"""
        # 获取当前时间
        current_time = datetime.datetime.now().strftime('%Y%m%d/%H:%M')
        function_name = 'list_models'
        model_name = 'API'
        
        try:
            # 方法开始日志
            print(f"[{current_time}--{model_name}-{function_name}-[Info]: 开始获取所有可用的AI模型列表")
            
            # 由于没有明确的API获取模型列表，返回预设的模型
            models = ["x-ai/grok-4-fast"]
            
            # 方法成功日志
            print(f"[{current_time}--{model_name}-{function_name}-[Info]: 获取模型列表成功, 返回{len(models)}个模型")
            return models
        except Exception as e:
            print(f"[{current_time}--{model_name}-{function_name}-[Error]: 获取模型列表异常: {str(e)}")
            # 返回默认模型列表作为备选
            default_models = ["x-ai/grok-4-fast"]
            print(f"[{current_time}--{model_name}-{function_name}-[Info]: 异常情况下返回默认模型列表: {default_models}")
            return default_models
    
    
    def chat_completion(self, messages, model=None, stream=False, max_tokens=4096):
        """发送聊天请求到AI模型"""
        # 获取当前时间
        current_time = datetime.datetime.now().strftime('%Y%m%d/%H:%M')
        function_name = 'chat_completion'
        if model is None:
            model = self.default_model
        
        try:
            # 方法开始日志
            print(f"[{current_time}--{model}-{function_name}-[Info]: 开始处理聊天完成请求, 消息数量: {len(messages)}, max_tokens: {max_tokens}")
            
            # 调试日志：打印最后一条消息的部分内容
            if messages:
                last_message_content = messages[-1].get('content', '')[:50] if messages else ''
                print(f"[{current_time}--{model}-{function_name}-[Debug]: 最后一条消息内容: {last_message_content}...")
            
            # 构建请求头
            headers = {
                "Authorization": f"Bearer {self.api_key}",
                "Content-Type": "application/json"
            }
            
            # 构建请求体
            payload = {
                "stream": stream,
                "model": model,
                "messages": messages,
                "max_tokens": max_tokens
            }
            
            print(f"[{current_time}--{model}-{function_name}-[Debug]: 调用API: {self.base_url}/chat/completions")
            
            # 发送请求到chat/completions接口
            url = f"{self.base_url}/chat/completions"
            
            # 添加代理支持并处理可能的代理错误
            try:
                response = requests.post(url, json=payload, headers=headers, proxies=self.proxies, timeout=30)
            except requests.exceptions.ProxyError as proxy_err:
                print(f"[{current_time}--{model}-{function_name}-[Error]: 代理连接错误: {str(proxy_err)}")
                # 尝试不使用代理再次请求
                print(f"[{current_time}--{model}-{function_name}-[Info]: 尝试不使用代理重新请求")
                response = requests.post(url, json=payload, headers=headers, timeout=30)
            except requests.exceptions.Timeout as timeout_err:
                print(f"[{current_time}--{model}-{function_name}-[Error]: 请求超时: {str(timeout_err)}")
                return None
            
            # 检查响应状态
            if response.status_code == 200:
                result = response.json()
                # 提取响应内容长度用于日志
                content_length = len(result.get('choices', [{}])[0].get('message', {}).get('content', ''))
                print(f"[{current_time}--{model}-{function_name}-[Info]: 聊天完成请求成功, 响应内容长度: {content_length}字符")
                return result
            else:
                print(f"[{current_time}--{model}-{function_name}-[Error]: 聊天请求失败，状态码: {response.status_code}, 错误信息: {response.text}")
                return None
        except Exception as e:
            print(f"[{current_time}--{model}-{function_name}-[Error]: 聊天请求异常: {str(e)}")
            return None
    
    def character_chat(self, character_name, character_description, user_query, 
                      model=None, stream=False):
        """以特定角色进行对话（兼容旧接口）"""
        # 获取当前时间
        current_time = datetime.datetime.now().strftime('%Y%m%d/%H:%M')
        function_name = 'character_chat'
        if model is None:
            model = self.default_model
        
        try:
            # 方法开始日志
            print(f"[{current_time}--{model}-{function_name}-[Info]: 开始处理角色扮演聊天请求, 角色: {character_name}")
            
            # 调试日志：打印用户查询的部分内容
            user_query_preview = user_query[:50] if user_query else ''
            print(f"[{current_time}--{model}-{function_name}-[Debug]: 用户查询内容: {user_query_preview}...")
            
            # 根据模板构建角色对话的提示词
            prompt = Config.CHARACTER_PROMPT_TEMPLATE.format(
                character_name=character_name,
                character_description=character_description,
                user_query=user_query
            )
            
            # 构建消息列表
            messages = [
                {"role": "user", "content": prompt}
            ]
            
            # 发送请求
            result = self.chat_completion(messages, model, stream)
            
            # 处理响应结果
            if result:
                content_length = len(result.get('choices', [{}])[0].get('message', {}).get('content', ''))
                print(f"[{current_time}--{model}-{function_name}-[Info]: 角色扮演聊天请求成功, 响应内容长度: {content_length}字符")
            return result
        except Exception as e:
            print(f"[{current_time}--{model}-{function_name}-[Error]: 角色扮演聊天请求异常: {str(e)}")
            return None
    
    def character_chat_with_context(self, messages, character_name=None, character_description=None, 
                                   model=None, stream=False, max_tokens=4096):
        """带上下文的角色扮演对话"""
        # 获取当前时间
        current_time = datetime.datetime.now().strftime('%Y%m%d/%H:%M')
        function_name = 'character_chat_with_context'
        if model is None:
            model = self.default_model
        
        try:
            # 方法开始日志
            print(f"[{current_time}--{model}-{function_name}-[Info]: 开始处理带上下文的角色扮演聊天, 角色: {character_name}, 消息数: {len(messages)}")
            
            # 如果提供了角色信息但消息列表中没有系统消息，添加系统消息
            if character_name and character_description and messages:
                has_system_message = any(msg.get('role') == 'system' for msg in messages)
                if not has_system_message:
                    system_message = {
                        "role": "system",
                        "content": f"你是{character_name}。{character_description}请始终保持这个角色的身份和特点进行对话。"
                    }
                    messages = [system_message] + messages
            
            # 调试日志：打印消息概要
            if messages:
                last_user_msg = next((msg['content'][:50] for msg in reversed(messages) if msg.get('role') == 'user'), '')
                print(f"[{current_time}--{model}-{function_name}-[Debug]: 最后用户消息: {last_user_msg}...")
            
            # 发送请求
            result = self.chat_completion(messages, model, stream, max_tokens)
            
            # 处理响应结果
            if result:
                content_length = len(result.get('choices', [{}])[0].get('message', {}).get('content', ''))
                print(f"[{current_time}--{model}-{function_name}-[Info]: 带上下文角色扮演聊天成功, 响应内容长度: {content_length}字符")
            return result
        except Exception as e:
            print(f"[{current_time}--{model}-{function_name}-[Error]: 带上下文角色扮演聊天异常: {str(e)}")
            return None
    
    def multimodal_completion(self, text=None, image=None, audio=None, video=None, model=None, stream=False):
        """支持文本、图像、音频、视频输入的多模态请求"""
        # 获取当前时间
        current_time = datetime.datetime.now().strftime('%Y%m%d/%H:%M')
        function_name = 'multimodal_completion'
        try:
            # 使用默认模型如果未指定
            if model is None:
                model = self.default_model
            
            # 方法开始日志
            print(f"[{current_time}--{model}-{function_name}-[Info]: 开始处理多模态输入请求")
            
            # 确定输入类型
            input_types = []
            if text: input_types.append('text')
            if image: input_types.append('image')
            if audio: input_types.append('audio')
            if video: input_types.append('video')
            
            # 调试日志：打印输入类型信息
            print(f"[{current_time}--{model}-{function_name}-[Debug]: 输入类型: {', '.join(input_types)}")
            
            # 调试日志：打印文本内容的部分预览
            if text:
                text_preview = text[:50] if text else ''
                print(f"[{current_time}--{model}-{function_name}-[Debug]: 文本内容: {text_preview}...")
            
            # 构建请求头
            headers = {
                "Authorization": f"Bearer {self.api_key}",
                "Content-Type": "application/json"
            }
            
            # 构建消息内容
            content = []
            if text:
                content.append({"type": "text", "text": text})
            if image:
                content.append({"type": "image", "image": image})  # 假设image是base64编码的图像数据
                print(f"[{current_time}--{model}-{function_name}-[Debug]: 已添加图像内容, 大小约{len(image)//1024}KB")
            if audio:
                content.append({"type": "audio", "audio": audio})  # 假设audio是base64编码的音频数据
                print(f"[{current_time}--{model}-{function_name}-[Debug]: 已添加音频内容, 大小约{len(audio)//1024}KB")
            if video:
                content.append({"type": "video", "video": video})  # 假设video是base64编码的视频数据
                print(f"[{current_time}--{model}-{function_name}-[Debug]: 已添加视频内容, 大小约{len(video)//1024}KB")
            
            # 构建请求体
            payload = {
                "stream": stream,
                "model": model,
                "messages": [
                    {"role": "user", "content": content}
                ]
            }
            
            # 发送请求到chat/completions接口
            url = f"{self.base_url}/chat/completions"
            print(f"[{current_time}--{model}-{function_name}-[Debug]: 调用API: {url}")
            
            # 添加代理支持并处理可能的代理错误
            try:
                response = requests.post(url, json=payload, headers=headers, proxies=self.proxies, timeout=30)
            except requests.exceptions.ProxyError as proxy_err:
                print(f"[{current_time}--{model}-{function_name}-[Error]: 代理连接错误: {str(proxy_err)}")
                # 尝试不使用代理再次请求
                print(f"[{current_time}--{model}-{function_name}-[Info]: 尝试不使用代理重新请求")
                response = requests.post(url, json=payload, headers=headers, timeout=30)
            except requests.exceptions.Timeout as timeout_err:
                print(f"[{current_time}--{model}-{function_name}-[Error]: 请求超时: {str(timeout_err)}")
                return None
            
            # 检查响应状态
            if response.status_code == 200:
                result = response.json()
                # 提取响应内容长度用于日志
                content_length = len(result.get('choices', [{}])[0].get('message', {}).get('content', ''))
                print(f"[{current_time}--{model}-{function_name}-[Info]: 多模态请求成功, 响应内容长度: {content_length}字符")
                return result
            else:
                print(f"[{current_time}--{model}-{function_name}-[Error]: 多模态请求失败，状态码: {response.status_code}, 错误信息: {response.text}")
                return None
        except Exception as e:
            print(f"[{current_time}--{model}-{function_name}-[Error]: 多模态请求异常: {str(e)}")
            return None
    
    def streaming_response_generator(self, response):
        """处理流式响应，生成器函数"""
        if not response:
            yield "发生错误，请重试"
            return
        
        try:
            # 对于非流式响应，直接返回内容
            if "choices" in response and len(response["choices"]) > 0:
                content = response["choices"][0]["message"]["content"]
                yield content
        except Exception as e:
            print(f"处理响应失败: {e}")
            yield "发生错误，请重试"