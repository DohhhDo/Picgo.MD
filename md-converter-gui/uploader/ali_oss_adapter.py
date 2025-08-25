#!/usr/bin/env python3
# -*- coding: utf-8 -*-

from __future__ import annotations

import os
from typing import Optional

import oss2


class AliOssAdapter:
    """阿里云 OSS 上传适配器（最小可用）"""

    def __init__(
        self,
        access_key_id: str,
        access_key_secret: str,
        bucket_name: str,
        endpoint: str,
        storage_path_prefix: str = "",
        custom_domain: Optional[str] = None,
    ) -> None:
        self.access_key_id = access_key_id
        self.access_key_secret = access_key_secret
        self.bucket_name = bucket_name
        self.endpoint = endpoint.rstrip("/")
        self.storage_path_prefix = storage_path_prefix.strip("/")
        self.custom_domain = custom_domain.rstrip("/") if custom_domain else None

        auth = oss2.Auth(self.access_key_id, self.access_key_secret)
        self.bucket = oss2.Bucket(auth, self.endpoint, self.bucket_name)

    def _join_key(self, key: str) -> str:
        key = key.lstrip("/")
        if self.storage_path_prefix:
            return f"{self.storage_path_prefix}/{key}"
        return key

    def upload_file(self, local_path: str, key: str) -> str:
        """上传本地文件，返回可访问 URL"""
        final_key = self._join_key(key)
        with open(local_path, "rb") as f:
            self.bucket.put_object(final_key, f)
        return self._build_url(final_key)

    def upload_bytes(self, data: bytes, key: str) -> str:
        final_key = self._join_key(key)
        self.bucket.put_object(final_key, data)
        return self._build_url(final_key)

    def _build_url(self, key: str) -> str:
        if self.custom_domain:
            return f"{self.custom_domain}/{key}"
        # 标准公网访问域名：{bucket}.{endpoint_host}/{key}
        # endpoint 形如 https://oss-cn-hangzhou.aliyuncs.com
        host = self.endpoint.split('://', 1)[-1]
        return f"https://{self.bucket_name}.{host}/{key}"


