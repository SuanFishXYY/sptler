#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
算鱼议会 · 续议上下文读取器 (continue_meeting.py)

根据会议索引读取上一次会议或指定会议，输出续议上下文：
原议题、结果文件、行动项、与会者、续议目标。

用法:
  python scripts/output/continue_meeting.py --last --item 3
  python scripts/output/continue_meeting.py --meeting-id SPTLER-xxx --sage 徐奕阳
  python scripts/output/continue_meeting.py --last --target "权限风险"
"""
import argparse
import json
import sys
from pathlib import Path

if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8")
    sys.stderr.reconfigure(encoding="utf-8")


def default_meetings_dir() -> Path:
    return Path.cwd() / "sptler-meetings"


def load_index(meetings_dir: Path) -> list[dict]:
    p = meetings_dir / "index.json"
    if not p.exists():
        return []
    try:
        data = json.loads(p.read_text(encoding="utf-8"))
    except Exception:
        return []
    if not isinstance(data, list):
        return []
    # 只保留 dict 条目：index.json 是用户可编辑文件，可能混入非 dict 元素，
    # 直接 .get 会致 AttributeError 崩溃（与记忆目录遍历脚本同源 bug 类）。
    return [e for e in data if isinstance(e, dict)]


def choose_entry(entries: list[dict], meeting_id: str = "", last: bool = False) -> dict:
    if meeting_id:
        return next((e for e in entries if e.get("meeting_id") == meeting_id), {})
    return entries[-1] if last and entries else {}


def main():
    ap = argparse.ArgumentParser(description="读取续议上下文")
    ap.add_argument("--meetings-dir", default="", help="sptler-meetings目录")
    ap.add_argument("--meeting-id", default="", help="指定原会议ID")
    ap.add_argument("--last", action="store_true", help="使用最近一次会议")
    ap.add_argument("--item", type=int, default=0, help="行动项编号(1-based)")
    ap.add_argument("--sage", default="", help="点名圣人")
    ap.add_argument("--target", default="", help="续议对象/风险点/方案")
    ap.add_argument("--json", action="store_true", help="JSON输出")
    args = ap.parse_args()

    meetings_dir = Path(args.meetings_dir).expanduser().resolve() if args.meetings_dir else default_meetings_dir()
    entries = load_index(meetings_dir)
    entry = choose_entry(entries, args.meeting_id, args.last)
    if not entry:
        print("（未找到会议索引；请先运行 index_meeting.py 登记会议，或指定 --meeting-id）")
        sys.exit(1)

    action = None
    if args.item:
        items = entry.get("action_items") or []
        if 1 <= args.item <= len(items):
            action = items[args.item - 1]

    ctx = {
        "parent_meeting_id": entry.get("meeting_id", ""),
        "parent_topic": entry.get("topic", ""),
        "parent_result_file": entry.get("result_file", ""),
        "parent_verdict": entry.get("verdict", ""),
        "attendees": entry.get("attendees", []),
        "target": args.target or (f"行动项{args.item}" if args.item else (args.sage or "")),
        "target_sage": args.sage,
        "action_item": action,
        "lite": bool(entry.get("lite")),  # 原会议是否 lite——续议据此走精简（≤3人，不重跑四律）
    }

    if args.json:
        print(json.dumps(ctx, ensure_ascii=False, indent=2))
        return

    print(f"【续议上下文】原会议：{ctx['parent_meeting_id']}")
    if ctx["lite"]:
        print("· ⚡ 原会议为 lite 模式——续议走精简（≤3人，不重跑四律，零 AskUser）")
    print(f"· 原议题：{ctx['parent_topic']}")
    print(f"· 原结论：{ctx['parent_verdict']}")
    print(f"· 结果文件：{ctx['parent_result_file'] or '（未登记）'}")
    if ctx["target"]:
        print(f"· 续议对象：{ctx['target']}")
    if ctx["target_sage"]:
        print(f"· 点名圣人：{ctx['target_sage']}")
    if action:
        print("· 行动项：" + json.dumps(action, ensure_ascii=False))
    print("· 原与会：" + "、".join(ctx["attendees"]))


if __name__ == "__main__":
    main()
