#!/usr/bin/env python3
"""
图标部署脚本 - 将生成的图标复制到项目的相应位置
"""

import os
import shutil
import argparse


def copy_file_safe(src: str, dst: str, create_dirs: bool = True) -> bool:
    """
    安全地复制文件

    Args:
        src: 源文件路径
        dst: 目标文件路径
        create_dirs: 是否创建目标目录

    Returns:
        复制是否成功
    """
    try:
        if create_dirs:
            os.makedirs(os.path.dirname(dst), exist_ok=True)

        shutil.copy2(src, dst)
        print(f"✅ {os.path.basename(src)} -> {dst}")
        return True
    except Exception as e:
        print(f"❌ 复制失败 {src} -> {dst}: {e}")
        return False


def deploy_icons():
    """部署图标到项目相应位置"""

    print("🚀 开始部署图标...")

    # 图标源目录
    icons_dir = "icons"

    # 部署映射
    deployments = [
        # Windows 应用程序
        {
            "src": f"{icons_dir}/app_icon.ico",
            "dst": "pictures/app_icon.ico",
            "desc": "Windows 应用程序主图标",
        },
        {
            "src": f"{icons_dir}/windows/icon_256x256.png",
            "dst": "pictures/app_icon_256.png",
            "desc": "Windows 大图标",
        },
        # GUI 应用程序图标
        {
            "src": f"{icons_dir}/windows/icon_64x64.png",
            "dst": "md-converter-gui/icon.png",
            "desc": "GUI 应用程序图标",
        },
        {
            "src": f"{icons_dir}/app_icon.ico",
            "dst": "md-converter-gui/icon.ico",
            "desc": "GUI 应用程序 ICO",
        },
        # Web 图标
        {
            "src": f"{icons_dir}/web/icon_32x32.png",
            "dst": "image/favicon.png",
            "desc": "网站 Favicon",
        },
        {
            "src": f"{icons_dir}/web/icon_192x192.png",
            "dst": "image/app-icon-192.png",
            "desc": "PWA 图标",
        },
        # 文档图标
        {
            "src": f"{icons_dir}/windows/icon_128x128.png",
            "dst": "image/logo.png",
            "desc": "文档用 Logo",
        },
        # 构建图标
        {
            "src": f"{icons_dir}/windows/icon_48x48.png",
            "dst": "winui3-app/Assets/app_icon.png",
            "desc": "WinUI3 应用图标",
        },
    ]

    # 执行部署
    success_count = 0
    total_count = len(deployments)

    for deployment in deployments:
        src = deployment["src"]
        dst = deployment["dst"]
        desc = deployment["desc"]

        print(f"\n📦 {desc}")

        if not os.path.exists(src):
            print(f"❌ 源文件不存在: {src}")
            continue

        if copy_file_safe(src, dst):
            success_count += 1

    print(f"\n🎉 部署完成！")
    print(f"📊 成功: {success_count}/{total_count}")

    # 显示使用建议
    print(f"\n💡 使用建议:")
    print(f"   • Windows 程序: 使用 pictures/app_icon.ico")
    print(f"   • GUI 应用: 使用 md-converter-gui/icon.ico")
    print(f"   • 网站: 使用 image/favicon.png")
    print(f"   • 文档: 使用 image/logo.png")


def create_icon_manifest():
    """创建图标清单文件"""

    manifest_content = """# 🎨 图标使用清单

## 主要图标文件

### Windows 应用程序
- `pictures/app_icon.ico` - 主应用程序图标 (多尺寸)
- `pictures/app_icon_256.png` - 256x256 PNG 格式

### GUI 应用程序  
- `md-converter-gui/icon.ico` - GUI 程序图标
- `md-converter-gui/icon.png` - GUI 程序 PNG 图标

### Web 应用程序
- `image/favicon.png` - 网站图标 (32x32)
- `image/app-icon-192.png` - PWA 图标 (192x192)
- `image/logo.png` - 通用 Logo (128x128)

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
      "src": "image/app-icon-192.png",
      "sizes": "192x192",
      "type": "image/png"
    }
  ]
}
```
"""

    with open("ICON_MANIFEST.md", "w", encoding="utf-8") as f:
        f.write(manifest_content)

    print("📝 已创建图标使用清单: ICON_MANIFEST.md")


def main():
    """主函数"""
    parser = argparse.ArgumentParser(description="图标部署脚本")
    parser.add_argument("--deploy", action="store_true", help="部署图标到项目位置")
    parser.add_argument("--manifest", action="store_true", help="创建图标使用清单")
    parser.add_argument("--all", action="store_true", help="执行所有操作")

    args = parser.parse_args()

    if args.all or (not args.deploy and not args.manifest):
        # 默认执行所有操作
        deploy_icons()
        print()
        create_icon_manifest()
    else:
        if args.deploy:
            deploy_icons()
        if args.manifest:
            create_icon_manifest()


if __name__ == "__main__":
    main()
