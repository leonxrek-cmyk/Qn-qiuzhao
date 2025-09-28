import os
import sys
import pytest

# 让 pytest 能正确导入 backend 下的模块
sys.path.append(os.path.join(os.path.dirname(__file__), '..'))

from app import create_app


@pytest.fixture
def app():
    return create_app()


@pytest.fixture
def client(app):
    return app.test_client()