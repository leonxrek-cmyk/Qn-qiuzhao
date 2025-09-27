# DeepTalk

一个基于Vue.js和Flask的AI角色扮演聊天应用，支持多种AI角色与用户进行对话。

## 功能特性

### 核心功能
- **多角色扮演**: 支持多种预设AI角色（哈利·波特、福尔摩斯、爱因斯坦等）
- **智能对话**: 基于OpenAI API的自然语言处理
- **对话上下文**: 支持会话记忆，保持对话连贯性
- **响应式设计**: 适配桌面和移动设备

### 对话上下文功能
- **会话管理**: 每个角色对话都有独立的会话ID
- **上下文记忆**: AI能够记住之前的对话内容
- **会话清空**: 支持清空当前会话历史
- **多轮对话**: 支持长时间的连续对话

## 技术栈

### 后端
- **Flask**: Web框架
- **OpenAI API**: AI模型服务
- **Flask-CORS**: 跨域支持
- **Python-dotenv**: 环境变量管理

### 前端
- **Vue.js 3**: 前端框架
- **Vue Router**: 路由管理
- **Axios**: HTTP客户端
- **Vite**: 构建工具

## 项目结构

```
├── backend/                    # 后端代码
│   ├── routes/                 # 路由模块
│   │   ├── ai_routes.py       # AI相关路由
│   │   ├── character_routes.py # 角色配置路由
│   │   └── session_routes.py   # 会话管理路由
│   ├── ai_service.py          # AI服务
│   ├── app.py                 # Flask应用主文件
│   ├── character_configs.json # 角色配置文件
│   ├── config.py              # 配置文件
│   ├── log_service.py         # 日志服务
│   ├── session_service.py     # 会话管理服务
│   └── requirements.txt       # Python依赖
├── frontend/                   # 前端代码
│   ├── src/
│   │   ├── components/        # Vue组件
│   │   ├── views/             # 页面组件
│   │   ├── router/            # 路由配置
│   │   ├── apiService.js      # API服务
│   │   └── main.js            # 应用入口
│   ├── public/                # 静态资源
│   └── package.json           # Node.js依赖
├── logs/                      # 日志文件
└── README.md                  # 项目文档
```

## 安装和运行

### 环境要求
- Python 3.8+
- Node.js 16+
- OpenAI API密钥

### 后端设置

1. 进入后端目录：
```bash
cd backend
```

2. 安装Python依赖：
```bash
pip install -r requirements.txt
```

3. 创建环境变量文件 `.env`：
```env
OPENAI_API_KEY=your_openai_api_key_here
FLASK_ENV=development
FLASK_RUN_PORT=5000
```

4. 启动后端服务：
```bash
python app.py
```

### 前端设置

1. 进入前端目录：
```bash
cd frontend
```

2. 安装Node.js依赖：
```bash
npm install
```

3. 启动开发服务器：
```bash
npm run dev
```

4. 构建生产版本：
```bash
npm run build
```

## API接口

### AI对话接口
- `POST /api/chat` - 基础聊天
- `POST /api/character_chat` - 角色扮演聊天
- `POST /api/multimodal_chat` - 多模态聊天
- `GET /api/models` - 获取可用模型

### 角色管理接口
- `GET /api/character_config` - 获取所有角色配置
- `GET /api/character_config/<id>` - 获取特定角色配置

### 会话管理接口
- `POST /api/sessions` - 创建新会话
- `GET /api/sessions/<id>` - 获取会话信息
- `GET /api/sessions/<id>/messages` - 获取会话消息
- `POST /api/sessions/<id>/clear` - 清空会话

## 角色配置

角色配置存储在 `backend/character_configs.json` 文件中，包含以下信息：
- 角色ID和名称
- 角色描述和背景
- 角色标签
- 语言风格设置

示例配置：
```json
{
  "harry-potter": {
    "id": "harry-potter",
    "name": "哈利·波特",
    "description": "霍格沃茨魔法学校的学生，勇敢善良",
    "tags": ["文学", "奇幻", "魔法"],
    "avatar": "/harry-potter.png",
    "prompt": "你现在扮演哈利·波特...",
    "language_style": {
      "tone": "勇敢而友好",
      "vocabulary": "包含一些魔法相关术语",
      "sentence_structure": "口语化，简短有力"
    }
  }
}
```

## 开发指南

### 添加新角色
1. 在 `character_configs.json` 中添加角色配置
2. 准备角色头像图片放入 `frontend/public/` 目录
3. 重启后端服务以加载新配置

### 自定义AI模型
在 `config.py` 中修改 `DEFAULT_MODEL` 配置，或通过API参数指定模型。

### 日志管理
应用日志存储在 `logs/` 目录下：
- `app.log` - 应用日志
- `error.log` - 错误日志

## 部署

### 生产环境部署
1. 设置环境变量 `FLASK_ENV=production`
2. 使用WSGI服务器（如Gunicorn）运行后端
3. 使用Nginx等反向代理服务器
4. 构建前端生产版本并部署到静态文件服务器

### Docker部署
项目支持Docker容器化部署，可以创建相应的Dockerfile和docker-compose.yml文件。

## 注意事项

### API密钥安全
- 不要将OpenAI API密钥提交到版本控制系统
- 在生产环境中使用环境变量或密钥管理服务

### 性能优化
- 对于高并发场景，建议使用Redis等缓存系统
- 可以实现会话数据的持久化存储
- 考虑实现API请求限流和缓存

### 错误处理
- 应用包含完整的错误处理和日志记录
- 前端有友好的错误提示界面
- 后端API返回标准化的错误响应

## 贡献

欢迎提交Issue和Pull Request来改进这个项目。

## 许可证

MIT License