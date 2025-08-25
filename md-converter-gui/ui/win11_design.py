#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Win11 Fluent Design System - 官方设计规范实现
采用与Windows设置、文件资源管理器一致的UI风格
"""

from PyQt6.QtWidgets import (
    QMainWindow, QWidget, QVBoxLayout, QHBoxLayout, 
    QSplitter, QLabel, QPushButton, QSlider, QGridLayout, 
    QFrame, QTextEdit, QFileDialog, QMessageBox, QToolButton,
    QSizePolicy, QApplication, QGraphicsDropShadowEffect
)
from PyQt6.QtCore import Qt, QTimer, QSize, pyqtSignal, QSettings, QRect, QPoint, QPropertyAnimation, QEasingCurve, QThread
from PyQt6.QtGui import QFont, QAction, QPalette, QColor, QPixmap, QPainter, QScreen, QCursor
import sys
import os
from pathlib import Path

# 添加core模块路径
current_dir = Path(__file__).parent.parent
sys.path.insert(0, str(current_dir))

try:
    from core.image_converter import convert_markdown_images
except ImportError:
    print("Warning: 无法导入图片转换模块")
    convert_markdown_images = None

class ConversionWorker(QThread):
    """图片转换工作线程"""
    progress_updated = pyqtSignal(int, str)
    conversion_finished = pyqtSignal(str, int, dict)  # 添加压缩统计
    conversion_error = pyqtSignal(str)
    
    def __init__(self, markdown_text, output_dir, quality):
        super().__init__()
        self.markdown_text = markdown_text
        self.output_dir = output_dir
        self.quality = quality
    
    def run(self):
        """在后台线程中执行转换"""
        try:
            if convert_markdown_images:
                def progress_callback(progress, message):
                    self.progress_updated.emit(progress, message)
                
                new_markdown, count, stats = convert_markdown_images(
                    self.markdown_text, 
                    self.output_dir, 
                    self.quality, 
                    progress_callback
                )
                self.conversion_finished.emit(new_markdown, count, stats)
            else:
                self.conversion_error.emit("图片转换模块未找到")
        except Exception as e:
            self.conversion_error.emit(f"转换失败: {str(e)}")

class Win11MarkdownEditor(QTextEdit):
    """Win11风格的Markdown编辑器"""
    def __init__(self):
        super().__init__()
        self.setup_ui()
    
    def setup_ui(self):
        # 设置Win11推荐字体
        font = QFont("Segoe UI", 11)
        self.setFont(font)
        
        # 检测系统主题
        self.is_dark_theme = self.detect_system_theme()
        
        # 应用主题样式
        self.apply_theme_style()
        
        # 设置占位符文本
        self.setPlaceholderText("在此编辑Markdown内容...")
    
    def detect_system_theme(self):
        """检测系统是否为深色主题"""
        try:
            import winreg
            registry = winreg.ConnectRegistry(None, winreg.HKEY_CURRENT_USER)
            key = winreg.OpenKey(registry, r"SOFTWARE\Microsoft\Windows\CurrentVersion\Themes\Personalize")
            value, _ = winreg.QueryValueEx(key, "AppsUseLightTheme")
            winreg.CloseKey(key)
            return value == 0  # 0表示深色主题，1表示浅色主题
        except:
            return False  # 默认浅色主题
    
    def apply_theme_style(self):
        """应用主题样式"""
        if self.is_dark_theme:
            # 深色主题样式
            self.setStyleSheet("""
                QTextEdit {
                    background-color: #1e1e1e;
                    color: #ffffff;
                    border: 1px solid #3f3f3f;
                    border-radius: 4px;
                    padding: 12px;
                    line-height: 1.4;
                    selection-background-color: #0078d4;
                    selection-color: #ffffff;
                    font-family: 'Segoe UI';
                }
                QScrollBar:vertical {
                    background: transparent;
                    width: 12px;
                    border: none;
                }
                QScrollBar::handle:vertical {
                    background: #606060;
                    border-radius: 6px;
                    min-height: 20px;
                    margin: 2px;
                }
                QScrollBar::handle:vertical:hover {
                    background: #808080;
                }
                QScrollBar::add-line:vertical, QScrollBar::sub-line:vertical {
                    border: none;
                    background: none;
                }
            """)
        else:
            # 浅色主题样式
            self.setStyleSheet("""
                QTextEdit {
                    background-color: #ffffff;
                    color: #000000;
                    border: 1px solid #8a8886;
                    border-radius: 4px;
                    padding: 12px;
                    line-height: 1.4;
                    selection-background-color: #0078d4;
                    selection-color: #ffffff;
                    font-family: 'Segoe UI';
                }
                QScrollBar:vertical {
                    background: transparent;
                    width: 12px;
                    border: none;
                }
                QScrollBar::handle:vertical {
                    background: #606060;
                    border-radius: 6px;
                    min-height: 20px;
                    margin: 2px;
                }
                QScrollBar::handle:vertical:hover {
                    background: #808080;
                }
                QScrollBar::add-line:vertical, QScrollBar::sub-line:vertical {
                    border: none;
                    background: none;
                }
            """)

class Win11ControlPanel(QWidget):
    """Win11风格的控制面板"""
    def __init__(self):
        super().__init__()
        self.quality_value = 73  # 默认质量值
        self.progress_value = 0  # 进度值
        
        # 检测系统主题
        self.is_dark_theme = self.detect_system_theme()
        
        self.setup_ui()
    
    def detect_system_theme(self):
        """检测系统是否为深色主题"""
        try:
            import winreg
            registry = winreg.ConnectRegistry(None, winreg.HKEY_CURRENT_USER)
            key = winreg.OpenKey(registry, r"SOFTWARE\Microsoft\Windows\CurrentVersion\Themes\Personalize")
            value, _ = winreg.QueryValueEx(key, "AppsUseLightTheme")
            winreg.CloseKey(key)
            return value == 0  # 0表示深色主题，1表示浅色主题
        except:
            return False  # 默认浅色主题
    
    def setup_ui(self):
        self.setFixedWidth(280)  # Win11推荐的侧边栏宽度
        
        # 应用主题样式
        self.apply_panel_theme()
        
        # 主布局
        main_layout = QVBoxLayout()
        main_layout.setSpacing(16)
        main_layout.setContentsMargins(20, 20, 20, 20)
        
        # 转换按钮 - 真实Win11按钮样式
        self.convert_btn = QPushButton("转换")
        self.convert_btn.setFixedHeight(32)
        self.convert_btn.setStyleSheet("""
            QPushButton {
                background-color: #0067b8;
                color: white;
                border: 1px solid #0067b8;
                border-radius: 2px;
                font-size: 14px;
                font-family: 'Microsoft YaHei';
                padding: 6px 20px;
            }
            QPushButton:hover {
                background-color: #106ebe;
                border-color: #106ebe;
            }
            QPushButton:pressed {
                background-color: #005a9e;
                border-color: #005a9e;
            }
        """)
        main_layout.addWidget(self.convert_btn)
        
        # 分隔线
        separator = QFrame()
        separator.setFrameShape(QFrame.Shape.HLine)
        separator.setStyleSheet("QFrame { color: #333333; }")
        main_layout.addWidget(separator)
        
        # 图片质量设置卡片
        quality_card = self.create_quality_card()
        main_layout.addWidget(quality_card)
        
        # 进度显示卡片
        progress_card = self.create_progress_card()
        main_layout.addWidget(progress_card)
        
        # 压缩统计卡片
        stats_card = self.create_stats_card()
        main_layout.addWidget(stats_card)
        
        # 预设网格
        presets_card = self.create_preset_card()
        main_layout.addWidget(presets_card)
        
        # 弹性空间
        main_layout.addStretch()
        
        # 设置布局
        self.setLayout(main_layout)
    
    def apply_panel_theme(self):
        """应用控制面板主题"""
        if self.is_dark_theme:
            # 深色主题
            self.setStyleSheet("""
                Win11ControlPanel {
                    background-color: #2d2d2d;
                    border-left: 1px solid #3f3f3f;
                }
            """)
        else:
            # 浅色主题
            self.setStyleSheet("""
                Win11ControlPanel {
                    background-color: #f3f3f3;
                    border-left: 1px solid #e5e5e5;
                }
            """)
    
    def get_card_style(self):
        """获取卡片样式"""
        if self.is_dark_theme:
            return """
                QFrame {
                    background-color: #2b2b2b;
                    border: 1px solid #3a3a3a;
                    border-radius: 10px;
                    padding: 0px;
                }
            """
        else:
            return """
                QFrame {
                    background-color: #ffffff;
                    border: 1px solid #e5e5e5;
                    border-radius: 10px;
                    padding: 0px;
                }
            """
    
    def get_label_style(self, size="14px", weight="normal", color=None):
        """获取标签样式"""
        if color is None:
            color = "#ffffff" if self.is_dark_theme else "#323130"
        
        return f"""
            QLabel {{
                font-size: {size};
                font-weight: {weight};
                color: {color};
            }}
        """
    
    def create_quality_card(self):
        """创建图片质量设置卡片"""
        card = QFrame()
        card.setFrameStyle(QFrame.Shape.NoFrame)
        card.setStyleSheet(self.get_card_style())
        
        # 添加阴影效果
        shadow = QGraphicsDropShadowEffect()
        shadow.setBlurRadius(10)
        shadow.setColor(QColor(0, 0, 0, 30))
        shadow.setOffset(0, 2)
        card.setGraphicsEffect(shadow)
        
        layout = QVBoxLayout()
        layout.setContentsMargins(16, 16, 16, 16)
        layout.setSpacing(12)
        
        # 标题
        title = QLabel("图片质量")
        title.setStyleSheet(self.get_label_style("16px", "600") + """
            QLabel {
                margin-bottom: 4px;
            }
        """)
        layout.addWidget(title)
        
        # 描述
        desc = QLabel("调整WebP压缩质量")
        desc.setStyleSheet("""
            QLabel {
                font-size: 12px;
                color: #605e5c;
                margin-bottom: 8px;
            }
        """)
        layout.addWidget(desc)
        
        # 滑块和数值显示容器
        control_layout = QHBoxLayout()
        control_layout.setSpacing(12)
        
        # 水平滑块 - Win11风格
        self.quality_slider = QSlider(Qt.Orientation.Horizontal)
        self.quality_slider.setRange(1, 100)
        self.quality_slider.setValue(self.quality_value)
        self.quality_slider.setFixedHeight(24)
        self.quality_slider.setStyleSheet("""
            QSlider::groove:horizontal {
                background: #dfe1e6;
                height: 4px;
                border-radius: 2px;
            }
            QSlider::handle:horizontal {
                background: #16a34a; /* 绿色强调 */
                width: 20px;
                height: 20px;
                border-radius: 10px;
                margin: -8px 0;
            }
            QSlider::handle:horizontal:hover {
                background: #15803d;
            }
            QSlider::sub-page:horizontal {
                background: #16a34a;
                border-radius: 2px;
            }
        """)
        
        # 数值显示
        self.quality_label = QLabel(f"{self.quality_value}%")
        self.quality_label.setFixedWidth(45)
        self.quality_label.setStyleSheet("""
            QLabel {
                background-color: #ecfdf5;
                color: #065f46;
                border: 1px solid #a7f3d0;
                border-radius: 6px;
                padding: 4px 8px;
                font-size: 13px;
                font-weight: 600;
            }
        """)
        self.quality_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        
        # 连接信号
        self.quality_slider.valueChanged.connect(self.on_quality_changed)
        
        control_layout.addWidget(self.quality_slider)
        control_layout.addWidget(self.quality_label)
        
        layout.addLayout(control_layout)
        card.setLayout(layout)
        
        return card
    
    def create_progress_card(self):
        """创建进度显示卡片"""
        card = QFrame()
        card.setFrameStyle(QFrame.Shape.NoFrame)
        card.setStyleSheet(self.get_card_style())
        
        # 添加阴影效果
        shadow = QGraphicsDropShadowEffect()
        shadow.setBlurRadius(10)
        shadow.setColor(QColor(0, 0, 0, 30))
        shadow.setOffset(0, 2)
        card.setGraphicsEffect(shadow)
        
        layout = QVBoxLayout()
        layout.setContentsMargins(16, 16, 16, 16)
        layout.setSpacing(12)
        
        # 标题
        title = QLabel("转换进度")
        title.setStyleSheet(self.get_label_style("16px", "600") + """
            QLabel {
                margin-bottom: 4px;
            }
        """)
        layout.addWidget(title)
        
        # Win11风格进度条
        progress_container = QWidget()
        progress_container.setFixedHeight(60)
        
        progress_layout = QVBoxLayout()
        progress_layout.setContentsMargins(0, 0, 0, 0)
        progress_layout.setSpacing(8)
        
        # 进度条背景
        self.progress_bg = QWidget()
        self.progress_bg.setFixedHeight(8)
        self.progress_bg.setStyleSheet("""
            QWidget {
                background-color: #dfe1e6;
                border-radius: 4px;
            }
        """)
        
        # 进度条填充
        self.progress_fill = QWidget(self.progress_bg)
        self.progress_fill.setFixedHeight(8)
        self.progress_fill.setFixedWidth(0)  # 初始宽度为0
        self.progress_fill.setStyleSheet("""
            QWidget {
                background-color: #16a34a;
                border-radius: 4px;
            }
        """)
        
        # 进度文本
        self.progress_text = QLabel("准备就绪")
        self.progress_text.setStyleSheet("""
            QLabel {
                font-size: 12px;
                color: #667085;
            }
        """)
        self.progress_text.setAlignment(Qt.AlignmentFlag.AlignCenter)
        
        progress_layout.addWidget(self.progress_bg)
        progress_layout.addWidget(self.progress_text)
        progress_container.setLayout(progress_layout)
        
        layout.addWidget(progress_container)
        card.setLayout(layout)
        
        return card
    
    def create_preset_card(self):
        """创建预设配置卡片"""
        card = QFrame()
        card.setFrameStyle(QFrame.Shape.NoFrame)
        card.setStyleSheet(self.get_card_style())
        
        # 添加阴影效果
        shadow = QGraphicsDropShadowEffect()
        shadow.setBlurRadius(10)
        shadow.setColor(QColor(0, 0, 0, 30))
        shadow.setOffset(0, 2)
        card.setGraphicsEffect(shadow)
        
        layout = QVBoxLayout()
        layout.setContentsMargins(16, 16, 16, 16)
        layout.setSpacing(12)
        
        # 标题
        title = QLabel("预设配置")
        title.setStyleSheet(self.get_label_style("16px", "600") + """
            QLabel {
                margin-bottom: 4px;
            }
        """)
        layout.addWidget(title)
        
        # 无损预设按钮（大按钮）
        self.lossless_btn = QPushButton("无损")
        self.lossless_btn.setMinimumHeight(42)
        self.lossless_btn.setStyleSheet("""
            QPushButton {
                background-color: #16a34a;
                color: white;
                border: 1px solid #16a34a;
                border-radius: 6px;
                font-size: 14px;
                font-family: 'Microsoft YaHei';
                font-weight: 600;
                text-align: center;
            }
            QPushButton:hover {
                background-color: #15803d;
                border-color: #15803d;
            }
            QPushButton:pressed {
                background-color: #166534;
                border-color: #166534;
            }
        """)
        self.lossless_btn.clicked.connect(lambda: self.set_quality_preset(100))
        layout.addWidget(self.lossless_btn)
        
        # 分隔线
        separator = QFrame()
        separator.setFrameShape(QFrame.Shape.HLine)
        separator.setStyleSheet("QFrame { color: #e1dfdd; margin: 8px 0px; }")
        layout.addWidget(separator)
        
        # 预设网格
        grid_layout = QGridLayout()
        grid_layout.setSpacing(8)
        
        self.preset_buttons = []
        preset_configs = [
            ("高质量", "90%", 90),
            ("标准", "73%", 73),
            ("压缩", "50%", 50),
            ("极压缩", "30%", 30),
        ]
        
        for i, (name, quality_text, quality_value) in enumerate(preset_configs):
            btn = QPushButton(f"{name}\n{quality_text}")
            btn.setFixedSize(55, 45)
            btn.setStyleSheet("""
                QPushButton {
                    background-color: #f8fafc;
                    border: 1px solid #e2e8f0;
                    border-radius: 6px;
                    font-size: 10px;
                    color: #334155;
                    text-align: center;
                    font-family: 'Microsoft YaHei';
                }
                QPushButton:hover {
                    background-color: #f1f5f9;
                    border-color: #cbd5e1;
                }
                QPushButton:pressed {
                    background-color: #e2e8f0;
                }
            """)
            
            # 为第二个按钮（标准）设置选中状态
            if i == 1:
                btn.setStyleSheet(btn.styleSheet() + """
                    QPushButton {
                        background-color: #dcfce7;
                        border-color: #16a34a;
                        color: #166534;
                        font-weight: 700;
                    }
                """)
            
            # 连接点击事件
            btn.clicked.connect(lambda checked, val=quality_value: self.set_quality_preset(val))
            
            self.preset_buttons.append(btn)
            grid_layout.addWidget(btn, i // 2, i % 2)
        
        layout.addLayout(grid_layout)
        card.setLayout(layout)
        
        return card
    
    def set_quality_preset(self, quality_value):
        """设置质量预设值"""
        self.quality_value = quality_value
        
        # 更新滑块位置
        if hasattr(self, 'quality_slider'):
            self.quality_slider.setValue(quality_value)
        
        # 更新按钮选中状态
        self.update_preset_button_states(quality_value)
    
    def update_preset_button_states(self, selected_quality):
        """更新预设按钮的选中状态"""
        # 重置所有按钮状态
        if hasattr(self, 'lossless_btn'):
            if selected_quality == 100:
                # 无损按钮选中状态
                self.lossless_btn.setStyleSheet("""
                    QPushButton {
                        background-color: #15803d;
                        color: white;
                        border: 2px solid #16a34a;
                        border-radius: 6px;
                        font-size: 14px;
                        font-family: 'Microsoft YaHei';
                        font-weight: 700;
                        text-align: center;
                    }
                    QPushButton:hover {
                        background-color: #166534;
                        border-color: #16a34a;
                    }
                """)
            else:
                # 无损按钮未选中状态
                self.lossless_btn.setStyleSheet("""
                    QPushButton {
                        background-color: #16a34a;
                        color: white;
                        border: 1px solid #16a34a;
                        border-radius: 6px;
                        font-size: 14px;
                        font-family: 'Microsoft YaHei';
                        font-weight: 600;
                        text-align: center;
                    }
                    QPushButton:hover {
                        background-color: #15803d;
                        border-color: #15803d;
                    }
                    QPushButton:pressed {
                        background-color: #166534;
                        border-color: #166534;
                    }
                """)
        
        # 更新其他预设按钮状态
        preset_values = [90, 73, 50, 30]
        for i, btn in enumerate(self.preset_buttons):
            if preset_values[i] == selected_quality and selected_quality != 100:
                # 选中状态
                btn.setStyleSheet("""
                    QPushButton {
                        background-color: #dcfce7;
                        border: 2px solid #16a34a;
                        border-radius: 6px;
                        font-size: 10px;
                        color: #166534;
                        text-align: center;
                        font-family: 'Microsoft YaHei';
                        font-weight: 700;
                    }
                    QPushButton:hover {
                        background-color: #bbf7d0;
                        border-color: #16a34a;
                    }
                """)
            else:
                # 未选中状态
                btn.setStyleSheet("""
                    QPushButton {
                        background-color: #f8fafc;
                        border: 1px solid #e2e8f0;
                        border-radius: 6px;
                        font-size: 10px;
                        color: #334155;
                        text-align: center;
                        font-family: 'Microsoft YaHei';
                    }
                    QPushButton:hover {
                        background-color: #f1f5f9;
                        border-color: #cbd5e1;
                    }
                    QPushButton:pressed {
                        background-color: #e2e8f0;
                    }
                """)
    
    def create_stats_card(self):
        """创建压缩统计卡片"""
        card = QFrame()
        card.setFrameStyle(QFrame.Shape.NoFrame)
        card.setStyleSheet(self.get_card_style())
        
        # 添加阴影效果
        shadow = QGraphicsDropShadowEffect()
        shadow.setBlurRadius(10)
        shadow.setColor(QColor(0, 0, 0, 30))
        shadow.setOffset(0, 2)
        card.setGraphicsEffect(shadow)
        
        layout = QVBoxLayout()
        layout.setContentsMargins(16, 16, 16, 16)
        layout.setSpacing(8)
        
        # 标题
        title = QLabel("压缩统计")
        title.setStyleSheet(self.get_label_style("16px", "600") + """
            QLabel {
                margin-bottom: 4px;
            }
        """)
        layout.addWidget(title)
        
        # 统计信息容器
        stats_container = QWidget()
        stats_layout = QVBoxLayout()
        stats_layout.setContentsMargins(0, 0, 0, 0)
        stats_layout.setSpacing(6)
        
        # 原始大小
        self.original_size_label = QLabel("原始大小: --")
        self.original_size_label.setStyleSheet("""
            QLabel {
                font-size: 12px;
                color: #605e5c;
            }
        """)
        stats_layout.addWidget(self.original_size_label)
        
        # 压缩后大小
        self.compressed_size_label = QLabel("压缩后: --")
        self.compressed_size_label.setStyleSheet("""
            QLabel {
                font-size: 12px;
                color: #605e5c;
            }
        """)
        stats_layout.addWidget(self.compressed_size_label)
        
        # 节省空间
        self.saved_size_label = QLabel("节省空间: --")
        self.saved_size_label.setStyleSheet("""
            QLabel {
                font-size: 12px;
                color: #107c10;
                font-weight: 600;
            }
        """)
        stats_layout.addWidget(self.saved_size_label)
        
        # 压缩比例
        self.compression_ratio_label = QLabel("压缩比例: --")
        self.compression_ratio_label.setStyleSheet("""
            QLabel {
                font-size: 14px;
                color: #0078d4;
                font-weight: 600;
            }
        """)
        stats_layout.addWidget(self.compression_ratio_label)
        
        stats_container.setLayout(stats_layout)
        layout.addWidget(stats_container)
        
        card.setLayout(layout)
        return card
    
    def update_compression_stats(self, stats):
        """更新压缩统计信息"""
        def format_size(size_bytes):
            """格式化文件大小"""
            if size_bytes == 0:
                return "0 B"
            
            for unit in ['B', 'KB', 'MB', 'GB']:
                if size_bytes < 1024:
                    return f"{size_bytes:.1f} {unit}"
                size_bytes /= 1024
            return f"{size_bytes:.1f} TB"
        
        original_size = stats.get('total_original_size', 0)
        compressed_size = stats.get('total_converted_size', 0)
        saved_size = stats.get('size_saved', 0)
        compression_ratio = stats.get('compression_ratio', 0)
        
        self.original_size_label.setText(f"原始大小: {format_size(original_size)}")
        self.compressed_size_label.setText(f"压缩后: {format_size(compressed_size)}")
        self.saved_size_label.setText(f"节省空间: {format_size(saved_size)}")
        self.compression_ratio_label.setText(f"压缩比例: {compression_ratio:.1f}%")
    
    def reset_compression_stats(self):
        """重置压缩统计信息"""
        self.original_size_label.setText("原始大小: --")
        self.compressed_size_label.setText("压缩后: --")
        self.saved_size_label.setText("节省空间: --")
        self.compression_ratio_label.setText("压缩比例: --")
    
    def on_quality_changed(self, value):
        """质量滑块值改变"""
        self.quality_value = value
        self.quality_label.setText(f"{value}%")
        
        # 更新预设按钮状态
        self.update_preset_button_states(value)
    
    def set_progress(self, value):
        """设置进度值 - Win11动画效果"""
        self.progress_value = value
        
        # 计算进度条宽度
        total_width = self.progress_bg.width()
        progress_width = int((value / 100) * total_width)
        
        # 设置进度条宽度（带动画效果）
        self.progress_fill.setFixedWidth(progress_width)
        
        # 更新进度文本
        if value == 0:
            self.progress_text.setText("准备就绪")
        elif value == 100:
            self.progress_text.setText("转换完成")
        else:
            self.progress_text.setText(f"转换中... {value}%")

class Win11MainWindow(QMainWindow):
    """Win11风格主窗口"""
    def __init__(self):
        super().__init__()
        self.current_file = None
        self.settings = QSettings("MdImgConverter", "Settings")
        self.setup_ui()
        self.setup_status_bar()
        self.restore_window_state()
        
    def setup_ui(self):
        """设置用户界面"""
        # 使用标准窗口
        self.setWindowTitle("MdImgConverter")
        self.setMinimumSize(900, 700)
        
        # 创建主容器
        main_container = QWidget()
        self.setCentralWidget(main_container)
        
        # 主容器布局
        container_layout = QVBoxLayout()
        container_layout.setContentsMargins(0, 0, 0, 0)
        container_layout.setSpacing(0)
        
        # Win11风格菜单栏
        self.setup_menu_bar()
        
        # 创建内容区域
        content_widget = QWidget()
        content_layout = QHBoxLayout()
        content_layout.setContentsMargins(0, 0, 0, 0)
        content_layout.setSpacing(1)  # Win11分割线宽度
        
        # 创建分割器
        self.splitter = QSplitter(Qt.Orientation.Horizontal)
        self.splitter.setHandleWidth(1)
        self.splitter.setStyleSheet("""
            QSplitter::handle {
                background-color: #e5e5e5;
            }
        """)
        
        # 左侧编辑器
        self.editor = Win11MarkdownEditor()
        self.splitter.addWidget(self.editor)
        
        # 右侧控制面板
        self.control_panel = Win11ControlPanel()
        self.splitter.addWidget(self.control_panel)
        
        # 设置分割器比例
        self.splitter.setStretchFactor(0, 3)
        self.splitter.setStretchFactor(1, 1)
        
        content_layout.addWidget(self.splitter)
        content_widget.setLayout(content_layout)
        container_layout.addWidget(content_widget)
        
        main_container.setLayout(container_layout)
        
        # 连接信号
        self.control_panel.convert_btn.clicked.connect(self.on_convert_clicked)
        
        # 设置Win11主题样式
        self.setStyleSheet("""
            QMainWindow {
                background-color: #ffffff;
            }
        """)
    
    def setup_menu_bar(self):
        """设置Win11风格菜单栏"""
        menubar = self.menuBar()
        menubar.setStyleSheet("""
            QMenuBar {
                background-color: #f9f9f9;
                color: #323130;
                border-bottom: 1px solid #e5e5e5;
                font-family: 'Segoe UI';
                font-size: 13px;
                padding: 4px;
            }
            QMenuBar::item {
                background: transparent;
                padding: 8px 16px;
                border-radius: 4px;
            }
            QMenuBar::item:selected {
                background-color: #f3f2f1;
            }
            QMenuBar::item:pressed {
                background-color: #edebe9;
            }
        """)
        
        # 文件菜单
        file_menu = menubar.addMenu("文件")
        
        # 编辑菜单
        edit_menu = menubar.addMenu("编辑")
        
        # 视图菜单
        view_menu = menubar.addMenu("视图")
        
        # 工具菜单
        tools_menu = menubar.addMenu("工具")
        
        # 帮助菜单
        help_menu = menubar.addMenu("帮助")
    
    def setup_status_bar(self):
        """设置Win11风格状态栏"""
        status_bar = self.statusBar()
        status_bar.setStyleSheet("""
            QStatusBar {
                background-color: #f9f9f9;
                color: #605e5c;
                border-top: 1px solid #e5e5e5;
                font-size: 12px;
                font-family: 'Segoe UI';
                padding: 4px 16px;
            }
        """)
        
        # 左侧信息
        self.status_label = QLabel("就绪")
        status_bar.addWidget(self.status_label)
        
        # 右侧上下文信息
        self.context_label = QLabel("质量: 73%")
        status_bar.addPermanentWidget(self.context_label)
        
        # 连接信号
        self.control_panel.quality_slider.valueChanged.connect(
            lambda v: self.context_label.setText(f"质量: {v}%")
        )
    
    def restore_window_state(self):
        """恢复窗口状态"""
        geometry = self.settings.value("geometry")
        if geometry:
            self.restoreGeometry(geometry)
        else:
            self.setGeometry(200, 200, 1200, 800)
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
        self.status_label.setText("正在转换...")
        self.real_conversion()
    
    def simulate_conversion(self):
        """模拟转换过程 - 带Win11动画"""
        self.progress_timer = QTimer()
        self.progress_value = 0
        
        def update_progress():
            self.progress_value += 5
            self.control_panel.set_progress(self.progress_value)
            
            if self.progress_value >= 100:
                self.progress_timer.stop()
                self.status_label.setText("转换完成")
                QTimer.singleShot(2000, lambda: self.control_panel.set_progress(0))
                QTimer.singleShot(2000, lambda: self.status_label.setText("就绪"))
        
        self.progress_timer.timeout.connect(update_progress)
        self.progress_timer.start(100)  # 更平滑的动画
    
    def real_conversion(self):
        """真正的图片转换过程"""
        # 获取Markdown文本
        markdown_text = self.editor.toPlainText().strip()
        
        if not markdown_text:
            QMessageBox.information(self, "提示", "请先输入Markdown内容")
            self.status_label.setText("就绪")
            return
        
        # 获取当前文件目录，如果没有文件则使用当前目录
        if hasattr(self, 'current_file') and self.current_file:
            base_dir = os.path.dirname(self.current_file)
        else:
            base_dir = os.getcwd()
        
        # 创建images目录
        output_dir = os.path.join(base_dir, "images")
        
        # 获取质量设置
        quality = self.control_panel.quality_value
        
        # 重置压缩统计
        self.control_panel.reset_compression_stats()
        
        # 禁用转换按钮
        self.control_panel.convert_btn.setEnabled(False)
        self.control_panel.convert_btn.setText("转换中...")
        
        # 创建并启动转换线程
        self.conversion_worker = ConversionWorker(markdown_text, output_dir, quality)
        self.conversion_worker.progress_updated.connect(self.on_conversion_progress)
        self.conversion_worker.conversion_finished.connect(self.on_conversion_finished)
        self.conversion_worker.conversion_error.connect(self.on_conversion_error)
        self.conversion_worker.start()
    
    def on_conversion_progress(self, progress, message):
        """转换进度更新"""
        self.control_panel.set_progress(progress)
        self.status_label.setText(message)
    
    def on_conversion_finished(self, new_markdown, count, stats):
        """转换完成"""
        # 更新编辑器内容
        self.editor.setPlainText(new_markdown)
        
        # 更新压缩统计
        self.control_panel.update_compression_stats(stats)
        
        # 重置UI状态
        self.control_panel.convert_btn.setEnabled(True)
        self.control_panel.convert_btn.setText("转换")
        self.control_panel.set_progress(0)
        self.status_label.setText(f"转换完成！成功转换 {count} 张图片")
        
        # 格式化统计信息用于显示
        def format_size(size_bytes):
            if size_bytes == 0:
                return "0 B"
            for unit in ['B', 'KB', 'MB', 'GB']:
                if size_bytes < 1024:
                    return f"{size_bytes:.1f} {unit}"
                size_bytes /= 1024
            return f"{size_bytes:.1f} TB"
        
        original_size = stats.get('total_original_size', 0)
        saved_size = stats.get('size_saved', 0)
        compression_ratio = stats.get('compression_ratio', 0)
        
        # 显示完成消息，包含压缩统计
        message = f"成功转换 {count} 张图片为WebP格式！\n\n"
        if original_size > 0:
            message += f"原始大小: {format_size(original_size)}\n"
            message += f"节省空间: {format_size(saved_size)}\n"
            message += f"压缩比例: {compression_ratio:.1f}%\n\n"
        message += "图片已保存到 images 目录。"
        
        QMessageBox.information(self, "转换完成", message)
    
    def on_conversion_error(self, error_message):
        """转换错误"""
        # 重置UI状态
        self.control_panel.convert_btn.setEnabled(True)
        self.control_panel.convert_btn.setText("转换")
        self.control_panel.set_progress(0)
        self.status_label.setText("转换失败")
        
        # 显示错误消息
        QMessageBox.critical(self, "转换失败", error_message)
