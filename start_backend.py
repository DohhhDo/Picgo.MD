#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Meowdown Backend Startup Script
启动 FastAPI 后端服务的便捷脚本
"""


import sys
import subprocess
from pathlib import Path


def main():
    print("🐾 启动 Meowdown 后端服务...")

    # 检查后端目录
    backend_dir = Path("meowdown-backend")
    if not backend_dir.exists():
        print("❌ 错误: meowdown-backend 目录不存在")
        return 1

    main_py = backend_dir / "main.py"
    if not main_py.exists():
        print("❌ 错误: meowdown-backend/main.py 不存在")
        return 1

    try:
        print("🚀 启动 FastAPI 服务器...")
        print("📍 服务地址: http://127.0.0.1:8000")
        print("📖 API 文档: http://127.0.0.1:8000/docs")
        print("🔄 WebSocket: ws://127.0.0.1:8000/ws/{task_id}")
        print()
        print("按 Ctrl+C 停止服务")
        print("-" * 50)

        # 启动服务
        subprocess.run([sys.executable, "main.py"], cwd=str(backend_dir))

    except KeyboardInterrupt:
        print("\n🛑 服务已停止")
        return 0
    except Exception as e:
        print(f"❌ 启动失败: {e}")
        return 1


if __name__ == "__main__":
    sys.exit(main())
