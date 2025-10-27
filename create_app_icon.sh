#!/bin/bash
# 为 PatentCheck-Desktop 创建 macOS 应用图标

APP_NAME="PatentCheck"
SCRIPT_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"

# 创建临时 AppleScript 应用
osascript <<EOF
tell application "Finder"
    set appPath to POSIX file "$SCRIPT_DIR/launch_gui.command" as alias
    make new alias to appPath at desktop
    set name of result to "$APP_NAME"
end tell

display notification "快捷方式已创建到桌面" with title "PatentCheck-Desktop"
EOF

echo "✅ 应用快捷方式已创建到桌面"
echo "双击 '$APP_NAME' 即可启动"
