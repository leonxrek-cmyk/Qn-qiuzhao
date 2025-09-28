"""
用户认证相关的路由处理
"""
from flask import Blueprint, request, jsonify
import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from services.log_service import LogService
from services.user_service import get_user_service
from .avatar_service import create_user_avatar

# 创建蓝图
auth_bp = Blueprint('auth', __name__)

@auth_bp.route('/register', methods=['POST'])
def register():
    """用户注册"""
    current_time = LogService.get_current_time()
    function_name = 'register'
    model_name = 'Auth'
    
    try:
        data = request.json
        username = data.get('username', '').strip()
        password = data.get('password', '').strip()
        email = data.get('email', '').strip()
        nickname = data.get('nickname', '').strip()
        
        LogService.log(current_time=current_time, model_name=model_name, function_name=function_name, 
                     log_level='Info', message=f'用户注册请求: {username}')
        
        # 参数验证
        if not username or not password:
            return jsonify({
                'success': False,
                'error': '用户名和密码不能为空'
            }), 400
        
        if len(username) < 3:
            return jsonify({
                'success': False,
                'error': '用户名至少需要3个字符'
            }), 400
        
        if len(password) < 6:
            return jsonify({
                'success': False,
                'error': '密码至少需要6个字符'
            }), 400
        
        user_service = get_user_service()
        result = user_service.register_user(username, password, email, nickname)
        
        if result['success']:
            LogService.log(current_time=current_time, model_name=model_name, function_name=function_name, 
                         log_level='Info', message=f'用户注册成功: {username}')
        else:
            LogService.log(current_time=current_time, model_name=model_name, function_name=function_name, 
                         log_level='Warning', message=f'用户注册失败: {username} - {result["error"]}')
        
        return jsonify(result)
        
    except Exception as e:
        LogService.log(current_time=current_time, model_name=model_name, function_name=function_name, 
                     log_level='Error', message=f'用户注册异常: {str(e)}')
        return jsonify({
            'success': False,
            'error': '注册失败，请稍后重试'
        }), 500

@auth_bp.route('/login', methods=['POST'])
def login():
    """用户登录"""
    current_time = LogService.get_current_time()
    function_name = 'login'
    model_name = 'Auth'
    
    try:
        data = request.json
        username = data.get('username', '').strip()
        password = data.get('password', '').strip()
        
        LogService.log(current_time=current_time, model_name=model_name, function_name=function_name, 
                     log_level='Info', message=f'用户登录请求: {username}')
        
        # 参数验证
        if not username or not password:
            return jsonify({
                'success': False,
                'error': '用户名和密码不能为空'
            }), 400
        
        user_service = get_user_service()
        result = user_service.login_user(username, password)
        
        if result['success']:
            # 登录成功后检查并生成头像（如果没有的话）
            try:
                user = result['user']
                if not user.get('avatar'):
                    # 使用昵称或用户名生成头像
                    display_name = user.get('nickname') or user.get('username')
                    avatar_data = create_user_avatar(display_name)
                    user_service.update_user_avatar(user['id'], avatar_data)
                    result['user']['avatar'] = avatar_data
                    LogService.log(current_time=current_time, model_name=model_name, function_name=function_name, 
                                 log_level='Info', message=f'为用户生成头像: {username}')
            except Exception as e:
                LogService.log(current_time=current_time, model_name=model_name, function_name=function_name, 
                             log_level='Warning', message=f'头像生成失败: {username} - {str(e)}')
            
            LogService.log(current_time=current_time, model_name=model_name, function_name=function_name, 
                         log_level='Info', message=f'用户登录成功: {username}')
            return jsonify(result), 200
        else:
            LogService.log(current_time=current_time, model_name=model_name, function_name=function_name, 
                         log_level='Warning', message=f'用户登录失败: {username} - {result["error"]}')
            # 登录失败时返回401状态码
            return jsonify(result), 401
        
    except Exception as e:
        LogService.log(current_time=current_time, model_name=model_name, function_name=function_name, 
                     log_level='Error', message=f'用户登录异常: {str(e)}')
        return jsonify({
            'success': False,
            'error': '登录失败，请稍后重试'
        }), 500

