## ✨ Meowdown · MdImgConverter

把 Markdown 里的图片一键变身 WebP，还能自动上传到图床！(=^･ω･^=)✧

![Preview](image/lightbulb-solid-full.svg)

---

## 💫 特性
- 🐾 一键转换：自动识别 Markdown 图片并输出 WebP
- 🎚️ 质量可调：滑杆控制画质/体积平衡
- 🔗 路径回写：`images/*.webp` 或外链 URL 智能替换
- ☁️ 图床上传：内置阿里云 OSS（可扩展其它图床）
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

## 🧰 图床 Endpoint 小贴士
- `oss-cn-beijing` → 自动变 `https://oss-cn-beijing.aliyuncs.com`
- `oss-cn-beijing.aliyuncs.com` → 自动补 `https://`
- `https://oss-cn-beijing.aliyuncs.com` → 原样
- `@https://oss-cn-beijing.aliyuncs.com` → 原样（强制按你写的用）
- 想清空本地保存？点弹窗里的「清空」即可

---

## 📝 License
MIT. 欢迎二次开发与同人创作（记得保留署名喵）。

---

想看技术细节、打包命令、接口扩展？请移步 `coder-README.md`。
