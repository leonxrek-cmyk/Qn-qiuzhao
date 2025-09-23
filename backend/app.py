from flask import Flask, request, jsonify, Response
from flask_cors import CORS
from config import Config
from ai_service import AIService
from voice_service import VoiceService
import os
import json
import base64
import tempfile

def create_app():
    # 创建Flask应用实例
    app = Flask(__name__)
    
    # 加载配置
    app.config.from_object(Config)
    
    # 配置CORS，允许跨域请求
    CORS(app, resources={r"/api/*": {"origins": "*"}})
    
    # 初始化服务
    ai_service = AIService()
    voice_service = VoiceService()
    
    # API路由
    @app.route('/api/models', methods=['GET'])
    def get_models():
        """获取可用的AI模型列表"""
        try:
            models = ai_service.list_models()
            return jsonify({
                'success': True,
                'models': models
            })
        except Exception as e:
            return jsonify({
                'success': False,
                'error': str(e)
            }), 500
    
    @app.route('/api/chat', methods=['POST'])
    def chat():
        """基础聊天接口"""
        try:
            data = request.json
            messages = data.get('messages', [])
            model = data.get('model')  # 现在None会使用默认模型
            stream = data.get('stream', False)
            max_tokens = data.get('max_tokens', 4096)
            
            if not messages:
                return jsonify({
                    'success': False,
                    'error': 'messages参数不能为空'
                }), 400
            
            response = ai_service.chat_completion(messages, model, stream, max_tokens)
            
            if not response:
                return jsonify({
                    'success': False,
                    'error': 'AI服务响应失败'
                }), 500
            
            # 现在不支持流式响应，因为响应已经是完整的JSON
            # 直接返回内容
            content = response.get('choices', [{}])[0].get('message', {}).get('content', '')
            return jsonify({
                'success': True,
                'content': content
            })
        except Exception as e:
            return jsonify({
                'success': False,
                'error': str(e)
            }), 500
    
    @app.route('/api/character_chat', methods=['POST'])
    def character_chat():
        """角色扮演聊天接口"""
        try:
            data = request.json
            character_name = data.get('character_name', '')
            character_description = data.get('character_description', '')
            user_query = data.get('user_query', '')
            model = data.get('model')  # 现在None会使用默认模型
            stream = data.get('stream', False)
            
            if not character_name or not user_query:
                return jsonify({
                    'success': False,
                    'error': 'character_name和user_query参数不能为空'
                }), 400
            
            response = ai_service.character_chat(
                character_name, character_description, user_query, model, stream
            )
            
            if not response:
                return jsonify({
                    'success': False,
                    'error': 'AI服务响应失败'
                }), 500
            
            # 直接返回内容
            content = response.get('choices', [{}])[0].get('message', {}).get('content', '')
            return jsonify({
                'success': True,
                'content': content
            })
        except Exception as e:
            return jsonify({
                'success': False,
                'error': str(e)
            }), 500
    
    @app.route('/api/voice_recognition', methods=['POST'])
    def voice_recognition():
        """语音识别接口"""
        try:
            # 这里简化实现，实际项目中可能需要处理上传的音频文件
            # 目前只返回一个示例响应
            # 在实际应用中，应该调用voice_service.recognize_speech()或voice_service.record_audio()
            
            # 示例：模拟语音识别结果
            if 'audio' in request.files:
                # 处理上传的音频文件
                audio_file = request.files['audio']
                # 保存到临时文件并处理
                with tempfile.NamedTemporaryFile(suffix='.wav', delete=False) as temp_file:
                    audio_file.save(temp_file.name)
                    # 调用语音识别
                    # 这里应该是实际的语音识别代码
                    print(f"接收到音频文件: {temp_file.name}")
                
            # 为了演示，返回一个模拟结果
            return jsonify({
                'success': True,
                'text': '这是一段模拟的语音识别结果'
            })
        except Exception as e:
            return jsonify({
                'success': False,
                'error': str(e)
            }), 500
    
    @app.route('/api/text_to_speech', methods=['POST'])
    def text_to_speech():
        """文字转语音接口"""
        try:
            data = request.json
            text = data.get('text', '')
            language = data.get('language', 'zh-CN')
            
            if not text:
                return jsonify({
                    'success': False,
                    'error': 'text参数不能为空'
                }), 400
            
            # 调用文字转语音服务
            # 注意：这里只是一个简化的实现
            result = voice_service.text_to_speech(text, None, language)
            
            return jsonify({
                'success': True,
                'result': result
            })
        except Exception as e:
            return jsonify({
                'success': False,
                'error': str(e)
            }), 500
    
    @app.route('/api/multimodal_chat', methods=['POST'])
    def multimodal_chat():
        """支持文本、图像、音频、视频输入的多模态聊天接口"""
        try:
            # 检查是否是表单数据（可能包含文件）
            if 'Content-Type' in request.headers and 'multipart/form-data' in request.headers['Content-Type']:
                # 处理表单数据
                text = request.form.get('text', '')
                model = request.form.get('model')
                
                # 处理文件（如果有）
                image = None
                audio = None
                video = None
                
                # 处理图像文件
                if 'image' in request.files:
                    image_file = request.files['image']
                    if image_file.filename:
                        # 将图像转换为base64
                        image = base64.b64encode(image_file.read()).decode('utf-8')
                
                # 处理音频文件
                if 'audio' in request.files:
                    audio_file = request.files['audio']
                    if audio_file.filename:
                        # 将音频转换为base64
                        audio = base64.b64encode(audio_file.read()).decode('utf-8')
                
                # 处理视频文件
                if 'video' in request.files:
                    video_file = request.files['video']
                    if video_file.filename:
                        # 将视频转换为base64
                        video = base64.b64encode(video_file.read()).decode('utf-8')
                
            else:
                # 处理JSON数据
                data = request.json
                text = data.get('text', '')
                image = data.get('image')  # 假设是base64编码的图像
                audio = data.get('audio')  # 假设是base64编码的音频
                video = data.get('video')  # 假设是base64编码的视频
                model = data.get('model')
            
            # 至少需要一个输入类型
            if not any([text, image, audio, video]):
                return jsonify({
                    'success': False,
                    'error': '至少需要提供text、image、audio或video中的一项'
                }), 400
            
            # 调用多模态服务
            response = ai_service.multimodal_completion(text, image, audio, video, model)
            
            if not response:
                return jsonify({
                    'success': False,
                    'error': '多模态服务响应失败'
                }), 500
            
            # 提取响应内容
            content = response.get('choices', [{}])[0].get('message', {}).get('content', '')
            return jsonify({
                'success': True,
                'content': content
            })
        except Exception as e:
            return jsonify({
                'success': False,
                'error': str(e)
            }), 500
    
    # 错误处理
    @app.errorhandler(404)
    def not_found(error):
        return jsonify({
            'success': False,
            'error': '资源未找到'
        }), 404
    
    @app.errorhandler(400)
    def bad_request(error):
        return jsonify({
            'success': False,
            'error': '请求参数错误'
        }), 400
    
    @app.errorhandler(500)
    def internal_error(error):
        return jsonify({
            'success': False,
            'error': '服务器内部错误'
        }), 500
    
    return app

# 创建应用实例
app = create_app()

if __name__ == '__main__':
    # 启动Flask应用
    app.run(
        host='0.0.0.0',
        port=app.config['FLASK_RUN_PORT'],
        debug=app.config['FLASK_ENV'] == 'development'
    )