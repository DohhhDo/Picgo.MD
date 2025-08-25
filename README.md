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

### 图床绑定（自定义适配器）
项目内置对“自定义图床”模式的支持：你可以实现一个适配器来完成上传逻辑，并在转换完成后将 `.webp` 上传到你的图床，返回图床 URL 并回写到 Markdown。

- 方式一：参考 `imarkdown` 的适配器机制（如阿里云 OSS）。示例可见仓库 `example/aliyun_oss_usage.py`。
- 方式二：自定义适配器。示意代码（伪示例）：

```python
# 伪代码示例：自定义图床上传（可参考 example/custom_adapter.py 与 imd-README.md 中的示例）
class MyImageBedAdapter:
    def upload(self, local_webp_path: str) -> str:
        # 将本地 .webp 上传到你的图床
        # 返回图床上的可访问 URL
        ...

# 在转换完每张图片后，调用 adapter.upload(webp_path)，
# 并把返回的 URL 写回 Markdown（替换本地 images/xxx.webp）。
```

> 说明：当前 GUI 侧已具备转换与回写能力；图床绑定能力已具备适配器示例与基础设施，后续将把“图床配置与上传流程”集成到 GUI 中，提供可视化设置。

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
