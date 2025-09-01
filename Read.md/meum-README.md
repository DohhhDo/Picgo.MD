# 📁 MdImgConverter 项目目录结构

本文档详细介绍了 MdImgConverter 项目的完整目录结构和各文件的功能说明。

## 🌟 项目概览

MdImgConverter 是一个功能强大的 Markdown 图片转换工具，支持多种云存储平台，提供桌面GUI界面和命令行接口。

## 📂 目录结构

```
md-webP/  （已简化的项目结构）
├── 📁 .github/                        # GitHub配置
│   ├── 📁 ISSUE_TEMPLATE/             # Issue模板
│   └── 📁 workflows/                  # GitHub Actions工作流
│       ├── 📄 build.yml              # 构建和测试工作流
│       └── 📄 python-publish.yml     # 发布工作流
├── 📁 icons/                          # 应用图标资源
│   ├── 📁 android/                    # Android平台图标
│   ├── 📁 ios/                        # iOS平台图标
│   ├── 📁 linux/                      # Linux平台图标
│   ├── 📁 macos/                      # macOS平台图标
│   ├── 📁 web/                        # Web平台图标
│   ├── 📁 windows/                    # Windows平台图标
│   ├── 📁 temp_iconset/               # 临时图标集
│   ├── 📄 app_icon.ico               # 主应用图标
│   └── 📄 README.md                  # 图标使用说明
├── 📁 image/                          # 项目图像资源
│   ├── 🖼️ app-icon-192.png           # 应用图标(192x192)
│   ├── 🖼️ favicon.png                # 网站图标
│   ├── 🖼️ logo.png                   # 项目Logo
│   ├── 🖼️ logo-A.png                 # Logo变体A
│   ├── 🖼️ logo-Dev.png               # 开发版Logo
│   ├── 🖼️ preview.png                # 预览图
│   └── 🎨 *.svg                      # SVG矢量图标
├── 📁 images/                         # 额外图像目录
├── 📁 imarkdown/                      # 核心转换库
│   ├── 📄 __init__.py                # 包初始化文件
│   ├── 📁 adapter/                    # 存储适配器
│   │   ├── 📄 aliyun_oss.py          # 阿里云OSS适配器
│   │   ├── 📄 base.py                # 基础适配器类
│   │   ├── 📄 cos.py                 # 腾讯云COS适配器
│   │   ├── 📄 github.py              # GitHub适配器
│   │   ├── 📄 local.py               # 本地存储适配器
│   │   ├── 📄 qiniu.py               # 七牛云适配器
│   │   ├── 📄 s3.py                  # AWS S3适配器
│   │   └── 📄 __init__.py            # 适配器包初始化
│   ├── 📁 client/                     # 客户端模块
│   │   └── 📄 __init__.py            # 客户端初始化
│   ├── 📁 utils/                      # 工具函数
│   │   ├── 📄 file.py                # 文件操作工具
│   │   ├── 📄 image.py               # 图像处理工具
│   │   └── 📄 url.py                 # URL处理工具
│   ├── 📄 config.py                  # 配置管理
│   ├── 📄 constant.py                # 常量定义
│   ├── 📄 converter.py               # 核心转换器
│   └── 📄 schema.py                  # 数据模式定义
├── 📁 md-converter-gui/               # 桌面GUI应用
│   ├── 📁 core/                       # 核心业务逻辑
│   │   ├── 📄 config.py              # GUI配置管理
│   │   └── 📄 converter.py           # GUI转换器
│   ├── 📁 images/                     # GUI图像资源
│   ├── 📁 ui/                         # 用户界面模块
│   │   ├── 📄 about_dialog.py        # 关于对话框
│   │   ├── 📄 base_window.py         # 基础窗口类
│   │   ├── 📄 config_dialog.py       # 配置对话框
│   │   ├── 📄 drag_drop_widget.py    # 拖拽组件
│   │   ├── 📄 help_dialog.py         # 帮助对话框
│   │   ├── 📄 log_dialog.py          # 日志对话框
│   │   ├── 📄 progress_dialog.py     # 进度对话框
│   │   ├── 📄 settings_dialog.py     # 设置对话框
│   │   ├── 📄 style_manager.py       # 样式管理器
│   │   └── 📄 win11_design.py        # Windows 11风格设计
│   ├── 📁 uploader/                   # 上传器模块
│   │   ├── 📄 aliyun_uploader.py     # 阿里云上传器
│   │   ├── 📄 base_uploader.py       # 基础上传器
│   │   ├── 📄 cos_uploader.py        # 腾讯云上传器
│   │   ├── 📄 github_uploader.py     # GitHub上传器
│   │   ├── 📄 qiniu_uploader.py      # 七牛云上传器
│   │   └── 📄 s3_uploader.py         # S3上传器
│   ├── 📄 icon.ico                   # GUI应用图标
│   ├── 📄 icon.png                   # GUI应用PNG图标
│   ├── 📄 main.py                    # GUI应用入口
│   ├── 📄 test_environment.py        # 环境测试脚本
│   └── 📄 test_images.md             # 图像测试文档
├── 📁 picgo/                          # PicGo相关代码
│   ├── 📁 docs/                       # 文档目录
│   ├── 📁 public/                     # 公共资源
│   ├── 📁 scripts/                    # 构建脚本
│   ├── 📁 src/                        # 源代码
│   ├── 📁 test/                       # 测试文件
│   ├── 📄 package.json               # Node.js依赖配置
│   ├── 📄 README.md                  # PicGo说明文档
│   └── 📄 *.config.js                # 各种配置文件
├── 📁 pictures/                       # 应用图片资源
│   ├── 🖼️ app_icon_256.png           # 256x256应用图标
│   ├── 📄 app_icon.ico               # Windows图标文件
│   ├── 🖼️ Meowdown.ico               # Meowdown图标
│   └── 🖼️ Meowdown*.png              # Meowdown相关图片
├── 📁 tests/                          # 测试文件目录
│   ├── 📁 mds/                        # Markdown测试文件
│   ├── 📁 single_mds/                 # 单个Markdown测试
│   ├── 📄 test_*.py                  # Python测试文件
│   └── 📄 test.md                    # 测试用Markdown
├── 📁 upx-5.0.2-win64/               # UPX压缩工具
├── 📁 winui3-app/                     # WinUI3应用(C#版本)
│   ├── 📁 Assets/                     # 资源文件
│   ├── 📁 bin/                        # 编译输出
│   ├── 📁 obj/                        # 编译对象文件
│   ├── 📄 *.xaml                     # XAML界面文件
│   ├── 📄 *.cs                       # C#源代码
│   └── 📄 *.csproj                   # 项目文件
├── 📄 BUILD_GUIDE.md                 # 📖 构建指南(详细打包说明)
├── 📄 PACKAGING_COMPARISON.md        # 📊 打包配置对比文档
├── 📄 meum-README.md                 # 📁 本文件(项目目录说明)
├── 📄 build_optimized.bat            # 🔨 Windows优化构建脚本
├── 📄 build_optimized.sh             # 🔨 Linux/macOS优化构建脚本
├── 📄 MdImgConverter.spec            # ⚙️ PyInstaller标准配置
├── 📄 MdImgConverter-small.spec      # ⚙️ PyInstaller小体积配置
├── 📄 MdImgConverter-optimized.spec  # ⚙️ PyInstaller优化配置
├── 📄 copy_icons.py                  # 🎨 图标复制脚本
├── 📄 create_icons.py                # 🎨 图标生成脚本
├── 📄 pyproject.toml                 # 📦 Poetry项目配置
├── 📄 requirements.txt               # 📦 Python依赖列表
├── 📄 setup.py                       # 📦 Python安装脚本
├── 📄 poetry.lock                    # 🔒 Poetry依赖锁定文件
├── 📄 Makefile                       # 🔨 Make构建配置
├── 📄 sweep.yaml                     # 🧹 Sweep配置文件
├── 📄 test_integration.py            # 🧪 集成测试脚本
├── 📄 upx.exe                        # 📦 UPX压缩工具可执行文件
├── 📄 README.md                      # 📖 项目主说明文档
├── 📄 *-README*.md                   # 📖 各种说明文档
├── 📄 COPYING                        # ⚖️ 版权声明
├── 📄 LICENSE                        # ⚖️ 许可证文件
├── 📄 NEWS                           # 📰 更新日志
├── 📄 THANKS.txt                     # 🙏 致谢文件
├── 📄 ICON_MANIFEST.md               # 🎨 图标清单说明
├── 📄 图床扩展完成总结.md              # 📝 扩展开发总结
├── 🖼️ MEOW.png                       # 🐱 MEOW主题图标
├── 🖼️ Meowdown.png                   # 🐱 Meowdown图标
└── 📄 *.yml/*.yaml                   # ⚙️ 各种YAML配置文件
```

