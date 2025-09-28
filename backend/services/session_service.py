import json
import datetime
import uuid
from typing import Dict, List, Optional
from config import Config
import os

class SessionService:
    """会话管理服务，用于管理对话上下文和历史"""
    
    def __init__(self):
        # 内存中的会话存储
        self.sessions: Dict[str, Dict] = {}
        
        # 会话配置
        self.max_messages_per_session = 50  # 每个会话最多保留的消息数
        self.session_timeout = 3600 * 24  # 会话超时时间（24小时）
        
        # 会话存储文件路径（可选的持久化存储）
        self.sessions_file = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), 'data', 'sessions.json')
        
        # 加载已有会话（如果存在）
        self._load_sessions()
    
    def _load_sessions(self):
        """从文件加载会话数据"""
        try:
            if os.path.exists(self.sessions_file):
                with open(self.sessions_file, 'r', encoding='utf-8') as f:
                    self.sessions = json.load(f)
                print(f"[SessionService]: 已加载 {len(self.sessions)} 个会话")
        except Exception as e:
            print(f"[SessionService]: 加载会话文件失败: {str(e)}")
            self.sessions = {}
    
    def _save_sessions(self):
        """保存会话数据到文件"""
        try:
            with open(self.sessions_file, 'w', encoding='utf-8') as f:
                json.dump(self.sessions, f, ensure_ascii=False, indent=2)
        except Exception as e:
            print(f"[SessionService]: 保存会话文件失败: {str(e)}")
    
    def create_session(self, character_id: str = None, user_id: str = None, user_token: str = None) -> str:
        """创建新的会话"""
        session_id = str(uuid.uuid4())
        current_time = datetime.datetime.now().isoformat()
        
        session_data = {
            'session_id': session_id,
            'character_id': character_id,
            'user_id': user_id,
            'user_token': user_token,  # 添加用户令牌关联
            'created_at': current_time,
            'last_activity': current_time,
            'messages': [],
            'context_summary': ''  # 用于存储对话摘要（当消息过多时）
        }
        
        self.sessions[session_id] = session_data
        self._save_sessions()
        
        print(f"[SessionService]: 创建新会话 {session_id}, 角色: {character_id}")
        return session_id
    
    def get_session(self, session_id: str) -> Optional[Dict]:
        """获取会话信息"""
        if session_id not in self.sessions:
            return None
        
        session = self.sessions[session_id]
        
        # 检查会话是否过期
        last_activity = datetime.datetime.fromisoformat(session['last_activity'])
        if (datetime.datetime.now() - last_activity).total_seconds() > self.session_timeout:
            print(f"[SessionService]: 会话 {session_id} 已过期")
            return None
        
        return session
    
    def add_message(self, session_id: str, role: str, content: str, character_id: str = None) -> bool:
        """向会话添加消息"""
        session = self.get_session(session_id)
        if not session:
            return False
        
        message = {
            'role': role,  # 'user' 或 'assistant'
            'content': content,
            'timestamp': datetime.datetime.now().isoformat(),
            'character_id': character_id
        }
        
        session['messages'].append(message)
        session['last_activity'] = datetime.datetime.now().isoformat()
        
        # 如果消息数量超过限制，移除最早的消息（保留系统消息）
        if len(session['messages']) > self.max_messages_per_session:
            # 保留第一条系统消息（如果有的话）
            system_messages = [msg for msg in session['messages'] if msg['role'] == 'system']
            user_assistant_messages = [msg for msg in session['messages'] if msg['role'] in ['user', 'assistant']]
            
            # 只保留最新的消息
            keep_count = self.max_messages_per_session - len(system_messages)
            session['messages'] = system_messages + user_assistant_messages[-keep_count:]
        
        self._save_sessions()
        print(f"[SessionService]: 向会话 {session_id} 添加消息，当前消息数: {len(session['messages'])}")
        return True
    
    def get_messages(self, session_id: str) -> List[Dict]:
        """获取会话的所有消息"""
        session = self.get_session(session_id)
        if not session:
            return []
        
        return session['messages']
    
    def get_context_messages(self, session_id: str, character_name: str = None, character_description: str = None) -> List[Dict]:
        """获取用于AI对话的上下文消息列表"""
        session = self.get_session(session_id)
        if not session:
            return []
        
        messages = []
        
        # 如果有角色信息，添加系统消息
        if character_name and character_description:
            system_prompt = Config.CHARACTER_PROMPT_TEMPLATE.format(
                character_name=character_name,
                character_description=character_description,
                user_query="请保持角色设定进行对话。"
            )
            messages.append({
                "role": "system",
                "content": f"你是{character_name}。{character_description}请始终保持这个角色的身份和特点进行对话。"
            })
        
        # 添加历史消息
        for msg in session['messages']:
            if msg['role'] in ['user', 'assistant']:
                messages.append({
                    "role": msg['role'],
                    "content": msg['content']
                })
        
        return messages
    
    def clear_session(self, session_id: str) -> bool:
        """清空会话消息"""
        session = self.get_session(session_id)
        if not session:
            return False
        
        session['messages'] = []
        session['last_activity'] = datetime.datetime.now().isoformat()
        self._save_sessions()
        
        print(f"[SessionService]: 清空会话 {session_id}")
        return True
    
    def delete_session(self, session_id: str) -> bool:
        """删除会话"""
        if session_id in self.sessions:
            del self.sessions[session_id]
            self._save_sessions()
            print(f"[SessionService]: 删除会话 {session_id}")
            return True
        return False
    
    def clear_all_user_sessions(self, user_token: str) -> bool:
        """清空用户的所有会话"""
        try:
            from .user_service import get_user_service
            
            # 获取用户ID
            user_service = get_user_service()
            user = user_service.get_user_by_token(user_token)
            if not user:
                return False
            
            user_id = user['id']
            
            # 找到属于该用户的所有会话
            user_sessions = []
            for session_id, session_data in self.sessions.items():
                if session_data.get('user_id') == user_id:
                    user_sessions.append(session_id)
            
            # 删除所有用户会话
            for session_id in user_sessions:
                if session_id in self.sessions:
                    del self.sessions[session_id]
            
            if user_sessions:
                self._save_sessions()
                print(f"[SessionService]: 清空用户所有会话，共删除 {len(user_sessions)} 个会话")
            
            return True
        except Exception as e:
            print(f"[SessionService]: 清空用户会话失败: {str(e)}")
            return False

    def get_all_sessions(self) -> Dict[str, Dict]:
        """获取所有会话数据（用于统计）"""
        return self.sessions.copy()
    
    def cleanup_expired_sessions(self):
        """清理过期的会话"""
        current_time = datetime.datetime.now()
        expired_sessions = []
        
        for session_id, session in self.sessions.items():
            last_activity = datetime.datetime.fromisoformat(session['last_activity'])
            if (current_time - last_activity).total_seconds() > self.session_timeout:
                expired_sessions.append(session_id)
        
        for session_id in expired_sessions:
            del self.sessions[session_id]
        
        if expired_sessions:
            self._save_sessions()
            print(f"[SessionService]: 清理了 {len(expired_sessions)} 个过期会话")
        
        return len(expired_sessions)
    
    def get_session_list(self, user_id: str = None) -> List[Dict]:
        """获取会话列表"""
        sessions = []
        for session_id, session in self.sessions.items():
            # 如果指定了用户ID，只返回该用户的会话
            if user_id and session.get('user_id') != user_id:
                continue
            
            # 检查会话是否过期
            last_activity = datetime.datetime.fromisoformat(session['last_activity'])
            if (datetime.datetime.now() - last_activity).total_seconds() > self.session_timeout:
                continue
            
            session_info = {
                'session_id': session_id,
                'character_id': session.get('character_id'),
                'created_at': session['created_at'],
                'last_activity': session['last_activity'],
                'message_count': len(session['messages'])
            }
            sessions.append(session_info)
        
        # 按最后活动时间排序
        sessions.sort(key=lambda x: x['last_activity'], reverse=True)
        return sessions
    
    def get_user_sessions(self, user_token: str, character_id: str = None) -> List[Dict]:
        """获取用户的会话列表"""
        from .user_service import get_user_service
        
        # 获取用户ID
        user_service = get_user_service()
        user = user_service.get_user_by_token(user_token)
        if not user:
            return []
        
        user_id = user['id']
        user_sessions = []
        
        for session_id, session in self.sessions.items():
            # 检查是否是该用户的会话（使用user_id而不是user_token）
            if session.get('user_id') != user_id:
                continue
            
            # 如果指定了角色ID，只返回该角色的会话
            if character_id and session.get('character_id') != character_id:
                continue
            
            # 检查会话是否过期
            try:
                last_activity = datetime.datetime.fromisoformat(session['last_activity'])
                if (datetime.datetime.now() - last_activity).total_seconds() > self.session_timeout:
                    continue
            except:
                continue
            
            session_info = {
                'session_id': session_id,
                'character_id': session.get('character_id'),
                'created_at': session['created_at'],
                'last_activity': session['last_activity'],
                'message_count': len(session['messages']),
                'context_summary': session.get('context_summary', '')
            }
            user_sessions.append(session_info)
        
        # 按最后活动时间排序
        user_sessions.sort(key=lambda x: x['last_activity'], reverse=True)
        return user_sessions
    
    def get_latest_user_session(self, user_token: str, character_id: str) -> Optional[str]:
        """获取用户与特定角色的最新会话ID"""
        user_sessions = self.get_user_sessions(user_token, character_id)
        if user_sessions:
            return user_sessions[0]['session_id']
        return None