@auth_bp.route('/logout', methods=['POST'])
def logout():
    """用户登出"""
    current_time = LogService.get_current_time()
    function_name = 'logout'
    model_name = 'Auth'
    
    try:
        token = request.headers.get('Authorization', '').replace('Bearer ', '')
        
        if not token:
            return jsonify({
                'success': False,
                'error': '缺少认证令牌'
            }), 401
        
        user_service = get_user_service()
        result = user_service.logout_user(token)
        
        LogService.log(current_time=current_time, model_name=model_name, function_name=function_name, 
                     log_level='Info', message='用户登出')
        
        return jsonify(result)
        
    except Exception as e:
        LogService.log(current_time=current_time, model_name=model_name, function_name=function_name, 
                     log_level='Error', message=f'用户登出异常: {str(e)}')
        return jsonify({
            'success': False,
            'error': '登出失败，请稍后重试'
        }), 500

@auth_bp.route('/me', methods=['GET'])
def get_current_user():
    """获取当前用户信息"""
    current_time = LogService.get_current_time()
    function_name = 'get_current_user'
    model_name = 'Auth'
    
    try:
        token = request.headers.get('Authorization', '').replace('Bearer ', '')
        
        if not token:
            return jsonify({
                'success': False,
                'error': '缺少认证令牌'
            }), 401
        
        user_service = get_user_service()
        user = user_service.get_user_by_token(token)
        
        if not user:
            return jsonify({
                'success': False,
                'error': '无效的认证令牌'
            }), 401
        
        return jsonify({
            'success': True,
            'user': user
        })
        
    except Exception as e:
        LogService.log(current_time=current_time, model_name=model_name, function_name=function_name, 
                     log_level='Error', message=f'获取用户信息异常: {str(e)}')
        return jsonify({
            'success': False,
            'error': '获取用户信息失败'
        }), 500

@auth_bp.route('/settings', methods=['GET', 'PUT'])
def user_settings():
    """获取或更新用户设置"""
    current_time = LogService.get_current_time()
    function_name = 'user_settings'
    model_name = 'Auth'
    
    try:
        token = request.headers.get('Authorization', '').replace('Bearer ', '')
        
        if not token:
            return jsonify({
                'success': False,
                'error': '缺少认证令牌'
            }), 401
        
        user_service = get_user_service()
        user = user_service.get_user_by_token(token)
        
        if not user:
            return jsonify({
                'success': False,
                'error': '无效的认证令牌'
            }), 401
        
        if request.method == 'GET':
            # 获取用户设置
            return jsonify({
                'success': True,
                'settings': user['settings']
            })
        
        elif request.method == 'PUT':
            # 更新用户设置
            data = request.json
            settings = data.get('settings', {})
            
            result = user_service.update_user_settings(token, settings)
            
            if result['success']:
                LogService.log(current_time=current_time, model_name=model_name, function_name=function_name, 
                             log_level='Info', message=f'用户设置更新成功: {user["username"]}')
            
            return jsonify(result)
        
    except Exception as e:
        LogService.log(current_time=current_time, model_name=model_name, function_name=function_name, 
                     log_level='Error', message=f'用户设置操作异常: {str(e)}')
        return jsonify({
            'success': False,
            'error': '操作失败，请稍后重试'
        }), 500

@auth_bp.route('/avatar', methods=['PUT'])
def update_avatar():
    """更新用户头像"""
    current_time = LogService.get_current_time()
    function_name = 'update_avatar'
    model_name = 'Auth'
    
    try:
        token = request.headers.get('Authorization', '').replace('Bearer ', '')
        
        if not token:
            return jsonify({
                'success': False,
                'error': '缺少认证令牌'
            }), 401
        
        data = request.json
        avatar_url = data.get('avatar', '').strip()
        
        if not avatar_url:
            return jsonify({
                'success': False,
                'error': '头像URL不能为空'
            }), 400
        
        user_service = get_user_service()
        result = user_service.update_user_avatar(token, avatar_url)
        
        if result['success']:
            LogService.log(current_time=current_time, model_name=model_name, function_name=function_name, 
                         log_level='Info', message='用户头像更新成功')
        
        return jsonify(result)
        
    except Exception as e:
        LogService.log(current_time=current_time, model_name=model_name, function_name=function_name, 
                     log_level='Error', message=f'更新头像异常: {str(e)}')
        return jsonify({
            'success': False,
            'error': '更新头像失败，请稍后重试'
        }), 500

