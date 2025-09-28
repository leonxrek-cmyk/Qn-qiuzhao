import unittest
import os
import sys

# 让测试能够找到 backend 下的模块
sys.path.append(os.path.join(os.path.dirname(__file__), '..'))

from services.session_service import SessionService


class TestSessionContext(unittest.TestCase):
    def setUp(self):
        self.session_service = SessionService()
        self.session_id = self.session_service.create_session(character_id="char_1", user_id="user_1")

    def tearDown(self):
        # 清理该会话，避免污染后续测试
        self.session_service.delete_session(self.session_id)

    def test_get_context_messages_with_role(self):
        # 添加历史消息
        self.session_service.add_message(self.session_id, role="user", content="你好")
        self.session_service.add_message(self.session_id, role="assistant", content="你好呀")

        # 构造上下文
        messages = self.session_service.get_context_messages(
            self.session_id,
            character_name="测试角色",
            character_description="这是一个用于测试的角色描述。"
        )

        # 应包含系统消息并且在首位
        self.assertGreaterEqual(len(messages), 3)
        self.assertEqual(messages[0]["role"], "system")
        self.assertIn("你是测试角色", messages[0]["content"])
        self.assertIn("请始终保持这个角色的身份和特点进行对话", messages[0]["content"])

    def test_get_context_messages_without_session(self):
        messages = self.session_service.get_context_messages("non_exist_session")
        self.assertEqual(messages, [])


if __name__ == '__main__':
    unittest.main()