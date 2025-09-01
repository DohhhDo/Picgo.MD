#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Win11 Fluent Design System - 官方设计规范实现
采用与Windows设置、文件资源管理器一致的UI风格
"""

from PyQt6.QtCore import (
    QEasingCurve,
    QPoint,
    QPropertyAnimation,
    QRect,
    QSettings,
    QSize,
    Qt,
    QTimer,
    pyqtSignal,
)
from PyQt6.QtGui import (
    QAction,
    QColor,
    QCursor,
    QFont,
    QFontMetrics,
    QIcon,
    QPainter,
    QPalette,
    QPixmap,
    QScreen,
)
from PyQt6.QtWidgets import (
    QApplication,
    QCheckBox,
    QComboBox,
    QDialog,
    QDialogButtonBox,
    QFileDialog,
    QFrame,
    QGraphicsDropShadowEffect,
    QGridLayout,
    QHBoxLayout,
    QLabel,
    QLineEdit,
    QMainWindow,
    QMessageBox,
    QPushButton,
    QScrollArea,
    QSizePolicy,
    QSlider,
    QSplitter,
    QTabWidget,
    QTextEdit,
    QToolBar,
    QToolButton,
    QVBoxLayout,
    QWidget,
)

try:
    from PyQt6.QtSvg import QSvgRenderer
except Exception:
    QSvgRenderer = None
import os
import re
import sys
from pathlib import Path

# 添加core模块路径
current_dir = Path(__file__).parent.parent
sys.path.insert(0, str(current_dir))

try:
    from core.image_converter import convert_markdown_images
except ImportError:
    print("Warning: 无法导入图片转换模块")
    convert_markdown_images = None

from .components.control_panel import Win11ControlPanel
from .components.markdown_editor import Win11MarkdownEditor
from .dialogs.image_bed_dialog import ImageBedDialog
from .themes.tokens import DARK_TOKENS, LIGHT_TOKENS
from .utils import detect_system_theme_default_dark, format_size_human
from .workers import ConversionWorker, UploadWorker

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
            key = winreg.OpenKey(
                registry,
                r"SOFTWARE\Microsoft\Windows\CurrentVersion\Themes\Personalize",
            )
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
        self.convert_btn.setSizePolicy(
            QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Fixed
        )
        self.convert_btn.setStyleSheet(
            """
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
        """
        )
        main_layout.addWidget(self.convert_btn)

        # 上传按钮（与转换分步）
        self.upload_btn = QPushButton("上传")
        self.upload_btn.setFixedHeight(40)
        self.upload_btn.setSizePolicy(
            QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Fixed
        )
        self.upload_btn.setStyleSheet(
            """
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
        """
        )
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
        self.convert_btn.setStyleSheet(
            f"""
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
            QPushButton:hover {{ 
                background-color: {tokens['primary_hover']}; 
                border-color: {tokens['primary_hover']}; 
            }}
            QPushButton:pressed {{ 
                background-color: {tokens['primary_press']}; 
                border-color: {tokens['primary_press']}; 
            }}
        """
        )
        # 上传按钮（次要描边款）
        if hasattr(self, "upload_btn"):
            self.upload_btn.setStyleSheet(
                f"""
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
                QPushButton:hover {{ 
                    background-color: {tokens['chip_hover_bg']}; 
                    border-color: {tokens['chip_border']}; 
                }}
                QPushButton:pressed {{ 
                    background-color: {tokens['chip_pressed_bg']}; 
                    border-color: {tokens['chip_border']}; 
                }}
            """
            )

        # 质量百分比徽标
        self.quality_label.setStyleSheet(
            f"""
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
        """
        )

        # 滑杆样式
        self.quality_slider.setStyleSheet(
            f"""
            QSlider::groove:horizontal {{ 
                background: {tokens['slider_track']}; 
                height: 4px; 
                border-radius: 2px; 
            }}
            QSlider::sub-page:horizontal {{ 
                background: {tokens['slider_fill']}; 
                border-radius: 2px; 
            }}
            QSlider::handle:horizontal {{ 
                background: {tokens['slider_fill']}; 
                width: 18px; 
                height: 18px; 
                border-radius: 9px; 
                margin: -7px 0; 
            }}
            QSlider::handle:horizontal:hover {{ 
                background: {tokens['primary_hover']}; 
            }}
        """
        )

        # 进度条
        if hasattr(self, "progress_bg"):
            self.progress_bg.setStyleSheet(
                f"QWidget {{ "
                f"background-color: {tokens['progress_bg']}; "
                f"border-radius: 3px; "
                f"}}"
            )
        if hasattr(self, "progress_fill"):
            self.progress_fill.setStyleSheet(
                f"QWidget {{ "
                f"background-color: {tokens['progress_fill']}; "
                f"border-radius: 3px; "
                f"}}"
            )
        if hasattr(self, "progress_text"):
            self.progress_text.setStyleSheet(
                f"QLabel {{ color: {tokens['progress_text']}; font-size: 12px; }}"
            )

        # 预设未选中样式
        for chip in getattr(self, "preset_chip_buttons", []):
            chip.setStyleSheet(
                f"""
                QPushButton {{
                    background-color: {tokens['chip_bg']};
                    color: {tokens['chip_text']};
                    border: 1px solid {tokens['chip_border']};
                    border-radius: 15px;
                    padding: 2px 12px;
                    font-size: 12px; font-weight: 600;
                }}
                QPushButton:hover {{ background-color: {tokens['chip_hover_bg']}; }}
                QPushButton:pressed {{ 
                    background-color: {tokens['chip_pressed_bg']}; 
                }}
            """
            )
        # 选中态刷新
        self.update_preset_button_states(self.quality_value)

    def apply_panel_theme(self):
        """应用控制面板主题"""
        if self.is_dark_theme:
            # 深色主题
            self.setStyleSheet(
                """
                Win11ControlPanel {
                    background-color: #2d2d2d;
                    border-left: 1px solid #3f3f3f;
                }
            """
            )
        else:
            # 浅色主题
            self.setStyleSheet(
                """
                Win11ControlPanel {
                    background-color: #f3f3f3;
                    border-left: 1px solid #e5e5e5;
                }
            """
            )

    def get_card_style(self):
        """获取卡片样式"""
        if self.is_dark_theme:
            return """
                QFrame {
                    background-color: #2b2b2b;
                    border-radius: 10px;
                    padding: 0px;
                }
            """
        else:
            return """
                QFrame {
                    background-color: #ffffff;
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
        # 取消卡片边框与阴影，弱化分隔，减少"小框线"感
        card.setStyleSheet(
            """
            QFrame { background-color: transparent; border: none; }
        """
        )

        layout = QVBoxLayout()
        layout.setContentsMargins(16, 16, 16, 16)
        layout.setSpacing(12)

        # 标题
        title = QLabel("图片质量")
        title.setStyleSheet(
            """
            QLabel { font-size: 14px; font-weight: 700; color: #166534; }
        """
        )
        layout.addWidget(title)

        # 描述
        desc = QLabel("调整WebP压缩质量")
        desc.setStyleSheet(
            """
            QLabel { font-size: 12px; color: #475569; margin-bottom: 6px; }
        """
        )
        layout.addWidget(desc)

        # 滑块和数值显示容器
        control_layout = QHBoxLayout()
        control_layout.setSpacing(12)

        # 水平滑块 - Win11风格
        self.quality_slider = QSlider(Qt.Orientation.Horizontal)
        self.quality_slider.setRange(1, 100)
        self.quality_slider.setValue(self.quality_value)
        self.quality_slider.setFixedHeight(24)
        self.quality_slider.setStyleSheet(
            """
            QSlider::groove:horizontal { 
                background: #d1fae5; 
                height: 4px; 
                border-radius: 2px; 
            }
            QSlider::sub-page:horizontal { background: #16a34a; border-radius: 2px; }
            QSlider::handle:horizontal { 
                background: #16a34a; 
                width: 18px; 
                height: 18px; 
                border-radius: 9px; 
                margin: -7px 0; 
            }
            QSlider::handle:horizontal:hover { background: #15803d; }
        """
        )

        # 数值显示
        self.quality_label = QLabel(f"{self.quality_value}%")
        self.quality_label.setFixedWidth(45)
        self.quality_label.setStyleSheet(
            """
            QLabel {
                background-color: #ecfdf5;
                color: #065f46;
                border: 1px solid #a7f3d0;
                border-radius: 6px;
                padding: 4px 8px;
                font-size: 13px;
                font-weight: 600;
            }
        """
        )
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
            chip.setStyleSheet(
                """
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
            """
            )
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
        card.setStyleSheet(
            """
            QFrame { background-color: transparent; border: none; }
        """
        )

        layout = QVBoxLayout()
        layout.setContentsMargins(16, 16, 16, 16)
        layout.setSpacing(12)

        # 标题
        self.progress_title = QLabel("转换进度")
        layout.addWidget(self.progress_title)

        # Win11风格进度条（统一绿色系）
        progress_container = QWidget()
        progress_container.setFixedHeight(60)

        progress_layout = QVBoxLayout()
        progress_layout.setContentsMargins(0, 0, 0, 0)
        progress_layout.setSpacing(8)

        # 进度条背景（去边框，浅绿色背景）
        self.progress_bg = QWidget()
        self.progress_bg.setFixedHeight(6)
        # 背景与文字样式在创建后统一由 _apply_progress_styles 控制

        # 进度条填充
        self.progress_fill = QWidget(self.progress_bg)
        self.progress_fill.setFixedHeight(6)
        self.progress_fill.setFixedWidth(0)  # 初始宽度为0
        self.progress_fill.setStyleSheet(
            """
            QWidget { background-color: #16a34a; border-radius: 3px; }
        """
        )

        # 进度文本
        self.progress_text = QLabel("准备就绪")
        # 初始样式
        self._apply_progress_styles(self.is_dark_theme)
        self.progress_text.setAlignment(Qt.AlignmentFlag.AlignCenter)

        progress_layout.addWidget(self.progress_bg)
        progress_layout.addWidget(self.progress_text)
        progress_container.setLayout(progress_layout)

        layout.addWidget(progress_container)
        card.setLayout(layout)

        return card

    def _apply_progress_styles(self, dark: bool):
        """根据主题更新"转换进度"区域的颜色样式"""
        if dark:
            if hasattr(self, "progress_title"):
                self.progress_title.setStyleSheet(
                    "QLabel{color:#E5E7EB;font-size:16px;font-weight:600;margin-bottom:4px;}"
                )
            if hasattr(self, "progress_bg"):
                self.progress_bg.setStyleSheet(
                    "QWidget { background-color: #1F2937; border-radius: 3px; }"
                )
            if hasattr(self, "progress_text"):
                self.progress_text.setStyleSheet(
                    "QLabel{font-size:12px;color:#E5E7EB;}"
                )
        else:
            if hasattr(self, "progress_title"):
                self.progress_title.setStyleSheet(
                    "QLabel{color:#065f46;font-size:16px;font-weight:600;margin-bottom:4px;}"
                )
            if hasattr(self, "progress_bg"):
                self.progress_bg.setStyleSheet(
                    "QWidget { background-color: #e2f7ec; border-radius: 3px; }"
                )
            if hasattr(self, "progress_text"):
                self.progress_text.setStyleSheet(
                    "QLabel{font-size:12px;color:#065f46;}"
                )

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
        title.setStyleSheet(
            self.get_label_style("16px", "600")
            + """
            QLabel {
                margin-bottom: 4px;
            }
        """
        )
        layout.addWidget(title)

        # 无损预设按钮（大按钮）
        self.lossless_btn = QPushButton("无损")
        self.lossless_btn.setMinimumHeight(42)
        self.lossless_btn.setStyleSheet(
            """
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
        """
        )
        self.lossless_btn.clicked.connect(lambda: self.set_quality_preset(100))
        layout.addWidget(self.lossless_btn)

        # 移除分隔线，保持整体简洁

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
            btn.setStyleSheet(
                """
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
            """
            )

            # 为第二个按钮（标准）设置选中状态
            if i == 1:
                btn.setStyleSheet(
                    btn.styleSheet()
                    + """
                    QPushButton {
                        background-color: #dcfce7;
                        border-color: #16a34a;
                        color: #166534;
                        font-weight: 700;
                    }
                """
                )

            # 连接点击事件
            btn.clicked.connect(
                lambda checked, val=quality_value: self.set_quality_preset(val)
            )

            self.preset_buttons.append(btn)
            grid_layout.addWidget(btn, i // 2, i % 2)

        layout.addLayout(grid_layout)
        card.setLayout(layout)

        return card

    def set_quality_preset(self, quality_value):
        """设置质量预设值"""
        self.quality_value = quality_value

        # 更新滑块位置
        if hasattr(self, "quality_slider"):
            self.quality_slider.setValue(quality_value)

        # 更新按钮选中状态
        self.update_preset_button_states(quality_value)

    def update_preset_button_states(self, selected_quality):
        """更新预设按钮的选中状态"""
        # 重置所有按钮状态
        if hasattr(self, "lossless_btn"):
            if selected_quality == 100:
                # 无损按钮选中状态
                self.lossless_btn.setStyleSheet(
                    """
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
                """
                )
            else:
                # 无损按钮未选中状态
                self.lossless_btn.setStyleSheet(
                    """
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
                """
                )

        # 更新其他预设按钮状态（旧网格按钮）
        preset_values = [90, 73, 50, 30]
        for i, btn in enumerate(getattr(self, "preset_buttons", [])):
            if (
                i < len(preset_values)
                and preset_values[i] == selected_quality
                and selected_quality != 100
            ):
                # 选中状态
                btn.setStyleSheet(
                    """
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
                """
                )
            else:
                # 未选中状态
                btn.setStyleSheet(
                    """
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
                """
                )

        # 更新轻量预设 Chips 选中状态
        tokens = getattr(self, "tokens", {}) or {}
        for chip in getattr(self, "preset_chip_buttons", []):
            value = getattr(self, "preset_chip_value", {}).get(chip, None)
            if value is None:
                continue
            if value == selected_quality:
                chip.setStyleSheet(
                    f"""
                    QPushButton {{
                        background-color: {tokens.get('chip_selected_bg', '#dcfce7')};
                        color: {tokens.get('chip_selected_text', '#166534')};
                        border: 2px solid {tokens.get(
                            'chip_selected_border', '#16a34a'
                        )};
                        border-radius: 15px;
                        padding: 2px 12px;
                        font-size: 12px; font-weight: 700;
                    }}
                """
                )
            else:
                chip.setStyleSheet(
                    f"""
                    QPushButton {{
                        background-color: {tokens.get('chip_bg', '#f8fafc')};
                        color: {tokens.get('chip_text', '#166534')};
                        border: 1px solid {tokens.get('chip_border', '#d1fae5')};
                        border-radius: 15px;
                        padding: 2px 12px;
                        font-size: 12px; font-weight: 600;
                    }}
                    QPushButton:hover {{ 
                        background-color: {tokens.get('chip_hover_bg', '#ecfdf5')}; 
                    }}
                    QPushButton:pressed {{ 
                        background-color: {tokens.get('chip_pressed_bg', '#dcfce7')}; 
                    }}
                """
                )

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
        title.setStyleSheet(
            self.get_label_style("16px", "600")
            + """
            QLabel {
                margin-bottom: 4px;
            }
        """
        )
        layout.addWidget(title)

        # 统计信息容器
        stats_container = QWidget()
        stats_layout = QVBoxLayout()
        stats_layout.setContentsMargins(0, 0, 0, 0)
        stats_layout.setSpacing(6)

        # 原始大小
        self.original_size_label = QLabel("原始大小: --")
        self.original_size_label.setStyleSheet(
            """
            QLabel {
                font-size: 12px;
                color: #605e5c;
            }
        """
        )
        stats_layout.addWidget(self.original_size_label)

        # 压缩后大小
        self.compressed_size_label = QLabel("压缩后: --")
        self.compressed_size_label.setStyleSheet(
            """
            QLabel {
                font-size: 12px;
                color: #605e5c;
            }
        """
        )
        stats_layout.addWidget(self.compressed_size_label)

        # 节省空间
        self.saved_size_label = QLabel("节省空间: --")
        self.saved_size_label.setStyleSheet(
            """
            QLabel {
                font-size: 12px;
                color: #107c10;
                font-weight: 600;
            }
        """
        )
        stats_layout.addWidget(self.saved_size_label)

        # 压缩比例
        self.compression_ratio_label = QLabel("压缩比例: --")
        self.compression_ratio_label.setStyleSheet(
            """
            QLabel {
                font-size: 14px;
                color: #0078d4;
                font-weight: 600;
            }
        """
        )
        stats_layout.addWidget(self.compression_ratio_label)

        stats_container.setLayout(stats_layout)
        layout.addWidget(stats_container)

        card.setLayout(layout)
        return card

    def update_compression_stats(self, stats):
        """更新压缩统计信息"""
        # 方案A：右侧仅保留质量与进度。若统计控件不存在，则直接跳过更新。
        if not hasattr(self, "original_size_label"):
            return
        from .utils import format_size_human as _fmt

        original_size = stats.get("total_original_size", 0)
        compressed_size = stats.get("total_converted_size", 0)
        saved_size = stats.get("size_saved", 0)
        compression_ratio = stats.get("compression_ratio", 0)

        self.original_size_label.setText(f"原始大小: {_fmt(original_size)}")
        self.compressed_size_label.setText(f"压缩后: {_fmt(compressed_size)}")
        self.saved_size_label.setText(f"节省空间: {_fmt(saved_size)}")
        self.compression_ratio_label.setText(f"压缩比例: {compression_ratio:.1f}%")

    def reset_compression_stats(self):
        """重置压缩统计信息"""
        if hasattr(self, "original_size_label"):
            self.original_size_label.setText("原始大小: --")
        if hasattr(self, "compressed_size_label"):
            self.compressed_size_label.setText("压缩后: --")
        if hasattr(self, "saved_size_label"):
            self.saved_size_label.setText("节省空间: --")
        if hasattr(self, "compression_ratio_label"):
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
        # 合并流程标记与最近一次转换统计
        self._combined_flow = False
        self._last_convert_count = 0
        self._last_convert_stats = {}
        self.setup_ui()
        self.setup_status_bar()
        self.restore_window_state()

    def setup_ui(self):
        """设置用户界面"""
        # 使用标准窗口
        self.setWindowTitle("MdImgConverter")
        self.setMinimumSize(900, 700)
        # 设置窗口与应用图标（任务栏 + 左上角），兼容 PyInstaller 资源路径
        try:
            app_icon = self._load_app_icon()
            if app_icon is not None:
                self.setWindowIcon(app_icon)
                try:
                    QApplication.setWindowIcon(app_icon)
                except Exception:
                    pass
        except Exception:
            pass

        # 创建主容器
        main_container = QWidget()
        self.setCentralWidget(main_container)

        # 主容器布局
        container_layout = QVBoxLayout()
        # 底部预留间隙，使内容区与状态栏之间有缓冲（颜色同窗口背景）
        container_layout.setContentsMargins(0, 0, 0, 8)
        container_layout.setSpacing(0)

        # Win11风格菜单栏
        self.setup_menu_bar()

        # 顶部 Hero 区（方案A）：价值主张 + 大按钮 + 右侧主题切换
        hero = self.create_hero_bar()
        container_layout.addWidget(hero)

        # 创建内容区域
        content_widget = QWidget()
        content_layout = QHBoxLayout()
        # 让编辑器左侧与窗口留白（仅左边 12px）
        content_layout.setContentsMargins(12, 0, 0, 0)
        content_layout.setSpacing(0)

        # 创建分割器
        self.splitter = QSplitter(Qt.Orientation.Horizontal)
        self.splitter.setHandleWidth(1)
        # 隐藏分割线
        self.splitter.setStyleSheet(
            "QSplitter::handle{background-color:transparent;}"
        )

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

        # 底部提示栏已移除，保持界面简洁

        main_container.setLayout(container_layout)

        # 连接信号（显式断开后再连接，避免重复/混乱）
        try:
            self.control_panel.convert_btn.clicked.disconnect()
        except Exception:
            pass
        self.control_panel.convert_btn.clicked.connect(self.on_convert_clicked)
        if hasattr(self.control_panel, "upload_btn"):
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
            key = winreg.OpenKey(
                registry,
                r"SOFTWARE\Microsoft\Windows\CurrentVersion\Themes\Personalize",
            )
            value, _ = winreg.QueryValueEx(key, "AppsUseLightTheme")
            winreg.CloseKey(key)
            return value == 0
        except Exception:
            return False

    def _resolve_base_dir(self) -> Path:
        """解析资源基路径：源码运行或 PyInstaller 下均可用。"""
        try:
            import sys as _sys

            return Path(getattr(_sys, "_MEIPASS", Path(__file__).resolve().parents[2]))
        except Exception:
            return Path(__file__).resolve().parents[2]

    def _load_app_icon(self) -> QIcon | None:
        """加载应用图标 pictures/app_icon.ico。找不到则返回 None。"""
        try:
            base_dir = self._resolve_base_dir()
            ico_path = base_dir / "pictures" / "app_icon.ico"
            if ico_path.exists():
                return QIcon(str(ico_path))
        except Exception:
            pass
        return None

    def apply_theme(self, dark: bool):
        """根据主题开关设置全局与局部样式"""
        if dark:
            # tokens - Clean Contrast (Dark)
            tokens = {
                "bg": "#0D1117",
                "surface": "#111827",
                "text": "#E5E7EB",
                "subtext": "#9CA3AF",
                "border": "#1F2937",
                "primary": "#16A34A",
                "primary_hover": "#15803D",
                "primary_press": "#166534",
                "quality_badge_bg": "#0B1220",
                "quality_badge_border": "#173D2A",
                "quality_badge_text": "#86EFAC",
                "slider_track": "#1F2937",
                "slider_fill": "#16A34A",
                "progress_bg": "#1F2937",
                "progress_fill": "#16A34A",
                "progress_text": "#E5E7EB",
                "chip_bg": "#0D1E14",
                "chip_text": "#86EFAC",
                "chip_border": "#173D2A",
                "chip_hover_bg": "#0F2318",
                "chip_pressed_bg": "#10331F",
                "chip_selected_bg": "#10331F",
                "chip_selected_text": "#86EFAC",
                "chip_selected_border": "#16A34A",
            }
            # 深色
            self.setStyleSheet(
                """
                        QMainWindow { background-color: #0f172a; }
                        QMenuBar { background-color: #111827; color: #e5e7eb; border: none; }
                        QMenuBar::item:selected { background-color: #1f2937; }
                    """
            )
            # 编辑器深色
            self.editor.is_dark_theme = True
            self.editor.apply_theme_style()
            # 控制面板深色
            self.control_panel.is_dark_theme = True
            self.control_panel.apply_panel_theme()
            # 更新内部控件色值
            self.control_panel.progress_text.setStyleSheet(
                "QLabel{color:#e5e7eb;font-size:12px;}"
            )
            # 顶部Hero与底部提示
            if hasattr(self, "hero_frame"):
                # 去除底部分割线，保持干净
                self.hero_frame.setStyleSheet("QFrame{background-color:#111827;}")
            if hasattr(self, "hero_title_label"):
                self.hero_title_label.setStyleSheet(
                    "QLabel{color:#f9fafb;font-size:18px;font-weight:700;}"
                )
            if hasattr(self, "hero_subtitle_label"):
                self.hero_subtitle_label.setStyleSheet(
                    "QLabel{color:#9ca3af;font-size:12px;}"
                )
            if hasattr(self, "hint_bar"):
                self.hint_bar.setStyleSheet("QFrame{background-color:#0b1220;}")
            if hasattr(self, "hint_label"):
                self.hint_label.setStyleSheet("QLabel{color:#94a3b8;font-size:12px;}")
            self.update_icons(True)
            # 应用 tokens 到右栏
            self.control_panel.apply_tokens(tokens)
            # 同步"转换进度"区域颜色
            if hasattr(self, "control_panel") and hasattr(
                self.control_panel, "_apply_progress_styles"
            ):
                self.control_panel._apply_progress_styles(True)
            # 设置深色 Logo
            try:
                import sys as _sys

                base_dir = Path(
                    getattr(_sys, "_MEIPASS", Path(__file__).resolve().parents[2])
                )
                logo_path = base_dir / "pictures" / "Meowdown – D.png"
                self._set_hero_logo_scaled(logo_path)
            except Exception:
                pass
            # Hero 颜色与按钮样式
            if hasattr(self, "hero_frame"):
                self.hero_frame.setStyleSheet("QFrame{background-color:#111827;}")
            if hasattr(self, "hero_title_label"):
                self.hero_title_label.setStyleSheet(
                    "QLabel{color:#f9fafb;font-size:18px;font-weight:700;}"
                )
            if hasattr(self, "hero_subtitle_label"):
                self.hero_subtitle_label.setStyleSheet(
                    "QLabel{color:#9ca3af;font-size:12px;}"
                )
            for btn in [
                getattr(self, "hero_open_btn", None),
                getattr(self, "hero_paste_btn", None),
                getattr(self, "hero_clear_btn", None),
                getattr(self, "hero_imagebed_btn", None),
            ]:
                if btn is not None:
                    btn.setStyleSheet(
                        "QToolButton{color:#E5E7EB;background:transparent;border:none;padding:2px 8px;} QToolButton:hover{background:#1f2937;border-radius:4px;}"
                    )
            if hasattr(self, "hero_start_btn"):
                self.hero_start_btn.setStyleSheet(
                    """
                    QPushButton { background-color: #16a34a; color: #ffffff; border: 1px solid #16a34a; border-radius: 8px; font-size: 14px; font-weight: 600; padding: 6px 16px; }
                    QPushButton:hover { background-color: #15803d; border-color: #15803d; }
                    QPushButton:pressed { background-color: #166534; border-color: #166534; }
                    """
                )
            # 底部状态栏与整体背景保持一致的深色
            if hasattr(self, "status_bar"):
                # 去除状态栏顶部分割线
                self.status_bar.setStyleSheet(
                    "QStatusBar{background-color:#0f172a;color:#E6EAF0;padding:4px 16px;font-size:12px;}"
                )
                # 明确设置状态栏上的文本颜色
                if hasattr(self, "status_label"):
                    self.status_label.setStyleSheet("QLabel{color:#E6EAF0;}")
                if hasattr(self, "context_label"):
                    self.context_label.setStyleSheet("QLabel{color:#E6EAF0;}")
            # 分割线更暗，避免过亮
            if hasattr(self, "splitter"):
                # 隐藏分割线
                self.splitter.setStyleSheet(
                    "QSplitter::handle{background-color:transparent;}"
                )
        else:
            # tokens - Clean Contrast (Light)
            tokens = {
                "bg": "#F6F8FA",
                "surface": "#FFFFFF",
                "text": "#0F172A",
                "subtext": "#475569",
                "border": "#E5E7EB",
                "primary": "#16A34A",
                "primary_hover": "#15803D",
                "primary_press": "#166534",
                "quality_badge_bg": "#ECFDF5",
                "quality_badge_border": "#A7F3D0",
                "quality_badge_text": "#065F46",
                "slider_track": "#D1FAE5",
                "slider_fill": "#16A34A",
                "progress_bg": "#E2F7EC",
                "progress_fill": "#16A34A",
                "progress_text": "#166534",
                "chip_bg": "#F8FAFC",
                "chip_text": "#166534",
                "chip_border": "#D1FAE5",
                "chip_hover_bg": "#ECFDF5",
                "chip_pressed_bg": "#DCFCE7",
                "chip_selected_bg": "#DCFCE7",
                "chip_selected_text": "#166534",
                "chip_selected_border": "#16A34A",
            }
            # 浅色
            self.setStyleSheet(
                """
                QMainWindow { background-color: #E8F5E9; }
                QMenuBar { background-color: #E8F5E9; color: #065f46; }
                QMenuBar::item:selected { background-color: #DCFCE7; }
            """
            )
            self.editor.is_dark_theme = False
            self.editor.apply_theme_style()
            self.control_panel.is_dark_theme = False
            self.control_panel.apply_panel_theme()
            self.control_panel.progress_text.setStyleSheet(
                "QLabel{color:#166534;font-size:12px;}"
            )
            if hasattr(self, "hero_frame"):
                self.hero_frame.setStyleSheet("QFrame{background-color:#E8F5E9;}")
            if hasattr(self, "hero_title_label"):
                self.hero_title_label.setStyleSheet(
                    "QLabel{color:#065f46;font-size:18px;font-weight:700;}"
                )
            if hasattr(self, "hero_subtitle_label"):
                self.hero_subtitle_label.setStyleSheet(
                    "QLabel{color:#0f766e;font-size:12px;}"
                )
            if hasattr(self, "hint_bar"):
                self.hint_bar.setStyleSheet("QFrame{background-color:#f8fafc;}")
            if hasattr(self, "hint_label"):
                self.hint_label.setStyleSheet("QLabel{color:#334155;font-size:12px;}")
            self.update_icons(False)
            # 应用 tokens 到右栏
            self.control_panel.apply_tokens(tokens)
            # 同步"转换进度"区域颜色
            if hasattr(self, "control_panel") and hasattr(
                self.control_panel, "_apply_progress_styles"
            ):
                self.control_panel._apply_progress_styles(False)
            # 设置浅色 Logo（等比缩放到标题字号高度，约18px）
            try:
                import sys as _sys

                base_dir = Path(
                    getattr(_sys, "_MEIPASS", Path(__file__).resolve().parents[2])
                )
                logo_path = base_dir / "pictures" / "Meowdown – L.png"
                self._set_hero_logo_scaled(logo_path)
            except Exception:
                pass
            # Hero 颜色与按钮样式
            if hasattr(self, "hero_frame"):
                self.hero_frame.setStyleSheet("QFrame{background-color:#E8F5E9;}")
            if hasattr(self, "hero_title_label"):
                self.hero_title_label.setStyleSheet(
                    "QLabel{color:#065f46;font-size:18px;font-weight:700;}"
                )
            if hasattr(self, "hero_subtitle_label"):
                self.hero_subtitle_label.setStyleSheet(
                    "QLabel{color:#0f766e;font-size:12px;}"
                )
            for btn in [
                getattr(self, "hero_open_btn", None),
                getattr(self, "hero_paste_btn", None),
                getattr(self, "hero_clear_btn", None),
                getattr(self, "hero_imagebed_btn", None),
            ]:
                if btn is not None:
                    btn.setStyleSheet(
                        "QToolButton{color:#065f46;background:#ECFDF5;border:1px solid #A7F3D0;border-radius:6px;padding:2px 8px;} QToolButton:hover{background:#DCFCE7;}"
                    )
            if hasattr(self, "hero_start_btn"):
                self.hero_start_btn.setStyleSheet(
                    """
                    QPushButton { background-color: #16a34a; color: #ffffff; border: 1px solid #16a34a; border-radius: 8px; font-size: 14px; font-weight: 600; padding: 6px 16px; }
                    QPushButton:hover { background-color: #15803d; border-color: #15803d; }
                    QPushButton:pressed { background-color: #166534; border-color: #166534; }
                    """
                )
            # 底部状态栏：亮色模式下背景与整体保持一致的浅绿，文字深色
            if hasattr(self, "status_bar"):
                self.status_bar.setStyleSheet(
                    "QStatusBar{background-color:#E8F5E9;color:#065f46;padding:4px 16px;font-size:12px;}"
                )
                # 明确设置状态栏上的文本颜色
                if hasattr(self, "status_label"):
                    self.status_label.setStyleSheet("QLabel{color:#065f46;}")
                if hasattr(self, "context_label"):
                    self.context_label.setStyleSheet("QLabel{color:#065f46;}")
            # 分割线更柔和
            if hasattr(self, "splitter"):
                self.splitter.setStyleSheet(
                    "QSplitter::handle{background-color:transparent;}"
                )
        # 重新渲染质量/预设等控件样式
        self.control_panel.update_preset_button_states(self.control_panel.quality_value)
        # 无手动切换，故不更新切换图标

    def _icon_from_svg_file(
        self, filename: str, color_hex: str | None = None, size: int = 28
    ) -> QIcon | None:
        """从 /icons/image/ 目录加载 SVG 并渲染为 QIcon，支持 PyInstaller 与源码两种运行方式。"""
        import sys

        # PyInstaller: 资源位于 sys._MEIPASS 根目录下的 icons/image/
        # 源码运行：以仓库根目录为基准（win11_design.py 位于 md-converter-gui/ui/ 下，向上两级到根）
        base_dir = Path(getattr(sys, "_MEIPASS", Path(__file__).resolve().parents[2]))
        p = base_dir / "icons" / "image" / filename
        if not p.exists():
            return None
        try:
            if QSvgRenderer is not None:
                renderer = QSvgRenderer(str(p))
                pix = QPixmap(size, size)
                pix.fill(Qt.GlobalColor.transparent)
                painter = QPainter(pix)
                renderer.render(painter)
                if color_hex:
                    painter.setCompositionMode(
                        QPainter.CompositionMode.CompositionMode_SourceIn
                    )
                    painter.fillRect(pix.rect(), QColor(color_hex))
                painter.end()
                return QIcon(pix)
            return QIcon(str(p))
        except Exception:
            return None

    def _em_px(self, ref_widget: QWidget, em: float) -> int:
        """把 em 转为像素：基于参考控件字体度量计算。"""
        try:
            fm = QFontMetrics(ref_widget.font())
            return int(fm.height() * em)
        except Exception:
            return int(16 * em)

    def _compute_logo_target_height(self) -> int:
        """计算顶部 Logo 目标高度：使用 2.9em（基于可用文本控件字体），并做上下限保护。"""
        try:
            ref = (
                getattr(self, "hero_subtitle_label", None)
                or getattr(self, "hero_logo_label", None)
                or self
            )
            return max(20, min(self._em_px(ref, 2.9), 64))
        except Exception:
            return 48

    def _set_hero_logo_scaled(self, logo_path: Path):
        """将 Logo 按目标高度等比缩放后设置到 hero_logo_label，不裁剪。"""
        try:
            if not hasattr(self, "hero_logo_label") or self.hero_logo_label is None:
                return
            if not logo_path or not logo_path.exists():
                return
            pix = QPixmap(str(logo_path))
            target_h = self._compute_logo_target_height()
            if target_h <= 0:
                target_h = 18
            scaled = pix.scaledToHeight(
                target_h, Qt.TransformationMode.SmoothTransformation
            )
            self.hero_logo_label.setPixmap(scaled)
            # 为底部预留少量空白，避免视觉上被裁切
            try:
                reserve = self._em_px(self.hero_logo_label, 0)
            except Exception:
                reserve = 0  # 减少到0像素
            label_h = target_h + reserve
            self.hero_logo_label.setContentsMargins(0, 0, 0, reserve)
            self.hero_logo_label.setFixedHeight(label_h)
            self.hero_logo_label.setMinimumHeight(label_h)
            self.hero_logo_label.setMaximumHeight(label_h)
            self.hero_logo_label.setSizePolicy(
                QSizePolicy.Policy.Fixed, QSizePolicy.Policy.Fixed
            )
        except Exception:
            pass

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

        # 顶部品牌 Logo（按主题切换图片）
        self.hero_logo_label = QLabel()
        self.hero_logo_label.setContentsMargins(0, 0, 0, 0)
        self.hero_logo_label.setAlignment(
            Qt.AlignmentFlag.AlignLeft | Qt.AlignmentFlag.AlignVCenter
        )

        subtitle = QLabel("粘贴或打开 Markdown，右侧调质量，点击开始转换")
        self.hero_subtitle_label = subtitle

        text_block = QWidget()
        v = QVBoxLayout()
        v.setContentsMargins(0, 0, 0, 0)
        try:
            v.setSpacing(self._em_px(subtitle, 0.5))
        except Exception:
            v.setSpacing(8)
        v.addWidget(self.hero_logo_label)
        v.addWidget(subtitle)
        # Hero 内的动作行：打开 / 粘贴 / 清空（紧凑款）
        actions_row = QHBoxLayout()
        actions_row.setContentsMargins(0, 0, 0, 0)
        actions_row.setSpacing(6)
        from PyQt6.QtWidgets import QToolButton

        self.hero_open_btn = QToolButton()
        self.hero_open_btn.setText("打开")
        self.hero_open_btn.setFixedHeight(34)
        self.hero_open_btn.setToolButtonStyle(Qt.ToolButtonStyle.ToolButtonTextOnly)
        self.hero_open_btn.clicked.connect(self.open_markdown_file)
        self.hero_paste_btn = QToolButton()
        self.hero_paste_btn.setText("粘贴")
        self.hero_paste_btn.setFixedHeight(34)
        self.hero_paste_btn.setToolButtonStyle(Qt.ToolButtonStyle.ToolButtonTextOnly)
        self.hero_paste_btn.clicked.connect(self.paste_from_clipboard)
        self.hero_clear_btn = QToolButton()
        self.hero_clear_btn.setText("清空")
        self.hero_clear_btn.setFixedHeight(34)
        self.hero_clear_btn.setToolButtonStyle(Qt.ToolButtonStyle.ToolButtonTextOnly)
        self.hero_clear_btn.clicked.connect(self.clear_editor)
        # 新增：图床入口
        self.hero_imagebed_btn = QToolButton()
        self.hero_imagebed_btn.setText("图床")
        self.hero_imagebed_btn.setFixedHeight(34)
        self.hero_imagebed_btn.setCursor(Qt.CursorShape.PointingHandCursor)
        self.hero_imagebed_btn.setToolButtonStyle(Qt.ToolButtonStyle.ToolButtonTextOnly)
        # 样式与前面三个一致（文本按钮，悬停高亮）
        self.hero_imagebed_btn.setStyleSheet(
            "QToolButton{background:transparent;color:#9CA3AF;padding:2px 8px;border:none;}"
            "QToolButton:hover{background:rgba(255,255,255,0.06);border-radius:4px;color:#E5E7EB;}"
            "QToolButton:pressed{background:rgba(255,255,255,0.10);}"
        )
        self.hero_imagebed_btn.clicked.connect(self.open_image_bed_dialog)
        actions_row.addWidget(self.hero_open_btn)
        actions_row.addWidget(self.hero_paste_btn)
        actions_row.addWidget(self.hero_clear_btn)
        actions_row.addWidget(self.hero_imagebed_btn)
        actions_row.addStretch()
        v.addLayout(actions_row)
        text_block.setLayout(v)

        start_btn = QPushButton("开始")
        start_btn.setFixedHeight(40)
        start_btn.setFixedWidth(120)
        # 样式由 tokens 注入
        self.hero_start_btn = start_btn
        try:
            start_btn.clicked.disconnect()
        except Exception:
            pass

        # 顶部"开始"采用合并流程：先转换，后上传，最后统一弹窗
        def _start_combined():
            self._combined_flow = True
            self.status_label.setText("正在转换...")
            self.real_conversion()

        start_btn.clicked.connect(_start_combined)

        layout.addWidget(text_block, 1)
        layout.addStretch()
        # 右侧放置主题切换图标按钮
        theme_btn = QToolButton()
        theme_btn.setToolButtonStyle(Qt.ToolButtonStyle.ToolButtonIconOnly)
        theme_btn.setFixedSize(38, 38)
        theme_btn.setCursor(Qt.CursorShape.PointingHandCursor)
        # 蓝色按钮，白色图标
        theme_btn.setStyleSheet(
            "QToolButton{background:#3B82F6;border:none;border-radius:8px;padding:4px 6px;color:#FFFFFF;}"
            "QToolButton:hover{background:#2563EB;}"
            "QToolButton:pressed{background:#1D4ED8;}"
        )
        theme_btn.clicked.connect(self.toggle_theme)
        self.theme_tool_btn = theme_btn
        # 初始图标由 update_icons 在 apply_theme 中设置
        # 右侧顺序：主题按钮 + 间距 + 开始按钮
        layout.addWidget(theme_btn, 0, Qt.AlignmentFlag.AlignVCenter)
        spacer = QWidget()
        spacer.setFixedWidth(6)
        layout.addWidget(spacer)
        layout.addWidget(start_btn, 0, Qt.AlignmentFlag.AlignVCenter)
        hero.setLayout(layout)
        # 自适应高度：按“Logo + 副标题 + 动作行”三者高度之和，再额外扩张 3em
        try:
            sub_h = (
                self.hero_subtitle_label.sizeHint().height()
                if hasattr(self, "hero_subtitle_label")
                else 0
            )
            row_h = max(
                self.hero_open_btn.sizeHint().height(),
                self.hero_paste_btn.sizeHint().height(),
                self.hero_clear_btn.sizeHint().height(),
                self.hero_imagebed_btn.sizeHint().height(),
            )
            right_btn_h = max(
                start_btn.sizeHint().height(),
                getattr(self, "theme_tool_btn", theme_btn).sizeHint().height(),
            )
            logo_h = self._compute_logo_target_height()
            try:
                reserve = self._em_px(self.hero_logo_label, 1.2)
            except Exception:
                reserve = 12
            logo_block_h = logo_h + reserve
            # 三块之间的布局间距（有两处间隔）
            try:
                gap = v.spacing()
            except Exception:
                gap = self._em_px(
                    (
                        self.hero_subtitle_label
                        if hasattr(self, "hero_subtitle_label")
                        else hero
                    ),
                    0.5,
                )
            total_gaps = gap * 2
            # 额外扩张 2em（适当缩小整体留白）
            extra = self._em_px(
                (
                    self.hero_subtitle_label
                    if hasattr(self, "hero_subtitle_label")
                    else hero
                ),
                2.0,
            )
            # 内容高度 = 三块高度和 + 间隔 + 额外 3em
            content_h = (
                logo_block_h + sub_h + max(row_h, right_btn_h) + total_gaps + extra
            )
            margins_v = 12 + 12
            h = content_h + margins_v
            # 将最小/最大固定为计算值（最低不小于 72），避免超出造成多余空白
            h = max(72, h)
            hero.setMinimumHeight(h)
            hero.setMaximumHeight(h)
        except Exception:
            pass
        return hero

    # 底部提示栏已删除

    def setup_menu_bar(self):
        """设置Win11风格菜单栏"""
        menubar = self.menuBar()
        # 直接隐藏菜单栏（去掉"文件/编辑/视图/工具/帮助"）
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

        # 主题切换按钮（FontAwesome 图标）
        self.theme_action = QAction("主题", self)
        self.theme_action.setStatusTip("切换深/浅色主题")
        # 初始图标在 apply_theme -> update_icons 中设置
        self.theme_action.triggered.connect(self.toggle_theme)
        toolbar.addAction(self.theme_action)

    def setup_status_bar(self):
        """设置Win11风格状态栏"""
        status_bar = self.statusBar()
        # 保存引用以便主题切换时统一控制（修复底部浅色问题）
        self.status_bar = status_bar

        # 左侧仅文字
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
        # 合并流程：点击任何"转换/开始"都执行先转换后上传
        self._combined_flow = True
        self.status_label.setText("正在转换...")
        self.real_conversion()

    def on_upload_clicked(self):
        """手动上传：把 images 下的 webp 上传并回写远程 URL"""
        try:
            self.start_upload(silent=False)
        except Exception as e:
            QMessageBox.critical(self, "上传失败", str(e))

    def start_upload(self, silent: bool = True):
        """启动上传流程；silent=True 时不弹窗，仅更新编辑器与状态栏"""
        base_dir = (
            os.path.dirname(self.current_file)
            if getattr(self, "current_file", None)
            else os.getcwd()
        )
        img_dir = os.path.join(base_dir, "images")
        try:
            print(
                f"[GUI] start_upload: base_dir={base_dir} img_dir={img_dir}", flush=True
            )
        except Exception:
            pass
        if not os.path.isdir(img_dir):
            if not silent:
                QMessageBox.information(self, "提示", "未找到 images 目录，请先执行转换。")
            return
        local_webps = [
            os.path.join(img_dir, n)
            for n in os.listdir(img_dir)
            if n.lower().endswith(".webp")
        ]
        try:
            print(
                f"[GUI] start_upload: found {len(local_webps)} webp files", flush=True
            )
        except Exception:
            pass
        if not local_webps:
            if not silent:
                QMessageBox.information(self, "提示", "没有可上传的 WebP 文件。")
            return
        self.status_label.setText("正在上传...")
        self.upload_worker = UploadWorker(base_dir, local_webps)
        self.upload_worker.progress_updated.connect(self.on_conversion_progress)
        try:
            print("[GUI] upload worker created", flush=True)
        except Exception:
            pass

        def _on_uploaded(mapping: dict):
            md = self.editor.toPlainText()
            new_md = self._replace_local_paths_with_remote(md, base_dir, mapping)
            self.editor.setPlainText(new_md)
            self.status_label.setText("上传完成")
            if not silent:
                # 合并流程下的统一弹窗在上传完成后显示
                if self._combined_flow:
                    cnt = self._last_convert_count
                    stats = self._last_convert_stats or {}
                    from .utils import format_size_human as format_size

                    original_size = stats.get("total_original_size", 0)
                    saved_size = stats.get("size_saved", 0)
                    compression_ratio = stats.get("compression_ratio", 0)
                    msg = f"成功转换并上传 {cnt} 张图片！\n\n"
                    if original_size > 0:
                        msg += f"原始大小: {format_size(original_size)}\n"
                        msg += f"节省空间: {format_size(saved_size)}\n"
                        msg += f"压缩比例: {compression_ratio:.1f}%\n\n"
                    msg += "图片已保存到 images 目录并替换为外链。"
                    QMessageBox.information(self, "完成", msg)
                    self._combined_flow = False
                else:
                    QMessageBox.information(self, "上传完成", "已将本地图片链接替换为远程 URL")

        self.upload_worker.finished_with_mapping.connect(_on_uploaded)
        if silent:
            self.upload_worker.error.connect(lambda e: None)
        else:
            self.upload_worker.error.connect(
                lambda e: QMessageBox.critical(self, "上传失败", e)
            )
        self.upload_worker.start()

    # === 内置一份转换实现，确保方法存在于类上（避免外部重复定义导致找不到） ===
    def real_conversion(self):
        """真正的图片转换过程（类内实现）"""
        markdown_text = self.editor.toPlainText().strip()
        if not markdown_text:
            QMessageBox.information(self, "提示", "请先输入Markdown内容")
            self.status_label.setText("就绪")
            return

        # 预检图片链接
        try:
            import re as _re

            pattern = r'(?:!\[.*?\]\s*\((.*?)\))|(?:<img.*?src=["\']([^"\']*)["\'].*?>)'
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
                QMessageBox.information(
                    self,
                    "未找到图片",
                    '未检测到 Markdown 中的图片链接，请确认语法：\n\n![](http://...) 或 <img src="...">',
                )
                return
        except Exception:
            pass

        # 目录 / 质量
        base_dir = (
            os.path.dirname(self.current_file)
            if getattr(self, "current_file", None)
            else os.getcwd()
        )
        output_dir = os.path.join(base_dir, "images")
        quality = getattr(self.control_panel, "quality_value", 73)

        # 重置统计与UI
        if hasattr(self.control_panel, "reset_compression_stats"):
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
        if (
            hasattr(self, "conversion_watchdog")
            and self.conversion_watchdog is not None
        ):
            self.conversion_watchdog.stop()
        # 暂时禁用超时功能，避免误报
        # self.conversion_watchdog = QTimer(self)
        # self.conversion_watchdog.setSingleShot(True)
        # self.conversion_watchdog.timeout.connect(self.on_conversion_timeout)
        # self.conversion_watchdog.start(120000)

    def on_conversion_progress(self, progress, message):
        self.control_panel.set_progress(progress)
        self.status_label.setText(message)
        # 超时功能已禁用
        # if hasattr(self, 'conversion_watchdog') and self.conversion_watchdog is not None and progress < 100:
        #     self.conversion_watchdog.start(120000)

    def on_conversion_finished(self, new_markdown, count, stats):
        if (
            hasattr(self, "conversion_watchdog")
            and self.conversion_watchdog is not None
        ):
            self.conversion_watchdog.stop()
        self.editor.setPlainText(new_markdown)
        if hasattr(self.control_panel, "update_compression_stats"):
            self.control_panel.update_compression_stats(stats)
        self.control_panel.convert_btn.setEnabled(True)
        self.control_panel.convert_btn.setText("转换")
        self.control_panel.set_progress(0)
        self.status_label.setText(f"转换完成！成功转换 {count} 张图片")

        # 记录统计以便合并流程统一弹窗
        self._last_convert_count = count
        self._last_convert_stats = stats

        from .utils import format_size_human as format_size

        original_size = stats.get("total_original_size", 0)
        saved_size = stats.get("size_saved", 0)
        compression_ratio = stats.get("compression_ratio", 0)

        # 合并流程：不在此处弹窗，转而触发上传
        if getattr(self, "_combined_flow", False):
            # 无图片则仍提示
            if count <= 0 and original_size == 0:
                QMessageBox.information(
                    self,
                    "未找到图片",
                    '未检测到 Markdown 中的图片链接，请确认语法：\n\n![](http://...) 或 <img src="...">',
                )
                self._combined_flow = False
                return
            # 触发上传
            try:
                self.status_label.setText("转换完成，准备上传...")
                QTimer.singleShot(0, lambda: self.start_upload(silent=False))
            except Exception:
                pass
            return

        # 非合并流程：保持原有弹窗
        if count <= 0 and original_size == 0:
            QMessageBox.information(
                self,
                "未找到图片",
                '未检测到 Markdown 中的图片链接，请确认语法：\n\n![](http://...) 或 <img src="...">',
            )
        else:
            msg = f"成功转换 {count} 张图片为WebP格式！\n\n"
            if original_size > 0:
                msg += f"原始大小: {format_size(original_size)}\n"
                msg += f"节省空间: {format_size(saved_size)}\n"
                msg += f"压缩比例: {compression_ratio:.1f}%\n\n"
            msg += "图片已保存到 images 目录。"
            QMessageBox.information(self, "转换完成", msg)

    def on_conversion_error(self, error_message):
        if (
            hasattr(self, "conversion_watchdog")
            and self.conversion_watchdog is not None
        ):
            self.conversion_watchdog.stop()
        self.control_panel.convert_btn.setEnabled(True)
        self.control_panel.convert_btn.setText("转换")
        self.control_panel.set_progress(0)
        self.status_label.setText("转换失败")
        QMessageBox.critical(self, "转换失败", error_message)

    def on_conversion_timeout(self):
        # 检查转换是否实际上已经完成了
        if hasattr(self, "conversion_thread") and self.conversion_thread is not None:
            if not self.conversion_thread.isRunning():
                print("[GUI] timeout but thread already finished, ignoring", flush=True)
                return

        print("[GUI] conversion timeout triggered (first handler)", flush=True)
        self.control_panel.convert_btn.setEnabled(True)
        self.control_panel.convert_btn.setText("转换")
        self.status_label.setText("转换超时，请检查网络或图片链接")
        QMessageBox.warning(
            self,
            "转换超时",
            "转换耗时过长，可能网络较慢或图片地址不可达。稍后重试，或检查图片 URL。",
        )

    def _replace_local_paths_with_remote(
        self, md: str, base_dir: str, mapping: dict
    ) -> str:
        def rel(p: str) -> tuple[str, str]:
            rp = os.path.relpath(p, base_dir).replace("\\", "/")
            rp2 = "./" + rp if not rp.startswith("./") else rp
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
        """在深色与浅色主题间切换（使用 FontAwesome 图标）"""
        try:
            self.current_theme_dark = not getattr(self, "current_theme_dark", False)
        except Exception:
            self.current_theme_dark = False
        self.apply_theme(self.current_theme_dark)

    # ===== 图床设置对话框（骨架） =====
    def open_image_bed_dialog(self):
        if not hasattr(self, "imagebed_dialog"):
            self.imagebed_dialog = ImageBedDialog(self)
            # 主题随窗口刷新
            # 图床设置弹窗固定使用深色主题
            self.imagebed_dialog.apply_theme(True)
        else:
            # 二次打开时刷新已保存配置
            try:
                if hasattr(self.imagebed_dialog, "load_from_settings"):
                    self.imagebed_dialog.load_from_settings()
            except Exception:
                pass
        self.imagebed_dialog.show()
        self.imagebed_dialog.raise_()
        self.imagebed_dialog.activateWindow()

    # ===== 额外功能：文件/粘贴/清空 =====
    def open_markdown_file(self):
        path, _ = QFileDialog.getOpenFileName(
            self,
            "打开 Markdown",
            os.getcwd(),
            "Markdown (*.md *.markdown);;所有文件 (*.*)",
        )
        if not path:
            return
        try:
            with open(path, "r", encoding="utf-8") as f:
                text = f.read()
        except Exception:
            with open(path, "r", encoding="gbk", errors="ignore") as f:
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
        """根据主题更新图标。主题按钮使用本地 /image 下 SVG；其余图标若可用使用 qtawesome。"""
        # 主题图标
        # 主题图标：优先给工具栏按钮赋值；若无，则尝试给 Hero 的 theme_tool_btn 赋值
        if hasattr(self, "theme_action"):
            # 固定使用根目录 /image 两个文件：fa-circle-half-stroke.svg（浅色）/ fa-lightbulb.svg（深色）
            light_icon = self._icon_from_svg_file("circle-half-stroke-solid-full.svg")
            dark_icon = self._icon_from_svg_file("lightbulb-solid-full.svg")
            theme_icon = dark_icon if dark else light_icon
            if theme_icon is not None:
                self.theme_action.setIcon(theme_icon)
        if hasattr(self, "theme_tool_btn"):
            # 图标统一使用白色
            light_icon = self._icon_from_svg_file(
                "circle-half-stroke-solid-full.svg", "#FFFFFF", 28
            )
            dark_icon = self._icon_from_svg_file(
                "lightbulb-solid-full.svg", "#FFFFFF", 28
            )
            theme_icon = dark_icon if dark else light_icon
            if theme_icon is not None:
                self.theme_tool_btn.setIcon(theme_icon)
                self.theme_tool_btn.setIconSize(QSize(28, 28))
                self.theme_tool_btn.setText("")
            else:
                # 文本替代：浅色显示 []，深色显示 ()
                self.theme_tool_btn.setIcon(QIcon())
                self.theme_tool_btn.setText("()" if dark else "[]")

        # 以下图标若 qtawesome 可用则更新，否则跳过
        if qta is None:
            return
        # 工具栏图标
        common_color = "#e5e7eb" if dark else "#111827"
        if hasattr(self, "open_action"):
            self.open_action.setIcon(qta.icon("fa5s.folder-open", color=common_color))
        if hasattr(self, "paste_action"):
            self.paste_action.setIcon(qta.icon("fa5s.paste", color=common_color))
        if hasattr(self, "clear_action"):
            self.clear_action.setIcon(qta.icon("fa5s.trash-alt", color=common_color))
        # 转换主按钮图标
        self.control_panel.convert_btn.setIcon(qta.icon("fa5s.play", color="#ffffff"))
        self.control_panel.convert_btn.setIconSize(QSize(16, 16))


class ImageBedDialog(QDialog):
    """图床设置对话框 - 骨架实现"""

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("图床设置")
        self.setModal(False)
        self.setMinimumSize(560, 420)
        self._build_ui()
        # 初始化时从本地配置加载
        try:
            self.load_from_settings()
        except Exception:
            pass

    def _build_ui(self):
        root = QVBoxLayout(self)
        # 顶部：图床选择与状态
        top = QHBoxLayout()
        top.addWidget(QLabel("图床："))
        self.provider_combo = QComboBox()
        self.provider_combo.addItems(
            [
                "七牛 v1.0",
                "腾讯云 COS v4 v1.1",
                "腾讯云 COS v5 v1.5.0",
                "又拍云 v1.2.0",
                "GitHub v1.5.0",
                "SM.MS V2 v2.3.0-beta.0",
                "阿里云 OSS v1.6.0",
                "Imgur v1.6.0",
            ]
        )
        top.addWidget(self.provider_combo)
        top.addStretch()
        self.status_chip = QLabel("未测试")
        self.status_chip.setStyleSheet(
            "QLabel{padding:2px 10px;border-radius:10px;background:#f1f5f9;color:#334155;font-size:12px;}"
        )
        top.addWidget(self.status_chip)
        root.addLayout(top)

        # Tabs
        self.tabs = QTabWidget(self)
        self.tab_status = QWidget()
        self.tab_config = QWidget()
        self.tabs.addTab(self.tab_status, "选择与状态")
        self.tabs.addTab(self.tab_config, "凭据与配置")
        root.addWidget(self.tabs)

        # 选择与状态
        st = QVBoxLayout(self.tab_status)
        st.addWidget(QLabel('说明：选择图床后，可在下方"保存"并稍后进行上传测试。'))
        st.addStretch()

        # 凭据与配置（动态表单）
        scroll = QScrollArea(self.tab_config)
        scroll.setWidgetResizable(True)
        self.config_host = QWidget()
        self.config_form = QVBoxLayout(self.config_host)

        # 创建所有可能用到的字段
        self.fields = {}
        self._init_all_fields()

        # 连接provider切换事件
        self.provider_combo.currentTextChanged.connect(self._update_config_form)

        scroll.setWidget(self.config_host)
        cfg = QVBoxLayout(self.tab_config)
        cfg.addWidget(scroll)

        # 移除"高级与策略"页，默认始终启用自动上传

        # 底部按钮：保存 / 测试上传 / 关闭
        btns = QDialogButtonBox(
            QDialogButtonBox.StandardButton.Save | QDialogButtonBox.StandardButton.Close
        )
        self.test_btn = QPushButton("测试上传")
        btns.addButton(self.test_btn, QDialogButtonBox.ButtonRole.ActionRole)
        self.clear_btn = QPushButton("清空")
        btns.addButton(self.clear_btn, QDialogButtonBox.ButtonRole.ActionRole)
        btns.accepted.connect(self.on_save)
        btns.rejected.connect(self.reject)
        self.test_btn.clicked.connect(self.on_test_upload)
        self.clear_btn.clicked.connect(self.on_clear)
        root.addWidget(btns)

    def _init_all_fields(self):
        """初始化所有可能的配置字段"""
        from PyQt6.QtWidgets import QCheckBox, QLineEdit

        # 通用字段
        self.fields["endpoint"] = QLineEdit()
        self.fields["bucket"] = QLineEdit()
        self.fields["access_id"] = QLineEdit()
        self.fields["access_secret"] = QLineEdit()
        self.fields["access_secret"].setEchoMode(QLineEdit.EchoMode.Password)

        # 腾讯云COS特有
        self.fields["secret_id"] = QLineEdit()
        self.fields["secret_key"] = QLineEdit()
        self.fields["secret_key"].setEchoMode(QLineEdit.EchoMode.Password)
        self.fields["region"] = QLineEdit()

        # 七牛云特有
        self.fields["domain"] = QLineEdit()

        # GitHub特有
        self.fields["token"] = QLineEdit()
        self.fields["token"].setEchoMode(QLineEdit.EchoMode.Password)
        self.fields["owner"] = QLineEdit()
        self.fields["repo"] = QLineEdit()
        self.fields["branch"] = QLineEdit()
        self.fields["path_prefix"] = QLineEdit()

        # 通用可选字段
        self.fields["custom_domain"] = QLineEdit()
        self.fields["prefix"] = QLineEdit()
        self.fields["use_https"] = QCheckBox("使用HTTPS")
        self.fields["use_https"].setChecked(True)
        self.fields["use_jsdelivr"] = QCheckBox("使用jsDelivr CDN")
        self.fields["path_style"] = QCheckBox("使用路径风格URL")

    def _update_config_form(self):
        """根据选择的图床类型更新配置表单"""
        # 清空现有表单
        while self.config_form.count():
            child = self.config_form.takeAt(0)
            if child.widget():
                child.widget().setParent(None)

        provider = self._provider_key()

        if provider == "aliyun_oss":
            self._build_aliyun_form()
        elif provider == "cos_v5":
            self._build_cos_form()
        elif provider == "qiniu":
            self._build_qiniu_form()
        elif provider == "s3":
            self._build_s3_form()
        elif provider == "github":
            self._build_github_form()
        else:
            self._build_generic_form()

        self.config_form.addStretch()

    def _build_aliyun_form(self):
        """构建阿里云OSS配置表单"""
        from PyQt6.QtWidgets import QLabel

        self.config_form.addWidget(QLabel("地域前缀(如 oss-cn-beijing)"))
        self.config_form.addWidget(self.fields["endpoint"])
        self.config_form.addWidget(QLabel("Bucket名称"))
        self.config_form.addWidget(self.fields["bucket"])
        self.config_form.addWidget(QLabel("AccessKey ID"))
        self.config_form.addWidget(self.fields["access_id"])
        self.config_form.addWidget(QLabel("AccessKey Secret"))
        self.config_form.addWidget(self.fields["access_secret"])
        self.config_form.addWidget(QLabel("路径前缀(可选)"))
        self.config_form.addWidget(self.fields["prefix"])
        self.config_form.addWidget(QLabel("自定义域名(可选)"))
        self.config_form.addWidget(self.fields["custom_domain"])

    def _build_cos_form(self):
        """构建腾讯云COS配置表单"""
        from PyQt6.QtWidgets import QLabel

        self.config_form.addWidget(QLabel("Secret ID"))
        self.config_form.addWidget(self.fields["secret_id"])
        self.config_form.addWidget(QLabel("Secret Key"))
        self.config_form.addWidget(self.fields["secret_key"])
        self.config_form.addWidget(QLabel("Bucket名称"))
        self.config_form.addWidget(self.fields["bucket"])
        self.config_form.addWidget(QLabel("地域(如 ap-beijing)"))
        self.config_form.addWidget(self.fields["region"])
        self.config_form.addWidget(QLabel("路径前缀(可选)"))
        self.config_form.addWidget(self.fields["prefix"])
        self.config_form.addWidget(QLabel("自定义域名(可选)"))
        self.config_form.addWidget(self.fields["custom_domain"])
        self.config_form.addWidget(self.fields["use_https"])

    def _build_qiniu_form(self):
        """构建七牛云配置表单"""
        from PyQt6.QtWidgets import QLabel

        self.config_form.addWidget(QLabel("Access Key"))
        self.config_form.addWidget(self.fields["access_id"])
        self.config_form.addWidget(QLabel("Secret Key"))
        self.config_form.addWidget(self.fields["access_secret"])
        self.config_form.addWidget(QLabel("Bucket名称"))
        self.config_form.addWidget(self.fields["bucket"])
        self.config_form.addWidget(QLabel("绑定域名"))
        self.config_form.addWidget(self.fields["domain"])
        self.config_form.addWidget(QLabel("路径前缀(可选)"))
        self.config_form.addWidget(self.fields["prefix"])
        self.config_form.addWidget(self.fields["use_https"])

    def _build_s3_form(self):
        """构建S3配置表单"""
        from PyQt6.QtWidgets import QLabel

        self.config_form.addWidget(QLabel("Access Key"))
        self.config_form.addWidget(self.fields["access_id"])
        self.config_form.addWidget(QLabel("Secret Key"))
        self.config_form.addWidget(self.fields["access_secret"])
        self.config_form.addWidget(QLabel("Bucket名称"))
        self.config_form.addWidget(self.fields["bucket"])
        self.config_form.addWidget(QLabel("地域(AWS必填,其他可选)"))
        self.config_form.addWidget(self.fields["region"])
        self.config_form.addWidget(QLabel("端点URL(MinIO等自建服务必填)"))
        self.config_form.addWidget(self.fields["endpoint"])
        self.config_form.addWidget(QLabel("路径前缀(可选)"))
        self.config_form.addWidget(self.fields["prefix"])
        self.config_form.addWidget(QLabel("自定义域名(可选)"))
        self.config_form.addWidget(self.fields["custom_domain"])
        self.config_form.addWidget(self.fields["use_https"])
        self.config_form.addWidget(self.fields["path_style"])

    def _build_github_form(self):
        """构建GitHub配置表单"""
        from PyQt6.QtWidgets import QLabel

        self.config_form.addWidget(QLabel("Personal Access Token"))
        self.config_form.addWidget(self.fields["token"])
        self.config_form.addWidget(QLabel("用户名/组织名"))
        self.config_form.addWidget(self.fields["owner"])
        self.config_form.addWidget(QLabel("仓库名"))
        self.config_form.addWidget(self.fields["repo"])
        self.config_form.addWidget(QLabel("分支名"))
        self.fields["branch"].setText("main")
        self.config_form.addWidget(self.fields["branch"])
        self.config_form.addWidget(QLabel("仓库路径前缀(可选)"))
        self.config_form.addWidget(self.fields["path_prefix"])
        self.config_form.addWidget(QLabel("存储路径前缀(可选)"))
        self.config_form.addWidget(self.fields["prefix"])
        self.config_form.addWidget(QLabel("自定义域名(可选)"))
        self.config_form.addWidget(self.fields["custom_domain"])
        self.config_form.addWidget(self.fields["use_jsdelivr"])

    def _build_generic_form(self):
        """构建通用配置表单"""
        from PyQt6.QtWidgets import QLabel

        self.config_form.addWidget(QLabel("该图床暂未支持，请选择其他图床"))

    def apply_theme(self, dark: bool):
        if dark:
            self.setStyleSheet("QDialog{background:#0F141A;color:#E6EAF0;}")
        else:
            self.setStyleSheet("QDialog{background:#FFFFFF;color:#0F172A;}")

    def load_from_settings(self):
        """从 QSettings 读取并预填表单（支持已配置的图床二次打开缓存）。"""
        settings = QSettings("MdImgConverter", "Settings")
        try:
            settings.sync()
        except Exception:
            pass
        # 选择图床
        prov = settings.value("imgbed/provider", "aliyun_oss") or "aliyun_oss"
        # 根据 provider 文本匹配下拉项
        text_map = {
            "aliyun_oss": "阿里云 OSS",
            "qiniu": "七牛",
            "cos_v4": "腾讯云 COS v4",
            "cos_v5": "腾讯云 COS v5",
            "upyun": "又拍云",
            "github": "GitHub",
            "smms": "SM.MS",
            "imgur": "Imgur",
            "s3": "S3",
        }
        target = text_map.get(prov, "阿里云 OSS")
        for i in range(self.provider_combo.count()):
            if target in self.provider_combo.itemText(i):
                self.provider_combo.setCurrentIndex(i)
                break

        # 更新表单显示
        self._update_config_form()

        # 加载对应图床的配置
        self._load_provider_config(prov, settings)

        # 状态提示
        if self._has_basic_config(prov, settings):
            self.status_chip.setText("已加载配置")
        else:
            self.status_chip.setText("未测试")

    def _load_provider_config(self, provider: str, settings):
        """加载指定图床的配置"""
        if provider == "aliyun_oss":
            self.fields["endpoint"].setText(
                str(settings.value("imgbed/aliyun/endpoint", "")) or ""
            )
            self.fields["bucket"].setText(
                str(settings.value("imgbed/aliyun/bucket", "")) or ""
            )
            self.fields["access_id"].setText(
                str(settings.value("imgbed/aliyun/accessKeyId", "")) or ""
            )
            self.fields["access_secret"].setText(
                str(settings.value("imgbed/aliyun/accessKeySecret", "")) or ""
            )
            self.fields["prefix"].setText(
                str(settings.value("imgbed/aliyun/prefix", "images")) or "images"
            )
            self.fields["custom_domain"].setText(
                str(settings.value("imgbed/aliyun/customDomain", "")) or ""
            )
        elif provider == "cos_v5":
            self.fields["secret_id"].setText(
                str(settings.value("imgbed/cos/secretId", "")) or ""
            )
            self.fields["secret_key"].setText(
                str(settings.value("imgbed/cos/secretKey", "")) or ""
            )
            self.fields["bucket"].setText(
                str(settings.value("imgbed/cos/bucket", "")) or ""
            )
            self.fields["region"].setText(
                str(settings.value("imgbed/cos/region", "")) or ""
            )
            self.fields["prefix"].setText(
                str(settings.value("imgbed/cos/prefix", "images")) or "images"
            )
            self.fields["custom_domain"].setText(
                str(settings.value("imgbed/cos/customDomain", "")) or ""
            )
            self.fields["use_https"].setChecked(
                settings.value("imgbed/cos/useHttps", True, type=bool)
            )
        elif provider == "qiniu":
            self.fields["access_id"].setText(
                str(settings.value("imgbed/qiniu/accessKey", "")) or ""
            )
            self.fields["access_secret"].setText(
                str(settings.value("imgbed/qiniu/secretKey", "")) or ""
            )
            self.fields["bucket"].setText(
                str(settings.value("imgbed/qiniu/bucket", "")) or ""
            )
            self.fields["domain"].setText(
                str(settings.value("imgbed/qiniu/domain", "")) or ""
            )
            self.fields["prefix"].setText(
                str(settings.value("imgbed/qiniu/prefix", "images")) or "images"
            )
            self.fields["use_https"].setChecked(
                settings.value("imgbed/qiniu/useHttps", True, type=bool)
            )
        elif provider == "s3":
            self.fields["access_id"].setText(
                str(settings.value("imgbed/s3/accessKey", "")) or ""
            )
            self.fields["access_secret"].setText(
                str(settings.value("imgbed/s3/secretKey", "")) or ""
            )
            self.fields["bucket"].setText(
                str(settings.value("imgbed/s3/bucket", "")) or ""
            )
            self.fields["region"].setText(
                str(settings.value("imgbed/s3/region", "")) or ""
            )
            self.fields["endpoint"].setText(
                str(settings.value("imgbed/s3/endpoint", "")) or ""
            )
            self.fields["prefix"].setText(
                str(settings.value("imgbed/s3/prefix", "images")) or "images"
            )
            self.fields["custom_domain"].setText(
                str(settings.value("imgbed/s3/customDomain", "")) or ""
            )
            self.fields["use_https"].setChecked(
                settings.value("imgbed/s3/useHttps", True, type=bool)
            )
            self.fields["path_style"].setChecked(
                settings.value("imgbed/s3/pathStyle", False, type=bool)
            )
        elif provider == "github":
            self.fields["token"].setText(
                str(settings.value("imgbed/github/token", "")) or ""
            )
            self.fields["owner"].setText(
                str(settings.value("imgbed/github/owner", "")) or ""
            )
            self.fields["repo"].setText(
                str(settings.value("imgbed/github/repo", "")) or ""
            )
            self.fields["branch"].setText(
                str(settings.value("imgbed/github/branch", "main")) or "main"
            )
            self.fields["path_prefix"].setText(
                str(settings.value("imgbed/github/pathPrefix", "")) or ""
            )
            self.fields["prefix"].setText(
                str(settings.value("imgbed/github/prefix", "images")) or "images"
            )
            self.fields["custom_domain"].setText(
                str(settings.value("imgbed/github/customDomain", "")) or ""
            )
            self.fields["use_jsdelivr"].setChecked(
                settings.value("imgbed/github/useJsdelivr", False, type=bool)
            )

    def _has_basic_config(self, provider: str, settings) -> bool:
        """检查是否有基本配置"""
        if provider == "aliyun_oss":
            return all(
                [
                    settings.value("imgbed/aliyun/endpoint", ""),
                    settings.value("imgbed/aliyun/bucket", ""),
                    settings.value("imgbed/aliyun/accessKeyId", ""),
                    settings.value("imgbed/aliyun/accessKeySecret", ""),
                ]
            )
        elif provider == "cos_v5":
            return all(
                [
                    settings.value("imgbed/cos/secretId", ""),
                    settings.value("imgbed/cos/secretKey", ""),
                    settings.value("imgbed/cos/bucket", ""),
                    settings.value("imgbed/cos/region", ""),
                ]
            )
        elif provider == "qiniu":
            return all(
                [
                    settings.value("imgbed/qiniu/accessKey", ""),
                    settings.value("imgbed/qiniu/secretKey", ""),
                    settings.value("imgbed/qiniu/bucket", ""),
                    settings.value("imgbed/qiniu/domain", ""),
                ]
            )
        elif provider == "s3":
            return all(
                [
                    settings.value("imgbed/s3/accessKey", ""),
                    settings.value("imgbed/s3/secretKey", ""),
                    settings.value("imgbed/s3/bucket", ""),
                ]
            )
        elif provider == "github":
            return all(
                [
                    settings.value("imgbed/github/token", ""),
                    settings.value("imgbed/github/owner", ""),
                    settings.value("imgbed/github/repo", ""),
                ]
            )
        return False

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
        if "S3" in text:
            return "s3"
        return ""

    def _normalize_aliyun_endpoint(self, region_prefix: str) -> str:
        rp = region_prefix.strip()
        if rp == "":
            return ""
        # 支持 @ 前缀：表示“按原样使用”
        if rp.startswith("@"):
            rp = rp[1:].strip()
        # 已是完整地址
        if rp.startswith("http://") or rp.startswith("https://"):
            return rp
        # 已包含域名但无协议
        if "aliyuncs.com" in rp:
            return f"https://{rp}"
        # 只填地域前缀
        return f"https://{rp}.aliyuncs.com"

    def on_save(self):
        settings = QSettings("MdImgConverter", "Settings")
        prov = self._provider_key()

        # 保存当前选择的图床类型
        settings.setValue("imgbed/provider", prov)
        settings.setValue("imgbed/enabled", True)

        # 根据图床类型保存对应的配置
        self._save_provider_config(prov, settings)

        # 立即落盘，避免下次打开读取到旧值
        try:
            settings.sync()
        except Exception:
            pass
        self.status_chip.setText("已保存（未测试）")
        self.accept()

    def _save_provider_config(self, provider: str, settings):
        """保存指定图床的配置"""
        if provider == "aliyun_oss":
            endpoint = self._normalize_aliyun_endpoint(self.fields["endpoint"].text())
            settings.setValue("imgbed/aliyun/endpoint", endpoint)
            settings.setValue(
                "imgbed/aliyun/bucket", self.fields["bucket"].text().strip()
            )
            settings.setValue(
                "imgbed/aliyun/accessKeyId", self.fields["access_id"].text().strip()
            )
            settings.setValue(
                "imgbed/aliyun/accessKeySecret",
                self.fields["access_secret"].text().strip(),
            )
            settings.setValue(
                "imgbed/aliyun/prefix", self.fields["prefix"].text().strip() or "images"
            )
            settings.setValue(
                "imgbed/aliyun/customDomain",
                self.fields["custom_domain"].text().strip(),
            )
        elif provider == "cos_v5":
            settings.setValue(
                "imgbed/cos/secretId", self.fields["secret_id"].text().strip()
            )
            settings.setValue(
                "imgbed/cos/secretKey", self.fields["secret_key"].text().strip()
            )
            settings.setValue("imgbed/cos/bucket", self.fields["bucket"].text().strip())
            settings.setValue("imgbed/cos/region", self.fields["region"].text().strip())
            settings.setValue(
                "imgbed/cos/prefix", self.fields["prefix"].text().strip() or "images"
            )
            settings.setValue(
                "imgbed/cos/customDomain", self.fields["custom_domain"].text().strip()
            )
            settings.setValue(
                "imgbed/cos/useHttps", self.fields["use_https"].isChecked()
            )
        elif provider == "qiniu":
            settings.setValue(
                "imgbed/qiniu/accessKey", self.fields["access_id"].text().strip()
            )
            settings.setValue(
                "imgbed/qiniu/secretKey", self.fields["access_secret"].text().strip()
            )
            settings.setValue(
                "imgbed/qiniu/bucket", self.fields["bucket"].text().strip()
            )
            settings.setValue(
                "imgbed/qiniu/domain", self.fields["domain"].text().strip()
            )
            settings.setValue(
                "imgbed/qiniu/prefix", self.fields["prefix"].text().strip() or "images"
            )
            settings.setValue(
                "imgbed/qiniu/useHttps", self.fields["use_https"].isChecked()
            )
        elif provider == "s3":
            settings.setValue(
                "imgbed/s3/accessKey", self.fields["access_id"].text().strip()
            )
            settings.setValue(
                "imgbed/s3/secretKey", self.fields["access_secret"].text().strip()
            )
            settings.setValue("imgbed/s3/bucket", self.fields["bucket"].text().strip())
            settings.setValue("imgbed/s3/region", self.fields["region"].text().strip())
            settings.setValue(
                "imgbed/s3/endpoint", self.fields["endpoint"].text().strip()
            )
            settings.setValue(
                "imgbed/s3/prefix", self.fields["prefix"].text().strip() or "images"
            )
            settings.setValue(
                "imgbed/s3/customDomain", self.fields["custom_domain"].text().strip()
            )
            settings.setValue(
                "imgbed/s3/useHttps", self.fields["use_https"].isChecked()
            )
            settings.setValue(
                "imgbed/s3/pathStyle", self.fields["path_style"].isChecked()
            )
        elif provider == "github":
            settings.setValue(
                "imgbed/github/token", self.fields["token"].text().strip()
            )
            settings.setValue(
                "imgbed/github/owner", self.fields["owner"].text().strip()
            )
            settings.setValue("imgbed/github/repo", self.fields["repo"].text().strip())
            settings.setValue(
                "imgbed/github/branch", self.fields["branch"].text().strip() or "main"
            )
            settings.setValue(
                "imgbed/github/pathPrefix", self.fields["path_prefix"].text().strip()
            )
            settings.setValue(
                "imgbed/github/prefix", self.fields["prefix"].text().strip() or "images"
            )
            settings.setValue(
                "imgbed/github/customDomain",
                self.fields["custom_domain"].text().strip(),
            )
            settings.setValue(
                "imgbed/github/useJsdelivr", self.fields["use_jsdelivr"].isChecked()
            )

    # === 业务：测试上传一张内存图片 ===
    def on_test_upload(self):
        """测试当前配置的图床上传功能"""
        try:
            from io import BytesIO

            from PIL import Image
        except Exception as e:
            QMessageBox.warning(self, "缺少依赖", f"测试失败：{e}")
            return

        prov = self._provider_key()

        # 检查基本配置
        if not self._validate_current_config(prov):
            return

        try:
            # 创建测试图片
            img = Image.new("RGB", (2, 2), (0, 255, 0))
            buf = BytesIO()
            img.save(buf, format="WEBP", quality=75)
            test_data = buf.getvalue()

            # 创建对应的适配器并测试上传
            adapter = self._create_test_adapter(prov)
            if not adapter:
                return

            url = adapter.upload_bytes(test_data, "mdimgconverter_test.webp")
            self.status_chip.setText("测试成功")
            QMessageBox.information(self, "测试成功", f"已上传：\n{url}")

        except Exception as e:
            self.status_chip.setText("测试失败")
            QMessageBox.critical(self, "测试失败", str(e))

    def _validate_current_config(self, provider: str) -> bool:
        """验证当前图床配置是否完整"""
        missing_fields = []

        if provider == "aliyun_oss":
            if not self.fields["endpoint"].text().strip():
                missing_fields.append("地域端点")
            if not self.fields["bucket"].text().strip():
                missing_fields.append("Bucket")
            if not self.fields["access_id"].text().strip():
                missing_fields.append("AccessKey ID")
            if not self.fields["access_secret"].text().strip():
                missing_fields.append("AccessKey Secret")
        elif provider == "cos_v5":
            if not self.fields["secret_id"].text().strip():
                missing_fields.append("Secret ID")
            if not self.fields["secret_key"].text().strip():
                missing_fields.append("Secret Key")
            if not self.fields["bucket"].text().strip():
                missing_fields.append("Bucket")
            if not self.fields["region"].text().strip():
                missing_fields.append("地域")
        elif provider == "qiniu":
            if not self.fields["access_id"].text().strip():
                missing_fields.append("Access Key")
            if not self.fields["access_secret"].text().strip():
                missing_fields.append("Secret Key")
            if not self.fields["bucket"].text().strip():
                missing_fields.append("Bucket")
            if not self.fields["domain"].text().strip():
                missing_fields.append("绑定域名")
        elif provider == "s3":
            if not self.fields["access_id"].text().strip():
                missing_fields.append("Access Key")
            if not self.fields["access_secret"].text().strip():
                missing_fields.append("Secret Key")
            if not self.fields["bucket"].text().strip():
                missing_fields.append("Bucket")
        elif provider == "github":
            if not self.fields["token"].text().strip():
                missing_fields.append("Token")
            if not self.fields["owner"].text().strip():
                missing_fields.append("用户名/组织名")
            if not self.fields["repo"].text().strip():
                missing_fields.append("仓库名")
        else:
            QMessageBox.information(self, "提示", "该图床类型暂不支持测试上传。")
            return False

        if missing_fields:
            QMessageBox.warning(
                self, "配置不完整", f"请填写以下必需字段：\n{', '.join(missing_fields)}"
            )
            return False

        return True

    def _create_test_adapter(self, provider: str):
        """创建用于测试的适配器实例"""
        try:
            if provider == "aliyun_oss":
                from uploader.ali_oss_adapter import AliOssAdapter

                endpoint = self._normalize_aliyun_endpoint(
                    self.fields["endpoint"].text()
                )
                return AliOssAdapter(
                    access_key_id=self.fields["access_id"].text().strip(),
                    access_key_secret=self.fields["access_secret"].text().strip(),
                    bucket_name=self.fields["bucket"].text().strip(),
                    endpoint=endpoint,
                    storage_path_prefix=self.fields["prefix"].text().strip()
                    or "images",
                    custom_domain=self.fields["custom_domain"].text().strip() or None,
                )
            elif provider == "cos_v5":
                from uploader.cos_adapter import CosAdapter

                return CosAdapter(
                    secret_id=self.fields["secret_id"].text().strip(),
                    secret_key=self.fields["secret_key"].text().strip(),
                    bucket=self.fields["bucket"].text().strip(),
                    region=self.fields["region"].text().strip(),
                    storage_path_prefix=self.fields["prefix"].text().strip()
                    or "images",
                    custom_domain=self.fields["custom_domain"].text().strip() or None,
                    use_https=self.fields["use_https"].isChecked(),
                )
            elif provider == "qiniu":
                from uploader.qiniu_adapter import QiniuAdapter

                return QiniuAdapter(
                    access_key=self.fields["access_id"].text().strip(),
                    secret_key=self.fields["access_secret"].text().strip(),
                    bucket=self.fields["bucket"].text().strip(),
                    domain=self.fields["domain"].text().strip(),
                    storage_path_prefix=self.fields["prefix"].text().strip()
                    or "images",
                    use_https=self.fields["use_https"].isChecked(),
                )
            elif provider == "s3":
                from uploader.s3_adapter import S3Adapter

                return S3Adapter(
                    access_key=self.fields["access_id"].text().strip(),
                    secret_key=self.fields["access_secret"].text().strip(),
                    bucket=self.fields["bucket"].text().strip(),
                    region=self.fields["region"].text().strip() or None,
                    endpoint=self.fields["endpoint"].text().strip() or None,
                    storage_path_prefix=self.fields["prefix"].text().strip()
                    or "images",
                    custom_domain=self.fields["custom_domain"].text().strip() or None,
                    use_https=self.fields["use_https"].isChecked(),
                    path_style=self.fields["path_style"].isChecked(),
                )
            elif provider == "github":
                from uploader.github_adapter import GitHubAdapter

                return GitHubAdapter(
                    token=self.fields["token"].text().strip(),
                    owner=self.fields["owner"].text().strip(),
                    repo=self.fields["repo"].text().strip(),
                    branch=self.fields["branch"].text().strip() or "main",
                    path_prefix=self.fields["path_prefix"].text().strip(),
                    storage_path_prefix=self.fields["prefix"].text().strip()
                    or "images",
                    custom_domain=self.fields["custom_domain"].text().strip() or None,
                    use_jsdelivr=self.fields["use_jsdelivr"].isChecked(),
                )
        except ImportError as e:
            QMessageBox.warning(self, "缺少依赖", f"无法导入{provider}适配器：{e}")
            return None
        except Exception as e:
            QMessageBox.warning(self, "配置错误", f"创建适配器失败：{e}")
            return None

    def on_clear(self):
        """清空当前已保存的图床配置（imgbed 分组）并清空表单。"""
        settings = QSettings("MdImgConverter", "Settings")
        try:
            settings.beginGroup("imgbed")
            settings.remove("")  # 清空整个分组
            settings.endGroup()
        except Exception:
            try:
                settings.remove("imgbed")
            except Exception:
                pass
        try:
            settings.sync()
        except Exception:
            pass
        # 清空表单
        try:
            self.field_endpoint.clear()
            self.field_bucket.clear()
            self.field_access_id.clear()
            self.field_access_secret.clear()
        except Exception:
            pass
        self.status_chip.setText("已清空")

    def on_convert_clicked(self):
        """转换按钮点击事件（合并流程：先转换后上传）"""
        self._combined_flow = True
        self.status_label.setText("正在转换...")
        self.real_conversion()

    def on_start_clicked(self):
        """顶部"开始"合并流程：先转换，后上传（静默），再一次性弹窗"""
        self._combined_flow = True
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
        # no debug popups or prints

        if not markdown_text:
            QMessageBox.information(self, "提示", "请先输入Markdown内容")
            self.status_label.setText("就绪")
            return

        # UI 侧先行快速校验是否含有图片链接，避免无感卡住
        try:
            import re as _re

            _pattern = (
                r'(?:!\[.*?\]\s*\((.*?)\))|(?:<img.*?src=["\']([^"\']*)["\'].*?>)'
            )
            _matches = _re.findall(_pattern, markdown_text)
            _urls = []
            for _m in _matches:
                _u = _m[0] or _m[1]
                if _u and _u.strip():
                    _urls.append(_u.strip())
            # no debug prints
            if not _urls:
                self.control_panel.convert_btn.setEnabled(True)
                self.control_panel.convert_btn.setText("转换")
                self.control_panel.set_progress(0)
                self.status_label.setText("未找到图片链接")
                QMessageBox.information(
                    self,
                    "未找到图片",
                    '未检测到 Markdown 中的图片链接，请确认语法：\n\n![](http://...) 或 <img src="...">',
                )
                return
        except Exception:
            pass

        # 获取当前文件目录，如果没有文件则使用当前目录
        if hasattr(self, "current_file") and self.current_file:
            base_dir = os.path.dirname(self.current_file)
        else:
            base_dir = os.getcwd()

        # 创建images目录
        output_dir = os.path.join(base_dir, "images")
        # no debug prints

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
            if (
                hasattr(self, "conversion_watchdog")
                and self.conversion_watchdog is not None
            ):
                self.conversion_watchdog.stop()
        except Exception:
            pass
        # 暂时禁用超时功能，避免误报
        # self.conversion_watchdog = QTimer(self)
        # self.conversion_watchdog.setSingleShot(True)
        # self.conversion_watchdog.timeout.connect(self.on_conversion_timeout)
        # self.conversion_watchdog.start(120000)  # 45s 超时提示

    def on_conversion_progress(self, progress, message):
        """转换进度更新"""
        self.control_panel.set_progress(progress)
        self.status_label.setText(message)
        try:
            print(f"[GUI] progress: {progress}%  {message}", flush=True)
        except Exception:
            pass
        # 超时功能已禁用，避免误报
        # try:
        #     if hasattr(self, 'conversion_watchdog') and self.conversion_watchdog is not None and progress < 100:
        #         self.conversion_watchdog.start(120000)
        # except Exception:
        #     pass

    def on_conversion_finished(self, new_markdown, count, stats):
        """转换完成"""
        # 立即停止超时定时器
        try:
            if (
                hasattr(self, "conversion_watchdog")
                and self.conversion_watchdog is not None
            ):
                self.conversion_watchdog.stop()
                print("[GUI] conversion watchdog stopped on finish", flush=True)
        except Exception as e:
            print(f"[GUI] error stopping watchdog: {e}", flush=True)
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

        # 不再自动上传，改为显式"上传"按钮触发

        # 格式化统计信息用于显示
        from .utils import format_size_human as format_size

        original_size = stats.get("total_original_size", 0)
        saved_size = stats.get("size_saved", 0)
        compression_ratio = stats.get("compression_ratio", 0)

        # 记录统计供合并流程使用
        self._last_convert_count = count
        self._last_convert_stats = stats

        # 合并流程：不在此处弹窗，改为静默上传后统一提示
        if self._combined_flow:
            try:
                # 状态栏提示
                self.status_label.setText("转换完成，准备上传...")
                # 让事件循环先返回，避免与收尾UI更新竞争
                QTimer.singleShot(0, lambda: self.start_upload(silent=False))
            except Exception:
                pass
        else:
            # 非合并流程：保持原有弹窗
            if count <= 0 and stats.get("total_original_size", 0) == 0:
                QMessageBox.information(
                    self,
                    "未找到图片",
                    '未检测到 Markdown 中的图片链接，请确认语法：\n\n![](http://...) 或 <img src="...">',
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
            if (
                hasattr(self, "conversion_watchdog")
                and self.conversion_watchdog is not None
            ):
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
            print("[GUI] conversion timeout triggered", flush=True)
            # 检查转换是否实际上已经完成了
            if (
                hasattr(self, "conversion_thread")
                and self.conversion_thread is not None
            ):
                if not self.conversion_thread.isRunning():
                    print(
                        "[GUI] timeout but thread already finished, ignoring",
                        flush=True,
                    )
                    return

            self.control_panel.convert_btn.setEnabled(True)
            self.control_panel.convert_btn.setText("转换")
            self.status_label.setText("转换超时，请检查网络或图片链接")
            QMessageBox.warning(
                self,
                "转换超时",
                "转换耗时过长，可能网络较慢或图片地址不可达。稍后重试，或检查图片 URL。",
            )
        except Exception as e:
            print(f"[GUI] error in timeout handler: {e}", flush=True)


# 兼容性修复：将下方（意外置于类外的）方法绑定回 Win11MainWindow
try:
    if (
        not hasattr(Win11MainWindow, "real_conversion")
        and "real_conversion" in globals()
    ):
        Win11MainWindow.real_conversion = globals()["real_conversion"]
    if (
        not hasattr(Win11MainWindow, "on_conversion_progress")
        and "on_conversion_progress" in globals()
    ):
        Win11MainWindow.on_conversion_progress = globals()["on_conversion_progress"]
    if (
        not hasattr(Win11MainWindow, "on_conversion_finished")
        and "on_conversion_finished" in globals()
    ):
        Win11MainWindow.on_conversion_finished = globals()["on_conversion_finished"]
    if (
        not hasattr(Win11MainWindow, "on_conversion_error")
        and "on_conversion_error" in globals()
    ):
        Win11MainWindow.on_conversion_error = globals()["on_conversion_error"]
    if (
        not hasattr(Win11MainWindow, "on_conversion_timeout")
        and "on_conversion_timeout" in globals()
    ):
        Win11MainWindow.on_conversion_timeout = globals()["on_conversion_timeout"]
    if (
        not hasattr(Win11MainWindow, "_replace_local_paths_with_remote")
        and "_replace_local_paths_with_remote" in globals()
    ):
        Win11MainWindow._replace_local_paths_with_remote = globals()[
            "_replace_local_paths_with_remote"
        ]
except Exception:
    pass

    def _replace_local_paths_with_remote(
        self, md: str, base_dir: str, mapping: dict
    ) -> str:
        """将 Markdown 中 ./images 或 images 的相对路径替换为远程 URL"""

        def rel(p: str) -> str:
            # 生成两种相对形式：images/name.webp 与 ./images/name.webp
            img_dir = os.path.join(base_dir, "images")
            rp = os.path.relpath(p, base_dir).replace("\\", "/")
            rp2 = "./" + rp if not rp.startswith("./") else rp
            return rp, rp2

        for lp, url in mapping.items():
            r1, r2 = rel(lp)
            # 粗略替换两种可能形式
            md = md.replace(r1, url).replace(r2, url)
        return md
