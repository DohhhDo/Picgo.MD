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
    QSizePolicy, QApplication, QGraphicsDropShadowEffect, QToolBar,
    QDialog, QTabWidget, QComboBox, QLineEdit, QCheckBox, QDialogButtonBox, QScrollArea
)
from PyQt6.QtCore import Qt, QTimer, QSize, pyqtSignal, QSettings, QRect, QPoint, QPropertyAnimation, QEasingCurve
from PyQt6.QtGui import QFont, QAction, QPalette, QColor, QPixmap, QPainter, QScreen, QCursor, QIcon
import sys
import os
from pathlib import Path
import re

# 添加core模块路径
current_dir = Path(__file__).parent.parent
sys.path.insert(0, str(current_dir))

try:
    from core.image_converter import convert_markdown_images
except ImportError:
    print("Warning: 无法导入图片转换模块")
    convert_markdown_images = None

from .utils import detect_system_theme_default_dark, format_size_human
from .workers import ConversionWorker, UploadWorker
from .components.markdown_editor import Win11MarkdownEditor
from .components.control_panel import Win11ControlPanel
from .dialogs.image_bed_dialog import ImageBedDialog
from .themes.tokens import DARK_TOKENS, LIGHT_TOKENS
from .components.markdown_editor import Win11MarkdownEditor
from .components.control_panel import Win11ControlPanel

# FontAwesome 图标支持（qtawesome）
try:
    import qtawesome as qta
except Exception:
    qta = None

from .workers import ConversionWorker, UploadWorker


