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
    QSizePolicy, QApplication, QGraphicsDropShadowEffect, QToolBar
)
from PyQt6.QtCore import Qt, QTimer, QSize, pyqtSignal, QSettings, QRect, QPoint, QPropertyAnimation, QEasingCurve, QThread
from PyQt6.QtGui import QFont, QAction, QPalette, QColor, QPixmap, QPainter, QScreen, QCursor, QIcon
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

# FontAwesome 图标支持（qtawesome）
try:
    import qtawesome as qta
except Exception:
    qta = None

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
        self.setFixedWidth(260)  # 方案A：更纤细的侧栏宽度
        
        # 应用主题样式
        self.apply_panel_theme()
        
        # 主布局
        main_layout = QVBoxLayout()
        main_layout.setSpacing(16)
        main_layout.setContentsMargins(20, 20, 20, 20)
        
        # 转换按钮 - 方案A：主按钮置顶，随滚动始终可见
        self.convert_btn = QPushButton("转换")
        self.convert_btn.setFixedHeight(44)
        self.convert_btn.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Fixed)
        self.convert_btn.setStyleSheet("""
            QPushButton {
                background-color: #16a34a; /* Primary */
                color: white;
                border: 1px solid #16a34a;
                border-radius: 6px;
                font-size: 15px;
                font-family: 'Microsoft YaHei';
                font-weight: 600;
                padding: 8px 14px;
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
        main_layout.addWidget(self.convert_btn)
        
        # 图片质量设置卡片
        quality_card = self.create_quality_card()
        main_layout.addWidget(quality_card)
        
        # 进度显示卡片
        progress_card = self.create_progress_card()
        main_layout.addWidget(progress_card)
        
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
        # 取消卡片边框与阴影，弱化分隔，减少“小框线”感
        card.setStyleSheet("""
            QFrame { background-color: transparent; border: none; }
        """)
        
        layout = QVBoxLayout()
        layout.setContentsMargins(16, 16, 16, 16)
        layout.setSpacing(12)
        
        # 标题
        title = QLabel("图片质量")
        title.setStyleSheet("""
            QLabel { font-size: 14px; font-weight: 700; color: #166534; }
        """)
        layout.addWidget(title)
        
        # 描述
        desc = QLabel("调整WebP压缩质量")
        desc.setStyleSheet("""
            QLabel { font-size: 12px; color: #475569; margin-bottom: 6px; }
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
            QSlider::groove:horizontal { background: #d1fae5; height: 4px; border-radius: 2px; }
            QSlider::sub-page:horizontal { background: #16a34a; border-radius: 2px; }
            QSlider::handle:horizontal { background: #16a34a; width: 18px; height: 18px; border-radius: 9px; margin: -7px 0; }
            QSlider::handle:horizontal:hover { background: #15803d; }
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
        
        # 轻量预设 Chips（中文标签：极缩/常规/轻压/无损）
        chips_grid = QGridLayout()
        chips_grid.setContentsMargins(0, 0, 0, 0)
        chips_grid.setHorizontalSpacing(10)
        chips_grid.setVerticalSpacing(8)
        self.preset_chip_buttons = []
        self.preset_chip_value = {}
        chip_configs = [("极缩", 30), ("常规", 73), ("轻压", 90), ("无损", 100)]
        for i, (label, val) in enumerate(chip_configs):
            chip = QPushButton(label)
            chip.setFixedHeight(30)
            chip.setMinimumWidth(72)
            chip.setCursor(Qt.CursorShape.PointingHandCursor)
            chip.setStyleSheet("""
                QPushButton {
                    background-color: #f8fafc;
                    color: #166534;
                    border: 1px solid #d1fae5;
                    border-radius: 15px;
                    padding: 2px 12px;
                    font-size: 12px;
                    font-weight: 600;
                }
                QPushButton:hover { background-color: #ecfdf5; }
                QPushButton:pressed { background-color: #dcfce7; }
            """)
            chip.clicked.connect(lambda checked, v=val: self.set_quality_preset(v))
            self.preset_chip_buttons.append(chip)
            self.preset_chip_value[chip] = val
            row, col = divmod(i, 2)  # 两行两列
            chips_grid.addWidget(chip, row, col)
        layout.addLayout(chips_grid)
        # 初始化选中态
        self.update_preset_button_states(self.quality_value)
        card.setLayout(layout)
        
        return card
    
    def create_progress_card(self):
        """创建进度显示卡片"""
        card = QFrame()
        card.setFrameStyle(QFrame.Shape.NoFrame)
        # 取消卡片边框与阴影
        card.setStyleSheet("""
            QFrame { background-color: transparent; border: none; }
        """)
        
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
        
        # Win11风格进度条（统一绿色系）
        progress_container = QWidget()
        progress_container.setFixedHeight(60)
        
        progress_layout = QVBoxLayout()
        progress_layout.setContentsMargins(0, 0, 0, 0)
        progress_layout.setSpacing(8)
        
        # 进度条背景（去边框，浅绿色背景）
        self.progress_bg = QWidget()
        self.progress_bg.setFixedHeight(6)
        self.progress_bg.setStyleSheet("""
            QWidget { background-color: #e2f7ec; border-radius: 3px; }
        """)
        
        # 进度条填充
        self.progress_fill = QWidget(self.progress_bg)
        self.progress_fill.setFixedHeight(6)
        self.progress_fill.setFixedWidth(0)  # 初始宽度为0
        self.progress_fill.setStyleSheet("""
            QWidget { background-color: #16a34a; border-radius: 3px; }
        """)
        
        # 进度文本
        self.progress_text = QLabel("准备就绪")
        self.progress_text.setStyleSheet("""
            QLabel {
                font-size: 12px;
                color: #166534;
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
        
        # 更新其他预设按钮状态（旧网格按钮）
        preset_values = [90, 73, 50, 30]
        for i, btn in enumerate(getattr(self, 'preset_buttons', [])):
            if i < len(preset_values) and preset_values[i] == selected_quality and selected_quality != 100:
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
        
        # 更新轻量预设 Chips 选中状态
        for chip in getattr(self, 'preset_chip_buttons', []):
            value = getattr(self, 'preset_chip_value', {}).get(chip, None)
            if value is None:
                continue
            if value == selected_quality:
                chip.setStyleSheet("""
                    QPushButton {
                        background-color: #dcfce7;
                        color: #166534;
                        border: 2px solid #16a34a;
                        border-radius: 14px;
                        padding: 2px 10px;
                        font-size: 12px;
                        font-weight: 700;
                    }
                """)
            else:
                chip.setStyleSheet("""
                    QPushButton {
                        background-color: #f8fafc;
                        color: #166534;
                        border: 1px solid #d1fae5;
                        border-radius: 14px;
                        padding: 2px 10px;
                        font-size: 12px;
                        font-weight: 600;
                    }
                    QPushButton:hover { background-color: #ecfdf5; }
                    QPushButton:pressed { background-color: #dcfce7; }
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
        # 方案A：右侧仅保留质量与进度。若统计控件不存在，则直接跳过更新。
        if not hasattr(self, 'original_size_label'):
            return
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
        if hasattr(self, 'original_size_label'):
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

        # 顶部 Hero 区（方案A）：价值主张 + 大按钮
        hero = self.create_hero_bar()
        container_layout.addWidget(hero)
        
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

        # 底部吸附提示条
        hint_bar = self.create_bottom_hint_bar()
        container_layout.addWidget(hint_bar)
        
        main_container.setLayout(container_layout)
        
        # 连接信号
        self.control_panel.convert_btn.clicked.connect(self.on_convert_clicked)
        
        # 工具栏（右上角主题切换图标）
        self.create_toolbar()

        # 设置主题样式（支持明暗切换，读取上次选择）
        self.current_theme_dark = self.settings.value("themeDark", False, type=bool)
        self.apply_theme(self.current_theme_dark)

    def apply_theme(self, dark: bool):
        """根据主题开关设置全局与局部样式"""
        if dark:
            # 深色
            self.setStyleSheet("""
                QMainWindow { background-color: #0f172a; }
                QMenuBar { background-color: #111827; color: #e5e7eb; border: none; }
                QMenuBar::item:selected { background-color: #1f2937; }
            """)
            # 编辑器深色
            self.editor.is_dark_theme = True
            self.editor.apply_theme_style()
            # 控制面板深色
            self.control_panel.is_dark_theme = True
            self.control_panel.apply_panel_theme()
            # 更新内部控件色值
            self.control_panel.progress_text.setStyleSheet("QLabel{color:#e5e7eb;font-size:12px;}")
            # 顶部Hero与底部提示
            if hasattr(self, 'hero_frame'):
                self.hero_frame.setStyleSheet("QFrame{background-color:#111827;border-bottom:1px solid #1f2937;}")
            if hasattr(self, 'hero_title_label'):
                self.hero_title_label.setStyleSheet("QLabel{color:#f9fafb;font-size:18px;font-weight:700;}")
            if hasattr(self, 'hero_subtitle_label'):
                self.hero_subtitle_label.setStyleSheet("QLabel{color:#9ca3af;font-size:12px;}")
            if hasattr(self, 'hint_bar'):
                self.hint_bar.setStyleSheet("QFrame{background-color:#0b1220;border-top:1px solid #1f2937;}")
            if hasattr(self, 'hint_label'):
                self.hint_label.setStyleSheet("QLabel{color:#94a3b8;font-size:12px;}")
            self.update_icons(True)
        else:
            # 浅色
            self.setStyleSheet("""
                QMainWindow { background-color: #ffffff; }
                QMenuBar { background-color: #f9f9f9; color: #323130; border-bottom: 1px solid #e5e5e5; }
                QMenuBar::item:selected { background-color: #f3f2f1; }
            """)
            self.editor.is_dark_theme = False
            self.editor.apply_theme_style()
            self.control_panel.is_dark_theme = False
            self.control_panel.apply_panel_theme()
            self.control_panel.progress_text.setStyleSheet("QLabel{color:#166534;font-size:12px;}")
            if hasattr(self, 'hero_frame'):
                self.hero_frame.setStyleSheet("QFrame{background-color:#E8F5E9;border-bottom:1px solid #e5e5e5;}")
            if hasattr(self, 'hero_title_label'):
                self.hero_title_label.setStyleSheet("QLabel{color:#065f46;font-size:18px;font-weight:700;}")
            if hasattr(self, 'hero_subtitle_label'):
                self.hero_subtitle_label.setStyleSheet("QLabel{color:#0f766e;font-size:12px;}")
            if hasattr(self, 'hint_bar'):
                self.hint_bar.setStyleSheet("QFrame{background-color:#f8fafc;border-top:1px solid #e5e5e5;}")
            if hasattr(self, 'hint_label'):
                self.hint_label.setStyleSheet("QLabel{color:#334155;font-size:12px;}")
            self.update_icons(False)
        # 重新渲染质量/预设等控件样式
        self.control_panel.update_preset_button_states(self.control_panel.quality_value)
        # 更新工具栏图标
        if hasattr(self, 'theme_action'):
            self.theme_action.setText('☀️' if dark else '🌙')
            self.theme_action.setToolTip('切换到浅色' if dark else '切换到深色')

    def create_hero_bar(self) -> QWidget:
        """方案A：顶部 Hero 条，包含标题、副标题和开始转换按钮"""
        hero = QFrame()
        hero.setFixedHeight(76)
        # 改为更柔和的浅色单色背景，避免突兀渐变
        hero.setStyleSheet("""
            QFrame {
                background-color: #E8F5E9; /* 淡绿背景 */
                border-bottom: 1px solid #e5e5e5;
            }
        """)
        layout = QHBoxLayout()
        layout.setContentsMargins(16, 12, 16, 12)
        layout.setSpacing(16)

        title = QLabel("Markdown 图片一键压缩为 WebP")
        title.setStyleSheet("""
            QLabel { color: #065f46; font-size: 18px; font-weight: 700; }
        """)

        subtitle = QLabel("粘贴或打开 Markdown，右侧调质量，点击开始转换")
        subtitle.setStyleSheet("""
            QLabel { color: #0f766e; font-size: 12px; }
        """)

        text_block = QWidget()
        v = QVBoxLayout()
        v.setContentsMargins(0, 0, 0, 0)
        v.setSpacing(4)
        v.addWidget(title)
        v.addWidget(subtitle)
        text_block.setLayout(v)

        start_btn = QPushButton("开始转换")
        start_btn.setFixedHeight(36)
        start_btn.setFixedWidth(120)
        start_btn.setStyleSheet("""
            QPushButton {
                background-color: #16a34a;
                color: #ffffff;
                border: 1px solid #16a34a;
                border-radius: 6px;
                font-size: 14px;
                font-weight: 600;
                padding: 6px 16px;
            }
            QPushButton:hover { background-color: #15803d; border-color: #15803d; }
            QPushButton:pressed { background-color: #166534; border-color: #166534; }
        """)
        start_btn.clicked.connect(self.on_convert_clicked)

        layout.addWidget(text_block, 1)
        layout.addStretch()
        layout.addWidget(start_btn, 0, Qt.AlignmentFlag.AlignVCenter)
        hero.setLayout(layout)
        return hero

    def create_bottom_hint_bar(self) -> QWidget:
        """方案A：底部吸附提示条，引导拖拽/粘贴"""
        bar = QFrame()
        bar.setFixedHeight(34)
        bar.setStyleSheet("""
            QFrame {
                background-color: #f8fafc;
                border-top: 1px solid #e5e5e5;
            }
        """)
        layout = QHBoxLayout()
        layout.setContentsMargins(12, 6, 12, 6)
        layout.setSpacing(8)
        hint = QLabel("提示：可拖拽 Markdown 文件进来，或直接 Ctrl+V 粘贴内容")
        hint.setStyleSheet("""
            QLabel { color: #334155; font-size: 12px; }
        """)
        layout.addWidget(hint)
        layout.addStretch()
        bar.setLayout(layout)
        return bar
    
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

    def create_toolbar(self):
        """顶端工具栏：右侧加入主题切换图标"""
        toolbar = QToolBar("toolbar")
        toolbar.setMovable(False)
        toolbar.setFloatable(False)
        toolbar.setIconSize(QSize(18, 18))
        toolbar.setStyleSheet("QToolBar{background:transparent;border:0px;padding:0px 6px;}")
        self.addToolBar(Qt.ToolBarArea.TopToolBarArea, toolbar)

        # 左侧常用动作
        self.open_action = QAction("打开", self)
        self.open_action.setStatusTip("打开 Markdown 文件")
        self.open_action.triggered.connect(self.open_markdown_file)
        toolbar.addAction(self.open_action)

        self.paste_action = QAction("粘贴", self)
        self.paste_action.setStatusTip("从剪贴板粘贴 Markdown")
        self.paste_action.triggered.connect(self.paste_from_clipboard)
        toolbar.addAction(self.paste_action)

        self.clear_action = QAction("清空", self)
        self.clear_action.setStatusTip("清空编辑器")
        self.clear_action.triggered.connect(self.clear_editor)
        toolbar.addAction(self.clear_action)

        spacer = QWidget()  # 拉伸把右侧图标推到最右
        spacer.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Preferred)
        toolbar.addWidget(spacer)

        self.theme_action = QAction('🌙', self)
        self.theme_action.setToolTip('切换到深色')
        self.theme_action.triggered.connect(self.toggle_theme)
        toolbar.addAction(self.theme_action)
    
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

    def toggle_theme(self):
        """切换浅色/深色主题"""
        self.current_theme_dark = not self.current_theme_dark
        self.apply_theme(self.current_theme_dark)
        # 持久化
        self.settings.setValue("themeDark", self.current_theme_dark)

    # ===== 额外功能：文件/粘贴/清空 =====
    def open_markdown_file(self):
        path, _ = QFileDialog.getOpenFileName(self, "打开 Markdown", os.getcwd(), "Markdown (*.md *.markdown);;所有文件 (*.*)")
        if not path:
            return
        try:
            with open(path, 'r', encoding='utf-8') as f:
                text = f.read()
        except Exception:
            with open(path, 'r', encoding='gbk', errors='ignore') as f:
                text = f.read()
        self.editor.setPlainText(text)
        self.current_file = path
        self.status_label.setText(f"已打开: {os.path.basename(path)}")

    def paste_from_clipboard(self):
        cb = QApplication.clipboard()
        text = cb.text()
        if text:
            self.editor.insertPlainText(text)
            self.status_label.setText("已粘贴剪贴板内容")

    def clear_editor(self):
        self.editor.clear()
        self.status_label.setText("编辑器已清空")

    def update_icons(self, dark: bool):
        """根据主题更新 FontAwesome 图标（若可用）"""
        if qta is None:
            return
        # 主题图标
        theme_icon = qta.icon('fa5s.sun', color='#fde68a') if dark else qta.icon('fa5s.moon', color='#111827')
        self.theme_action.setIcon(theme_icon)
        # 工具栏图标
        common_color = '#e5e7eb' if dark else '#111827'
        if hasattr(self, 'open_action'):
            self.open_action.setIcon(qta.icon('fa5s.folder-open', color=common_color))
        if hasattr(self, 'paste_action'):
            self.paste_action.setIcon(qta.icon('fa5s.paste', color=common_color))
        if hasattr(self, 'clear_action'):
            self.clear_action.setIcon(qta.icon('fa5s.trash-alt', color=common_color))
        # 转换主按钮图标
        self.control_panel.convert_btn.setIcon(qta.icon('fa5s.play', color='#ffffff'))
        self.control_panel.convert_btn.setIconSize(QSize(16, 16))
    
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
