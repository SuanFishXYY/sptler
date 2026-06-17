#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""根据 sptler-meetings/index.json 的共现关系更新 saints/<姓名>/RELATIONS.json。"""
import argparse, json, sys
from pathlib import Path
from collections import defaultdict
from datetime import datetime
if hasattr(sys.stdout,'reconfigure'):
    sys.stdout.reconfigure(encoding='utf-8'); sys.stderr.reconfigure(encoding='utf-8')
ROOT=Path(__file__).resolve().parent.parent

def default_meetings_dir(): return Path.cwd()/'sptler-meetings'
def load(path):
    try: return json.loads(path.read_text(encoding='utf-8'))
    except Exception: return None

def main():
    ap=argparse.ArgumentParser(description='从会议索引构建圣人关系网')
    ap.add_argument('--meetings-dir', default='')
    args=ap.parse_args()
    md=Path(args.meetings_dir).expanduser().resolve() if args.meetings_dir else default_meetings_dir()
    index=load(md/'index.json') or []
    rel=defaultdict(lambda: defaultdict(lambda: {'co_meetings':0,'topics':[],'last_topic':'','last_meeting_id':'','last_updated':''}))
    for e in index:
        attendees=[a for a in (e.get('attendees') or []) if a and a!='邹蕴']
        for i,a in enumerate(attendees):
            for b in attendees[i+1:]:
                for x,y in [(a,b),(b,a)]:
                    r=rel[x][y]
                    r['co_meetings']+=1
                    topic=e.get('topic','')
                    if topic and topic not in r['topics']:
                        r['topics'].append(topic)
                    r['topics']=r['topics'][-20:]
                    r['last_topic']=topic
                    r['last_meeting_id']=e.get('meeting_id','')
                    r['last_updated']=datetime.now().strftime('%Y-%m-%d')
    count=0
    for sage, rs in rel.items():
        d=ROOT/'saints'/sage
        if not d.exists(): continue
        out={'sage':sage,'relations':dict(rs)}
        (d/'RELATIONS.json').write_text(json.dumps(out,ensure_ascii=False,indent=2),encoding='utf-8')
        print(f'✅ 更新 {sage}/RELATIONS.json ({len(rs)} relations)')
        count+=1
    if not count: print('（无可构建关系；请先生成 sptler-meetings/index.json）')

if __name__=='__main__': main()
