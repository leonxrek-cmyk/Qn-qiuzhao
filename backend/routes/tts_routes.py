"""
TTS语音合成API路由
"""
from flask import Blueprint, request, jsonify
import logging
from services.tts_service import tts_service

logger = logging.getLogger(__name__)

# 创建蓝图
tts_bp = Blueprint('tts', __name__)

@tts_bp.route('/text_to_speech', methods=['POST'])
def text_to_speech():
    """
    文字转语音接口
    接收文本和角色信息，返回语音数据
    """
    try:
        data = request.get_json()
        
        if not data:
            return jsonify({
                'success': False,
                'error': '请求数据为空'
            }), 400
        
        # 获取参数
        text = data.get('text', '').strip()
        character_id = data.get('character_id')
        encoding = data.get('encoding', 'mp3')
        
        # 验证参数
        if not text:
            return jsonify({
                'success': False,
                'error': '文本内容不能为空'
            }), 400
        
        if len(text) > 1000:
            return jsonify({
                'success': False,
                'error': '文本内容过长，请控制在1000字符以内'
            }), 400
        
        logger.info(f"TTS请求: 角色={character_id}, 文本长度={len(text)}, 编码={encoding}")
        
        # 调用TTS服务
        result = tts_service.text_to_speech(text, character_id, encoding)
        
        if result['success']:
            logger.info(f"TTS成功: 音色={result.get('voice_type')}, 语速={result.get('speed_ratio')}")
            return jsonify({
                'success': True,
                'audio_data': result['audio_data'],
                'duration': result['duration'],
                'voice_type': result['voice_type'],
                'speed_ratio': result['speed_ratio'],
                'cleaned_text': result['cleaned_text']
            })
        else:
            logger.error(f"TTS失败: {result['error']}")
            return jsonify({
                'success': False,
                'error': result['error']
            }), 500
            
    except Exception as e:
        logger.error(f"TTS接口发生异常: {e}")
        return jsonify({
            'success': False,
            'error': '服务器内部错误'
        }), 500

@tts_bp.route('/voice_list', methods=['GET'])
def get_voice_list():
    """
    获取可用音色列表
    """
    try:
        voice_list = [
            # 女性音色
            {
                'id': 'qiniu_zh_female_wwxkjx',
                'name': '温文学科教学',
                'gender': 'female',
                'language': 'zh'
            },
            {
                'id': 'qiniu_zh_female_tmjxxy',
                'name': '甜美学小源',
                'gender': 'female',
                'language': 'zh'
            },
            {
                'id': 'qiniu_zh_female_zxjxnjs',
                'name': '知性教学女教师',
                'gender': 'female',
                'language': 'zh'
            },
            {
                'id': 'qiniu_zh_female_glktss',
                'name': '古灵可爱思思',
                'gender': 'female',
                'language': 'zh'
            },
            {
                'id': 'qiniu_zh_female_kljxdd',
                'name': '可爱教学丹丹',
                'gender': 'female',
                'language': 'zh'
            },
            # 男性音色
            {
                'id': 'qiniu_zh_male_whxkxg',
                'name': '文化学者小刚',
                'gender': 'male',
                'language': 'zh'
            },
            {
                'id': 'qiniu_zh_male_ybxknjs',
                'name': '优秀学科男教师',
                'gender': 'male',
                'language': 'zh'
            },
            {
                'id': 'qiniu_zh_male_tyygjs',
                'name': '通用语言讲师',
                'gender': 'male',
                'language': 'zh'
            },
            {
                'id': 'qiniu_zh_male_hlsnkk',
                'name': '活力少年开朗',
                'gender': 'male',
                'language': 'zh'
            },
            {
                'id': 'qiniu_zh_male_wncwxz',
                'name': '温暖成稳学者',
                'gender': 'male',
                'language': 'zh'
            }
        ]
        
        return jsonify({
            'success': True,
            'voices': voice_list
        })
        
    except Exception as e:
        logger.error(f"获取音色列表异常: {e}")
        return jsonify({
            'success': False,
            'error': '获取音色列表失败'
        }), 500

@tts_bp.route('/character_voices', methods=['GET'])
def get_character_voices():
    """
    获取角色音色映射
    """
    try:
        character_voices = tts_service.character_voices
        
        return jsonify({
            'success': True,
            'character_voices': character_voices,
            'default_voice': tts_service.default_voice
        })
        
    except Exception as e:
        logger.error(f"获取角色音色映射异常: {e}")
        return jsonify({
            'success': False,
            'error': '获取角色音色映射失败'
        }), 500
