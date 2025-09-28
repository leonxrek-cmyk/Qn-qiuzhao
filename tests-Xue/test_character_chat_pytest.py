import pytest
from routes.ai_service import AIService


def test_character_chat_success(client, monkeypatch):
    def mock_chat_with_intimacy(self, messages, character_name=None, character_description=None,
                                 intimacy_level=0, intimacy_name="陌生人", is_first_message=False,
                                 model=None, stream=False, max_tokens=4096):
        return {"choices": [{"message": {"content": "角色回复"}}]}

    monkeypatch.setattr(AIService, "character_chat_with_intimacy", mock_chat_with_intimacy)

    resp = client.post(
        "/api/character_chat",
        json={
            "character_name": "测试角色",
            "character_description": "这是一个用于测试的角色描述。",
            "user_query": "你好",
        },
    )

    assert resp.status_code == 200
    data = resp.get_json()
    assert data["success"] is True
    assert data["content"] == "角色回复"


def test_character_chat_failure(client, monkeypatch):
    monkeypatch.setattr(AIService, "character_chat_with_intimacy", lambda *args, **kwargs: None)

    resp = client.post(
        "/api/character_chat",
        json={
            "character_name": "测试角色",
            "user_query": "你好",
        },
    )

    assert resp.status_code == 500
    data = resp.get_json()
    assert data["success"] is False
    assert "AI服务响应失败" in data["error"]