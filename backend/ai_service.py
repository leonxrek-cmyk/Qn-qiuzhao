from openai import OpenAI
import requests
import json
import datetime
import os
import time
from config import Config
from log_service import LogService

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
        current_time = LogService.get_current_time()
        if self.proxies:
            LogService.log(current_time=current_time, model_name="AIService", function_name="__init__", log_level='Info', message=f"已加载代理配置: {self.proxies}")
        else:
            LogService.log(current_time=current_time, model_name="AIService", function_name="__init__", log_level='Info', message="未使用代理")

    def list_models(self):
        """获取所有可用的模型列表"""
        # 获取当前时间
        current_time = LogService.get_current_time()
        function_name = 'list_models'
        model_name = 'API'
        
        try:
            # 方法开始日志
            LogService.log(current_time=current_time, model_name=model_name, function_name=function_name, log_level='Info', message="开始获取所有可用的AI模型列表")
            
            # 由于没有明确的API获取模型列表，返回预设的模型
            models = ["x-ai/grok-4-fast"]
            
            # 方法成功日志
            LogService.log(current_time=current_time, model_name=model_name, function_name=function_name, log_level='Info', message=f"获取模型列表成功, 返回{len(models)}个模型")
            return models
        except Exception as e:
            LogService.log(current_time=current_time, model_name=model_name, function_name=function_name, log_level='Error', message=f"获取模型列表异常: {str(e)}")
            # 返回默认模型列表作为备选
            default_models = ["x-ai/grok-4-fast"]
            LogService.log(current_time=current_time, model_name=model_name, function_name=function_name, log_level='Info', message=f"异常情况下返回默认模型列表: {default_models}")
            return default_models
    
    
    def preprocess_input(self, text):
        """预处理用户输入文本，进行清洗和规范化"""
        if not text:
            return text
        
        # 去除多余的空格和特殊字符
        processed_text = ' '.join(text.strip().split())
        
        # 可以根据需要添加更多的预处理逻辑
        return processed_text
    
    def validate_input(self, messages):
        """验证用户输入的消息列表是否有效"""
        if not messages or not isinstance(messages, list):
            return False, "无效的消息格式，消息必须是非空列表"
        
        # 验证每一条消息
        for i, msg in enumerate(messages):
            if not isinstance(msg, dict):
                return False, f"消息 {i+1} 必须是字典格式"
            
            if 'role' not in msg or 'content' not in msg:
                return False, f"消息 {i+1} 缺少必要的字段 'role' 或 'content'"
            
            if msg['role'] not in ['user', 'assistant', 'system']:
                return False, f"消息 {i+1} 的 'role' 字段必须是 'user'、'assistant' 或 'system'"
            
            if not msg['content'] or not isinstance(msg['content'], (str, list)):
                return False, f"消息 {i+1} 的 'content' 字段必须是非空字符串或列表"
        
        return True, "输入验证通过"
    
    def chat_completion(self, messages, model=None, stream=False, max_tokens=4096, 
                        temperature=0.7, top_p=1.0, frequency_penalty=0.0, 
                        presence_penalty=0.0, retry_count=3, retry_delay=2):
        """发送聊天请求到AI模型"""
        # 获取当前时间
        current_time = LogService.get_current_time()
        function_name = 'chat_completion'
        if model is None:
            model = self.default_model
        
        try:
            # 输入验证
            is_valid, validation_msg = self.validate_input(messages)
            if not is_valid:
                LogService.log(current_time=current_time, model_name=model, function_name=function_name, log_level='Error', message=f"输入验证失败: {validation_msg}")
                return None, validation_msg
            
            # 方法开始日志
            LogService.log(current_time=current_time, model_name=model, function_name=function_name, log_level='Info', message=f"开始处理聊天完成请求, 消息数量: {len(messages)}, max_tokens: {max_tokens}")
            
            # 调试日志：打印最后一条消息的部分内容
            if messages:
                last_message_content = messages[-1].get('content', '')[:50] if messages else ''
                LogService.log(current_time=current_time, model_name=model, function_name=function_name, log_level='Debug', message=f"最后一条消息内容: {last_message_content}...")
            
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
                "max_tokens": max_tokens,
                "temperature": temperature,
                "top_p": top_p,
                "frequency_penalty": frequency_penalty,
                "presence_penalty": presence_penalty
            }
            
            LogService.log(current_time=current_time, model_name=model, function_name=function_name, 
                          log_level='Debug', message=f"请求参数: temperature={temperature}, top_p={top_p}, \
                          frequency_penalty={frequency_penalty}, presence_penalty={presence_penalty}")
            
            LogService.log(current_time=current_time, model_name=model, function_name=function_name, log_level='Debug', message=f"调用API: {self.base_url}/chat/completions")
            
            # 发送请求到chat/completions接口
            url = f"{self.base_url}/chat/completions"
            
            # 请求重试逻辑
            response = None
            attempt = 0
            last_error = None
            
            while attempt <= retry_count:
                if attempt > 0:
                    wait_time = retry_delay * (2 ** (attempt - 1))  # 指数退避
                    LogService.log(current_time=current_time, model_name=model, function_name=function_name, 
                                  log_level='Info', message=f"第 {attempt} 次重试, 等待 {wait_time} 秒后重试...")
                    time.sleep(wait_time)
                
                try:
                    # 首先尝试使用代理
                    if self.proxies and attempt == 0:
                        response = requests.post(url, json=payload, headers=headers, proxies=self.proxies, timeout=30)
                    else:
                        # 重试时不使用代理或本来就没有代理
                        response = requests.post(url, json=payload, headers=headers, timeout=30)
                    
                    # 检查响应状态码
                    if response.status_code == 200:
                        # 请求成功，跳出循环
                        break
                    else:
                        last_error = f"请求失败，状态码: {response.status_code}, 错误信息: {response.text}"
                        LogService.log(current_time=current_time, model_name=model, function_name=function_name, 
                                      log_level='Error', message=last_error)
                        
                except requests.exceptions.ProxyError as proxy_err:
                    last_error = f"代理连接错误: {str(proxy_err)}"
                    LogService.log(current_time=current_time, model_name=model, function_name=function_name, 
                                  log_level='Error', message=last_error)
                    # 下一次尝试不使用代理
                    
                except requests.exceptions.Timeout as timeout_err:
                    last_error = f"请求超时: {str(timeout_err)}"
                    LogService.log(current_time=current_time, model_name=model, function_name=function_name, 
                                  log_level='Error', message=last_error)
                    
                except requests.exceptions.ConnectionError as conn_err:
                    last_error = f"连接错误: {str(conn_err)}"
                    LogService.log(current_time=current_time, model_name=model, function_name=function_name, 
                                  log_level='Error', message=last_error)
                    
                except Exception as e:
                    last_error = f"请求异常: {str(e)}"
                    LogService.log(current_time=current_time, model_name=model, function_name=function_name, 
                                  log_level='Error', message=last_error)
                    
                attempt += 1
                
            if attempt > retry_count:
                LogService.log(current_time=current_time, model_name=model, function_name=function_name, 
                              log_level='Error', message=f"达到最大重试次数 {retry_count}，请求失败")
                return None, last_error
            
            # 检查响应状态
            if response and response.status_code == 200:
                # 尝试解析响应JSON
                try:
                    result = response.json()
                    # 提取响应内容长度用于日志
                    content_length = len(result.get('choices', [{}])[0].get('message', {}).get('content', ''))
                    LogService.log(current_time=current_time, model_name=model, function_name=function_name, log_level='Info', message=f"聊天完成请求成功, 响应内容长度: {content_length}字符")
                    return result, None
                except ValueError as json_err:
                    error_message = f"解析响应JSON失败: {str(json_err)}"
                    LogService.log(current_time=current_time, model_name=model, function_name=function_name, log_level='Error', message=error_message)
                    return None, error_message
            else:
                error_message = f"聊天请求失败，状态码: {response.status_code if response else '无响应'}, 错误信息: {response.text if response else '未知错误'}"
                LogService.log(current_time=current_time, model_name=model, function_name=function_name, log_level='Error', message=error_message)
                return None, error_message
        except Exception as e:
            error_message = f"聊天请求异常: {str(e)}"
            LogService.log(current_time=current_time, model_name=model, function_name=function_name, log_level='Error', message=error_message)
            return None, error_message
    
    def character_chat(self, character_name, character_description, user_query, 
                      model=None, stream=False, max_tokens=4096, temperature=0.7, 
                      top_p=1.0, frequency_penalty=0.0, presence_penalty=0.0, 
                      retry_count=3, retry_delay=2):
        """以特定角色进行对话"""
        # 获取当前时间
        current_time = LogService.get_current_time()
        function_name = 'character_chat'
        if model is None:
            model = self.default_model
        
        try:
            # 方法开始日志
            LogService.log(current_time=current_time, model_name=model, function_name=function_name, 
                          log_level='Info', message=f"开始处理角色扮演聊天请求, 角色: {character_name}")
            
            # 输入验证
            if not character_name or not isinstance(character_name, str):
                error_msg = "角色名称不能为空且必须是字符串"
                LogService.log(current_time=current_time, model_name=model, function_name=function_name, 
                              log_level='Error', message=f"输入验证失败: {error_msg}")
                return None, error_msg
            
            if not character_description or not isinstance(character_description, str):
                error_msg = "角色描述不能为空且必须是字符串"
                LogService.log(current_time=current_time, model_name=model, function_name=function_name, 
                              log_level='Error', message=f"输入验证失败: {error_msg}")
                return None, error_msg
            
            if not user_query or not isinstance(user_query, str):
                error_msg = "用户查询不能为空且必须是字符串"
                LogService.log(current_time=current_time, model_name=model, function_name=function_name, 
                              log_level='Error', message=f"输入验证失败: {error_msg}")
                return None, error_msg
            
            # 预处理用户输入
            processed_query = self.preprocess_input(user_query)
            
            # 调试日志：打印用户查询的部分内容
            user_query_preview = processed_query[:50] if processed_query else ''
            LogService.log(current_time=current_time, model_name=model, function_name=function_name, 
                          log_level='Debug', message=f"用户查询内容: {user_query_preview}...")
            
            # 根据模板构建角色对话的提示词
            try:
                prompt = Config.CHARACTER_PROMPT_TEMPLATE.format(
                    character_name=character_name,
                    character_description=character_description,
                    user_query=processed_query
                )
            except Exception as template_err:
                error_msg = f"构建提示词模板失败: {str(template_err)}"
                LogService.log(current_time=current_time, model_name=model, function_name=function_name, 
                              log_level='Error', message=error_msg)
                return None, error_msg
            
            # 构建消息列表
            messages = [
                {"role": "user", "content": prompt}
            ]
            
            # 发送请求，传递所有调参选项和重试参数
            result, error_msg = self.chat_completion(messages, model, stream, max_tokens, 
                                                   temperature, top_p, frequency_penalty, 
                                                   presence_penalty, retry_count, retry_delay)
            
            # 处理响应结果
            if result and not error_msg:
                content_length = len(result.get('choices', [{}])[0].get('message', {}).get('content', ''))
                LogService.log(current_time=current_time, model_name=model, function_name=function_name, 
                              log_level='Info', message=f"角色扮演聊天请求成功, 响应内容长度: {content_length}字符")
            
            return result, error_msg
        except Exception as e:
            error_msg = f"角色扮演聊天请求异常: {str(e)}"
            LogService.log(current_time=current_time, model_name=model, function_name=function_name, 
                          log_level='Error', message=error_msg)
            return None, error_msg
    
    def multimodal_completion(self, text=None, image=None, audio=None, video=None, model=None, stream=False, 
                             max_tokens=4096, temperature=0.7, top_p=1.0, 
                             frequency_penalty=0.0, presence_penalty=0.0, 
                             retry_count=3, retry_delay=2):
        """支持文本、图像、音频、视频输入的多模态请求"""
        # 获取当前时间
        current_time = LogService.get_current_time()
        function_name = 'multimodal_completion'
        try:
            # 使用默认模型如果未指定
            if model is None:
                model = self.default_model
            
            # 方法开始日志
            LogService.log(current_time=current_time, model_name=model, function_name=function_name, 
                          log_level='Info', message=f"开始处理多模态输入请求")
            
            # 输入验证
            # 确保至少有一个输入
            if not any([text, image, audio, video]):
                error_msg = "至少需要提供一种输入类型: text, image, audio 或 video"
                LogService.log(current_time=current_time, model_name=model, function_name=function_name, 
                              log_level='Error', message=f"输入验证失败: {error_msg}")
                return None, error_msg
            
            # 验证各输入类型
            if text is not None and not isinstance(text, str):
                error_msg = "text 必须是字符串类型"
                LogService.log(current_time=current_time, model_name=model, function_name=function_name, 
                              log_level='Error', message=f"输入验证失败: {error_msg}")
                return None, error_msg
            
            if image is not None and not isinstance(image, str):
                error_msg = "image 必须是base64编码的字符串类型"
                LogService.log(current_time=current_time, model_name=model, function_name=function_name, 
                              log_level='Error', message=f"输入验证失败: {error_msg}")
                return None, error_msg
            
            if audio is not None and not isinstance(audio, str):
                error_msg = "audio 必须是base64编码的字符串类型"
                LogService.log(current_time=current_time, model_name=model, function_name=function_name, 
                              log_level='Error', message=f"输入验证失败: {error_msg}")
                return None, error_msg
            
            if video is not None and not isinstance(video, str):
                error_msg = "video 必须是base64编码的字符串类型"
                LogService.log(current_time=current_time, model_name=model, function_name=function_name, 
                              log_level='Error', message=f"输入验证失败: {error_msg}")
                return None, error_msg
            
            # 确定输入类型
            input_types = []
            if text: input_types.append('text')
            if image: input_types.append('image')
            if audio: input_types.append('audio')
            if video: input_types.append('video')
            
            # 调试日志：打印输入类型信息
            LogService.log(current_time=current_time, model_name=model, function_name=function_name, 
                          log_level='Debug', message=f"输入类型: {', '.join(input_types)}")
            
            # 预处理文本输入（如果有）
            processed_text = self.preprocess_input(text) if text else None
            
            # 调试日志：打印文本内容的部分预览
            if processed_text:
                text_preview = processed_text[:50] if processed_text else ''
                LogService.log(current_time=current_time, model_name=model, function_name=function_name, 
                              log_level='Debug', message=f"文本内容: {text_preview}...")
            
            # 构建请求头
            headers = {
                "Authorization": f"Bearer {self.api_key}",
                "Content-Type": "application/json"
            }
            
            # 构建消息内容
            content = []
            if processed_text:
                content.append({"type": "text", "text": processed_text})
            if image:
                content.append({"type": "image", "image": image})  # 假设image是base64编码的图像数据
                LogService.log(current_time=current_time, model_name=model, function_name=function_name, 
                              log_level='Debug', message=f"已添加图像内容, 大小约{len(image)//1024}KB")
            if audio:
                content.append({"type": "audio", "audio": audio})  # 假设audio是base64编码的音频数据
                LogService.log(current_time=current_time, model_name=model, function_name=function_name, 
                              log_level='Debug', message=f"已添加音频内容, 大小约{len(audio)//1024}KB")
            if video:
                content.append({"type": "video", "video": video})  # 假设video是base64编码的视频数据
                LogService.log(current_time=current_time, model_name=model, function_name=function_name, 
                              log_level='Debug', message=f"已添加视频内容, 大小约{len(video)//1024}KB")
            
            # 构建请求体
            payload = {
                "stream": stream,
                "model": model,
                "messages": [
                    {"role": "user", "content": content}
                ],
                "max_tokens": max_tokens,
                "temperature": temperature,
                "top_p": top_p,
                "frequency_penalty": frequency_penalty,
                "presence_penalty": presence_penalty
            }
            
            LogService.log(current_time=current_time, model_name=model, function_name=function_name, 
                          log_level='Debug', message=f"请求参数: temperature={temperature}, top_p={top_p}, \
                          frequency_penalty={frequency_penalty}, presence_penalty={presence_penalty}")
            
            # 发送请求到chat/completions接口
            url = f"{self.base_url}/chat/completions"
            LogService.log(current_time=current_time, model_name=model, function_name=function_name, 
                          log_level='Debug', message=f"调用API: {url}")
            
            # 请求重试逻辑
            response = None
            attempt = 0
            last_error = None
            
            while attempt <= retry_count:
                if attempt > 0:
                    wait_time = retry_delay * (2 ** (attempt - 1))  # 指数退避
                    LogService.log(current_time=current_time, model_name=model, function_name=function_name, 
                                  log_level='Info', message=f"第 {attempt} 次重试, 等待 {wait_time} 秒后重试...")
                    time.sleep(wait_time)
                
                try:
                    # 首先尝试使用代理
                    if self.proxies and attempt == 0:
                        response = requests.post(url, json=payload, headers=headers, proxies=self.proxies, timeout=30)
                    else:
                        # 重试时不使用代理或本来就没有代理
                        response = requests.post(url, json=payload, headers=headers, timeout=30)
                    
                    # 检查响应状态码
                    if response.status_code == 200:
                        # 请求成功，跳出循环
                        break
                    else:
                        last_error = f"请求失败，状态码: {response.status_code}, 错误信息: {response.text}"
                        LogService.log(current_time=current_time, model_name=model, function_name=function_name, 
                                      log_level='Error', message=last_error)
                        
                except requests.exceptions.ProxyError as proxy_err:
                    last_error = f"代理连接错误: {str(proxy_err)}"
                    LogService.log(current_time=current_time, model_name=model, function_name=function_name, 
                                  log_level='Error', message=last_error)
                    # 下一次尝试不使用代理
                    
                except requests.exceptions.Timeout as timeout_err:
                    last_error = f"请求超时: {str(timeout_err)}"
                    LogService.log(current_time=current_time, model_name=model, function_name=function_name, 
                                  log_level='Error', message=last_error)
                    
                except requests.exceptions.ConnectionError as conn_err:
                    last_error = f"连接错误: {str(conn_err)}"
                    LogService.log(current_time=current_time, model_name=model, function_name=function_name, 
                                  log_level='Error', message=last_error)
                    
                except Exception as e:
                    last_error = f"请求异常: {str(e)}"
                    LogService.log(current_time=current_time, model_name=model, function_name=function_name, 
                                  log_level='Error', message=last_error)
                    
                attempt += 1
                
            if attempt > retry_count:
                LogService.log(current_time=current_time, model_name=model, function_name=function_name, 
                              log_level='Error', message=f"达到最大重试次数 {retry_count}，请求失败")
                return None, last_error
            
            # 检查响应状态
            if response and response.status_code == 200:
                # 尝试解析响应JSON
                try:
                    result = response.json()
                    # 提取响应内容长度用于日志
                    content_length = len(result.get('choices', [{}])[0].get('message', {}).get('content', ''))
                    LogService.log(current_time=current_time, model_name=model, function_name=function_name, 
                                  log_level='Info', message=f"多模态请求成功, 响应内容长度: {content_length}字符")
                    return result, None
                except ValueError as json_err:
                    error_msg = f"解析响应JSON失败: {str(json_err)}"
                    LogService.log(current_time=current_time, model_name=model, function_name=function_name, 
                                  log_level='Error', message=error_msg)
                    return None, error_msg
            else:
                error_msg = f"多模态请求失败，状态码: {response.status_code if response else '无响应'}, 错误信息: {response.text if response else '未知错误'}"
                LogService.log(current_time=current_time, model_name=model, function_name=function_name, 
                              log_level='Error', message=error_msg)
                return None, error_msg
        except Exception as e:
            error_msg = f"多模态请求异常: {str(e)}"
            LogService.log(current_time=current_time, model_name=model, function_name=function_name, 
                          log_level='Error', message=error_msg)
            return None, error_msg
    
    def streaming_response_generator(self, response):
        """处理流式响应，生成器函数"""
        if not response:
            error_msg = "响应为空，请检查API请求"
            current_time = LogService.get_current_time()
            LogService.log(current_time=current_time, model_name="AIService", function_name="streaming_response_generator", 
                          log_level='Error', message=error_msg)
            yield (None, error_msg)
            return
        
        try:
            # 对于非流式响应，直接返回内容
            if "choices" in response and len(response["choices"]) > 0:
                content = response["choices"][0]["message"]["content"]
                current_time = LogService.get_current_time()
                LogService.log(current_time=current_time, model_name="AIService", function_name="streaming_response_generator", 
                              log_level='Info', message=f"流式响应处理成功")
                yield (content, None)
            else:
                error_msg = "响应格式不正确，缺少choices字段或choices为空"
                current_time = LogService.get_current_time()
                LogService.log(current_time=current_time, model_name="AIService", function_name="streaming_response_generator", 
                              log_level='Error', message=error_msg)
                yield (None, error_msg)
        except KeyError as key_err:
            error_msg = f"响应格式错误，缺少必要字段: {str(key_err)}"
            current_time = LogService.get_current_time()
            LogService.log(current_time=current_time, model_name="AIService", function_name="streaming_response_generator", 
                          log_level='Error', message=error_msg)
            yield (None, error_msg)
        except Exception as e:
            error_msg = f"处理响应失败: {str(e)}"
            current_time = LogService.get_current_time()
            LogService.log(current_time=current_time, model_name="AIService", function_name="streaming_response_generator", 
                          log_level='Error', message=error_msg)
            yield (None, error_msg)