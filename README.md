### markdwon图片压缩

> 基于开源项目 `imarkdown` 二次开发的 Markdown 图片优化工具。支持将 Markdown 文本中的图片链接一键转换为 WebP 并回写到原文，提供现代化图形界面、压缩质量调节和图床绑定能力。项目承诺永久免费开源。

---

### 主要特性
- **一键替换为 WebP**: 自动识别 Markdown 中的 `![]()` 与 `<img src="">` 图片链接，将 `.png/.jpg/.jpeg/...` 转换并替换为 `.webp`，并将新地址写回 Markdown 文本。
- **可视化界面**: 提供桌面 GUI（Win11 风格），所见即所得，一键转换。
- **压缩质量可调**: 质量范围 1-100，内置“无损/高质量/标准/压缩/极压缩”等预设，平衡画质与体积。
- **图床绑定**: 支持将转换后的 `.webp` 自动上传到自定义图床，并回写为图床 URL（支持自定义适配器，示例见下文）。
- **批量与统计**: 支持批量处理 Markdown 中的所有图片，提供原始大小、压缩后大小、节省空间、压缩比例等统计信息。
- **免费开源**: 项目名称为“markdwon图片压缩”，永久免费开源。

---

### 运行环境
- **系统**: Windows 10 / Windows 11（测试阶段，仅在中文环境验证）
- **Python**: 建议 Python 3.8+（桌面端使用 PyQt6）

> 注意：当前处于测试阶段，仅保证在 Win10/Win11 中文环境下的基本可用性。

---

### 安装与启动（GUI）
1. 克隆仓库后进入项目根目录。
2. 安装依赖：
   - 基础依赖：
     ```bash
     pip install -r requirements.txt
     ```
   - GUI 与图像处理依赖（若未包含于你的环境）：
     ```bash
     pip install PyQt6 Pillow
     ```
3. 启动桌面应用：
   ```bash
   python md-converter-gui/main.py
   ```

启动后你将看到左侧 Markdown 编辑器 + 右侧控制面板：
- 粘贴或输入 Markdown 文本，点击“转换”。
- 根据需要拖动“图片质量”滑块或选择预设。
- 转换完成后，新的 `.webp` 路径会被自动回写到编辑器中的 Markdown。
- 生成的图片默认保存在当前目录下的 `images/` 中。

### 代码结构（已模块化）
```text
md-converter-gui/
  core/                    # 转换核心（下载→WebP→回写）
  uploader/                # 图床适配与管理器（Aliyun 示例）
  ui/
    components/            # 复用组件（编辑器、右侧面板）
    dialogs/               # 对话框（图床设置）
    themes/                # 深/浅色 tokens
    workers.py             # ConversionWorker / UploadWorker（后台线程）
    win11_design.py        # 主窗口与布局（仅保留主逻辑）
```

### 当前状态与稳定化计划
- 项目进入“稳定化梳理”阶段，目标是先跑通主流程、再逐步完善。
- 已实现：
  - 外链图片“下载→本地 WebP→Markdown 回写”。
  - 异步上传基础设施（UploadWorker + Aliyun 示例适配/配置持久化）。
  - Win11 风格 UI、深/浅色 tokens、右侧质量与进度显示。
- 主要阻断（启动时报错多与缩进/残留旧代码有关）：
  - `win11_design.py` 的 `apply_theme` 深色分支缩进需完全归位到 `if dark:` 内。
  - 已迁移的组件/对话框在 `win11_design.py` 内的旧定义需彻底移除，仅保留导入。
- 稳定化待办（验收顺序）：
  1) 修复 `apply_theme` 深色分支缩进与样式套用。
  2) 清除 `win11_design.py` 中已迁移的组件/对话框类定义。
  3) 统一导入：从 `components/`、`dialogs/`、`themes/`、`workers` 导入并通过。
  4) 启动烟测：应用能无异常进入主界面。
  5) 转换验证：远程图片下载→本地 WebP→编辑器回写。
  6) 上传验证：UploadWorker 异步上传并回写外链（阿里云）。
  7) 主题样式一致性：深/浅色、状态栏、分割线、按钮。

### 用户验证清单（建议按此顺序）
1. 打开应用能正常进入主界面，无报错。
2. 粘贴含 http(s) 图片链接的 Markdown，点击“转换”后：
   - `images/` 目录出现 `.webp` 文件；
   - 编辑器内的图片链接回写为相对路径 `images/xxx.webp`。
