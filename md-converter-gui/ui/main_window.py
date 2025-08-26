#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
主窗口 - 精确复制用户的UI设计
"""

import sys

from PyQt6.QtCore import QPoint, QRect, QSettings, QSize, Qt, QTimer, pyqtSignal
from PyQt6.QtGui import (
    QAction,
    QColor,
    QCursor,
    QFont,
    QPainter,
    QPalette,
    QPixmap,
    QScreen,
)
from PyQt6.QtWidgets import (
    QApplication,
    QFileDialog,
    QFrame,
    QGridLayout,
    QHBoxLayout,
    QLabel,
    QMainWindow,
    QMessageBox,
    QPushButton,
    QSizePolicy,
    QSlider,
    QSplitter,
    QTextEdit,
    QToolButton,
    QVBoxLayout,
    QWidget,
)


class MarkdownEditor(QTextEdit):
    """左侧Markdown编辑器"""

    def __init__(self):
        super().__init__()
        self.setup_ui()

    def setup_ui(self):
        # 设置字体 - 微软雅黑
        font = QFont("Microsoft YaHei", 11)
        self.setFont(font)

        # 设置样式 - 精确复制你的深色主题
        self.setStyleSheet(
            """
            QTextEdit {
                background-color: #1e1e1e;
                color: #d4d4d4;
                border: none;
                line-height: 1.6;
                padding: 15px;
                selection-background-color: #264f78;
            }
            QScrollBar:vertical {
                background: #2d2d30;
                width: 12px;
                border: none;
            }
            QScrollBar::handle:vertical {
                background: #464647;
                border-radius: 6px;
                min-height: 20px;
            }
            QScrollBar::handle:vertical:hover {
                background: #5a5a5c;
            }
        """
        )

        # 设置占位符文本
        self.setPlaceholderText(
            "在此编辑Markdown内容...\n\n示例:\n# 标题\n![图片描述](图片链接)"
        )


class ControlPanel(QWidget):
    """右侧控制面板 - 精确复制UI设计"""

    def __init__(self):
        super().__init__()
        self.quality_value = 73  # 默认质量值
        self.progress_value = 0  # 进度值
        self.setup_ui()

    def setup_ui(self):
        self.setFixedWidth(200)  # 根据你的设计调整宽度

        main_layout = QVBoxLayout()
        main_layout.setSpacing(15)
        main_layout.setContentsMargins(15, 15, 15, 15)

        # 转换按钮 - 绿色，和你的设计一致
        self.convert_btn = QPushButton("转换")
        self.convert_btn.setFixedHeight(40)
        self.convert_btn.setStyleSheet(
            """
            QPushButton {
                background-color: #4CAF50;
                color: white;
                border: none;
                border-radius: 8px;
                font-size: 16px;
                font-weight: bold;
                font-family: 'Microsoft YaHei';
            }
            QPushButton:hover {
                background-color: #45a049;
            }
            QPushButton:pressed {
                background-color: #3d8b40;
            }
        """
        )
        main_layout.addWidget(self.convert_btn)

        # 两栏布局区域
        two_column_layout = QHBoxLayout()
        two_column_layout.setSpacing(15)

        # 左栏：图片质量控制
        left_column = self.create_quality_column()
        two_column_layout.addWidget(left_column)

        # 右栏：文章进度显示
        right_column = self.create_progress_column()
        two_column_layout.addWidget(right_column)

        main_layout.addLayout(two_column_layout)

        # 预设网格
        preset_frame = self.create_preset_grid()
        main_layout.addWidget(preset_frame)

        # 添加弹性空间
        main_layout.addStretch()

        self.setLayout(main_layout)

        # 设置控制面板背景 - 和你的设计一致
        self.setStyleSheet(
            """
            QWidget {
                background-color: #f5f5f5;
                font-family: 'Microsoft YaHei';
            }
        """
        )

    def create_quality_column(self):
        """创建左栏：图片质量控制"""
        column = QWidget()
        layout = QVBoxLayout()
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(8)

        # 标题
        title = QLabel("图片")
        title.setStyleSheet(
            "font-size: 14px; font-weight: bold; color: #333; font-family: 'Microsoft YaHei';"
        )
        title.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(title)

        # 垂直滑块
        self.quality_slider = QSlider(Qt.Orientation.Vertical)
        self.quality_slider.setRange(1, 100)
        self.quality_slider.setValue(self.quality_value)
        self.quality_slider.setFixedHeight(120)
        self.quality_slider.setFixedWidth(25)
        self.quality_slider.setStyleSheet(
            """
            QSlider::groove:vertical {
                background: #e0e0e0;
                width: 10px;
                border-radius: 5px;
            }
            QSlider::handle:vertical {
                background: #4CAF50;
                border: 2px solid #4CAF50;
                width: 20px;
                height: 20px;
                border-radius: 10px;
                margin: 0 -5px;
            }
            QSlider::sub-page:vertical {
                background: #4CAF50;
                border-radius: 5px;
            }
        """
        )

        # 滑块居中
        slider_container = QWidget()
        slider_layout = QHBoxLayout()
        slider_layout.setContentsMargins(0, 0, 0, 0)
        slider_layout.addStretch()
        slider_layout.addWidget(self.quality_slider)
        slider_layout.addStretch()
        slider_container.setLayout(slider_layout)
        layout.addWidget(slider_container)

        # 数值显示 - 绿色圆角标签
        self.quality_label = QLabel(f"{self.quality_value}%")
        self.quality_label.setFixedSize(60, 30)
        self.quality_label.setStyleSheet(
            """
            QLabel {
                background-color: #4CAF50;
                color: white;
                border-radius: 15px;
                font-weight: bold;
                font-size: 13px;
                font-family: 'Microsoft YaHei';
            }
        """
        )
        self.quality_label.setAlignment(Qt.AlignmentFlag.AlignCenter)

        # 标签居中
        label_container = QWidget()
        label_layout = QHBoxLayout()
        label_layout.setContentsMargins(0, 0, 0, 0)
        label_layout.addStretch()
        label_layout.addWidget(self.quality_label)
        label_layout.addStretch()
        label_container.setLayout(label_layout)
        layout.addWidget(label_container)

        # 连接信号
        self.quality_slider.valueChanged.connect(self.on_quality_changed)

        column.setLayout(layout)
        return column

    def create_progress_column(self):
        """创建右栏：文章进度显示（竖直绿条）"""
        column = QWidget()
        layout = QVBoxLayout()
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(8)

        # 标题
        title = QLabel("文章")
        title.setStyleSheet(
            "font-size: 14px; font-weight: bold; color: #333; font-family: 'Microsoft YaHei';"
        )
        title.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(title)

        # 进度条容器
        progress_container = QWidget()
        progress_container.setFixedHeight(120)
        progress_layout = QHBoxLayout()
        progress_layout.setContentsMargins(0, 0, 0, 0)
        progress_layout.addStretch()

        # 创建自定义进度条（竖直绿条）
        self.progress_bar = QWidget()
        self.progress_bar.setFixedSize(20, 120)
        self.progress_bar.setStyleSheet(
            """
            QWidget {
                background-color: #e0e0e0;
                border-radius: 10px;
            }
        """
        )

        # 进度指示器
        self.progress_indicator = QWidget(self.progress_bar)
        self.progress_indicator.setFixedWidth(20)
        self.progress_indicator.setStyleSheet(
            """
            QWidget {
                background-color: #4CAF50;
                border-radius: 10px;
            }
        """
        )
        self.progress_indicator.setGeometry(0, 120, 20, 0)  # 初始高度为0

        progress_layout.addWidget(self.progress_bar)
        progress_layout.addStretch()
        progress_container.setLayout(progress_layout)
        layout.addWidget(progress_container)

        layout.addStretch()
        column.setLayout(layout)
        return column

    def create_preset_grid(self):
        """创建预设网格 - 精确复制你的设计"""
        frame = QFrame()
        layout = QVBoxLayout()
        layout.setContentsMargins(8, 8, 8, 8)

        # 标题
        title = QLabel("预设")
        title.setStyleSheet(
            "font-size: 14px; font-weight: bold; color: #333; margin-bottom: 8px; font-family: 'Microsoft YaHei';"
        )
        layout.addWidget(title)

        # 3x4网格
        grid_layout = QGridLayout()
        grid_layout.setSpacing(6)

        self.preset_buttons = []
        for row in range(3):
            for col in range(4):
                btn = QPushButton()
                btn.setFixedSize(38, 30)
                btn.setStyleSheet(
                    """
                    QPushButton {
                        background-color: #ffffff;
                        border: 1px solid #e0e0e0;
                        border-radius: 6px;
                        font-size: 10px;
                        color: #666;
                        font-family: 'Microsoft YaHei';
                    }
                    QPushButton:hover {
                        background-color: #f0f0f0;
                        border-color: #ccc;
                    }
                """
                )

                # 为第一个按钮设置示例数据 - 绿色主题
                if row == 0 and col == 0:
                    btn.setText("36x100")
                    btn.setStyleSheet(
                        """
                        QPushButton {
                            background-color: #e8f5e8;
                            border: 1px solid #4CAF50;
                            border-radius: 6px;
                            font-size: 10px;
                            color: #2e7d32;
                            font-weight: bold;
                            font-family: 'Microsoft YaHei';
                        }
                        QPushButton:hover {
                            background-color: #c8e6c9;
                        }
                    """
                    )

                self.preset_buttons.append(btn)
                grid_layout.addWidget(btn, row, col)

        layout.addLayout(grid_layout)
        frame.setLayout(layout)

        return frame

    def on_quality_changed(self, value):
        """质量滑块值改变"""
        self.quality_value = value
        self.quality_label.setText(f"{value}%")

    def set_progress(self, value):
        """设置进度值 - 更新竖直绿条"""
        self.progress_value = value
        # 计算进度条高度
        max_height = 120
        progress_height = int((value / 100) * max_height)

        # 更新进度指示器的位置和高度
        self.progress_indicator.setGeometry(
            0, max_height - progress_height, 20, progress_height  # 从底部向上填充
        )


class MainWindow(QMainWindow):
    """主窗口 - 支持现代Windows功能"""

    def __init__(self):
        super().__init__()
        self.current_file = None
        self.settings = QSettings("MdImgConverter", "Settings")
        self.setup_ui()
        self.setup_status_bar()
        self.restore_window_state()

    def setup_ui(self):
        """设置用户界面"""
        # 使用标准窗口，但自定义样式
        self.setWindowTitle("MdImgConverter")

        # 设置窗口最小尺寸
        self.setMinimumSize(800, 600)

        # 创建主容器
        main_container = QWidget()
        self.setCentralWidget(main_container)

        # 主容器布局
        container_layout = QVBoxLayout()
        container_layout.setContentsMargins(0, 0, 0, 0)
        container_layout.setSpacing(0)

        # 添加自定义菜单栏
        self.custom_menu_bar = self.create_custom_menu_bar()
        container_layout.addWidget(self.custom_menu_bar)

        # 创建内容区域
        content_widget = QWidget()
        content_layout = QHBoxLayout()
        content_layout.setContentsMargins(0, 0, 0, 0)
        content_layout.setSpacing(0)

        # 创建分割器
        self.splitter = QSplitter(Qt.Orientation.Horizontal)
        self.splitter.setHandleWidth(1)
        self.splitter.setStyleSheet(
            """
            QSplitter::handle {
                background-color: #3e3e42;
            }
        """
        )

        # 左侧编辑器
        self.editor = MarkdownEditor()
        self.splitter.addWidget(self.editor)

        # 右侧控制面板
        self.control_panel = ControlPanel()
        self.splitter.addWidget(self.control_panel)

        # 设置分割器比例
        self.splitter.setStretchFactor(0, 4)
        self.splitter.setStretchFactor(1, 0)

        content_layout.addWidget(self.splitter)
        content_widget.setLayout(content_layout)
        container_layout.addWidget(content_widget)

        main_container.setLayout(container_layout)

        # 连接信号
        self.control_panel.convert_btn.clicked.connect(self.on_convert_clicked)

        # 设置窗口样式 - 深色主题
        self.setStyleSheet(
            """
            QMainWindow {
                background-color: #2d2d30;
            }
        """
        )

    def create_custom_menu_bar(self):
        """创建自定义菜单栏"""
        menu_widget = QWidget()
        menu_widget.setFixedHeight(35)
        menu_widget.setStyleSheet(
            """
            QWidget {
                background-color: #2d2d30;
                color: white;
            }
        """
        )

        layout = QHBoxLayout()
        layout.setContentsMargins(10, 0, 10, 0)
        layout.setSpacing(0)

        # 左侧菜单按钮
        menu_layout = QHBoxLayout()
        menu_layout.setSpacing(15)

        file_btn = QPushButton("文件(F)")
        edit_btn = QPushButton("编辑(E)")
        image_btn = QPushButton("图床(I)")

        for btn in [file_btn, edit_btn, image_btn]:
            btn.setStyleSheet(
                """
                QPushButton {
                    background: transparent;
                    color: #cccccc;
                    border: none;
                    padding: 6px 12px;
                    font-size: 13px;
                    font-family: 'Microsoft YaHei';
                }
                QPushButton:hover {
                    background-color: #3e3e42;
                    color: white;
                }
            """
            )
            menu_layout.addWidget(btn)

        layout.addLayout(menu_layout)
        layout.addStretch()

        menu_widget.setLayout(layout)
        return menu_widget

    def setup_status_bar(self):
        """设置状态栏"""
        status_bar = self.statusBar()
        status_bar.setStyleSheet(
            """
            QStatusBar {
                background-color: #007ACC;
                color: white;
                border: none;
                font-size: 12px;
                padding: 2px 10px;
                font-family: 'Microsoft YaHei';
            }
        """
        )

        # 左侧信息
        self.status_label = QLabel("开发中版本，不代表正式品质...")
        status_bar.addWidget(self.status_label)

        # 右侧上下文信息
        self.context_label = QLabel("质量选定: 73%")
        status_bar.addPermanentWidget(self.context_label)

        # 连接编辑器和滑块信号
        self.control_panel.quality_slider.valueChanged.connect(
            lambda v: self.context_label.setText(f"质量选定: {v}%")
        )

    def restore_window_state(self):
        """恢复窗口状态"""
        # 恢复窗口几何
        geometry = self.settings.value("geometry")
        if geometry:
            self.restoreGeometry(geometry)
        else:
            # 默认居中显示
            self.setGeometry(100, 100, 1200, 800)
            self.center_on_screen()

        # 恢复窗口状态（最大化等）
        window_state = self.settings.value("windowState")
        if window_state:
            self.restoreState(window_state)

        # 恢复分割器状态
        splitter_state = self.settings.value("splitterState")
        if splitter_state:
            self.splitter.restoreState(splitter_state)

    def save_window_state(self):
        """保存窗口状态"""
        self.settings.setValue("geometry", self.saveGeometry())
        self.settings.setValue("windowState", self.saveState())
        self.settings.setValue("splitterState", self.splitter.saveState())

    def center_on_screen(self):
        """居中显示窗口"""
        screen = QApplication.primaryScreen()
        screen_geometry = screen.availableGeometry()
        window_geometry = self.frameGeometry()
        center_point = screen_geometry.center()
        window_geometry.moveCenter(center_point)
        self.move(window_geometry.topLeft())

    def closeEvent(self, event):
        """窗口关闭事件"""
        self.save_window_state()
        event.accept()

    def on_convert_clicked(self):
        """转换按钮点击事件"""
        self.context_label.setText("开始转换...")
        self.simulate_conversion()

    def simulate_conversion(self):
        """模拟转换过程"""
        self.progress_timer = QTimer()
        self.progress_value = 0

        def update_progress():
            self.progress_value += 10
            self.control_panel.set_progress(self.progress_value)
            self.context_label.setText(f"转换中... {self.progress_value}%")

            if self.progress_value >= 100:
                self.progress_timer.stop()
                self.control_panel.set_progress(0)
                self.context_label.setText("转换完成！")

        self.progress_timer.timeout.connect(update_progress)
        self.progress_timer.start(200)
