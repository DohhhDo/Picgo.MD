#!/usr/bin/env python3
# -*- coding: utf-8 -*-

from __future__ import annotations

import os
from typing import Optional

try:
    from qiniu import Auth, put_data
except ImportError:
    Auth = None
    put_data = None


class QiniuAdapter:
    """七牛云 Kodo 上传适配器（GUI版本）"""

    def __init__(
        self,
        access_key: str,
        secret_key: str,
        bucket: str,
        domain: str,
        storage_path_prefix: str = "",
        use_https: bool = True,
    ) -> None:
        if Auth is None or put_data is None:
            raise ImportError("缺少依赖：pip install qiniu")
            
        self.access_key = access_key
        self.secret_key = secret_key
        self.bucket = bucket
        self.domain = domain.strip("/")
        self.storage_path_prefix = storage_path_prefix.strip("/")
        self.use_https = use_https

        self.auth = Auth(self.access_key, self.secret_key)

    def _join_key(self, key: str) -> str:
        key = key.lstrip("/")
        if self.storage_path_prefix:
            return f"{self.storage_path_prefix}/{key}"
        return key

    def upload_file(self, local_path: str, key: str) -> str:
        """上传本地文件，返回可访问 URL"""
        final_key = self._join_key(key)
        token = self.auth.upload_token(self.bucket, final_key)
        
        with open(local_path, "rb") as f:
            ret, info = put_data(token, final_key, f.read())
            
        if info.status_code != 200:
            raise Exception(f"Upload failed with status {info.status_code}: {info.text_body}")
            
        return self._build_url(final_key)

    def upload_bytes(self, data: bytes, key: str) -> str:
        final_key = self._join_key(key)
        token = self.auth.upload_token(self.bucket, final_key)
        
        ret, info = put_data(token, final_key, data)
        
        if info.status_code != 200:
            raise Exception(f"Upload failed with status {info.status_code}: {info.text_body}")
            
        return self._build_url(final_key)

    def _build_url(self, key: str) -> str:
        protocol = "https" if self.use_https else "http"
        return f"{protocol}://{self.domain}/{key}"
