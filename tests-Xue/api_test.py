import requests
import json
from typing import Any, Dict, List, Optional, Callable

TIMEOUT = 30

CONFIG: Dict[str, Any] = {
    "base_url": "http://localhost:8000",  # 根据实际后端地址调整
    "auth": {"type": "bearer", "token": None},  # 若需要登录后再注入 token
    "endpoints": {
        # AI 基础聊天
        "ai_chat": {
            "method": "POST",
            "path": "/chat",
            "cases": [
                {
                    "name": "正常-最小messages",
                    "request": {
                        "json": {"messages": [{"role": "user", "content": "你好"}]}
                    },
                    "expect": {
                        "status": 200,
                        "json_schema": {"content": str}
                    }
                },
                {
                    "name": "边界-空messages",
                    "request": {"json": {"messages": []}},
                    "expect": {"status": 400}
                },
                {
                    "name": "异常-非法model",
                    "request": {
                        "json": {
                            "messages": [{"role": "user", "content": "test"}],
                            "model": "unknown-model"
                        }
                    },
                    "expect": {"status": 400}
                },
            ]
        },
        # 角色聊天（与亲密度、会话可能关联）
        "character_chat": {
            "method": "POST",
            "path": "/character_chat",
            "cases": [
                {
                    "name": "正常-基于名称",
                    "request": {
                        "json": {
                            "character_name": "Alice",
                            "user_query": "早上好"
                        }
                    },
                    "expect": {"status": 200, "json_schema": {"content": str}}
                },
                {
                    "name": "异常-缺少必填",
                    "request": {"json": {"character_name": "Alice"}},
                    "expect": {"status": 400}
                },
            ]
        },
        # 多模态聊天（支持 multipart/form-data 与 JSON）
        "multimodal_chat": {
            "method": "POST",
            "path": "/multimodal_chat",
            "cases": [
                {
                    "name": "正常-JSON文本输入",
                    "request": {
                        "json": {
                            "text": "描述这张图片",
                            "model": "auto"
                        }
                    },
                    "expect": {"status": 200, "json_schema": {"content": str}}
                },
                {
                    "name": "正常-multipart图片",
                    "request": {
                        "data": {"text": "这是什么?"},
                        # 替换为本地存在的图片文件路径
                        "files": {"image": ("test.jpg", open("tests/assets/test.jpg", "rb"), "image/jpeg")}
                    },
                    "expect": {"status": 200}
                },
                {
                    "name": "异常-不支持的文件类型",
                    "request": {
                        "data": {"text": "看看这个"},
                        "files": {"image": ("bad.txt", b"hello", "text/plain")}
                    },
                    "expect": {"status": 400}
                },
            ]
        },
        # 会话管理
        "sessions_create": {
            "method": "POST",
            "path": "/sessions",
            "cases": [
                {
                    "name": "正常-创建会话",
                    "request": {"json": {"character_id": 1}},
                    "expect": {"status": 200, "json_schema": {"session_id": (str, int)}},
                    "save": {"session_id": "session_id"}
                }
            ]
        },
        "sessions_get": {
            "method": "GET",
            "path": "/sessions/{session_id}",
            "cases": [
                {
                    "name": "正常-查看会话",
                    "request": {},
                    "expect": {"status": 200, "json_schema": {"id": (str, int), "messages": list}}
                }
            ]
        },
        "session_messages": {
            "method": "GET",
            "path": "/sessions/{session_id}/messages",
            "cases": [
                {"name": "正常-获取消息", "request": {}, "expect": {"status": 200, "json_schema": {"messages": list}}}
            ]
        },
        "session_clear": {
            "method": "POST",
            "path": "/sessions/{session_id}/clear",
            "cases": [
                {"name": "正常-清空消息", "request": {}, "expect": {"status": 200}}
            ]
        },
        # 亲密度
        "intimacy_get": {
            "method": "GET",
            "path": "/intimacy/{character_id}",
            "cases": [
                {"name": "正常-查看亲密度", "request": {}, "expect": {"status": 200, "json_schema": {"level": int, "progress": float}}}
            ]
        },
        # ASR
        "asr_recognize": {
            "method": "POST",
            "path": "/recognize",
            "cases": [
                {
                    "name": "正常-上传音频",
                    "request": {
                        "files": {"audio": ("test.wav", open("tests/assets/test.wav", "rb"), "audio/wav")},
                        "data": {"language": "zh"}
                    },
                    "expect": {"status": 200, "json_schema": {"text": str}}
                }
            ]
        },
        # TTS
        "tts_text_to_speech": {
            "method": "POST",
            "path": "/text_to_speech",
            "cases": [
                {
                    "name": "正常-合成",
                    "request": {"json": {"text": "你好", "voice": "female"}},
                    "expect": {"status": 200}  # 若返回音频字节或下载链接，可进一步校验
                },
                {
                    "name": "异常-空文本",
                    "request": {"json": {"text": "", "voice": "female"}},
                    "expect": {"status": 400}
                }
            ]
        },
    }
}

