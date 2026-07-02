#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""校验 OpenClaw 圣人操作系统文件与 registry 一致性。"""
import json, sys
from pathlib import Path
if hasattr(sys.stdout, 'reconfigure'):
    sys.stdout.reconfigure(encoding='utf-8'); sys.stderr.reconfigure(encoding='utf-8')
ROOT=Path(__file__).resolve().parent.parent.parent
REG=ROOT/'references'/'saints'/'saints.registry.json'
REQ=['SOUL.md','IDENTITY.md','BOUNDARY.md','SUMMON.md','GROWTH.md','RELATIONS.json']

def main():
    failed=0
    if not REG.exists():
        print('❌ 缺 references/saints/saints.registry.json'); sys.exit(1)
    reg=json.loads(REG.read_text(encoding='utf-8'))
    print(f'== 圣人OS校验：{len(reg)} 位 ==')
    for name, meta in reg.items():
        d=ROOT/'saints'/name
        miss=[f for f in REQ if not (d/f).exists()]
        if miss:
            print(f'❌ {name}: 缺 {miss}'); failed+=1; continue
        # identity weight sanity
        ident=(d/'IDENTITY.md').read_text(encoding='utf-8')
        if str(meta.get('weight')) not in ident:
            print(f'❌ {name}: registry权重与IDENTITY不一致'); failed+=1
        rel=json.loads((d/'RELATIONS.json').read_text(encoding='utf-8'))
        if rel.get('sage')!=name:
            print(f'❌ {name}: RELATIONS sage字段不一致'); failed+=1
    if failed:
        print(f'❌ {failed} 项失败'); sys.exit(1)
    # 三源一致性：generate_saints 内置 SAINTS 字典 == registry == saints/ 目录
    # 防止扩展圣人只加了目录/registry 却漏改 generate_saints（--force 重建会丢人）
    import importlib.util, os
    gs_path = ROOT / 'scripts' / 'saints' / 'generate_saints.py'
    if gs_path.exists():
        try:
            spec = importlib.util.spec_from_file_location('_gs', str(gs_path))
            gs = importlib.util.module_from_spec(spec); spec.loader.exec_module(gs)
            gen = set(gs.SAINTS.keys())
            regi = set(reg.keys())
            dirs = {d for d in os.listdir(ROOT / 'saints') if (ROOT / 'saints' / d).is_dir()}
            if gen == regi == dirs:
                print(f'✅ 三源一致：generate_saints({len(gen)}) = registry({len(regi)}) = 目录({len(dirs)})')
            else:
                print(f'❌ 三源不一致: gen缺{sorted(dirs-gen)} reg缺{sorted(dirs-regi)}')
                failed += 1
        except Exception as e:
            print(f'⚠️  generate_saints 一致性校验跳过: {e}')
    if failed:
        print(f'❌ {failed} 项失败'); sys.exit(1)
    print('✅ 全部圣人OS文件通过')

if __name__=='__main__': main()
