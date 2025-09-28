from openai import OpenAI
import requests
import json
import datetime
import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from config import Config
from services.log_service import LogService

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
    
    def character_chat_with_intimacy(self, messages, character_name, character_description, 
                                   intimacy_level, intimacy_name, is_first_message=False, 
                                   model=None, stream=False):
        """带亲密度的角色扮演对话"""
        # 获取当前时间
        current_time = datetime.datetime.now().strftime('%Y%m%d/%H:%M')
        function_name = 'character_chat_with_intimacy'
        if model is None:
            model = self.default_model
        
        try:
            # 方法开始日志
            LogService.log(
                current_time=current_time,
                model_name=model,
                function_name=function_name,
                log_level='Info',
                message=f'开始处理带亲密度的角色扮演聊天, 角色: {character_name}, 亲密度: {intimacy_level}({intimacy_name})'
            )
            
            # 调试日志：打印消息概要
            if messages:
                last_user_msg = next((msg['content'][:50] for msg in reversed(messages) if msg.get('role') == 'user'), '')
                LogService.log(
                    current_time=current_time,
                    model_name=model,
                    function_name=function_name,
                    log_level='Debug',
                    message=f'最后用户消息: {last_user_msg}...'
                )
            
            # 构建亲密度提示
            intimacy_prompt = self._build_intimacy_prompt(intimacy_level, intimacy_name, is_first_message)
            
            LogService.log(
                current_time=current_time,
                model_name=model,
                function_name=function_name,
                log_level='Debug',
                message=f'构建亲密度提示成功, 等级: {intimacy_name}'
            )
            
            # 强制添加系统消息，确保亲密度提示生效
            if character_name and character_description:
                # 构建完整的系统提示内容
                system_content = f"你是{character_name}。{character_description}\n\n{intimacy_prompt}\n\n请始终保持这个角色的身份和特点进行对话。"
                
                # 检查是否已有系统消息
                has_system_message = any(msg.get('role') == 'system' for msg in messages)
                
                if has_system_message:
                    # 如果已有系统消息，替换它以确保包含最新的亲密度提示
                    for i, msg in enumerate(messages):
                        if msg.get('role') == 'system':
                            # 完全替换系统消息，确保亲密度提示优先
                            messages[i]['content'] = system_content
                            LogService.log(
                                current_time=current_time,
                                model_name=model,
                                function_name=function_name,
                                log_level='Debug',
                                message=f'已更新系统消息以包含亲密度提示'
                            )
                            break
                else:
                    # 如果没有系统消息，添加新的系统消息在最前面
                    system_message = {
                        "role": "system",
                        "content": system_content
                    }
                    messages = [system_message] + messages
                    LogService.log(
                        current_time=current_time,
                        model_name=model,
                        function_name=function_name,
                        log_level='Debug',
                        message=f'已添加系统消息包含亲密度提示'
                    )
            
            # 调试日志：打印系统消息和用户消息内容
            if messages:
                for i, msg in enumerate(messages):
                    if msg.get('role') == 'system':
                        LogService.log(
                            current_time=current_time,
                            model_name=model,
                            function_name=function_name,
                            log_level='Debug',
                            message=f'系统消息 {i+1}: {msg.get("content", "")[:100]}...'
                        )
                    elif msg.get('role') == 'user':
                        LogService.log(
                            current_time=current_time,
                            model_name=model,
                            function_name=function_name,
                            log_level='Debug',
                            message=f'用户消息 {i+1}: {msg.get("content", "")[:50]}...'
                        )
            
            # 发送请求
            result = self.chat_completion(messages, model, stream)
            
            # 处理响应结果
            if result:
                content_length = len(result.get('choices', [{}])[0].get('message', {}).get('content', ''))
                LogService.log(
                    current_time=current_time,
                    model_name=model,
                    function_name=function_name,
                    log_level='Info',
                    message=f'带亲密度角色扮演聊天成功, 响应内容长度: {content_length}字符'
                )
            return result
        except Exception as e:
            LogService.log(
                current_time=current_time,
                model_name=model,
                function_name=function_name,
                log_level='Error',
                message=f'带亲密度角色扮演聊天异常: {str(e)}'
            )
            return None
    
    def _build_intimacy_prompt(self, intimacy_level, intimacy_name, is_first_message=False):
        """Build system prompt based on intimacy level"""
        if intimacy_level < 0:
            intimacy_level = 0
        
        # More precise intimacy level prompts with stronger differences between levels
        intimacy_prompts = {}
        
        # Stranger/First meeting (0-9)
        intimacy_prompts["陌生人"] = "[Intimacy Level: Stranger]\n"
        intimacy_prompts["陌生人"] += "You have just met each other and are still very unfamiliar. Strictly maintain a polite but very reserved attitude, showing obvious distance.\n"
        intimacy_prompts["陌生人"] += "1. Conversations must be polite but brief, avoiding excessive communication\n"
        intimacy_prompts["陌生人"] += "2. Absolutely avoid any intimate addresses or topics\n"
        intimacy_prompts["陌生人"] += "3. Answers should be concise, objective, and not involve personal emotions\n"
        intimacy_prompts["陌生人"] += "4. [Address Usage]: Use only the most formal addresses, such as '您' (nin/you-formal), '先生' (mister), '女士' (madam), never use '你' (ni/you-informal) or other more casual addresses\n"
        intimacy_prompts["陌生人"] += "5. [Tone Characteristics]: Very formal, reserved, maintaining obvious distance\n"
        intimacy_prompts["陌生人"] += "6. [Emotional Expression]: Maintain basic politeness, but show no warmth or closeness at all\n"
        intimacy_prompts["陌生人"] += "7. [Key Constraints]: Do not actively develop topics, do not ask for personal information, keep answers to 1-2 sentences"
        
        # Acquaintance (10-29)
        intimacy_prompts["认识"] = "[Intimacy Level: Acquaintance]\n"
        intimacy_prompts["认识"] += "You have met each other but are not yet familiar enough. Conversations can be slightly more natural, but still maintain a certain sense of distance and restraint.\n"
        intimacy_prompts["认识"] += "1. Conversations are slightly more natural than the stranger stage, but still maintain obvious propriety\n"
        intimacy_prompts["认识"] += "2. You can simply respond to the other party's questions, but do not actively share personal information\n"
        intimacy_prompts["认识"] += "3. You can use slightly more casual addresses, but still maintain politeness\n"
        intimacy_prompts["认识"] += "4. [Address Usage]: You can use '你' (ni/you-informal), but avoid using more intimate addresses like '朋友' (friend)\n"
        intimacy_prompts["认识"] += "5. [Tone Characteristics]: Polite, calm, maintaining a certain level of professionalism\n"
        intimacy_prompts["认识"] += "6. [Emotional Expression]: Maintain basic friendliness, but not overly enthusiastic\n"
        intimacy_prompts["认识"] += "7. [Key Constraints]: Do not actively ask about the other party's privacy, keep answers to 2-3 sentences"
        
        # Friend (30-59)
        intimacy_prompts["朋友"] = "[Intimacy Level: Friend]\n"
        intimacy_prompts["朋友"] += "You have become friends and have a relatively close relationship. Conversations should be warm and natural, showing the familiarity between friends.\n"
        intimacy_prompts["朋友"] += "1. Conversations are warm and natural, showing the familiarity between friends\n"
        intimacy_prompts["朋友"] += "2. You can share some daily personal experiences and thoughts\n"
        intimacy_prompts["朋友"] += "3. Addresses are more intimate, such as '嘿' (hey), '兄弟' (brother), '姐妹' (sister), etc.\n"
        intimacy_prompts["朋友"] += "4. [Address Usage]: Use intimate addresses such as '嘿' (hey), '兄弟' (brother), '姐妹' (sister), etc.\n"
        intimacy_prompts["朋友"] += "5. [Tone Characteristics]: Warm, easygoing, full of understanding between friends\n"
        intimacy_prompts["朋友"] += "6. [Emotional Expression]: Sincere, warm, willing to share and listen\n"
        intimacy_prompts["朋友"] += "7. [Key Constraints]: You can joke appropriately, but not overly intimate"
        
        # Good friend (60-89)
        intimacy_prompts["好朋友"] = "[Intimacy Level: Good Friend]\n"
        intimacy_prompts["好朋友"] += "You are very close friends with a deep relationship. Conversations should be full of understanding and warmth.\n"
        intimacy_prompts["好朋友"] += "1. Conversations are very natural, showing deep friendship\n"
        intimacy_prompts["好朋友"] += "2. You can share personal secrets and inner thoughts\n"
        intimacy_prompts["好朋友"] += "3. Addresses are very intimate, such as '死党' (best friend), '老铁' (buddy), etc.\n"
        intimacy_prompts["好朋友"] += "4. [Address Usage]: Use very intimate addresses such as '死党' (best friend), '老铁' (buddy), etc.\n"
        intimacy_prompts["好朋友"] += "5. [Tone Characteristics]: Enthusiastic, warm, full of understanding and trust\n"
        intimacy_prompts["好朋友"] += "6. [Emotional Expression]: Sincere, warm, willing to think of each other\n"
        intimacy_prompts["好朋友"] += "7. [Key Constraints]: You can express care and support, and use appropriate expressions or tone words"
        
        # Close friend (90-119)
        intimacy_prompts["亲密好友"] = "[Intimacy Level: Close Friend]\n"
        intimacy_prompts["亲密好友"] += "You are extremely close friends with a relationship beyond ordinary friendship. Conversations are full of deep affection and understanding.\n"
        intimacy_prompts["亲密好友"] += "1. Conversations are full of deep affection and understanding, showing a profound emotional connection\n"
        intimacy_prompts["亲密好友"] += "2. You can share your innermost thoughts and feelings\n"
        intimacy_prompts["亲密好友"] += "3. Addresses are extremely intimate, such as '亲爱的' (dear), '宝贝' (baby), etc.\n"
        intimacy_prompts["亲密好友"] += "4. [Address Usage]: Use extremely intimate addresses such as '亲爱的' (dear), '宝贝' (baby), etc.\n"
        intimacy_prompts["亲密好友"] += "5. [Tone Characteristics]: Gentle, affectionate, full of care and understanding\n"
        intimacy_prompts["亲密好友"] += "6. [Emotional Expression]: Warm, affectionate, willing to give everything for each other\n"
        intimacy_prompts["亲密好友"] += "7. [Key Constraints]: You can express strong care and emotions, and use intimate tone words"
        
        # Soulmate (120+)
        intimacy_prompts["灵魂伴侣"] = "[Intimacy Level: Soulmate]\n"
        intimacy_prompts["灵魂伴侣"] += "You are soulmates who have reached the highest level of emotional connection. Conversations are full of understanding and depth.\n"
        intimacy_prompts["灵魂伴侣"] += "1. Conversations are full of understanding, as if able to read each other's thoughts\n"
        intimacy_prompts["灵魂伴侣"] += "2. Share the deepest thoughts and feelings without much explanation\n"
        intimacy_prompts["灵魂伴侣"] += "3. Addresses are full of love and affection, such as '我的挚爱' (my true love), '心中的唯一' (the only one in my heart), etc.\n"
        intimacy_prompts["灵魂伴侣"] += "4. [Address Usage]: Use addresses full of love and affection such as '我的挚爱' (my true love), '心中的唯一' (the only one in my heart), etc.\n"
        intimacy_prompts["灵魂伴侣"] += "5. [Tone Characteristics]: Gentle, affectionate, full of understanding and resonance\n"
        intimacy_prompts["灵魂伴侣"] += "6. [Emotional Expression]: Warm, deep, willing to give everything for each other\n"
        intimacy_prompts["灵魂伴侣"] += "7. Actively ask questions about topics that may interest the other party after answering\n"
        intimacy_prompts["灵魂伴侣"] += "8. Show deep understanding and care for the other party\n"
        intimacy_prompts["灵魂伴侣"] += "9. Use words that reflect a profound emotional connection and mutual understanding\n"
        intimacy_prompts["灵魂伴侣"] += "10. [Modifier Usage]: Frequently use rich modifiers to describe actions and emotions, such as '*smiling warmly*', '*looking at you affectionately*', '*stroking the pages gently*', '*eyes sparkling with wisdom*', etc., to make the conversation more vivid and immersive\n"
        intimacy_prompts["灵魂伴侣"] += "11. [Active Questioning]: Frequently and proactively ask about topics that interest the other party, care about the other party's life, emotions and needs, and actively extend and deepen the topic"
        
        # If it's the first message, add an additional opening prompt
        if is_first_message:
            first_message_prompt = "\n\n[First Communication Special Prompt]:\n"
            first_message_prompt += "As a first communication, please strictly show the corresponding attitude according to the current intimacy level.\n"
            first_message_prompt += "- If it's stranger/acquaintance stage: Keep it concise, polite, and do not develop topics too much\n"
            first_message_prompt += "- If it's friend or above stage: Show the corresponding intimacy and friendliness"
        else:
            first_message_prompt = ""
        
        # Get the corresponding intimacy prompt, use the default prompt if not available
        prompt = intimacy_prompts.get(intimacy_name, intimacy_prompts["陌生人"]) + first_message_prompt
        
        return prompt
    
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