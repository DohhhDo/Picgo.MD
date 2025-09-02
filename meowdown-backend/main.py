#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Meowdown Backend API Server
基于 FastAPI 的现代化后端服务
"""

import sys
import os
import asyncio
import uuid
from pathlib import Path
from typing import Dict, List, Optional
import json
import tempfile
import shutil

from fastapi import FastAPI, HTTPException, WebSocket, WebSocketDisconnect, UploadFile, File
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from pydantic import BaseModel
from fastapi.staticfiles import StaticFiles
from starlette.middleware.base import BaseHTTPMiddleware
import uvicorn
import requests
try:
    import oss2 as _oss2
except Exception:
    _oss2 = None

# 运行环境路径检测（开发/打包）
def _detect_base_dirs():
    if getattr(sys, "frozen", False) and hasattr(sys, "_MEIPASS"):
        # PyInstaller 解包临时目录（放置随包资源）
        meipass = Path(getattr(sys, "_MEIPASS"))
        # 打包后：写入用户目录，避免 Program Files 权限问题
        try:
            local_appdata = os.environ.get("LOCALAPPDATA") or os.environ.get("APPDATA")
        except Exception:
            local_appdata = None
        if local_appdata:
            writable = Path(local_appdata) / "Meowdown"
        else:
            writable = Path.home() / ".meowdown"
        writable.mkdir(parents=True, exist_ok=True)
        return meipass, writable
    # 源码运行：以仓库根为基准
    repo_root = Path(__file__).parent.parent
    return repo_root, repo_root

# 添加项目路径
project_root, writable_root = _detect_base_dirs()
if str(project_root) not in sys.path:
    sys.path.insert(0, str(project_root))

# 导入现有的图片转换模块（兼容含连字符的目录名）
MarkdownImageProcessor = None
UploadManager = None
GitHubAdapter = None
AliOssAdapter = None
CosAdapter = None
QiniuAdapter = None
S3Adapter = None

try:
    # 首先尝试常规包名（如果你未来把目录重命名为 md_converter_gui 可直接生效）
    from md_converter_gui.core.image_converter import MarkdownImageProcessor as _MIP
    from md_converter_gui.uploader.manager import UploadManager as _UM
    from md_converter_gui.uploader.github_adapter import GitHubAdapter as _GH
    from md_converter_gui.uploader.ali_oss_adapter import AliOssAdapter as _ALI
    from md_converter_gui.uploader.cos_adapter import CosAdapter as _COS
    from md_converter_gui.uploader.qiniu_adapter import QiniuAdapter as _QNU
    from md_converter_gui.uploader.s3_adapter import S3Adapter as _S3
    MarkdownImageProcessor = _MIP
    UploadManager = _UM
    GitHubAdapter = _GH
    AliOssAdapter = _ALI
    CosAdapter = _COS
    QiniuAdapter = _QNU
    S3Adapter = _S3
except Exception as e:
    print(f"Warning: Could not import conversion modules by package name: {e}")
    # 回退：使用文件路径动态加载
    import importlib.util as _importlib_util

    def _load_module_from_path(mod_name: str, file_path: Path):
        try:
            spec = _importlib_util.spec_from_file_location(mod_name, str(file_path))
            if spec and spec.loader:
                module = _importlib_util.module_from_spec(spec)
                spec.loader.exec_module(module)
                return module
        except Exception as _e:
            print(f"Warning: dynamic import failed for {file_path}: {_e}")
        return None

    gui_root = project_root / 'md-converter-gui'
    img_conv_path = gui_root / 'core' / 'image_converter.py'
    uploader_mgr_path = gui_root / 'uploader' / 'manager.py'
    github_adapter_path = gui_root / 'uploader' / 'github_adapter.py'
    aliyun_adapter_path = gui_root / 'uploader' / 'ali_oss_adapter.py'
    cos_adapter_path = gui_root / 'uploader' / 'cos_adapter.py'
    qiniu_adapter_path = gui_root / 'uploader' / 'qiniu_adapter.py'
    s3_adapter_path = gui_root / 'uploader' / 's3_adapter.py'

    img_conv_mod = _load_module_from_path('image_converter', img_conv_path) if img_conv_path.exists() else None
    uploader_mgr_mod = _load_module_from_path('uploader_manager', uploader_mgr_path) if uploader_mgr_path.exists() else None
    github_adapter_mod = _load_module_from_path('github_adapter', github_adapter_path) if github_adapter_path.exists() else None
    aliyun_adapter_mod = _load_module_from_path('ali_oss_adapter', aliyun_adapter_path) if aliyun_adapter_path.exists() else None
    cos_adapter_mod = _load_module_from_path('cos_adapter', cos_adapter_path) if cos_adapter_path.exists() else None
    qiniu_adapter_mod = _load_module_from_path('qiniu_adapter', qiniu_adapter_path) if qiniu_adapter_path.exists() else None
    s3_adapter_mod = _load_module_from_path('s3_adapter', s3_adapter_path) if s3_adapter_path.exists() else None

    try:
        if img_conv_mod and hasattr(img_conv_mod, 'MarkdownImageProcessor'):
            MarkdownImageProcessor = getattr(img_conv_mod, 'MarkdownImageProcessor')
        if uploader_mgr_mod and hasattr(uploader_mgr_mod, 'UploadManager'):
            UploadManager = getattr(uploader_mgr_mod, 'UploadManager')
        if github_adapter_mod and hasattr(github_adapter_mod, 'GitHubAdapter'):
            GitHubAdapter = getattr(github_adapter_mod, 'GitHubAdapter')
        if aliyun_adapter_mod and hasattr(aliyun_adapter_mod, 'AliOssAdapter'):
            AliOssAdapter = getattr(aliyun_adapter_mod, 'AliOssAdapter')
        if cos_adapter_mod and hasattr(cos_adapter_mod, 'CosAdapter'):
            CosAdapter = getattr(cos_adapter_mod, 'CosAdapter')
        if qiniu_adapter_mod and hasattr(qiniu_adapter_mod, 'QiniuAdapter'):
            QiniuAdapter = getattr(qiniu_adapter_mod, 'QiniuAdapter')
        if s3_adapter_mod and hasattr(s3_adapter_mod, 'S3Adapter'):
            S3Adapter = getattr(s3_adapter_mod, 'S3Adapter')
    except Exception as e2:
        print(f"Warning: Could not set conversion classes: {e2}")

# 最后兜底：若仍未获得 MarkdownImageProcessor，则提供一个最小可用实现
if MarkdownImageProcessor is None:
    print("Warning: using built-in fallback MarkdownImageProcessor")
    from PIL import Image
    import re
    import io
    import requests as _req

    class _FallbackProcessor:
        def __init__(self, webp_quality: int = 80):
            self.quality = max(1, min(100, int(webp_quality)))
            self._cb = None

        def set_progress_callback(self, cb):
            self._cb = cb

        def _progress(self, p: int, m: str):
            try:
                if self._cb:
                    self._cb(p, m)
            except Exception:
                pass

        def _find_images(self, text: str):
            pat = r'(?:!\[.*?\]\s*\((.*?)\))|(?:<img.*?src=["\']([^"\']*)["\'].*?>)'
            res = re.findall(pat, text or "")
            out = []
            for a, b in res:
                u = a or b
                if u:
                    u = u.strip()
                    if u.startswith('<') and u.endswith('>'):
                        u = u[1:-1].strip()
                    out.append(u)
            return out

        def _save_webp(self, pil_img: Image.Image, out_path: str):
            save_kwargs = {
                "format": "WEBP",
                "quality": self.quality,
                "optimize": True,
                "method": 6,
            }
            pil_img.save(out_path, **save_kwargs)

        def process_markdown(self, markdown_text: str, output_dir: str = "images"):
            os.makedirs(output_dir, exist_ok=True)
            urls = self._find_images(markdown_text)
            if not urls:
                self._progress(100, "未找到图片链接")
                return markdown_text, 0, {"total_original_size": 0, "total_converted_size": 0, "compression_ratio": 0, "size_saved": 0}

            self._progress(10, f"找到 {len(urls)} 个图片链接")
            new_md = markdown_text
            succ = 0
            tot_o = 0
            tot_c = 0

            for i, u in enumerate(urls):
                self._progress(10 + (i * 80 // max(1, len(urls))), f"处理图片 {i+1}/{len(urls)}")
                try:
                    if u.startswith(('http://', 'https://')):
                        r = _req.get(u, timeout=(8, 25))
                        r.raise_for_status()
                        img = Image.open(io.BytesIO(r.content))
                        if img.mode not in ("RGB", "L"):
                            img = img.convert("RGB")
                        name = f"img_{i+1}.webp"
                        outp = os.path.join(output_dir, name)
                        self._save_webp(img, outp)
                        o = len(r.content)
                        c = os.path.getsize(outp)
                        tot_o += o
                        tot_c += c
                        rel = os.path.relpath(outp, os.path.dirname(output_dir)).replace('\\', '/')
                        for old in (f"<{u}>", u):
                            new_md = new_md.replace(old, rel)
                        succ += 1
                    elif os.path.exists(u):
                        img = Image.open(u)
                        if img.mode not in ("RGB", "L"):
                            img = img.convert("RGB")
                        base = os.path.splitext(os.path.basename(u))[0] + ".webp"
                        outp = os.path.join(output_dir, base)
                        self._save_webp(img, outp)
                        o = os.path.getsize(u)
                        c = os.path.getsize(outp)
                        tot_o += o
                        tot_c += c
                        rel = os.path.relpath(outp, os.path.dirname(output_dir)).replace('\\', '/')
                        for old in (f"<{u}>", u):
                            new_md = new_md.replace(old, rel)
                        succ += 1
                except Exception:
                    continue

            ratio = (tot_o - tot_c) / tot_o * 100 if tot_o > 0 else 0
            stats = {"total_original_size": tot_o, "total_converted_size": tot_c, "compression_ratio": ratio, "size_saved": tot_o - tot_c}
            self._progress(100, f"转换完成！成功转换 {succ} 张图片")
            return new_md, succ, stats

    MarkdownImageProcessor = _FallbackProcessor
# 创建 FastAPI 应用
app = FastAPI(
    title="Meowdown API",
    description="现代化 Markdown 图片转换服务",
    version="1.0.0"
)

# 配置 CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:5173",
        "http://127.0.0.1:5173",
        "http://localhost:5175",
        "http://127.0.0.1:5175",
        "http://localhost:3000",
        "http://127.0.0.1:3000",
        # Tauri 应用打包后的来源
        "tauri://localhost",
        "app://localhost",
        "https://tauri.localhost",
        "http://tauri.localhost",
        # 允许所有 tauri 相关的 origin
        "*",
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# 为 Chrome/Edge 的 Private Network Access(PNA) 预检添加响应头，安装版（tauri://localhost）到 127.0.0.1 可能触发预检
class _AddPnaHeaderMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request, call_next):
        response = await call_next(request)
        try:
            origin = request.headers.get("origin") or request.headers.get("Origin")
            if origin:
                response.headers["Access-Control-Allow-Private-Network"] = "true"
        except Exception:
            pass
        return response

app.add_middleware(_AddPnaHeaderMiddleware)

# 静态文件：持久输出目录（打包后放在可执行文件同级）
OUTPUTS_ROOT = (writable_root / "outputs").resolve()
OUTPUTS_ROOT.mkdir(parents=True, exist_ok=True)
app.mount("/static", StaticFiles(directory=str(OUTPUTS_ROOT)), name="static")

# 配置持久化文件
IMAGEBED_CONFIG_PATH = OUTPUTS_ROOT / "imagebed_config.json"

# 工具函数：规范化阿里云 OSS endpoint
def _normalize_ali_endpoint(endpoint: Optional[str]) -> Optional[str]:
    try:
        if not endpoint:
            return endpoint
        ep = str(endpoint).strip().rstrip('/')
        # 仅区域前缀（例如 oss-cn-hangzhou）
        if ep.startswith('oss-') and '.' not in ep:
            return f"https://{ep}.aliyuncs.com"
        # 仅主机名（例如 oss-cn-hangzhou.aliyuncs.com）
        if '://' not in ep:
            ep = f"https://{ep}"
        return ep
    except Exception:
        return endpoint

# 数据模型
class ConversionRequest(BaseModel):
    markdown: str
    quality: int = 73
    output_dir: str = "images"
    use_image_bed: Optional[bool] = False
    image_bed_provider: Optional[str] = None
    image_bed_config: Optional[Dict] = None

class ConversionResponse(BaseModel):
    success: bool
    message: str
    new_markdown: Optional[str] = None
    stats: Optional[Dict] = None
    task_id: Optional[str] = None

class ProgressUpdate(BaseModel):
    task_id: str
    progress: int
    message: str
    completed: bool = False

class ImageBedConfig(BaseModel):
    provider: str
    enabled: bool
    config: Dict

# 全局状态管理
class TaskManager:
    def __init__(self):
        self.tasks: Dict[str, Dict] = {}
        self.websocket_connections: Dict[str, WebSocket] = {}
    
    def create_task(self, task_id: str) -> None:
        self.tasks[task_id] = {
            "status": "pending",
            "progress": 0,
            "message": "任务创建",
            "result": None
        }
    
    def update_task(self, task_id: str, progress: int, message: str, completed: bool = False):
        if task_id in self.tasks:
            self.tasks[task_id].update({
                "progress": progress,
                "message": message,
                "status": "completed" if completed else "running"
            })
    
    def get_task(self, task_id: str) -> Optional[Dict]:
        return self.tasks.get(task_id)

# 全局任务管理器
task_manager = TaskManager()

# WebSocket 连接管理
@app.websocket("/ws/{task_id}")
async def websocket_endpoint(websocket: WebSocket, task_id: str):
    await websocket.accept()
    task_manager.websocket_connections[task_id] = websocket
    
    try:
        while True:
            # 发送任务状态更新
            task = task_manager.get_task(task_id)
            if task:
                await websocket.send_json({
                    "task_id": task_id,
                    "progress": task["progress"],
                    "message": task["message"],
                    "completed": task["status"] == "completed"
                })
            
            await asyncio.sleep(0.5)
            
    except WebSocketDisconnect:
        if task_id in task_manager.websocket_connections:
            del task_manager.websocket_connections[task_id]

# API 端点
@app.get("/")
async def root():
    return {
        "message": "Meowdown Backend API",
        "version": "1.0.0",
        "status": "running"
    }

@app.get("/health")
async def health_check():
    return {
        "status": "healthy",
        "conversion_available": MarkdownImageProcessor is not None,
        "upload_available": UploadManager is not None
    }

@app.post("/api/convert", response_model=ConversionResponse)
async def convert_markdown(request: ConversionRequest):
    """转换 Markdown 中的图片"""
    
    if not MarkdownImageProcessor:
        raise HTTPException(
            status_code=503, 
            detail="图片转换服务不可用"
        )
    
    # 创建任务
    task_id = str(uuid.uuid4())
    task_manager.create_task(task_id)
    
    try:
        # 持久化输出目录：C:\Git\Meowdown\outputs\images（或使用请求中的相对目录名）
        outputs_root = OUTPUTS_ROOT
        # 允许前端传入相对目录名（默认 images）
        req_dir = request.output_dir or "images"
        if os.path.isabs(req_dir):
            output_dir = req_dir
        else:
            output_dir = str((outputs_root / req_dir).resolve())
        os.makedirs(output_dir, exist_ok=True)

        # 创建图片处理器
        processor = MarkdownImageProcessor(request.quality)

        # 设置进度回调（通过 WS 推送）
        async def progress_callback(progress: int, message: str):
            task_manager.update_task(task_id, progress, message)
            if task_id in task_manager.websocket_connections:
                websocket = task_manager.websocket_connections[task_id]
                try:
                    await websocket.send_json({
                        "task_id": task_id,
                        "progress": progress,
                        "message": message,
                        "completed": progress >= 100,
                    })
                except:
                    pass

        # 在线程池中运行同步转换
        import concurrent.futures

        # 复用当前请求所在事件循环，避免在子线程频繁创建/销毁新事件循环导致卡顿或崩溃
        main_loop = asyncio.get_running_loop()

        def sync_convert():
            def sync_progress_callback(progress: int, message: str):
                try:
                    fut = asyncio.run_coroutine_threadsafe(
                        progress_callback(progress, message), main_loop
                    )
                    # 避免阻塞：不等待结果，仅在出现异常时静默忽略
                    _ = fut
                except Exception:
                    pass

            processor.set_progress_callback(sync_progress_callback)
            return processor.process_markdown(request.markdown, output_dir)

        with concurrent.futures.ThreadPoolExecutor() as executor:
            future = executor.submit(sync_convert)
            new_markdown, success_count, stats = future.result()

        # 将相对路径 images/ 替换为可直接访问的静态路径 /static/images/
        try:
            if isinstance(new_markdown, str):
                new_markdown = new_markdown.replace("images/", "/static/images/")
        except Exception:
            pass

        # 规范化统计字段为小驼峰
        norm_stats = {}
        try:
            if isinstance(stats, dict):
                norm_stats = {
                    "totalOriginalSize": stats.get("total_original_size") or stats.get("totalOriginalSize"),
                    "totalConvertedSize": stats.get("total_converted_size") or stats.get("totalConvertedSize"),
                    "compressionRatio": stats.get("compression_ratio") or stats.get("compressionRatio"),
                    "sizeSaved": stats.get("size_saved") or stats.get("sizeSaved"),
                }
        except Exception:
            norm_stats = stats or {}

        # 解析“有效的图床配置”来源：优先请求体，其次读取本地持久化配置
        try:
            print(f"[imagebed] request flags: use={request.use_image_bed} provider={request.image_bed_provider}")
        except Exception:
            pass
        effective_enabled = bool(request.use_image_bed)
        effective_provider = request.image_bed_provider or None
        effective_cfg = request.image_bed_config or None

        if not effective_enabled or not effective_provider:
            try:
                if IMAGEBED_CONFIG_PATH.exists():
                    with open(IMAGEBED_CONFIG_PATH, 'r', encoding='utf-8') as f:
                        persisted = json.load(f)
                    if bool(persisted.get('enabled')):
                        effective_enabled = True
                        effective_provider = persisted.get('provider') or effective_provider
                        effective_cfg = persisted.get('config') or effective_cfg
                    try:
                        print(f"[imagebed] persisted: enabled={persisted.get('enabled')} provider={persisted.get('provider')}")
                    except Exception:
                        pass
            except Exception:
                pass

        try:
            # 不打印敏感字段，仅打印键名
            cfg_keys = list((effective_cfg or {}).keys())
            print(f"[imagebed] effective: enabled={effective_enabled} provider={effective_provider} cfg_keys={cfg_keys}")
        except Exception:
            pass

        # 如果启用图床上传，执行上传并替换链接
        if effective_enabled and effective_provider == 'github' and GitHubAdapter:
            try:
                task_manager.update_task(task_id, max(task_manager.get_task(task_id).get('progress', 0), 90), "准备上传到图床...")
                print("[upload] image bed enabled, provider=github")
                # 简单策略：将 /static/<dir>/*.webp（或 <dir>/*.webp）提取为文件名并上传
                replaced = new_markdown or ""
                upload_dir = (OUTPUTS_ROOT / (request.output_dir or 'images')).resolve()
                urls_map = {}
                import re
                dir_name = request.output_dir or 'images'
                # 同时匹配带 /static/ 前缀和纯相对路径两种形式
                pattern_static = rf"/static/{re.escape(dir_name)}/([^/\\?#]+?\\.webp)"
                pattern_relative = rf"(?<![\w/]){re.escape(dir_name)}/([^/\\?#]+?\\.webp)"
                keys = set(re.findall(pattern_static, replaced, flags=re.IGNORECASE)) | set(re.findall(pattern_relative, replaced, flags=re.IGNORECASE))
                print(f"[upload] dir_name={dir_name} upload_dir={upload_dir}")
                print(f"[upload] matched keys ({len(keys)}): {list(keys)[:5]}{'...' if len(keys) > 5 else ''}")
                local_paths = []
                for fn in keys:
                    p = os.path.join(str(upload_dir), fn)
                    if os.path.exists(p):
                        local_paths.append(p)
                    else:
                        # 打印不存在的文件，便于定位为何找不到
                        print(f"[upload] not found on disk: {p}")
                print(f"[upload] files to upload (regex): {len(local_paths)}")

                # 回退策略：若正则未匹配到，但 markdown 中包含 /static/<dir>/ 或 <dir>/，按文件名在目录中筛选最近生成且被引用的文件
                if not local_paths:
                    try:
                        import time
                        recent_threshold_sec = 10 * 60  # 10 分钟内
                        candidates = []
                        for fn in os.listdir(upload_dir):
                            if not fn.lower().endswith('.webp'):
                                continue
                            full = os.path.join(str(upload_dir), fn)
                            try:
                                mtime = os.path.getmtime(full)
                            except Exception:
                                continue
                            if (time.time() - mtime) <= recent_threshold_sec:
                                # 仅收录 markdown 中确实引用到的文件名
                                if (f"/static/{dir_name}/{fn}" in replaced) or (f"{dir_name}/{fn}" in replaced):
                                    candidates.append(full)
                        if candidates:
                            local_paths = candidates
                        print(f"[upload] files to upload (fallback): {len(local_paths)}")
                    except Exception as _fe:
                        print(f"[upload] fallback scan error: {_fe}")
                cfg = effective_cfg or {}
                gh = GitHubAdapter(
                    token=cfg.get('token',''),
                    owner=cfg.get('owner',''),
                    repo=cfg.get('repo',''),
                    branch=cfg.get('branch') or 'main',
                    path_prefix=cfg.get('path_prefix') or '',
                    storage_path_prefix=cfg.get('storage_path_prefix') or '',
                    custom_domain=cfg.get('custom_domain') or None,
                    use_jsdelivr=bool(cfg.get('use_jsdelivr')),
                )
                total_files = len(local_paths)
                if total_files == 0:
                    task_manager.update_task(task_id, 95, "未发现可上传文件，跳过上传")
                for index, lp in enumerate(local_paths, start=1):
                    # 上传进度：90% -> 98%
                    step = 90 + int(8 * index / max(1, total_files))
                    task_manager.update_task(task_id, step, f"上传中 {index}/{total_files}")
                    key = os.path.basename(lp)
                    url = gh.upload_file(lp, key)
                    urls_map[key] = url
                # 替换链接
                for key, url in urls_map.items():
                    replaced = replaced.replace(f"/static/{dir_name}/{key}", url)
                    replaced = replaced.replace(f"{dir_name}/{key}", url)
                new_markdown = replaced
                # 清理本地已上传的 webp 文件
                deleted_count = 0
                for lp in local_paths:
                    try:
                        os.remove(lp)
                        deleted_count += 1
                    except Exception:
                        pass
                # 如目录为空，可尝试清理空目录（忽略错误）
                try:
                    if os.path.isdir(upload_dir) and not os.listdir(upload_dir):
                        os.rmdir(upload_dir)
                except Exception:
                    pass
                task_manager.update_task(task_id, 99, f"图床上传完成，已清理本地文件 {deleted_count} 个")
            except Exception as ue:
                task_manager.update_task(task_id, 95, f"图床上传失败: {ue}")
        elif effective_enabled and effective_provider == 'aliyun' and AliOssAdapter:
            try:
                task_manager.update_task(task_id, max(task_manager.get_task(task_id).get('progress', 0), 90), "准备上传到阿里云...")
                replaced = new_markdown or ""
                upload_dir = (OUTPUTS_ROOT / (request.output_dir or 'images')).resolve()
                urls_map = {}
                import re
                dir_name = request.output_dir or 'images'
                pattern_static = rf"/static/{re.escape(dir_name)}/([^/\\?#]+?\\.webp)"
                pattern_relative = rf"(?<![\w/]){re.escape(dir_name)}/([^/\\?#]+?\\.webp)"
                keys = set(re.findall(pattern_static, replaced, flags=re.IGNORECASE)) | set(re.findall(pattern_relative, replaced, flags=re.IGNORECASE))
                print(f"[aliyun] dir_name={dir_name} upload_dir={upload_dir}")
                print(f"[aliyun] matched keys ({len(keys)}): {list(keys)[:5]}{'...' if len(keys) > 5 else ''}")
                try:
                    sample = replaced[:200].replace("\n"," ")
                    print(f"[aliyun] new_md sample: {sample}")
                except Exception:
                    pass
                local_paths = []
                for fn in keys:
                    p = os.path.join(str(upload_dir), fn)
                    if os.path.exists(p):
                        local_paths.append(p)
                    else:
                        print(f"[aliyun] not found on disk: {p}")
                # Fallback: scan recent files in upload_dir referenced by markdown
                if not local_paths:
                    try:
                        import time
                        recent_threshold_sec = 10 * 60
                        candidates = []
                        for fn in os.listdir(upload_dir):
                            if not fn.lower().endswith('.webp'):
                                continue
                            full = os.path.join(str(upload_dir), fn)
                            try:
                                mtime = os.path.getmtime(full)
                            except Exception:
                                continue
                            if (time.time() - mtime) <= recent_threshold_sec:
                                if (f"/static/{dir_name}/{fn}" in replaced) or (f"{dir_name}/{fn}" in replaced):
                                    candidates.append(full)
                        if candidates:
                            local_paths = candidates
                        print(f"[aliyun] files to upload (fallback): {len(local_paths)}")
                    except Exception as _fe:
                        print(f"[aliyun] fallback scan error: {_fe}")
                cfg = effective_cfg or {}
                # 规范化 endpoint
                norm_endpoint = _normalize_ali_endpoint(cfg.get('endpoint',''))
                oss = AliOssAdapter(
                    access_key_id=cfg.get('access_key_id',''),
                    access_key_secret=cfg.get('access_key_secret',''),
                    bucket_name=cfg.get('bucket_name',''),
                    endpoint=norm_endpoint or '',
                    storage_path_prefix=cfg.get('storage_path_prefix') or '',
                    custom_domain=cfg.get('custom_domain') or None,
                )
                total_files = len(local_paths)
                if total_files == 0:
                    task_manager.update_task(task_id, 95, "未发现可上传文件，跳过上传")
                for index, lp in enumerate(local_paths, start=1):
                    step = 90 + int(8 * index / max(1, total_files))
                    task_manager.update_task(task_id, step, f"上传中 {index}/{total_files}")
                    key = os.path.basename(lp)
                    url = oss.upload_file(lp, key)
                    urls_map[key] = url
                for key, url in urls_map.items():
                    replaced = replaced.replace(f"/static/{dir_name}/{key}", url)
                    replaced = replaced.replace(f"{dir_name}/{key}", url)
                new_markdown = replaced
                # 清理本地
                deleted_count = 0
                for lp in local_paths:
                    try:
                        os.remove(lp)
                        deleted_count += 1
                    except Exception:
                        pass
                try:
                    if os.path.isdir(upload_dir) and not os.listdir(upload_dir):
                        os.rmdir(upload_dir)
                except Exception:
                    pass
                task_manager.update_task(task_id, 99, f"阿里云上传完成，已清理本地文件 {deleted_count} 个")
            except Exception as ue:
                task_manager.update_task(task_id, 95, f"阿里云上传失败: {ue}")
        elif effective_enabled and effective_provider == 'cos' and CosAdapter:
            try:
                task_manager.update_task(task_id, max(task_manager.get_task(task_id).get('progress', 0), 90), "准备上传到 COS...")
                replaced = new_markdown or ""
                upload_dir = (OUTPUTS_ROOT / (request.output_dir or 'images')).resolve()
                urls_map = {}
                import re
                dir_name = request.output_dir or 'images'
                pattern_static = rf"/static/{re.escape(dir_name)}/([^/\\?#]+?\\.webp)"
                pattern_relative = rf"(?<![\w/]){re.escape(dir_name)}/([^/\\?#]+?\\.webp)"
                keys = set(re.findall(pattern_static, replaced, flags=re.IGNORECASE)) | set(re.findall(pattern_relative, replaced, flags=re.IGNORECASE))
                try:
                    print(f"[cos] dir_name={dir_name} upload_dir={upload_dir}")
                    print(f"[cos] matched keys ({len(keys)}): {list(keys)[:5]}{'...' if len(keys) > 5 else ''}")
                    sample = replaced[:200].replace("\n"," ")
                    print(f"[cos] new_md sample: {sample}")
                except Exception:
                    pass
                local_paths = [os.path.join(str(upload_dir), fn) for fn in keys if os.path.exists(os.path.join(str(upload_dir), fn))]
                # fallback: 引用匹配 + mtime
                if not local_paths:
                    try:
                        import time
                        recent_threshold_sec = 10 * 60
                        candidates = []
                        for fn in os.listdir(upload_dir):
                            if not fn.lower().endswith('.webp'):
                                continue
                            full = os.path.join(str(upload_dir), fn)
                            try:
                                mtime = os.path.getmtime(full)
                            except Exception:
                                continue
                            if (time.time() - mtime) <= recent_threshold_sec:
                                if (f"/static/{dir_name}/{fn}" in replaced) or (f"{dir_name}/{fn}" in replaced):
                                    candidates.append(full)
                        if candidates:
                            local_paths = candidates
                        print(f"[cos] files to upload (fallback): {len(local_paths)}")
                    except Exception as _fe:
                        print(f"[cos] fallback scan error: {_fe}")
                cfg = effective_cfg or {}
                cos = CosAdapter(
                    secret_id=cfg.get('secret_id',''),
                    secret_key=cfg.get('secret_key',''),
                    bucket=cfg.get('bucket',''),
                    region=cfg.get('region',''),
                    storage_path_prefix=cfg.get('storage_path_prefix') or '',
                    custom_domain=cfg.get('custom_domain') or None,
                    use_https=bool(cfg.get('use_https', True)),
                )
                total_files = len(local_paths)
                if total_files == 0:
                    task_manager.update_task(task_id, 95, "未发现可上传文件，跳过上传")
                for index, lp in enumerate(local_paths, start=1):
                    step = 90 + int(8 * index / max(1, total_files))
                    task_manager.update_task(task_id, step, f"上传中 {index}/{total_files}")
                    key = os.path.basename(lp)
                    url = cos.upload_file(lp, key)
                    urls_map[key] = url
                for key, url in urls_map.items():
                    try:
                        pattern_static2 = rf"/static/{re.escape(dir_name)}/{re.escape(key)}([\\?#][^\\s\\)]*)?"
                        pattern_relative2 = rf"(?<![\w/]){re.escape(dir_name)}/{re.escape(key)}([\\?#][^\\s\\)]*)?"
                        replaced, n1 = re.subn(pattern_static2, url, replaced)
                        replaced, n2 = re.subn(pattern_relative2, url, replaced)
                        print(f"[cos] replaced {key} -> {url} (static:{n1}, rel:{n2})")
                    except Exception:
                        before = replaced
                        replaced = replaced.replace(f"/static/{dir_name}/{key}", url)
                        replaced = replaced.replace(f"{dir_name}/{key}", url)
                        print(f"[cos] replaced (fallback) {key} -> {url} (changed:{1 if before != replaced else 0})")
                new_markdown = replaced
                # 清理本地
                deleted = 0
                for lp in local_paths:
                    try:
                        os.remove(lp)
                        deleted += 1
                    except Exception:
                        pass
                task_manager.update_task(task_id, 99, f"COS 上传完成，已清理 {deleted} 个文件")
            except Exception as ue:
                task_manager.update_task(task_id, 95, f"COS 上传失败: {ue}")
        elif effective_enabled and effective_provider == 'qiniu' and QiniuAdapter:
            try:
                task_manager.update_task(task_id, max(task_manager.get_task(task_id).get('progress', 0), 90), "准备上传到七牛...")
                replaced = new_markdown or ""
                upload_dir = (OUTPUTS_ROOT / (request.output_dir or 'images')).resolve()
                urls_map = {}
                import re
                dir_name = request.output_dir or 'images'
                pattern_static = rf"/static/{re.escape(dir_name)}/([^/\\?#]+?\\.webp)"
                pattern_relative = rf"(?<![\w/]){re.escape(dir_name)}/([^/\\?#]+?\\.webp)"
                keys = set(re.findall(pattern_static, replaced, flags=re.IGNORECASE)) | set(re.findall(pattern_relative, replaced, flags=re.IGNORECASE))
                local_paths = [os.path.join(str(upload_dir), fn) for fn in keys if os.path.exists(os.path.join(str(upload_dir), fn))]
                cfg = effective_cfg or {}
                qn = QiniuAdapter(
                    access_key=cfg.get('access_key',''),
                    secret_key=cfg.get('secret_key',''),
                    bucket=cfg.get('bucket',''),
                    domain=cfg.get('domain',''),
                    storage_path_prefix=cfg.get('storage_path_prefix') or '',
                    use_https=bool(cfg.get('use_https', True)),
                )
                total_files = len(local_paths)
                if total_files == 0:
                    task_manager.update_task(task_id, 95, "未发现可上传文件，跳过上传")
                for index, lp in enumerate(local_paths, start=1):
                    step = 90 + int(8 * index / max(1, total_files))
                    task_manager.update_task(task_id, step, f"上传中 {index}/{total_files}")
                    key = os.path.basename(lp)
                    url = qn.upload_file(lp, key)
                    urls_map[key] = url
                for key, url in urls_map.items():
                    replaced = replaced.replace(f"/static/{dir_name}/{key}", url)
                    replaced = replaced.replace(f"{dir_name}/{key}", url)
                new_markdown = replaced
                for lp in local_paths:
                    try:
                        os.remove(lp)
                    except Exception:
                        pass
                task_manager.update_task(task_id, 99, "七牛上传完成")
            except Exception as ue:
                task_manager.update_task(task_id, 95, f"七牛上传失败: {ue}")
        elif effective_enabled and effective_provider == 's3' and S3Adapter:
            try:
                task_manager.update_task(task_id, max(task_manager.get_task(task_id).get('progress', 0), 90), "准备上传到 S3...")
                replaced = new_markdown or ""
                upload_dir = (OUTPUTS_ROOT / (request.output_dir or 'images')).resolve()
                urls_map = {}
                import re
                dir_name = request.output_dir or 'images'
                pattern_static = rf"/static/{re.escape(dir_name)}/([^/\\?#]+?\\.webp)"
                pattern_relative = rf"(?<![\w/]){re.escape(dir_name)}/([^/\\?#]+?\\.webp)"
                keys = set(re.findall(pattern_static, replaced, flags=re.IGNORECASE)) | set(re.findall(pattern_relative, replaced, flags=re.IGNORECASE))
                local_paths = [os.path.join(str(upload_dir), fn) for fn in keys if os.path.exists(os.path.join(str(upload_dir), fn))]
                cfg = effective_cfg or {}
                s3 = S3Adapter(
                    access_key=cfg.get('access_key',''),
                    secret_key=cfg.get('secret_key',''),
                    bucket=cfg.get('bucket',''),
                    region=cfg.get('region'),
                    endpoint=cfg.get('endpoint'),
                    storage_path_prefix=cfg.get('storage_path_prefix') or '',
                    custom_domain=cfg.get('custom_domain') or None,
                    use_https=bool(cfg.get('use_https', True)),
                    path_style=bool(cfg.get('path_style', False)),
                )
                total_files = len(local_paths)
                if total_files == 0:
                    task_manager.update_task(task_id, 95, "未发现可上传文件，跳过上传")
                for index, lp in enumerate(local_paths, start=1):
                    step = 90 + int(8 * index / max(1, total_files))
                    task_manager.update_task(task_id, step, f"上传中 {index}/{total_files}")
                    key = os.path.basename(lp)
                    url = s3.upload_file(lp, key)
                    urls_map[key] = url
                for key, url in urls_map.items():
                    replaced = replaced.replace(f"/static/{dir_name}/{key}", url)
                    replaced = replaced.replace(f"{dir_name}/{key}", url)
                new_markdown = replaced
                for lp in local_paths:
                    try:
                        os.remove(lp)
                    except Exception:
                        pass
                task_manager.update_task(task_id, 99, "S3 上传完成")
            except Exception as ue:
                task_manager.update_task(task_id, 95, f"S3 上传失败: {ue}")
        else:
            # 明确记录未进行上传的原因，便于调试
            reason = []
            if not effective_enabled:
                reason.append("未启用")
            if effective_provider not in ('github','aliyun','cos','qiniu','s3'):
                reason.append(f"provider={effective_provider or 'None'} 不支持")
            if effective_provider == 'github' and not GitHubAdapter:
                reason.append("GitHubAdapter 未加载")
            if effective_provider == 'aliyun' and not AliOssAdapter:
                reason.append("AliOssAdapter 未加载")
            if effective_provider == 'cos' and not CosAdapter:
                reason.append("CosAdapter 未加载")
            if effective_provider == 'qiniu' and not QiniuAdapter:
                reason.append("QiniuAdapter 未加载")
            if effective_provider == 's3' and not S3Adapter:
                reason.append("S3Adapter 未加载")
            if reason:
                task_manager.update_task(task_id, max(task_manager.get_task(task_id).get('progress', 0), 90), f"跳过上传：{'，'.join(reason)}")
                try:
                    print(f"[imagebed] skip upload: {'，'.join(reason)}")
                except Exception:
                    pass

        # 标记完成
        task_manager.update_task(task_id, 100, "转换完成", True)

        return ConversionResponse(
            success=True,
            message=f"成功转换 {success_count} 张图片",
            new_markdown=new_markdown,
            stats=norm_stats,
            task_id=task_id,
        )
            
    except Exception as e:
        task_manager.update_task(task_id, 0, f"转换失败: {str(e)}", True)
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/task/{task_id}")
async def get_task_status(task_id: str):
    """获取任务状态"""
    task = task_manager.get_task(task_id)
    if not task:
        raise HTTPException(status_code=404, detail="任务不存在")
    
    return task

@app.post("/api/upload")
async def upload_to_imagebed(
    files: List[UploadFile] = File(...),
    config: str = None
):
    """上传文件到图床"""
    
    if not UploadManager:
        raise HTTPException(
            status_code=503, 
            detail="图床上传服务不可用"
        )
    
    try:
        # 解析配置
        if config:
            imagebed_config = json.loads(config)
        else:
            imagebed_config = None
        
        # 创建上传管理器
        upload_manager = UploadManager()
        
        # 临时保存上传的文件
        temp_files = []
        for file in files:
            temp_file = tempfile.NamedTemporaryFile(delete=False, suffix=f".{file.filename.split('.')[-1]}")
            content = await file.read()
            temp_file.write(content)
            temp_file.close()
            temp_files.append(temp_file.name)
        
        try:
            # 上传文件
            result_mapping = upload_manager.upload_webps(temp_files)
            
            return {
                "success": True,
                "message": f"成功上传 {len(result_mapping)} 个文件",
                "urls": result_mapping
            }
        
        finally:
            # 清理临时文件
            for temp_file in temp_files:
                try:
                    os.unlink(temp_file)
                except:
                    pass
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/api/imagebed/config")
async def save_imagebed_config(config: ImageBedConfig):
    """保存图床配置到本地 JSON 文件"""
    try:
        data = {
            "provider": config.provider,
            "enabled": bool(config.enabled),
            "config": config.config or {},
        }
        # 原子写入：先写临时文件再替换
        tmp_path = IMAGEBED_CONFIG_PATH.with_suffix(".json.tmp")
        with open(tmp_path, "w", encoding="utf-8") as f:
            json.dump(data, f, ensure_ascii=False, indent=2)
        os.replace(tmp_path, IMAGEBED_CONFIG_PATH)

        return {
            "success": True,
            "message": "图床配置已保存",
            "data": data,
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"保存失败: {e}")

@app.get("/api/imagebed/config")
async def get_imagebed_config():
    """获取图床配置（从本地 JSON 文件读取）"""
    try:
        if IMAGEBED_CONFIG_PATH.exists():
            with open(IMAGEBED_CONFIG_PATH, "r", encoding="utf-8") as f:
                data = json.load(f)
            # 兜底字段
            provider = data.get("provider") or ""
            enabled = bool(data.get("enabled"))
            cfg = data.get("config") or {}
            return {
                "provider": provider,
                "enabled": enabled,
                "config": cfg,
            }
    except Exception:
        # 读取失败则回退为默认
        pass
    return {
        "provider": "",
        "enabled": False,
        "config": {}
    }

@app.post("/api/imagebed/test")
async def test_imagebed_config(config: ImageBedConfig):
    """测试图床配置是否可用（当前实现：GitHub）"""
    try:
        if not config.enabled:
            return {"success": False, "message": "图床未启用"}

        provider = config.provider
        cfg = config.config or {}

        if provider == "github":
            token = cfg.get("token")
            owner = cfg.get("owner")
            repo = cfg.get("repo")
            branch = cfg.get("branch") or "main"
            if not token or not owner or not repo:
                return {"success": False, "message": "缺少 token/owner/repo"}

            repo_api = f"https://api.github.com/repos/{owner}/{repo}"
            headers = {
                "Authorization": f"token {token}",
                "Accept": "application/vnd.github.v3+json",
            }
            r = requests.get(repo_api, headers=headers, timeout=10)
            if r.status_code != 200:
                return {"success": False, "message": f"仓库访问失败: {r.status_code}"}

            data = r.json()
            perms = (data or {}).get("permissions", {})
            can_push = bool(perms.get("push")) or bool(perms.get("admin"))
            if not can_push:
                return {"success": False, "message": "无写入权限（需要 push 权限）"}

            # 分支检查（可选）
            br = requests.get(f"{repo_api}/branches/{branch}", headers=headers, timeout=10)
            if br.status_code != 200:
                return {"success": False, "message": f"分支不存在或无权访问: {branch}"}

            return {"success": True, "message": "GitHub 配置可用"}

        if provider == "aliyun":
            try:
                access_key_id = cfg.get("access_key_id")
                access_key_secret = cfg.get("access_key_secret")
                bucket_name = cfg.get("bucket_name")
                endpoint = _normalize_ali_endpoint(cfg.get("endpoint"))
                if not all([access_key_id, access_key_secret, bucket_name, endpoint]):
                    return {"success": False, "message": "缺少 access_key_id/secret/bucket/endpoint"}
                if AliOssAdapter is None:
                    return {"success": False, "message": "AliOssAdapter 未加载"}
                try:
                    tmp = AliOssAdapter(access_key_id, access_key_secret, bucket_name, endpoint)
                    # 真实请求：获取 bucket 信息以验证凭证与 endpoint/bucket 一致性
                    info = tmp.bucket.get_bucket_info()
                    # 返回部分元数据，避免暴露敏感信息
                    return {"success": True, "message": "阿里云配置可用", "region": getattr(info, 'region', None)}
                except Exception as _e:
                    return {"success": False, "message": f"连接失败: {_e}"}
            except Exception as _ex:
                return {"success": False, "message": f"测试失败: {_ex}"}
        if provider == "cos":
            try:
                sid = cfg.get('secret_id')
                skey = cfg.get('secret_key')
                bucket = cfg.get('bucket')
                region = cfg.get('region')
                if not all([sid, skey, bucket, region]):
                    return {"success": False, "message": "缺少 secret_id/secret_key/bucket/region"}
                if CosAdapter is None:
                    return {"success": False, "message": "CosAdapter 未加载"}
                try:
                    tmp = CosAdapter(sid, skey, bucket, region)
                    # 真实请求：head_bucket 校验连通与权限
                    tmp.client.head_bucket(Bucket=bucket)
                except Exception as _e:
                    return {"success": False, "message": f"连接失败: {_e}"}
                return {"success": True, "message": "COS 配置可用"}
            except Exception as _ex:
                return {"success": False, "message": f"测试失败: {_ex}"}
        if provider == "qiniu":
            try:
                ak = cfg.get('access_key')
                sk = cfg.get('secret_key')
                bucket = cfg.get('bucket')
                domain = cfg.get('domain')
                if not all([ak, sk, bucket, domain]):
                    return {"success": False, "message": "缺少 access_key/secret_key/bucket/domain"}
                if QiniuAdapter is None:
                    return {"success": False, "message": "QiniuAdapter 未加载"}
                try:
                    tmp = QiniuAdapter(ak, sk, bucket, domain)
                    _ = tmp.domain
                except Exception as _e:
                    return {"success": False, "message": f"连接失败: {_e}"}
                return {"success": True, "message": "七牛配置可用"}
            except Exception as _ex:
                return {"success": False, "message": f"测试失败: {_ex}"}
        if provider == "s3":
            try:
                ak = cfg.get('access_key')
                sk = cfg.get('secret_key')
                bucket = cfg.get('bucket')
                region = cfg.get('region')
                endpoint = cfg.get('endpoint')
                if not all([ak, sk, bucket]):
                    return {"success": False, "message": "缺少 access_key/secret_key/bucket"}
                if S3Adapter is None:
                    return {"success": False, "message": "S3Adapter 未加载"}
                try:
                    tmp = S3Adapter(ak, sk, bucket, region=region, endpoint=endpoint)
                    # 真实请求：head_bucket 校验
                    tmp.client.head_bucket(Bucket=bucket)
                except Exception as _e:
                    return {"success": False, "message": f"连接失败: {_e}"}
                return {"success": True, "message": "S3 配置可用"}
            except Exception as _ex:
                return {"success": False, "message": f"测试失败: {_ex}"}
        return {"success": False, "message": "暂不支持的图床类型"}
    except Exception as e:
        return {"success": False, "message": f"测试失败: {e}"}

if __name__ == "__main__":
    # 在打包环境（PyInstaller）下禁用热重载，避免 watchfiles 反复重启
    is_frozen = bool(getattr(sys, "frozen", False))
    reload_flag = False if is_frozen else bool(os.getenv("UVICORN_RELOAD", "1") not in ("0", "false", "False"))
    uvicorn.run(
        app,
        host="127.0.0.1",
        port=8000,
        reload=reload_flag,
        log_level="info",
    )
