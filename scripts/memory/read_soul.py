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
    print(f'【{args.sage} OpenClaw灵魂注入】')
    for key,label in [('identity','身份'),('soul','灵魂'),('boundary','边界'),('summon','召唤')]:
        txt=data[key].strip().splitlines()
        print(f'\n## {label}')
        print('\n'.join(txt[:12]))

if __name__=='__main__': main()
