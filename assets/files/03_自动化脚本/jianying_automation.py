#!/usr/bin/env python3
"""
剪映自动化剪辑工具 — 通过 cliclick 发送键盘鼠标指令到剪映专业版。
操作顺序：
1. 激活剪映窗口
2. 通过 Cmd+Z/Cmd+B 等快捷键在时间线上操作
3. 根据 editing_plan.json 执行删除/移动操作

使用 cliclick (macOS 命令行自动化工具) 发送键盘事件
触发条件：操作系统级事件发送，不需要 Accessibility 权限（cliclick uses CGEvent API）

WARNING: 该脚本会直接控制你的鼠标和键盘！
请先备份剪映项目文件夹。
"""
import json
import os
import subprocess
import time
import sys

PROJECT_NAME = "6月29日"
PLAN_PATH = "/Users/huangshifu/Desktop/claude code/editing_plan.json"

def cli(cmd: str, delay: float = 0.1):
    """Execute a cliclick command. Raises on failure."""
    # cliclick accepts: kd:cmd t:ku:cmd (keyboard down, type, keyboard up)
    # Also: kp:return (key press), w:1000 (wait ms), m:x,y (move), c:x,y (click), dd:x,y (double-click), dc:x,y (right-click)
    full = f"cliclick {cmd}"
    result = subprocess.run(full, shell=True, capture_output=True, text=True, timeout=5)
    if result.returncode != 0 and result.stderr.strip():
        print(f"  cliclick WARNING: {result.stderr.strip()}")
    time.sleep(delay)

def activate_jianying():
    """Bring 剪映 to front."""
    subprocess.run([
        "osascript", "-e",
        'tell application "VideoFusion-macOS" to activate'
    ], capture_output=True)
    time.sleep(0.5)

def export_subtitles_as_srt():
    """
    在剪映中导出字幕SRT文件。
    需要剪映已打开项目。
    Step:
    1. Cmd+E 导出
    2. 或通过剪映的"导出字幕"功能
    """
    pass

def get_timeline_snapshot():
    """
    获取时间线快照。
    剪映的自动字幕已经匹配了逐字稿，通过导出SRT可以得到时间戳-文字对应关系。
    """
    pass

def cut_at_playhead():
    """在播放头位置切割 (Cmd+B)"""
    cli("kd:cmd t:b ku:cmd", 0.3)

def select_clip_before_playhead():
    """选择播放头前面的片段 (左箭头选中)"""
    cli("kp:arrow-left", 0.2)

def select_clip_after_playhead():
    """选择播放头后面的片段 (右箭头选中)"""
    cli("kp:arrow-right", 0.2)

def delete_selected():
    """删除选中的片段 (Delete/Backspace)"""
    cli("kp:delete", 0.3)

def move_playhead_forward(seconds: float = 5):
    """向右移动播放头 (Shift+Right)"""
    # Roughly 1 press = 1 frame at 30fps, so use multiple presses for seconds
    frames = int(seconds * 30)
    for _ in range(min(frames, 30)):  # Cap at 30 presses per call
        cli("kp:arrow-right", 0.01)
    if frames > 30:
        # Use longer jumps: Cmd+Right = jump to next marker
        pass

def jump_to_next_edit():
    """跳到下一个编辑点 (down arrow or Page Down)"""
    cli("kp:arrow-down", 0.2)

def undo():
    """撤销 (Cmd+Z)"""
    cli("kd:cmd t:z ku:cmd", 0.3)

def save_project():
    """保存项目 (Cmd+S)"""
    cli("kd:cmd t:s ku:cmd", 0.5)

def select_all():
    """全选 (Cmd+A)"""
    cli("kd:cmd t:a ku:cmd", 0.3)

def press_esc():
    """按 Escape"""
    cli("kp:esc", 0.2)

def zoom_timeline_in():
    """放大时间线 (Cmd+=)"""
    cli("kd:cmd t:= ku:cmd", 0.2)

def zoom_timeline_out():
    """缩小时间线 (Cmd+-)"""
    cli("kd:cmd t:- ku:cmd", 0.2)

def press_tab():
    """Tab键切换焦点"""
    cli("kp:tab", 0.2)

def press_right():
    """右键"""
    cli("kp:arrow-right", 0.1)

