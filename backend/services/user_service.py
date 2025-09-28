"""
用户管理服务
"""
import uuid
import hashlib
import datetime
import json
import os
from typing import Dict, List, Any, Optional

class UserService:
    def __init__(self):
        self.users: Dict[str, Dict[str, Any]] = {}
        self.user_sessions: Dict[str, str] = {}  # session_token -> user_id
        self.data_file = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'data', 'users.json')
        self.load_users()
        self.ensure_admin_user()  # 确保管理员账户存在

    def load_users(self):
        """从文件加载用户数据"""
        try:
            if os.path.exists(self.data_file):
                with open(self.data_file, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                    self.users = data.get('users', {})
                    self.user_sessions = data.get('user_sessions', {})
        except Exception as e:
            print(f"加载用户数据失败: {str(e)}")
            self.users = {}
            self.user_sessions = {}

    def save_users(self):
        """保存用户数据到文件"""
        try:
            data = {
                'users': self.users,
                'user_sessions': self.user_sessions
            }
            with open(self.data_file, 'w', encoding='utf-8') as f:
                json.dump(data, f, ensure_ascii=False, indent=2)
        except Exception as e:
            print(f"保存用户数据失败: {str(e)}")

    def _hash_password(self, password: str) -> str:
        """密码哈希"""
        return hashlib.sha256(password.encode()).hexdigest()

    def _generate_token(self) -> str:
        """生成会话令牌"""
        return str(uuid.uuid4())

    def ensure_admin_user(self):
        """确保管理员账户存在"""
        admin_username = 'admin'
        admin_password = '123'
        
        if admin_username not in self.users:
            # 创建管理员账户
            user_id = str(uuid.uuid4())
            self.users[admin_username] = {
                'id': user_id,
                'username': admin_username,
                'password': self._hash_password(admin_password),
                'email': 'admin@system.local',
                'nickname': '系统管理员',
                'avatar': None,
                'is_admin': True,
                'created_at': datetime.datetime.now().isoformat(),
                'chat_history': {},
                'settings': {
                    'theme': 'light',
                    'language': 'zh-CN',
                    'notifications': True,
                    'auto_play_voice': False
                }
            }
            self.save_users()
            print(f"管理员账户已创建: {admin_username}")
        
        # 确保测试用户存在
        test_username = '123'
        test_password = '123456'
        
        if test_username not in self.users:
            # 创建测试用户
            user_id = str(uuid.uuid4())
            self.users[test_username] = {
                'id': user_id,
                'username': test_username,
                'password': self._hash_password(test_password),
                'email': 'test@example.com',
                'nickname': '测试用户',
                'avatar': None,
                'is_admin': False,
                'created_at': datetime.datetime.now().isoformat(),
                'chat_history': {},
                'settings': {
                    'theme': 'light',
                    'language': 'zh-CN',
                    'notifications': True,
                    'auto_play_voice': False
                }
            }
            self.save_users()
            print(f"测试用户已创建: {test_username}")

    def is_admin_user(self, token: str) -> bool:
        """检查用户是否为管理员"""
        if token not in self.user_sessions:
            return False
        
        user_id = self.user_sessions[token]
        for username, user_data in self.users.items():
            if user_data['id'] == user_id:
                return user_data.get('is_admin', False)
        return False

    def get_all_users(self, token: str) -> Dict[str, Any]:
        """获取所有用户（仅管理员）"""
        if not self.is_admin_user(token):
            return {'success': False, 'error': '权限不足'}
        
        users_list = []
        for username, user_data in self.users.items():
            users_list.append({
                'id': user_data['id'],
                'username': username,
                'email': user_data.get('email', ''),
                'nickname': user_data.get('nickname', username),
                'avatar': user_data.get('avatar'),
                'is_admin': user_data.get('is_admin', False),
                'created_at': user_data.get('created_at'),
                'chat_sessions': len(user_data.get('chat_history', {}))
            })
        
        return {
            'success': True,
            'users': users_list,
            'total': len(users_list)
        }

    def register_user(self, username: str, password: str, email: str = None) -> Dict[str, Any]:
        """用户注册"""
        if username in self.users:
            return {
                'success': False,
                'error': '用户名已存在'
            }

        user_id = str(uuid.uuid4())
        hashed_password = self._hash_password(password)
        
        user_data = {
            'id': user_id,
            'username': username,
            'password': hashed_password,
            'email': email,
            'avatar': '/user-avatar.svg',  # 默认头像
            'created_at': datetime.datetime.now().isoformat(),
            'last_login': None,
            'settings': {
                'theme': 'light',
                'language': 'zh-CN',
                'auto_play_voice': False,
                'default_model': 'deepseek-v3'
            },
            'chat_history': {}  # character_id -> [session_ids]
        }

        self.users[username] = user_data
        self.save_users()

        return {
            'success': True,
            'user_id': user_id,
            'message': '注册成功'
        }

    def login_user(self, username: str, password: str) -> Dict[str, Any]:
        """用户登录"""
        if username not in self.users:
            return {
                'success': False,
                'error': '用户名不存在'
            }

        user = self.users[username]
        hashed_password = self._hash_password(password)

        if user['password'] != hashed_password:
            return {
                'success': False,
                'error': '密码错误'
            }

        # 生成会话令牌
        token = self._generate_token()
        self.user_sessions[token] = user['id']

        # 更新最后登录时间
        user['last_login'] = datetime.datetime.now().isoformat()
        self.save_users()

        return {
            'success': True,
            'token': token,
            'user': {
                'id': user['id'],
                'username': user['username'],
                'email': user.get('email', ''),
                'nickname': user.get('nickname', user['username']),
                'avatar': user.get('avatar'),
                'is_admin': user.get('is_admin', False),
                'settings': user.get('settings', {
                    'theme': 'light',
                    'language': 'zh-CN',
                    'notifications': True,
                    'auto_play_voice': False
                })
            },
            'message': '登录成功'
        }

    def logout_user(self, token: str) -> Dict[str, Any]:
        """用户登出"""
        if token in self.user_sessions:
            del self.user_sessions[token]
            self.save_users()
            return {
                'success': True,
                'message': '登出成功'
            }
        return {
            'success': False,
            'error': '无效的会话令牌'
        }

    def get_user_by_token(self, token: str) -> Optional[Dict[str, Any]]:
        """通过令牌获取用户信息"""
        if token not in self.user_sessions:
            return None

        user_id = self.user_sessions[token]
        for username, user_data in self.users.items():
            if user_data['id'] == user_id:
                return {
                    'id': user_data['id'],
                    'username': user_data['username'],
                    'email': user_data.get('email', ''),
                    'nickname': user_data.get('nickname', user_data['username']),
                    'avatar': user_data.get('avatar'),
                    'is_admin': user_data.get('is_admin', False),
                    'settings': user_data.get('settings', {
                        'theme': 'light',
                        'language': 'zh-CN',
                        'notifications': True,
                        'auto_play_voice': False
                    })
                }
        return None

    def get_user_id_by_session(self, token: str) -> Optional[str]:
        """通过会话令牌获取用户ID"""
        return self.user_sessions.get(token)

    def update_user_settings(self, token: str, settings: Dict[str, Any]) -> Dict[str, Any]:
        """更新用户设置"""
        user = self.get_user_by_token(token)
        if not user:
            return {
                'success': False,
                'error': '无效的会话令牌'
            }

        user_id = self.user_sessions[token]
        for username, user_data in self.users.items():
            if user_data['id'] == user_id:
                user_data['settings'].update(settings)
                self.save_users()
                return {
                    'success': True,
                    'settings': user_data['settings'],
                    'message': '设置更新成功'
                }

        return {
            'success': False,
            'error': '用户不存在'
        }

    def add_chat_session(self, token: str, character_id: str, session_id: str) -> bool:
        """添加聊天会话到用户历史"""
        if token not in self.user_sessions:
            return False

        user_id = self.user_sessions[token]
        for username, user_data in self.users.items():
            if user_data['id'] == user_id:
                if character_id not in user_data['chat_history']:
                    user_data['chat_history'][character_id] = []
                
                # 避免重复添加
                if session_id not in user_data['chat_history'][character_id]:
                    user_data['chat_history'][character_id].append(session_id)
                    self.save_users()
                return True
        return False

    def get_user_chat_sessions(self, token: str, character_id: str) -> List[str]:
        """获取用户与特定角色的聊天会话列表"""
        if token not in self.user_sessions:
            return []

        user_id = self.user_sessions[token]
        for username, user_data in self.users.items():
            if user_data['id'] == user_id:
                return user_data['chat_history'].get(character_id, [])
        return []

    def remove_chat_session(self, token: str, character_id: str, session_id: str) -> bool:
        """从用户历史中移除指定的聊天会话"""
        if token not in self.user_sessions:
            return False

        user_id = self.user_sessions[token]
        for username, user_data in self.users.items():
            if user_data['id'] == user_id:
                if character_id in user_data['chat_history']:
                    if session_id in user_data['chat_history'][character_id]:
                        user_data['chat_history'][character_id].remove(session_id)
                        # 如果该角色的会话列表为空，删除该角色的记录
                        if not user_data['chat_history'][character_id]:
                            del user_data['chat_history'][character_id]
                        self.save_users()
                        return True
        return False

    def clear_all_chat_history(self, token: str) -> bool:
        """清空用户的所有聊天历史"""
        if token not in self.user_sessions:
            return False

        user_id = self.user_sessions[token]
        for username, user_data in self.users.items():
            if user_data['id'] == user_id:
                user_data['chat_history'] = {}
                self.save_users()
                return True
        return False

    def update_user_avatar(self, user_id_or_token: str, avatar_url: str) -> Dict[str, Any]:
        """更新用户头像（支持通过user_id或token）"""
        # 判断是token还是user_id
        if user_id_or_token in self.user_sessions:
            # 是token
            user_id = self.user_sessions[user_id_or_token]
        else:
            # 是user_id
            user_id = user_id_or_token

        for username, user_data in self.users.items():
            if user_data['id'] == user_id:
                user_data['avatar'] = avatar_url
                self.save_users()
                return {
                    'success': True,
                    'avatar': avatar_url,
                    'message': '头像更新成功'
                }

        return {
            'success': False,
            'error': '用户不存在'
        }

    def update_user_nickname(self, token: str, nickname: str) -> Dict[str, Any]:
        """更新用户昵称"""
        if token not in self.user_sessions:
            return {
                'success': False,
                'error': '无效的会话令牌'
            }

        user_id = self.user_sessions[token]
        for username, user_data in self.users.items():
            if user_data['id'] == user_id:
                # 更新昵称
                old_nickname = user_data.get('nickname', username)
                user_data['nickname'] = nickname
                
                # 重新生成头像（基于新昵称）
                try:
                    from routes.avatar_service import create_user_avatar
                    avatar_data = create_user_avatar(nickname)
                    user_data['avatar'] = avatar_data
                except Exception as e:
                    print(f"重新生成头像失败: {str(e)}")
                
                self.save_users()
                return {
                    'success': True,
                    'nickname': nickname,
                    'avatar': user_data.get('avatar'),
                    'message': '昵称更新成功'
                }

        return {
            'success': False,
            'error': '用户不存在'
        }

    def update_user_email(self, token: str, email: str) -> Dict[str, Any]:
        """更新用户邮箱"""
        if token not in self.user_sessions:
            return {'success': False, 'error': '无效的会话令牌'}
        
        # 检查邮箱是否已被其他用户使用
        for username, user_data in self.users.items():
            if user_data.get('email') == email and user_data['id'] != self.user_sessions[token]:
                return {'success': False, 'error': '该邮箱已被其他用户使用'}
        
        user_id = self.user_sessions[token]
        for username, user_data in self.users.items():
            if user_data['id'] == user_id:
                user_data['email'] = email
                self.save_users()
                return {
                    'success': True,
                    'email': email,
                    'message': '邮箱更新成功'
                }
                return {'success': False, 'error': '用户不存在'}

    def update_user_nickname_by_id(self, user_id: str, nickname: str) -> bool:
        """通过用户ID更新昵称"""
        for username, user_data in self.users.items():
            if user_data['id'] == user_id:
                user_data['nickname'] = nickname
                self.save_users()
                return True
        return False

    def update_user_email_by_id(self, user_id: str, email: str) -> bool:
        """通过用户ID更新邮箱"""
        for username, user_data in self.users.items():
            if user_data['id'] == user_id:
                user_data['email'] = email
                self.save_users()
                return True
        return False

    def set_admin_status(self, user_id: str, is_admin: bool) -> bool:
        """设置用户管理员状态"""
        for username, user_data in self.users.items():
            if user_data['id'] == user_id:
                user_data['is_admin'] = is_admin
                self.save_users()
                return True
        return False

    def delete_user(self, user_id: str) -> bool:
        """删除用户"""
        for username, user_data in list(self.users.items()):
            if user_data['id'] == user_id:
                # 不能删除管理员账户
                if user_data.get('is_admin', False) and username == 'admin':
                    return False
                
                # 删除用户会话
                sessions_to_remove = []
                for token, session_user_id in self.user_sessions.items():
                    if session_user_id == user_id:
                        sessions_to_remove.append(token)
                
                for token in sessions_to_remove:
                    del self.user_sessions[token]
                
                # 删除用户数据
                del self.users[username]
                self.save_users()
                return True
        return False

# 全局用户服务实例
_user_service_instance = None

def get_user_service() -> UserService:
    global _user_service_instance
    if _user_service_instance is None:
        _user_service_instance = UserService()
    return _user_service_instance
