import json
import os

# 测试角色配置文件的加载
def test_character_configs():
    file_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'character_configs.json')
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            data = json.load(f)
            print(f'成功加载角色配置文件，包含{len(data)}个角色')
            # 打印前几个角色的基本信息
            count = 0
            for character_id, config in data.items():
                print(f'角色ID: {character_id}, 名称: {config.get("name", "未知")}')
                count += 1
                if count >= 2:  # 只打印前两个角色
                    break
    except Exception as e:
        print(f'加载角色配置文件失败: {e}')

if __name__ == '__main__':
    test_character_configs()