CONTEXT: Dict[str, Any] = {}

# ---------- 简单校验工具 ----------

def expect_status(resp: requests.Response, status: int):
    assert resp.status_code == status, f"status {resp.status_code} != {status}, body={safe_body(resp)}"


def safe_body(resp: requests.Response) -> str:
    try:
        return json.dumps(resp.json(), ensure_ascii=False)
    except Exception:
        return resp.text[:500]


def validate_json_schema(resp: requests.Response, schema: Dict[str, Any]):
    data = resp.json()
    for key, type_or_tuple in schema.items():
        assert key in data, f"missing key: {key}, body={data}"
        value = data[key]
        if isinstance(type_or_tuple, tuple):
            assert isinstance(value, type_or_tuple), f"key {key} type {type(value)} not in {type_or_tuple}"
        elif isinstance(type_or_tuple, type):
            assert isinstance(value, type_or_tuple), f"key {key} type {type(value)} != {type_or_tuple}"
        else:
            raise AssertionError(f"schema for {key} must be type or tuple of types")


def apply_save(resp: requests.Response, save_cfg: Dict[str, str]):
    """将返回 JSON 中的字段保存到上下文，如 {"session_id": "session_id"}"""
    try:
        data = resp.json()
    except Exception:
        return
    for ctx_key, json_key in save_cfg.items():
        if json_key in data:
            CONTEXT[ctx_key] = data[json_key]


def build_url(base: str, path: str) -> str:
    # 替换路径中的上下文变量，如 {session_id}
    for k, v in CONTEXT.items():
        placeholder = "{" + k + "}"
        if placeholder in path:
            path = path.replace(placeholder, str(v))
    return base.rstrip("/") + path


def build_headers(auth_cfg: Dict[str, Any]) -> Dict[str, str]:
    headers = {"Accept": "application/json"}
    if auth_cfg and auth_cfg.get("type") == "bearer" and auth_cfg.get("token"):
        headers["Authorization"] = f"Bearer {auth_cfg['token']}"
    return headers


def send_request(method: str, url: str, headers: Dict[str, str], req_cfg: Dict[str, Any]) -> requests.Response:
    kwargs: Dict[str, Any] = {"headers": headers, "timeout": TIMEOUT}
    if "json" in req_cfg: kwargs["json"] = req_cfg["json"]
    if "params" in req_cfg: kwargs["params"] = req_cfg["params"]
    if "data" in req_cfg: kwargs["data"] = req_cfg["data"]
    if "files" in req_cfg: kwargs["files"] = req_cfg["files"]
    # 若需要流式响应，可在某些 case 中添加 req_cfg["stream"] = True
    if req_cfg.get("stream"):
        kwargs["stream"] = True
    return requests.request(method=method.upper(), url=url, **kwargs)


def run_case(ep_name: str, method: str, path: str, case: Dict[str, Any], base_url: str, auth_cfg: Dict[str, Any]) -> Dict[str, Any]:
    url = build_url(base_url, path)
    headers = build_headers(auth_cfg)
    req_cfg = case.get("request", {})
    resp = send_request(method, url, headers, req_cfg)

    expect = case.get("expect", {})
    status = expect.get("status", 200)
    expect_status(resp, status)

    if status == 200 and "json_schema" in expect:
        validate_json_schema(resp, expect["json_schema"])

    if "save" in case:
        apply_save(resp, case["save"])

    return {
        "endpoint": ep_name,
        "case": case.get("name", "Unnamed"),
        "status_code": resp.status_code,
        "ok": True,
    }


def run_all():
    base_url = CONFIG["base_url"]
    auth_cfg = CONFIG.get("auth", {})
    results: List[Dict[str, Any]] = []

    for ep_name, ep in CONFIG["endpoints"].items():
        method = ep["method"]
        path = ep["path"]
        cases = ep.get("cases", [])
        for case in cases:
            try:
                result = run_case(ep_name, method, path, case, base_url, auth_cfg)
                print(f"[PASS] {ep_name} - {case.get('name')}")
                results.append(result)
            except AssertionError as e:
                print(f"[FAIL] {ep_name} - {case.get('name')}: {e}")
                results.append({
                    "endpoint": ep_name,
                    "case": case.get("name", "Unnamed"),
                    "ok": False,
                    "error": str(e)
                })
            except Exception as e:
                print(f"[ERROR] {ep_name} - {case.get('name')}: {e}")
                results.append({
                    "endpoint": ep_name,
                    "case": case.get("name", "Unnamed"),
                    "ok": False,
                    "error": str(e)
                })
    print("\n=== SUMMARY ===")
    total = len(results)
    passed = sum(1 for r in results if r.get("ok"))
    failed = total - passed
    print(f"Total: {total}, Passed: {passed}, Failed: {failed}")
    return results


if __name__ == "__main__":
    run_all()