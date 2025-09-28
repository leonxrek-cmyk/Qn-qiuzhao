"""
亲密度相关的路由处理
"""
from flask import Blueprint, request, jsonify
from services.intimacy_service import IntimacyService
from services.log_service import LogService
from services.user_service import UserService

# 创建蓝图
intimacy_bp = Blueprint('intimacy', __name__)

@intimacy_bp.route('/intimacy/<character_id>', methods=['GET'])
def get_intimacy(character_id):
    """获取用户与指定角色的亲密度"""
    current_time = LogService.get_current_time()
    function_name = 'get_intimacy'
    
    try:
        # 获取用户ID
        session_token = request.headers.get('Authorization', '').replace('Bearer ', '')
        if not session_token:
            return jsonify({
                'success': False,
                'error': '未提供认证令牌'
            }), 401
        
        user_service = UserService()
        user_id = user_service.get_user_id_by_session(session_token)
        
        if not user_id:
            return jsonify({
                'success': False,
                'error': '无效的认证令牌'
            }), 401
        
        intimacy_service = IntimacyService()
        intimacy = intimacy_service.get_intimacy(user_id, character_id)
        level_progress = intimacy_service.get_level_progress(intimacy)
        
        LogService.log(
            current_time=current_time,
            model_name='IntimacyAPI',
            function_name=function_name,
            log_level='Info',
            message=f'获取亲密度成功: 用户 {user_id}, 角色 {character_id}, 亲密度 {intimacy}'
        )
        
        return jsonify({
            'success': True,
            'intimacy': intimacy,
            'level_progress': level_progress
        })
        
    except Exception as e:
        LogService.log(
            current_time=current_time,
            model_name='IntimacyAPI',
            function_name=function_name,
            log_level='Error',
            message=f'获取亲密度失败: {str(e)}'
        )
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@intimacy_bp.route('/intimacy/<character_id>/increase', methods=['POST'])
def increase_intimacy(character_id):
    """增加用户与指定角色的亲密度"""
    current_time = LogService.get_current_time()
    function_name = 'increase_intimacy'
    
    try:
        # 获取用户ID
        session_token = request.headers.get('Authorization', '').replace('Bearer ', '')
        if not session_token:
            return jsonify({
                'success': False,
                'error': '未提供认证令牌'
            }), 401
        
        user_service = UserService()
        user_id = user_service.get_user_id_by_session(session_token)
        
        if not user_id:
            return jsonify({
                'success': False,
                'error': '无效的认证令牌'
            }), 401
        
        intimacy_service = IntimacyService()
        result = intimacy_service.increase_intimacy(user_id, character_id)
        
        if result['success']:
            level_progress = intimacy_service.get_level_progress(result['intimacy'])
            result['level_progress'] = level_progress
            
            LogService.log(
                current_time=current_time,
                model_name='IntimacyAPI',
                function_name=function_name,
                log_level='Info',
                message=f'增加亲密度成功: 用户 {user_id}, 角色 {character_id}, 新亲密度 {result["intimacy"]}'
            )
        
        return jsonify(result)
        
    except Exception as e:
        LogService.log(
            current_time=current_time,
            model_name='IntimacyAPI',
            function_name=function_name,
            log_level='Error',
            message=f'增加亲密度失败: {str(e)}'
        )
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@intimacy_bp.route('/intimacy/all', methods=['GET'])
def get_all_intimacy():
    """获取用户所有角色的亲密度"""
    current_time = LogService.get_current_time()
    function_name = 'get_all_intimacy'
    
    try:
        # 获取用户ID
        session_token = request.headers.get('Authorization', '').replace('Bearer ', '')
        if not session_token:
            return jsonify({
                'success': False,
                'error': '未提供认证令牌'
            }), 401
        
        user_service = UserService()
        user_id = user_service.get_user_id_by_session(session_token)
        
        if not user_id:
            return jsonify({
                'success': False,
                'error': '无效的认证令牌'
            }), 401
        
        intimacy_service = IntimacyService()
        all_intimacy = intimacy_service.get_all_intimacy(user_id)
        
        # 为每个角色添加等级进度信息
        result = {}
        for character_id, intimacy in all_intimacy.items():
            level_progress = intimacy_service.get_level_progress(intimacy)
            result[character_id] = {
                'intimacy': intimacy,
                'level_progress': level_progress
            }
        
        LogService.log(
            current_time=current_time,
            model_name='IntimacyAPI',
            function_name=function_name,
            log_level='Info',
            message=f'获取所有亲密度成功: 用户 {user_id}, 角色数量 {len(result)}'
        )
        
        return jsonify({
            'success': True,
            'intimacy_data': result
        })
        
    except Exception as e:
        LogService.log(
            current_time=current_time,
            model_name='IntimacyAPI',
            function_name=function_name,
            log_level='Error',
            message=f'获取所有亲密度失败: {str(e)}'
        )
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500