# 已迁移到 ui/components/markdown_editor.py

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
        
        # 转换按钮 - 次按钮（描边款），仅保留顶部Hero为唯一主CTA
        self.convert_btn = QPushButton("转换")
        self.convert_btn.setFixedHeight(44)
        self.convert_btn.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Fixed)
        self.convert_btn.setStyleSheet("""
            QPushButton {
                background: transparent;
                color: #16a34a;
                border: 1.5px solid #16a34a;
                border-radius: 8px;
                font-size: 15px;
                font-family: 'Microsoft YaHei';
                font-weight: 600;
                padding: 8px 14px;
            }
            QPushButton:hover { background-color: #ecfdf5; }
            QPushButton:pressed { background-color: #dcfce7; }
        """)
        main_layout.addWidget(self.convert_btn)
        
        # 上传按钮（与转换分步）
        self.upload_btn = QPushButton("上传")
        self.upload_btn.setFixedHeight(40)
        self.upload_btn.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Fixed)
        self.upload_btn.setStyleSheet("""
            QPushButton {
                background: transparent;
                color: #0f766e;
                border: 1.5px solid #0f766e;
                border-radius: 8px;
                font-size: 14px;
                font-family: 'Microsoft YaHei';
                font-weight: 600;
                padding: 6px 12px;
            }
            QPushButton:hover { background-color: #ecfeff; }
            QPushButton:pressed { background-color: #cffafe; }
        """)
        main_layout.addWidget(self.upload_btn)
        
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
        # tokens 用于主题化
        self.tokens = None

    def apply_tokens(self, tokens: dict):
        """应用主题 tokens 到控制面板各控件（方案2.1 Clean Contrast）"""
        self.tokens = tokens
        # 主转换按钮
        self.convert_btn.setStyleSheet(f"""
            QPushButton {{
                background-color: {tokens['primary']};
                color: white;
                border: 1px solid {tokens['primary']};
                border-radius: 6px;
                font-size: 15px;
                font-family: 'Microsoft YaHei';
                font-weight: 600;
                padding: 8px 14px;
            }}
            QPushButton:hover {{ background-color: {tokens['primary_hover']}; border-color: {tokens['primary_hover']}; }}
            QPushButton:pressed {{ background-color: {tokens['primary_press']}; border-color: {tokens['primary_press']}; }}
        """)
        # 上传按钮（次要描边款）
        if hasattr(self, 'upload_btn'):
            self.upload_btn.setStyleSheet(f"""
                QPushButton {{
                    background: transparent;
                    color: {tokens['text']};
                    border: 1px solid {tokens['border']};
                    border-radius: 6px;
                    font-size: 14px;
                    font-family: 'Microsoft YaHei';
                    font-weight: 600;
                    padding: 6px 12px;
                }}
                QPushButton:hover {{ background-color: {tokens['chip_hover_bg']}; border-color: {tokens['chip_border']}; }}
                QPushButton:pressed {{ background-color: {tokens['chip_pressed_bg']}; border-color: {tokens['chip_border']}; }}
            """)

        # 质量百分比徽标
        self.quality_label.setStyleSheet(f"""
            QLabel {{
                background-color: {tokens['quality_badge_bg']};
                color: {tokens['quality_badge_text']};
                border: 1px solid {tokens['quality_badge_border']};
                border-radius: 6px;
                padding: 0px 8px;
                font-size: 13px;
                font-weight: 700;
                font-family: 'Consolas','Microsoft YaHei';
            }}
        """)

        # 滑杆样式
        self.quality_slider.setStyleSheet(f"""
            QSlider::groove:horizontal {{ background: {tokens['slider_track']}; height: 4px; border-radius: 2px; }}
            QSlider::sub-page:horizontal {{ background: {tokens['slider_fill']}; border-radius: 2px; }}
            QSlider::handle:horizontal {{ background: {tokens['slider_fill']}; width: 18px; height: 18px; border-radius: 9px; margin: -7px 0; }}
            QSlider::handle:horizontal:hover {{ background: {tokens['primary_hover']}; }}
        """)

        # 进度条
        if hasattr(self, 'progress_bg'):
            self.progress_bg.setStyleSheet(f"QWidget {{ background-color: {tokens['progress_bg']}; border-radius: 3px; }}")
        if hasattr(self, 'progress_fill'):
            self.progress_fill.setStyleSheet(f"QWidget {{ background-color: {tokens['progress_fill']}; border-radius: 3px; }}")
        if hasattr(self, 'progress_text'):
            self.progress_text.setStyleSheet(f"QLabel {{ color: {tokens['progress_text']}; font-size: 12px; }}")

        # 预设未选中样式
        for chip in getattr(self, 'preset_chip_buttons', []):
            chip.setStyleSheet(f"""
                QPushButton {{
                    background-color: {tokens['chip_bg']};
                    color: {tokens['chip_text']};
                    border: 1px solid {tokens['chip_border']};
                    border-radius: 15px;
                    padding: 2px 12px;
                    font-size: 12px; font-weight: 600;
                }}
                QPushButton:hover {{ background-color: {tokens['chip_hover_bg']}; }}
                QPushButton:pressed {{ background-color: {tokens['chip_pressed_bg']}; }}
            """)
        # 选中态刷新
        self.update_preset_button_states(self.quality_value)
    
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
        tokens = getattr(self, 'tokens', {}) or {}
        for chip in getattr(self, 'preset_chip_buttons', []):
            value = getattr(self, 'preset_chip_value', {}).get(chip, None)
            if value is None:
                continue
            if value == selected_quality:
                chip.setStyleSheet(f"""
                    QPushButton {{
                        background-color: {tokens.get('chip_selected_bg', '#dcfce7')};
                        color: {tokens.get('chip_selected_text', '#166534')};
                        border: 2px solid {tokens.get('chip_selected_border', '#16a34a')};
                        border-radius: 15px;
                        padding: 2px 12px;
                        font-size: 12px; font-weight: 700;
                    }}
                """)
            else:
                chip.setStyleSheet(f"""
                    QPushButton {{
                        background-color: {tokens.get('chip_bg', '#f8fafc')};
                        color: {tokens.get('chip_text', '#166534')};
                        border: 1px solid {tokens.get('chip_border', '#d1fae5')};
                        border-radius: 15px;
                        padding: 2px 12px;
                        font-size: 12px; font-weight: 600;
                    }}
                    QPushButton:hover {{ background-color: {tokens.get('chip_hover_bg', '#ecfdf5')}; }}
                    QPushButton:pressed {{ background-color: {tokens.get('chip_pressed_bg', '#dcfce7')}; }}
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
        from .utils import format_size_human as _fmt
        
        original_size = stats.get('total_original_size', 0)
        compressed_size = stats.get('total_converted_size', 0)
        saved_size = stats.get('size_saved', 0)
        compression_ratio = stats.get('compression_ratio', 0)
        
        self.original_size_label.setText(f"原始大小: {_fmt(original_size)}")
        self.compressed_size_label.setText(f"压缩后: {_fmt(compressed_size)}")
        self.saved_size_label.setText(f"节省空间: {_fmt(saved_size)}")
        self.compression_ratio_label.setText(f"压缩比例: {compression_ratio:.1f}%")
    
    def reset_compression_stats(self):
        """重置压缩统计信息"""
        if hasattr(self, 'original_size_label'):
            self.original_size_label.setText("原始大小: --")
        if hasattr(self, 'compressed_size_label'):
            self.compressed_size_label.setText("压缩后: --")
        if hasattr(self, 'saved_size_label'):
            self.saved_size_label.setText("节省空间: --")
        if hasattr(self, 'compression_ratio_label'):
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
        self._debug_ui = True
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
        # 让编辑器左侧与窗口留白（仅左边 12px）
        content_layout.setContentsMargins(12, 0, 0, 0)
        content_layout.setSpacing(1)  # Win11分割线宽度
        
        # 创建分割器
        self.splitter = QSplitter(Qt.Orientation.Horizontal)
        self.splitter.setHandleWidth(1)
        # 分割线颜色在主题中统一更新，这里设置默认较柔的浅色
        self.splitter.setStyleSheet("QSplitter::handle{background-color:#e5e5e5;}")
        
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
        self.hint_bar = hint_bar
        container_layout.addWidget(hint_bar)
        
        main_container.setLayout(container_layout)
        
        # 连接信号（显式断开后再连接，避免重复/混乱）
        try:
            self.control_panel.convert_btn.clicked.disconnect()
        except Exception:
            pass
        self.control_panel.convert_btn.clicked.connect(self.on_convert_clicked)
        if hasattr(self.control_panel, 'upload_btn'):
            try:
                self.control_panel.upload_btn.clicked.disconnect()
            except Exception:
                pass
            self.control_panel.upload_btn.clicked.connect(self.on_upload_clicked)
        
        # 跟随系统主题（不提供手动切换）
        self.current_theme_dark = self.detect_system_theme()
        self.apply_theme(self.current_theme_dark)

    def detect_system_theme(self) -> bool:
        """检测系统主题：True=深色，False=浅色"""
        try:
            import winreg
            registry = winreg.ConnectRegistry(None, winreg.HKEY_CURRENT_USER)
            key = winreg.OpenKey(registry, r"SOFTWARE\Microsoft\Windows\CurrentVersion\Themes\Personalize")
            value, _ = winreg.QueryValueEx(key, "AppsUseLightTheme")
            winreg.CloseKey(key)
            return value == 0
        except Exception:
            return False

    def apply_theme(self, dark: bool):
        """根据主题开关设置全局与局部样式"""
        if dark:
            # tokens - Clean Contrast (Dark)
            tokens = {
                'bg': '#0D1117', 'surface': '#111827', 'text': '#E5E7EB', 'subtext': '#9CA3AF', 'border': '#1F2937',
                'primary': '#16A34A', 'primary_hover': '#15803D', 'primary_press': '#166534',
                'quality_badge_bg': '#0B1220', 'quality_badge_border': '#173D2A', 'quality_badge_text': '#86EFAC',
                'slider_track': '#1F2937', 'slider_fill': '#16A34A',
                'progress_bg': '#1F2937', 'progress_fill': '#16A34A', 'progress_text': '#E5E7EB',
                'chip_bg': '#0D1E14', 'chip_text': '#86EFAC', 'chip_border': '#173D2A',
                'chip_hover_bg': '#0F2318', 'chip_pressed_bg': '#10331F',
                'chip_selected_bg': '#10331F', 'chip_selected_text': '#86EFAC', 'chip_selected_border': '#16A34A'
            }
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
            # 应用 tokens 到右栏
            self.control_panel.apply_tokens(tokens)
            # Hero 颜色与按钮样式
            if hasattr(self, 'hero_frame'):
                self.hero_frame.setStyleSheet("QFrame{background-color:#111827;border-bottom:1px solid #1f2937;}")
            if hasattr(self, 'hero_title_label'):
                self.hero_title_label.setStyleSheet("QLabel{color:#f9fafb;font-size:18px;font-weight:700;}")
            if hasattr(self, 'hero_subtitle_label'):
                self.hero_subtitle_label.setStyleSheet("QLabel{color:#9ca3af;font-size:12px;}")
            for btn in [getattr(self,'hero_open_btn',None), getattr(self,'hero_paste_btn',None), getattr(self,'hero_clear_btn',None)]:
                if btn is not None:
                    btn.setStyleSheet("QToolButton{color:#E5E7EB;background:transparent;border:none;padding:2px 8px;} QToolButton:hover{background:#1f2937;border-radius:4px;}")
            if hasattr(self, 'hero_start_btn'):
                self.hero_start_btn.setStyleSheet(
                    """
                    QPushButton { background-color: #16a34a; color: #ffffff; border: 1px solid #16a34a; border-radius: 8px; font-size: 14px; font-weight: 600; padding: 6px 16px; }
                    QPushButton:hover { background-color: #15803d; border-color: #15803d; }
                    QPushButton:pressed { background-color: #166534; border-color: #166534; }
                    """
                )
            # 底部状态栏与提示条同步深色
            if hasattr(self, 'status_bar'):
                self.status_bar.setStyleSheet(
                    "QStatusBar{background-color:#0F141A;color:#E6EAF0;border-top:1px solid #1F2937;padding:4px 16px;font-size:12px;}"
                )
            # 分割线更暗，避免过亮
            if hasattr(self, 'splitter'):
                self.splitter.setStyleSheet("QSplitter::handle{background-color:#1F2937;}")
        else:
            # tokens - Clean Contrast (Light)
            tokens = {
                'bg': '#F6F8FA', 'surface': '#FFFFFF', 'text': '#0F172A', 'subtext': '#475569', 'border': '#E5E7EB',
                'primary': '#16A34A', 'primary_hover': '#15803D', 'primary_press': '#166534',
                'quality_badge_bg': '#ECFDF5', 'quality_badge_border': '#A7F3D0', 'quality_badge_text': '#065F46',
                'slider_track': '#D1FAE5', 'slider_fill': '#16A34A',
                'progress_bg': '#E2F7EC', 'progress_fill': '#16A34A', 'progress_text': '#166534',
                'chip_bg': '#F8FAFC', 'chip_text': '#166534', 'chip_border': '#D1FAE5',
                'chip_hover_bg': '#ECFDF5', 'chip_pressed_bg': '#DCFCE7',
                'chip_selected_bg': '#DCFCE7', 'chip_selected_text': '#166534', 'chip_selected_border': '#16A34A'
            }
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
            # 应用 tokens 到右栏
            self.control_panel.apply_tokens(tokens)
            # Hero 颜色与按钮样式
            if hasattr(self, 'hero_frame'):
                self.hero_frame.setStyleSheet("QFrame{background-color:#E8F5E9;border-bottom:1px solid #e5e5e5;}")
            if hasattr(self, 'hero_title_label'):
                self.hero_title_label.setStyleSheet("QLabel{color:#065f46;font-size:18px;font-weight:700;}")
            if hasattr(self, 'hero_subtitle_label'):
                self.hero_subtitle_label.setStyleSheet("QLabel{color:#0f766e;font-size:12px;}")
            for btn in [getattr(self,'hero_open_btn',None), getattr(self,'hero_paste_btn',None), getattr(self,'hero_clear_btn',None)]:
                if btn is not None:
                    btn.setStyleSheet("QToolButton{color:#065f46;background:#ECFDF5;border:1px solid #A7F3D0;border-radius:6px;padding:2px 8px;} QToolButton:hover{background:#DCFCE7;}")
            if hasattr(self, 'hero_start_btn'):
                self.hero_start_btn.setStyleSheet(
                    """
                    QPushButton { background-color: #16a34a; color: #ffffff; border: 1px solid #16a34a; border-radius: 8px; font-size: 14px; font-weight: 600; padding: 6px 16px; }
                    QPushButton:hover { background-color: #15803d; border-color: #15803d; }
                    QPushButton:pressed { background-color: #166534; border-color: #166534; }
                    """
                )
            # 底部状态栏浅色
            if hasattr(self, 'status_bar'):
                self.status_bar.setStyleSheet(
                    "QStatusBar{background-color:#FFFFFF;color:#605e5c;border-top:1px solid #e5e5e5;padding:4px 16px;font-size:12px;}"
                )
            # 分割线更柔和
            if hasattr(self, 'splitter'):
                self.splitter.setStyleSheet("QSplitter::handle{background-color:#e2e8f0;}")
        # 重新渲染质量/预设等控件样式
        self.control_panel.update_preset_button_states(self.control_panel.quality_value)
        # 无手动切换，故不更新切换图标

    def create_hero_bar(self) -> QWidget:
        """方案A：顶部 Hero 条，包含标题、副标题和开始转换按钮"""
        hero = QFrame()
        # 让头部区域根据内容自适应高度（不再固定）
        hero.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Minimum)
        # 使用 tokens 的 surfaceMuted，避免大面积绿色
        self.hero_frame = hero
        layout = QHBoxLayout()
        # 合理的上下内边距，保证文字不被裁切
        layout.setContentsMargins(16, 12, 16, 12)
        layout.setSpacing(8)

        title = QLabel("Markdown 图片一键压缩为 WebP")
        self.hero_title_label = title

        subtitle = QLabel("粘贴或打开 Markdown，右侧调质量，点击开始转换")
        self.hero_subtitle_label = subtitle

        text_block = QWidget()
        v = QVBoxLayout()
        v.setContentsMargins(0, 0, 0, 0)
        v.setSpacing(4)
        v.addWidget(title)
        v.addWidget(subtitle)
        # Hero 内的动作行：打开 / 粘贴 / 清空（紧凑款）
        actions_row = QHBoxLayout()
        actions_row.setContentsMargins(0, 0, 0, 0)
        actions_row.setSpacing(6)
        from PyQt6.QtWidgets import QToolButton
        self.hero_open_btn = QToolButton()
        self.hero_open_btn.setText("打开")
        self.hero_open_btn.setFixedHeight(26)
        self.hero_open_btn.setToolButtonStyle(Qt.ToolButtonStyle.ToolButtonTextOnly)
        self.hero_open_btn.clicked.connect(self.open_markdown_file)
        self.hero_paste_btn = QToolButton()
        self.hero_paste_btn.setText("粘贴")
        self.hero_paste_btn.setFixedHeight(26)
        self.hero_paste_btn.setToolButtonStyle(Qt.ToolButtonStyle.ToolButtonTextOnly)
        self.hero_paste_btn.clicked.connect(self.paste_from_clipboard)
        self.hero_clear_btn = QToolButton()
        self.hero_clear_btn.setText("清空")
        self.hero_clear_btn.setFixedHeight(26)
        self.hero_clear_btn.setToolButtonStyle(Qt.ToolButtonStyle.ToolButtonTextOnly)
        self.hero_clear_btn.clicked.connect(self.clear_editor)
        # 新增：图床入口
        self.hero_imagebed_btn = QToolButton()
        self.hero_imagebed_btn.setText("图床")
        self.hero_imagebed_btn.setFixedHeight(26)
        self.hero_imagebed_btn.setToolButtonStyle(Qt.ToolButtonStyle.ToolButtonTextOnly)
        self.hero_imagebed_btn.clicked.connect(self.open_image_bed_dialog)
        actions_row.addWidget(self.hero_open_btn)
        actions_row.addWidget(self.hero_paste_btn)
        actions_row.addWidget(self.hero_clear_btn)
        actions_row.addWidget(self.hero_imagebed_btn)
        actions_row.addStretch()
        v.addLayout(actions_row)
        text_block.setLayout(v)

        start_btn = QPushButton("开始转换")
        start_btn.setFixedHeight(38)
        start_btn.setFixedWidth(128)
        # 样式由 tokens 注入
        self.hero_start_btn = start_btn
        try:
            start_btn.clicked.disconnect()
        except Exception:
            pass
        start_btn.clicked.connect(self.on_convert_clicked)

        layout.addWidget(text_block, 1)
        layout.addStretch()
        layout.addWidget(start_btn, 0, Qt.AlignmentFlag.AlignVCenter)
        hero.setLayout(layout)
        # 以 sizeHint 作为最小高度，随文字/按钮变化自适应
        try:
            hero.setMinimumHeight(hero.sizeHint().height())
        except Exception:
            pass
        return hero

    def create_bottom_hint_bar(self) -> QWidget:
        """方案A：底部吸附提示条，引导拖拽/粘贴"""
        bar = QFrame()
        bar.setFixedHeight(34)
        layout = QHBoxLayout()
        layout.setContentsMargins(12, 6, 12, 6)
        layout.setSpacing(8)
        hint = QLabel("提示：可拖拽 Markdown 文件进来，或直接 Ctrl+V 粘贴内容")
        self.hint_label = hint
        layout.addWidget(hint)
        layout.addStretch()
        bar.setLayout(layout)
        return bar
    
    def setup_menu_bar(self):
        """设置Win11风格菜单栏"""
        menubar = self.menuBar()
        # 直接隐藏菜单栏（去掉“文件/编辑/视图/工具/帮助”）
        menubar.hide()
        return

    def create_toolbar(self):
        """顶端工具栏：仅保留常用动作 + 图床入口"""
        toolbar = QToolBar("toolbar")
        toolbar.setMovable(False)
        toolbar.setFloatable(False)
        toolbar.setIconSize(QSize(18, 18))
        # 提升工具栏高度，避免与窗口标题区产生视觉挤压/遮挡
        toolbar.setFixedHeight(44)
        toolbar.setStyleSheet(
            "QToolBar{background:transparent;border:0px;padding:6px 8px;min-height:44px;}"
        )
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

        # 图床设置入口
        self.imagebed_action = QAction("图床", self)
        self.imagebed_action.setStatusTip("图床选择与配置")
        self.imagebed_action.triggered.connect(self.open_image_bed_dialog)
        toolbar.addAction(self.imagebed_action)
    
    def setup_status_bar(self):
        """设置Win11风格状态栏"""
        status_bar = self.statusBar()
        # 保存引用以便主题切换时统一控制（修复底部浅色问题）
        self.status_bar = status_bar
        
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

    def on_convert_clicked(self):
        """开始转换（供 Hero 按钮/右侧按钮调用）"""
        self.status_label.setText("正在转换...")
        if getattr(self, '_debug_ui', False):
            try:
                QMessageBox.information(self, "DEBUG", "on_convert_clicked")
            except Exception:
                pass
        try:
            self.real_conversion()
        except Exception as e:
            try:
                import traceback
                QMessageBox.critical(self, "real_conversion 异常", traceback.format_exc())
            except Exception:
                pass

    def on_upload_clicked(self):
        """手动上传：把 images 下的 webp 上传并回写远程 URL"""
        try:
            base_dir = os.path.dirname(self.current_file) if getattr(self, 'current_file', None) else os.getcwd()
            img_dir = os.path.join(base_dir, "images")
            if not os.path.isdir(img_dir):
                QMessageBox.information(self, "提示", "未找到 images 目录，请先执行转换。")
                return
            local_webps = [os.path.join(img_dir, n) for n in os.listdir(img_dir) if n.lower().endswith('.webp')]
            if not local_webps:
                QMessageBox.information(self, "提示", "没有可上传的 WebP 文件。")
                return
            self.status_label.setText("正在上传...")
            self.upload_worker = UploadWorker(base_dir, local_webps)
            self.upload_worker.progress_updated.connect(self.on_conversion_progress)
            def _on_uploaded(mapping: dict):
                md = self.editor.toPlainText()
                new_md = self._replace_local_paths_with_remote(md, base_dir, mapping)
                self.editor.setPlainText(new_md)
                self.status_label.setText("上传完成")
                QMessageBox.information(self, "上传完成", "已将本地图片链接替换为远程 URL")
            self.upload_worker.finished_with_mapping.connect(_on_uploaded)
            self.upload_worker.error.connect(lambda e: QMessageBox.critical(self, "上传失败", e))
            self.upload_worker.start()
        except Exception as e:
            QMessageBox.critical(self, "上传失败", str(e))

    # === 内置一份转换实现，确保方法存在于类上（避免外部重复定义导致找不到） ===
    def real_conversion(self):
        """真正的图片转换过程（类内实现）"""
        markdown_text = self.editor.toPlainText().strip()
        try:
            print("[GUI] real_conversion(cls): text_len=", len(markdown_text), flush=True)
        except Exception:
            pass
        if not markdown_text:
            QMessageBox.information(self, "提示", "请先输入Markdown内容")
            self.status_label.setText("就绪")
            return

        # 预检图片链接
        try:
            import re as _re
            pattern = r'(?:!\[.*?\]\((.*?)\))|(?:<img.*?src=["\']([^"\']*)["\'].*?>)'
            matches = _re.findall(pattern, markdown_text)
            urls = []
            for m in matches:
                u = m[0] or m[1]
                if u and u.strip():
                    urls.append(u.strip())
            if not urls:
                self.control_panel.convert_btn.setEnabled(True)
                self.control_panel.convert_btn.setText("转换")
                self.control_panel.set_progress(0)
                self.status_label.setText("未找到图片链接")
                QMessageBox.information(self, "未找到图片", "未检测到 Markdown 中的图片链接，请确认语法：\n\n![](http://...) 或 <img src=\"...\">")
                return
        except Exception:
            pass

        # 目录 / 质量
        base_dir = os.path.dirname(self.current_file) if getattr(self, 'current_file', None) else os.getcwd()
        output_dir = os.path.join(base_dir, "images")
        quality = getattr(self.control_panel, 'quality_value', 73)

        # 重置统计与UI
        if hasattr(self.control_panel, 'reset_compression_stats'):
            self.control_panel.reset_compression_stats()
        self.control_panel.convert_btn.setEnabled(False)
        self.control_panel.convert_btn.setText("转换中...")

        # 线程执行
        self.conversion_worker = ConversionWorker(markdown_text, output_dir, quality)
        self.conversion_worker.progress_updated.connect(self.on_conversion_progress)
        self.conversion_worker.conversion_finished.connect(self.on_conversion_finished)
        self.conversion_worker.conversion_error.connect(self.on_conversion_error)
        self.conversion_worker.start()

        # 看门狗
        try:
            if hasattr(self, 'conversion_watchdog') and self.conversion_watchdog is not None:
                self.conversion_watchdog.stop()
        except Exception:
            pass
        self.conversion_watchdog = QTimer(self)
        self.conversion_watchdog.setSingleShot(True)
        self.conversion_watchdog.timeout.connect(self.on_conversion_timeout)
        self.conversion_watchdog.start(45000)

    def on_conversion_progress(self, progress, message):
        self.control_panel.set_progress(progress)
        self.status_label.setText(message)
        try:
            if hasattr(self, 'conversion_watchdog') and self.conversion_watchdog is not None:
                self.conversion_watchdog.start(45000)
        except Exception:
            pass

    def on_conversion_finished(self, new_markdown, count, stats):
        try:
            if hasattr(self, 'conversion_watchdog') and self.conversion_watchdog is not None:
                self.conversion_watchdog.stop()
        except Exception:
            pass
        self.editor.setPlainText(new_markdown)
        if hasattr(self.control_panel, 'update_compression_stats'):
            self.control_panel.update_compression_stats(stats)
        self.control_panel.convert_btn.setEnabled(True)
        self.control_panel.convert_btn.setText("转换")
        self.control_panel.set_progress(0)
        self.status_label.setText(f"转换完成！成功转换 {count} 张图片")

        from .utils import format_size_human as format_size
        original_size = stats.get('total_original_size', 0)
        saved_size = stats.get('size_saved', 0)
        compression_ratio = stats.get('compression_ratio', 0)
        if count <= 0 and original_size == 0:
            QMessageBox.information(self, "未找到图片", "未检测到 Markdown 中的图片链接，请确认语法：\n\n![](http://...) 或 <img src=\"...\">")
        else:
            msg = f"成功转换 {count} 张图片为WebP格式！\n\n"
            if original_size > 0:
                msg += f"原始大小: {format_size(original_size)}\n"
                msg += f"节省空间: {format_size(saved_size)}\n"
                msg += f"压缩比例: {compression_ratio:.1f}%\n\n"
            msg += "图片已保存到 images 目录。"
            QMessageBox.information(self, "转换完成", msg)

    def on_conversion_error(self, error_message):
        try:
            if hasattr(self, 'conversion_watchdog') and self.conversion_watchdog is not None:
                self.conversion_watchdog.stop()
        except Exception:
            pass
        self.control_panel.convert_btn.setEnabled(True)
        self.control_panel.convert_btn.setText("转换")
        self.control_panel.set_progress(0)
        self.status_label.setText("转换失败")
        QMessageBox.critical(self, "转换失败", error_message)

    def on_conversion_timeout(self):
        try:
            self.control_panel.convert_btn.setEnabled(True)
            self.control_panel.convert_btn.setText("转换")
            self.status_label.setText("转换超时，请检查网络或图片链接")
            QMessageBox.warning(self, "转换超时", "转换耗时过长，可能网络较慢或图片地址不可达。稍后重试，或检查图片 URL。")
        except Exception:
            pass

    def _replace_local_paths_with_remote(self, md: str, base_dir: str, mapping: dict) -> str:
        def rel(p: str) -> tuple[str, str]:
            rp = os.path.relpath(p, base_dir).replace('\\','/')
            rp2 = './' + rp if not rp.startswith('./') else rp
            return rp, rp2
        for lp, url in mapping.items():
            r1, r2 = rel(lp)
            md = md.replace(r1, url).replace(r2, url)
        return md
    
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

    # 不再提供手动切换主题
    def toggle_theme(self):
        pass

    # ===== 图床设置对话框（骨架） =====
    def open_image_bed_dialog(self):
        if not hasattr(self, 'imagebed_dialog'):
            self.imagebed_dialog = ImageBedDialog(self)
            # 主题随窗口刷新
            self.imagebed_dialog.apply_theme(self.current_theme_dark)
        self.imagebed_dialog.show()
        self.imagebed_dialog.raise_()
        self.imagebed_dialog.activateWindow()


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
        if hasattr(self, 'theme_action'):
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

class ImageBedDialog(QDialog):
    """图床设置对话框 - 骨架实现"""
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("图床设置")
        self.setModal(False)
        self.setMinimumSize(560, 420)
        self._build_ui()

    def _build_ui(self):
        root = QVBoxLayout(self)
        # 顶部：图床选择与状态
        top = QHBoxLayout()
        top.addWidget(QLabel("图床："))
        self.provider_combo = QComboBox()
        self.provider_combo.addItems([
            "七牛 v1.0", "腾讯云 COS v4 v1.1", "腾讯云 COS v5 v1.5.0",
            "又拍云 v1.2.0", "GitHub v1.5.0", "SM.MS V2 v2.3.0-beta.0",
            "阿里云 OSS v1.6.0", "Imgur v1.6.0",
        ])
        top.addWidget(self.provider_combo)
        top.addStretch()
        self.status_chip = QLabel("未测试")
        self.status_chip.setStyleSheet("QLabel{padding:2px 10px;border-radius:10px;background:#f1f5f9;color:#334155;font-size:12px;}")
        top.addWidget(self.status_chip)
        root.addLayout(top)

        # Tabs
        self.tabs = QTabWidget(self)
        self.tab_status = QWidget(); self.tab_config = QWidget(); self.tab_advanced = QWidget()
        self.tabs.addTab(self.tab_status, "选择与状态")
        self.tabs.addTab(self.tab_config, "凭据与配置")
        self.tabs.addTab(self.tab_advanced, "高级与策略")
        root.addWidget(self.tabs)

        # 选择与状态
        st = QVBoxLayout(self.tab_status)
        st.addWidget(QLabel("说明：选择图床后，可在下方“保存”并稍后进行上传测试。"))
        st.addStretch()

        # 凭据与配置（占位表单）
        scroll = QScrollArea(self.tab_config); scroll.setWidgetResizable(True)
        host = QWidget(); form = QVBoxLayout(host)
        self.field_endpoint = QLineEdit(); self.field_bucket = QLineEdit()
        self.field_access_id = QLineEdit(); self.field_access_secret = QLineEdit(); self.field_access_secret.setEchoMode(QLineEdit.EchoMode.Password)
        region_lbl = QLabel("地域前缀(如 oss-cn-beijing)")
        form.addWidget(region_lbl); form.addWidget(self.field_endpoint)
        form.addWidget(QLabel("Bucket/仓库")); form.addWidget(self.field_bucket)
        form.addWidget(QLabel("AccessKey/Token")); form.addWidget(self.field_access_id)
        form.addWidget(QLabel("Secret")); form.addWidget(self.field_access_secret)
        form.addStretch(); scroll.setWidget(host)
        cfg = QVBoxLayout(self.tab_config); cfg.addWidget(scroll)

        # 高级与策略（占位）
        adv = QVBoxLayout(self.tab_advanced)
        self.chk_enable_upload = QCheckBox("启用转换后自动上传")
        adv.addWidget(self.chk_enable_upload)
        adv.addStretch()

        # 底部按钮：保存 / 测试上传 / 关闭
        btns = QDialogButtonBox(QDialogButtonBox.StandardButton.Save | QDialogButtonBox.StandardButton.Close)
        self.test_btn = QPushButton("测试上传")
        btns.addButton(self.test_btn, QDialogButtonBox.ButtonRole.ActionRole)
        btns.accepted.connect(self.on_save)
        btns.rejected.connect(self.reject)
        self.test_btn.clicked.connect(self.on_test_upload)
        root.addWidget(btns)

    def apply_theme(self, dark: bool):
        if dark:
            self.setStyleSheet("QDialog{background:#0F141A;color:#E6EAF0;}")
        else:
            self.setStyleSheet("QDialog{background:#FFFFFF;color:#0F172A;}")
    
    # === 业务：保存配置到 QSettings ===
    def _provider_key(self) -> str:
        text = self.provider_combo.currentText()
        if "阿里云" in text or "OSS" in text:
            return "aliyun_oss"
        if "七牛" in text:
            return "qiniu"
        if "腾讯云" in text and "v4" in text:
            return "cos_v4"
        if "腾讯云" in text and "v5" in text:
            return "cos_v5"
        if "又拍云" in text:
            return "upyun"
        if "GitHub" in text:
            return "github"
        if "SM.MS" in text:
            return "smms"
        if "Imgur" in text:
            return "imgur"
        return ""

    def _normalize_aliyun_endpoint(self, region_prefix: str) -> str:
        rp = region_prefix.strip()
        # 允许用户直接填完整域名；若已包含 http 则直接返回
        if rp.startswith("http://") or rp.startswith("https://"):
            return rp
        # 只填了地域前缀：拼为 https://<prefix>.aliyuncs.com
        return f"https://{rp}.aliyuncs.com"

    def on_save(self):
        settings = QSettings("MdImgConverter", "Settings")
        prov = self._provider_key()
        settings.setValue("imgbed/provider", prov)
        # 是否启用自动上传
        enabled = bool(self.chk_enable_upload.isChecked()) if hasattr(self, 'chk_enable_upload') else False
        settings.setValue("imgbed/enabled", enabled)
        # 仅针对阿里云字段（其余图床后续补充）
        if prov == "aliyun_oss":
            endpoint = self._normalize_aliyun_endpoint(self.field_endpoint.text())
            settings.setValue("imgbed/aliyun/endpoint", endpoint)
            settings.setValue("imgbed/aliyun/bucket", self.field_bucket.text().strip())
            settings.setValue("imgbed/aliyun/accessKeyId", self.field_access_id.text().strip())
            settings.setValue("imgbed/aliyun/accessKeySecret", self.field_access_secret.text().strip())
            # 路径前缀默认 images
            if settings.value("imgbed/aliyun/prefix", "") in (None, ""):
                settings.setValue("imgbed/aliyun/prefix", "images")
        self.status_chip.setText("已保存（未测试）")
        self.accept()

    # === 业务：测试上传一张内存图片 ===
    def on_test_upload(self):
        try:
            from uploader.ali_oss_adapter import AliOssAdapter
            from PIL import Image
            from io import BytesIO
        except Exception as e:
            QMessageBox.warning(self, "缺少依赖", f"测试失败：{e}")
            return
        prov = self._provider_key()
        if prov != "aliyun_oss":
            QMessageBox.information(self, "提示", "当前先支持测试阿里云 OSS，其他图床后续补充。")
            return
        endpoint = self._normalize_aliyun_endpoint(self.field_endpoint.text())
        bucket = self.field_bucket.text().strip()
        ak = self.field_access_id.text().strip()
        sk = self.field_access_secret.text().strip()
        if not all([endpoint, bucket, ak, sk]):
            QMessageBox.warning(self, "缺少配置", "请填写 Endpoint/Bucket/AccessKey/Secret")
            return
        try:
            adapter = AliOssAdapter(
                access_key_id=ak,
                access_key_secret=sk,
                bucket_name=bucket,
                endpoint=endpoint,
                storage_path_prefix="images",
            )
            img = Image.new('RGB', (2, 2), (0, 255, 0))
            buf = BytesIO()
            img.save(buf, format='WEBP', quality=75)
            url = adapter.upload_bytes(buf.getvalue(), "mdimgconverter_test.webp")
            self.status_chip.setText("测试成功")
            QMessageBox.information(self, "测试成功", f"已上传：\n{url}")
        except Exception as e:
            self.status_chip.setText("测试失败")
            QMessageBox.critical(self, "测试失败", str(e))
    
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
        if getattr(self, '_debug_ui', False):
            try:
                QMessageBox.information(self, "DEBUG", "enter real_conversion")
            except Exception:
                pass
        try:
            print("[GUI] real_conversion: text_len=", len(markdown_text), flush=True)
        except Exception:
            pass
        
        if not markdown_text:
            QMessageBox.information(self, "提示", "请先输入Markdown内容")
            self.status_label.setText("就绪")
            return
        
        # UI 侧先行快速校验是否含有图片链接，避免无感卡住
        try:
            import re as _re
            _pattern = r'(?:!\[.*?\]\((.*?)\))|(?:<img.*?src=["\']([^"\']*)["\'].*?>)'
            _matches = _re.findall(_pattern, markdown_text)
            _urls = []
            for _m in _matches:
                _u = _m[0] or _m[1]
                if _u and _u.strip():
                    _urls.append(_u.strip())
            print(f"[GUI] precheck image urls: {len(_urls)}", flush=True)
            if not _urls:
                self.control_panel.convert_btn.setEnabled(True)
                self.control_panel.convert_btn.setText("转换")
                self.control_panel.set_progress(0)
                self.status_label.setText("未找到图片链接")
                QMessageBox.information(self, "未找到图片", "未检测到 Markdown 中的图片链接，请确认语法：\n\n![](http://...) 或 <img src=\"...\">")
                return
        except Exception:
            pass

        # 获取当前文件目录，如果没有文件则使用当前目录
        if hasattr(self, 'current_file') and self.current_file:
            base_dir = os.path.dirname(self.current_file)
        else:
            base_dir = os.getcwd()
        
        # 创建images目录
        output_dir = os.path.join(base_dir, "images")
        try:
            print("[GUI] base_dir=", base_dir, " output_dir=", output_dir, flush=True)
        except Exception:
            pass
        
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
        try:
            print("[GUI] starting ConversionWorker...", flush=True)
        except Exception:
            pass
        self.conversion_worker.start()

        # 启动看门狗，防止长时间无响应（如网络卡住）
        try:
            if hasattr(self, 'conversion_watchdog') and self.conversion_watchdog is not None:
                self.conversion_watchdog.stop()
        except Exception:
            pass
        self.conversion_watchdog = QTimer(self)
        self.conversion_watchdog.setSingleShot(True)
        self.conversion_watchdog.timeout.connect(self.on_conversion_timeout)
        self.conversion_watchdog.start(45000)  # 45s 超时提示
    
    def on_conversion_progress(self, progress, message):
        """转换进度更新"""
        self.control_panel.set_progress(progress)
        self.status_label.setText(message)
        try:
            print(f"[GUI] progress: {progress}%  {message}", flush=True)
        except Exception:
            pass
        # 刷新看门狗
        try:
            if hasattr(self, 'conversion_watchdog') and self.conversion_watchdog is not None:
                self.conversion_watchdog.start(45000)
        except Exception:
            pass
    
    def on_conversion_finished(self, new_markdown, count, stats):
        """转换完成"""
        try:
            if hasattr(self, 'conversion_watchdog') and self.conversion_watchdog is not None:
                self.conversion_watchdog.stop()
        except Exception:
            pass
        try:
            print(f"[GUI] finished: count={count} stats={stats}", flush=True)
        except Exception:
            pass
        # 更新编辑器内容（先显示转换结果，不阻塞）
        self.editor.setPlainText(new_markdown)
        
        # 更新压缩统计
        self.control_panel.update_compression_stats(stats)
        
        # 重置UI状态
        self.control_panel.convert_btn.setEnabled(True)
        self.control_panel.convert_btn.setText("转换")
        self.control_panel.set_progress(0)
        self.status_label.setText(f"转换完成！成功转换 {count} 张图片")

        # 不再自动上传，改为显式“上传”按钮触发
        
        # 格式化统计信息用于显示
        from .utils import format_size_human as format_size
        
        original_size = stats.get('total_original_size', 0)
        saved_size = stats.get('size_saved', 0)
        compression_ratio = stats.get('compression_ratio', 0)
        
        # 弹窗提示：区分未找到图片与成功转换
        if count <= 0 and stats.get('total_original_size', 0) == 0:
            QMessageBox.information(
                self,
                "未找到图片",
                "未检测到 Markdown 中的图片链接，请确认语法：\n\n![](http://...) 或 <img src=\"...\">",
            )
        else:
            message = f"成功转换 {count} 张图片为WebP格式！\n\n"
            if original_size > 0:
                message += f"原始大小: {format_size(original_size)}\n"
                message += f"节省空间: {format_size(saved_size)}\n"
                message += f"压缩比例: {compression_ratio:.1f}%\n\n"
            message += "图片已保存到 images 目录。"
            QMessageBox.information(self, "转换完成", message)
    
    def on_conversion_error(self, error_message):
        """转换错误"""
        try:
            if hasattr(self, 'conversion_watchdog') and self.conversion_watchdog is not None:
                self.conversion_watchdog.stop()
        except Exception:
            pass
        try:
            print(f"[GUI] error: {error_message}", flush=True)
        except Exception:
            pass
        # 重置UI状态
        self.control_panel.convert_btn.setEnabled(True)
        self.control_panel.convert_btn.setText("转换")
        self.control_panel.set_progress(0)
        self.status_label.setText("转换失败")
        
        # 显示错误消息
        QMessageBox.critical(self, "转换失败", error_message)

    def on_conversion_timeout(self):
        """转换超时提示（不强杀线程，仅提示并恢复按钮）"""
        try:
            print("[GUI] timeout", flush=True)
            self.control_panel.convert_btn.setEnabled(True)
            self.control_panel.convert_btn.setText("转换")
            self.status_label.setText("转换超时，请检查网络或图片链接")
            QMessageBox.warning(self, "转换超时", "转换耗时过长，可能网络较慢或图片地址不可达。稍后重试，或检查图片 URL。")
        except Exception:
            pass

# 兼容性修复：将下方（意外置于类外的）方法绑定回 Win11MainWindow
try:
    if not hasattr(Win11MainWindow, 'real_conversion') and 'real_conversion' in globals():
        Win11MainWindow.real_conversion = globals()['real_conversion']
    if not hasattr(Win11MainWindow, 'on_conversion_progress') and 'on_conversion_progress' in globals():
        Win11MainWindow.on_conversion_progress = globals()['on_conversion_progress']
    if not hasattr(Win11MainWindow, 'on_conversion_finished') and 'on_conversion_finished' in globals():
        Win11MainWindow.on_conversion_finished = globals()['on_conversion_finished']
    if not hasattr(Win11MainWindow, 'on_conversion_error') and 'on_conversion_error' in globals():
        Win11MainWindow.on_conversion_error = globals()['on_conversion_error']
    if not hasattr(Win11MainWindow, 'on_conversion_timeout') and 'on_conversion_timeout' in globals():
        Win11MainWindow.on_conversion_timeout = globals()['on_conversion_timeout']
    if not hasattr(Win11MainWindow, '_replace_local_paths_with_remote') and '_replace_local_paths_with_remote' in globals():
        Win11MainWindow._replace_local_paths_with_remote = globals()['_replace_local_paths_with_remote']
except Exception:
    pass

    def _replace_local_paths_with_remote(self, md: str, base_dir: str, mapping: dict) -> str:
        """将 Markdown 中 ./images 或 images 的相对路径替换为远程 URL"""
        def rel(p: str) -> str:
            # 生成两种相对形式：images/name.webp 与 ./images/name.webp
            img_dir = os.path.join(base_dir, "images")
            rp = os.path.relpath(p, base_dir).replace('\\','/')
            rp2 = './' + rp if not rp.startswith('./') else rp
            return rp, rp2
        for lp, url in mapping.items():
            r1, r2 = rel(lp)
            # 粗略替换两种可能形式
            md = md.replace(r1, url).replace(r2, url)
        return md
