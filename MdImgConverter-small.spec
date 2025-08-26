# -*- mode: python ; coding: utf-8 -*-
# 小体积版本的打包配置

a = Analysis(
    ['md-converter-gui\\main.py'],
    pathex=[],
    binaries=[],
    datas=[
        ('pictures', 'pictures'),
        ('image', 'image'),
        ('imarkdown', 'imarkdown'),
    ],
    hiddenimports=[
        'qcloud_cos',
        'qiniu', 
        'boto3',
        'botocore',
        'urllib3',
    ],
    hookspath=[],
    hooksconfig={},
    runtime_hooks=[],
    excludes=[
        # PyQt6 不需要的模块
        'PyQt6.QtQml',
        'PyQt6.QtWebEngineCore', 
        'PyQt6.QtWebEngineWidgets',
        'PyQt6.QtNetwork',
        'PyQt6.QtTest',
        'PyQt6.QtSql',
        'PyQt6.QtMultimedia',
        'PyQt6.QtChart',
        'PyQt6.QtBluetooth',
        'PyQt6.QtNfc',
        'PyQt6.QtPositioning',
        'PyQt6.QtSensors',
        'PyQt6.QtSerialPort',
        'PyQt6.QtWebChannel',
        # 科学计算库
        'matplotlib',
        'numpy',
        'scipy', 
        'pandas',
        # 开发工具
        'jupyter',
        'notebook',
        'ipython',
        'pdb',
        'pydoc',
        'unittest',
        'doctest',
        # GUI 库
        'tkinter',
        'tk',
        'tcl',
        # 网络和数据库
        'sqlite3',
        'xmlrpc',
        'html',
        # 打包工具
        'setuptools', 
        'pip',
        'wheel',
        # 其他
        'difflib',
        'qtawesome',
    ],
    noarchive=False,
    optimize=2,
)

pyz = PYZ(a.pure, a.zipped_data, cipher=None)

exe = EXE(
    pyz,
    a.scripts,
    [],
    exclude_binaries=True,
    name='MdImgConverter',
    debug=False,
    bootloader_ignore_signals=False,
    strip=True,  # 启用符号剥离
    upx=True,   # 启用 UPX 压缩
    console=False,
    disable_windowed_traceback=False,
    argv_emulation=False,
    target_arch=None,
    codesign_identity=None,
    entitlements_file=None,
    icon='pictures/app_icon.ico',
)

coll = COLLECT(
    exe,
    a.binaries,
    a.datas,
    strip=True,   # 启用符号剥离
    upx=True,     # 启用 UPX 压缩
    upx_exclude=[
        'vcruntime140.dll',  # 不压缩系统DLL
        'python*.dll',
        'Qt6*.dll',
    ],
    name='MdImgConverter',
)
