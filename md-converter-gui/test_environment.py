#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
测试开发环境是否正确配置
"""

import sys
import traceback

def test_imports():
    """测试必要的包是否能正常导入"""
    results = {}
    
    # 测试PyQt6
    try:
        from PyQt6.QtWidgets import QApplication, QMainWindow, QLabel
        from PyQt6.QtCore import Qt
        results['PyQt6'] = "✓ 成功"
    except ImportError as e:
        results['PyQt6'] = f"✗ 失败: {e}"
    
    # 测试Pillow
    try:
        from PIL import Image
        results['Pillow'] = "✓ 成功"
    except ImportError as e:
        results['Pillow'] = f"✗ 失败: {e}"
    
    # 测试requests
    try:
        import requests
        results['requests'] = "✓ 成功"
    except ImportError as e:
        results['requests'] = f"✗ 失败: {e}"
    
    return results

def test_simple_gui():
    """测试是否能创建简单的GUI窗口"""
    try:
        from PyQt6.QtWidgets import QApplication, QMainWindow, QLabel
        from PyQt6.QtCore import Qt
        
        app = QApplication([])
        window = QMainWindow()
        window.setWindowTitle("环境测试 - MdImgConverter")
        window.setGeometry(100, 100, 400, 300)
        
        label = QLabel("开发环境测试成功！\n点击关闭按钮退出", window)
        label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        label.setStyleSheet("""
            QLabel {
                font-size: 16px;
                color: #333;
                background-color: #f0f0f0;
                border: 2px solid #ccc;
                border-radius: 10px;
                padding: 20px;
            }
        """)
        
        window.setCentralWidget(label)
        window.show()
        
        print("GUI窗口已创建并显示，请查看是否正常显示")
        print("关闭窗口后程序将退出")
        
        app.exec()
        return True
        
    except Exception as e:
        print(f"GUI测试失败: {e}")
        traceback.print_exc()
        return False

def main():
    print("=== MdImgConverter 开发环境测试 ===\n")
    
    print("1. 测试Python版本:")
    print(f"   Python {sys.version}\n")
    
    print("2. 测试依赖包导入:")
    results = test_imports()
    for package, result in results.items():
        print(f"   {package}: {result}")
    
    # 检查是否所有包都导入成功
    all_success = all("✓ 成功" in result for result in results.values())
    
    if all_success:
        print("\n✓ 所有依赖包导入成功！")
        print("\n3. 测试GUI创建:")
        if test_simple_gui():
            print("✓ GUI测试成功！开发环境配置完成。")
        else:
            print("✗ GUI测试失败，请检查错误信息。")
    else:
        print("\n✗ 部分依赖包导入失败，请检查安装。")
        return False
    
    return True

if __name__ == "__main__":
    main()

