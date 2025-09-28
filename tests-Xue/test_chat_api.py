import unittest
from unittest.mock import patch
import os
import sys

# 让测试能够找到 backend 下的模块
sys.path.append(os.path.join(os.path.dirname(__file__), '..'))

from app import create_app


class TestChatAPI(unittest.TestCase):
    def setUp(self):
        self.app = create_app()
        self.client = self.app.test_client()

    @patch("routes.ai_service.AIService.chat_completion")
    def test_chat_success(self, mock_chat):
        mock_chat.return_value = {
            "choices": [{"message": {"content": "Hello"}}]
        }

        resp = self.client.post(
            "/api/chat",
            json={
                "messages": [{"role": "user", "content": "hi"}],
                "model": "x-ai/grok-4-fast",
                "stream": False,
                "max_tokens": 50,
            },
        )

        self.assertEqual(resp.status_code, 200)
        data = resp.get_json()
        self.assertTrue(data["success"]) 
        self.assertEqual(data["content"], "Hello")

    @patch("routes.ai_service.AIService.chat_completion")
    def test_chat_failure_backend_none(self, mock_chat):
        mock_chat.return_value = None

        resp = self.client.post(
            "/api/chat",
            json={
                "messages": [{"role": "user", "content": "hi"}],
            },
        )

        self.assertEqual(resp.status_code, 500)
        data = resp.get_json()
        self.assertFalse(data["success"]) 
        self.assertIn("AI服务响应失败", data["error"]) 

    def test_chat_bad_request(self):
        resp = self.client.post(
            "/api/chat",
            json={
                "messages": [],
            },
        )
        self.assertEqual(resp.status_code, 400)
        data = resp.get_json()
        self.assertFalse(data["success"]) 
        self.assertIn("messages参数不能为空", data["error"]) 


if __name__ == "__main__":
    unittest.main()