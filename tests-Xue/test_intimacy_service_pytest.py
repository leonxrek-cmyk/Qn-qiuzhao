import json
import tempfile
import os
import pytest
from services.intimacy_service import IntimacyService


@pytest.fixture
def temp_users_file():
    fd, path = tempfile.mkstemp(suffix="_users.json")
    os.close(fd)
    # 初始化用户数据
    init_data = {
        "users": {
            "alice": {"id": "u1", "intimacy": {"charA": 0}},
            "bob": {"id": "u2"}
        }
    }
    with open(path, "w", encoding="utf-8") as f:
        json.dump(init_data, f, ensure_ascii=False, indent=2)
    yield path
    try:
        os.remove(path)
    except Exception:
        pass


def test_intimacy_levels_and_progress(temp_users_file):
    service = IntimacyService()
    # 将读写文件定位到临时文件
    service.users_file = temp_users_file

    # 等级名称判定
    assert service.get_level_name(0) == "陌生人"
    assert service.get_level_name(5) == "聊得火热"
    assert service.get_level_name(10) == "相见恨晚"
    assert service.get_level_name(20) == "亲密无间"
    assert service.get_level_name(50) == "知音难觅"
    assert service.get_level_name(100) == "伯乐"

    # 进度信息判定（边界与最高级）
    p0 = service.get_level_progress(0)
    assert p0["current_level"] == "陌生人"
    assert p0["next_level"] == "初次相识"

    p_top = service.get_level_progress(120)
    assert p_top["current_level"] == "伯乐"
    assert p_top["next_level"] is None
    assert p_top["progress"] == 100


def test_increase_intimacy(temp_users_file):
    service = IntimacyService()
    service.users_file = temp_users_file

    # 初始值
    val0 = service.get_intimacy("u1", "charA")
    assert val0 == 0

    # 增加亲密度
    result = service.increase_intimacy("u1", "charA")
    assert result["success"] is True
    assert result["intimacy"] == 1
    assert result["level_name"] in ("初次相识", "聊得火热", "陌生人")

    # 再次增加，验证持续写入
    result2 = service.increase_intimacy("u1", "charA")
    assert result2["success"] is True
    assert result2["intimacy"] == 2