"""
管理员路由
"""
from flask import Blueprint, request, jsonify
from log_service import LogService
from user_service import get_user_service
from session_service import SessionService
import json
import os
from datetime import datetime, timedelta

admin_bp = Blueprint('admin', __name__, url_prefix='/admin')

def load_character_configs():
    """加载角色配置"""
    try:
        config_path = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'character_configs.json')
        with open(config_path, 'r', encoding='utf-8') as f:
            return json.load(f)
    except Exception as e:
        print(f"加载角色配置失败: {str(e)}")
        return {}

def save_character_configs(configs):
    """保存角色配置"""
    try:
        config_path = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'character_configs.json')
        with open(config_path, 'w', encoding='utf-8') as f:
            json.dump(configs, f, ensure_ascii=False, indent=2)
        return True
    except Exception as e:
        print(f"保存角色配置失败: {str(e)}")
        return False

def check_admin_permission(token):
    """检查管理员权限"""
    user_service = get_user_service()
    return user_service.is_admin_user(token)

@admin_bp.route('/users', methods=['GET'])
def get_all_users():
    """获取所有用户"""
    current_time = LogService.get_current_time()
    function_name = 'get_all_users'
    model_name = 'Admin'
    
    try:
        token = request.headers.get('Authorization', '').replace('Bearer ', '')
        if not token:
            return jsonify({'success': False, 'error': '缺少认证令牌'}), 401
        
        if not check_admin_permission(token):
            return jsonify({'success': False, 'error': '权限不足'}), 403
        
        user_service = get_user_service()
        result = user_service.get_all_users(token)
        
        LogService.log(current_time=current_time, model_name=model_name, function_name=function_name, 
                      log_level='Info', message=f'管理员获取用户列表，共{result.get("total", 0)}个用户')
        
        return jsonify(result)
        
    except Exception as e:
        LogService.log(current_time=current_time, model_name=model_name, function_name=function_name, 
                      log_level='Error', message=f'获取用户列表失败: {str(e)}')
        return jsonify({'success': False, 'error': '获取用户列表失败'}), 500

@admin_bp.route('/users', methods=['POST'])
def create_user():
    """创建用户"""
    current_time = LogService.get_current_time()
    function_name = 'create_user'
    model_name = 'Admin'
    
    try:
        token = request.headers.get('Authorization', '').replace('Bearer ', '')
        if not token:
            return jsonify({'success': False, 'error': '缺少认证令牌'}), 401
        
        if not check_admin_permission(token):
            return jsonify({'success': False, 'error': '权限不足'}), 403
        
        data = request.json
        username = data.get('username', '').strip()
        password = data.get('password', '').strip()
        email = data.get('email', '').strip()
        nickname = data.get('nickname', '').strip()
        is_admin = data.get('is_admin', False)
        
        if not username or not password:
            return jsonify({'success': False, 'error': '用户名和密码不能为空'}), 400
        
        user_service = get_user_service()
        result = user_service.register_user(username, password, email)
        
        if result['success']:
            # 更新用户信息
            user_id = result['user']['id']
            if nickname:
                user_service.update_user_nickname_by_id(user_id, nickname)
            if is_admin:
                user_service.set_admin_status(user_id, True)
            
            LogService.log(current_time=current_time, model_name=model_name, function_name=function_name, 
                          log_level='Info', message=f'管理员创建用户: {username}')
        
        return jsonify(result)
        
    except Exception as e:
        LogService.log(current_time=current_time, model_name=model_name, function_name=function_name, 
                      log_level='Error', message=f'创建用户失败: {str(e)}')
        return jsonify({'success': False, 'error': '创建用户失败'}), 500

