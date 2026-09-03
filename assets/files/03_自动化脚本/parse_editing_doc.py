#!/usr/bin/env python3
"""
Parse 非常深科技6月29 docx — extract editing instructions.
Uses explicit markup: DELETE blocks mark removal, MOVE blocks mark relocation.
Everything outside marked blocks = keep.
"""
import json, re
from docx import Document

doc_path = "/Users/huangshifu/Library/Containers/com.tencent.xinWeChat/Data/Documents/xwechat_files/edward704952_1cef/msg/file/2026-06/非常深科技6月29苏俊老师访谈_10分钟内原稿删改移动标记版.docx"

doc = Document(doc_path)

segments = []
in_block = False
block_op = None
block_reason = ""

for para in doc.paragraphs:
    text = para.text.strip()
    if not text:
        continue

    # Detect block start
    if "DELETE" in text and "删除开始" in text:
        in_block = True
        block_op = "delete"
        m = re.search(r'删除开始[｜\|](.*?)(?:】|$)', text)
        block_reason = m.group(1) if m else ""
        continue
    if "MOVE" in text and "移动开始" in text:
        in_block = True
        block_op = "move"
        m = re.search(r'移动开始[｜\|](.*?)(?:】|$)', text)
        block_reason = m.group(1) if m else ""
        continue

    # Detect block end
    if "END" in text and ("删除结束" in text or "移动结束" in text):
        in_block = False
        block_op = None
        block_reason = ""
        continue

    # Parse numbered paragraph
    m = re.match(r'^(\d{4})\s+(.*)', text)
    if not m:
        continue

    para_num = m.group(1)
    content = m.group(2)

    op = block_op if in_block else "keep"
    reason = block_reason if in_block else ""

    seg = {"num": para_num, "text": content, "operation": op, "reason": reason}

    if op == "move" or "[移动" in content:
        seg["operation"] = "move"
        tgt = re.search(r'移至(.*?)(?:】|$)', content)
        seg["move_target"] = tgt.group(1) if tgt else ""

    segments.append(seg)

# Build groups
groups = []
cur = None
for s in segments:
    op = s["operation"]
    if cur is None or cur["operation"] != op:
        if cur:
            groups.append(cur)
        cur = {
            "operation": op,
            "reason": s.get("reason", ""),
            "start_num": s["num"],
            "end_num": s["num"],
            "count": 0,
            "text_preview": s["text"][:80],
        }
    cur["end_num"] = s["num"]
    cur["count"] += 1
if cur:
    groups.append(cur)

stats = {
    "total": len(segments),
    "keep": sum(1 for s in segments if s["operation"] == "keep"),
    "delete": sum(1 for s in segments if s["operation"] == "delete"),
    "move": sum(1 for s in segments if s["operation"] == "move"),
}

out = {"stats": stats, "groups": groups, "segments": segments}
out_path = "/Users/huangshifu/Desktop/claude code/editing_plan.json"
with open(out_path, "w", encoding="utf-8") as f:
    json.dump(out, f, ensure_ascii=False, indent=2)

print(f"Segments: {stats['total']} | keep={stats['keep']} delete={stats['delete']} move={stats['move']}")
print(f"Groups: {len(groups)}")
for g in groups:
    rng = f"{g['start_num']}-{g['end_num']}"
    print(f"  [{g['operation']:6s}] {rng:14s} ({g['count']:3d}) | {g['text_preview'][:70]}")
print(f"Output: {out_path}")
