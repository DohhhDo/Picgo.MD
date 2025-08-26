#!/usr/bin/env python3
# -*- coding: utf-8 -*-

from __future__ import annotations

import base64
import os
from typing import Optional

try:
    import requests
except ImportError:
    requests = None


class GitHubAdapter:
    """GitHub仓库上传适配器（GUI版本）"""

    def __init__(
        self,
        token: str,
        owner: str,
        repo: str,
        branch: str = "main",
        path_prefix: str = "",
        storage_path_prefix: str = "",
        custom_domain: Optional[str] = None,
        use_jsdelivr: bool = False,
    ) -> None:
        if requests is None:
            raise ImportError("缺少依赖：pip install requests")
            
        self.token = token
        self.owner = owner
        self.repo = repo
        self.branch = branch
        self.path_prefix = path_prefix.strip("/")
        self.storage_path_prefix = storage_path_prefix.strip("/")
        self.custom_domain = custom_domain.rstrip("/") if custom_domain else None
        self.use_jsdelivr = use_jsdelivr

    def _join_key(self, key: str) -> str:
        key = key.lstrip("/")
        
        prefixes = []
        if self.storage_path_prefix:
            prefixes.append(self.storage_path_prefix)
        if self.path_prefix:
            prefixes.append(self.path_prefix)
            
        if prefixes:
            return "/".join(prefixes) + "/" + key
        return key

    def upload_file(self, local_path: str, key: str) -> str:
        """上传本地文件，返回可访问 URL"""
        with open(local_path, "rb") as f:
            data = f.read()
        return self.upload_bytes(data, key)

    def upload_bytes(self, data: bytes, key: str) -> str:
        final_key = self._join_key(key)
        
        # 编码为base64
        content_b64 = base64.b64encode(data).decode('utf-8')
        
        # GitHub API URL
        api_url = f"https://api.github.com/repos/{self.owner}/{self.repo}/contents/{final_key}"
        
        headers = {
            "Authorization": f"token {self.token}",
            "Accept": "application/vnd.github.v3+json",
            "Content-Type": "application/json"
        }
        
        # 检查文件是否存在
        response = requests.get(api_url, headers=headers)
        sha = None
        if response.status_code == 200:
            sha = response.json().get("sha")
        
        # 准备请求数据
        request_data = {
            "message": f"Upload image: {os.path.basename(key)}",
            "content": content_b64,
            "branch": self.branch
        }
        
        if sha:
            request_data["sha"] = sha
        
        # 上传文件
        response = requests.put(api_url, headers=headers, json=request_data)
        
        if response.status_code not in [200, 201]:
            raise Exception(f"GitHub API error {response.status_code}: {response.text}")
            
        return self._build_url(final_key)

    def _build_url(self, key: str) -> str:
        if self.custom_domain:
            return f"https://{self.custom_domain}/{key}"
        
        if self.use_jsdelivr:
            return f"https://cdn.jsdelivr.net/gh/{self.owner}/{self.repo}@{self.branch}/{key}"
        
        return f"https://raw.githubusercontent.com/{self.owner}/{self.repo}/{self.branch}/{key}"

