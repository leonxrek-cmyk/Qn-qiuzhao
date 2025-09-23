# 七牛云AI角色扮演聊天平台

一个基于七牛云AI大模型X-Ai/Grok 4 Fast的角色扮演聊天网站，用户可以搜索自己感兴趣的角色并与其进行多模态交互（支持文本、图像、音频、视频输入）。

## 项目结构

```
Qn-qiuzhao/
├── backend/           # 后端Python代码
│   ├── ai_service.py  # AI服务封装
│   ├── voice_service.py # 语音服务封装
│   └── app.py         # Flask应用入口
├── frontend/          # 前端Vue代码
│   ├── src/           # 前端源代码
│   ├── package.json   # 前端依赖配置
│   └── vite.config.js # Vite配置
├── common/            # 公共资源
│   └── characters.json # 角色数据
└── README.md          # 项目说明文档
```

## 功能特点

- **角色选择**：内置多种经典角色供用户选择
- **文字聊天**：与AI角色进行实时文字对话
- **语音交互**：支持语音输入和语音输出
- **多模态支持**：支持文本、图像、音频、视频输入，返回文本响应
- **角色搜索**：搜索和筛选感兴趣的角色
- **个性化设置**：语言、主题、AI参数等配置

## 团队分工说明

### 曹艺洋
- **技术全面负责**：主导前端代码开发工作，同时提供后端技术支持，确保前后端技术栈协同与整体架构一致性
- **项目管理**：全面负责Pull Request（PR）的审核工作，制定并执行严格的代码审查标准，确保代码质量，并及时完成项目合并操作，保障项目开发进度
- **原型开发**：独立完成项目初期基本业务原型的开发工作，构建可运行、可演示的系统雏形
- **技术指导**：为后端开发团队提供开发模板示例，规范开发流程与代码风格，提升团队整体开发效率
- **业务与技术设计**：全面负责业务需求分析、功能规划、接口设计及技术细节设计工作，确保系统设计的合理性、完整性与可扩展性

### 薛雅倩、刘翔宇
- **后端开发实现**：负责后端程序的具体编码与实现工作，严格遵循项目技术规范与编码标准
- **需求落地**：根据曹艺洋提供的业务场景分析与技术设计方案，进行具体功能的编码实现，确保业务需求的准确落地
- **代码重构**：在完成快速原型开发阶段后，负责Java业务代码的重构工作，优化代码结构，提升系统性能与可维护性
- **技术优化**：持续关注后端系统的性能表现，识别并解决潜在技术问题，提出并实施优化方案，确保系统的稳定性与高效性

## 技术栈

- **前端**：Vue 3、Vite、Axios、Vue Router
- **后端**：Python、Flask、Requests
- **AI服务**：七牛云AI大模型X-Ai/Grok 4 Fast推理API
- **语音处理**：Google语音识别API

## 快速开始

### 后端设置

1. 进入后端目录：
```bash
cd backend
```

2. 创建虚拟环境：
```bash
python -m venv venv
```

3. 激活虚拟环境：
```bash
# Windows
env\Scripts\activate
# macOS/Linux
source venv/bin/activate
```

4. 安装依赖：
```bash
pip install flask openai python-dotenv requests speech_recognition pyaudio
```

5. 创建`.env`文件，配置七牛云API密钥（如果不配置，将使用默认的API密钥）：
```env
QINIU_AI_API_KEY=sk-7b910549d43e0b5ca876b8aa3392f71fe1dd35b73c256f8e3b3a22bb708de331
QINIU_AI_BASE_URL=https://openai.qiniu.com/v1
```

6. 启动后端服务：
```bash
python app.py
```

### 前端设置

1. 进入前端目录：
```bash
cd frontend
```

2. 安装依赖：
```bash
npm install
```

3. 启动开发服务器：
```bash
npm run dev
```

4. 在浏览器中访问：`http://localhost:3000`

## 部署说明

### 后端部署

1. 安装依赖：
```bash
pip install -r requirements.txt
```

2. 使用Gunicorn或uWSGI部署Flask应用：
```bash
gunicorn -w 4 -b 0.0.0.0:5000 app:app
```

### 前端部署

1. 构建前端项目：
```bash
npm run build
```

2. 将`dist`目录部署到Web服务器（如Nginx、Apache）

## 注意事项

- 默认使用X-Ai/Grok 4 Fast模型，支持多模态输入
- 语音功能需要浏览器支持麦克风访问
- 多模态功能支持上传图片、音频和视频文件
- 项目处于开发阶段，可能会有功能更新和bug修复

## License

MIT