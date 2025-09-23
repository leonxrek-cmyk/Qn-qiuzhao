import json
import os

filepath = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'character_configs.json')
print(f'文件路径: {filepath}')
try:
    with open(filepath, 'r', encoding='utf-8') as f:
        data = json.load(f)
        print(f'JSON解析成功! 角色数量: {len(data)}')
except Exception as e:
    print(f'JSON解析失败: {e}')