@admin_bp.route('/users/<user_id>', methods=['PUT'])
def update_user(user_id):
    """更新用户"""
    current_time = LogService.get_current_time()
    function_name = 'update_user'
    model_name = 'Admin'
    
    try:
        token = request.headers.get('Authorization', '').replace('Bearer ', '')
        if not token:
            return jsonify({'success': False, 'error': '缺少认证令牌'}), 401
        
        if not check_admin_permission(token):
            return jsonify({'success': False, 'error': '权限不足'}), 403
        
        data = request.json
        nickname = data.get('nickname', '').strip()
        email = data.get('email', '').strip()
        is_admin = data.get('is_admin', False)
        
        user_service = get_user_service()
        
        # 更新昵称
        if nickname:
            user_service.update_user_nickname_by_id(user_id, nickname)
        
        # 更新邮箱
        if email:
            user_service.update_user_email_by_id(user_id, email)
        
        # 更新管理员状态
        user_service.set_admin_status(user_id, is_admin)
        
        LogService.log(current_time=current_time, model_name=model_name, function_name=function_name, 
                      log_level='Info', message=f'管理员更新用户: {user_id}')
        
        return jsonify({'success': True, 'message': '用户更新成功'})
        
    except Exception as e:
        LogService.log(current_time=current_time, model_name=model_name, function_name=function_name, 
                      log_level='Error', message=f'更新用户失败: {str(e)}')
        return jsonify({'success': False, 'error': '更新用户失败'}), 500

@admin_bp.route('/users/<user_id>', methods=['DELETE'])
def delete_user(user_id):
    """删除用户"""
    current_time = LogService.get_current_time()
    function_name = 'delete_user'
    model_name = 'Admin'
    
    try:
        token = request.headers.get('Authorization', '').replace('Bearer ', '')
        if not token:
            return jsonify({'success': False, 'error': '缺少认证令牌'}), 401
        
        if not check_admin_permission(token):
            return jsonify({'success': False, 'error': '权限不足'}), 403
        
        user_service = get_user_service()
        result = user_service.delete_user(user_id)
        
        if result:
            LogService.log(current_time=current_time, model_name=model_name, function_name=function_name, 
                          log_level='Info', message=f'管理员删除用户: {user_id}')
            return jsonify({'success': True, 'message': '用户删除成功'})
        else:
            return jsonify({'success': False, 'error': '用户不存在或删除失败'}), 404
        
    except Exception as e:
        LogService.log(current_time=current_time, model_name=model_name, function_name=function_name, 
                      log_level='Error', message=f'删除用户失败: {str(e)}')
        return jsonify({'success': False, 'error': '删除用户失败'}), 500

@admin_bp.route('/characters', methods=['POST'])
def create_character():
    """创建角色"""
    current_time = LogService.get_current_time()
    function_name = 'create_character'
    model_name = 'Admin'
    
    try:
        token = request.headers.get('Authorization', '').replace('Bearer ', '')
        if not token:
            return jsonify({'success': False, 'error': '缺少认证令牌'}), 401
        
        if not check_admin_permission(token):
            return jsonify({'success': False, 'error': '权限不足'}), 403
        
        data = request.json
        character_id = data.get('id', '').strip()
        
        if not character_id:
            return jsonify({'success': False, 'error': '角色ID不能为空'}), 400
        
        configs = load_character_configs()
        
        if character_id in configs:
            return jsonify({'success': False, 'error': '角色ID已存在'}), 400
        
        # 创建新角色配置
        new_character = {
            'id': character_id,
            'name': data.get('name', ''),
            'description': data.get('description', ''),
            'avatar': data.get('avatar', f'/avatars/{character_id}.png'),
            'tags': data.get('tags', []),
            'prompt': data.get('prompt', ''),
            'voice_params': data.get('voice_params', {}),
            'language_style': data.get('language_style', 'formal')
        }
        
        configs[character_id] = new_character
        
        if save_character_configs(configs):
            LogService.log(current_time=current_time, model_name=model_name, function_name=function_name, 
                          log_level='Info', message=f'管理员创建角色: {character_id}')
            return jsonify({'success': True, 'message': '角色创建成功'})
        else:
            return jsonify({'success': False, 'error': '保存角色配置失败'}), 500
        
    except Exception as e:
        LogService.log(current_time=current_time, model_name=model_name, function_name=function_name, 
                      log_level='Error', message=f'创建角色失败: {str(e)}')
        return jsonify({'success': False, 'error': '创建角色失败'}), 500

