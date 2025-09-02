# <img src="meowdown-web/public/maoer.png" width="39" height="39" alt="Meowdown Logo" style="vertical-align: middle;">   Meowdown · MdImgConverter

把 Markdown 里的图片一键变身 WebP，还能自动上传到图床！(=^･ω･^=)✧

![Preview](icons/image/previewStory1.jpg)

## 🤔 这是什么？
Meowdown 是一个帮你“喂”好 Markdown 里所有图片的小助手。

它会溜进你的文章里，抓取所有本地图片，把它们变成更小、加载更快的 WebP 格式，然后“咻”地一下上传到你自己的图床，最后再乖乖地把链接给你换回来。

整个过程，你只需要点一下按钮。

## 💡 为什么需要一只 Meowdown？

### 告别图床的“压缩盲盒”，画质你说了算！
> “我的图床也带 WebP 压缩，干嘛要用你？”

听起来不错，但效果真的好吗？很多图床的压缩是个“黑盒”，要么压得太狠，图片糊成一片；要么根本没使劲，体积还是那么大。

Meowdown 把控制权交给你！拖动一下滑杆，就能亲眼看着图片在**画质和体积间找到完美平衡点**。又快又清晰，这才是我们想要的！✨

### 从“体力活”到“一键流”，把时间还给写作
> “我用在线工具批量压一下不也一样？”

想想你以前是怎么做的：写完文章，把图片一张张拖到压缩工具，再一张张上传到图床，最后再一个个复制链接粘回来……天啊，光是想想就累了！😫

现在，你只需要专注于写作，图片随便拖。写完后，把文章交给 Meowdown，按下那个神奇的按钮，它会帮你**搞定后续所有事**。这才是真正的自动化，不是吗？

**简单说：Meowdown 消灭了所有手动处理图片的繁琐步骤，让你专心写出好内容。**

---

## 💫 特性

### 🌟 核心功能
- 🐾 **一键转换**：自动识别 Markdown 图片并输出 WebP 格式
- 🎚️ **质量可调**：滑杆控制画质/体积平衡，默认 73% 最优
- 🔗 **路径回写**：`images/*.webp` 或外链 URL 智能替换
- ☁️ **图床上传**：支持阿里云 OSS、腾讯云 COS、七牛云、S3、GitHub 等多种图床

### 🚀 应用版本
- 🖥️ **桌面版**：基于 Tauri 构建，体积小巧、性能优秀、原生体验
- 🌐 **Web 版**：现代化 React + Chakra UI，支持在线使用
- 🪄 **简洁界面**：删除了调试和后端设置按钮，专注核心功能

---

## 🚀 快速上手

### 🖥️ 桌面版应用（推荐）
- 前往仓库的 Releases 页面，下载最新的桌面版本：
  - 📦 **MSI 安装包**：`Meowdown_0.1.0_x64_en-US.msi` - 标准 Windows 安装程序
  - 🚀 **便携版**：`Meowdown_0.1.0_x64-setup.exe` - 免安装直接运行
- 首次运行若被 SmartScreen 拦截，点击"更多信息"→"仍要运行"
- 基于 Tauri 构建，体积小巧、性能优秀！✨

### 🌐 Web 版应用
- 在线体验：访问部署的 Web 版本
- 需要配合后端服务：`python meowdown-backend/main.py`
- 适合服务器部署或本地开发使用

### 👨‍💻 开发者版本
- 想用源码运行？见 `Read.md/coder-README.md`
- 桌面版开发：`cd desktop && npm run tauri dev`
- Web 版开发：`cd meowdown-web && npm run dev`

---

## 🎯 使用方法

### 🖥️ 桌面版使用
1. 📝 **输入内容**：粘贴或拖拽 Markdown 文件到编辑器
2. 🎚️ **调节质量**：右侧滑杆调整压缩质量（默认 73% 很香）
3. 🔄 **开始转换**：点击「开始转换」按钮
4. ☁️ **上传图床**：需要外链？点击「设置」配置图床后自动上传
5. 💾 **保存结果**：转换完成后保存新的 Markdown 文件

### 🌐 Web 版使用
1. 🚀 启动后端：`python meowdown-backend/main.py`
2. 🌐 打开 Web 界面（通常是 `http://localhost:8000`）
3. 📝 在左侧编辑器输入 Markdown 内容
4. 🎛️ 右侧调节参数并点击转换
5. 📥 下载转换后的文件

---

## 🧰 支持的图床服务

### 📡 阿里云 OSS
**配置参数：**
- **Access Key ID** 和 **Access Key Secret**：阿里云账户密钥
- **Bucket**：存储桶名称
- **Endpoint**：如 `oss-cn-beijing`（自动补全协议和域名）
- **自定义域名**：可选，绑定的 CDN 域名
- **存储路径前缀**：可选，如 `images/` 在桶内创建目录结构

**URL 格式：** `https://bucket.oss-cn-beijing.aliyuncs.com/path/file.webp`

### 🌪️ 腾讯云 COS
**配置参数：**
- **Secret ID** 和 **Secret Key**：腾讯云账户密钥
- **Bucket**：存储桶名称（格式：`bucket-appid`）
- **Region**：地域，如 `ap-beijing`
- **自定义域名**：可选，绑定的 CDN 域名
- **存储路径前缀**：可选，目录前缀

