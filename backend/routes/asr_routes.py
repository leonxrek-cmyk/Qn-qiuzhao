"""
语音识别API路由
"""
from flask import Blueprint, request, jsonify
import logging
from services.asr_service import asr_service
from werkzeug.utils import secure_filename
import os
import tempfile

logger = logging.getLogger(__name__)

# 创建蓝图
asr_bp = Blueprint('asr', __name__)

# 支持的音频格式
ALLOWED_EXTENSIONS = {'wav', 'mp3', 'webm', 'ogg', 'm4a'}

def allowed_file(filename):
    """检查文件扩展名是否被允许"""
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

@asr_bp.route('/voice_recognition', methods=['POST'])
def voice_recognition():
    """
    语音识别接口
    接收音频文件，返回识别的文字
    """
    try:
        # 检查是否是测试模式
        if request.content_type == 'application/json':
            data = request.get_json()
            if data and data.get('test'):
                logger.info("收到测试请求")
                return jsonify({
                    'success': True,
                    'text': '测试成功',
                    'message': '后端API工作正常'
                })
        
        # 检查是否有文件上传
        if 'audio' not in request.files:
            return jsonify({
                'success': False,
                'error': '没有上传音频文件'
            }), 400
        
        audio_file = request.files['audio']
        
        # 检查文件是否为空
        if audio_file.filename == '':
            return jsonify({
                'success': False,
                'error': '没有选择文件'
            }), 400
        
        # 检查文件格式
        if not allowed_file(audio_file.filename):
            return jsonify({
                'success': False,
                'error': f'不支持的音频格式，支持的格式: {", ".join(ALLOWED_EXTENSIONS)}'
            }), 400
        
        # 获取音频格式和MIME类型
        audio_format = audio_file.filename.rsplit('.', 1)[1].lower() if '.' in audio_file.filename else 'unknown'
        content_type = audio_file.content_type or 'unknown'
        
        # 读取音频数据
        audio_data = audio_file.read()
        
        # 检查文件大小 (限制为10MB)
        max_size = 10 * 1024 * 1024  # 10MB
        if len(audio_data) > max_size:
            return jsonify({
                'success': False,
                'error': '音频文件过大，请上传小于10MB的文件'
            }), 400
        
        # 检查文件是否为空
        if len(audio_data) == 0:
            return jsonify({
                'success': False,
                'error': '音频文件为空'
            }), 400
        
        # 检查最小文件大小（至少1KB）
        if len(audio_data) < 1000:
            logger.warning(f"音频文件过小: {len(audio_data)} bytes，可能录音时间不足")
            return jsonify({
                'success': False,
                'error': '音频文件过小，请确保录音时间足够长（至少1秒）'
            }), 400
        
        logger.info(f"接收到音频文件: {audio_file.filename}, 大小: {len(audio_data)} bytes, 扩展名: {audio_format}, MIME: {content_type}")
        
        # 检查音频数据的前几个字节，用于调试和格式检测
        if len(audio_data) >= 12:
            header_bytes = audio_data[:12]
            logger.info(f"音频文件头部字节: {header_bytes.hex()}")
            
            # 检查是否是有效的音频格式
            detected_format = None
            if audio_data.startswith(b'RIFF') and b'WAVE' in audio_data[:20]:
                detected_format = "WAV"
                logger.info("检测到WAV格式文件")
            elif audio_data.startswith(b'\x1a\x45\xdf\xa3'):
                detected_format = "WebM"
                logger.info("检测到WebM格式文件")
            elif audio_data.startswith(b'ID3') or (audio_data[0] == 0xFF and (audio_data[1] & 0xE0) == 0xE0):
                detected_format = "MP3"
                logger.info("检测到MP3格式文件")
            elif audio_data.startswith(b'ftyp'):
                detected_format = "MP4/M4A"
                logger.info("检测到MP4/M4A格式文件")
            else:
                logger.warning(f"未识别的音频格式，文件头: {header_bytes.hex()}")
            
            # 如果检测到的格式与扩展名不匹配，使用检测到的格式
            if detected_format and detected_format.lower() != audio_format:
                logger.warning(f"格式不匹配，使用检测到的格式: {detected_format} (原扩展名: {audio_format})")
                # 优先使用检测到的格式
                if detected_format.lower() in ['wav', 'webm', 'mp3', 'mp4', 'm4a']:
                    audio_format = detected_format.lower()
                    
            # 如果不是WAV格式，记录警告
            if audio_format != 'wav':
                logger.error(f"收到非WAV格式音频: {audio_format}")
                logger.error("前端音频转换可能失败，建议检查转换逻辑")
        
        # 调用语音识别服务
        result = asr_service.speech_to_text(audio_data, audio_format)
        
        if result['success']:
            logger.info(f"语音识别成功: {result['text']}")
            return jsonify({
                'success': True,
                'text': result['text'],
                'confidence': result.get('confidence', 0)
            })
        else:
            logger.error(f"语音识别失败: {result['error']}")
            return jsonify({
                'success': False,
                'error': result['error']
            }), 500
            
    except Exception as e:
        logger.error(f"语音识别接口发生异常: {e}")
        return jsonify({
            'success': False,
            'error': '服务器内部错误'
        }), 500

@asr_bp.route('/voice_recognition_base64', methods=['POST'])
def voice_recognition_base64():
    """
    语音识别接口 - Base64格式
    接收Base64编码的音频数据，返回识别的文字
    """
    try:
        data = request.get_json()
        
        if not data:
            return jsonify({
                'success': False,
                'error': '请求数据为空'
            }), 400
        
        # 获取Base64音频数据
        audio_base64 = data.get('audio_data')
        audio_format = data.get('format', 'wav')
        
        if not audio_base64:
            return jsonify({
                'success': False,
                'error': '缺少音频数据'
            }), 400
        
        try:
            import base64
            # 解码Base64数据
            audio_data = base64.b64decode(audio_base64)
        except Exception as e:
            return jsonify({
                'success': False,
                'error': 'Base64数据格式错误'
            }), 400
        
        # 检查文件大小
        max_size = 10 * 1024 * 1024  # 10MB
        if len(audio_data) > max_size:
            return jsonify({
                'success': False,
                'error': '音频数据过大，请上传小于10MB的数据'
            }), 400
        
        logger.info(f"接收到Base64音频数据, 大小: {len(audio_data)} bytes, 格式: {audio_format}")
        
        # 调用语音识别服务
        result = asr_service.speech_to_text(audio_data, audio_format)
        
        if result['success']:
            logger.info(f"语音识别成功: {result['text']}")
            return jsonify({
                'success': True,
                'text': result['text'],
                'confidence': result.get('confidence', 0)
            })
        else:
            logger.error(f"语音识别失败: {result['error']}")
            return jsonify({
                'success': False,
                'error': result['error']
            }), 500
            
    except Exception as e:
        logger.error(f"语音识别接口发生异常: {e}")
        return jsonify({
            'success': False,
            'error': '服务器内部错误'
        }), 500
