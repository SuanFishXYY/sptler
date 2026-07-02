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
    "/sptler#",
    "名单确认",
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

    # 子 skill (sptler-brief/sptler-lite) frontmatter 守卫：独立 skill 目录的 SKILL.md 也须合法，
    # 否则 Claude Code 不识别——主 validator 只查根 SKILL.md，子 skill 坏了抓不到。
    print("\n== 子 skill frontmatter ==")
    for sub in ["sptler-brief", "sptler-lite"]:
        sp = ROOT / sub / "SKILL.md"
        if not sp.exists():
            bad(f"{sub}/SKILL.md 缺失"); failed += 1; continue
        st = sp.read_text(encoding="utf-8")
        sm = re.match(r"^---\n(.*?)\n---", st, re.S)
        if not sm:
            bad(f"{sub} frontmatter 缺失"); failed += 1; continue
        if yaml:
            sfm = yaml.safe_load(sm.group(1))
            sextra = set(sfm.keys()) - allowed
            schecks = [
                (not sextra, f"{sub} 无非法字段 {sextra}"),
                (sfm.get("name") == sub, f"{sub} name={sub}"),
                (len(sfm.get("description", "")) <= 1024, f"{sub} description<=1024"),
                ("<" not in sfm.get("description", "") and ">" not in sfm.get("description", ""), f"{sub} description无尖括号"),
            ]
            for passed, label in schecks:
                if passed: ok(label)
                else: bad(label); failed += 1
        sbody = st[sm.end():]
        if len(sbody.split()) <= 5000: ok(f"{sub} body<=5000词 ({len(sbody.split())})")
        else: bad(f"{sub} body过长"); failed += 1

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

    # JSON 遍历/加载脚本必须 isinstance 守卫：杂散的非对象 JSON（合法 list、
    # list-of-non-dict、dict-when-list-expected）曾导致 7 个脚本崩溃（同源 bug 类）。
    # 覆盖：记忆目录遍历（compact/watch/update_growth/list_memories）+
    #       会议索引加载（continue_meeting/index_meeting/build_relations）。
    GLOB_GUARD = [
        "scripts/memory/compact_memories.py",
        "scripts/memory/watch_memory.py",
        "scripts/memory/update_growth.py",
        "scripts/saints/list_memories.py",
        "scripts/output/continue_meeting.py",
        "scripts/output/index_meeting.py",
        "scripts/memory/build_relations.py",
        "scripts/output/briefing.py",
        "scripts/output/action_board.py",
        "scripts/memory/memory_io.py",
    ]
    print("\n== JSON 遍历脚本守卫 ==")
    for rel in GLOB_GUARD:
        src = (ROOT / rel).read_text(encoding="utf-8")
        # 精确匹配 isinstance(x, dict) 守卫（", dict)" 避开 defaultdict 等误匹配）。
        if "isinstance(" in src and ", dict)" in src:
            ok(f"{rel} 含 isinstance(dict) 守卫")
        else:
            bad(f"{rel} 缺 isinstance(dict) 守卫 — 杂散 JSON 会致崩溃"); failed += 1

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

    # 检查 lite 模式（/sptler#）：read_soul 与 summon_sage 必须支持 --lite，否则精简模式静默失效
    print("\n== lite 模式守卫 ==")
    import subprocess
    import json as _json
    for rel in ["scripts/memory/read_soul.py", "scripts/memory/summon_sage.py", "scripts/routing/route_sages.py", "scripts/memory/record_memory.py", "scripts/output/index_meeting.py"]:
        p = ROOT / rel
        if not p.exists():
            bad(f"{rel} 不存在"); failed += 1
            continue
        try:
            out = subprocess.run([sys.executable, str(p), "--help"], capture_output=True, text=True, encoding="utf-8")
            if "--lite" in (out.stdout or ""):
                ok(f"{rel} 支持 --lite（/sptler# 精简模式可用）")
            else:
                bad(f"{rel} 缺 --lite — /sptler# 会静默退化为完整模式"); failed += 1
        except Exception as e:
            bad(f"{rel} --help 执行失败: {e}"); failed += 1
    # lite 行为守卫：route_sages --lite 必须把多域议题截到 ≤3 人、专利场景拒绝
    rs_lit = ROOT / "scripts" / "routing" / "route_sages.py"
    if rs_lit.exists():
        try:
            out = subprocess.run([sys.executable, str(rs_lit), "--topic", "AI检索流水线落地架构",
                                  "--lite", "--json"], capture_output=True, text=True, encoding="utf-8")
            d = _json.loads(out.stdout)
            n = len(d.get("attendees", []))
            if n <= 3:
                ok(f"route_sages --lite 多域议题截到 {n} 人（≤3）")
            else:
                bad(f"route_sages --lite 多域议题返回 {n} 人，超过 lite 封顶 3"); failed += 1
            out2 = subprocess.run([sys.executable, str(rs_lit), "--topic", "查新检索蓝牙AOA新颖性",
                                   "--lite", "--json"], capture_output=True, text=True, encoding="utf-8")
            d2 = _json.loads(out2.stdout)
            if d2.get("lite_rejected") and len(d2.get("attendees", [])) == 0:
                ok("route_sages --lite 拒绝专利场景（lite_rejected=true，0 人）")
            else:
                bad("route_sages --lite 未拒绝专利场景 — 会用精简模式跑专属流程"); failed += 1
            out3 = subprocess.run([sys.executable, str(rs_lit), "--topic", "战略平台建设方向预算",
                                   "--lite", "--json"], capture_output=True, text=True, encoding="utf-8")
            d3 = _json.loads(out3.stdout)
            if d3.get("lite_quality_concern"):
                ok("route_sages --lite formal 降级时标 lite_quality_concern（质量护栏）")
            else:
                bad("route_sages --lite 对 formal 降级未标 lite_quality_concern — 质量存疑无信号"); failed += 1
            # lite + 多邀请：邀请不可被 cap 静默截断（Discipline #10 Honor invites）
            out4 = subprocess.run([sys.executable, str(rs_lit), "--topic", "边界问题",
                                   "--invites", "王升,张鑫,徐奕阳,范征", "--lite", "--json"],
                                  capture_output=True, text=True, encoding="utf-8")
            d4 = _json.loads(out4.stdout)
            got = {a["name"] for a in d4.get("attendees", [])}
            need = {"王升", "张鑫", "徐奕阳", "范征"}
            if need.issubset(got):
                ok("lite cap 不截断用户邀请（Honor invites，超 cap 全留+告警）")
            else:
                bad(f"lite cap 截断了用户邀请 {need - got} — 违反 Honor invites"); failed += 1
        except Exception as e:
            bad(f"route_sages --lite 行为校验失败: {e}"); failed += 1
    # briefing 守卫：route_sages --briefing 场景题须 ≤5 且 fast（非 formal 8），briefing:true
    if rs_lit.exists():
        try:
            out = subprocess.run([sys.executable, str(rs_lit), "--topic", "OA审查意见答复AI流水线怎么落地",
                                  "--briefing", "--json"], capture_output=True, text=True, encoding="utf-8")
            d = _json.loads(out.stdout)
            n = len(d.get("attendees", []))
            sz = d.get("target_size", 0)
            tk = d.get("track", "")
            if d.get("briefing") and n <= 5 and sz <= 5 and tk != "formal":
                ok(f"briefing 场景题截到 {n} 人 fast（≤5，非 formal 8）")
            else:
                bad(f"briefing 未强制：attendees={n} size={sz} track={tk} briefing={d.get('briefing')}"); failed += 1
            # briefing verdict 单域题不应膨胀成 fast 多人（按问题重量降级是核心设计）
            out5 = subprocess.run([sys.executable, str(rs_lit), "--topic", "权利要求边界怎么收",
                                   "--briefing", "--json"], capture_output=True, text=True, encoding="utf-8")
            d5 = _json.loads(out5.stdout)
            if d5.get("track") == "verdict" and len(d5.get("attendees", [])) <= 1:
                ok("briefing verdict 单域题不膨胀（按重量降级，1 人裁决）")
            else:
                bad(f"briefing 把 verdict 膨胀成 {d5.get('track')} {len(d5.get('attendees',[]))}人 — 违反按重量降级"); failed += 1
        except Exception as e:
            bad(f"route_sages --briefing 行为校验失败: {e}"); failed += 1
    # lite 记忆守卫：record_memory --lite 不得翻转圣人风险画像（事件留痕、画像不动）
    import tempfile, shutil
    rm_lit = ROOT / "scripts" / "memory" / "record_memory.py"
    if rm_lit.exists():
        tmpd = Path(tempfile.mkdtemp())
        try:
            base = {"topic":"T","meeting_id":"S0","mode":"快速","verdict":"通过","meeting_type":"regular",
                    "attendees":[{"sage":"王升","stance":"赞成","reason":"r","ideas":"i","recommendation":"rec"}]}
            opp = {"topic":"T","meeting_id":"L0","mode":"快速","verdict":"否决","meeting_type":"regular",
                   "attendees":[{"sage":"王升","stance":"反对","reason":"r","ideas":"i","recommendation":"rec"}]}
            for b, lite in [(base, False), (opp, True)]:
                bp = tmpd / "b.json"; bp.write_text(_json.dumps(b, ensure_ascii=False), encoding="utf-8")
                subprocess.run([sys.executable, str(rm_lit), "--batch", str(bp), "--mem-dir", str(tmpd)]
                               + (["--lite"] if lite else []), capture_output=True)
            mf = [f for f in tmpd.iterdir() if f.suffix == ".json" and f.name != "b.json"][0]
            m = _json.loads(mf.read_text(encoding="utf-8"))
            risk = m["profile"].get("risk_tendency", "")
            has_lite_tag = any(e.get("lite") for e in m["experiences"])
            # 1赞1反对(50% oppose) 标准→审慎保守；lite 不应重算→应停在 平衡中立(来自首条标准记录)
            if has_lite_tag and risk == "平衡中立":
                ok("record_memory --lite 不翻转风险画像（lite=true 标记 + risk 未重算）")
            else:
                bad(f"record_memory --lite 翻转了画像或未标 lite（risk={risk}, lite_tag={has_lite_tag}）"); failed += 1
        except Exception as e:
            bad(f"record_memory --lite 行为校验失败: {e}"); failed += 1
        finally:
            shutil.rmtree(tmpd, ignore_errors=True)
    # lite 记忆降权守卫：构造 lite 记忆原始分更高(更新)但正式记忆应排前的场景。
    # 正式记忆 2年前(decay 0.15) vs lite 记忆今天(decay 1.0)：无降权时 lite 赢(0.15<1.0)；
    # 有降权时 lite×0.5，若原始分相近则正式可反超——这里用同原始分让 lite 0.5×仍可能输。
    # 更严格：让 lite 原始分 = 正式×2，降权后 lite = 正式，平分时稳定排序正式先(插入序)。
    try:
        import importlib.util as _ilu
        _spec = _ilu.spec_from_file_location("_ss", str(ROOT / "scripts" / "memory" / "summon_sage.py"))
        _ss = _ilu.module_from_spec(_spec); _spec.loader.exec_module(_ss)
        # 正式：今天、value_score=2 → final = s*1.0*2 = 2s
        # lite：今天、value_score=3 → 无降权=3s (lite赢)；降权=3s*0.5=1.5s < 2s (正式赢)
        # 这是唯一能区分降权是否生效的分值组合：lite 原始分更高，降权后才输给正式。
        _mem = {"experiences": [
            {"topic":"权利要求边界","domain":"边界/权利要求","stance":"赞成","verdict":"通过","value_score":2,"recorded_at":"2026-07-01 00:00"},
            {"topic":"权利要求边界","domain":"边界/权利要求","stance":"赞成","verdict":"通过","value_score":3,"recorded_at":"2026-07-01 00:00","lite":True,"citation_count":2},
        ]}
        _hits = _ss.relevant_experiences(_mem, "权利要求边界")
        if _hits and not _hits[0][0].get("lite"):
            ok("lite 记忆降权：正式记忆排前，lite 不污染引用")
        else:
            bad("lite 记忆未降权 — lite 快调可能平权污染正式引用"); failed += 1
    except Exception as e:
        bad(f"lite 记忆降权校验失败: {e}"); failed += 1
    # lite 留痕守卫：compact 不得物理删除 lite:true 记忆（lite 是事件留痕，可回溯）
    try:
        _cspec = _ilu.spec_from_file_location("_cc", str(ROOT / "scripts" / "memory" / "compact_memories.py"))
        _cc = _ilu.module_from_spec(_cspec); _cspec.loader.exec_module(_cc)
        _lite_trivial = _cc.classify(
            {'is_turning_point': False, 'value_score': 0, 'meeting_type': 'regular',
             'mode': 'verdict', 'citation_count': 0, 'parent_meeting_id': '', 'lite': True}, False)
        if _lite_trivial != "delete":
            ok(f"compact 不物理删 lite 记忆（判 {_lite_trivial}，留痕可回溯）")
        else:
            bad("compact 物理删 lite 记忆 — 破坏 lite 事件留痕可回溯性"); failed += 1
    except Exception as e:
        bad(f"compact lite 留痕校验失败: {e}"); failed += 1
    # lite 索引闭环守卫：index_meeting --lite 写 lite:true，continue_meeting 读回 lite:true
    im_lit = ROOT / "scripts" / "output" / "index_meeting.py"
    cm_lit = ROOT / "scripts" / "output" / "continue_meeting.py"
    if im_lit.exists() and cm_lit.exists():
        tmpd2 = Path(tempfile.mkdtemp())
        try:
            subprocess.run([sys.executable, str(im_lit), "--meeting-id", "LGATE", "--topic", "T",
                            "--mode", "lite·裁决", "--attendees", "王升", "--lite", "--meetings-dir", str(tmpd2)],
                           capture_output=True)
            out = subprocess.run([sys.executable, str(cm_lit), "--last", "--json", "--meetings-dir", str(tmpd2)],
                                 capture_output=True, text=True, encoding="utf-8")
            d = _json.loads(out.stdout)
            if d.get("lite") is True:
                ok("lite 索引闭环：index_meeting --lite 写入 → continue_meeting 读回 lite:true")
            else:
                bad(f"lite 索引闭环断裂（continue_meeting 读到 lite={d.get('lite')}）"); failed += 1
        except Exception as e:
            bad(f"lite 索引闭环校验失败: {e}"); failed += 1
        finally:
            shutil.rmtree(tmpd2, ignore_errors=True)
    # lite 回顾守卫：briefing.py 读到 lite 会议须标"lite快调"（防 lite 快调在回顾里与正式议会平权呈现）
    bf_lit = ROOT / "scripts" / "output" / "briefing.py"
    if bf_lit.exists() and im_lit.exists():
        tmpd3 = Path(tempfile.mkdtemp())
        try:
            subprocess.run([sys.executable, str(im_lit), "--meeting-id", "BGATE", "--topic", "T",
                            "--mode", "lite·裁决", "--attendees", "王升", "--lite", "--meetings-dir", str(tmpd3)],
                           capture_output=True)
            out = subprocess.run([sys.executable, str(bf_lit), "--meetings-dir", str(tmpd3)],
                                 capture_output=True, text=True, encoding="utf-8")
            if "⚡lite快调" in (out.stdout or "") and "BGATE" in (out.stdout or ""):
                ok("briefing.py 区分 lite 会议（回顾标 lite 标记）")
            else:
                bad("briefing.py 未区分 lite 会议 — lite 快调在回顾里与正式平权"); failed += 1
        except Exception as e:
            bad(f"briefing lite 校验失败: {e}"); failed += 1
        finally:
            shutil.rmtree(tmpd3, ignore_errors=True)
    # memory_io 导入守卫：import 须标 imported=true + 走 lite 路径不翻转画像
    mio = ROOT / "scripts" / "memory" / "memory_io.py"
    if mio.exists():
        tmpd4 = Path(tempfile.mkdtemp())
        try:
            imp = tmpd4 / "imp.txt"
            imp.write_text("议题:外部会议 | 立场:反对 | 建议:驳回", encoding="utf-8")
            subprocess.run([sys.executable, str(mio), "import", "--sage", "王升",
                            "--file", str(imp), "--topic", "外部", "--verdict", "否决",
                            "--mem-dir", str(tmpd4)], capture_output=True)
            mf = [f for f in tmpd4.iterdir() if f.suffix == ".json" and f.name != "imp.txt"][0]
            m = _json.loads(mf.read_text(encoding="utf-8"))
            tagged = any(e.get("imported") for e in m.get("experiences", []))
            risk = m["profile"].get("risk_tendency", "")
            # 1反对否决：标准→审慎保守；lite 路径→应停在 平衡中立 或 未知（不翻转）
            if tagged and risk != "审慎保守":
                ok("memory_io import 标 imported + 不翻转风险画像（lite 路径）")
            else:
                bad(f"memory_io import 未标 imported 或翻转了画像（tagged={tagged}, risk={risk}）"); failed += 1
        except Exception as e:
            bad(f"memory_io import 校验失败: {e}"); failed += 1
        finally:
            shutil.rmtree(tmpd4, ignore_errors=True)

    # 检查 auto_invite 能力表
    ai_path = ROOT / "scripts" / "routing" / "auto_invite.py"
    if ai_path.exists():
        ai_text = ai_path.read_text(encoding="utf-8")
        cap_count = ai_text.count('"triggers"')
        if cap_count >= 12:
            ok(f"auto_invite 能力表完整 ({cap_count} 项能力)")
        else:
            bad(f"auto_invite 能力表不足 ({cap_count} 项, 预期≥12)"); failed += 1
        # 检查每位可路由圣人至少归属一个能力类别（智能补人无盲区）
        # 邹蕴是固定议长，不入 route_sages.SAGES、不被「邀请」，故用 rs.SAGES 而非全注册表。
        routeable = set(rs.SAGES.keys())
        missing_cap = sorted(n for n in routeable if n not in ai_text)
        if not missing_cap:
            ok(f"auto_invite 能力表覆盖全部可路由圣人 ({len(routeable)} 位无盲区)")
        else:
            bad(f"auto_invite 缺能力覆盖的圣人: {missing_cap}（智能补人无法建议他们）"); failed += 1
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
