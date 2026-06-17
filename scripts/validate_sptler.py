#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
算鱼议会技能自检 (validate_sptler.py)

检查 frontmatter、引用文件、脚本语法和关键规则残留。
用法: python scripts/validate_sptler.py
"""
import py_compile
import re
import sys
from pathlib import Path

try:
    import yaml
except ImportError:
    yaml = None

if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8")
    sys.stderr.reconfigure(encoding="utf-8")

ROOT = Path(__file__).resolve().parent.parent

REQUIRED = [
    "SKILL.md",
    "references/roster.md",
    "references/philosophy.md",
    "references/orglaw.md",
    "references/templates.md",
    "references/saints.registry.json",
    "references/routing_rules.json",
    "scripts/generate_saints.py",
    "scripts/read_soul.py",
    "scripts/summon_sage.py",
    "scripts/update_growth.py",
    "scripts/build_relations.py",
    "scripts/validate_saints.py",
    "scripts/record_memory.py",
    "scripts/read_memory.py",
    "scripts/list_memories.py",
    "scripts/route_sages.py",
    "scripts/index_meeting.py",
    "scripts/continue_meeting.py",
    "scripts/compact_memories.py",
]

KEYWORDS = [
    "/sptler!",
    "Phase 0.5",
    "加权投票",
    "[姓名]",
    "record_memory",
    "read_memory",
    "read_soul",
    "summon_sage",
    "update_growth",
    "build_relations",
    "routing_rules.json",
    "saints.registry.json",
    "route_sages",
    "index_meeting",
    "continue_meeting",
    "meeting_type=followup",
    "快速轨",
    "正式轨",
    "续议轨",
    "议会到此结束",
    "续议到此结束",
]

BAD_PATTERNS = ["±0.5", "完整五阶段", "3/4", "4/4", "the three output templates"]


def ok(label):
    print(f"✅ {label}")


def bad(label):
    print(f"❌ {label}")


def main():
    failed = 0
    print("== 文件存在 ==")
    for f in REQUIRED:
        if (ROOT / f).exists(): ok(f)
        else:
            bad(f); failed += 1

    print("\n== SKILL frontmatter ==")
    skill = (ROOT / "SKILL.md").read_text(encoding="utf-8")
    m = re.match(r"^---\n(.*?)\n---", skill, re.S)
    if not m:
        bad("frontmatter 缺失"); failed += 1
    else:
        if yaml:
            fm = yaml.safe_load(m.group(1))
            allowed = {"name", "description", "license", "allowed-tools", "metadata"}
            extra = set(fm.keys()) - allowed
            checks = [
                (not extra, f"无非法字段 {extra}"),
                (fm.get("name") == "sptler", "name=sptler"),
                (len(fm.get("description", "")) <= 1024, "description<=1024"),
                ("<" not in fm.get("description", "") and ">" not in fm.get("description", ""), "description无尖括号"),
            ]
            for passed, label in checks:
                if passed: ok(label)
                else: bad(label); failed += 1
        body = skill[m.end():]
        if len(body.split()) <= 5000: ok(f"body<=5000词 ({len(body.split())})")
        else: bad(f"body过长 ({len(body.split())})"); failed += 1

    print("\n== 关键能力关键词 ==")
    all_text = "\n".join((ROOT / f).read_text(encoding="utf-8") for f in ["SKILL.md", "references/orglaw.md", "references/templates.md"])
    for k in KEYWORDS:
        if k in all_text: ok(k)
        else: bad(k); failed += 1

    print("\n== 旧规则残留 ==")
    for p in BAD_PATTERNS:
        if p in all_text:
            bad(f"发现残留: {p}"); failed += 1
        else:
            ok(f"无残留: {p}")

    print("\n== 脚本语法 ==")
    for p in sorted((ROOT / "scripts").glob("*.py")):
        try:
            py_compile.compile(str(p), doraise=True)
            ok(p.name)
        except Exception as e:
            bad(f"{p.name}: {e}"); failed += 1

    print("\n== 结果 ==")
    if failed:
        print(f"❌ 自检失败：{failed} 项")
        sys.exit(1)
    print("✅ 全部通过")


if __name__ == "__main__":
    main()
