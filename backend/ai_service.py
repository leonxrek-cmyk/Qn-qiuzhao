from openai import OpenAI
import requests
import json
from config import Config

class AIService:
    def __init__(self):
        # 初始化配置
        self.base_url = Config.QINIU_AI_BASE_URL
        self.api_key = Config.QINIU_AI_API_KEY
        self.default_model = Config.DEFAULT_MODEL
        
    def list_models(self):
        """获取所有可用的模型列表"""
        # 由于没有明确的API获取模型列表，返回预设的模型
        return ["x-ai/grok-4-fast"]
    
    def chat_completion(self, messages, model=None, stream=False, max_tokens=4096):
        """发送聊天请求到AI模型"""
        try:
            # 使用默认模型如果未指定
            if model is None:
                model = self.default_model
            
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
            
            # 发送请求到chat/completions接口
            url = f"{self.base_url}/chat/completions"
            response = requests.post(url, json=payload, headers=headers)
            
            # 检查响应状态
            if response.status_code == 200:
                return response.json()
            else:
                print(f"聊天请求失败，状态码: {response.status_code}, 错误信息: {response.text}")
                return None
        except Exception as e:
            print(f"聊天请求失败: {e}")
            return None
    
    def character_chat(self, character_name, character_description, user_query, 
                      model=None, stream=False):
        """以特定角色进行对话"""
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
        return self.chat_completion(messages, model, stream)
    
    def multimodal_completion(self, text=None, image=None, audio=None, video=None, model=None, stream=False):
        """支持文本、图像、音频、视频输入的多模态请求"""
        try:
            # 使用默认模型如果未指定
            if model is None:
                model = self.default_model
            
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
            if audio:
                content.append({"type": "audio", "audio": audio})  # 假设audio是base64编码的音频数据
            if video:
                content.append({"type": "video", "video": video})  # 假设video是base64编码的视频数据
            
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
            response = requests.post(url, json=payload, headers=headers)
            
            # 检查响应状态
            if response.status_code == 200:
                return response.json()
            else:
                print(f"多模态请求失败，状态码: {response.status_code}, 错误信息: {response.text}")
                return None
        except Exception as e:
            print(f"多模态请求失败: {e}")
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