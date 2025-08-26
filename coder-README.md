### markdwon图片压缩（技术文档）

> 基于开源项目 `imarkdown` 二次开发的 Markdown 图片优化工具。提供 GUI、批量转换、图床上传与可扩展的适配器机制。本文件面向开发者与贡献者。

---

### 运行环境
- Windows 10 / 11（首测平台）
- Python 3.8+
- 主要依赖：PyQt6、Pillow、oss2

---

### 安装与启动
```bash
pip install -r requirements.txt
python md-converter-gui/main.py
```

---

### 代码结构
```text
md-converter-gui/
  core/                    # 转换核心（下载→WebP→回写）
  uploader/                # 图床适配（Aliyun 示例）
  ui/
    components/            # 编辑器与控制面板
    dialogs/               # 图床设置弹窗
    themes/                # 主题 tokens
    workers.py             # ConversionWorker / UploadWorker
    win11_design.py        # 主窗口
```

---

### 关键逻辑
- 图片解析与替换：`core/image_converter.py`
- 阿里云上传：`md-converter-gui/uploader/ali_oss_adapter.py`
- 图床设置缓存：`QSettings("MdImgConverter","Settings")`
- Endpoint 规范化规则：
  - `oss-cn-xxx` → `https://oss-cn-xxx.aliyuncs.com`
  - 含 `aliyuncs.com` 无协议 → 自动补 `https://`
  - 以 `@` 开头 → 原样使用（不再拼接）

---

### 打包（Windows onedir）
```powershell
pyinstaller -w -n MdImgConverter --clean --noconfirm --icon pictures/Meowdown.ico `
  --add-data "pictures;pictures" `
  --add-data "image;image" `
  --add-data "imarkdown;imarkdown" `
  md-converter-gui\main.py
```

可选：onefile 需注意 `sys._MEIPASS` 的资源路径处理。

---

### 二次开发（核心调用示例）
```python
from core.image_converter import convert_markdown_images

new_md, count, stats = convert_markdown_images(
    markdown_text,
    output_dir="images",
    quality=80,
)
```

---

### 兼容性与限制
- 以 Win10/11 中文环境为主测试面。
- 远程图片需要可直连；受防盗链限制的链接需自行处理头部。

---

### 许可证与贡献
- License: MIT（根目录 `license`）
- 欢迎提交 Issues / PR，共建更稳定的 GUI 体验与更多图床适配。


