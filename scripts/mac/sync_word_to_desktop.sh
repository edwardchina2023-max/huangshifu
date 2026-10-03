#!/bin/bash
# ============================================================
# 实验室雷达 · Word 同步到 Mac 桌面
# 作用：从 GitHub 拉取云端生成的 .docx（早报 / 诺奖解读），
#       复制到 ~/Desktop/实验室雷达/，只复制新增或更新过的文件。
# 由 launchd 每 30 分钟自动运行一次（见 install_mac_sync.sh），
# 也可以手动运行：bash ~/.huangshifu-radar/scripts/mac/sync_word_to_desktop.sh
# ============================================================
set -euo pipefail

REPO_URL="https://github.com/edwardchina2023-max/huangshifu.git"
BRANCH="claude/science-tech-daily-digest-t9guxa"
LOCAL_DIR="$HOME/.huangshifu-radar"          # 隐藏的本地镜像，不占桌面
DEST_DIR="$HOME/Desktop/实验室雷达"
LOG_FILE="$HOME/Library/Logs/huangshifu-radar-sync.log"

log() { echo "[$(date '+%Y-%m-%d %H:%M:%S')] $*" >> "$LOG_FILE"; }

mkdir -p "$DEST_DIR" "$(dirname "$LOG_FILE")"

# 1. 首次运行：浅克隆指定分支；之后：只拉取该分支最新内容
if [ ! -d "$LOCAL_DIR/.git" ]; then
  if ! git clone --depth 1 --branch "$BRANCH" "$REPO_URL" "$LOCAL_DIR" >> "$LOG_FILE" 2>&1; then
    log "错误：克隆仓库失败（检查网络或 GitHub 登录）"
    exit 1
  fi
  log "首次克隆完成"
else
  if ! git -C "$LOCAL_DIR" fetch --depth 1 origin "$BRANCH" >> "$LOG_FILE" 2>&1; then
    log "错误：拉取失败（网络问题，下次自动重试）"
    exit 1
  fi
  git -C "$LOCAL_DIR" reset --hard "origin/$BRANCH" >> "$LOG_FILE" 2>&1
fi

# 2. 复制 Word：只复制桌面上没有、或云端版本更新的文件
SRC="$LOCAL_DIR/assets/files/word"
if [ ! -d "$SRC" ]; then
  log "提示：仓库中暂无 Word 目录"
  exit 0
fi

copied=0
for f in "$SRC"/*.docx; do
  [ -e "$f" ] || continue
  name="$(basename "$f")"
  if [ ! -e "$DEST_DIR/$name" ] || ! cmp -s "$f" "$DEST_DIR/$name"; then
    if cp "$f" "$DEST_DIR/$name" 2>> "$LOG_FILE"; then
      copied=$((copied + 1))
      log "已同步：$name"
    else
      # macOS 隐私保护可能禁止后台任务写桌面（Operation not permitted）
      log "错误：无法写入桌面。请到 系统设置 → 隐私与安全性 → 完全磁盘访问权限，添加 /bin/bash 后重试"
      exit 1
    fi
  fi
done

# 3. 有新文件时弹出系统通知
if [ "$copied" -gt 0 ]; then
  osascript -e "display notification \"新增/更新 $copied 份 Word，已放到桌面「实验室雷达」文件夹\" with title \"实验室雷达\"" 2>/dev/null || true
fi
log "本次检查完成，同步 $copied 个文件"
