import unittest
import os
import sys

# 让测试能够找到 backend 下的模块
sys.path.append(os.path.join(os.path.dirname(__file__), '..'))

from routes.ai_service import AIService


class TestAIIntimacyPrompt(unittest.TestCase):
    def setUp(self):
        self.service = AIService()

    def test_level_stranger_prompt(self):
        prompt = self.service._build_intimacy_prompt(0, "陌生人", is_first_message=False)
        self.assertIn("亲密度等级：初次相识/陌生人", prompt)
        self.assertIn("严格避免使用任何修饰词", prompt)
        self.assertIn("严格禁止主动询问任何问题", prompt)

    def test_level_hot_chat_prompt(self):
        prompt = self.service._build_intimacy_prompt(5, "聊得火热", is_first_message=False)
        self.assertIn("亲密度等级：聊得火热", prompt)
        self.assertIn("更加亲切友好的语气", prompt)

    def test_level_meant_to_meet_prompt(self):
        prompt = self.service._build_intimacy_prompt(10, "相见恨晚", is_first_message=True)
        self.assertIn("亲密度等级：相见恨晚", prompt)
        # 首次消息应包含主动问候的指引
        self.assertIn("在对话开始时主动问候对方", prompt)

    def test_level_intimate_prompt(self):
        prompt = self.service._build_intimacy_prompt(20, "亲密无间", is_first_message=False)
        self.assertIn("亲密度等级：亲密无间", prompt)
        self.assertIn("在回答问题后总是主动询问关怀性问题", prompt)

    def test_level_soulmate_prompt(self):
        prompt = self.service._build_intimacy_prompt(50, "知音难觅", is_first_message=False)
        self.assertIn("亲密度等级：知音难觅", prompt)
        self.assertIn("更详细、更有深度", prompt)

    def test_level_top_prompt(self):
        prompt = self.service._build_intimacy_prompt(100, "伯乐", is_first_message=True)
        self.assertIn("亲密度等级：伯乐", prompt)
        self.assertIn("极其亲密和温暖的称呼", prompt)
        # 首次消息附加建议
        self.assertIn("在对话开始时主动询问对方最近的生活状况", prompt)


if __name__ == '__main__':
    unittest.main()