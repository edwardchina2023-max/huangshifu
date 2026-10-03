#!/bin/bash
# ============================================================
# 一次性安装：让 Mac 每 30 分钟自动把云端 Word 同步到桌面
# 用法（在「终端」里粘贴运行）：
#   curl -fsSL https://raw.githubusercontent.com/edwardchina2023-max/huangshifu/claude/science-tech-daily-digest-t9guxa/scripts/mac/install_mac_sync.sh | bash
# 卸载：
#   launchctl unload ~/Library/LaunchAgents/com.huangshifu.radar-sync.plist && rm ~/Library/LaunchAgents/com.huangshifu.radar-sync.plist
# ============================================================
set -euo pipefail

REPO_URL="https://github.com/edwardchina2023-max/huangshifu.git"
BRANCH="claude/science-tech-daily-digest-t9guxa"
LOCAL_DIR="$HOME/.huangshifu-radar"
PLIST="$HOME/Library/LaunchAgents/com.huangshifu.radar-sync.plist"

# 1. 检查 git（macOS 首次使用会提示安装「命令行开发者工具」，点安装即可）
if ! command -v git >/dev/null 2>&1; then
  echo "未检测到 git，正在触发安装命令行开发者工具，安装完成后请重新运行本命令。"
  xcode-select --install || true
  exit 1
fi

# 2. 拉取仓库到隐藏目录
if [ ! -d "$LOCAL_DIR/.git" ]; then
  git clone --depth 1 --branch "$BRANCH" "$REPO_URL" "$LOCAL_DIR"
else
  git -C "$LOCAL_DIR" fetch --depth 1 origin "$BRANCH" && git -C "$LOCAL_DIR" reset --hard "origin/$BRANCH"
fi

# 3. 写入 launchd 定时任务：登录时运行一次，之后每 30 分钟一次
mkdir -p "$HOME/Library/LaunchAgents"
cat > "$PLIST" <<EOF
<?xml version="1.0" encoding="UTF-8"?>
<!DOCTYPE plist PUBLIC "-//Apple//DTD PLIST 1.0//EN" "http://www.apple.com/DTDs/PropertyList-1.0.dtd">
<plist version="1.0">
<dict>
  <key>Label</key><string>com.huangshifu.radar-sync</string>
  <key>ProgramArguments</key>
  <array>
    <string>/bin/bash</string>
    <string>$LOCAL_DIR/scripts/mac/sync_word_to_desktop.sh</string>
  </array>
  <key>StartInterval</key><integer>1800</integer>
  <key>RunAtLoad</key><true/>
  <key>StandardErrorPath</key><string>$HOME/Library/Logs/huangshifu-radar-sync.err.log</string>
</dict>
</plist>
EOF

launchctl unload "$PLIST" 2>/dev/null || true
launchctl load "$PLIST"

# 4. 立即同步一次
bash "$LOCAL_DIR/scripts/mac/sync_word_to_desktop.sh" || true

echo ""
echo "✅ 安装完成：Word 已同步到 桌面/实验室雷达，之后每 30 分钟自动检查一次。"
echo "   日志：~/Library/Logs/huangshifu-radar-sync.log"
