"""
会话管理相关的路由处理
"""
from flask import Blueprint, request, jsonify
import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from services.log_service import LogService
from services.session_service import SessionService
from services.user_service import get_user_service

# 创建蓝图
session_bp = Blueprint('session', __name__)

@session_bp.route('/sessions', methods=['POST'])
def create_session():
    """创建新的会话"""
    current_time = LogService.get_current_time()
    function_name = 'create_session'
    model_name = 'API'
    
    try:
        data = request.json or {}
        character_id = data.get('character_id')
        user_id = data.get('user_id', 'anonymous')
        
        # 获取用户认证信息
        token = request.headers.get('Authorization', '').replace('Bearer ', '')
        user_token = None
        
        if token:
            user_service = get_user_service()
            user = user_service.get_user_by_token(token)
            if user:
                user_id = user['id']
                user_token = token
        
        LogService.log(current_time=current_time, model_name=model_name, function_name=function_name, 
                     log_level='Info', message=f'创建新会话请求, 角色ID: {character_id}, 用户ID: {user_id}')
        
        session_service = SessionService()
        session_id = session_service.create_session(character_id, user_id, user_token)
        
        # 如果是认证用户，将会话添加到用户历史
        if user_token:
            user_service.add_chat_session(user_token, character_id, session_id)
        
        LogService.log(current_time=current_time, model_name=model_name, function_name=function_name, 
                     log_level='Info', message=f'会话创建成功: {session_id}')
        
        return jsonify({
            'success': True,
            'session_id': session_id
        })
    except Exception as e:
        LogService.log(current_time=current_time, model_name=model_name, function_name=function_name, 
                     log_level='Error', message=f'创建会话失败: {str(e)}')
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@session_bp.route('/sessions/<session_id>', methods=['GET'])
def get_session(session_id):
    """获取会话信息"""
    current_time = LogService.get_current_time()
    function_name = 'get_session'
    model_name = 'API'
    
    try:
        LogService.log(current_time=current_time, model_name=model_name, function_name=function_name, 
                     log_level='Info', message=f'获取会话信息: {session_id}')
        
        session_service = SessionService()
        session = session_service.get_session(session_id)
        if not session:
            return jsonify({
                'success': False,
                'error': '会话不存在或已过期'
            }), 404
        
        return jsonify({
            'success': True,
            'session': session
        })
    except Exception as e:
        LogService.log(current_time=current_time, model_name=model_name, function_name=function_name, 
                     log_level='Error', message=f'获取会话信息失败: {str(e)}')
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@session_bp.route('/sessions/<session_id>/messages', methods=['GET'])
def get_session_messages(session_id):
    """获取会话消息历史"""
    current_time = LogService.get_current_time()
    function_name = 'get_session_messages'
    model_name = 'API'
    
    try:
        LogService.log(current_time=current_time, model_name=model_name, function_name=function_name, 
                     log_level='Info', message=f'获取会话消息: {session_id}')
        
        session_service = SessionService()
        messages = session_service.get_messages(session_id)
        
        return jsonify({
            'success': True,
            'messages': messages
        })
    except Exception as e:
        LogService.log(current_time=current_time, model_name=model_name, function_name=function_name, 
                     log_level='Error', message=f'获取会话消息失败: {str(e)}')
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@session_bp.route('/sessions/<session_id>/clear', methods=['POST'])
def clear_session(session_id):
    """清空会话消息"""
    current_time = LogService.get_current_time()
    function_name = 'clear_session'
    model_name = 'API'
    
    try:
        LogService.log(current_time=current_time, model_name=model_name, function_name=function_name, 
                     log_level='Info', message=f'清空会话消息: {session_id}')
        
        session_service = SessionService()
        success = session_service.clear_session(session_id)
        if not success:
            return jsonify({
                'success': False,
                'error': '会话不存在或已过期'
            }), 404
        
        return jsonify({
            'success': True,
            'message': '会话已清空'
        })
    except Exception as e:
        LogService.log(current_time=current_time, model_name=model_name, function_name=function_name, 
                     log_level='Error', message=f'清空会话失败: {str(e)}')
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@session_bp.route('/user_sessions', methods=['GET'])
def get_user_sessions():
    """获取用户的会话历史"""
    current_time = LogService.get_current_time()
    function_name = 'get_user_sessions'
    model_name = 'API'
    
    try:
        # 获取用户认证信息
        token = request.headers.get('Authorization', '').replace('Bearer ', '')
        
        if not token:
            return jsonify({
                'success': False,
                'error': '需要用户认证'
            }), 401
        
        user_service = get_user_service()
        user = user_service.get_user_by_token(token)
        
        if not user:
            return jsonify({
                'success': False,
                'error': '无效的认证令牌'
            }), 401
        
        character_id = request.args.get('character_id')
        
        LogService.log(current_time=current_time, model_name=model_name, function_name=function_name, 
                     log_level='Info', message=f'获取用户会话历史, 用户ID: {user["id"]}, 角色ID: {character_id}')
        
        session_service = SessionService()
        sessions = session_service.get_user_sessions(token, character_id)
        
        return jsonify({
            'success': True,
            'sessions': sessions
        })
        
    except Exception as e:
        LogService.log(current_time=current_time, model_name=model_name, function_name=function_name, 
                     log_level='Error', message=f'获取用户会话历史失败: {str(e)}')
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@session_bp.route('/latest_session/<character_id>', methods=['GET'])
def get_latest_session(character_id):
    """获取用户与特定角色的最新会话"""
    current_time = LogService.get_current_time()
    function_name = 'get_latest_session'
    model_name = 'API'
    
    try:
        # 获取用户认证信息
        token = request.headers.get('Authorization', '').replace('Bearer ', '')
        
        if not token:
            return jsonify({
                'success': False,
                'error': '需要用户认证'
            }), 401
        
        user_service = get_user_service()
        user = user_service.get_user_by_token(token)
        
        if not user:
            return jsonify({
                'success': False,
                'error': '无效的认证令牌'
            }), 401
        
        LogService.log(current_time=current_time, model_name=model_name, function_name=function_name, 
                     log_level='Info', message=f'获取最新会话, 用户ID: {user["id"]}, 角色ID: {character_id}')
        
        session_service = SessionService()
        session_id = session_service.get_latest_user_session(token, character_id)
        
        if session_id:
            return jsonify({
                'success': True,
                'session_id': session_id
            })
        else:
            return jsonify({
                'success': False,
                'error': '没有找到会话'
            }), 404
        
    except Exception as e:
        LogService.log(current_time=current_time, model_name=model_name, function_name=function_name, 
                     log_level='Error', message=f'获取最新会话失败: {str(e)}')
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@session_bp.route('/delete_session/<character_id>/<session_id>', methods=['DELETE'])
def delete_session(character_id, session_id):
    """删除指定的会话"""
    current_time = LogService.get_current_time()
    function_name = 'delete_session'
    model_name = 'API'
    
    try:
        # 获取用户认证信息
        token = request.headers.get('Authorization', '').replace('Bearer ', '')
        
        if not token:
            return jsonify({
                'success': False,
                'error': '需要用户认证'
            }), 401
        
        user_service = get_user_service()
        user = user_service.get_user_by_token(token)
        
        if not user:
            return jsonify({
                'success': False,
                'error': '无效的认证令牌'
            }), 401
        
        LogService.log(current_time=current_time, model_name=model_name, function_name=function_name, 
                     log_level='Info', message=f'删除会话, 用户ID: {user["id"]}, 角色ID: {character_id}, 会话ID: {session_id}')
        
        # 删除会话
        session_service = SessionService()
        success = session_service.delete_session(session_id)
        
        if success:
            # 从用户历史中移除
            user_service.remove_chat_session(token, character_id, session_id)
            
            return jsonify({
                'success': True,
                'message': '会话已删除'
            })
        else:
            return jsonify({
                'success': False,
                'error': '会话不存在或删除失败'
            }), 404
        
    except Exception as e:
        LogService.log(current_time=current_time, model_name=model_name, function_name=function_name, 
                     log_level='Error', message=f'删除会话失败: {str(e)}')
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@session_bp.route('/clear_all_history', methods=['DELETE'])
def clear_all_history():
    """清空用户的所有历史记录"""
    current_time = LogService.get_current_time()
    function_name = 'clear_all_history'
    model_name = 'API'
    
    try:
        # 获取用户认证信息
        token = request.headers.get('Authorization', '').replace('Bearer ', '')
        
        if not token:
            return jsonify({
                'success': False,
                'error': '需要用户认证'
            }), 401
        
        user_service = get_user_service()
        user = user_service.get_user_by_token(token)
        
        if not user:
            return jsonify({
                'success': False,
                'error': '无效的认证令牌'
            }), 401
        
        LogService.log(current_time=current_time, model_name=model_name, function_name=function_name, 
                     log_level='Info', message=f'清空所有历史记录, 用户ID: {user["id"]}')
        
        # 清空用户的所有会话历史
        session_service = SessionService()
        success = session_service.clear_all_user_sessions(token)
        
        if success:
            # 清空用户历史记录
            user_service.clear_all_chat_history(token)
            
            return jsonify({
                'success': True,
                'message': '所有历史记录已清空'
            })
        else:
            return jsonify({
                'success': False,
                'error': '清空历史记录失败'
            }), 500
        
    except Exception as e:
        LogService.log(current_time=current_time, model_name=model_name, function_name=function_name, 
                     log_level='Error', message=f'清空所有历史记录失败: {str(e)}')
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500
