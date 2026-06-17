#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""完整召唤圣人上下文：SOUL + IDENTITY + BOUNDARY + SUMMON + MEMORY + RELATIONS。

带 --topic 时，额外从记忆中筛出与当前议题最相关的历史经历（魔法时刻素材）。
"""
import argparse, json, re, sys
from pathlib import Path
if hasattr(sys.stdout,'reconfigure'):
    sys.stdout.reconfigure(encoding='utf-8'); sys.stderr.reconfigure(encoding='utf-8')
ROOT=Path(__file__).resolve().parent.parent

def read(path):
    return path.read_text(encoding='utf-8') if path.exists() else ''

def load_json(path):
    try: return json.loads(path.read_text(encoding='utf-8'))
    except Exception: return {}

def memory_summary(sage, mem_dir=None):
    p=(Path(mem_dir).expanduser().resolve() if mem_dir else ROOT/'memories')/f'{sage}.json'
    mem=load_json(p)
    if not mem: return {'total_meetings':0,'note':'新晋圣人，暂无议会经历','recent':[],'relevant':[]}
    prof=mem.get('profile',{})
    return {
        'total_meetings': prof.get('total_meetings',0),
        'specialty_focus': prof.get('specialty_focus',[]),
        'risk_tendency': prof.get('risk_tendency','未知'),
        'stances': prof.get('stances',{}),
        'frequent_views': (prof.get('frequent_views',[]) or [])[:5],
        'recent': (mem.get('experiences',[]) or [])[-3:],
        'relevant': [],
        '_mem': mem
    }

def relevant_experiences(mem, topic, limit=3):
    """按 domain 命中 + topic 关键词重叠，筛出与当前议题最相关的历史经历。"""
    exps = (mem or {}).get('experiences',[]) or []
    if not exps or not topic:
        return []
    t = topic.lower()
    scored = []
    for e in exps:
        et = (e.get('topic','') or '').lower()
        ed = e.get('domain','') or ''
        score = 0
        # domain 名出现在新 topic（如 domain="AI/铸模"，新topic含"ai"/"铸模"）
        for part in re.split(r'[/、 ]', ed):
            p = part.strip().lower()
            if p and len(p) >= 2 and p in t:
                score += 5
        # 历史 topic 与新 topic 的 2 字关键词重叠
        bigrams = {et[i:i+2] for i in range(len(et)-1) if re.match(r'[一-鿿]{2}', et[i:i+2])}
        for bg in bigrams:
            if bg in t:
                score += 2
        # 共享 stance 类型不加分，避免噪声
        if score > 0:
            scored.append((score, e))
    scored.sort(key=lambda x: x[0], reverse=True)
    return [e for _, e in scored[:limit]]

def summon(sage, mem_dir=None, topic=None):
    d=ROOT/'saints'/sage
    mem_summary = memory_summary(sage, mem_dir)
    mem = mem_summary.pop('_mem', {})
    if topic:
        mem_summary['relevant'] = relevant_experiences(mem, topic)
    return {
        'sage': sage,
        'topic': topic or '',
        'identity': read(d/'IDENTITY.md'),
        'soul': read(d/'SOUL.md'),
        'boundary': read(d/'BOUNDARY.md'),
        'summon': read(d/'SUMMON.md'),
        'growth': read(d/'GROWTH.md'),
        'relations': load_json(d/'RELATIONS.json'),
        'memory': mem_summary
    }

def fmt_exp(e):
    return (f"  - [{e.get('recorded_at','')}] {e.get('topic','')}（{e.get('mode','')}/{e.get('verdict','')}）："
            f"立场={e.get('stance','')}，建议={e.get('recommendation','')}")

def main():
    ap=argparse.ArgumentParser(description='完整召唤圣人上下文')
    ap.add_argument('--sage', required=True)
    ap.add_argument('--topic', default='', help='当前议题；传入时额外返回相关历史记忆')
    ap.add_argument('--mem-dir', default='')
    ap.add_argument('--json', action='store_true')
    args=ap.parse_args()
    data=summon(args.sage, args.mem_dir or None, args.topic or None)
    if args.json:
        print(json.dumps(data,ensure_ascii=False,indent=2)); return
    if not (ROOT/'saints'/args.sage).exists():
        print(f'【{args.sage}】暂无圣人OS档案，请先运行 generate_saints.py'); return
    print(f'【完整召唤：{args.sage}】' + (f'（议题：{args.topic}）' if args.topic else ''))
    for key,label in [('identity','身份'),('soul','灵魂'),('boundary','边界'),('summon','召唤')]:
        print(f'\n## {label}\n'+ '\n'.join(data[key].strip().splitlines()[:10]))
    print('\n## 记忆摘要')
    mem=data['memory']
    print(f"参与 {mem.get('total_meetings',0)} 次；风险偏好：{mem.get('risk_tendency','未知')}；焦点：{'、'.join(mem.get('specialty_focus',[]) or []) or '—'}")
    if mem.get('frequent_views'):
        print('常提观点：'+'；'.join(v.get('text','') for v in mem['frequent_views'][:3]))
    # 魔法时刻：相关历史记忆
    rel = mem.get('relevant', [])
    if rel:
        print('\n## ⚡ 可引用的相关记忆（请在发言第一句引用）')
        for e in rel:
            print(fmt_exp(e))
    elif mem.get('total_meetings',0) > 0:
        print('\n## 近期经历（无强相关记忆，可按需引用）')
        for e in mem.get('recent', [])[-2:]:
            print(fmt_exp(e))
    else:
        print('\n## 新晋圣人，暂无议会经历')
    rels=data.get('relations',{}).get('relations',{})
    if rels:
        print('\n## 关系摘要')
        for n,r in list(rels.items())[:5]:
            print(f"- {n}: 共议{r.get('co_meetings',0)}次，最近：{r.get('last_topic','')}")

if __name__=='__main__': main()