## 📋 文件分类说明

### 🏗️ 构建和打包
- **BUILD_GUIDE.md** - 详细的构建和打包指南
- **PACKAGING_COMPARISON.md** - 三种打包配置的对比分析
- **build_optimized.{bat,sh}** - 跨平台自动化构建脚本
- **MdImgConverter*.spec** - PyInstaller打包配置文件
- **Makefile** - Make构建配置

### 📦 依赖管理
- **pyproject.toml** - Poetry现代Python项目配置
- **requirements.txt** - 传统pip依赖列表
- **poetry.lock** - Poetry依赖版本锁定
- **setup.py** - Python包安装脚本

### 🎨 图标和资源
- **icons/** - 多平台图标资源集合
- **image/** - 项目图像和Logo资源
- **pictures/** - 应用程序图标文件
- **create_icons.py** - 自动化图标生成工具
- **copy_icons.py** - 图标部署脚本
- **ICON_MANIFEST.md** - 图标使用说明

### 💻 核心代码
- **imarkdown/** - 核心转换库，支持多种云存储
- **md-converter-gui/** - PyQt6桌面GUI应用
- **winui3-app/** - WinUI3版本(C#实现)
- **picgo/** - PicGo相关功能代码

### 📚 示例和测试
- **example/** - 各种云存储平台的使用示例
- **tests/** - 完整的测试套件
- **test_integration.py** - 集成测试脚本

### 📖 文档
- **README.md** - 项目主文档
- **meum-README.md** - 本文件(目录结构说明)
- **BUILD_GUIDE.md** - 构建指南
- **各种README文件** - 特定功能的说明文档

### 🔧 工具和配置
- **upx.exe** + **upx-5.0.2-win64/** - UPX压缩工具
- **sweep.yaml** - 代码清理配置
- **各种.yml/.yaml** - CI/CD和配置文件

## 🚀 快速开始

### 1. 环境准备
```bash
# 安装Python依赖
pip install -r requirements.txt
# 或使用Poetry
poetry install
```

### 2. 运行GUI应用
```bash
cd md-converter-gui
python main.py
```

### 3. 打包应用
```bash
# 使用优化版本(推荐)
.\build_optimized.bat          # Windows
./build_optimized.sh           # Linux/macOS

# 或手动打包
pyinstaller MdImgConverter-optimized.spec --clean
```

## 📊 项目统计

- **总文件数**: 200+ 文件
- **代码行数**: 10,000+ 行
- **支持平台**: Windows, Linux, macOS, Android, iOS
- **云存储支持**: 阿里云OSS, 腾讯云COS, 七牛云, AWS S3, GitHub
- **界面技术**: PyQt6, WinUI3
- **打包体积**: 60MB-150MB(根据配置)

## 🤝 贡献指南

1. 查看 **example/** 目录了解使用方法
2. 运行 **tests/** 中的测试确保功能正常
3. 参考 **BUILD_GUIDE.md** 进行构建
4. 使用 **PACKAGING_COMPARISON.md** 选择合适的打包方案

## 📄 许可证

本项目遵循多种开源许可证，详见 **COPYING** 和 **LICENSE** 文件。

---

*本文档自动生成于 2024年，如有更新请参考最新版本的项目结构*
