@echo off
chcp 65001 > nul
echo ========================================
echo    MdImgConverter 优化版打包脚本
echo ========================================
echo.

:: 设置颜色
set GREEN=[92m
set RED=[91m
set YELLOW=[93m
set BLUE=[94m
set RESET=[0m

:: 检查Python环境
echo %BLUE%[1/6] 检查Python环境...%RESET%
python --version >nul 2>&1
if errorlevel 1 (
    echo %RED%错误: Python未安装或未添加到PATH%RESET%
    pause
    exit /b 1
)
echo %GREEN%✓ Python环境正常%RESET%
echo.

:: 检查PyInstaller
echo %BLUE%[2/6] 检查PyInstaller...%RESET%
python -c "import PyInstaller" >nul 2>&1
if errorlevel 1 (
    echo %YELLOW%正在安装PyInstaller...%RESET%
    pip install pyinstaller
    if errorlevel 1 (
        echo %RED%错误: PyInstaller安装失败%RESET%
        pause
        exit /b 1
    )
)
echo %GREEN%✓ PyInstaller已安装%RESET%
echo.

:: 检查UPX（可选）
echo %BLUE%[3/6] 检查UPX压缩工具...%RESET%
if exist "upx.exe" (
    echo %GREEN%✓ UPX已存在，将启用压缩%RESET%
) else (
    echo %YELLOW%! UPX未找到，将跳过压缩优化%RESET%
    echo   可从 https://upx.github.io/ 下载upx.exe放到项目根目录
)
echo.

:: 检查必要文件
echo %BLUE%[4/6] 检查必要文件...%RESET%
if not exist "MdImgConverter-optimized.spec" (
    echo %RED%错误: MdImgConverter-optimized.spec 文件不存在%RESET%
    pause
    exit /b 1
)
if not exist "md-converter-gui\main.py" (
    echo %RED%错误: md-converter-gui\main.py 文件不存在%RESET%
    pause
    exit /b 1
)
if not exist "pictures\app_icon.ico" (
    echo %RED%错误: pictures\app_icon.ico 图标文件不存在%RESET%
    pause
    exit /b 1
)
echo %GREEN%✓ 必要文件检查完成%RESET%
echo.

:: 清理旧构建
echo %BLUE%[5/6] 清理旧构建文件...%RESET%
if exist "build" (
    rmdir /s /q "build" 2>nul
    echo %GREEN%✓ 清理build目录%RESET%
)
if exist "dist" (
    rmdir /s /q "dist" 2>nul
    echo %GREEN%✓ 清理dist目录%RESET%
)
echo.

:: 开始打包
echo %BLUE%[6/6] 开始打包...%RESET%
echo 使用配置: MdImgConverter-optimized.spec
echo.

:: 记录开始时间
set start_time=%time%
echo 开始时间: %start_time%
echo.

:: 执行打包
pyinstaller MdImgConverter-optimized.spec --clean --noconfirm

:: 检查打包结果
if errorlevel 1 (
    echo.
    echo %RED%========================================%RESET%
    echo %RED%           打包失败！%RESET%
    echo %RED%========================================%RESET%
    echo.
    echo 可能的解决方案:
    echo 1. 检查依赖是否完整安装: pip install -r requirements.txt
    echo 2. 检查Python版本是否兼容（推荐3.8+）
    echo 3. 查看上方错误信息进行排查
    echo.
    pause
    exit /b 1
)

:: 记录结束时间
set end_time=%time%

:: 检查输出文件
if exist "dist\MdImgConverter\MdImgConverter.exe" (
    echo.
    echo %GREEN%========================================%RESET%
    echo %GREEN%           打包成功！%RESET%
    echo %GREEN%========================================%RESET%
    echo.
    echo 输出位置: dist\MdImgConverter\
    echo 主程序: MdImgConverter.exe
    echo.
    
    :: 显示文件大小
    echo 文件信息:
    dir "dist\MdImgConverter\MdImgConverter.exe" | findstr "MdImgConverter.exe"
    
    :: 显示总体积
    echo.
    echo 总体积统计:
    for /f %%i in ('dir "dist\MdImgConverter" /s /-c ^| find "个文件"') do echo %%i
    
    echo.
    echo 开始时间: %start_time%
    echo 结束时间: %end_time%
    echo.
    
    :: 询问是否运行测试
    set /p test_run="是否运行测试? (y/n): "
    if /i "%test_run%"=="y" (
        echo.
        echo %BLUE%启动测试...%RESET%
        cd dist\MdImgConverter
        start MdImgConverter.exe
        cd ..\..
    )
    
) else (
    echo.
    echo %RED%========================================%RESET%
    echo %RED%        打包完成但文件缺失！%RESET%
    echo %RED%========================================%RESET%
    echo.
    echo 请检查dist目录的内容
)

echo.
echo 按任意键退出...
pause >nul
