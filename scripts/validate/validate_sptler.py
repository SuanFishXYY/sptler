#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
算鱼议会技能自检 (validate_sptler.py)

检查 frontmatter、引用文件、脚本语法和关键规则残留。
用法: python scripts/validate/validate_sptler.py
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

ROOT = Path(__file__).resolve().parent.parent.parent

REQUIRED = [
    "SKILL.md",
    "references/saints/roster.md",
    "references/core/philosophy.md",
    "references/core/orglaw.md",
    "references/templates/templates.md",
    "references/saints/saints.registry.json",
    "references/scenarios/routing_rules.json",
    "references/core/runtime.md",
    "references/memory/memory_philosophy.md",
    "references/scenarios/scenarios.md",
    "scripts/saints/generate_saints.py",
    "scripts/memory/read_soul.py",
    "scripts/memory/summon_sage.py",
    "scripts/memory/update_growth.py",
    "scripts/memory/build_relations.py",
    "scripts/validate/validate_saints.py",
    "scripts/routing/sptler_run.py",
    "scripts/routing/sptler_prelude.py",
    "scripts/output/briefing.py",
    "scripts/output/action_board.py",
    "scripts/memory/memory_io.py",
    "scripts/memory/commit_citations.py",
    "scripts/routing/auto_invite.py",
    "scripts/memory/watch_memory.py",
    "scripts/memory/record_memory.py",
    "scripts/memory/read_memory.py",
    "scripts/saints/list_memories.py",
    "scripts/routing/route_sages.py",
    "scripts/output/index_meeting.py",
    "scripts/output/continue_meeting.py",
    "scripts/memory/compact_memories.py",
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
    "verdict",
    "单圣人裁决",
    "交付物",
    "查新检索",
    "FTO",
    "价值评估",
    "Cite memory",
    "watch_memory",
    "deliver_dir",
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
    all_text = "\n".join((ROOT / f).read_text(encoding="utf-8") for f in ["SKILL.md", "references/core/orglaw.md", "references/templates/templates.md"])
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
    for p in sorted((ROOT / "scripts").rglob("*.py")):
        try:
            py_compile.compile(str(p), doraise=True)
            ok(str(p.relative_to(ROOT)))
        except Exception as e:
            bad(f"{p.name}: {e}"); failed += 1

    print("\n== 运行时自检（RULES/场景/路由）==")
    import importlib.util
    # 加载 route_sages
    rs_path = ROOT / "scripts" / "routing" / "route_sages.py"
    if rs_path.exists():
        spec = importlib.util.spec_from_file_location("route_sages", rs_path)
        rs = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(rs)
        # 检查 RULES 非空
        if rs.RULES:
            ok(f"RULES 加载成功 ({len(rs.RULES)} 顶层键)")
        else:
            bad("RULES 加载为空 — routing_rules.json 路径错误或文件损坏"); failed += 1
        # 检查场景识别
        scenarios = rs.RULES.get("scenarios", {})
        if scenarios:
            ok(f"场景配置加载成功 ({len(scenarios)} 场景)")
        else:
            bad("场景配置为空 — routing_rules.json §scenarios 缺失"); failed += 1
        # 逐场景测试识别
        test_cases = {
            "查新检索": "蓝牙AOA查新颖性",
            "FTO检索": "蓝牙模组FTO侵权风险",
            "专利价值评估": "这批专利值不值钱",
            "OA答复策略": "审查意见答复区别技术特征",
            "专利布局选型": "三个方案选哪个申请专利",
            "无效宣告攻防": "对手专利提无效宣告",
        }
        for expected_scenario, test_topic in test_cases.items():
            name, rule = rs.detect_scenario(test_topic)
            if name == expected_scenario:
                ok(f"场景识别: {expected_scenario} ✓")
            else:
                bad(f"场景识别: 期望「{expected_scenario}」, 实际「{name}」(议题: {test_topic})"); failed += 1
        # 检查 verdict 不误吞设计题
        track, _ = rs.decide_track("这个接口怎么设计", "auto")
        if track != "verdict":
            ok("verdict 不误吞开放式设计题")
        else:
            bad("verdict 误吞「这个接口怎么设计」— medium_markers 缺设计域词"); failed += 1
        # 检查 "oa" 不再单独作为关键词
        oa_check = any(" oa " in f" {s['keywords']} " for s in rs.SAGES.values())
        if not oa_check:
            ok("SAGES 关键词无单独 'oa'（已改为审查意见）")
        else:
            bad("SAGES 仍有单独 'oa' 关键词 — 会误匹配"); failed += 1
    else:
        bad("route_sages.py 不存在"); failed += 1

    # 检查 auto_invite 能力表
    ai_path = ROOT / "scripts" / "routing" / "auto_invite.py"
    if ai_path.exists():
        ai_text = ai_path.read_text(encoding="utf-8")
        cap_count = ai_text.count('"triggers"')
        if cap_count >= 12:
            ok(f"auto_invite 能力表完整 ({cap_count} 项能力)")
        else:
            bad(f"auto_invite 能力表不足 ({cap_count} 项, 预期≥12)"); failed += 1
        # 检查6新圣人是否在能力表里
        for sage in ["周全", "吴畏", "钱孟清", "叶诚", "须一平", "朱立鸣"]:
            if sage in ai_text:
                ok(f"auto_invite 含 {sage}")
            else:
                bad(f"auto_invite 缺 {sage}"); failed += 1
    else:
        bad("auto_invite.py 不存在"); failed += 1

    # 检查 saints.registry 与 saints/ 目录一致
    reg_path = ROOT / "references" / "saints" / "saints.registry.json"
    if reg_path.exists():
        import json
        reg = json.loads(reg_path.read_text(encoding="utf-8"))
        sage_dirs = set(p.name for p in (ROOT / "saints").iterdir() if p.is_dir())
        reg_names = set(reg.keys())
        if reg_names == sage_dirs:
            ok(f"saints/registry 一致 ({len(reg_names)} 位)")
        else:
            missing = sage_dirs - reg_names
            extra = reg_names - sage_dirs
            if missing: bad(f"saints/ 有目录但 registry 缺: {missing}"); failed += 1
            if extra: bad(f"registry 有但 saints/ 无目录: {extra}"); failed += 1
            if not missing and not extra: ok(f"saints/registry 一致 ({len(reg_names)} 位)")
    else:
        bad("saints.registry.json 不存在"); failed += 1

    print("\n== 结果 ==")
    if failed:
        print(f"❌ 自检失败：{failed} 项")
        sys.exit(1)
    print("✅ 全部通过")


if __name__ == "__main__":
    main()
