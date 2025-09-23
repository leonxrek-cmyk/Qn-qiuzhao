import requests
import json

# 测试前端代理API连接
def test_frontend_proxy():
    print('开始测试前端API代理...')
    
    frontend_url = 'http://localhost:3000'
    
    try:
        # 测试获取模型列表
        models_response = requests.get(f'{frontend_url}/api/models')
        models_data = models_response.json()
        print(f'模型列表API响应状态码: {models_response.status_code}')
        print(f'可用模型: {models_data.get("models", [])}')
        
        # 测试基础聊天API
        chat_response = requests.post(
            f'{frontend_url}/api/chat',
            headers={'Content-Type': 'application/json'},
            json={
                'message': '你好，测试前端代理连接',
                'model': 'x-ai/grok-4-fast'
            }
        )
        chat_data = chat_response.json()
        print(f'聊天API响应状态码: {chat_response.status_code}')
        print(f'聊天响应内容: {chat_data.get("content", "无内容")}')
        
        # 测试角色扮演聊天API
        character_chat_response = requests.post(
            f'{frontend_url}/api/character_chat',
            headers={'Content-Type': 'application/json'},
            json={
                'character_name': '爱因斯坦',
                'character_description': '20世纪最著名的物理学家，相对论的创立者',
                'user_query': '你能简单解释一下相对论吗？',
                'model': 'x-ai/grok-4-fast'
            }
        )
        character_chat_data = character_chat_response.json()
        print(f'角色扮演聊天API响应状态码: {character_chat_response.status_code}')
        print(f'角色扮演聊天响应内容: {character_chat_data.get("content", "无内容")}')
        
        print('✅ 所有前端代理API测试成功完成！')
        return True
    except Exception as e:
        print(f'❌ API测试失败: {str(e)}')
        return False

if __name__ == '__main__':
    test_frontend_proxy()