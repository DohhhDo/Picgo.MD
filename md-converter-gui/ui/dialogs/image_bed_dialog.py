from PyQt6.QtCore import QSettings
from PyQt6.QtWidgets import (
    QCheckBox,
    QComboBox,
    QDialog,
    QDialogButtonBox,
    QHBoxLayout,
    QLabel,
    QLineEdit,
    QMessageBox,
    QPushButton,
    QScrollArea,
    QTabWidget,
    QVBoxLayout,
    QWidget,
)


class ImageBedDialog(QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("图床设置")
        self.setModal(False)
        self.setMinimumSize(560, 420)
        self._build_ui()
        # 初始预填设置
        try:
            self.load_from_settings()
        except Exception:
            pass

    def _build_ui(self):
        root = QVBoxLayout(self)
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
        top.addWidget(self.status_chip)
        root.addLayout(top)

        self.tabs = QTabWidget(self)
        self.tab_status = QWidget()
        self.tab_config = QWidget()
        self.tabs.addTab(self.tab_status, "选择与状态")
        self.tabs.addTab(self.tab_config, "凭据与配置")
        root.addWidget(self.tabs)

        st = QVBoxLayout(self.tab_status)
        st.addWidget(QLabel("说明：选择图床后，可在下方“保存”并稍后进行上传测试。"))
        st.addStretch()

        scroll = QScrollArea(self.tab_config)
        scroll.setWidgetResizable(True)
        host = QWidget()
        form = QVBoxLayout(host)
        self.field_endpoint = QLineEdit()
        self.field_bucket = QLineEdit()
        self.field_access_id = QLineEdit()
        self.field_access_secret = QLineEdit()
        self.field_access_secret.setEchoMode(QLineEdit.EchoMode.Password)
        form.addWidget(QLabel("地域前缀(如 oss-cn-beijing)"))
        form.addWidget(self.field_endpoint)
        form.addWidget(QLabel("Bucket/仓库"))
        form.addWidget(self.field_bucket)
        form.addWidget(QLabel("AccessKey/Token"))
        form.addWidget(self.field_access_id)
        form.addWidget(QLabel("Secret"))
        form.addWidget(self.field_access_secret)
        form.addStretch()
        scroll.setWidget(host)
        cfg = QVBoxLayout(self.tab_config)
        cfg.addWidget(scroll)

        # 移除“高级与策略”页与自动上传开关，默认启用

        btns = QDialogButtonBox(
            QDialogButtonBox.StandardButton.Save | QDialogButtonBox.StandardButton.Close
        )
        self.test_btn = QPushButton("测试上传")
        btns.addButton(self.test_btn, QDialogButtonBox.ButtonRole.ActionRole)
        self.clear_btn = QPushButton("清空")
        btns.addButton(self.clear_btn, QDialogButtonBox.ButtonRole.ActionRole)
        btns.accepted.connect(self.on_save)
        btns.rejected.connect(self.reject)
        self.clear_btn.clicked.connect(self.on_clear)
        root.addWidget(btns)

    def apply_theme(self, dark: bool):
        # 弹窗固定深色主题
        self.setStyleSheet("QDialog{background:#0F141A;color:#E6EAF0;}")

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
        if rp == "":
            return ""
        # 支持 @ 前缀：按原样使用
        if rp.startswith("@"):
            rp = rp[1:].strip()
        # 已包含协议
        if rp.startswith("http://") or rp.startswith("https://"):
            return rp
        # 包含域名但无协议
        if "aliyuncs.com" in rp:
            return f"https://{rp}"
        # 仅地域前缀
        return f"https://{rp}.aliyuncs.com"

    def load_from_settings(self):
        """从 QSettings 读取并预填表单。"""
        settings = QSettings("MdImgConverter", "Settings")
        prov = settings.value("imgbed/provider", "aliyun_oss") or "aliyun_oss"
        text_map = {
            "aliyun_oss": "阿里云 OSS",
            "qiniu": "七牛",
            "cos_v4": "腾讯云 COS v4",
            "cos_v5": "腾讯云 COS v5",
            "upyun": "又拍云",
            "github": "GitHub",
            "smms": "SM.MS",
            "imgur": "Imgur",
        }
        target = text_map.get(prov, "阿里云 OSS")
        for i in range(self.provider_combo.count()):
            if target in self.provider_combo.itemText(i):
                self.provider_combo.setCurrentIndex(i)
                break
        # 预填阿里云字段
        self.field_endpoint.setText(
            str(settings.value("imgbed/aliyun/endpoint", "")) or ""
        )
        self.field_bucket.setText(str(settings.value("imgbed/aliyun/bucket", "")) or "")
        self.field_access_id.setText(
            str(settings.value("imgbed/aliyun/accessKeyId", "")) or ""
        )
        self.field_access_secret.setText(
            str(settings.value("imgbed/aliyun/accessKeySecret", "")) or ""
        )
        if any(
            [
                self.field_bucket.text(),
                self.field_endpoint.text(),
                self.field_access_id.text(),
            ]
        ):
            self.status_chip.setText("已加载配置")
        else:
            self.status_chip.setText("未测试")

    def on_save(self):
        settings = QSettings("MdImgConverter", "Settings")
        prov = self._provider_key()
        # 若填写了阿里云字段但未选择阿里云，自动切换为阿里云
        if prov != "aliyun_oss":
            if any(
                [
                    self.field_endpoint.text().strip(),
                    self.field_bucket.text().strip(),
                    self.field_access_id.text().strip(),
                    self.field_access_secret.text().strip(),
                ]
            ):
                prov = "aliyun_oss"
                for i in range(self.provider_combo.count()):
                    if "阿里云 OSS" in self.provider_combo.itemText(i):
                        self.provider_combo.setCurrentIndex(i)
                        break
        settings.setValue("imgbed/provider", prov)
        # 强制启用自动上传
        settings.setValue("imgbed/enabled", True)
        if prov == "aliyun_oss":
            endpoint = self._normalize_aliyun_endpoint(self.field_endpoint.text())
            settings.setValue("imgbed/aliyun/endpoint", endpoint)
            settings.setValue("imgbed/aliyun/bucket", self.field_bucket.text().strip())
            settings.setValue(
                "imgbed/aliyun/accessKeyId", self.field_access_id.text().strip()
            )
            settings.setValue(
                "imgbed/aliyun/accessKeySecret", self.field_access_secret.text().strip()
            )
            if settings.value("imgbed/aliyun/prefix", "") in (None, ""):
                settings.setValue("imgbed/aliyun/prefix", "images")
        # 立即落盘
        try:
            settings.sync()
        except Exception:
            pass
        self.accept()

    def on_clear(self):
        """清空QSettings中的 imgbed 分组，并清空表单。"""
        settings = QSettings("MdImgConverter", "Settings")
        try:
            settings.beginGroup("imgbed")
            settings.remove("")
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
        # 清空表单并状态
        try:
            self.field_endpoint.clear()
            self.field_bucket.clear()
            self.field_access_id.clear()
            self.field_access_secret.clear()
        except Exception:
            pass
        self.status_chip.setText("已清空")
