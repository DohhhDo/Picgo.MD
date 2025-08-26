#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
现代化无边框窗口 - 支持Win11交互
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


class ModernTitleBar(QWidget):
    """现代化标题栏 - 支持Win11交互"""

    # 定义信号
    minimize_clicked = pyqtSignal()
    maximize_clicked = pyqtSignal()
    close_clicked = pyqtSignal()

    def __init__(self):
        super().__init__()
        self.is_maximized = False
        self.setup_ui()

    def setup_ui(self):
        self.setFixedHeight(40)
        self.setStyleSheet(
            """
            QWidget {
                background-color: #2d2d30;
                color: white;
            }
        """
        )

        layout = QHBoxLayout()
        layout.setContentsMargins(15, 0, 0, 0)
        layout.setSpacing(0)

        # 左侧菜单按钮
        menu_layout = QHBoxLayout()
        menu_layout.setSpacing(20)

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
                    padding: 8px 12px;
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

        # 右侧窗口控制按钮
        controls_layout = QHBoxLayout()
        controls_layout.setSpacing(0)

        # 最小化按钮
        self.minimize_btn = QToolButton()
        self.minimize_btn.setText("─")
        self.minimize_btn.clicked.connect(self.minimize_clicked.emit)

        # 最大化/还原按钮
        self.maximize_btn = QToolButton()
        self.maximize_btn.setText("□")
        self.maximize_btn.clicked.connect(self.maximize_clicked.emit)

        # 关闭按钮
        self.close_btn = QToolButton()
        self.close_btn.setText("✕")
        self.close_btn.clicked.connect(self.close_clicked.emit)

        for btn in [self.minimize_btn, self.maximize_btn, self.close_btn]:
            btn.setFixedSize(45, 30)
            btn.setStyleSheet(
                """
                QToolButton {
                    background: transparent;
                    color: #cccccc;
                    border: none;
                    font-size: 14px;
                }
                QToolButton:hover {
                    background-color: #3e3e42;
                    color: white;
                }
            """
            )
            controls_layout.addWidget(btn)

        # 关闭按钮特殊样式
        self.close_btn.setStyleSheet(
            self.close_btn.styleSheet()
            + """
            QToolButton:hover {
                background-color: #e74c3c;
                color: white;
            }
        """
        )

        layout.addLayout(controls_layout)
        self.setLayout(layout)

    def update_maximize_button(self, is_maximized):
        """更新最大化按钮状态"""
        self.is_maximized = is_maximized
        if is_maximized:
            self.maximize_btn.setText("❐")  # 还原图标
        else:
            self.maximize_btn.setText("□")  # 最大化图标


