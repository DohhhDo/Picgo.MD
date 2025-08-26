# 🚀 MdImgConverter 打包指南

使用新的 MEOW 图标重新打包应用程序的完整步骤。

## 📋 准备工作

### 1. 确认环境
```bash
# 检查 Python 版本
python --version  # 应该是 3.8+

# 检查 PyInstaller
pip show pyinstaller
# 如果没有安装：pip install pyinstaller
```

### 2. 确认图标文件
确保以下图标文件存在：
- ✅ `pictures/app_icon.ico` - 主应用程序图标
- ✅ `md-converter-gui/icon.ico` - GUI 程序图标  
- ✅ `image/logo.png` - 文档用图标

## 🔨 打包步骤

### 方法一：使用小体积版本（推荐）

```bash
# 1. 清理之前的构建
rmdir /s build dist 2>nul

# 2. 使用小体积配置打包
pyinstaller MdImgConverter-small.spec --clean

# 3. 检查输出
dir dist\MdImgConverter\
```

### 方法二：使用标准版本

```bash
# 1. 清理之前的构建  
rmdir /s build dist 2>nul

# 2. 使用标准配置打包
pyinstaller MdImgConverter.spec --clean

# 3. 检查输出
dir dist\MdImgConverter\
```

## 📁 输出结构

打包完成后，您会得到：
```
dist/
└── MdImgConverter/
    ├── MdImgConverter.exe  # 主程序（带新图标）
    ├── pictures/           # 图标资源
    │   └── app_icon.ico   # 新的应用图标
    ├── image/             # 图像资源
    │   └── logo.png       # Logo 图标
    └── [其他依赖文件...]
```

## 🎯 验证图标

### 1. 文件图标验证
- 在文件管理器中查看 `MdImgConverter.exe`
- 应该显示新的 MEOW 图标

### 2. 运行时图标验证
```bash
# 运行程序
cd dist\MdImgConverter
.\MdImgConverter.exe
```
- 任务栏应显示新图标
- 窗口左上角应显示新图标
- Alt+Tab 切换时应显示新图标

## ⚡ 优化选项

### 启用 UPX 压缩（已配置）
小体积版本已启用 UPX 压缩，可减小约 30-50% 的文件大小。

### 排除不需要的模块（已配置）
配置文件已排除：
- Qt 不需要的模块
- 科学计算库（numpy, scipy等）
- 开发工具（jupyter, pdb等）

## 🐛 常见问题

### 问题1：图标不显示
**解决方案：**
```bash
# 确认图标文件存在
dir pictures\app_icon.ico
# 重新生成图标（如果需要）
python create_icons.py MEOW.png -o icons
python copy_icons.py --deploy
```

### 问题2：缺少依赖
**解决方案：**
```bash
# 检查隐藏导入
pip install qcloud-cos qiniu boto3 pillow PyQt6
```

### 问题3：UPX 压缩失败
**解决方案：**
```bash
# 下载 UPX 到项目目录
# 或者禁用 UPX：在 spec 文件中设置 upx=False
```

## 📦 分发准备

### 1. 测试程序
```bash
# 在干净的 Windows 系统上测试
cd dist\MdImgConverter
.\MdImgConverter.exe
```

### 2. 创建安装包（可选）
可以使用 NSIS 或 Inno Setup 创建安装程序。

### 3. 数字签名（可选）
```bash
# 使用代码签名证书
signtool sign /f certificate.p12 /p password dist\MdImgConverter\MdImgConverter.exe
```

## 🎉 完成

现在您的应用程序已经：
- ✅ 使用新的 MEOW 图标
- ✅ 优化了文件大小
- ✅ 排除了不需要的依赖
- ✅ 准备好分发

---

*如需帮助，请参考 `ICON_MANIFEST.md` 了解图标使用详情*