@admin_bp.route('/characters/<character_id>', methods=['PUT'])
def update_character(character_id):
    """更新角色"""
    current_time = LogService.get_current_time()
    function_name = 'update_character'
    model_name = 'Admin'
    
    try:
        token = request.headers.get('Authorization', '').replace('Bearer ', '')
        if not token:
            return jsonify({'success': False, 'error': '缺少认证令牌'}), 401
        
        if not check_admin_permission(token):
            return jsonify({'success': False, 'error': '权限不足'}), 403
        
        data = request.json
        configs = load_character_configs()
        
        if character_id not in configs:
            return jsonify({'success': False, 'error': '角色不存在'}), 404
        
        # 更新角色配置
        configs[character_id].update({
            'name': data.get('name', configs[character_id].get('name', '')),
            'description': data.get('description', configs[character_id].get('description', '')),
            'avatar': data.get('avatar', configs[character_id].get('avatar', '')),
            'tags': data.get('tags', configs[character_id].get('tags', [])),
            'prompt': data.get('prompt', configs[character_id].get('prompt', '')),
            'voice_params': data.get('voice_params', configs[character_id].get('voice_params', {})),
            'language_style': data.get('language_style', configs[character_id].get('language_style', 'formal'))
        })
        
        if save_character_configs(configs):
            LogService.log(current_time=current_time, model_name=model_name, function_name=function_name, 
                          log_level='Info', message=f'管理员更新角色: {character_id}')
            return jsonify({'success': True, 'message': '角色更新成功'})
        else:
            return jsonify({'success': False, 'error': '保存角色配置失败'}), 500
        
    except Exception as e:
        LogService.log(current_time=current_time, model_name=model_name, function_name=function_name, 
                      log_level='Error', message=f'更新角色失败: {str(e)}')
        return jsonify({'success': False, 'error': '更新角色失败'}), 500

@admin_bp.route('/characters/<character_id>', methods=['DELETE'])
def delete_character(character_id):
    """删除角色"""
    current_time = LogService.get_current_time()
    function_name = 'delete_character'
    model_name = 'Admin'
    
    try:
        token = request.headers.get('Authorization', '').replace('Bearer ', '')
        if not token:
            return jsonify({'success': False, 'error': '缺少认证令牌'}), 401
        
        if not check_admin_permission(token):
            return jsonify({'success': False, 'error': '权限不足'}), 403
        
        configs = load_character_configs()
        
        if character_id not in configs:
            return jsonify({'success': False, 'error': '角色不存在'}), 404
        
        del configs[character_id]
        
        if save_character_configs(configs):
            LogService.log(current_time=current_time, model_name=model_name, function_name=function_name, 
                          log_level='Info', message=f'管理员删除角色: {character_id}')
            return jsonify({'success': True, 'message': '角色删除成功'})
        else:
            return jsonify({'success': False, 'error': '保存角色配置失败'}), 500
        
    except Exception as e:
        LogService.log(current_time=current_time, model_name=model_name, function_name=function_name, 
                      log_level='Error', message=f'删除角色失败: {str(e)}')
        return jsonify({'success': False, 'error': '删除角色失败'}), 500

@admin_bp.route('/statistics', methods=['GET'])
def get_statistics():
    """获取统计数据"""
    current_time = LogService.get_current_time()
    function_name = 'get_statistics'
    model_name = 'Admin'
    
    try:
        token = request.headers.get('Authorization', '').replace('Bearer ', '')
        if not token:
            return jsonify({'success': False, 'error': '缺少认证令牌'}), 401
        
        if not check_admin_permission(token):
            return jsonify({'success': False, 'error': '权限不足'}), 403
        
        user_service = get_user_service()
        session_service = SessionService()
        
        # 获取基本统计
        users_result = user_service.get_all_users(token)
        total_users = users_result.get('total', 0) if users_result.get('success') else 0
        
        # 获取角色数量
        configs = load_character_configs()
        total_characters = len(configs)
        
        # 获取会话统计（简化版本，实际应该从数据库获取）
        total_messages = 0
        today_messages = 0
        popular_characters = []
        
        # 这里应该实现真实的统计逻辑
        # 目前返回模拟数据
        statistics = {
            'totalMessages': total_messages,
            'totalUsers': total_users,
            'totalCharacters': total_characters,
            'todayMessages': today_messages,
            'popularCharacters': popular_characters
        }
        
        LogService.log(current_time=current_time, model_name=model_name, function_name=function_name, 
                      log_level='Info', message='管理员获取统计数据')
        
        return jsonify({'success': True, 'data': statistics})
        
    except Exception as e:
        LogService.log(current_time=current_time, model_name=model_name, function_name=function_name, 
                      log_level='Error', message=f'获取统计数据失败: {str(e)}')
        return jsonify({'success': False, 'error': '获取统计数据失败'}), 500
