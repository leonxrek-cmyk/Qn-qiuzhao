import base64
import pytest
from routes.ai_service import AIService


def test_multimodal_chat_text_only_success(client, monkeypatch):
    def mock_multi(self, text=None, image=None, audio=None, video=None, model=None, stream=False):
        assert text == "hello"
        return {"choices": [{"message": {"content": "OK-TEXT"}}]}

    monkeypatch.setattr(AIService, "multimodal_completion", mock_multi)

    resp = client.post(
        "/api/multimodal_chat",
        json={
            "text": "hello",
            "model": "x-ai/grok-4-fast",
        },
    )

    assert resp.status_code == 200
    data = resp.get_json()
    assert data["success"] is True
    assert data["content"] == "OK-TEXT"


def test_multimodal_chat_image_audio_success(client, monkeypatch):
    def mock_multi(self, text=None, image=None, audio=None, video=None, model=None, stream=False):
        assert isinstance(image, str) and isinstance(audio, str)
        return {"choices": [{"message": {"content": "OK-IMG-AUDIO"}}]}

    monkeypatch.setattr(AIService, "multimodal_completion", mock_multi)

    # 构造简短的 base64 数据（不要求真实图片/音频）
    fake_image = base64.b64encode(b"fakepng").decode("utf-8")
    fake_audio = base64.b64encode(b"fakewav").decode("utf-8")

    resp = client.post(
        "/api/multimodal_chat",
        json={
            "text": "描述一下这张图与音频",
            "image": fake_image,
            "audio": fake_audio,
        },
    )

    assert resp.status_code == 200
    data = resp.get_json()
    assert data["success"] is True
    assert data["content"] == "OK-IMG-AUDIO"


def test_multimodal_chat_bad_request(client):
    resp = client.post(
        "/api/multimodal_chat",
        json={},
    )

    assert resp.status_code == 400
    data = resp.get_json()
    assert data["success"] is False
    assert "至少需要提供" in data["error"]


def test_multimodal_chat_backend_none(client, monkeypatch):
    monkeypatch.setattr(AIService, "multimodal_completion", lambda *args, **kwargs: None)

    resp = client.post(
        "/api/multimodal_chat",
        json={
            "text": "hello",
        },
    )

    assert resp.status_code == 500
    data = resp.get_json()
    assert data["success"] is False
    assert "多模态服务响应失败" in data["error"]