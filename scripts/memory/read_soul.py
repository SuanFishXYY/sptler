#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""读取某位圣人的 OpenClaw 灵魂摘要，用于发言注入。"""
import argparse, json, sys
from pathlib import Path
if hasattr(sys.stdout, 'reconfigure'):
    sys.stdout.reconfigure(encoding='utf-8'); sys.stderr.reconfigure(encoding='utf-8')
ROOT = Path(__file__).resolve().parent.parent.parent

def read(path):
    return path.read_text(encoding='utf-8') if path.exists() else ''

def main():
    ap=argparse.ArgumentParser(description='读取圣人SOUL/IDENTITY/BOUNDARY/SUMMON摘要')
    ap.add_argument('--sage', required=True)
    ap.add_argument('--json', action='store_true')
    ap.add_argument('--lite', action='store_true', help='精简模式：只取身份+边界一行，省 token（sptler# 用）')
    args=ap.parse_args()
    d=ROOT/'saints'/args.sage
    data={
        'sage': args.sage,
        'soul': read(d/'SOUL.md'),
        'identity': read(d/'IDENTITY.md'),
        'boundary': read(d/'BOUNDARY.md'),
        'summon': read(d/'SUMMON.md'),
    }
    if args.json:
        print(json.dumps(data,ensure_ascii=False,indent=2)); return
    if not d.exists():
        print(f'【{args.sage}】暂无圣人灵魂档案，请先运行 generate_saints.py'); return
    if args.lite:
        # lite：只够让圣人"按身份与边界说话"，砍掉灵魂命题/张力/失败模式/SUMMON。
        # 身份取非标题行（圣号/官职/权重），边界取第 1 条「必须反对」。
        id_parts=[l.strip().lstrip('-').strip() for l in data['identity'].strip().splitlines()
                  if l.strip() and not l.startswith('#')][:3]
        bdy_first=next((l for l in data['boundary'].strip().splitlines()
                        if l.strip() and not l.startswith('#')), '—')
        bdy = bdy_first.strip().lstrip('-').strip()
        print('【' + args.sage + '·lite】' + '｜'.join(id_parts) + ' ｜ 边界：' + bdy)
        return
    print(f'【{args.sage} OpenClaw灵魂注入】')
    for key,label in [('identity','身份'),('soul','灵魂'),('boundary','边界'),('summon','召唤')]:
        txt=data[key].strip().splitlines()
        print(f'\n## {label}')
        print('\n'.join(txt[:12]))

if __name__=='__main__': main()
