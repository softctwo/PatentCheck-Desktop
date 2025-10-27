#!/bin/bash
# PatentCheck 快速启动脚本

cd "$(dirname "$0")"

echo "🚀 正在启动 PatentCheck..."
python3 src/gui/main_window.py &

sleep 2

# 激活窗口
osascript -e 'tell application "System Events" to set frontmost of first process whose name contains "python3" to true' 2>/dev/null

echo "✅ 应用已启动"
echo "💡 如果看不到窗口，请检查其他桌面空间或按 Cmd+Tab 切换"