3. 打开“图床设置”，填写阿里云 OSS 凭据，保存；勾选“启用转换后自动上传”。
4. 再次“转换”，状态栏看到上传进度；编辑器内回写为外链 URL。
5. 浅色/深色主题下控件样式、分割线、状态栏与按钮可读性良好。

---

### 使用方法（脚本/二次开发）
如需在你自己的脚本中复用核心能力，可直接调用核心方法：

```python
# 示例：在脚本中将 Markdown 文本中的所有图片转换为 WebP 并回写
import os
import sys
from pathlib import Path

# 将 core 模块加入路径
core_dir = Path(__file__).parent / 'md-converter-gui' / 'core'
sys.path.insert(0, str(core_dir.parent))  # 允许 from core.xxx 导入

from core.image_converter import convert_markdown_images

markdown_text = """
# 示例
![示例](https://example.com/a.png)
<img src="https://example.com/b.jpg" />
"""

new_md, count, stats = convert_markdown_images(
    markdown_text,
    output_dir="images",   # 输出目录
    quality=80              # 压缩质量 1-100
)

print(new_md)  # 含回写后的 .webp 路径
print(count, stats)
```

核心方法说明：
- `convert_markdown_images(markdown_text: str, output_dir: str = "images", quality: int = 80, progress_callback: Optional[Callable[[int, str], None]] = None)`
  - 返回值：`(new_markdown: str, success_count: int, compression_stats: dict)`。
  - 自动处理本地与网络图片；网络图片会先下载再转换。

---

### 图床绑定（当前实现与扩展）
GUI 已具备“转换完成→后台上传→回写外链”的基础流程，现阶段优先支持阿里云 OSS：
- 在“图床设置”填写 endpoint/bucket/AK/SK 并保存；可选择“启用转换后自动上传”。
- 转换完成后由 UploadWorker 异步上传，状态栏显示进度，成功后编辑器回写外链 URL。

你也可以按适配器模式扩展更多图床：
- 方式一：沿用 `imarkdown` 适配器机制（如阿里云 OSS）。
- 方式二：自定义适配器（伪示例）：

```python
# 伪代码示例：自定义图床上传（可参考 example/custom_adapter.py 与 imd-README.md 中的示例）
class MyImageBedAdapter:
    def upload(self, local_webp_path: str) -> str:
        # 将本地 .webp 上传到你的图床
        # 返回图床上的可访问 URL
        ...

# 在转换完每张图片后，调用 adapter.upload(webp_path)，再把返回的 URL 写回 Markdown。
```

> 说明：图床上传在 GUI 中已可用（阿里云示例），其他图床按适配器扩展即可。

---

### 与上游项目的关系
- 本项目基于 `imarkdown` 改造：保留其“元素识别/适配器扩展”等优势，同时聚焦于“图像转 WebP + GUI + 图床绑定”。
- 原项目说明可见 `imd-README.md` / `imd-README_zh.md`。

---

### 兼容性与限制
- 仅保证在 **Windows 10 / 11 中文环境** 的基本可用性（测试阶段）。
- 当前主要支持替换以下形式的图片：`![]()` 与 `<img src="">`。
- 远程图片需可直接访问；网络不通或受防盗链限制的链接可能无法下载。
- WebP 转换依赖 `Pillow`；请确保已安装并可用。
- 路径统一使用正斜杠 `/`（Windows 下自动归一化）。

---

### 路线图（Roadmap）
- 集成 GUI 端图床配置与一键上传。
- 批量文件/文件夹处理（GUI）。
- 更多图床适配（如腾讯云、七牛等）。
- 拖拽导入与导出、历史记录与回退。
- 命令行模式与自动化管线支持。

---

### 许可证与致谢
- **许可证**: MIT（见仓库根目录 `license`）。
- **致谢**: 感谢上游开源项目 `imarkdown` 的出色设计与实现。
- **承诺**: “markdwon图片压缩” 将 **永远免费开源**，欢迎 Star、Issue 与 PR。

---

### 反馈与贡献
- 遇到问题或想法建议：请提交 Issue。
- 欢迎 PR 参与共建（UI/交互、稳定性、图床适配器、新特性）。
