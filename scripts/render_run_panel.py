#!/usr/bin/env python3
"""Render a self-contained, secret-free HTML audit panel from state.json."""
import html, json
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]; STATE=ROOT/'data/state.json'; OUT=ROOT/'reports'/'run-panel.html'
def e(v): return html.escape(str(v or ''))
def main():
 s=json.loads(STATE.read_text(encoding='utf-8'))
 run=s.get('runs',[])[-1] if s.get('runs') else {}; pkg=s.get('packages',[])[-1] if s.get('packages') else {}; post=s.get('posts',[])[-1] if s.get('posts') else {}
 source=pkg.get('benchmarkPostUrl',''); verified=pkg.get('verificationSources',[]); image=pkg.get('imagePath','')
 status='PUBLISHED' if post.get('status')=='published' else (run.get('status') or 'blocked').upper()
 def link(url,label): return f'<a href="{e(url)}">{e(label)}</a>' if url else '—'
 sections=[('采集',link(source,'对标原帖') if source else '没有合格的对标源'),('核验','<br>'.join(link(x,'一级来源') for x in verified) or '未完成'),('制作',e(pkg.get('title')) or '未完成'),('发布',link(post.get('url'),'X 公开链接') if post.get('url') else e(run.get('reason')) or '未完成')]
 cards=''.join(f'<section><h2>{name}</h2><p>{detail}</p></section>' for name,detail in sections)
 pic=f'<img src="../{e(image)}" alt="when2buy creative">' if image else ''
 OUT.write_text(f'''<!doctype html><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1"><title>when2buy run panel</title><style>body{{margin:0;background:#0f0f0f;color:#f7f7f5;font:16px/1.6 system-ui}}main{{max-width:900px;margin:auto;padding:44px 22px}}.brand,a{{color:#61B74E}}.brand{{font-weight:800;letter-spacing:.1em}}section{{background:#191919;border:1px solid #303030;border-radius:14px;padding:18px;margin:14px 0}}.status{{color:#E36547;font-weight:800}}img{{max-width:100%;border-radius:12px}}</style><main><div class="brand">when2buy</div><h1>内容运行面板</h1><p>状态：<span class="status">{e(status)}</span> · 更新：{e(s.get('updatedAt'))}</p>{cards}{pic}</main>''',encoding='utf-8')
 print(f'Wrote {OUT}')
if __name__=='__main__': main()
