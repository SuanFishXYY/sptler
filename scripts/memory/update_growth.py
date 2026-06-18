#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""根据 memories/*.json 自动更新 saints/<姓名>/GROWTH.md。"""
import argparse, json, sys
from pathlib import Path
from datetime import datetime
if hasattr(sys.stdout,'reconfigure'):
    sys.stdout.reconfigure(encoding='utf-8'); sys.stderr.reconfigure(encoding='utf-8')
ROOT=Path(__file__).resolve().parent.parent.parent

def load(path):
    try: return json.loads(path.read_text(encoding='utf-8'))
    except Exception: return None

def render_growth(mem):
    sage=mem.get('sage','未知')
    prof=mem.get('profile',{})
    prof_recent=mem.get('profile_recent',{})
    exps=mem.get('experiences',[]) or []
    views=prof.get('frequent_views',[]) or []
    lines=[f'# {sage} · GROWTH', '', '> 本文件由 update_growth.py 按记忆哲学宪法自动生成。', '', f'## 更新时间', datetime.now().strftime('%Y-%m-%d %H:%M'), '', '## 双画像']
    lines.append(f"- 长期（底色）：{prof.get('total_meetings', len(exps))}次｜{prof.get('risk_tendency','未知')}｜焦点：{'、'.join(prof.get('specialty_focus',[]) or []) or '—'}")
    lines.append(f"- 短期（近况·近30次）：{prof_recent.get('total_meetings',0)}次｜{prof_recent.get('risk_tendency','未知')}｜焦点：{'、'.join(prof_recent.get('specialty_focus',[]) or []) or '—'}")
    if prof.get('risk_tendency') and prof_recent.get('risk_tendency') and prof['risk_tendency']!=prof_recent.get('risk_tendency'):
        lines.append(f"- ⚠️ 张力：底色{prof['risk_tendency']} ↔ 近况{prof_recent['risk_tendency']}")
    lines += ['', '## 常提观点（长期）']
    if views:
        for v in views[:10]: lines.append(f"- {v.get('text','')}（{v.get('count',1)}次）")
    else: lines.append('- （暂无）')
    # 高价值记忆
    high = [e for e in exps if (e.get('value_score',0) or 0) >= 2]
    if high:
        lines += ['', '## 高价值记忆（通过且被引用）']
        for e in high[-8:]:
            lines.append(f"- {e.get('recorded_at','')} {e.get('topic','')}｜价值{e.get('value_score',0)}·引用{e.get('citation_count',0)}")
    # 转折点
    tps = [e for e in exps if e.get('is_turning_point')]
    if tps:
        lines += ['', '## 转折点（改主意记录）']
        for e in tps[-8:]:
            tag = '（已被推翻）' if e.get('superseded') else '（新立场·推翻旧）'
            lines.append(f"- {e.get('recorded_at','')} {e.get('topic','')}：{e.get('stance','')} {tag}")
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
