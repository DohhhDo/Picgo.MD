from PyQt6.QtWidgets import QWidget, QVBoxLayout, QLabel, QSlider, QPushButton, QGridLayout, QFrame, QHBoxLayout
from PyQt6.QtCore import Qt
from PyQt6.QtGui import QFont


class Win11ControlPanel(QWidget):
    def __init__(self):
        super().__init__()
        self.quality_value = 73
        self.progress_value = 0
        self.is_dark_theme = self.detect_system_theme()
        self.setup_ui()

    def detect_system_theme(self):
        try:
            import winreg
            registry = winreg.ConnectRegistry(None, winreg.HKEY_CURRENT_USER)
            key = winreg.OpenKey(registry, r"SOFTWARE\\Microsoft\\Windows\\CurrentVersion\\Themes\\Personalize")
            value, _ = winreg.QueryValueEx(key, "AppsUseLightTheme")
            winreg.CloseKey(key)
            return value == 0
        except Exception:
            return False

    def setup_ui(self):
        self.setFixedWidth(260)
        self.apply_panel_theme()
        main_layout = QVBoxLayout()
        main_layout.setSpacing(16)
        main_layout.setContentsMargins(20, 20, 20, 20)

        # 标题
        title = QLabel("图片质量")
        title.setStyleSheet("QLabel{font-size:14px;font-weight:700;}")
        main_layout.addWidget(title)

        # 质量滑块
        self.quality_slider = QSlider(Qt.Orientation.Horizontal)
        self.quality_slider.setRange(1, 100)
        self.quality_slider.setValue(self.quality_value)
        main_layout.addWidget(self.quality_slider)

        # 显示当前值
        self.quality_label = QLabel(f"{self.quality_value}%")
        main_layout.addWidget(self.quality_label)

        # 预设按钮（占位简单版）
        grid = QGridLayout()
        self.preset_extreme = QPushButton("极缩")
        self.preset_normal = QPushButton("常规")
        self.preset_light = QPushButton("轻压")
        self.preset_lossless = QPushButton("无损")
        grid.addWidget(self.preset_extreme, 0, 0)
        grid.addWidget(self.preset_normal, 0, 1)
        grid.addWidget(self.preset_light, 1, 0)
        grid.addWidget(self.preset_lossless, 1, 1)
        main_layout.addLayout(grid)

        # 进度条占位 + 文本
        self.progress_bg = QFrame(); self.progress_bg.setFixedHeight(8)
        self.progress_bg.setStyleSheet("QFrame{background:#e5e7eb;border-radius:4px;}")
        self.progress_fill = QFrame(); self.progress_fill.setStyleSheet("QFrame{background:#16a34a;border-radius:4px;}")
        self.progress_fill.setFixedWidth(0)
        main_layout.addWidget(self.progress_bg)
        text_row = QHBoxLayout(); self.progress_text = QLabel("准备就绪"); text_row.addWidget(self.progress_text); text_row.addStretch();
        main_layout.addLayout(text_row)

        # 转换按钮（右侧）
        self.convert_btn = QPushButton("转换")
        main_layout.addWidget(self.convert_btn)

        self.setLayout(main_layout)

    def apply_panel_theme(self):
        if self.is_dark_theme:
            self.setStyleSheet("QWidget{background:transparent;color:#e5e7eb;}")
        else:
            self.setStyleSheet("QWidget{background:transparent;color:#0f172a;}")

    def update_preset_button_states(self, value: int):
        # 简化：不改变样式，仅保留接口
        return

    def set_progress(self, value: int):
        self.progress_value = value
        total_width = max(1, self.progress_bg.width())
        self.progress_fill.setFixedWidth(int((value/100)*total_width))
        if value == 0:
            self.progress_text.setText("准备就绪")
        elif value >= 100:
            self.progress_text.setText("转换完成")
        else:
            self.progress_text.setText(f"转换中... {value}%")


