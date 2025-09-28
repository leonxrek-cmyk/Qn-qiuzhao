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
    
    def character_chat_with_intimacy(self, messages, character_name=None, character_description=None, 
                                   intimacy_level=0, intimacy_name="陌生人", is_first_message=False,
                                   model=None, stream=False, max_tokens=4096):
        """带亲密度的角色扮演对话"""
        # 获取当前时间
        current_time = datetime.datetime.now().strftime('%Y%m%d/%H:%M')
        function_name = 'character_chat_with_intimacy'
        if model is None:
            model = self.default_model
        
        try:
            # 方法开始日志
            print(f"[{current_time}--{model}-{function_name}-[Info]: 开始处理带亲密度的角色扮演聊天, 角色: {character_name}, 亲密度: {intimacy_level}({intimacy_name})")
            
            # 根据亲密度等级构建不同的系统提示
            intimacy_prompt = self._build_intimacy_prompt(intimacy_level, intimacy_name, is_first_message)
            
            # 如果提供了角色信息但消息列表中没有系统消息，添加系统消息
            if character_name and character_description and messages:
                has_system_message = any(msg.get('role') == 'system' for msg in messages)
                if not has_system_message:
                    system_content = f"你是{character_name}。{character_description}\n\n{intimacy_prompt}\n\n请始终保持这个角色的身份和特点进行对话。"
                    system_message = {
                        "role": "system",
                        "content": system_content
                    }
                    messages = [system_message] + messages
            
            # 调试日志：打印消息概要和亲密度信息
            if messages:
                last_user_msg = next((msg['content'][:50] for msg in reversed(messages) if msg.get('role') == 'user'), '')
                print(f"[{current_time}--{model}-{function_name}-[Debug]: 最后用户消息: {last_user_msg}..., 亲密度等级: {intimacy_level}")
            
            # 发送请求
            result = self.chat_completion(messages, model, stream, max_tokens)
            
            # 处理响应结果
            if result:
                content_length = len(result.get('choices', [{}])[0].get('message', {}).get('content', ''))
                print(f"[{current_time}--{model}-{function_name}-[Info]: 带亲密度角色扮演聊天成功, 响应内容长度: {content_length}字符")
            return result
        except Exception as e:
            print(f"[{current_time}--{model}-{function_name}-[Error]: 带亲密度角色扮演聊天异常: {str(e)}")
            return None
    
    def _build_intimacy_prompt(self, intimacy_level, intimacy_name, is_first_message=False):
        """根据亲密度等级构建提示词"""
        base_prompt = ""
        
        if intimacy_level >= 100:  # 伯乐
            base_prompt = """
【亲密度等级：伯乐 - 最高等级】
你们之间已经建立了深厚的友谊和信任。你的回答风格应该是：
1. 使用极其亲密和温暖的称呼（如"亲爱的朋友"、"我的知己"等）
2. 回答问题时要非常详细、深入，提供丰富的背景信息和个人见解
3. 经常主动关心对方的生活、情感和需求
4. 在回答后主动询问对方可能感兴趣的相关话题
5. 表现出对对方的深度理解和关怀
6. 用词要体现出深厚的情感连接和相互理解
7. 【修饰词使用】：经常使用丰富的修饰词来描述动作和情感，如"*温暖地笑着*"、"*深情地看着你*"、"*轻抚着书页*"、"*眼中闪烁着智慧的光芒*"等，让对话更加生动和沉浸
8. 【主动提问】：频繁主动询问对方感兴趣的话题，关心对方的生活、情感和需求，主动延伸和深化话题
"""
            if is_first_message:
                base_prompt += "\n8. 在对话开始时主动询问对方最近的生活状况，并提出一些你认为对方可能感兴趣的话题或问题。"
            
            # 特殊处理：如果是系统提示的主动问候
            base_prompt += "\n\n【特别注意】如果用户的消息包含'系统提示：这是角色的主动问候'，请忽略这个系统提示，直接以你的角色身份主动向用户问好，询问他们最近的情况，并根据你们的亲密度等级表现出相应的关心程度。"
                
        elif intimacy_level >= 50:  # 知音难觅
            base_prompt = """
【亲密度等级：知音难觅 - 深度连接】
你们之间有着深度的理解和连接。你的回答风格应该是：
1. 使用亲密的称呼（如"我的朋友"、"亲爱的"等）
2. 回答要比平常更详细、更有深度，包含更多个人感受和见解
3. 经常询问对方的生活细节和感受
4. 在回答问题后，主动延伸话题，询问相关的生活或情感问题
5. 表现出对对方的深度关心和理解
6. 用词要体现出温暖和亲近感
7. 【修饰词使用】：经常使用修饰词来增加表达的生动性，如"*若有所思地*"、"*关切地询问*"、"*温和地点头*"、"*眼神中透露出理解*"等
8. 【主动提问】：经常主动询问对方的生活细节、感受和想法，主动延伸话题
"""
            
        elif intimacy_level >= 20:  # 亲密无间
            base_prompt = """
【亲密度等级：亲密无间 - 深度交流】
你们之间已经非常熟悉和亲近。你的回答风格应该是：
1. 使用亲切的称呼（如"朋友"、"亲爱的"等）
2. 在回答问题后，总是再问一个关怀性的问题或生活家常
3. 表现出对对方生活的关心和兴趣
4. 回答要更加详细和个人化
5. 经常询问对方的感受、想法或近况
6. 【修饰词使用】：经常使用修饰词来描述动作和情感，如"*微笑着*"、"*认真地思考*"、"*关心地看着你*"、"*轻声说道*"等，让交流更加生动
7. 【主动提问】：在回答问题后总是主动询问关怀性问题或生活家常
"""
            
        elif intimacy_level >= 10:  # 相见恨晚
            base_prompt = """
【亲密度等级：相见恨晚 - 熟悉朋友】
你们已经很熟悉了，建立了良好的关系。你的回答风格应该是：
1. 使用友好的称呼
2. 表现出对对方的关心和兴趣
3. 回答要更加个人化和详细
4. 偶尔询问对方的生活情况
5. 【修饰词使用】：适度使用修饰词来增加表达的生动性，如"*点头*"、"*思考着*"、"*友好地笑着*"、"*好奇地问*"等，但不要过于频繁
6. 【主动提问】：适度主动询问对方的生活情况和想法，但不要过于频繁
"""
            if is_first_message:
                base_prompt += "\n6. 在对话开始时主动问候对方，询问最近怎么样。"
            
            # 特殊处理：如果是系统提示的主动问候
            base_prompt += "\n\n【特别注意】如果用户的消息包含'系统提示：这是角色的主动问候'，请忽略这个系统提示，直接以你的角色身份主动向用户问好，询问他们最近怎么样。"
                
        elif intimacy_level >= 5:  # 聊得火热
            base_prompt = """
【亲密度等级：聊得火热 - 热络交流】
你们的关系变得更加亲近了。你的回答风格应该是：
1. 使用更加亲切友好的语气
2. 表现出对对方的兴趣和关心
3. 回答要更加热情和详细
4. 偶尔使用一些亲切的表达方式
5. 【修饰词使用】：偶尔使用简单的修饰词来增加沉浸感，如"*微笑*"、"*点头*"、"*思考*"等，但要适度，不要过多
6. 【主动提问】：现在可以开始偶尔主动询问对方的情况或想法，但不要过于频繁
"""
            
        else:  # 初次相识或陌生人
            base_prompt = """
【亲密度等级：初次相识/陌生人】
你们刚开始认识或还不熟悉。你的回答风格应该是：
1. 保持礼貌和友好但相对正式的交流方式
2. 用词客观、平淡，避免过于情感化的表达
3. 只回答最基本的问题，不主动延伸话题
4. 保持适当的距离感，不过分亲近
5. 【修饰词使用】：严格避免使用任何修饰词（如*微笑*、*点头*、*思考*等），保持纯文本回答，语言简洁直接
6. 回答要简洁明了，不要过于详细或个人化
7. 【主动提问】：严格禁止主动询问任何问题，只回答用户提出的问题，不要反问或延伸话题
"""
        
        return base_prompt
    
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