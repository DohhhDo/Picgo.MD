#!/usr/bin/env python3
# -*- coding: utf-8 -*-

from __future__ import annotations

import os
from typing import Dict, List, Tuple

from PyQt6.QtCore import QSettings

from .ali_oss_adapter import AliOssAdapter
from .cos_adapter import CosAdapter
from .github_adapter import GitHubAdapter
from .qiniu_adapter import QiniuAdapter
from .s3_adapter import S3Adapter


class UploadManager:
    """支持多种图床的上传管理器"""

    def __init__(self) -> None:
        self.settings = QSettings("MdImgConverter", "Settings")

    def _load_aliyun_config(self) -> Dict[str, str]:
        cfg = {
            "access_key_id": self.settings.value("imgbed/aliyun/accessKeyId", ""),
            "access_key_secret": self.settings.value(
                "imgbed/aliyun/accessKeySecret", ""
            ),
            "bucket_name": self.settings.value("imgbed/aliyun/bucket", ""),
            "endpoint": self.settings.value("imgbed/aliyun/endpoint", ""),
            "storage_path_prefix": self.settings.value(
                "imgbed/aliyun/prefix", "images"
            ),
            "custom_domain": self.settings.value("imgbed/aliyun/customDomain", ""),
        }
        try:
            print(
                f"[UploadManager] cfg loaded: provider={self.settings.value('imgbed/provider','')} enabled={self.settings.value('imgbed/enabled', True, type=bool)}",
                flush=True,
            )
        except Exception:
            pass
        return cfg

    def _load_cos_config(self) -> Dict[str, str]:
        return {
            "secret_id": self.settings.value("imgbed/cos/secretId", ""),
            "secret_key": self.settings.value("imgbed/cos/secretKey", ""),
            "bucket": self.settings.value("imgbed/cos/bucket", ""),
            "region": self.settings.value("imgbed/cos/region", ""),
            "storage_path_prefix": self.settings.value("imgbed/cos/prefix", "images"),
            "custom_domain": self.settings.value("imgbed/cos/customDomain", ""),
            "use_https": self.settings.value("imgbed/cos/useHttps", True, type=bool),
        }

    def _load_qiniu_config(self) -> Dict[str, str]:
        return {
            "access_key": self.settings.value("imgbed/qiniu/accessKey", ""),
            "secret_key": self.settings.value("imgbed/qiniu/secretKey", ""),
            "bucket": self.settings.value("imgbed/qiniu/bucket", ""),
            "domain": self.settings.value("imgbed/qiniu/domain", ""),
            "storage_path_prefix": self.settings.value("imgbed/qiniu/prefix", "images"),
            "use_https": self.settings.value("imgbed/qiniu/useHttps", True, type=bool),
        }

    def _load_s3_config(self) -> Dict[str, str]:
        return {
            "access_key": self.settings.value("imgbed/s3/accessKey", ""),
            "secret_key": self.settings.value("imgbed/s3/secretKey", ""),
            "bucket": self.settings.value("imgbed/s3/bucket", ""),
            "region": self.settings.value("imgbed/s3/region", ""),
            "endpoint": self.settings.value("imgbed/s3/endpoint", ""),
            "storage_path_prefix": self.settings.value("imgbed/s3/prefix", "images"),
            "custom_domain": self.settings.value("imgbed/s3/customDomain", ""),
            "use_https": self.settings.value("imgbed/s3/useHttps", True, type=bool),
            "path_style": self.settings.value("imgbed/s3/pathStyle", False, type=bool),
        }

    def _load_github_config(self) -> Dict[str, str]:
        return {
            "token": self.settings.value("imgbed/github/token", ""),
            "owner": self.settings.value("imgbed/github/owner", ""),
            "repo": self.settings.value("imgbed/github/repo", ""),
            "branch": self.settings.value("imgbed/github/branch", "main"),
            "path_prefix": self.settings.value("imgbed/github/pathPrefix", ""),
            "storage_path_prefix": self.settings.value(
                "imgbed/github/prefix", "images"
            ),
            "custom_domain": self.settings.value("imgbed/github/customDomain", ""),
            "use_jsdelivr": self.settings.value(
                "imgbed/github/useJsdelivr", False, type=bool
            ),
        }

    def upload_webps(self, local_paths: List[str]) -> Dict[str, str]:
        """上传本地 webp 文件，返回 {local_path: remote_url}"""
        provider = self.settings.value("imgbed/provider", "")
        enabled = self.settings.value("imgbed/enabled", True, type=bool)

        if not enabled:
            return {}

        adapter = self._get_adapter_by_provider(provider)
        if not adapter:
            return {}

        mapping: Dict[str, str] = {}
        for p in local_paths:
            try:
                fn = os.path.basename(p)
                remote = adapter.upload_file(p, fn)
                mapping[p] = remote
            except Exception as e:
                print(f"[UploadManager] Upload failed for {p}: {e}")
                # 继续处理其他文件
                continue
        return mapping

    def _get_adapter_by_provider(self, provider: str):
        """根据provider类型创建对应的适配器"""
        try:
            if provider == "aliyun_oss":
                cfg = self._load_aliyun_config()
                if all(
                    cfg.get(k)
                    for k in [
                        "access_key_id",
                        "access_key_secret",
                        "bucket_name",
                        "endpoint",
                    ]
                ):
                    return AliOssAdapter(**cfg)
            elif provider == "cos_v5":
                cfg = self._load_cos_config()
                if all(
                    cfg.get(k) for k in ["secret_id", "secret_key", "bucket", "region"]
                ):
                    return CosAdapter(**cfg)
            elif provider == "qiniu":
                cfg = self._load_qiniu_config()
                if all(
                    cfg.get(k) for k in ["access_key", "secret_key", "bucket", "domain"]
                ):
                    return QiniuAdapter(**cfg)
            elif provider == "s3":
                cfg = self._load_s3_config()
                if all(cfg.get(k) for k in ["access_key", "secret_key", "bucket"]):
                    return S3Adapter(**cfg)
            elif provider == "github":
                cfg = self._load_github_config()
                if all(cfg.get(k) for k in ["token", "owner", "repo"]):
                    return GitHubAdapter(**cfg)
        except Exception as e:
            print(f"[UploadManager] Failed to create adapter for {provider}: {e}")
        return None

    # 供后台线程逐个上传并汇报进度
    def get_adapter_if_enabled(self):
        provider = self.settings.value("imgbed/provider", "")
        enabled = self.settings.value("imgbed/enabled", True, type=bool)

        if not enabled:
            return None

        return self._get_adapter_by_provider(provider)

    # 供"手动上传"按钮使用：忽略是否启用开关，只要配置存在即可返回适配器
    def get_adapter(self):
        provider = self.settings.value("imgbed/provider", "")
        return self._get_adapter_by_provider(provider)
