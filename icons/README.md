# 🎨 Meowdown 多尺寸图标包

基于 `MEOW.png` 生成的多平台软件图标包，包含各种尺寸和格式，适用于不同的使用场景。

## 📁 目录结构

```
icons/
├── app_icon.ico              # Windows ICO 文件 (多尺寸合集)
├── windows/                  # Windows 平台 PNG 图标
│   ├── icon_16x16.png       # 小图标
│   ├── icon_24x24.png       # 任务栏图标
│   ├── icon_32x32.png       # 标准图标
│   ├── icon_48x48.png       # 大图标
│   ├── icon_64x64.png       # 高清图标
│   ├── icon_128x128.png     # 超高清图标
│   ├── icon_256x256.png     # 特大图标
│   └── icon_512x512.png     # 超大图标
├── macos/                   # macOS 平台图标
│   ├── icon_16x16.png       # 菜单栏图标
│   ├── icon_32x32.png       # Finder 小图标
│   ├── icon_64x64.png       # Finder 中图标
│   ├── icon_128x128.png     # Finder 大图标
│   ├── icon_256x256.png     # Dock 图标
│   ├── icon_512x512.png     # 高清 Dock 图标
│   └── icon_1024x1024.png   # Retina 显示屏图标
├── linux/                  # Linux 平台图标
│   ├── icon_16x16.png       # 面板图标
│   ├── icon_22x22.png       # GNOME 小图标
│   ├── icon_24x24.png       # KDE 小图标
│   ├── icon_32x32.png       # 标准桌面图标
│   ├── icon_48x48.png       # 大桌面图标
│   ├── icon_64x64.png       # 高清桌面图标
│   ├── icon_128x128.png     # 应用程序图标
│   ├── icon_256x256.png     # 大应用程序图标
│   └── icon_512x512.png     # 超大应用程序图标
├── web/                     # Web 平台图标
│   ├── icon_16x16.png       # Favicon
│   ├── icon_32x32.png       # 标准 Favicon
│   ├── icon_48x48.png       # Chrome 扩展图标
│   ├── icon_96x96.png       # Android Chrome 图标
│   ├── icon_144x144.png     # Windows 磁贴图标
│   ├── icon_192x192.png     # Android 主屏图标
│   ├── icon_256x256.png     # 大网页图标
│   └── icon_512x512.png     # PWA 图标
├── android/                 # Android 平台图标
│   ├── icon_36x36.png       # ldpi (120dpi)
│   ├── icon_48x48.png       # mdpi (160dpi)
│   ├── icon_72x72.png       # hdpi (240dpi)
│   ├── icon_96x96.png       # xhdpi (320dpi)
│   ├── icon_144x144.png     # xxhdpi (480dpi)
│   ├── icon_192x192.png     # xxxhdpi (640dpi)
│   └── icon_512x512.png     # Play Store 图标
├── ios/                     # iOS 平台图标
│   ├── icon_29x29.png       # 设置图标
│   ├── icon_40x40.png       # Spotlight 搜索图标
│   ├── icon_58x58.png       # 设置图标 @2x
│   ├── icon_60x60.png       # iPhone 应用图标
│   ├── icon_76x76.png       # iPad 应用图标
│   ├── icon_80x80.png       # Spotlight 图标 @2x
│   ├── icon_87x87.png       # 设置图标 @3x
│   ├── icon_120x120.png     # iPhone 应用图标 @2x
│   ├── icon_152x152.png     # iPad 应用图标 @2x
│   ├── icon_167x167.png     # iPad Pro 应用图标
│   ├── icon_180x180.png     # iPhone 应用图标 @3x
│   └── icon_1024x1024.png   # App Store 图标
└── temp_iconset/            # macOS ICNS 生成用临时文件
    ├── icon_16x16.png
    ├── icon_32x32.png
    ├── icon_32x32@2x.png
    ├── icon_128x128.png
    ├── icon_256x256.png
    ├── icon_512x512.png
    └── icon_512x512@2x.png
```

## 🚀 使用指南

### Windows 应用程序
- **ICO 文件**: 使用 `app_icon.ico`，包含多个尺寸
- **单独 PNG**: 从 `windows/` 目录选择合适尺寸

### macOS 应用程序
- **ICNS 文件**: 使用 `temp_iconset/` 目录生成 ICNS
  ```bash
  iconutil -c icns temp_iconset/
  ```
- **单独 PNG**: 从 `macos/` 目录选择合适尺寸

### Linux 应用程序
- 使用 `linux/` 目录中的 PNG 文件
- 常用尺寸：16x16, 32x32, 48x48, 128x128

### Web 应用程序
- **Favicon**: 使用 `web/icon_16x16.png` 或 `web/icon_32x32.png`
- **PWA**: 使用 `web/icon_192x192.png` 和 `web/icon_512x512.png`
- **网站图标**: 根据需要选择合适尺寸

### 移动应用程序
- **Android**: 使用 `android/` 目录，根据 DPI 选择
- **iOS**: 使用 `ios/` 目录，根据设备类型选择

## 📝 文件命名规范

- **格式**: `icon_{宽度}x{高度}.png`
- **示例**: `icon_256x256.png`
- **Retina**: `icon_32x32@2x.png` (实际 64x64)

## 🔧 技术规格

- **源文件**: MEOW.png (256x256)
- **格式**: PNG (RGBA), ICO
- **质量**: 高质量重采样 (Lanczos)
- **透明度**: 支持 Alpha 通道
- **特殊处理**: Android/iOS 图标带圆角

## 💡 使用建议

1. **Windows**: 优先使用 ICO 文件，包含多尺寸
2. **macOS**: 生成 ICNS 文件或使用 PNG
3. **Linux**: 使用标准 PNG 格式
4. **Web**: 提供多个尺寸以适应不同设备
5. **移动**: 严格按照平台规范使用对应尺寸

## 🎨 图标特色

- 基于可爱的猫咪 MEOW 设计
- 保持原始设计风格
- 适配各平台设计规范
- 高质量缩放处理
- 完整的尺寸覆盖

---

*图标由 create_icons.py 自动生成 | 源文件: MEOW.png*
