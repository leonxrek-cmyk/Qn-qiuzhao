from flask import Flask, request, jsonify, send_file
from flask_cors import CORS
from config import Config
from ai_service import AIService
from voice_service import VoiceService
from log_service import LogService
import os
import json
import base
=======
import datetime
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
    
    # 角色配置文件路径
    CHARACTERS_CONFIG_FILE = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'character_configs.json')
    
    # 加载角色配置
    def load_character_configs():
        try:
            with open(CHARACTERS_CONFIG_FILE, 'r', encoding='utf-8') as f:
                return json.load(f)
        except Exception as e:
            LogService.error(model_name='App', function_name='load_character_configs', message=f'加载角色配置失败: {str(e)}')
            return {}
    
    # 全局角色配置数据
    character_configs = load_character_configs()
    
    # API路由
    @app.route('/api/models', methods=['GET'])
    def get_models():
        """获取可用的AI模型列表"""
        current_time = LogService.get_current_time()
        model_name = Config.DEFAULT_MODEL
        function_name = 'get_models'
        
        # 请求开始日志
        LogService.info(model_name=model_name, function_name=function_name, message='请求开始获取可用模型列表')
        
        try:
            models = ai_service.list_models()
            
            # 请求成功日志
            LogService.info(model_name=model_name, function_name=function_name, message=f'获取模型列表成功, 模型数量: {len(models)}')
            
            return jsonify({
                'success': True,
                'models': models
            })
        except Exception as e:
            # 请求失败日志
            LogService.error(model_name=model_name, function_name=function_name, message=f'获取模型列表失败: {str(e)}')
            
            return jsonify({
                'success': False,
                'error': str(e)
            }), 500
    
    @app.route('/api/character_config', methods=['GET'])
    def get_all_character_configs():
        """获取所有角色的配置列表"""
        current_time = LogService.get_current_time()
        function_name = 'get_all_character_configs'
        model_name = 'API'
        
        try:
            LogService.info(model_name=model_name, function_name=function_name, message='请求获取所有角色配置')
            
            # 将字典转换为列表格式，并添加角色ID
            config_list = []
            for character_id, config in character_configs.items():
                config_with_id = config.copy()
                config_with_id['id'] = character_id
                config_list.append(config_with_id)
            
            LogService.info(model_name=model_name, function_name=function_name, message=f'获取角色配置列表成功, 角色数量: {len(config_list)}')
            return jsonify({
                'success': True,
                'configs': config_list
            })
        except Exception as e:
            LogService.error(model_name=model_name, function_name=function_name, message=f'获取角色配置列表失败: {str(e)}')
            return jsonify({
                'success': False,
                'error': str(e)
            }), 500
    
    @app.route('/api/character_config/<character_id>', methods=['GET'])
    def get_character_config(character_id):
        """获取特定角色的配置"""
        current_time = LogService.get_current_time()
        function_name = 'get_character_config'
        model_name = 'API'
        
        try:
            LogService.info(model_name=model_name, function_name=function_name, message=f'请求获取角色配置, 角色ID: {character_id}')
            
            # 检查角色是否存在
            if character_id not in character_configs:
                LogService.error(model_name=model_name, function_name=function_name, message=f'角色不存在: {character_id}')
                return jsonify({
                    'success': False,
                    'error': '角色不存在'
                }), 404
            
            config = character_configs[character_id].copy()
            config['id'] = character_id
            LogService.info(model_name=model_name, function_name=function_name, message=f'获取角色配置成功: {character_id}')
            return jsonify({
                'success': True,
                'config': config
            })
        except Exception as e:
            LogService.error(model_name=model_name, function_name=function_name, message=f'获取角色配置失败: {str(e)}')
            return jsonify({
                'success': False,
                'error': str(e)
            }), 500
    
    @app.route('/api/chat', methods=['POST'])
    def chat():
        """基础聊天接口"""
        current_time = LogService.get_current_time()
        function_name = 'chat'
        
        try:
            data = request.json
            messages = data.get('messages', [])
            model = data.get('model') or Config.DEFAULT_MODEL
            stream = data.get('stream', False)
            max_tokens = data.get('max_tokens', 4096)
            
            # 请求开始日志
            LogService.info(model_name=model, function_name=function_name, message=f'请求开始处理聊天消息, 消息数量: {len(messages)}, max_tokens: {max_tokens}')
            
            if not messages:
                LogService.error(model_name=model, function_name=function_name, message='请求参数错误: messages参数不能为空')
                return jsonify({
                    'success': False,
                    'error': 'messages参数不能为空'
                }), 400
            
            # 调试日志：打印最后一条消息的部分内容
            last_message_content = messages[-1].get('content', '')[:50] if messages else ''
            LogService.debug(model_name=model, function_name=function_name, message=f'最后一条消息内容: {last_message_content}...')
            
            response = ai_service.chat_completion(messages, model, stream, max_tokens)
            
            if not response:
                LogService.error(model_name=model, function_name=function_name, message='AI服务响应为空')
                return jsonify({
                    'success': False,
                    'error': 'AI服务响应失败'
                }), 500
            
            # 提取响应内容
            content = response.get('choices', [{}])[0].get('message', {}).get('content', '')
            
            # 请求成功日志
            LogService.info(model_name=model, function_name=function_name, message=f'聊天请求处理成功, 响应内容长度: {len(content)}字符')
            
            return jsonify({
                'success': True,
                'content': content
            })
        except Exception as e:
            LogService.error(model_name=Config.DEFAULT_MODEL, function_name=function_name, message=f'聊天请求处理失败: {str(e)}')
            return jsonify({
                'success': False,
                'error': str(e)
            }), 500
    
    @app.route('/api/character_chat', methods=['POST'])
    def character_chat():
        """角色扮演聊天接口"""
        current_time = LogService.get_current_time()
        function_name = 'character_chat'
        
        try:
            data = request.json
            character_id = data.get('character_id', '')
            character_name = data.get('character_name', '')
            character_description = data.get('character_description', '')
            user_query = data.get('user_query', '')
            model = data.get('model') or Config.DEFAULT_MODEL
            stream = data.get('stream', False)
            
            # 如果提供了character_id，使用配置文件中的角色信息
            if character_id and character_id in character_configs:
                config = character_configs[character_id]
                character_name = config['name']
                character_description = config['description']
                
                # 请求开始日志
                LogService.info(model_name=model, function_name=function_name, message=f'请求开始处理角色扮演聊天, 角色ID: {character_id}, 角色名称: {character_name}')
            else:
                # 请求开始日志
                LogService.info(model_name=model, function_name=function_name, message=f'请求开始处理角色扮演聊天, 角色名称: {character_name}')
            
            if not character_name or not user_query:
                LogService.error(model_name=model, function_name=function_name, message='请求参数错误: character_name和user_query参数不能为空')
                return jsonify({
                    'success': False,
                    'error': 'character_name和user_query参数不能为空'
                }), 400
            
            # 调试日志：打印用户查询的部分内容
            user_query_content = user_query[:50] if user_query else ''
            LogService.debug(model_name=model, function_name=function_name, message=f'用户查询内容: {user_query_content}...')
            
            # 使用角色配置文件中的提示词模板（如果有）
            if character_id and character_id in character_configs:
                config = character_configs[character_id]
                if 'prompt_template' in config:
                    # 构建自定义提示词
                    prompt = config['prompt_template'].format(user_query=user_query)
                    messages = [{"role": "user", "content": prompt}]
                    response = ai_service.chat_completion(messages, model, stream)
                else:
                    # 使用原始方式调用
                    response = ai_service.character_chat(
                        character_name, character_description, user_query, model, stream
                    )
            else:
                # 使用原始方式调用
                response = ai_service.character_chat(
                    character_name, character_description, user_query, model, stream
                )
            
            if not response:
                LogService.error(model_name=model, function_name=function_name, message='AI服务响应为空')
                return jsonify({
                    'success': False,
                    'error': 'AI服务响应失败'
                }), 500
            
            # 提取响应内容
            content = response.get('choices', [{}])[0].get('message', {}).get('content', '')
            
            # 请求成功日志
            LogService.info(model_name=model, function_name=function_name, message=f'角色扮演聊天请求处理成功, 响应内容长度: {len(content)}字符')
            
            return jsonify({
                'success': True,
                'content': content,
                'character_id': character_id
            })
        except Exception as e:
            LogService.error(model_name=Config.DEFAULT_MODEL, function_name=function_name, message=f'角色扮演聊天请求处理失败: {str(e)}')
            return jsonify({
                'success': False,
                'error': str(e)
            }), 500
    
    @app.route('/api/voice_recognition', methods=['POST'])
    def voice_recognition():
        """语音识别接口"""
        current_time = LogService.get_current_time()
        function_name = 'voice_recognition'
        model_name = 'SpeechRecognition'
        
        try:
            # 请求开始日志
            LogService.info(model_name=model_name, function_name=function_name, message='请求开始处理语音识别')
            
            # 这里简化实现，实际项目中可能需要处理上传的音频文件
            # 目前只返回一个示例响应
            # 在实际应用中，应该调用voice_service.recognize_speech()或voice_service.record_audio()
            
            # 示例：模拟语音识别结果
            if 'audio' in request.files:
                # 处理上传的音频文件
                audio_file = request.files['audio']
                language = request.form.get('language', 'zh-CN')
                
                # 调试日志：打印音频文件信息
                LogService.debug(model_name=model_name, function_name=function_name, message=f'接收音频文件: {audio_file.filename}, 语言: {language}')
                
                # 保存到临时文件并处理
                with tempfile.NamedTemporaryFile(suffix='.wav', delete=False) as temp_file:
                    audio_file.save(temp_file.name)
                    # 调用语音识别
                    # 这里应该是实际的语音识别代码
                    LogService.info(model_name=model_name, function_name=function_name, message=f'保存音频文件到临时路径: {temp_file.name}')
            else:
                LogService.debug(model_name=model_name, function_name=function_name, message='没有接收到音频文件，使用模拟结果')
                language = request.form.get('language', 'zh-CN')
                LogService.debug(model_name=model_name, function_name=function_name, message=f'语言设置: {language}')
            
            # 为了演示，返回一个模拟结果
            mock_text = '这是一段模拟的语音识别结果'
            LogService.info(model_name=model_name, function_name=function_name, message=f'语音识别处理完成, 识别文本长度: {len(mock_text)}字符')
            
            return jsonify({
                'success': True,
                'text': mock_text
            })
        except Exception as e:
            LogService.error(model_name=model_name, function_name=function_name, message=f'语音识别处理失败: {str(e)}')
            return jsonify({
                'success': False,
                'error': str(e)
            }), 500
    
    @app.route('/api/text_to_speech', methods=['POST'])
    def text_to_speech():
        """文字转语音接口，返回音频文件"""
        current_time = LogService.get_current_time()
        function_name = 'text_to_speech'
        model_name = 'TextToSpeech'
        
        try:
            LogService.info(model_name=model_name, function_name=function_name, message='请求开始文本转语音处理')
            
            data = request.json
            text = data.get('text', '')
            language = data.get('language', 'zh-CN')
            character_id = data.get('character_id')
            
            # 参数验证
            if not text:
                LogService.error(model_name=model_name, function_name=function_name, message='请求参数错误: text参数不能为空')
                return jsonify({
                    'success': False,
                    'error': 'text参数不能为空'
                }), 400
            
            # 调试日志：打印文本内容的部分预览
            text_preview = text[:50] if text else ''
            LogService.debug(model_name=model_name, function_name=function_name, message=f'文本内容: {text_preview}..., 语言: {language}')
            
            # 获取角色特定的语音配置（如果提供了角色ID）
            voice_params = {}
            if character_id and character_id in character_configs:
                config = character_configs[character_id]
                voice_params['voice'] = config.get('tts_voice')
                voice_params['speed'] = config.get('tts_speed', 1.0)
                LogService.debug(model_name=model_name, function_name=function_name, message=f'使用角色特定语音配置: {character_id}')
            
            # 调用语音服务进行文本转语音
            audio_file = voice_service.text_to_speech(text, language=language, **voice_params)
            
            if not audio_file:
                LogService.error(model_name=model_name, function_name=function_name, message='文本转语音失败')
                return jsonify({
                    'success': False,
                    'error': '文本转语音失败'
                }), 500
            
            # 返回音频文件
            LogService.info(model_name=model_name, function_name=function_name, message=f'文本转语音成功, 文本长度: {len(text)}字符')
            
            # 创建临时文件用于返回
            temp_output = tempfile.NamedTemporaryFile(suffix='.mp3', delete=False)
            
            # 复制内容
            with open(audio_file, 'rb') as f:
                temp_output.write(f.read())
            temp_output.close()
            
            # 清理原文件
            try:
                os.remove(audio_file)
            except:
                pass
            
            # 发送文件
            response = send_file(temp_output.name, mimetype='audio/mpeg', as_attachment=False)
            
            # 注册清理函数
            @response.call_on_close
            def cleanup():
                try:
                    os.remove(temp_output.name)
                except:
                    pass
            
            return response
            
        except Exception as e:
            LogService.error(model_name=model_name, function_name=function_name, message=f'文本转语音处理失败: {str(e)}')
            return jsonify({
                'success': False,
                'error': str(e)
            }), 500
    
    @app.route('/api/multimodal_chat', methods=['POST'])
    def multimodal_chat():
        """支持文本、图像、音频、视频输入的多模态聊天接口"""
        current_time = LogService.get_current_time()
        function_name = 'multimodal_chat'
        
        try:
            # 请求开始日志
            LogService.info(model_name=Config.DEFAULT_MODEL, function_name=function_name, message='请求开始处理多模态聊天')
            
            # 检查是否是表单数据（可能包含文件）
            if 'Content-Type' in request.headers and 'multipart/form-data' in request.headers['Content-Type']:
                # 处理表单数据
                text = request.form.get('text', '')
                model = request.form.get('model') or Config.DEFAULT_MODEL
                
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
                model = data.get('model') or Config.DEFAULT_MODEL
            
            # 调试日志：打印请求参数信息
            input_types = []
            if text: input_types.append('text')
            if image: input_types.append('image')
            if audio: input_types.append('audio')
            if video: input_types.append('video')
            LogService.debug(model_name=model, function_name=function_name, message=f'模型: {model}, 输入类型: {", ".join(input_types)}')
            
            # 调试日志：打印文本内容的部分预览
            if text:
                text_preview = text[:50] if text else ''
                LogService.debug(model_name=model, function_name=function_name, message=f'文本内容: {text_preview}...')
            
            # 至少需要一个输入类型
            if not any([text, image, audio, video]):
                LogService.error(model_name=model, function_name=function_name, message='请求参数错误: 至少需要提供text、image、audio或video中的一项')
                return jsonify({
                    'success': False,
                    'error': '至少需要提供text、image、audio或video中的一项'
                }), 400
            
            # 调用多模态服务
            response = ai_service.multimodal_completion(text, image, audio, video, model)
            
            if not response:
                LogService.error(model_name=model, function_name=function_name, message='多模态服务响应为空')
                return jsonify({
                    'success': False,
                    'error': '多模态服务响应失败'
                }), 500
            
            # 提取响应内容
            content = response.get('choices', [{}])[0].get('message', {}).get('content', '')
            
            # 请求成功日志
            LogService.info(model_name=model, function_name=function_name, message=f'多模态聊天请求处理成功, 响应内容长度: {len(content)}字符')
            
            return jsonify({
                'success': True,
                'content': content
            })
        except Exception as e:
            LogService.error(model_name=Config.DEFAULT_MODEL, function_name=function_name, message=f'多模态聊天请求处理失败: {str(e)}')
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