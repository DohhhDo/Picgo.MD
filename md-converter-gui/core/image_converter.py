#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
图片转换核心模块 - 集成imarkdown和WebP转换功能
"""

import os
import random
import re
import sys
import tempfile
import time
from pathlib import Path
from typing import Callable, List, Optional, Tuple

import requests
from PIL import Image

# 添加imarkdown路径到系统路径
current_dir = Path(__file__).parent.parent.parent
imarkdown_path = current_dir / "imarkdown"
if imarkdown_path.exists():
    sys.path.insert(0, str(current_dir))

try:
    from imarkdown import LocalFileAdapter, MdFile, MdImageConverter
except ImportError:
    print("Warning: imarkdown not found, using fallback implementation")
    MdImageConverter = None
    LocalFileAdapter = None
    MdFile = None


class WebPConverter:
    """WebP转换器"""

    def __init__(self, quality: int = 80):
        self.quality = quality

    def set_quality(self, quality: int):
        """设置WebP质量"""
        self.quality = max(1, min(100, quality))

    def convert_to_webp(
        self, input_path: str, output_path: str
    ) -> Tuple[bool, int, int]:
        """
        将图片转换为WebP格式

        Returns:
            Tuple[成功状态, 原始文件大小(bytes), 转换后文件大小(bytes)]
        """
        try:
            # 获取原始文件大小
            original_size = os.path.getsize(input_path)

            with Image.open(input_path) as img:
                # 如果是RGBA模式，转换为RGB
                if img.mode == "RGBA":
                    # 创建白色背景
                    background = Image.new("RGB", img.size, (255, 255, 255))
                    background.paste(img, mask=img.split()[-1])  # 使用alpha通道作为mask
                    img = background
                elif img.mode not in ("RGB", "L"):
                    img = img.convert("RGB")

                # 根据质量设置选择不同的压缩策略
                save_kwargs = {
                    "format": "WEBP",
                    "quality": self.quality,
                    "optimize": True,
                    "method": 6,  # 使用最佳压缩方法
                }

                # 低质量时使用更激进的压缩
                if self.quality < 50:
                    save_kwargs["lossless"] = False
                    save_kwargs["method"] = 6
                elif self.quality > 90:
                    # 高质量时保持更多细节
                    save_kwargs["method"] = 4

                # 保存为WebP格式
                img.save(output_path, **save_kwargs)

                # 获取转换后文件大小
                converted_size = os.path.getsize(output_path)

                return True, original_size, converted_size

        except Exception as e:
            print(f"WebP转换失败: {e}")
            return False, 0, 0

    def download_and_convert(
        self, url: str, output_dir: str
    ) -> Optional[Tuple[str, int, int]]:
        """
        下载网络图片并转换为WebP

        Returns:
            Optional[Tuple[输出路径, 原始大小, 转换后大小]]
        """
        try:
            # 为部分站点添加常见请求头，避免被简单的反爬/热链保护拦截
            headers = {
                "User-Agent": (
                    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
                    "AppleWebKit/537.36 (KHTML, like Gecko) "
                    "Chrome/124.0 Safari/537.36"
                ),
                "Accept": "image/avif,image/webp,image/apng,image/*,*/*;q=0.8",
            }

            # 处理包含空格与中文字符的 URL（例如阿里云 OSS 对象名中存在空格），先快速 HEAD 取 Content-Type
            safe_url = requests.utils.requote_uri(url)
            # 动态设置 Referer：多数站点允许来自自身域的请求
            try:
                from urllib.parse import urlparse

                _p = urlparse(safe_url)
                if _p.scheme and _p.netloc:
                    headers["Referer"] = f"{_p.scheme}://{_p.netloc}/"
            except Exception:
                # 回退到通用 Referer
                headers.setdefault("Referer", "https://www.google.com/")
            try:
                head = requests.head(
                    safe_url, headers=headers, timeout=(5, 10), allow_redirects=True
                )
                head.raise_for_status()
            except Exception:
                # 忽略 head 失败，继续走 get
                pass

            # 先发起 GET（流式）并设置合理超时：连接 8s，读取 25s
            resp = requests.get(
                safe_url,
                headers=headers,
                timeout=(8, 25),
                stream=True,
                allow_redirects=True,
            )
            resp.raise_for_status()

            # 简单校验内容类型
            ctype = resp.headers.get("Content-Type", "")
            if "image" not in ctype.lower():
                raise ValueError(f"非图片资源，Content-Type={ctype}")

            # 限制最大下载大小（例如 15MB），防止超大图阻塞
            max_bytes = 15 * 1024 * 1024
            downloaded = 0

            # 生成临时文件名
            timestamp = time.strftime("%Y%m%d_%H%M%S", time.localtime())
            temp_name = f"img_{timestamp}_{random.randint(1000, 9999)}"

            with tempfile.NamedTemporaryFile(delete=False, suffix=".tmp") as temp_file:
                for chunk in resp.iter_content(chunk_size=64 * 1024):
                    if not chunk:
                        continue
                    downloaded += len(chunk)
                    if downloaded > max_bytes:
                        raise ValueError("图片超过 15MB，已取消")
                    temp_file.write(chunk)
                temp_path = temp_file.name

            # 转换为 WebP
            output_path = os.path.join(output_dir, f"{temp_name}.webp")
            success, original_size, converted_size = self.convert_to_webp(
                temp_path, output_path
            )

            # 清理临时文件
            try:
                os.unlink(temp_path)
            except Exception:
                pass

            if success:
                return output_path, original_size, converted_size
            return None

        except Exception as e:
            print(f"下载和转换失败: {e}")
            return None


class MarkdownImageProcessor:
    """Markdown图片处理器"""

    def __init__(self, webp_quality: int = 80):
        self.webp_converter = WebPConverter(webp_quality)
        self.progress_callback: Optional[Callable[[int, str], None]] = None

    def set_quality(self, quality: int):
        """设置WebP质量"""
        self.webp_converter.set_quality(quality)

    def set_progress_callback(self, callback: Callable[[int, str], None]):
        """设置进度回调函数"""
        self.progress_callback = callback

    def _update_progress(self, progress: int, message: str):
        """更新进度"""
        if self.progress_callback:
            self.progress_callback(progress, message)

    def find_image_links(self, markdown_text: str) -> List[str]:
        """查找Markdown中的所有图片链接"""
        # 匹配 ![alt](url) 和 <img src="url"> 格式；允许 ] 与 ( 之间存在空格
        pattern = r'(?:!\[.*?\]\s*\((.*?)\))|(?:<img.*?src=["\']([^"\']*)["\'].*?>)'
        matches = re.findall(pattern, markdown_text)

        # 提取非空的URL
        urls = []
        for match in matches:
            url = match[0] or match[1]  # 取第一个非空的组
            if not url:
                continue
            candidate = url.strip()
            # 允许 Markdown 形式 ![](<url with space>)，去除外围尖括号
            if candidate.startswith("<") and candidate.endswith(">"):
                candidate = candidate[1:-1].strip()
            if candidate:
                urls.append(candidate)

        return urls

    def process_markdown(
        self, markdown_text: str, output_dir: str = "images"
    ) -> Tuple[str, int, dict]:
        """
        处理Markdown文本，转换图片为WebP格式

        Args:
            markdown_text: Markdown文本内容
            output_dir: 图片输出目录

        Returns:
            Tuple[新的Markdown文本, 转换成功的图片数量, 压缩统计信息]
        """
        # 确保输出目录存在
        os.makedirs(output_dir, exist_ok=True)

        # 查找所有图片链接
        image_urls = self.find_image_links(markdown_text)

        if not image_urls:
            self._update_progress(100, "未找到图片链接")
            return (
                markdown_text,
                0,
                {
                    "total_original_size": 0,
                    "total_converted_size": 0,
                    "compression_ratio": 0,
                    "size_saved": 0,
                },
            )

        self._update_progress(10, f"找到 {len(image_urls)} 个图片链接")

        new_markdown = markdown_text
        success_count = 0
        total_original_size = 0
        total_converted_size = 0

        for i, url in enumerate(image_urls):
            try:
                progress = 10 + (i * 80 // len(image_urls))
                self._update_progress(progress, f"处理图片 {i+1}/{len(image_urls)}")

                if url.startswith(("http://", "https://")):
                    # 网络图片：下载并转换
                    result = self.webp_converter.download_and_convert(url, output_dir)
                    if result:
                        webp_path, original_size, converted_size = result
                        # 计算相对路径
                        relative_path = os.path.relpath(
                            webp_path, os.path.dirname(output_dir)
                        )
                        relative_path = relative_path.replace(
                            "\\", "/"
                        )  # 统一使用正斜杠

                        # 替换Markdown中的链接（同时处理可能存在的尖括号包裹形式）
                        for old in (f"<{url}>", url):
                            new_markdown = new_markdown.replace(old, relative_path)
                        success_count += 1
                        total_original_size += original_size
                        total_converted_size += converted_size

                elif os.path.exists(url):
                    # 本地图片：直接转换
                    filename = os.path.splitext(os.path.basename(url))[0]
                    webp_path = os.path.join(output_dir, f"{filename}.webp")

                    success, original_size, converted_size = (
                        self.webp_converter.convert_to_webp(url, webp_path)
                    )
                    if success:
                        # 计算相对路径
                        relative_path = os.path.relpath(
                            webp_path, os.path.dirname(output_dir)
                        )
                        relative_path = relative_path.replace("\\", "/")

                        # 替换Markdown中的链接（同时处理可能存在的尖括号包裹形式）
                        for old in (f"<{url}>", url):
                            new_markdown = new_markdown.replace(old, relative_path)
                        success_count += 1
                        total_original_size += original_size
                        total_converted_size += converted_size

            except Exception as e:
                print(f"处理图片失败 {url}: {e}")
                continue

        # 计算压缩比例
        compression_ratio = 0
        if total_original_size > 0:
            compression_ratio = (
                (total_original_size - total_converted_size) / total_original_size
            ) * 100

        compression_stats = {
            "total_original_size": total_original_size,
            "total_converted_size": total_converted_size,
            "compression_ratio": compression_ratio,
            "size_saved": total_original_size - total_converted_size,
        }

        self._update_progress(100, f"转换完成！成功转换 {success_count} 张图片")
        return new_markdown, success_count, compression_stats


# 为了向后兼容，提供简化的接口
def convert_markdown_images(
    markdown_text: str,
    output_dir: str = "images",
    quality: int = 80,
    progress_callback: Optional[Callable[[int, str], None]] = None,
) -> Tuple[str, int, dict]:
    """
    转换Markdown中的图片为WebP格式

    Args:
        markdown_text: Markdown文本
        output_dir: 输出目录
        quality: WebP质量 (1-100)
        progress_callback: 进度回调函数

    Returns:
        Tuple[新的Markdown文本, 成功转换的图片数量, 压缩统计信息]
    """
    processor = MarkdownImageProcessor(quality)
    if progress_callback:
        processor.set_progress_callback(progress_callback)

    return processor.process_markdown(markdown_text, output_dir)
