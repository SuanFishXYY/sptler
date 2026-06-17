#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""完整召唤圣人上下文：SOUL + IDENTITY + BOUNDARY + SUMMON + MEMORY + RELATIONS。"""
import argparse, json, sys
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
    if not mem: return {'total_meetings':0,'note':'新晋圣人，暂无议会经历'}
    prof=mem.get('profile',{})
    return {
        'total_meetings': prof.get('total_meetings',0),
        'specialty_focus': prof.get('specialty_focus',[]),
        'risk_tendency': prof.get('risk_tendency','未知'),
        'stances': prof.get('stances',{}),
        'frequent_views': (prof.get('frequent_views',[]) or [])[:5],
        'recent': (mem.get('experiences',[]) or [])[-3:]
    }

def summon(sage, mem_dir=None):
    d=ROOT/'saints'/sage
    return {
        'sage': sage,
        'identity': read(d/'IDENTITY.md'),
        'soul': read(d/'SOUL.md'),
        'boundary': read(d/'BOUNDARY.md'),
        'summon': read(d/'SUMMON.md'),
        'growth': read(d/'GROWTH.md'),
        'relations': load_json(d/'RELATIONS.json'),
        'memory': memory_summary(sage, mem_dir)
    }

def main():
    ap=argparse.ArgumentParser(description='完整召唤圣人上下文')
    ap.add_argument('--sage', required=True)
    ap.add_argument('--mem-dir', default='')
    ap.add_argument('--json', action='store_true')
    args=ap.parse_args()
    data=summon(args.sage, args.mem_dir or None)
    if args.json:
        print(json.dumps(data,ensure_ascii=False,indent=2)); return
    if not (ROOT/'saints'/args.sage).exists():
        print(f'【{args.sage}】暂无圣人OS档案，请先运行 generate_saints.py'); return
    print(f'【完整召唤：{args.sage}】')
    for key,label in [('identity','身份'),('soul','灵魂'),('boundary','边界'),('summon','召唤')]:
        print(f'\n## {label}\n'+ '\n'.join(data[key].strip().splitlines()[:10]))
    print('\n## 记忆摘要')
    mem=data['memory']
    print(f"参与 {mem.get('total_meetings',0)} 次；风险偏好：{mem.get('risk_tendency','未知')}；焦点：{'、'.join(mem.get('specialty_focus',[]) or []) or '—'}")
    if mem.get('frequent_views'):
        print('常提观点：'+'；'.join(v.get('text','') for v in mem['frequent_views'][:3]))
    rels=data.get('relations',{}).get('relations',{})
    if rels:
        print('\n## 关系摘要')
        for n,r in list(rels.items())[:5]:
            print(f"- {n}: 共现{r.get('co_meetings',0)}次，最近：{r.get('last_topic','')}")

if __name__=='__main__': main()