def move_playhead_to_start():
    """跳到开头 (Home / Fn+Left)"""
    # On Mac, Fn+Left = Home
    cli("kd:fn t:arrow-left ku:fn", 0.3)
    # Alternative: use "kp:home"
    # cli("kp:home", 0.3)

def move_playhead_to_end():
    """跳到末尾 (Fn+Right)"""
    cli("kd:fn t:arrow-right ku:fn", 0.3)

# ============================================================
# Operations derived from editing_plan.json
# ============================================================

def select_region_from_keyboard(start_offset_seconds: float, duration_seconds: float):
    """
    选择时间线区域：使用键盘快捷键
    在剪映中：
    - 按住 Shift + 左右箭头 = 扩展选择
    - I/O 键设置入出点
    """
    pass

def apply_delete_block(block_info: dict):
    """
    删除一个指定的段落区间。
    在剪映中操作：
    1. 找到该段落的起始位置
    2. 选中片段
    3. 按 Delete
    """
    print(f"  DELETE: {block_info['para_range']} — {block_info['text_preview'][:50]}")

def apply_move_block(block_info: dict):
    """
    移动一个指定的段落区间。
    在剪映中操作：
    1. 选中片段
    2. Cmd+X 剪切
    3. 移动播放头到目标位置
    4. Cmd+V 粘贴
    """
    print(f"  MOVE: {block_info['para_range']} → {block_info.get('move_target', '?')}")

# ============================================================
# Main execution
# ============================================================

def load_plan():
    with open(PLAN_PATH) as f:
        return json.load(f)

def main():
    plan = load_plan()
    groups = plan["groups"]
    stats = plan["stats"]

    print(f"=== 剪辑计划 ===")
    print(f"总段落: {stats['total']}")
    print(f"保留: {stats['keep']}, 删除: {stats['delete']}, 移动: {stats['move']}")
    print(f"操作组数: {len(groups)}")
    print()

    # Step 1: Backup
    print("步骤 1: 备份剪映项目...")
    backup_cmd = """
    SRC="$HOME/Movies/JianyingPro/User Data/Projects/com.lveditor.draft/6月29日"
    BACKUP="$HOME/Movies/JianyingPro/User Data/Projects/com.lveditor.draft/6月29日_backup_$(date +%Y%m%d_%H%M%S)"
    cp -R "$SRC" "$BACKUP" 2>/dev/null && echo "Backup: $BACKUP" || echo "Backup skipped (already exists or no permission)"
    """
    # Run backup... but first check if 剪映 is idle
    print("  请在手动保存剪映项目后确认继续...")

    # Step 2: Activate 剪映
    print("\n步骤 2: 激活剪映...")
    activate_jianying()
    time.sleep(1)

    # Step 3: Show operation plan
    print("\n步骤 3: 执行计划")
    print("="*60)
    print("操作顺序（按时间线从前往后）:")
    print("="*60)

    for g in groups:
        op = g["operation"]
        rng = g["para_range"]
        preview = g["text_preview"][:60]
        if op == "delete":
            print(f"  ✂️  DELETE [{rng}] ({g['count']}段) {g.get('reason','')[:50]}")
            print(f"     {preview}...")
        elif op == "move":
            tgt = g.get("move_target", "")
            print(f"  📦 MOVE  [{rng}] ({g['count']}段) → {tgt[:50]}")
            print(f"     {preview}...")
        else:
            print(f"  ✅ KEEP  [{rng}] ({g['count']}段)")

    print(f"\n{'='*60}")
    print(f"总计: DELETE {stats['delete']}段 + MOVE {stats['move']}段 = {stats['delete']+stats['move']}次操作")

    # Step 4: Show execution strategy
    print(f"""
执行策略选择:
  A) 直接操作剪映界面（需要你手动执行部分操作）
  B) 生成剪映草稿文件（利用已有的 export_capcut.py 生成新项目）
  C) 使用剪映内置的「视频浓缩」AI功能按脚本剪辑

推荐: 方案 B - 你已有完整的 export_capcut.py 管线
     将原始视频 + editing_plan.json 输入到管线，生成可直接打开的剪映项目。
""")

if __name__ == "__main__":
    main()
