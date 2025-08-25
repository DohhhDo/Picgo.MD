from PyQt6.QtCore import QThread, pyqtSignal, QSettings
import os

try:
    from uploader.manager import UploadManager
except Exception:
    UploadManager = None

try:
    from core.image_converter import convert_markdown_images
except Exception:
    convert_markdown_images = None


class ConversionWorker(QThread):
    """图片转换工作线程"""
    progress_updated = pyqtSignal(int, str)
    conversion_finished = pyqtSignal(str, int, dict)  # new_md, count, stats
    conversion_error = pyqtSignal(str)

    def __init__(self, markdown_text: str, output_dir: str, quality: int):
        super().__init__()
        self.markdown_text = markdown_text
        self.output_dir = output_dir
        self.quality = quality

    def run(self):
        try:
            if convert_markdown_images is None:
                self.conversion_error.emit("图片转换模块未找到")
                return

            def progress_callback(progress: int, message: str):
                self.progress_updated.emit(progress, message)

            new_markdown, count, stats = convert_markdown_images(
                self.markdown_text,
                self.output_dir,
                self.quality,
                progress_callback,
            )
            self.conversion_finished.emit(new_markdown, count, stats)
        except Exception as e:
            self.conversion_error.emit(f"转换失败: {e}")


class UploadWorker(QThread):
    """后台上传线程：逐图上传并回写"""
    progress_updated = pyqtSignal(int, str)
    finished_with_mapping = pyqtSignal(dict)
    error = pyqtSignal(str)

    def __init__(self, base_dir: str, local_webps: list):
        super().__init__()
        self.base_dir = base_dir
        self.local_webps = local_webps

    def run(self):
        try:
            if UploadManager is None or not self.local_webps:
                try:
                    print("[Worker] UploadManager missing or no files", flush=True)
                except Exception:
                    pass
                self.finished_with_mapping.emit({})
                return
            um = UploadManager()
            adapter = um.get_adapter_if_enabled()
            # 回退：若未显式启用但已配置图床，则也允许上传
            if adapter is None:
                try:
                    adapter = um.get_adapter()
                except Exception:
                    adapter = None
            if adapter is None:
                try:
                    print("[Worker] No adapter available", flush=True)
                except Exception:
                    pass
                self.finished_with_mapping.emit({})
                return
            mapping = {}
            total = len(self.local_webps)
            for i, p in enumerate(self.local_webps, 1):
                try:
                    fn = os.path.basename(p)
                    url = adapter.upload_file(p, fn)
                    mapping[p] = url
                    self.progress_updated.emit(int(i / total * 100), f"上传 {i}/{total}：{fn}")
                except Exception:
                    try:
                        print(f"[Worker] upload failed for {p}", flush=True)
                    except Exception:
                        pass
                    self.progress_updated.emit(int(i / total * 100), f"上传失败 {i}/{total}：{os.path.basename(p)}")
                    continue
            self.finished_with_mapping.emit(mapping)
        except Exception as e:
            self.error.emit(str(e))


