#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
算鱼议会 · 会议索引器 (index_meeting.py)

把正式会议/续议登记到 sptler-meetings/index.json，供后续续议读取。

用法:
  python scripts/index_meeting.py --meeting-id SPTLER-xxx --topic "..." --result-file path.md --attendees 王升,张鑫 --action-items actions.json
  python scripts/index_meeting.py --batch meeting_index.json
  python scripts/index_meeting.py --list
"""
import argparse
import json
import sys
from pathlib import Path
from datetime import datetime

if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8")
    sys.stderr.reconfigure(encoding="utf-8")


def default_meetings_dir() -> Path:
    return Path.cwd() / "sptler-meetings"


def index_path(meetings_dir: Path) -> Path:
    return meetings_dir / "index.json"


def load_index(meetings_dir: Path) -> list[dict]:
    p = index_path(meetings_dir)
    if not p.exists():
        return []
    try:
        data = json.loads(p.read_text(encoding="utf-8"))
        return data if isinstance(data, list) else []
    except Exception:
        return []


def save_index(meetings_dir: Path, entries: list[dict]):
    meetings_dir.mkdir(parents=True, exist_ok=True)
    index_path(meetings_dir).write_text(json.dumps(entries, ensure_ascii=False, indent=2), encoding="utf-8")


def normalize_entry(data: dict) -> dict:
    mid = data.get("meeting_id") or "SPTLER-" + datetime.now().strftime("%Y%m%d%H%M%S")
    return {
        "meeting_id": mid,
        "meeting_type": data.get("meeting_type") or "regular",
        "parent_meeting_id": data.get("parent_meeting_id") or "",
        "followup_type": data.get("followup_type") or "",
        "followup_target": data.get("followup_target") or "",
        "topic": data.get("topic") or "",
        "mode": data.get("mode") or "",
        "verdict": data.get("verdict") or "",
        "result_file": data.get("result_file") or "",
        "deliverable_file": data.get("deliverable_file") or "",
        "deliver_dir": data.get("deliver_dir") or "",
        "summary_file": data.get("summary_file") or "",
        "transcript_file": data.get("transcript_file") or "",
        "attendees": data.get("attendees") or [],
        "action_items": data.get("action_items") or [],
        "created_at": data.get("created_at") or datetime.now().strftime("%Y-%m-%d %H:%M"),
    }


def upsert(entries: list[dict], entry: dict) -> list[dict]:
    entries = [e for e in entries if e.get("meeting_id") != entry["meeting_id"]]
    entries.append(entry)
    entries.sort(key=lambda e: e.get("created_at", ""))
    return entries


def main():
    ap = argparse.ArgumentParser(description="登记/查询算鱼议会会议索引")
    ap.add_argument("--meetings-dir", default="", help="sptler-meetings 目录（默认当前工作目录/sptler-meetings）")
    ap.add_argument("--batch", help="从 JSON 文件读取完整 entry；传 - 表示 stdin")
    ap.add_argument("--list", action="store_true", help="列出会议索引")
    ap.add_argument("--last", action="store_true", help="输出最后一次会议 JSON")
    ap.add_argument("--meeting-id", help="会议ID")
    ap.add_argument("--topic", help="议题")
    ap.add_argument("--mode", default="", help="会议模式")
    ap.add_argument("--verdict", default="", help="通过/否决/小修/等")
    ap.add_argument("--result-file", default="", help="结果md路径")
    ap.add_argument("--summary-file", default="", help="纪要md路径")
    ap.add_argument("--transcript-file", default="", help="过程md路径")
    ap.add_argument("--attendees", default="", help="与会者，逗号分隔")
    args = ap.parse_args()

    meetings_dir = Path(args.meetings_dir).expanduser().resolve() if args.meetings_dir else default_meetings_dir()
    entries = load_index(meetings_dir)

    if args.list:
        if not entries:
            print("（暂无会议索引）")
            return
        for e in entries[-20:]:
            print(f"{e.get('meeting_id')} | {e.get('meeting_type')} | {e.get('topic')} | {e.get('result_file')}")
        return

    if args.last:
        print(json.dumps(entries[-1] if entries else {}, ensure_ascii=False, indent=2))
        return

    if args.batch:
        raw = sys.stdin.buffer.read().decode("utf-8-sig") if args.batch == "-" else Path(args.batch).read_text(encoding="utf-8")
        data = json.loads(raw)
    else:
        data = {
            "meeting_id": args.meeting_id,
            "topic": args.topic,
            "mode": args.mode,
            "verdict": args.verdict,
            "result_file": args.result_file,
            "summary_file": args.summary_file,
            "transcript_file": args.transcript_file,
            "attendees": [x.strip() for x in args.attendees.split(",") if x.strip()],
        }

    entry = normalize_entry(data)
    entries = upsert(entries, entry)
    save_index(meetings_dir, entries)
    print(f"✅ 已登记会议：{entry['meeting_id']} → {index_path(meetings_dir)}")


if __name__ == "__main__":
    main()
