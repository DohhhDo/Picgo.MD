# -*- mode: python ; coding: utf-8 -*-
# MdImgConverter 优化版打包配置
# 基于简略版进一步优化，减小体积并提高性能

import os
import platform

# 检测系统架构和平台
is_windows = platform.system() == 'Windows'
is_64bit = platform.machine().endswith('64')

# 定义数据文件
datas = [
    ('pictures', 'pictures'),
    ('image', 'image'), 
    ('imarkdown', 'imarkdown'),
]

# 定义隐藏导入 - 仅包含必需的模块
hiddenimports = [
    # 云存储相关
    'qcloud_cos',
    'qiniu', 
    'boto3',
    'botocore',
    'urllib3',
    # 图像处理
    'PIL',
    'PIL.Image',
    'PIL.ImageQt',
    # 网络请求
    'requests',
    'requests.adapters',
    'requests.packages.urllib3',
    # JSON和配置
    'json',
    'configparser',
    # 系统相关
    'platform',
    'subprocess',
    # PyQt6 核心模块
    'PyQt6.QtCore',
    'PyQt6.QtGui', 
    'PyQt6.QtWidgets',
    'PyQt6.sip',
]

# 定义要排除的模块 - 更精确的排除列表
excludes = [
    # PyQt6 非必需模块
    'PyQt6.QtQml',
    'PyQt6.QtQuick',
    'PyQt6.QtQuickWidgets',
    'PyQt6.QtWebEngineCore', 
    'PyQt6.QtWebEngineWidgets',
    'PyQt6.QtWebChannel',
    'PyQt6.QtNetwork',
    'PyQt6.QtTest',
    'PyQt6.QtSql',
    'PyQt6.QtMultimedia',
    'PyQt6.QtMultimediaWidgets',
    'PyQt6.QtChart',
    'PyQt6.QtBluetooth',
    'PyQt6.QtNfc',
    'PyQt6.QtPositioning',
    'PyQt6.QtSensors',
    'PyQt6.QtSerialPort',
    'PyQt6.Qt3DCore',
    'PyQt6.Qt3DRender',
    'PyQt6.Qt3DInput',
    'PyQt6.Qt3DLogic',
    'PyQt6.Qt3DAnimation',
    'PyQt6.Qt3DExtras',
    'PyQt6.QtDataVisualization',
    'PyQt6.QtDesigner',
    'PyQt6.QtHelp',
    'PyQt6.QtLocation',
    'PyQt6.QtOpenGL',
    'PyQt6.QtOpenGLWidgets',
    'PyQt6.QtPdf',
    'PyQt6.QtPdfWidgets',
    'PyQt6.QtRemoteObjects',
    'PyQt6.QtSvg',
    'PyQt6.QtSvgWidgets',
    
    # 科学计算库
    'matplotlib',
    'matplotlib.pyplot',
    'numpy',
    'scipy', 
    'pandas',
    'sympy',
    'sklearn',
    
    # 开发和调试工具
    'jupyter',
    'notebook',
    'ipython',
    'IPython',
    'pdb',
    'pydoc',
    'unittest',
    'doctest',
    'pytest',
    'coverage',
    
    # 其他GUI库
    'tkinter',
    'tk',
    'tcl',
    'turtle',
    
    # 网络和服务器
    'http.server',
    'socketserver',
    'xmlrpc',
    'wsgiref',
    'tornado',
    'flask',
    'django',
    
    # 数据库
    'sqlite3',
    'mysql',
    'postgresql',
    'pymongo',
    
    # 打包和分发工具
    'setuptools', 
    'pip',
    'wheel',
    'distutils',
    'pkg_resources',
    
    # 编译和构建工具
    'distutils.util',
    'compiler',
    'py_compile',
    'compileall',
    
    # 其他非必需模块
    'difflib',
    'qtawesome',  # 如果不使用图标库
    'email',
    'calendar',
    'cmd',
    'code',
    'codeop',
    'curses',
    'imaplib',
    'poplib',
    'smtplib',
    'telnetlib',
    'ftplib',
    'csv',
    'xml',
    'html',
    'antigravity',
    'this',
]

# Windows特定的排除项
if is_windows:
    excludes.extend([
        'readline',
        'termios',
        'tty',
        'pty',
        'fcntl',
        'grp',
        'pwd',
        'resource',
        'syslog',
    ])

a = Analysis(
    ['md-converter-gui\\main.py'],
    pathex=[],
    binaries=[],
    datas=datas,
    hiddenimports=hiddenimports,
    hookspath=[],
    hooksconfig={},
    runtime_hooks=[],
    excludes=excludes,
    noarchive=False,
    optimize=2,  # 最高级别的Python字节码优化
)

# 移除不需要的文件
def remove_unwanted_files(a):
    """移除不需要的文件以减小体积"""
    unwanted_patterns = [
        # 测试文件
        'test_', 'tests/', '_test',
        # 文档文件
        'README', 'CHANGELOG', 'LICENSE', 'COPYING',
        # 示例文件
        'example', 'demo', 'sample',
        # 开发文件
        '.pyi', '.pyx', '.pxd',
        # 语言文件（如果不需要国际化）
        'locale/',
    ]
    
    filtered_datas = []
    for dest, source, kind in a.datas:
        should_exclude = False
        for pattern in unwanted_patterns:
            if pattern in dest.lower() or pattern in source.lower():
                should_exclude = True
                break
        if not should_exclude:
            filtered_datas.append((dest, source, kind))
    
    a.datas = filtered_datas
    return a

# 应用文件过滤
a = remove_unwanted_files(a)

pyz = PYZ(a.pure, a.zipped_data, cipher=None)

exe = EXE(
    pyz,
    a.scripts,
    [],
    exclude_binaries=True,
    name='MdImgConverter',
    debug=False,
    bootloader_ignore_signals=False,
    strip=True,  # 启用符号剥离以减小体积
    upx=True,   # 启用 UPX 压缩
    console=False,  # 无控制台窗口
    disable_windowed_traceback=False,
    argv_emulation=False,
    target_arch=None,
    codesign_identity=None,
    entitlements_file=None,
    icon='pictures/app_icon.ico',
    version_file=None,  # 可以添加版本信息文件
)

coll = COLLECT(
    exe,
    a.binaries,
    a.datas,
    strip=True,   # 启用符号剥离
    upx=True,     # 启用 UPX 压缩
    upx_exclude=[
        # 不压缩的关键DLL，避免运行时错误
        'vcruntime140.dll',
        'vcruntime140_1.dll', 
        'msvcp140.dll',
        'python*.dll',
        'Qt6Core.dll',
        'Qt6Gui.dll',
        'Qt6Widgets.dll',
        # 避免压缩可能导致问题的库
        'api-ms-win-*.dll',
        'ucrtbase.dll',
    ],
    name='MdImgConverter',
)