class ResizableFramelessWindow(QMainWindow):
    """可调整大小的无边框窗口 - 支持Win11现代交互"""

    def __init__(self):
        super().__init__()
        self.border_width = 5  # 边框宽度
        self.corner_width = 10  # 角落宽度
        self.dragging = False
        self.resizing = False
        self.resize_direction = None
        self.drag_position = QPoint()
        self.is_maximized_state = False
        self.normal_geometry = None
        self.settings = QSettings("MdImgConverter", "Settings")

        # 设置窗口属性
        self.setWindowFlags(
            Qt.WindowType.FramelessWindowHint
            | Qt.WindowType.WindowMinMaxButtonsHint
            | Qt.WindowType.WindowSystemMenuHint
        )

        # 启用鼠标追踪
        self.setMouseTracking(True)

        # 设置最小尺寸
        self.setMinimumSize(800, 600)

        self.setup_ui()
        self.setup_status_bar()
        self.restore_window_state()

    def setup_ui(self):
        """设置用户界面"""
        self.setWindowTitle("MdImgConverter")

        # 创建主容器
        main_container = QWidget()
        self.setCentralWidget(main_container)

        # 主容器布局
        container_layout = QVBoxLayout()
        container_layout.setContentsMargins(0, 0, 0, 0)
        container_layout.setSpacing(0)

        # 添加标题栏
        self.title_bar = ModernTitleBar()
        self.title_bar.minimize_clicked.connect(self.showMinimized)
        self.title_bar.maximize_clicked.connect(self.toggle_maximize)
        self.title_bar.close_clicked.connect(self.close)
        container_layout.addWidget(self.title_bar)

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
        from .main_window import MarkdownEditor

        self.editor = MarkdownEditor()
        self.splitter.addWidget(self.editor)

        # 右侧控制面板
        from .main_window import ControlPanel

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
                border: 1px solid #3e3e42;
            }
        """
        )

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

    def setup_resize_cursors(self, pos):
        """设置调整大小的鼠标光标"""
        if self.is_maximized_state:
            self.setCursor(QCursor(Qt.CursorShape.ArrowCursor))
            self.resize_direction = None
            return

        rect = self.rect()

        # 检查鼠标位置并设置相应光标
        if pos.x() < self.border_width and pos.y() < self.corner_width:
            # 左上角
            self.setCursor(QCursor(Qt.CursorShape.SizeFDiagCursor))
            self.resize_direction = "top-left"
        elif pos.x() > rect.width() - self.border_width and pos.y() < self.corner_width:
            # 右上角
            self.setCursor(QCursor(Qt.CursorShape.SizeBDiagCursor))
            self.resize_direction = "top-right"
        elif (
            pos.x() < self.border_width and pos.y() > rect.height() - self.corner_width
        ):
            # 左下角
            self.setCursor(QCursor(Qt.CursorShape.SizeBDiagCursor))
            self.resize_direction = "bottom-left"
        elif (
            pos.x() > rect.width() - self.border_width
            and pos.y() > rect.height() - self.corner_width
        ):
            # 右下角
            self.setCursor(QCursor(Qt.CursorShape.SizeFDiagCursor))
            self.resize_direction = "bottom-right"
        elif pos.x() < self.border_width:
            # 左边
            self.setCursor(QCursor(Qt.CursorShape.SizeHorCursor))
            self.resize_direction = "left"
        elif pos.x() > rect.width() - self.border_width:
            # 右边
            self.setCursor(QCursor(Qt.CursorShape.SizeHorCursor))
            self.resize_direction = "right"
        elif pos.y() < self.border_width:
            # 上边
            self.setCursor(QCursor(Qt.CursorShape.SizeVerCursor))
            self.resize_direction = "top"
        elif pos.y() > rect.height() - self.border_width:
            # 下边
            self.setCursor(QCursor(Qt.CursorShape.SizeVerCursor))
            self.resize_direction = "bottom"
        else:
            # 内部区域
            self.setCursor(QCursor(Qt.CursorShape.ArrowCursor))
            self.resize_direction = None

    def mousePressEvent(self, event):
        if event.button() == Qt.MouseButton.LeftButton:
            self.drag_position = event.globalPosition().toPoint() - self.pos()

            if self.resize_direction and not self.is_maximized_state:
                self.resizing = True
                self.normal_geometry = self.geometry()
            elif event.position().toPoint().y() < 40:  # 标题栏区域
                self.dragging = True

            event.accept()

    def mouseMoveEvent(self, event):
        if not self.is_maximized_state:
            if self.resizing and self.resize_direction:
                self.resize_window(event.globalPosition().toPoint())
            elif self.dragging:
                # 检查是否拖拽到屏幕顶部进行最大化
                if event.globalPosition().toPoint().y() <= 0:
                    self.toggle_maximize()
                else:
                    self.move(event.globalPosition().toPoint() - self.drag_position)
            else:
                self.setup_resize_cursors(event.position().toPoint())
        elif self.dragging and event.globalPosition().toPoint().y() > 40:
            # 从最大化状态拖拽还原
            self.is_maximized_state = False
            self.title_bar.update_maximize_button(False)

            # 计算新的窗口位置
            if hasattr(self, "normal_geometry_backup"):
                new_size = self.normal_geometry_backup.size()
            else:
                new_size = QSize(1200, 800)

            # 计算鼠标相对窗口的位置
            mouse_x_ratio = event.globalPosition().toPoint().x() / self.width()
            new_x = event.globalPosition().toPoint().x() - int(
                new_size.width() * mouse_x_ratio
            )
            new_y = event.globalPosition().toPoint().y() - 20

            self.setGeometry(new_x, new_y, new_size.width(), new_size.height())
            self.dragging = True
            self.drag_position = QPoint(int(new_size.width() * mouse_x_ratio), 20)

        event.accept()

    def mouseReleaseEvent(self, event):
        self.dragging = False
        self.resizing = False
        self.resize_direction = None
        event.accept()

    def mouseDoubleClickEvent(self, event):
        if event.position().toPoint().y() < 40:  # 双击标题栏
            self.toggle_maximize()
        event.accept()

    def resize_window(self, global_pos):
        """调整窗口大小"""
        if not self.normal_geometry:
            return

        geometry = self.geometry()
        delta_x = global_pos.x() - (self.normal_geometry.x() + self.drag_position.x())
        delta_y = global_pos.y() - (self.normal_geometry.y() + self.drag_position.y())

        new_geo = geometry

        if "left" in self.resize_direction:
            new_geo.setLeft(geometry.left() + delta_x)
        if "right" in self.resize_direction:
            new_geo.setRight(geometry.right() + delta_x)
        if "top" in self.resize_direction:
            new_geo.setTop(geometry.top() + delta_y)
        if "bottom" in self.resize_direction:
            new_geo.setBottom(geometry.bottom() + delta_y)

        # 确保最小尺寸
        if (
            new_geo.width() >= self.minimumWidth()
            and new_geo.height() >= self.minimumHeight()
        ):
            self.setGeometry(new_geo)

    def toggle_maximize(self):
        """切换最大化状态"""
        if self.is_maximized_state:
            # 还原窗口
            if hasattr(self, "normal_geometry_backup"):
                self.setGeometry(self.normal_geometry_backup)
            else:
                self.showNormal()
            self.is_maximized_state = False
        else:
            # 最大化窗口
            self.normal_geometry_backup = self.geometry()
            screen = QApplication.primaryScreen().availableGeometry()
            self.setGeometry(screen)
            self.is_maximized_state = True

        # 更新标题栏按钮
        self.title_bar.update_maximize_button(self.is_maximized_state)

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

        # 恢复分割器状态
        splitter_state = self.settings.value("splitterState")
        if splitter_state:
            self.splitter.restoreState(splitter_state)

    def save_window_state(self):
        """保存窗口状态"""
        self.settings.setValue("geometry", self.saveGeometry())
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
