from PyQt6.QtWidgets import (
    QDialog, QVBoxLayout, QHBoxLayout, QLabel, QComboBox, QTabWidget,
    QWidget, QLineEdit, QScrollArea, QDialogButtonBox, QPushButton,
    QMessageBox, QCheckBox
)
from PyQt6.QtCore import QSettings


class ImageBedDialog(QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("图床设置")
        self.setModal(False)
        self.setMinimumSize(560, 420)
        self._build_ui()

    def _build_ui(self):
        root = QVBoxLayout(self)
        top = QHBoxLayout()
        top.addWidget(QLabel("图床："))
        self.provider_combo = QComboBox(); self.provider_combo.addItems([
            "七牛 v1.0","腾讯云 COS v4 v1.1","腾讯云 COS v5 v1.5.0",
            "又拍云 v1.2.0","GitHub v1.5.0","SM.MS V2 v2.3.0-beta.0",
            "阿里云 OSS v1.6.0","Imgur v1.6.0",
        ])
        top.addWidget(self.provider_combo); top.addStretch();
        self.status_chip = QLabel("未测试"); top.addWidget(self.status_chip)
        root.addLayout(top)

        self.tabs = QTabWidget(self)
        self.tab_status = QWidget(); self.tab_config = QWidget(); self.tab_advanced = QWidget()
        self.tabs.addTab(self.tab_status, "选择与状态")
        self.tabs.addTab(self.tab_config, "凭据与配置")
        self.tabs.addTab(self.tab_advanced, "高级与策略")
        root.addWidget(self.tabs)

        st = QVBoxLayout(self.tab_status)
        st.addWidget(QLabel("说明：选择图床后，可在下方“保存”并稍后进行上传测试。"))
        st.addStretch()

        scroll = QScrollArea(self.tab_config); scroll.setWidgetResizable(True)
        host = QWidget(); form = QVBoxLayout(host)
        self.field_endpoint = QLineEdit(); self.field_bucket = QLineEdit()
        self.field_access_id = QLineEdit(); self.field_access_secret = QLineEdit(); self.field_access_secret.setEchoMode(QLineEdit.EchoMode.Password)
        form.addWidget(QLabel("地域前缀(如 oss-cn-beijing)")); form.addWidget(self.field_endpoint)
        form.addWidget(QLabel("Bucket/仓库")); form.addWidget(self.field_bucket)
        form.addWidget(QLabel("AccessKey/Token")); form.addWidget(self.field_access_id)
        form.addWidget(QLabel("Secret")); form.addWidget(self.field_access_secret)
        form.addStretch(); scroll.setWidget(host)
        cfg = QVBoxLayout(self.tab_config); cfg.addWidget(scroll)

        adv = QVBoxLayout(self.tab_advanced)
        self.chk_enable_upload = QCheckBox("启用转换后自动上传"); adv.addWidget(self.chk_enable_upload); adv.addStretch()

        btns = QDialogButtonBox(QDialogButtonBox.StandardButton.Save | QDialogButtonBox.StandardButton.Close)
        self.test_btn = QPushButton("测试上传"); btns.addButton(self.test_btn, QDialogButtonBox.ButtonRole.ActionRole)
        btns.accepted.connect(self.on_save); btns.rejected.connect(self.reject)
        root.addWidget(btns)

    def apply_theme(self, dark: bool):
        if dark:
            self.setStyleSheet("QDialog{background:#0F141A;color:#E6EAF0;}")
        else:
            self.setStyleSheet("QDialog{background:#FFFFFF;color:#0F172A;}")

    def _provider_key(self) -> str:
        text = self.provider_combo.currentText()
        if "阿里云" in text or "OSS" in text:
            return "aliyun_oss"
        if "七牛" in text: return "qiniu"
        if "腾讯云" in text and "v4" in text: return "cos_v4"
        if "腾讯云" in text and "v5" in text: return "cos_v5"
        if "又拍云" in text: return "upyun"
        if "GitHub" in text: return "github"
        if "SM.MS" in text: return "smms"
        if "Imgur" in text: return "imgur"
        return ""

    def _normalize_aliyun_endpoint(self, region_prefix: str) -> str:
        rp = region_prefix.strip()
        if rp.startswith("http://") or rp.startswith("https://"):
            return rp
        return f"https://{rp}.aliyuncs.com"

    def on_save(self):
        settings = QSettings("MdImgConverter", "Settings")
        prov = self._provider_key()
        settings.setValue("imgbed/provider", prov)
        enabled = bool(self.chk_enable_upload.isChecked()) if hasattr(self, 'chk_enable_upload') else False
        settings.setValue("imgbed/enabled", enabled)
        if prov == "aliyun_oss":
            endpoint = self._normalize_aliyun_endpoint(self.field_endpoint.text())
            settings.setValue("imgbed/aliyun/endpoint", endpoint)
            settings.setValue("imgbed/aliyun/bucket", self.field_bucket.text().strip())
            settings.setValue("imgbed/aliyun/accessKeyId", self.field_access_id.text().strip())
            settings.setValue("imgbed/aliyun/accessKeySecret", self.field_access_secret.text().strip())
            if settings.value("imgbed/aliyun/prefix", "") in (None, ""):
                settings.setValue("imgbed/aliyun/prefix", "images")
        self.accept()


