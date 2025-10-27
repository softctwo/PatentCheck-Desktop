#!/bin/bash
# PatentCheck-Desktop GUI 启动脚本 (macOS)

# 获取脚本所在目录
SCRIPT_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"
cd "$SCRIPT_DIR"

# 打印欢迎信息
echo "======================================"
echo "  PatentCheck-Desktop GUI 启动中..."
echo "======================================"
echo ""

# 检查Python环境
if ! command -v python3 &> /dev/null; then
    echo "❌ 错误: 未找到 Python 3"
    echo "请先安装 Python 3"
    read -p "按任意键退出..."
    exit 1
fi

# 检查依赖
echo "🔍 检查依赖..."
python3 -c "import PySide6" 2>/dev/null
if [ $? -ne 0 ]; then
    echo "⚠️  未安装 PySide6，正在安装..."
    pip3 install PySide6 Pillow python-docx reportlab
    if [ $? -ne 0 ]; then
        echo "❌ 依赖安装失败"
        read -p "按任意键退出..."
        exit 1
    fi
    echo "✅ 依赖安装完成"
fi

# 启动GUI
echo "🚀 启动应用..."
echo ""
python3 src/gui/main_window.py

# 退出信息
echo ""
echo "应用已关闭"
