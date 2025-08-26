from PyQt6.QtGui import QFont
from PyQt6.QtWidgets import QTextEdit


class Win11MarkdownEditor(QTextEdit):
    def __init__(self):
        super().__init__()
        self.setup_ui()

    def setup_ui(self):
        font = QFont("Segoe UI", 11)
        self.setFont(font)
        self.is_dark_theme = self.detect_system_theme()
        self.apply_theme_style()
        self.setPlaceholderText("在此编辑Markdown内容...")

    def detect_system_theme(self):
        try:
            import winreg

            registry = winreg.ConnectRegistry(None, winreg.HKEY_CURRENT_USER)
            key = winreg.OpenKey(
                registry,
                r"SOFTWARE\\Microsoft\\Windows\\CurrentVersion\\Themes\\Personalize",
            )
            value, _ = winreg.QueryValueEx(key, "AppsUseLightTheme")
            winreg.CloseKey(key)
            return value == 0
        except Exception:
            return False

    def apply_theme_style(self):
        if self.is_dark_theme:
            self.setStyleSheet(
                """
                QTextEdit { background-color: #1e1e1e; color: #ffffff; border: none; border-radius: 4px; padding: 12px; line-height: 1.4; selection-background-color: #0078d4; selection-color: #ffffff; font-family: 'Segoe UI'; }
                QScrollBar:vertical { background: transparent; width: 12px; border: none; }
                QScrollBar::handle:vertical { background: #606060; border-radius: 6px; min-height: 20px; margin: 2px; }
                QScrollBar::handle:vertical:hover { background: #808080; }
                QScrollBar::add-line:vertical, QScrollBar::sub-line:vertical { border: none; background: none; }
                """
            )
        else:
            self.setStyleSheet(
                """
                QTextEdit { background-color: #ffffff; color: #000000; border: none; border-radius: 4px; padding: 12px; line-height: 1.4; selection-background-color: #0078d4; selection-color: #ffffff; font-family: 'Segoe UI'; }
                QScrollBar:vertical { background: transparent; width: 12px; border: none; }
                QScrollBar::handle:vertical { background: #606060; border-radius: 6px; min-height: 20px; margin: 2px; }
                QScrollBar::handle:vertical:hover { background: #808080; }
                QScrollBar::add-line:vertical, QScrollBar::sub-line:vertical { border: none; background: none; }
                """
            )
