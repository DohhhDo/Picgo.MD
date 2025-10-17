# 🐾 Picgo.MD 全栈开发环境设置指南

## 🏗️ 项目架构

```
Picgo.MD/
├── picgomd-web/          # React 前端 (端口: 5173)
│   ├── src/
│   │   ├── components/    # UI 组件
│   │   ├── hooks/         # React Hooks
│   │   ├── services/      # API 客户端
│   │   └── theme/         # Chakra UI 主题
│   └── package.json
├── picgomd-backend/      # Python 后端 (端口: 8000)
│   ├── main.py           # FastAPI 服务器
│   └── requirements.txt
├── md-converter-gui/      # 原 PyQt 应用 (复用核心逻辑)
│   ├── core/             # 图片转换核心
│   └── uploader/         # 图床上传模块
└── imarkdown/            # 图片处理库
```

## 🚀 快速启动

### 1. 启动后端服务

```bash
# 方式一：使用启动脚本
python start_backend.py

# 方式二：手动启动
cd picgomd-backend
python main.py
```

后端服务将在 `http://127.0.0.1:8000` 启动

### 2. 启动前端服务

```bash
cd picgomd-web
npm run dev
```

前端应用将在 `http://localhost:5173` 启动

### 3. 访问应用

打开浏览器访问 `
http://localhost:5173`

## 📋 详细设置步骤

### 后端设置

1. **安装 Python 依赖**
   ```bash
   cd meowdown-backend
   pip install -r requirements.txt
   ```

2. **验证核心模块**
   确保以下模块可用：
   - `md-converter-gui/core/image_converter.py` - 图片转换
   - `md-converter-gui/uploader/manager.py` - 图床上传
   - `imarkdown/` - 图片处理库

3. **启动服务**
   ```bash
   python main.py
   ```

### 前端设置

1. **安装 Node.js 依赖**
   ```bash
   cd meowdown-web
   npm install
   ```

2. **启动开发服务器**
   ```bash
   npm run dev
   ```

## 🔌 API 接口

### 核心端点

- **健康检查**: `GET /health`
- **转换 Markdown**: `POST /api/convert`
- **任务状态**: `GET /api/task/{task_id}`
- **上传图床**: `POST /api/upload`
- **WebSocket 进度**: `ws://127.0.0.1:8000/ws/{task_id}`

### API 文档

启动后端后访问：`http://127.0.0.1:8000/docs`

## 🧪 测试功能

1. **连接状态测试**
   - 前端会自动检测后端连接状态
   - 顶部显示连接状态指示器

2. **图片转换测试**
   ```markdown
   # 测试 Markdown
   ![测试图片](https://example.com/image.jpg)
   ```
   - 输入包含图片的 Markdown
   - 调节质量滑块
   - 点击"转换"按钮

3. **实时进度测试**
   - 转换过程中观察进度条更新
   - WebSocket 实时通信测试

## 🛠️ 开发工具

### 前端开发

- **热重载**: Vite 自动刷新
- **类型检查**: TypeScript
- **代码检查**: ESLint
- **UI 组件**: Chakra UI Storybook

### 后端开发

- **自动重载**: FastAPI 开发模式
- **API 文档**: Swagger UI
- **WebSocket 测试**: 浏览器开发者工具

## 🔧 故障排除

### 常见问题

1. **后端无法启动**
   - 检查 Python 版本 (推荐 3.8+)
   - 安装缺失的依赖包
   - 确认端口 8000 未被占用

2. **前端连接失败**
   - 确认后端服务正在运行
   - 检查 CORS 配置
   - 查看浏览器控制台错误

3. **图片转换失败**
   - 检查 `md-converter-gui` 模块导入
   - 确认 Pillow 库正常安装
   - 查看后端日志错误信息

### 调试模式

1. **后端调试**
   ```bash
   # 启用详细日志
   uvicorn main:app --host 127.0.0.1 --port 8000 --reload --log-level debug
   ```

2. **前端调试**
   - 打开浏览器开发者工具
   - 查看 Console 标签
   - 监控 Network 标签

## 🌟 功能特性

### 已实现

- ✅ 现代化 React + Chakra UI 界面
- ✅ FastAPI 后端服务
- ✅ 实时 WebSocket 通信
- ✅ 图片质量控制
- ✅ 转换进度显示
- ✅ 连接状态监控
- ✅ 错误处理和用户反馈

### 开发中

- 🔄 图床配置界面
- 🔄 文件拖拽上传
- 🔄 批量处理优化
- 🔄 转换结果预览

## 📚 技术栈

### 前端

- **React 18** - UI 框架
- **TypeScript** - 类型安全
- **Chakra UI** - 组件库
- **Vite** - 构建工具
- **Axios** - HTTP 客户端

### 后端

- **FastAPI** - Web 框架
- **WebSocket** - 实时通信
- **Pillow** - 图片处理
- **Uvicorn** - ASGI 服务器

### 集成

- **现有 Python 模块** - 复用图片转换逻辑
- **RESTful API** - 标准化接口
- **WebSocket** - 实时进度更新

## 🎯 下一步

1. 启动两个服务
2. 测试基本转换功能
3. 检查实时进度更新
4. 开发图床配置界面
5. 优化用户体验
