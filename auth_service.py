"""
用户认证服务模块
处理用户注册、登录、Token验证等功能
"""

import hashlib
import secrets
import json
import os
from datetime import datetime, timedelta
from functools import wraps
from flask import request, jsonify, current_app
import jwt
import re
from typing import Optional, Dict, Any

# 用户数据存储文件
USERS_DB_FILE = 'users_db.json'
TOKENS_DB_FILE = 'tokens_db.json'

class AuthService:
    """用户认证服务类"""
    
    def __init__(self, secret_key: str = None):
        """初始化认证服务"""
        self.secret_key = secret_key or os.environ.get('JWT_SECRET_KEY', 'your-secret-key-change-in-production')
        self.token_expiry_hours = 24
        self.refresh_token_expiry_days = 7
        
        # 初始化数据存储
        self._init_database()
    
    def _init_database(self):
        """初始化用户数据库文件"""
        if not os.path.exists(USERS_DB_FILE):
            with open(USERS_DB_FILE, 'w') as f:
                json.dump({}, f)
        
        if not os.path.exists(TOKENS_DB_FILE):
            with open(TOKENS_DB_FILE, 'w') as f:
                json.dump({}, f)
    
    def _load_users(self) -> Dict[str, Dict]:
        """加载用户数据"""
        try:
            with open(USERS_DB_FILE, 'r', encoding='utf-8') as f:
                return json.load(f)
        except Exception:
            return {}
    
    def _save_users(self, users: Dict[str, Dict]):
        """保存用户数据"""
        with open(USERS_DB_FILE, 'w', encoding='utf-8') as f:
            json.dump(users, f, indent=2, ensure_ascii=False)
    
    def _load_tokens(self) -> Dict[str, Dict]:
        """加载Token数据"""
        try:
            with open(TOKENS_DB_FILE, 'r', encoding='utf-8') as f:
                return json.load(f)
        except Exception:
            return {}
    
    def _save_tokens(self, tokens: Dict[str, Dict]):
        """保存Token数据"""
        with open(TOKENS_DB_FILE, 'w', encoding='utf-8') as f:
            json.dump(tokens, f, indent=2, ensure_ascii=False)
    
    def _hash_password(self, password: str, salt: str = None) -> tuple:
        """哈希密码"""
        if salt is None:
            salt = secrets.token_hex(32)
        
        # 使用PBKDF2算法
        password_hash = hashlib.pbkdf2_hmac(
            'sha256',
            password.encode('utf-8'),
            salt.encode('utf-8'),
            100000  # 迭代次数
        ).hex()
        
        return password_hash, salt
    
    def _verify_password(self, password: str, password_hash: str, salt: str) -> bool:
        """验证密码"""
        computed_hash, _ = self._hash_password(password, salt)
        return computed_hash == password_hash
    
    def _validate_email(self, email: str) -> bool:
        """验证邮箱格式"""
        pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
        return re.match(pattern, email) is not None
    
    def _validate_username(self, username: str) -> bool:
        """验证用户名格式"""
        # 用户名: 3-20字符，只能包含字母、数字、下划线、中文
        pattern = r'^[\u4e00-\u9fa5a-zA-Z0-9_]{2,20}$'
        return re.match(pattern, username) is not None
    
    def _validate_password_strength(self, password: str) -> tuple:
        """验证密码强度"""
        if len(password) < 8:
            return False, "密码长度至少为8位"
        
        strength = 0
        if re.search(r'[a-z]', password):
            strength += 1
        if re.search(r'[A-Z]', password):
            strength += 1
        if re.search(r'[0-9]', password):
            strength += 1
        if re.search(r'[!@#$%^&*(),.?":{}|<>]', password):
            strength += 1
        
        if strength < 2:
            return False, "密码强度太弱，请包含大小写字母、数字或特殊字符"
        
        return True, "密码强度符合要求"
    
    def generate_token(self, user_id: str, username: str) -> Dict[str, str]:
        """生成JWT Token"""
        # Access Token
        access_payload = {
            'user_id': user_id,
            'username': username,
            'exp': datetime.utcnow() + timedelta(hours=self.token_expiry_hours),
            'iat': datetime.utcnow(),
            'type': 'access'
        }
        access_token = jwt.encode(access_payload, self.secret_key, algorithm='HS256')
        
        # Refresh Token
        refresh_payload = {
            'user_id': user_id,
            'exp': datetime.utcnow() + timedelta(days=self.refresh_token_expiry_days),
            'iat': datetime.utcnow(),
            'type': 'refresh'
        }
        refresh_token = jwt.encode(refresh_payload, self.secret_key, algorithm='HS256')
        
        # 保存Token记录
        tokens = self._load_tokens()
        tokens[user_id] = {
            'access_token': access_token,
            'refresh_token': refresh_token,
            'created_at': datetime.utcnow().isoformat(),
            'expires_at': (datetime.utcnow() + timedelta(hours=self.token_expiry_hours)).isoformat()
        }
        self._save_tokens(tokens)
        
        return {
            'access_token': access_token,
            'refresh_token': refresh_token,
            'expires_in': self.token_expiry_hours * 3600
        }
    
    def verify_token(self, token: str) -> Optional[Dict]:
        """验证JWT Token"""
        try:
            payload = jwt.decode(token, self.secret_key, algorithms=['HS256'])
            return payload
        except jwt.ExpiredSignatureError:
            return None
        except jwt.InvalidTokenError:
            return None
    
    def register(self, username: str, email: str, password: str) -> Dict[str, Any]:
        """用户注册"""
        # 验证输入
        if not self._validate_username(username):
            return {'success': False, 'message': '用户名格式不正确，只能包含字母、数字、下划线和中文，长度2-20'}
        
        if not self._validate_email(email):
            return {'success': False, 'message': '邮箱格式不正确'}
        
        valid, msg = self._validate_password_strength(password)
        if not valid:
            return {'success': False, 'message': msg}
        
        # 检查用户是否已存在
        users = self._load_users()
        
        # 检查用户名
        for user_id, user_data in users.items():
            if user_data['username'].lower() == username.lower():
                return {'success': False, 'message': '用户名已存在'}
            if user_data['email'].lower() == email.lower():
                return {'success': False, 'message': '邮箱已被注册'}
        
        # 创建新用户
        user_id = secrets.token_urlsafe(16)
        password_hash, salt = self._hash_password(password)
        
        new_user = {
            'user_id': user_id,
            'username': username,
            'email': email,
            'password_hash': password_hash,
            'salt': salt,
            'created_at': datetime.utcnow().isoformat(),
            'last_login': None,
            'is_active': True,
            'profile': {
                'avatar': None,
                'nickname': username,
                'bio': '',
                'preferences': {
                    'theme': 'light',
                    'language': 'zh-CN',
                    'favorite_characters': []
                }
            },
            'statistics': {
                'total_conversations': 0,
                'total_messages': 0,
                'favorite_character': None,
                'join_days': 0
            }
        }
        
        users[user_id] = new_user
        self._save_users(users)
        
        return {
            'success': True,
            'message': '注册成功',
            'user_id': user_id
        }
    
    def login(self, username_or_email: str, password: str, remember_me: bool = False) -> Dict[str, Any]:
        """用户登录"""
        users = self._load_users()
        
        # 查找用户
        user = None
        for user_id, user_data in users.items():
            if (user_data['username'].lower() == username_or_email.lower() or 
                user_data['email'].lower() == username_or_email.lower()):
                user = user_data
                user['user_id'] = user_id
                break
        
        if not user:
            return {'success': False, 'message': '用户名或密码错误'}
        
        # 验证密码
        if not self._verify_password(password, user['password_hash'], user['salt']):
            return {'success': False, 'message': '用户名或密码错误'}
        
        # 检查账户状态
        if not user.get('is_active', True):
            return {'success': False, 'message': '账户已被禁用'}
        
        # 更新最后登录时间
        user['last_login'] = datetime.utcnow().isoformat()
        users[user['user_id']] = user
        self._save_users(users)
        
        # 生成Token
        if remember_me:
            self.token_expiry_hours = 24 * 7  # 7天
        
        tokens = self.generate_token(user['user_id'], user['username'])
        
        return {
            'success': True,
            'message': '登录成功',
            'user': {
                'user_id': user['user_id'],
                'username': user['username'],
                'email': user['email'],
                'nickname': user['profile']['nickname'],
                'avatar': user['profile']['avatar']
            },
            'tokens': tokens
        }
    
    def logout(self, user_id: str) -> Dict[str, Any]:
        """用户登出"""
        tokens = self._load_tokens()
        if user_id in tokens:
            del tokens[user_id]
            self._save_tokens(tokens)
        
        return {'success': True, 'message': '登出成功'}
    
    def refresh_token(self, refresh_token: str) -> Dict[str, Any]:
        """刷新Token"""
        payload = self.verify_token(refresh_token)
        
        if not payload or payload.get('type') != 'refresh':
            return {'success': False, 'message': '无效的Refresh Token'}
        
        users = self._load_users()
        user_id = payload['user_id']
        
        if user_id not in users:
            return {'success': False, 'message': '用户不存在'}
        
        user = users[user_id]
        tokens = self.generate_token(user_id, user['username'])
        
        return {
            'success': True,
            'message': 'Token刷新成功',
            'tokens': tokens
        }
    
    def get_user_profile(self, user_id: str) -> Optional[Dict]:
        """获取用户资料"""
        users = self._load_users()
        
        if user_id not in users:
            return None
        
        user = users[user_id]
        return {
            'user_id': user_id,
            'username': user['username'],
            'email': user['email'],
            'created_at': user['created_at'],
            'profile': user['profile'],
            'statistics': user['statistics']
        }
    
    def update_user_profile(self, user_id: str, updates: Dict) -> Dict[str, Any]:
        """更新用户资料"""
        users = self._load_users()
        
        if user_id not in users:
            return {'success': False, 'message': '用户不存在'}
        
        user = users[user_id]
        
        # 更新允许的字段
        allowed_fields = ['nickname', 'bio', 'avatar']
        for field in allowed_fields:
            if field in updates:
                user['profile'][field] = updates[field]
        
        # 更新偏好设置
        if 'preferences' in updates:
            user['profile']['preferences'].update(updates['preferences'])
        
        users[user_id] = user
        self._save_users(users)
        
        return {'success': True, 'message': '资料更新成功'}
    
    def change_password(self, user_id: str, old_password: str, new_password: str) -> Dict[str, Any]:
        """修改密码"""
        users = self._load_users()
        
        if user_id not in users:
            return {'success': False, 'message': '用户不存在'}
        
        user = users[user_id]
        
        # 验证旧密码
        if not self._verify_password(old_password, user['password_hash'], user['salt']):
            return {'success': False, 'message': '原密码错误'}
        
        # 验证新密码强度
        valid, msg = self._validate_password_strength(new_password)
        if not valid:
            return {'success': False, 'message': msg}
        
        # 更新密码
        password_hash, salt = self._hash_password(new_password)
        user['password_hash'] = password_hash
        user['salt'] = salt
        
        users[user_id] = user
        self._save_users(users)
        
        # 清除所有Token
        tokens = self._load_tokens()
        if user_id in tokens:
            del tokens[user_id]
            self._save_tokens(tokens)
        
        return {'success': True, 'message': '密码修改成功，请重新登录'}
    
    def reset_password(self, email: str) -> Dict[str, Any]:
        """重置密码（发送重置链接）"""
        users = self._load_users()
        
        # 查找用户
        user = None
        for user_id, user_data in users.items():
            if user_data['email'].lower() == email.lower():
                user = user_data
                user['user_id'] = user_id
                break
        
        if not user:
            # 出于安全考虑，即使邮箱不存在也返回成功
            return {'success': True, 'message': '如果该邮箱已注册，重置链接将发送到您的邮箱'}
        
        # 生成重置Token
        reset_token = secrets.token_urlsafe(32)
        reset_payload = {
            'user_id': user['user_id'],
            'email': email,
            'token': reset_token,
            'exp': datetime.utcnow() + timedelta(hours=1),
            'type': 'password_reset'
        }
        
        # 这里应该发送邮件
        # send_reset_email(email, reset_token)
        
        return {'success': True, 'message': '如果该邮箱已注册，重置链接将发送到您的邮箱'}


# 装饰器：验证Token
def token_required(f):
    """Token验证装饰器"""
    @wraps(f)
    def decorated(*args, **kwargs):
        token = None
        auth_header = request.headers.get('Authorization')
        
        if auth_header:
            try:
                token = auth_header.split(' ')[1]  # Bearer <token>
            except IndexError:
                return jsonify({'success': False, 'message': '无效的Token格式'}), 401
        
        if not token:
            return jsonify({'success': False, 'message': '缺少认证Token'}), 401
        
        auth_service = AuthService()
        payload = auth_service.verify_token(token)
        
        if not payload:
            return jsonify({'success': False, 'message': 'Token已过期或无效'}), 401
        
        # 将用户信息添加到请求上下文
        request.current_user = {
            'user_id': payload['user_id'],
            'username': payload.get('username')
        }
        
        return f(*args, **kwargs)
    
    return decorated


# 初始化认证服务实例
auth_service = AuthService()