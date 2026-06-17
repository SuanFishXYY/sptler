#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""根据 memories/*.json 自动更新 saints/<姓名>/GROWTH.md。"""
import argparse, json, sys
from pathlib import Path
from datetime import datetime
if hasattr(sys.stdout,'reconfigure'):
    sys.stdout.reconfigure(encoding='utf-8'); sys.stderr.reconfigure(encoding='utf-8')
ROOT=Path(__file__).resolve().parent.parent

def load(path):
    try: return json.loads(path.read_text(encoding='utf-8'))
    except Exception: return None

def render_growth(mem):
    sage=mem.get('sage','未知')
    prof=mem.get('profile',{})
    exps=mem.get('experiences',[]) or []
    views=prof.get('frequent_views',[]) or []
    lines=[f'# {sage} · GROWTH', '', '> 本文件由 update_growth.py 根据圣人记忆自动生成。', '', f'## 更新时间', datetime.now().strftime('%Y-%m-%d %H:%M'), '', '## 当前画像', f"- 总议事数：{prof.get('total_meetings', len(exps))}", f"- 专长焦点：{'、'.join(prof.get('specialty_focus',[]) or []) or '—'}", f"- 风险偏好：{prof.get('risk_tendency','未知')}", f"- 历史立场：{prof.get('stances',{})}", '', '## 常提观点']
    if views:
        for v in views[:10]: lines.append(f"- {v.get('text','')}（{v.get('count',1)}次）")
    else: lines.append('- （暂无）')
    lines += ['', '## 近期经历']
    for e in exps[-10:]:
        lines.append(f"- {e.get('recorded_at','')}｜{e.get('meeting_type','regular')}｜{e.get('topic','')}｜立场：{e.get('stance','')}｜建议：{e.get('recommendation','')}")
    return '\n'.join(lines)+'\n'

def main():
    ap=argparse.ArgumentParser(description='更新圣人成长日志')
    ap.add_argument('--sage')
    ap.add_argument('--mem-dir', default='')
    args=ap.parse_args()
    mem_dir=Path(args.mem_dir).expanduser().resolve() if args.mem_dir else ROOT/'memories'
    paths=[mem_dir/f'{args.sage}.json'] if args.sage else sorted(mem_dir.glob('*.json'))
    count=0
    for p in paths:
        mem=load(p)
        if not mem: continue
        sage=mem.get('sage') or p.stem
        d=ROOT/'saints'/sage
        if not d.exists(): continue
        (d/'GROWTH.md').write_text(render_growth(mem), encoding='utf-8')
        print(f'✅ 更新 {sage}/GROWTH.md')
        count+=1
    if not count: print('（暂无可更新的成长日志）')

if __name__=='__main__': main()
