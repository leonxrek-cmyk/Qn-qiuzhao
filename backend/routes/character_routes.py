"""
角色配置相关的路由处理
"""
from flask import Blueprint, request, jsonify
import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from log_service import LogService
import json
from .avatar_service import create_character_avatar

# 创建蓝图
character_bp = Blueprint('character', __name__)

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

def ensure_character_avatar(character_id, character_name, avatar_path):
    """确保角色头像存在，如果不存在则自动生成"""
    try:
        # 构建完整的文件路径
        if avatar_path.startswith('/avatars/'):
            # 移除开头的斜杠，构建相对于项目根目录的路径
            relative_path = avatar_path[1:]  # 移除开头的 '/'
            full_path = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))), 'frontend', 'public', relative_path)
        else:
            # 如果路径不是以/avatars/开头，直接使用
            full_path = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))), 'frontend', 'public', avatar_path.lstrip('/'))
        
        # 检查文件是否存在
        if not os.path.exists(full_path):
            current_time = LogService.get_current_time()
            LogService.log(current_time=current_time, model_name='Avatar', function_name='ensure_character_avatar', 
                         log_level='Info', message=f'头像不存在，自动生成: {character_name} -> {full_path}')
            
            # 自动生成头像
            generated_path = create_character_avatar(character_name, character_id)
            LogService.log(current_time=current_time, model_name='Avatar', function_name='ensure_character_avatar', 
                         log_level='Info', message=f'头像生成成功: {character_name} -> {generated_path}')
            return generated_path
        else:
            return avatar_path
    except Exception as e:
        current_time = LogService.get_current_time()
        LogService.log(current_time=current_time, model_name='Avatar', function_name='ensure_character_avatar', 
                     log_level='Error', message=f'头像检查/生成失败: {character_name} - {str(e)}')
        return avatar_path  # 返回原路径，即使可能不存在

@character_bp.route('/character_config', methods=['GET'])
def get_all_character_configs():
    """获取所有角色的配置列表"""
    current_time = LogService.get_current_time()
    function_name = 'get_all_character_configs'
    model_name = 'API'
    
    try:
        LogService.log(current_time=current_time, model_name=model_name, function_name=function_name, log_level='Info', message='请求获取所有角色配置')
        
        # 每次请求时重新加载配置文件
        character_configs = load_character_configs()
        
        # 将字典转换为列表格式，并添加角色ID
        config_list = []
        for character_id, config in character_configs.items():
            config_with_id = config.copy()
            config_with_id['id'] = character_id
            
            # 确保头像存在，如果不存在则自动生成
            if 'avatar' in config_with_id and 'name' in config_with_id:
                config_with_id['avatar'] = ensure_character_avatar(
                    character_id, 
                    config_with_id['name'], 
                    config_with_id['avatar']
                )
            
            config_list.append(config_with_id)
        
        LogService.log(current_time=current_time, model_name=model_name, function_name=function_name, log_level='Info', message=f'获取角色配置列表成功, 角色数量: {len(config_list)}')
        return jsonify({
            'success': True,
            'configs': config_list
        })
    except Exception as e:
        LogService.log(current_time=current_time, model_name=model_name, function_name=function_name, log_level='Error', message=f'获取角色配置列表失败: {str(e)}')
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@character_bp.route('/character_config/<character_id>', methods=['GET'])
def get_character_config(character_id):
    """获取特定角色的配置"""
    current_time = LogService.get_current_time()
    function_name = 'get_character_config'
    model_name = 'API'
    
    try:
        LogService.log(current_time=current_time, model_name=model_name, function_name=function_name, log_level='Info', message=f'请求获取角色配置, 角色ID: {character_id}')
        
        # 每次请求时重新加载配置文件
        character_configs = load_character_configs()
        
        # 检查角色是否存在
        if character_id not in character_configs:
            LogService.log(current_time=current_time, model_name=model_name, function_name=function_name, log_level='Error', message=f'角色不存在: {character_id}')
            return jsonify({
                'success': False,
                'error': '角色不存在'
            }), 404
        
        config = character_configs[character_id].copy()
        config['id'] = character_id
        
        # 确保头像存在，如果不存在则自动生成
        if 'avatar' in config and 'name' in config:
            config['avatar'] = ensure_character_avatar(
                character_id, 
                config['name'], 
                config['avatar']
            )
        
        LogService.log(current_time=current_time, model_name=model_name, function_name=function_name, log_level='Info', message=f'获取角色配置成功: {character_id}')
        return jsonify({
            'success': True,
            'config': config
        })
    except Exception as e:
        LogService.log(current_time=current_time, model_name=model_name, function_name=function_name, log_level='Error', message=f'获取角色配置失败: {str(e)}')
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500
