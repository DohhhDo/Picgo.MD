#!/usr/bin/env python3
# -*- coding: utf-8 -*-

from __future__ import annotations

import os
from typing import Optional

try:
    from qcloud_cos import CosConfig, CosS3Client
except ImportError:
    CosConfig = None
    CosS3Client = None


class CosAdapter:
    """腾讯云 COS 上传适配器（GUI版本）"""

    def __init__(
        self,
        secret_id: str,
        secret_key: str,
        bucket: str,
        region: str,
        storage_path_prefix: str = "",
        custom_domain: Optional[str] = None,
        use_https: bool = True,
    ) -> None:
        if CosConfig is None or CosS3Client is None:
            raise ImportError("缺少依赖：pip install cos-python-sdk-v5")

        self.secret_id = secret_id
        self.secret_key = secret_key
        self.bucket = bucket
        self.region = region
        self.storage_path_prefix = storage_path_prefix.strip("/")
        self.custom_domain = custom_domain.rstrip("/") if custom_domain else None
        self.use_https = use_https

        scheme = "https" if use_https else "http"
        config = CosConfig(
            Region=self.region,
            SecretId=self.secret_id,
            SecretKey=self.secret_key,
            Scheme=scheme,
        )
        self.client = CosS3Client(config)

    def _join_key(self, key: str) -> str:
        key = key.lstrip("/")
        if self.storage_path_prefix:
            return f"{self.storage_path_prefix}/{key}"
        return key

    def upload_file(self, local_path: str, key: str) -> str:
        """上传本地文件，返回可访问 URL"""
        final_key = self._join_key(key)
        with open(local_path, "rb") as f:
            self.client.put_object(Bucket=self.bucket, Key=final_key, Body=f)
        return self._build_url(final_key)

    def upload_bytes(self, data: bytes, key: str) -> str:
        final_key = self._join_key(key)
        self.client.put_object(Bucket=self.bucket, Key=final_key, Body=data)
        return self._build_url(final_key)

    def _build_url(self, key: str) -> str:
        if self.custom_domain:
            return f"{self.custom_domain}/{key}"

        protocol = "https" if self.use_https else "http"
        return f"{protocol}://{self.bucket}.cos.{self.region}.myqcloud.com/{key}"
