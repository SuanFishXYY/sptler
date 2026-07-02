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
        # lite 灵魂四件套：身份 + 核心命题(怎么想) + 边界1条(反对什么) + 失败模式1条(自警) + 必须追问1条(驱动要点)。
        # 命题/边界/失败模式/追问 都是裁决质量基石——省 token 省张力/风格/句式，不省这四样。
        id_parts=[l.strip().lstrip('-').strip() for l in data['identity'].strip().splitlines()
                  if l.strip() and not l.startswith('#')][:3]
        def first_under(text, heading):
            """提取 '## heading' 后第一个非空非标题行（支持 `- xxx` 列表项）。"""
            in_sec = False
            for l in (text or '').strip().splitlines():
                ls = l.strip()
                if ls.startswith('## ' + heading):
                    in_sec = True; continue
                if in_sec and ls.startswith('## '):
                    break
                if in_sec and ls:
                    # 多条用 ; 分隔时只取首条（lite 省 token，全塞违背初衷）
                    return ls.lstrip('-').strip().split(';')[0].strip()
            return ''
        prop = first_under(data['soul'], '核心命题')
        fail = first_under(data['soul'], '失败模式')
        bdy = first_under(data['boundary'], '必须反对')
        ask = first_under(data['boundary'], '必须追问')
        parts = ['｜'.join(id_parts)]
        if prop: parts.append('命题：' + prop)
        if bdy: parts.append('边界：' + bdy)
        if fail: parts.append('自警：' + fail)
        if ask: parts.append('追问：' + ask)
        print('【' + args.sage + '·lite】' + ' ｜ '.join(parts))
        return
    print(f'【{args.sage} OpenClaw灵魂注入】')
    for key,label in [('identity','身份'),('soul','灵魂'),('boundary','边界'),('summon','召唤')]:
        txt=data[key].strip().splitlines()
        print(f'\n## {label}')
        print('\n'.join(txt[:12]))

if __name__=='__main__': main()