@auth_bp.route('/update-nickname', methods=['POST'])
def update_nickname():
    """更新用户昵称"""
    current_time = LogService.get_current_time()
    function_name = 'update_nickname'
    model_name = 'Auth'
    
    try:
        token = request.headers.get('Authorization', '').replace('Bearer ', '')
        
        if not token:
            return jsonify({
                'success': False,
                'error': '缺少认证令牌'
            }), 401
        
        data = request.json
        nickname = data.get('nickname', '').strip()
        
        if not nickname:
            return jsonify({
                'success': False,
                'error': '昵称不能为空'
            }), 400
        
        if len(nickname) < 1 or len(nickname) > 20:
            return jsonify({
                'success': False,
                'error': '昵称长度应在1-20个字符之间'
            }), 400
        
        user_service = get_user_service()
        result = user_service.update_user_nickname(token, nickname)
        
        if result['success']:
            LogService.log(current_time=current_time, model_name=model_name, function_name=function_name, 
                         log_level='Info', message=f'用户昵称更新成功: {nickname}')
        else:
            LogService.log(current_time=current_time, model_name=model_name, function_name=function_name, 
                         log_level='Warning', message=f'用户昵称更新失败: {result["error"]}')
        
        return jsonify(result)
        
    except Exception as e:
        LogService.log(current_time=current_time, model_name=model_name, function_name=function_name, 
                     log_level='Error', message=f'更新昵称异常: {str(e)}')
        return jsonify({
            'success': False,
            'error': '更新失败，请稍后重试'
        }), 500

@auth_bp.route('/update-email', methods=['POST'])
def update_email():
    """更新用户邮箱"""
    current_time = LogService.get_current_time()
    function_name = 'update_email'
    model_name = 'Auth'
    
    try:
        token = request.headers.get('Authorization', '').replace('Bearer ', '')
        
        if not token:
            return jsonify({
                'success': False,
                'error': '缺少认证令牌'
            }), 401
        
        data = request.json
        email = data.get('email', '').strip()
        
        if not email:
            return jsonify({
                'success': False,
                'error': '邮箱不能为空'
            }), 400
        
        # 简单的邮箱格式验证
        import re
        email_pattern = r'^[^\s@]+@[^\s@]+\.[^\s@]+$'
        if not re.match(email_pattern, email):
            return jsonify({
                'success': False,
                'error': '邮箱格式不正确'
            }), 400
        
        user_service = get_user_service()
        result = user_service.update_user_email(token, email)
        
        if result['success']:
            LogService.log(current_time=current_time, model_name=model_name, function_name=function_name, 
                         log_level='Info', message=f'用户邮箱更新成功: {email}')
        else:
            LogService.log(current_time=current_time, model_name=model_name, function_name=function_name, 
                         log_level='Warning', message=f'用户邮箱更新失败: {result["error"]}')
        
        return jsonify(result)
        
    except Exception as e:
        LogService.log(current_time=current_time, model_name=model_name, function_name=function_name, 
                     log_level='Error', message=f'更新邮箱异常: {str(e)}')
        return jsonify({
            'success': False,
            'error': '更新失败，请稍后重试'
        }), 500

@auth_bp.route('/generate-guest-avatar', methods=['POST'])
def generate_guest_avatar():
    """为游客生成头像"""
    current_time = LogService.get_current_time()
    function_name = 'generate_guest_avatar'
    model_name = 'Auth'
    
    try:
        data = request.json
        nickname = data.get('nickname', '').strip()
        guest_id = data.get('guest_id', '').strip()
        
        if not nickname or not guest_id:
            return jsonify({
                'success': False,
                'error': '昵称和游客ID不能为空'
            }), 400
        
        LogService.log(current_time=current_time, model_name=model_name, function_name=function_name, 
                     log_level='Info', message=f'为游客生成头像: {nickname}')
        
        # 生成头像（返回base64格式）
        avatar_data = create_user_avatar(nickname)
        
        LogService.log(current_time=current_time, model_name=model_name, function_name=function_name, 
                     log_level='Info', message=f'游客头像生成成功: {nickname}')
        
        return jsonify({
            'success': True,
            'avatar': avatar_data
        })
        
    except Exception as e:
        LogService.log(current_time=current_time, model_name=model_name, function_name=function_name, 
                     log_level='Error', message=f'生成游客头像异常: {str(e)}')
        return jsonify({
            'success': False,
            'error': '头像生成失败，请稍后重试'
        }), 500
