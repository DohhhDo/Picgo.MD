#!/usr/bin/env python3
# -*- coding: utf-8 -*-

from __future__ import annotations

import os
from typing import Dict, List, Tuple

from PyQt6.QtCore import QSettings

from .ali_oss_adapter import AliOssAdapter


class UploadManager:
    """最小实现：仅支持阿里云 OSS，把本地 webp 批量上传并返回映射"""

    def __init__(self) -> None:
        self.settings = QSettings("MdImgConverter", "Settings")

    def _load_aliyun_config(self) -> Dict[str, str]:
        cfg = {
            "access_key_id": self.settings.value("imgbed/aliyun/accessKeyId", ""),
            "access_key_secret": self.settings.value("imgbed/aliyun/accessKeySecret", ""),
            "bucket_name": self.settings.value("imgbed/aliyun/bucket", ""),
            "endpoint": self.settings.value("imgbed/aliyun/endpoint", ""),
            "storage_path_prefix": self.settings.value("imgbed/aliyun/prefix", "images"),
            "custom_domain": self.settings.value("imgbed/aliyun/customDomain", ""),
        }
        try:
            print(f"[UploadManager] cfg loaded: provider={self.settings.value('imgbed/provider','')} enabled={self.settings.value('imgbed/enabled', True, type=bool)}", flush=True)
        except Exception:
            pass
        return cfg

    def upload_webps(self, local_paths: List[str]) -> Dict[str, str]:
        """上传本地 webp 文件，返回 {local_path: remote_url}"""
        provider = self.settings.value("imgbed/provider", "")
        enabled = self.settings.value("imgbed/enabled", True, type=bool)
        cfg = self._load_aliyun_config()
        # 容错：未设置 provider 或开关，但已配置阿里云字段时仍允许上传
        allow_aliyun = (
            provider == "aliyun_oss" or
            all(cfg.get(k) for k in ["access_key_id", "access_key_secret", "bucket_name", "endpoint"])  # 基本配置齐全
        ) and enabled
        if not allow_aliyun:
            return {}

        adapter = AliOssAdapter(**cfg)
        mapping: Dict[str, str] = {}
        for p in local_paths:
            fn = os.path.basename(p)
            remote = adapter.upload_file(p, fn)
            mapping[p] = remote
        return mapping

    # 供后台线程逐个上传并汇报进度
    def get_adapter_if_enabled(self):
        provider = self.settings.value("imgbed/provider", "")
        enabled = self.settings.value("imgbed/enabled", True, type=bool)
        cfg = self._load_aliyun_config()
        # 容错：provider 未写入但已配置阿里云字段时仍返回适配器
        if enabled and (
            provider == "aliyun_oss" or
            all(cfg.get(k) for k in ["access_key_id", "access_key_secret", "bucket_name", "endpoint"])
        ):
            return AliOssAdapter(**cfg)
        return None

    # 供“手动上传”按钮使用：忽略是否启用开关，只要配置存在即可返回适配器
    def get_adapter(self):
        provider = self.settings.value("imgbed/provider", "")
        if provider == "aliyun_oss":
            cfg = self._load_aliyun_config()
            return AliOssAdapter(**cfg)
        return None




