#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
算鱼圣人记忆 · 导入导出 (memory_io.py)

- 导入：从外部文本（会议纪要/邮件/聊天记录摘要）补充某圣人的记忆。
        文本里每条用「议题:xxx | 立场:xxx | 建议:xxx」或自由文本，脚本解析成 experience。
- 导出：把某圣人的记忆画像+近期经历导出成可读 md，给同事看。

用法:
  # 导入：从文本文件补充王升记忆
  python scripts/memory_io.py import --sage 王升 --file notes.txt --topic "外部会议" --verdict 通过

  # 导入：从 stdin
  echo "议题:X | 立场:赞成 | 建议:做Y" | python scripts/memory_io.py import --sage 王升 --topic "外部" --verdict 通过

  # 导出：王升记忆画像 md
  python scripts/memory_io.py export --sage 王升 --out 王升记忆.md
"""
import argparse, json, sys, re
from pathlib import Path
from datetime import datetime
sys.path.insert(0, str(Path(__file__).resolve().parent))
if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8")
    sys.stderr.reconfigure(encoding="utf-8")
import record_memory as rm


def parse_lines(text: str, default_topic: str, default_verdict: str) -> list[dict]:
    """从文本解析经历。支持「议题:X|立场:Y|建议:Z」格式，或每行作为一条 ideas。"""
    exps = []
    for line in (text or "").splitlines():
        line = line.strip()
        if not line or line.startswith("#"):
            continue
        # 结构化格式
        m = re.match(r"议题[:：]\s*(.+?)\s*\|\s*立场[:：]\s*(.+?)(?:\s*\|\s*建议[:：]\s*(.+))?$", line)
        if m:
            exps.append({
                "topic": m.group(1).strip(),
                "stance": m.group(2).strip(),
                "recommendation": (m.group(3) or "").strip(),
                "ideas": "",
            })
            continue
        # 自由文本：作为一条 ideas
        exps.append({"topic": default_topic, "stance": "赞成", "recommendation": "", "ideas": line})
    return exps


def do_import(sage, text, topic, verdict, mem_dir):
    exps = parse_lines(text, topic, verdict)
    if not exps:
        print("（未解析到任何经历）")
        return
    for e in exps:
        e["verdict"] = verdict
        e["mode"] = "导入"
        e["meeting_id"] = "IMPORT-" + datetime.now().strftime("%Y%m%d%H%M%S")
        rm.MEM_DIR = mem_dir
        rm.record_one(sage, e, verbose=False)
    print(f"✅ 导入 {len(exps)} 条经历到 {sage} 记忆")


def do_export(sage, out_path, mem_dir):
    p = mem_dir / f"{sage}.json"
    if not p.exists():
        print(f"（{sage} 暂无记忆档案）")
        return
    mem = json.loads(p.read_text(encoding="utf-8"))
    prof = mem.get("profile", {})
    prof_r = mem.get("profile_recent", {})
    exps = mem.get("experiences", []) or []
    arch = mem.get("archive_summary", {}) or {}
    lines = [f"# {sage} · 记忆导出", "", f"> 导出时间：{datetime.now().strftime('%Y-%m-%d %H:%M')}", "", "## 长期画像（底色）"]
    lines.append(f"- 总议事：{prof.get('total_meetings',0)}次")
    lines.append(f"- 风险偏好：{prof.get('risk_tendency','未知')}")
    lines.append(f"- 专长焦点：{'、'.join(prof.get('specialty_focus',[]) or []) or '—'}")
    lines.append(f"- 立场分布：{prof.get('stances',{})}")
    lines += ["", "## 短期画像（近况·近30次）"]
    lines.append(f"- 风险偏好：{prof_r.get('risk_tendency','未知')}")
    lines.append(f"- 专长焦点：{'、'.join(prof_r.get('specialty_focus',[]) or []) or '—'}")
    fv = prof.get("frequent_views", []) or []
    if fv:
        lines += ["", "## 常提观点"]
        for v in fv[:10]:
            lines.append(f"- {v.get('text','')}（{v.get('count',1)}次）")
    lines += ["", "## 近期经历"]
    for e in exps[-15:]:
        lines.append(f"- {e.get('recorded_at','')} {e.get('topic','')}（{e.get('stance','')}）建议：{e.get('recommendation','')}")
    if arch:
        lines += ["", "## 归档摘要"]
        lines.append(f"- 已归档 {arch.get('compacted_count',0)} 条，删除 {arch.get('deleted_count',0)} 条")
    content = "\n".join(lines) + "\n"
    Path(out_path).write_text(content, encoding="utf-8")
    print(f"✅ 导出 {sage} 记忆到 {out_path}（{len(exps)}条经历）")


def main():
    ap = argparse.ArgumentParser(description="圣人记忆导入导出")
    sub = ap.add_subparsers(dest="cmd")
    pi = sub.add_parser("import", help="从文本导入补充记忆")
    pi.add_argument("--sage", required=True)
    pi.add_argument("--file", default="", help="文本文件；不填则 stdin")
    pi.add_argument("--topic", default="外部导入")
    pi.add_argument("--verdict", default="通过")
    pi.add_argument("--mem-dir", default="")
    pe = sub.add_parser("export", help="导出某圣人记忆为 md")
    pe.add_argument("--sage", required=True)
    pe.add_argument("--out", required=True)
    pe.add_argument("--mem-dir", default="")
    args = ap.parse_args()

    mem_dir = Path(args.mem_dir).expanduser().resolve() if args.mem_dir else rm.MEM_DIR

    if args.cmd == "import":
        text = Path(args.file).read_text(encoding="utf-8") if args.file else sys.stdin.buffer.read().decode("utf-8-sig")
        do_import(args.sage, text, args.topic, args.verdict, mem_dir)
    elif args.cmd == "export":
        do_export(args.sage, args.out, mem_dir)
    else:
        ap.print_help()


if __name__ == "__main__":
    main()
