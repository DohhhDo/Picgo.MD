#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
MdImgConverter - Markdown图片转换桌面应用
主程序入口
"""

import sys
from PyQt6.QtWidgets import QApplication
from PyQt6.QtCore import Qt
from PyQt6.QtGui import QFont
from ui.win11_design import Win11MainWindow

def main():
    try:
        print("正在启动应用...")
        # 创建应用实例
        app = QApplication(sys.argv)
        print("QApplication 创建成功")
        
        # 设置应用属性
        app.setApplicationName("MdImgConverter")
        app.setApplicationVersion("1.0.0")
        app.setOrganizationName("MdImgConverter")
        print("应用属性设置完成")
        
        # 设置高DPI支持
        # 在PyQt6中，高DPI支持是默认启用的，这些设置不再需要
        
        # 创建主窗口
        # 统一应用字体为 Microsoft YaHei
        print("正在设置字体...")
        try:
            app.setFont(QFont("Microsoft YaHei", 10))
            print("字体设置完成")
        except Exception as font_error:
            print(f"字体设置失败: {font_error}")
            print("使用默认字体")

        print("正在创建主窗口...")
        window = Win11MainWindow()
        print("主窗口创建成功")
        
        print("正在显示窗口...")
        window.show()
        print("窗口显示成功")
        
        print("应用启动完成，进入事件循环...")
        # 运行应用
        sys.exit(app.exec())
        
    except Exception as e:
        print(f"启动失败: {e}")
        import traceback
        traceback.print_exc()
        input("按回车键退出...")

if __name__ == "__main__":
    main()
