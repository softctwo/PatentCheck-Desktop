#!/bin/bash
# 创建 macOS 应用包

APP_NAME="PatentCheck"
SCRIPT_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"
APP_DIR="$SCRIPT_DIR/$APP_NAME.app"

echo "🔨 创建 macOS 应用包..."

# 清理旧的应用包
if [ -d "$APP_DIR" ]; then
    echo "🗑️  删除旧的应用包..."
    rm -rf "$APP_DIR"
fi

# 创建应用包结构
echo "📁 创建应用包结构..."
mkdir -p "$APP_DIR/Contents/MacOS"
mkdir -p "$APP_DIR/Contents/Resources"

# 复制图标
if [ -f "$SCRIPT_DIR/resources/icons/app_icon.icns" ]; then
    cp "$SCRIPT_DIR/resources/icons/app_icon.icns" "$APP_DIR/Contents/Resources/AppIcon.icns"
    echo "✓ 图标已复制"
else
    echo "⚠️  未找到图标文件"
fi

# 创建启动脚本
cat > "$APP_DIR/Contents/MacOS/$APP_NAME" << 'EOF'
#!/bin/bash
# 获取可执行文件的真实路径
EXECUTABLE_PATH="$0"
while [ -L "$EXECUTABLE_PATH" ]; do
    EXECUTABLE_PATH=$(readlink "$EXECUTABLE_PATH")
done

# 获取项目根目录（.app的父目录）
APP_DIR=$(cd "$(dirname "$EXECUTABLE_PATH")/../../.." && pwd)
PROJECT_DIR="$APP_DIR"

# 如果在 /Applications 中，则使用源代码路径
if [[ "$APP_DIR" == /Applications* ]]; then
    PROJECT_DIR="$HOME/workspaces/PatentCheck-Desktop"
fi

cd "$PROJECT_DIR" || exit 1

# 启动Python应用
python3 src/gui/main_window.py 2>&1 | tee /tmp/patentcheck.log &
PYTHON_PID=$!

# 等待窗口启动
sleep 2

# 激活窗口
osascript -e 'tell application "System Events" to set frontmost of first process whose name contains "python3" to true' 2>/dev/null

# 等待进程结束
wait $PYTHON_PID
EOF

chmod +x "$APP_DIR/Contents/MacOS/$APP_NAME"
echo "✓ 启动脚本已创建"

# 创建 Info.plist
cat > "$APP_DIR/Contents/Info.plist" << EOF
<?xml version="1.0" encoding="UTF-8"?>
<!DOCTYPE plist PUBLIC "-//Apple//DTD PLIST 1.0//EN" "http://www.apple.com/DTDs/PropertyList-1.0.dtd">
<plist version="1.0">
<dict>
    <key>CFBundleDevelopmentRegion</key>
    <string>zh_CN</string>
    <key>CFBundleExecutable</key>
    <string>$APP_NAME</string>
    <key>CFBundleIconFile</key>
    <string>AppIcon</string>
    <key>CFBundleIdentifier</key>
    <string>com.patentcheck.desktop</string>
    <key>CFBundleInfoDictionaryVersion</key>
    <string>6.0</string>
    <key>CFBundleName</key>
    <string>PatentCheck</string>
    <key>CFBundlePackageType</key>
    <string>APPL</string>
    <key>CFBundleShortVersionString</key>
    <string>0.9</string>
    <key>CFBundleVersion</key>
    <string>1</string>
    <key>LSMinimumSystemVersion</key>
    <string>10.13</string>
    <key>NSHighResolutionCapable</key>
    <true/>
    <key>NSPrincipalClass</key>
    <string>NSApplication</string>
</dict>
</plist>
EOF

echo "✓ Info.plist 已创建"

echo ""
echo "✅ 应用包创建完成！"
echo "📍 位置: $APP_DIR"
echo ""
echo "使用方法："
echo "1. 双击 $APP_NAME.app 启动应用"
echo "2. 或将应用拖到 应用程序 文件夹"
echo ""
