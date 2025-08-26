## <img src="image/logo.png" width="32" height="32" alt="Meowdown Logo" style="vertical-align: middle;"> Meowdown · MdImgConverter

把 Markdown 里的图片一键变身 WebP，还能自动上传到图床！(=^･ω･^=)✧

![Preview](image/preview.png)

---

## 💫 特性
- 🐾 一键转换：自动识别 Markdown 图片并输出 WebP
- 🎚️ 质量可调：滑杆控制画质/体积平衡
- 🔗 路径回写：`images/*.webp` 或外链 URL 智能替换
- ☁️ 图床上传：支持阿里云 OSS、腾讯云 COS、七牛云、S3 兼容、GitHub 等多种图床
- 🪄 轻量界面：Win11 风格 UI，简洁可爱

---

## 🚀 快速上手
- 前往仓库的 Releases 页面，下载与你系统匹配的版本（推荐 onedir 目录版）
- Windows（onedir）：解压后运行 `dist/MdImgConverter/MdImgConverter.exe`
- Windows（onefile）：下载 `MdImgConverter.exe` 直接双击运行
- 首次运行若被 SmartScreen 拦截，点击“更多信息”→“仍要运行”
- 想用源码运行？见 `coder-README.md`

---

## 🎯 使用方法
1. 粘贴或打开 Markdown
2. 右侧调质量（默认 73% 很香）
3. 点「转换」→ 输出到 `images/`
4. 需要外链？在「图床设置」保存凭据再点「上传」

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

## 📝 License
MIT. 欢迎二次开发与同人创作（记得保留署名喵）。

---

想看技术细节、打包命令、接口扩展？请移步 `coder-README.md`。
