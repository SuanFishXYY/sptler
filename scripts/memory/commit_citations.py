#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
算鱼圣人记忆 · 批量提交引用计数 (commit_citations.py)

Phase 5b 选"写入记忆"后，一次性提交所有圣人的 pending citations（避免逐人 re-run summon_sage）。
按 topic 对每位圣人重算相关记忆并 +1 citation_count + 重算 value_score，回写。

用法:
  # stdin: [{"sage":"王升","topic":"OA流水线"},{"sage":"卢若雨","topic":"OA流水线"}]
  echo '[{"sage":"王升","topic":"OA流水线"}]' | python scripts/memory/commit_citations.py --batch -
  python scripts/memory/commit_citations.py --sages 王升,卢若雨 --topic "OA流水线"
"""
import argparse, json, sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parent))
if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8")
    sys.stderr.reconfigure(encoding="utf-8")
import summon_sage as ss


def commit_one(sage, topic, mem_dir):
    """对一位圣人按 topic 重算相关记忆并提交 citation+1。"""
    p = ss.mem_path(sage, mem_dir)
    mem = ss.load_json(p)
    if not mem:
        return 0
    hits = ss.relevant_experiences(mem, topic)
    if not hits:
        return 0
    ss.bump_citations(mem, p, hits)  # bump_citations 内部会回写
    return len(hits)


def main():
    ap = argparse.ArgumentParser(description="批量提交圣人引用计数（Phase5b写入记忆后）")
    ap.add_argument("--batch", help="JSON数组 [{sage,topic},...]；- 为 stdin")
    ap.add_argument("--sages", help="圣人逗号分隔（配合 --topic）")
    ap.add_argument("--topic", default="")
    ap.add_argument("--mem-dir", default="")
    args = ap.parse_args()
    mem_dir = Path(args.mem_dir).expanduser().resolve() if args.mem_dir else ss.ROOT / "memories"

    items = []
    if args.batch:
        raw = sys.stdin.buffer.read().decode("utf-8-sig") if args.batch == "-" else Path(args.batch).read_text(encoding="utf-8")
        items = json.loads(raw)
    elif args.sages:
        items = [{"sage": n.strip(), "topic": args.topic} for n in args.sages.split(",") if n.strip()]

    if not items:
        ap.error("需要 --batch 或 --sages --topic")

    total = 0
    for it in items:
        sage = it.get("sage", "")
        topic = it.get("topic", "")
        if not sage:
            continue
        n = commit_one(sage, topic, mem_dir)
        if n:
            print(f"✅ {sage}: 提交 {n} 条 citation+1")
            total += n
        else:
            print(f"  {sage}: 无相关记忆可提交")
    print(f"\n共提交 {total} 条 citation。")


if __name__ == "__main__":
    main()
