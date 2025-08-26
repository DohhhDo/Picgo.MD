#!/bin/bash
# MdImgConverter 优化版打包脚本 (Linux/macOS)

# 颜色定义
GREEN='\033[0;32m'
RED='\033[0;31m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

echo "========================================"
echo "   MdImgConverter 优化版打包脚本"
echo "========================================"
echo ""

# 检查Python环境
echo -e "${BLUE}[1/6] 检查Python环境...${NC}"
if ! command -v python3 &> /dev/null; then
    if ! command -v python &> /dev/null; then
        echo -e "${RED}错误: Python未安装或未添加到PATH${NC}"
        exit 1
    else
        PYTHON_CMD="python"
    fi
else
    PYTHON_CMD="python3"
fi

echo -e "${GREEN}✓ Python环境正常${NC}"
$PYTHON_CMD --version
echo ""

# 检查PyInstaller
echo -e "${BLUE}[2/6] 检查PyInstaller...${NC}"
if ! $PYTHON_CMD -c "import PyInstaller" &> /dev/null; then
    echo -e "${YELLOW}正在安装PyInstaller...${NC}"
    $PYTHON_CMD -m pip install pyinstaller
    if [ $? -ne 0 ]; then
        echo -e "${RED}错误: PyInstaller安装失败${NC}"
        exit 1
    fi
fi
echo -e "${GREEN}✓ PyInstaller已安装${NC}"
echo ""

# 检查UPX（可选）
echo -e "${BLUE}[3/6] 检查UPX压缩工具...${NC}"
if command -v upx &> /dev/null; then
    echo -e "${GREEN}✓ UPX已安装，将启用压缩${NC}"
elif [ -f "./upx" ]; then
    echo -e "${GREEN}✓ UPX已存在，将启用压缩${NC}"
else
    echo -e "${YELLOW}! UPX未找到，将跳过压缩优化${NC}"
    echo "  可通过包管理器安装: sudo apt install upx (Ubuntu) 或 brew install upx (macOS)"
fi
echo ""

# 检查必要文件
echo -e "${BLUE}[4/6] 检查必要文件...${NC}"
if [ ! -f "MdImgConverter-optimized.spec" ]; then
    echo -e "${RED}错误: MdImgConverter-optimized.spec 文件不存在${NC}"
    exit 1
fi
if [ ! -f "md-converter-gui/main.py" ]; then
    echo -e "${RED}错误: md-converter-gui/main.py 文件不存在${NC}"
    exit 1
fi
if [ ! -f "pictures/app_icon.ico" ]; then
    echo -e "${RED}错误: pictures/app_icon.ico 图标文件不存在${NC}"
    exit 1
fi
echo -e "${GREEN}✓ 必要文件检查完成${NC}"
echo ""

# 清理旧构建
echo -e "${BLUE}[5/6] 清理旧构建文件...${NC}"
if [ -d "build" ]; then
    rm -rf build
    echo -e "${GREEN}✓ 清理build目录${NC}"
fi
if [ -d "dist" ]; then
    rm -rf dist
    echo -e "${GREEN}✓ 清理dist目录${NC}"
fi
echo ""

# 开始打包
echo -e "${BLUE}[6/6] 开始打包...${NC}"
echo "使用配置: MdImgConverter-optimized.spec"
echo ""

# 记录开始时间
start_time=$(date +%s)
echo "开始时间: $(date)"
echo ""

# 执行打包
$PYTHON_CMD -m PyInstaller MdImgConverter-optimized.spec --clean --noconfirm

# 检查打包结果
if [ $? -ne 0 ]; then
    echo ""
    echo -e "${RED}========================================${NC}"
    echo -e "${RED}           打包失败！${NC}"
    echo -e "${RED}========================================${NC}"
    echo ""
    echo "可能的解决方案:"
    echo "1. 检查依赖是否完整安装: pip install -r requirements.txt"
    echo "2. 检查Python版本是否兼容（推荐3.8+）"
    echo "3. 查看上方错误信息进行排查"
    echo ""
    exit 1
fi

# 记录结束时间
end_time=$(date +%s)
duration=$((end_time - start_time))

# 检查输出文件
if [ -f "dist/MdImgConverter/MdImgConverter" ] || [ -f "dist/MdImgConverter/MdImgConverter.exe" ]; then
    echo ""
    echo -e "${GREEN}========================================${NC}"
    echo -e "${GREEN}           打包成功！${NC}"
    echo -e "${GREEN}========================================${NC}"
    echo ""
    echo "输出位置: dist/MdImgConverter/"
    echo "主程序: MdImgConverter"
    echo ""
    
    # 显示文件信息
    echo "文件信息:"
    ls -lh dist/MdImgConverter/MdImgConverter* 2>/dev/null || ls -lh dist/MdImgConverter/
    
    # 显示总体积
    echo ""
    echo "总体积统计:"
    du -sh dist/MdImgConverter/
    
    echo ""
    echo "开始时间: $(date -d @$start_time 2>/dev/null || date -r $start_time)"
    echo "结束时间: $(date -d @$end_time 2>/dev/null || date -r $end_time)"
    echo "耗时: ${duration}秒"
    echo ""
    
    # 询问是否运行测试
    read -p "是否运行测试? (y/n): " test_run
    if [ "$test_run" = "y" ] || [ "$test_run" = "Y" ]; then
        echo ""
        echo -e "${BLUE}启动测试...${NC}"
        cd dist/MdImgConverter
        if [ -f "MdImgConverter" ]; then
            ./MdImgConverter &
        elif [ -f "MdImgConverter.exe" ]; then
            wine MdImgConverter.exe &
        fi
        cd ../..
    fi
    
else
    echo ""
    echo -e "${RED}========================================${NC}"
    echo -e "${RED}        打包完成但文件缺失！${NC}"
    echo -e "${RED}========================================${NC}"
    echo ""
    echo "请检查dist目录的内容"
fi

echo ""
echo "脚本执行完成"
