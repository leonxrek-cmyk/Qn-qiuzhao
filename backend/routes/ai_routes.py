"""
AI相关的路由处理
"""
from flask import Blueprint, request, jsonify
import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from config import Config
from routes.ai_service import AIService
from services.log_service import LogService
from services.session_service import SessionService
import json

# 创建蓝图
ai_bp = Blueprint('ai', __name__)

# 角色配置文件路径
CHARACTERS_CONFIG_FILE = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), 'character_configs.json')

def load_character_configs():
    """加载角色配置"""
    try:
        with open(CHARACTERS_CONFIG_FILE, 'r', encoding='utf-8') as f:
            return json.load(f)
    except Exception as e:
        current_time = LogService.get_current_time()
        LogService.log(current_time=current_time, model_name='App', function_name='load_character_configs', log_level='Error', message=f'加载角色配置失败: {str(e)}')
        return {}

# 移除全局缓存，每次使用时重新加载

@ai_bp.route('/models', methods=['GET'])
def get_models():
    """获取可用的AI模型列表"""
    current_time = LogService.get_current_time()
    model_name = Config.DEFAULT_MODEL
    function_name = 'get_models'
    
    # 请求开始日志
    LogService.log(current_time=current_time, model_name=model_name, function_name=function_name, log_level='Info', message='请求开始获取可用模型列表')
    
    try:
        ai_service = AIService()
        models = ai_service.list_models()
        
        # 请求成功日志
        LogService.log(current_time=current_time, model_name=model_name, function_name=function_name, log_level='Info', message=f'获取模型列表成功, 模型数量: {len(models)}')
        
        return jsonify({
            'success': True,
            'models': models
        })
    except Exception as e:
        # 请求失败日志
        LogService.log(current_time=current_time, model_name=model_name, function_name=function_name, log_level='Error', message=f'获取模型列表失败: {str(e)}')
    
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@ai_bp.route('/chat', methods=['POST'])
def chat():
    """基础聊天接口"""
    current_time = LogService.get_current_time()
    function_name = 'chat'
    
    try:
        # 请求开始日志
        LogService.log(current_time=current_time, model_name=Config.DEFAULT_MODEL, function_name=function_name, log_level='Info', message='请求开始处理聊天消息')
        
        data = request.json
        messages = data.get('messages', [])
        model = data.get('model') or Config.DEFAULT_MODEL
        stream = data.get('stream', False)
        max_tokens = data.get('max_tokens', 4096)
        
        # 调试日志：打印请求参数信息
        LogService.log(current_time=current_time, model_name=model, function_name=function_name, log_level='Debug', message=f'模型: {model}, 消息数量: {len(messages)}, max_tokens: {max_tokens}')
        
        if not messages:
            LogService.log(current_time=current_time, model_name=model, function_name=function_name, log_level='Error', message='请求参数错误: messages参数不能为空')
            return jsonify({
                'success': False,
                'error': 'messages参数不能为空'
            }), 400
        
        # 调试日志：打印最后一条消息的部分内容
        last_message_content = messages[-1].get('content', '')[:50] if messages else ''
        LogService.log(current_time=current_time, model_name=model, function_name=function_name, log_level='Debug', message=f'最后一条消息内容: {last_message_content}...')
        
        ai_service = AIService()
        response = ai_service.chat_completion(messages, model, stream, max_tokens)
        
        if not response:
            LogService.log(current_time=current_time, model_name=model, function_name=function_name, log_level='Error', message='AI服务响应为空')
            return jsonify({
                'success': False,
                'error': 'AI服务响应失败'
            }), 500
        
        # 提取响应内容
        content = response.get('choices', [{}])[0].get('message', {}).get('content', '')
        
        # 请求成功日志
        LogService.log(current_time=current_time, model_name=model, function_name=function_name, log_level='Info', message=f'聊天请求处理成功, 响应内容长度: {len(content)}字符')
        
        return jsonify({
            'success': True,
            'content': content
        })
    except Exception as e:
        # 请求失败日志
        LogService.log(current_time=current_time, model_name=Config.DEFAULT_MODEL, function_name=function_name, log_level='Error', message=f'聊天请求处理失败: {str(e)}')
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@ai_bp.route('/character_chat', methods=['POST'])
def character_chat():
    """角色扮演聊天接口（支持会话上下文）"""
    current_time = LogService.get_current_time()
    function_name = 'character_chat'
    
    try:
        data = request.json
        character_id = data.get('character_id', '')
        character_name = data.get('character_name', '')
        character_description = data.get('character_description', '')
        user_query = data.get('user_query', '')
        session_id = data.get('session_id')  # 新增：会话ID
        model = data.get('model') or Config.DEFAULT_MODEL
        stream = data.get('stream', False)
        
        # 如果提供了character_id，使用配置文件中的角色信息
        character_configs = load_character_configs()
        if character_id and character_id in character_configs:
            config = character_configs[character_id]
            character_name = config['name']
            character_description = config['description']
        
        # 请求开始日志
        if character_id:
            LogService.log(current_time=current_time, model_name=model, function_name=function_name, 
                         log_level='Info', message=f'请求开始处理角色扮演聊天, 角色ID: {character_id}, 角色名称: {character_name}, 会话ID: {session_id}')
        else:
            LogService.log(current_time=current_time, model_name=model, function_name=function_name, 
                         log_level='Info', message=f'请求开始处理角色扮演聊天, 角色名称: {character_name}, 会话ID: {session_id}')
        
        if not character_name or not user_query:
            LogService.log(current_time=current_time, model_name=model, function_name=function_name, 
                         log_level='Error', message='请求参数错误: character_name和user_query参数不能为空')
            return jsonify({
                'success': False,
                'error': 'character_name和user_query参数不能为空'
            }), 400
        
        # 调试日志：打印用户查询的部分内容
        user_query_content = user_query[:50] if user_query else ''
        LogService.log(current_time=current_time, model_name=model, function_name=function_name, 
                     log_level='Debug', message=f'用户查询内容: {user_query_content}...')
        
        ai_service = AIService()
        session_service = SessionService()
        
        # 如果提供了会话ID，使用会话上下文
        if session_id:
            # 先将用户消息添加到会话中
            session_service.add_message(session_id, 'user', user_query, character_id)
            
            # 获取会话上下文消息
            context_messages = session_service.get_context_messages(session_id, character_name, character_description)
            
            # 使用带上下文的聊天方法
            response = ai_service.character_chat_with_context(
                context_messages, character_name, character_description, model, stream
            )
        else:
            # 使用角色配置文件中的提示词模板（如果有）
            character_configs = load_character_configs()
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
            LogService.log(current_time=current_time, model_name=model, function_name=function_name, 
                         log_level='Error', message='AI服务响应为空')
            return jsonify({
                'success': False,
                'error': 'AI服务响应失败'
            }), 500
        
        # 提取响应内容
        content = response.get('choices', [{}])[0].get('message', {}).get('content', '')
        
        # 如果有会话ID，将AI回复也添加到会话中
        if session_id:
            session_service.add_message(session_id, 'assistant', content, character_id)
        
        # 请求成功日志
        LogService.log(current_time=current_time, model_name=model, function_name=function_name, 
                     log_level='Info', message=f'角色扮演聊天请求处理成功, 响应内容长度: {len(content)}字符')
        
        return jsonify({
            'success': True,
            'content': content,
            'character_id': character_id,
            'session_id': session_id
        })
    except Exception as e:
        LogService.log(current_time=current_time, model_name=Config.DEFAULT_MODEL, function_name=function_name, 
                     log_level='Error', message=f'角色扮演聊天请求处理失败: {str(e)}')
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@ai_bp.route('/multimodal_chat', methods=['POST'])
def multimodal_chat():
    """支持文本、图像、音频、视频输入的多模态聊天接口"""
    current_time = LogService.get_current_time()
    function_name = 'multimodal_chat'
    
    try:
        # 请求开始日志
        LogService.log(current_time=current_time, model_name=Config.DEFAULT_MODEL, function_name=function_name, log_level='Info', message='请求开始处理多模态聊天')
        
        import base64
        
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
        LogService.log(current_time=current_time, model_name=model, function_name=function_name, log_level='Debug', message=f'模型: {model}, 输入类型: {", ".join(input_types)}')

        # 调试日志：打印文本内容的部分预览
        if text:
            text_preview = text[:50] if text else ''
            LogService.log(current_time=current_time, model_name=model, function_name=function_name, log_level='Debug', message=f'文本内容: {text_preview}...')
        
        # 至少需要一个输入类型
        if not any([text, image, audio, video]):
            LogService.log(current_time=current_time, model_name=model, function_name=function_name, log_level='Error', message='请求参数错误: 至少需要提供text、image、audio或video中的一项')
            return jsonify({
                'success': False,
                'error': '至少需要提供text、image、audio或video中的一项'
            }), 400
        
        # 调用多模态服务
        ai_service = AIService()
        response = ai_service.multimodal_completion(text, image, audio, video, model)
        
        if not response:
            LogService.log(current_time=current_time, model_name=model, function_name=function_name, log_level='Error', message='多模态服务响应为空')
            return jsonify({
                'success': False,
                'error': '多模态服务响应失败'
            }), 500
        
        # 提取响应内容
        content = response.get('choices', [{}])[0].get('message', {}).get('content', '')
        
        # 请求成功日志
        LogService.log(current_time=current_time, model_name=model, function_name=function_name, log_level='Info', message=f'多模态聊天请求处理成功, 响应内容长度: {len(content)}字符')
        
        return jsonify({
            'success': True,
            'content': content
        })
    except Exception as e:
        LogService.log(current_time=current_time, model_name=Config.DEFAULT_MODEL, function_name=function_name, log_level='Error', message=f'多模态聊天请求处理失败: {str(e)}')
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500
