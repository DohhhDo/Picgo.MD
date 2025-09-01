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
import uvicorn
import requests

# 添加项目路径
project_root = Path(__file__).parent.parent
if str(project_root) not in sys.path:
    sys.path.insert(0, str(project_root))

# 导入现有的图片转换模块（兼容含连字符的目录名）
MarkdownImageProcessor = None
UploadManager = None
GitHubAdapter = None

try:
    # 首先尝试常规包名（如果你未来把目录重命名为 md_converter_gui 可直接生效）
    from md_converter_gui.core.image_converter import MarkdownImageProcessor as _MIP
    from md_converter_gui.uploader.manager import UploadManager as _UM
    from md_converter_gui.uploader.github_adapter import GitHubAdapter as _GH
    MarkdownImageProcessor = _MIP
    UploadManager = _UM
    GitHubAdapter = _GH
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

    img_conv_mod = _load_module_from_path('image_converter', img_conv_path) if img_conv_path.exists() else None
    uploader_mgr_mod = _load_module_from_path('uploader_manager', uploader_mgr_path) if uploader_mgr_path.exists() else None
    github_adapter_mod = _load_module_from_path('github_adapter', github_adapter_path) if github_adapter_path.exists() else None

    try:
        if img_conv_mod and hasattr(img_conv_mod, 'MarkdownImageProcessor'):
            MarkdownImageProcessor = getattr(img_conv_mod, 'MarkdownImageProcessor')
        if uploader_mgr_mod and hasattr(uploader_mgr_mod, 'UploadManager'):
            UploadManager = getattr(uploader_mgr_mod, 'UploadManager')
        if github_adapter_mod and hasattr(github_adapter_mod, 'GitHubAdapter'):
            GitHubAdapter = getattr(github_adapter_mod, 'GitHubAdapter')
    except Exception as e2:
        print(f"Warning: Could not set conversion classes: {e2}")

# 创建 FastAPI 应用
app = FastAPI(
    title="Meowdown API",
    description="现代化 Markdown 图片转换服务",
    version="1.0.0"
)

# 配置 CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173", "http://127.0.0.1:5173"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# 静态文件：持久输出目录
OUTPUTS_ROOT = (project_root / "outputs").resolve()
OUTPUTS_ROOT.mkdir(parents=True, exist_ok=True)
app.mount("/static", StaticFiles(directory=str(OUTPUTS_ROOT)), name="static")

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

        def sync_convert():
            def sync_progress_callback(progress: int, message: str):
                loop = asyncio.new_event_loop()
                asyncio.set_event_loop(loop)
                loop.run_until_complete(progress_callback(progress, message))
                loop.close()

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

        # 如果启用图床上传，执行上传并替换链接
        if request.use_image_bed and request.image_bed_provider == 'github' and GitHubAdapter:
            try:
                # 简单策略：将 /static/images/*.webp 转为临时本地路径列表并上传
                replaced = new_markdown
                upload_dir = (OUTPUTS_ROOT / (request.output_dir or 'images')).resolve()
                urls_map = {}
                # 从 markdown 抽取 /static/images/ 文件名
                import re
                paths = re.findall(r"/static/(?:images|[^/]+)/([\w\-\.]+\.webp)", replaced or "")
                local_paths = []
                for fn in set(paths):
                    p = os.path.join(str(upload_dir), fn)
                    if os.path.exists(p):
                        local_paths.append(p)
                cfg = request.image_bed_config or {}
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
                for lp in local_paths:
                    key = os.path.basename(lp)
                    url = gh.upload_file(lp, key)
                    urls_map[key] = url
                # 替换链接
                for key, url in urls_map.items():
                    replaced = replaced.replace(f"/static/{request.output_dir}/{key}", url)
                new_markdown = replaced
                task_manager.update_task(task_id, 95, "图床上传完成")
            except Exception as ue:
                task_manager.update_task(task_id, 95, f"图床上传失败: {ue}")

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
    """保存图床配置"""
    # 这里应该保存到配置文件或数据库
    # 目前只是返回成功响应
    return {
        "success": True,
        "message": "图床配置已保存"
    }

@app.get("/api/imagebed/config")
async def get_imagebed_config():
    """获取图床配置"""
    # 这里应该从配置文件或数据库读取
    # 目前返回默认配置
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

        return {"success": False, "message": "暂不支持的图床类型"}
    except Exception as e:
        return {"success": False, "message": f"测试失败: {e}"}

if __name__ == "__main__":
    uvicorn.run(
        "main:app", 
        host="127.0.0.1", 
        port=8000, 
        reload=True,
        log_level="info"
    )