**URL 格式：** `https://bucket-appid.cos.ap-beijing.myqcloud.com/path/file.webp`

### 🦄 七牛云 Kodo
**配置参数：**
- **Access Key** 和 **Secret Key**：七牛云账户密钥
- **Bucket**：存储空间名称
- **域名**：绑定的访问域名（必填）
- **存储路径前缀**：可选，目录前缀

**URL 格式：** `https://your-domain.com/path/file.webp`

### 🪣 S3 兼容存储
**支持服务：** AWS S3、MinIO、阿里云 OSS S3 API、腾讯云 COS S3 API 等
**配置参数：**
- **Access Key** 和 **Secret Key**：S3 访问密钥
- **Bucket**：存储桶名称
- **Region**：区域，如 `us-east-1`
- **Endpoint**：可选，自定义端点（如 MinIO 服务器地址）
- **自定义域名**：可选，CDN 域名
- **存储路径前缀**：可选，目录前缀
- **路径样式**：可选，启用路径样式访问

**URL 格式：** `https://s3.region.amazonaws.com/bucket/path/file.webp`

### 🐙 GitHub 仓库
**配置参数：**
- **Personal Access Token**：GitHub 个人访问令牌（需要 repo 权限）
- **仓库所有者**：GitHub 用户名或组织名
- **仓库名称**：存储图片的仓库名
- **分支**：目标分支，如 `main` 或 `master`
- **仓库路径前缀**：可选，如 `images/` 在仓库内创建目录
- **自定义域名**：可选，自定义域名访问
- **使用 jsDelivr CDN**：可选，通过 CDN 加速访问

**URL 格式：** 
- GitHub 直链：`https://raw.githubusercontent.com/user/repo/branch/path/file.webp`
- jsDelivr CDN：`https://cdn.jsdelivr.net/gh/user/repo@branch/path/file.webp`

## 🔧 配置小贴士
- **阿里云 OSS Endpoint**：`oss-cn-beijing` → 自动变 `https://oss-cn-beijing.aliyuncs.com`
- **URL 协议**：所有服务都支持 HTTPS（推荐）和 HTTP
- **清空配置**：在图床设置对话框中点击「清空」按钮
- **测试上传**：配置完成后可点击「测试上传」验证配置是否正确

---

## 🧭 下一步开发
- ✅ **界面优化**：已删除调试和后端设置按钮，界面更简洁
- ✅ **桌面版本**：基于 Tauri 的现代桌面应用已完成
- ✅ **Web 版本**：现代化 React + Chakra UI 界面
- 🔄 **增加少量用户界面动画**
- 🔄 **增加其他压缩格式支持**（AVIF、JPEG XL）
- 🔄 **增加 Markdown 文件渲染预览功能**
- 🔄 **多语言支持**（英文、日文）
- 🔄 **批量处理模式**

---

## 📝 License
MIT. 欢迎二次开发与同人创作（记得保留署名喵）。

---

## 📚 文档导航

### 🎯 用户文档
- **[README.md](README.md)** - 项目主页，快速上手指南
- **[Read.md/BUILD_GUIDE.md](Read.md/BUILD_GUIDE.md)** - 详细的构建和打包指南
- **[Read.md/PACKAGING_COMPARISON.md](Read.md/PACKAGING_COMPARISON.md)** - 打包配置对比分析

### 🔧 开发者文档
- **[Read.md/coder-README.md](Read.md/coder-README.md)** - 技术文档，开发环境设置
- **[Read.md/coder-picgo-README.md](Read.md/coder-picgo-README.md)** - 图床扩展开发指南
- **[Read.md/imd-README.md](Read.md/imd-README.md)** - imarkdown 核心库详细文档
- **[Read.md/imd-README_zh.md](Read.md/imd-README_zh.md)** - imarkdown 中文版文档

### 🎨 设计资源
- **[Read.md/ICON_MANIFEST.md](Read.md/ICON_MANIFEST.md)** - 图标使用清单和配置说明
- **[icons/README.md](icons/README.md)** - 多平台图标包详细说明

### 📊 项目管理
- **[Read.md/meum-README.md](Read.md/meum-README.md)** - 完整项目目录结构说明
- **[Read.md/DOCS_INDEX.md](Read.md/DOCS_INDEX.md)** - 文档索引和导航

### 🧪 测试文档
- **[md-converter-gui/test_images.md](md-converter-gui/test_images.md)** - GUI测试用例

---

**快速导航：**
- 🚀 想快速使用？看 [README.md](README.md) 
- 🔧 想开发扩展？看 [Read.md/coder-README.md](Read.md/coder-README.md)
- 📦 想自己打包？看 [Read.md/BUILD_GUIDE.md](Read.md/BUILD_GUIDE.md)
- 🎨 想了解图标？看 [Read.md/ICON_MANIFEST.md](Read.md/ICON_MANIFEST.md)
- 📁 想了解结构？看 [Read.md/meum-README.md](Read.md/meum-README.md)
