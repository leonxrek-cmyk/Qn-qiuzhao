import os
from dotenv import load_dotenv

# 加载环境变量
load_dotenv()

class Config:
    # 七牛云AI API配置
    QINIU_AI_API_KEY = os.getenv('QINIU_AI_API_KEY', 'sk-7b910549d43e0b5ca876b8aa3392f71fe1dd35b73c256f8e3b3a22bb708de331')
    QINIU_AI_BASE_URL = os.getenv('QINIU_AI_BASE_URL', 'https://openai.qiniu.com/v1')
    
    # Flask配置
    FLASK_APP = os.getenv('FLASK_APP', 'app.py')
    FLASK_ENV = os.getenv('FLASK_ENV', 'development')
    FLASK_RUN_PORT = int(os.getenv('FLASK_RUN_PORT', 5000))
    
    # 默认模型配置
    DEFAULT_MODEL = 'x-ai/grok-4-fast'
    
    # 角色配置
    CHARACTER_PROMPT_TEMPLATE = """你现在需要扮演{character_name}，请严格按照以下要求进行对话：
1. 保持{character_name}的语言风格、性格特点和知识背景
2. 回答要符合{character_name}的身份和时代背景
3. 不要说任何不符合角色设定的内容
4. 对话要自然流畅，符合日常交流的方式
5. 请以{character_name}的第一人称进行回答

{character_description}

用户的问题：{user_query}"""