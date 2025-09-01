# 🎨 图标使用清单

## 主要图标文件

### Windows 应用程序
- `pictures/app_icon.ico` - 主应用程序图标 (多尺寸)
- `pictures/app_icon_256.png` - 256x256 PNG 格式

### GUI 应用程序  
- `md-converter-gui/icon.ico` - GUI 程序图标
- `md-converter-gui/icon.png` - GUI 程序 PNG 图标

### Web 应用程序
- `icons/image/favicon.png` - 网站图标 (32x32)
- `icons/image/app-icon-192.png` - PWA 图标 (192x192)
- `icons/image/logo.png` - 通用 Logo (128x128)

### 移动应用程序
- `icons/android/` - Android 各 DPI 图标
- `icons/ios/` - iOS 各尺寸图标

## 完整图标包
所有尺寸和格式的图标都在 `icons/` 目录中，按平台分类：
- `icons/windows/` - Windows PNG 图标
- `icons/macos/` - macOS PNG 图标  
- `icons/linux/` - Linux PNG 图标
- `icons/web/` - Web PNG 图标
- `icons/android/` - Android PNG 图标
- `icons/ios/` - iOS PNG 图标
- `icons/app_icon.ico` - Windows ICO 文件

## 构建配置

### PyInstaller
```python
# 在 .spec 文件中使用
icon='pictures/app_icon.ico'
```

### Electron
```json
{
  "build": {
    "win": {
      "icon": "pictures/app_icon.ico"
    },
    "mac": {
      "icon": "icons/temp_iconset/"  
    },
    "linux": {
      "icon": "icons/linux/"
    }
  }
}
```

### Web Manifest
```json
{
  "icons": [
    {
      "src": "icons/image/app-icon-192.png",
      "sizes": "192x192",
      "type": "image/png"
    }
  ]
}
```
