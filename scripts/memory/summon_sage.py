#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""完整召唤圣人上下文：SOUL + IDENTITY + BOUNDARY + SUMMON + MEMORY + RELATIONS。

遵循 references/memory/memory_philosophy.md：
- 命中相关记忆时 citation_count += 1 并回写（用过即重要）
- relevant 排序按 价值分 × 时效衰减（近期优先，旧记忆降权）
- 输出双画像（长期 profile + 短期 profile_recent），圣人能表达"骨子 vs 近况"
- superseded 记忆不引用，但提示"曾主张 X 后改 Y"（转折点可见但不污染）
"""
import argparse, json, re, sys
from pathlib import Path
from datetime import datetime
if hasattr(sys.stdout,'reconfigure'):
    sys.stdout.reconfigure(encoding='utf-8'); sys.stderr.reconfigure(encoding='utf-8')
ROOT=Path(__file__).resolve().parent.parent.parent

def read(path):
    return path.read_text(encoding='utf-8') if path.exists() else ''

def load_json(path):
    try: return json.loads(path.read_text(encoding='utf-8'))
    except Exception: return {}

def mem_path(sage, mem_dir=None):
    return (Path(mem_dir).expanduser().resolve() if mem_dir else ROOT/'memories')/f'{sage}.json'

def recency_days(recorded_at):
    """距今天数；解析失败返回大数（视为很久前）。"""
    try:
        d = datetime.strptime(recorded_at[:10], '%Y-%m-%d')
        return max(0, (datetime.now() - d).days)
    except Exception:
        return 9999

def time_decay(days):
    """时效衰减因子：90天内≈1，1年≈0.5，2年≈0.25。"""
    if days <= 90: return 1.0
    if days <= 365: return 0.7
    if days <= 730: return 0.4
    return 0.15

def relevant_experiences(mem, topic, limit=3):
    """按 domain+关键词命中 × 时效衰减 排序；排除 superseded。返回 (exp, score, days)。
    lite 记忆(lite=true)降权 ×0.5——它是快调（可能不充分），不得与正式结论平权引用，
    只在无正式记忆匹配时才被引用，避免 lite 快调污染后续正式决策。"""
    exps = (mem or {}).get('experiences',[]) or []
    if not exps or not topic:
        return []
    t = topic.lower()
    scored = []
    for e in exps:
        if e.get('superseded'):  # 已被推翻的不引用
            continue
        et = (e.get('topic','') or '').lower()
        ed = e.get('domain','') or ''
        s = 0
        for part in re.split(r'[/、 ]', ed):
            p = part.strip().lower()
            if p and len(p) >= 2 and p in t:
                s += 5
        bigrams = {et[i:i+2] for i in range(len(et)-1) if re.match(r'[一-鿿]{2}', et[i:i+2])}
        for bg in bigrams:
            if bg in t:
                s += 2
        if s > 0:
            days = recency_days(e.get('recorded_at',''))
            final = s * time_decay(days) * (e.get('value_score',1) or 1)
            if e.get('lite'):  # lite 快调降权：让位于正式结论，防止不充分快调被当定论引用
                final *= 0.5
            scored.append((final, days, e))
    scored.sort(key=lambda x: x[0], reverse=True)
    return [(e, sc, d) for sc, d, e in scored[:limit]]

def bump_citations(mem, mem_file, hits):
    """命中记忆 citation_count += 1，重算 value_score，回写。"""
    if not hits or not mem_file:
        return
    changed = False
    hit_ids = {id(e) for e, _, _ in hits}
    for e in mem.get('experiences',[]) or []:
        if id(e) in hit_ids and not e.get('superseded'):
            e['citation_count'] = int(e.get('citation_count',0)) + 1
            passed = 1 if e.get('verdict')=='通过' else 0
            e['value_score'] = passed * (int(e['citation_count']) + 1)
            changed = True
    if changed:
        try:
            mem_file.write_text(json.dumps(mem, ensure_ascii=False, indent=2), encoding='utf-8')
        except Exception:
            pass


def pending_citations(mem, hits):
    """dry-run 模式：记录待回写的 citation（不立即写盘），返回可序列化的待提交清单。"""
    pending = []
    for e, _, _ in hits:
        if not e.get('superseded'):
            pending.append({
                'meeting_id': e.get('meeting_id', ''),
                'topic': e.get('topic', ''),
                'recorded_at': e.get('recorded_at', ''),
            })
    return pending

def profile_block(prof):
    if not prof: return None
    return {
        'total_meetings': prof.get('total_meetings',0),
        'specialty_focus': prof.get('specialty_focus',[]),
        'risk_tendency': prof.get('risk_tendency','未知'),
        'stances': prof.get('stances',{}),
        'frequent_views': (prof.get('frequent_views',[]) or [])[:5],
    }

def memory_summary(sage, mem_dir=None):
    p = mem_path(sage, mem_dir)
    mem = load_json(p)
    if not mem:
        return {'total_meetings':0,'note':'新晋圣人，暂无议会经历','recent':[],'relevant':[],'turning_points':[]}
    prof = mem.get('profile',{})
    prof_recent = mem.get('profile_recent',{})
    return {
        'total_meetings': prof.get('total_meetings',0),
        'profile_longterm': profile_block(prof),
        'profile_recent': profile_block(prof_recent) or profile_block(prof),
        'recent': (mem.get('experiences',[]) or [])[-3:],
        'relevant': [],
        'turning_points': [],
        '_mem': mem,
        '_mem_file': p,
    }

def turning_points(mem):
    """superseded=true 的旧立场（转折点），供提示"曾主张X后改Y"。"""
    return [e for e in (mem.get('experiences',[]) or []) if e.get('is_turning_point') and e.get('superseded')]

def summon(sage, mem_dir=None, topic=None, dry_run=False, lite=False):
    d = ROOT/'saints'/sage
    if lite:
        # lite：精简灵魂（身份+核心命题+边界）+ 轻记忆指针（最近1条lite经历，1行）。
        # 不读记忆全文（省 token），但给1条"上次lite"指针——同类问题第二次问，圣人知道上次结论。
        # 平衡：lite 保留极轻记忆连续性，代价仅 +1 行（远小于全文注入）。
        lite_ptr = ''
        mem = load_json(mem_path(sage, mem_dir))
        if isinstance(mem, dict):
            for e in reversed(mem.get('experiences', []) or []):
                if isinstance(e, dict) and e.get('lite') and not e.get('superseded'):
                    date = (e.get('recorded_at', '') or '')[:10]
                    topic_e = e.get('topic', '') or ''
                    rec = e.get('recommendation', '') or ''
                    verdict = e.get('verdict', '') or ''
                    lite_ptr = f'{date} {topic_e}({verdict})→{rec}'
                    break
        return {
            'sage': sage, 'topic': topic or '', 'lite': True,
            'identity': read(d/'IDENTITY.md'),
            'soul': read(d/'SOUL.md'),
            'boundary': read(d/'BOUNDARY.md'),
            'lite_memory_pointer': lite_ptr,
            'memory': {}, 'relations': {},
        }
    msum = memory_summary(sage, mem_dir)
    mem = msum.pop('_mem', {})
    mem_file = msum.pop('_mem_file', None)
    if topic:
        hits = relevant_experiences(mem, topic)
        if dry_run:
            # 延迟回写：只返回 pending 清单，不立即改 citation（等用户确认写入记忆）
            msum['pending_citations'] = pending_citations(mem, hits)
        else:
            bump_citations(mem, mem_file, hits)  # 用过即重要：引用计数+1回写
        msum['relevant'] = [(e, sc, d_) for e, sc, d_ in hits]
        msum['turning_points'] = turning_points(mem)
    return {
        'sage': sage,
        'topic': topic or '',
        'identity': read(d/'IDENTITY.md'),
        'soul': read(d/'SOUL.md'),
        'boundary': read(d/'BOUNDARY.md'),
        'summon': read(d/'SUMMON.md'),
        'growth': read(d/'GROWTH.md'),
        'relations': load_json(d/'RELATIONS.json'),
        'memory': msum
    }

def age_label(days):
    if days <= 30: return f"{days}天前"
    if days <= 90: return f"{days//30}月前"
    return f"{days//365}年前" if days >= 365 else f"{days//30}月前"

def fmt_exp(e, days=None):
    age = f"（{age_label(days)}）" if days is not None else ""
    val = e.get('value_score',0)
    valtag = f"[价值{val}·引用{e.get('citation_count',0)}]" if val else ""
    litetag = " ｜⚠️ lite快调·可能不充分" if e.get('lite') else ""
    return (f"  - {age} {e.get('topic','')}（{e.get('mode','')}/{e.get('verdict','')}）："
            f"立场={e.get('stance','')}，建议={e.get('recommendation','')} {valtag}{litetag}")

def main():
    ap=argparse.ArgumentParser(description='完整召唤圣人上下文（记忆哲学宪法版）')
    ap.add_argument('--sage', required=True)
    ap.add_argument('--topic', default='', help='当前议题；传入时返回相关记忆并+1引用计数')
    ap.add_argument('--mem-dir', default='')
    ap.add_argument('--dry-run', action='store_true', help='延迟回写模式：不立即改citation，返回pending清单，等用户确认写入记忆后再回写')
    ap.add_argument('--lite', action='store_true', help='精简模式：只读身份+边界，不注入记忆/关系/历史（sptler# 用，省 token）')
    ap.add_argument('--json', action='store_true')
    args=ap.parse_args()
    data=summon(args.sage, args.mem_dir or None, args.topic or None, dry_run=args.dry_run, lite=args.lite)
    if args.json:
        # relevant 里的 tuple 转成可序列化
        m=data['memory']
        if not args.lite:
            m['relevant']=[{'experience':e,'score':sc,'days_ago':d_} for e,sc,d_ in m.get('relevant',[])]
        print(json.dumps(data,ensure_ascii=False,indent=2)); return
    if not (ROOT/'saints'/args.sage).exists():
        print(f'【{args.sage}】暂无圣人OS档案，请先运行 generate_saints.py'); return
    if args.lite:
        # lite 灵魂四件套：身份 + 命题(怎么想) + 边界(反对什么) + 自警(失败模式) + 追问(驱动要点) + 上次lite指针
        id_parts=[l.strip().lstrip('-').strip() for l in (data.get('identity','') or '').strip().splitlines()
                  if l.strip() and not l.startswith('#')][:3]
        def first_under(text, heading):
            in_sec = False
            for l in (text or '').strip().splitlines():
                ls = l.strip()
                if ls.startswith('## ' + heading):
                    in_sec = True; continue
                if in_sec and ls.startswith('## '):
                    break
                if in_sec and ls:
                    return ls.lstrip('-').strip().split(';')[0].strip()
            return ''
        prop = first_under(data.get('soul',''), '核心命题')
        conflict = first_under(data.get('soul',''), '内在冲突')
        quote = first_under(data.get('soul',''), '典型句式')
        fail = first_under(data.get('soul',''), '失败模式')
        bdy = first_under(data.get('boundary',''), '必须反对')
        ask = first_under(data.get('boundary',''), '必须追问')
        parts = ['｜'.join(id_parts)]
        if prop: parts.append('命题：' + prop)
        if conflict: parts.append('冲突：' + conflict)
        if bdy: parts.append('边界：' + bdy)
        if fail: parts.append('自警：' + fail)
        if ask: parts.append('追问：' + ask)
        if quote: parts.append('句式：' + quote)
        ptr = data.get('lite_memory_pointer') or ''
        if ptr: parts.append('上次lite：' + ptr)
        print('【' + args.sage + '·lite】' + ' ｜ '.join(parts))
        return
    print(f'【完整召唤：{args.sage}】' + (f'（议题：{args.topic}）' if args.topic else ''))
    for key,label in [('identity','身份'),('soul','灵魂'),('boundary','边界'),('summon','召唤')]:
        print(f'\n## {label}\n'+ '\n'.join(data[key].strip().splitlines()[:10]))
    print('\n## 记忆画像（双画像）')
    mem=data['memory']
    lt=mem.get('profile_longterm') or {}
    rc=mem.get('profile_recent') or {}
    print(f"长期（底色）：{lt.get('total_meetings',0)}次｜{lt.get('risk_tendency','未知')}｜焦点：{'、'.join(lt.get('specialty_focus',[]) or []) or '—'}")
    print(f"短期（近况）：{rc.get('total_meetings',0)}次｜{rc.get('risk_tendency','未知')}｜焦点：{'、'.join(rc.get('specialty_focus',[]) or []) or '—'}")
    if lt.get('risk_tendency') and rc.get('risk_tendency') and lt['risk_tendency']!=rc['risk_tendency']:
        print(f"  ⚠️ 底色{lt['risk_tendency']}但近况{rc['risk_tendency']}——圣人可表达'我向来{lt['risk_tendency']}，但最近{rc['risk_tendency']}'")
    rel = mem.get('relevant', [])
    if rel:
        print('\n## ⚡ 可引用的相关记忆（请在发言第一句引用；引用计数已+1）')
        for e, sc, d_ in rel:
            print(fmt_exp(e, d_))
    elif mem.get('total_meetings',0) > 0:
        print('\n## 近期经历（无强相关记忆，可按需引用）')
        for e in mem.get('recent', [])[-2:]:
            print(fmt_exp(e, recency_days(e.get('recorded_at',''))))
    else:
        print('\n## 新晋圣人，暂无议会经历')
    tps = mem.get('turning_points', [])
    if tps:
        print('\n## 🔄 转折点（曾主张后被推翻，不引用但可提"我以前认为…后来改了"）')
        for e in tps[-3:]:
            print(f"  - {e.get('recorded_at','')} {e.get('topic','')}：曾{e.get('stance','')}，已被新结论推翻")
    rels=data.get('relations',{}).get('relations',{})
    if rels:
        print('\n## 关系摘要')
        for n,r in list(rels.items())[:5]:
            print(f"- {n}: 共议{r.get('co_meetings',0)}次，最近：{r.get('last_topic','')}")

if __name__=='__main__': main()
