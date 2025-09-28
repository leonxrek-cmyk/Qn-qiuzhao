# 🎭 AI角色对话系统 (AI Character Chat System)

一个基于Vue.js + Flask的智能角色对话平台，支持与历史名人、科学家、文学家等多种角色进行个性化对话，具备亲密度系统、语音交互、管理后台等丰富功能。

## 📺 演示视频

🎬 **项目演示**: [https://www.bilibili.com/video/BV1EknZzaE9K/](https://www.bilibili.com/video/BV1EknZzaE9K/)

## ✨ 核心特性

### 🎯 智能角色系统
- **24+历史名人角色**: 包括孔子、苏格拉底、爱因斯坦、居里夫人、莎士比亚等
- **个性化对话**: 每个角色都有独特的语言风格、知识背景和性格特点
- **动态角色管理**: 支持管理员创建、编辑、删除角色配置

### 💕 亲密度系统
- **7级亲密度等级**: 从陌生人到伯乐，逐步解锁更深入的对话体验
- **智能语气调节**: 根据亲密度自动调整角色的语气和回答风格
- **互动增长**: 通过对话自然提升与角色的亲密度

### 🎙️ 语音交互
- **语音识别**: 支持实时语音输入，自动转换为文字
- **语音合成**: 每个角色配备专属音色，提供沉浸式对话体验
- **多格式支持**: 兼容WAV、MP3等多种音频格式

### 👥 用户系统
- **多种登录方式**: 支持注册用户和游客模式
- **个人信息管理**: 自定义昵称、头像等个人资料
- **对话历史**: 完整保存与每个角色的对话记录

### 🛠️ 管理后台
- **数据统计**: 实时显示用户数量、对话统计、热门角色等
- **用户管理**: 查看、编辑、删除用户，设置管理员权限
- **角色管理**: 创建和配置AI角色，设置个性化参数
- **系统监控**: 查看系统日志和运行状态

## 🏗️ 技术架构

### 前端技术栈
- **Vue.js 3**: 现代化前端框架
- **Vue Router**: 单页面应用路由管理
- **Axios**: HTTP客户端，处理API请求
- **CSS3**: 响应式设计和动画效果

### 后端技术栈
- **Flask**: 轻量级Python Web框架
- **Flask-CORS**: 跨域资源共享支持
- **七牛云AI API**: 提供大语言模型和语音服务
- **JSON**: 数据存储和配置管理

### 核心功能模块
- **AI服务**: 智能对话生成和亲密度管理
- **语音服务**: ASR语音识别和TTS语音合成
- **用户服务**: 用户认证、权限管理、数据存储
- **会话服务**: 对话上下文管理和历史记录
- **日志服务**: 系统监控和错误追踪

## 🚀 快速开始

### 环境要求
- **Node.js** >= 16.0.0
- **Python** >= 3.8
- **七牛云AI API密钥**

### 1. 克隆项目
```bash
git clone <repository-url>
cd Qn-qiuzhao
```

### 2. 后端设置
```bash
# 进入后端目录
cd backend

# 安装Python依赖
pip install -r requirements.txt

# 配置环境变量
# 创建 .env 文件并添加以下配置：
QINIU_AI_API_KEY=your_api_key_here
QINIU_AI_BASE_URL=https://openai.qiniu.com/v1

# 启动后端服务
python app.py
```

### 3. 前端设置
```bash
# 进入前端目录
cd frontend

# 安装依赖
npm install

# 开发模式启动
npm run dev

# 生产构建
npm run build
```

### 4. 访问应用
- **前端应用**: http://localhost:5173
- **后端API**: http://localhost:5000
- **管理后台**: http://localhost:5173/admin

## 📁 项目结构

```
Qn-qiuzhao/
├── backend/                 # 后端Flask应用
│   ├── routes/             # API路由模块
│   │   ├── ai_routes.py    # AI对话接口
│   │   ├── auth_routes.py  # 用户认证接口
│   │   ├── admin_routes.py # 管理后台接口
│   │   └── ...
│   ├── services/           # 业务逻辑服务
│   │   ├── ai_service.py   # AI对话服务
│   │   ├── user_service.py # 用户管理服务
│   │   └── ...
│   ├── data/              # 数据存储
│   │   ├── character_configs.json # 角色配置
│   │   ├── users.json     # 用户数据
│   │   └── ...
│   └── app.py             # Flask应用入口
├── frontend/               # 前端Vue应用
│   ├── src/
│   │   ├── components/    # Vue组件
│   │   ├── views/         # 页面视图
│   │   ├── router/        # 路由配置
│   │   └── ...
│   └── dist/              # 构建输出
├── tests/                 # 测试文件
└── logs/                  # 系统日志
```

## 🎮 使用指南

### 用户端功能

#### 1. 注册和登录
- 支持用户注册，自动生成个性化头像
- 提供游客模式，无需注册即可体验
- 个人信息管理和密码修改

#### 2. 角色对话
- 选择喜欢的历史名人角色
- 开始个性化对话，体验不同的语言风格
- 通过持续对话提升亲密度等级

#### 3. 语音交互
- 点击麦克风按钮进行语音输入
- 系统自动识别语音并转换为文字
- 角色回答支持语音播放

#### 4. 对话管理
- 查看与每个角色的对话历史
- 支持对话记录的搜索和筛选
- 亲密度进度可视化显示

### 管理员功能

#### 1. 数据统计
- 实时用户数量和活跃度统计
- 对话数量和热门角色分析
- 系统运行状态监控

#### 2. 用户管理
- 查看所有用户信息和状态
- 编辑用户资料和权限设置
- 用户搜索和批量操作

#### 3. 角色管理
- 创建新的AI角色配置
- 编辑角色的个性和对话风格
- 管理角色头像和语音参数

## 🔧 配置说明

### 环境变量配置
```env
# 七牛云AI API配置
QINIU_AI_API_KEY=your_api_key_here
QINIU_AI_BASE_URL=https://openai.qiniu.com/v1

# Flask应用配置
FLASK_ENV=development
FLASK_RUN_PORT=5000
```

### 角色配置示例
```json
{
  "character_id": {
    "name": "角色名称",
    "description": "角色描述",
    "tags": ["标签1", "标签2"],
    "avatar": "/avatars/character.png",
    "prompt": "角色对话风格提示词",
    "voice_params": {
      "voice_id": "qiniu_zh_male_voice",
      "rate": 160,
      "volume": 0.8
    }
  }
}
```

## 🎨 亲密度系统详解

### 等级划分
1. **陌生人** (0级): 冷漠客观，简洁回答
2. **初次相识** (1-4级): 礼貌但保持距离
3. **聊得火热** (5-9级): 开始热情交流
4. **相见恨晚** (10-19级): 建立友好关系
5. **亲密无间** (20-49级): 深度交流互动
6. **知音难觅** (50-99级): 心灵相通
7. **伯乐** (100级+): 最高级别的信任关系

### 提升机制
- 每次成功对话自动增加亲密度
- 不同角色有独立的亲密度计算
- 游客模式不累积亲密度

## 🔒 安全特性

- **用户认证**: JWT令牌验证和会话管理
- **权限控制**: 管理员和普通用户权限分离
- **数据加密**: 用户密码SHA256加密存储
- **输入验证**: 前后端双重数据验证
- **日志监控**: 完整的操作日志记录

## 🚀 部署指南

### 开发环境
```bash
# 后端
cd backend && python app.py

# 前端
cd frontend && npm run dev
```

### 生产环境
```bash
# 构建前端
cd frontend && npm run build

# 部署后端（推荐使用Gunicorn）
cd backend && gunicorn -w 4 -b 0.0.0.0:5000 app:app
```

## 🤝 贡献指南

1. Fork 本项目
2. 创建特性分支 (`git checkout -b feature/AmazingFeature`)
3. 提交更改 (`git commit -m 'Add some AmazingFeature'`)
4. 推送到分支 (`git push origin feature/AmazingFeature`)
5. 开启 Pull Request

## 📄 开源协议

本项目采用 MIT 协议 - 查看 [LICENSE](LICENSE) 文件了解详情

## 🙏 致谢

- [七牛云AI开放平台](https://ai.qiniu.com/) - 提供AI大模型和语音服务
- [Vue.js](https://vuejs.org/) - 优秀的前端框架
- [Flask](https://flask.palletsprojects.com/) - 简洁的Python Web框架
- 所有为开源社区做出贡献的开发者们

## 📞 联系方式

如有问题或建议，欢迎通过以下方式联系：

- 📧 邮箱: [your-email@example.com]
- 🐛 问题反馈: [GitHub Issues](https://github.com/your-repo/issues)
- 💬 讨论交流: [GitHub Discussions](https://github.com/your-repo/discussions)

---

⭐ 如果这个项目对您有帮助，请给我们一个星标！

🎬 **观看演示视频**: [https://www.bilibili.com/video/BV1EknZzaE9K/](https://www.bilibili.com/video/BV1EknZzaE9K/)
