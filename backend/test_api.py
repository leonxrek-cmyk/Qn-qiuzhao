import requests

# 测试获取模型列表
def test_get_models():
    url = 'http://localhost:5000/api/models'
    try:
        response = requests.get(url)
        print(f"获取模型列表响应状态码: {response.status_code}")
        print(f"响应内容: {response.json()}")
    except Exception as e:
        print(f"测试失败: {e}")

# 测试基础聊天接口
def test_chat():
    url = 'http://localhost:5000/api/chat'
    data = {
        "messages": [
            {"role": "user", "content": "你好，能简单介绍一下你自己吗？"}
        ]
    }
    try:
        response = requests.post(url, json=data)
        print(f"基础聊天接口响应状态码: {response.status_code}")
        print(f"响应内容: {response.json()}")
    except Exception as e:
        print(f"测试失败: {e}")

if __name__ == '__main__':
    print("开始测试 API...")
    test_get_models()
    print("\n测试基础聊天接口...")
    test_chat()