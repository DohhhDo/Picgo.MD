#!/usr/bin/env python3
# -*- coding: utf-8 -*-

from __future__ import annotations

import os
from typing import Optional

try:
    import boto3
    from botocore.config import Config
except ImportError:
    boto3 = None
    Config = None


class S3Adapter:
    """S3兼容服务上传适配器（GUI版本）"""

    def __init__(
        self,
        access_key: str,
        secret_key: str,
        bucket: str,
        region: Optional[str] = None,
        endpoint: Optional[str] = None,
        storage_path_prefix: str = "",
        custom_domain: Optional[str] = None,
        use_https: bool = True,
        path_style: bool = False,
    ) -> None:
        if boto3 is None or Config is None:
            raise ImportError("缺少依赖：pip install boto3")

        self.access_key = access_key
        self.secret_key = secret_key
        self.bucket = bucket
        self.region = region
        self.endpoint = endpoint
        self.storage_path_prefix = storage_path_prefix.strip("/")
        self.custom_domain = custom_domain.rstrip("/") if custom_domain else None
        self.use_https = use_https
        self.path_style = path_style

        # 创建 boto3 客户端
        session = boto3.Session(
            aws_access_key_id=self.access_key,
            aws_secret_access_key=self.secret_key,
            region_name=self.region,
        )

        client_kwargs = {}
        if self.endpoint:
            client_kwargs["endpoint_url"] = self.endpoint
        if self.path_style:
            client_kwargs["config"] = Config(s3={"addressing_style": "path"})

        self.client = session.client("s3", **client_kwargs)

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
            protocol = "https" if self.use_https else "http"
            return f"{protocol}://{self.custom_domain}/{key}"

        protocol = "https" if self.use_https else "http"

        if self.endpoint:
            # 自定义端点（如MinIO）
            endpoint_host = self.endpoint.replace("https://", "").replace("http://", "")
            if self.path_style:
                return f"{protocol}://{endpoint_host}/{self.bucket}/{key}"
            else:
                return f"{protocol}://{self.bucket}.{endpoint_host}/{key}"

        # 标准AWS S3
        if self.region and self.region != "us-east-1":
            if self.path_style:
                return (
                    f"{protocol}://s3.{self.region}.amazonaws.com/{self.bucket}/{key}"
                )
            else:
                return (
                    f"{protocol}://{self.bucket}.s3.{self.region}.amazonaws.com/{key}"
                )
        else:
            if self.path_style:
                return f"{protocol}://s3.amazonaws.com/{self.bucket}/{key}"
            else:
                return f"{protocol}://{self.bucket}.s3.amazonaws.com/{key}"
