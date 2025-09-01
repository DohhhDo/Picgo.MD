# 🐾 Meowdown Web - 现代化 Markdown 图片转换器

基于 React + Chakra UI 的现代化 Web 版本，提供统一的设计系统和优秀的用户体验。

## ✨ 特性

### 🎨 现代化 UI/UX
- **Chakra UI 设计系统** - 统一、可复用的组件库
- **响应式设计** - 适配各种屏幕尺寸
- **深色/浅色主题** - 自动跟随系统主题
- **流畅动画** - 基于 Framer Motion 的交互动画

### 🚀 核心功能
- **Markdown 编辑器** - 实时编辑，语法高亮
- **图片质量控制** - 滑块调节，预设选项
- **批量转换** - 智能识别并转换图片
- **进度显示** - 实时转换进度反馈
- **图床上传** - 多平台图床支持

### 🛠️ 技术栈
- **React 18** - 最新的 React 版本
- **TypeScript** - 类型安全的开发体验
- **Vite** - 快速的构建工具
- **Chakra UI** - 现代化组件库
- **Framer Motion** - 动画库
- **Axios** - HTTP 客户端

## 📁 项目结构

```
src/
├── components/          # UI 组件
│   ├── AppLayout.tsx   # 主布局组件
│   ├── MarkdownEditor.tsx # Markdown 编辑器
│   ├── ControlPanel.tsx   # 控制面板
│   └── index.ts        # 组件导出
├── hooks/              # 自定义 Hooks
│   └── useAppState.ts  # 应用状态管理
├── theme/              # 主题配置
│   └── index.ts        # Chakra UI 主题
├── types/              # TypeScript 类型定义
│   └── index.ts        # 通用类型
├── App.tsx             # 主应用组件
└── main.tsx           # 应用入口
```

## 🚦 快速开始

### 安装依赖
```bash
npm install
```

### 启动开发服务器
```bash
npm run dev
```

### 构建生产版本
```bash
npm run build
```

## 🎯 设计原则

### 统一性
- 使用 Chakra UI 的设计令牌确保视觉一致性
- 标准化的间距、颜色、字体规范
- 一致的交互模式和动画效果

### 可维护性
- 组件化架构，高度可复用
- TypeScript 类型安全
- 清晰的文件组织结构

### 可扩展性
- 模块化的组件设计
- 灵活的主题系统
- 易于添加新功能和样式

### 用户体验
- 响应式设计，适配各种设备
- 直观的操作流程
- 实时反馈和状态提示

## 🔄 从 PyQt 到 React 的迁移

### 架构对比

| 功能 | PyQt 版本 | React 版本 |
|------|-----------|------------|
| UI 框架 | PyQt6 | React + Chakra UI |
| 状态管理 | 类属性 | React Hooks |
| 样式系统 | CSS 字符串 | Chakra UI 主题 |
| 组件复用 | 继承 | 组合 |
| 类型安全 | Python 类型提示 | TypeScript |

### 优势提升
1. **更好的开发体验** - 热重载、类型检查、组件复用
2. **统一的设计系统** - Chakra UI 提供一致的视觉语言
3. **更容易维护** - 函数式组件、Hooks、模块化架构
4. **更好的性能** - 虚拟 DOM、按需渲染
5. **跨平台兼容** - Web 标准，无需安装

## 🔮 后续计划

- [ ] 集成后端 API 接口
- [ ] 实现真实的图片转换功能
- [ ] 添加图床配置界面
- [ ] 实现文件拖拽上传
- [ ] 添加预览功能
- [ ] 优化移动端体验
- [ ] 添加快捷键支持
- [ ] 实现离线功能 (PWA)

## 🤝 贡献指南

1. Fork 项目
2. 创建特性分支 (`git checkout -b feature/AmazingFeature`)
3. 提交更改 (`git commit -m 'Add some AmazingFeature'`)
4. 推送到分支 (`git push origin feature/AmazingFeature`)
5. 创建 Pull Request

## 📄 许可证

MIT License - 详见 [LICENSE](../LICENSE) 文件