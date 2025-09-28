"""
亲密度服务
"""
import json
import os
from typing import Dict, Optional
from services.log_service import LogService

class IntimacyService:
    """亲密度管理服务"""
    
    # 亲密度等级配置
    INTIMACY_LEVELS = {
        1: "初次相识",
        5: "聊得火热", 
        10: "相见恨晚",
        20: "亲密无间",
        50: "知音难觅",
        100: "伯乐"
    }
    
    def __init__(self):
        self.users_file = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), 'data', 'users.json')
    
    def _load_users(self) -> Dict:
        """加载用户数据"""
        try:
            with open(self.users_file, 'r', encoding='utf-8') as f:
                return json.load(f)
        except Exception as e:
            LogService.log(
                current_time=LogService.get_current_time(),
                model_name='IntimacyService',
                function_name='_load_users',
                log_level='Error',
                message=f'加载用户数据失败: {str(e)}'
            )
            return {}
    
    def _save_users(self, users_data: Dict) -> bool:
        """保存用户数据"""
        try:
            with open(self.users_file, 'w', encoding='utf-8') as f:
                json.dump(users_data, f, ensure_ascii=False, indent=2)
            return True
        except Exception as e:
            LogService.log(
                current_time=LogService.get_current_time(),
                model_name='IntimacyService',
                function_name='_save_users',
                log_level='Error',
                message=f'保存用户数据失败: {str(e)}'
            )
            return False
    
    def get_intimacy(self, user_id: str, character_id: str) -> int:
        """获取用户与角色的亲密度"""
        users_data = self._load_users()
        
        # 查找用户
        user = None
        for username, user_data in users_data.get('users', {}).items():
            if user_data.get('id') == user_id:
                user = user_data
                break
        
        if not user:
            return 0
        
        intimacy_data = user.get('intimacy', {})
        return intimacy_data.get(character_id, 0)
    
    def increase_intimacy(self, user_id: str, character_id: str) -> Dict:
        """增加亲密度"""
        users_data = self._load_users()
        
        # 查找用户
        user = None
        username = None
        for uname, user_data in users_data.get('users', {}).items():
            if user_data.get('id') == user_id:
                user = user_data
                username = uname
                break
        
        if not user:
            return {'success': False, 'error': '用户不存在'}
        
        # 初始化亲密度数据
        if 'intimacy' not in user:
            user['intimacy'] = {}
        
        # 获取当前亲密度
        current_intimacy = user['intimacy'].get(character_id, 0)
        new_intimacy = current_intimacy + 1
        
        # 更新亲密度
        user['intimacy'][character_id] = new_intimacy
        
        # 保存数据
        if not self._save_users(users_data):
            return {'success': False, 'error': '保存失败'}
        
        # 检查是否达到新等级
        old_level = self.get_level_name(current_intimacy)
        new_level = self.get_level_name(new_intimacy)
        level_up = old_level != new_level
        
        LogService.log(
            current_time=LogService.get_current_time(),
            model_name='IntimacyService',
            function_name='increase_intimacy',
            log_level='Info',
            message=f'用户 {user_id} 与角色 {character_id} 亲密度增加: {current_intimacy} -> {new_intimacy}'
        )
        
        return {
            'success': True,
            'intimacy': new_intimacy,
            'level_name': new_level,
            'level_up': level_up,
            'old_level': old_level
        }
    
    def get_level_name(self, intimacy: int) -> str:
        """根据亲密度获取等级名称"""
        if intimacy == 0:
            return "陌生人"
        
        # 找到对应的等级
        for threshold in sorted(self.INTIMACY_LEVELS.keys(), reverse=True):
            if intimacy >= threshold:
                return self.INTIMACY_LEVELS[threshold]
        
        return "初次相识"
    
    def get_level_progress(self, intimacy: int) -> Dict:
        """获取等级进度信息"""
        if intimacy == 0:
            return {
                'current_level': "陌生人",
                'next_level': "初次相识",
                'current_threshold': 0,
                'next_threshold': 1,
                'progress': 0
            }
        
        # 找到当前等级和下一等级
        current_threshold = 0
        next_threshold = None
        current_level = "初次相识"
        next_level = None
        
        thresholds = sorted(self.INTIMACY_LEVELS.keys())
        
        for i, threshold in enumerate(thresholds):
            if intimacy >= threshold:
                current_threshold = threshold
                current_level = self.INTIMACY_LEVELS[threshold]
                if i + 1 < len(thresholds):
                    next_threshold = thresholds[i + 1]
                    next_level = self.INTIMACY_LEVELS[next_threshold]
        
        # 如果已经是最高等级
        if next_threshold is None:
            return {
                'current_level': current_level,
                'next_level': None,
                'current_threshold': current_threshold,
                'next_threshold': None,
                'progress': 100
            }
        
        # 计算进度百分比
        progress_range = next_threshold - current_threshold
        current_progress = intimacy - current_threshold
        progress_percent = (current_progress / progress_range) * 100
        
        return {
            'current_level': current_level,
            'next_level': next_level,
            'current_threshold': current_threshold,
            'next_threshold': next_threshold,
            'progress': progress_percent
        }
    
    def get_all_intimacy(self, user_id: str) -> Dict:
        """获取用户所有角色的亲密度"""
        users_data = self._load_users()
        
        # 查找用户
        user = None
        for username, user_data in users_data.get('users', {}).items():
            if user_data.get('id') == user_id:
                user = user_data
                break
        
        if not user:
            return {}
        
        return user.get('intimacy', {})
