#!/usr/bin/env python3
"""Render the single, continuously updated, secret-free when2buy run panel."""
import html, json
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]; STATE=ROOT/'data/state.json'; OUT=ROOT/'reports'/'run-panel.html'
def e(value): return html.escape(str(value or '').replace('\n', ' '),quote=True)
def link(url,label): return f'<a href="{e(url)}" target="_blank" rel="noreferrer">{e(label)}</a>' if url else '—'
def gallery(posts):
 cards=[]
 for post in reversed(posts[-30:]):
  urls=[u for u in post.get('mediaUrls',[]) if isinstance(u,str) and u.startswith('https://')]
  if not urls: continue
  thumbs=''.join(f'<a href="{e(url)}" target="_blank" rel="noreferrer"><img loading="lazy" referrerpolicy="no-referrer" src="{e(url)}" alt="original media from @{e(post.get("account"))}"></a>' for url in urls[:2])
  cards.append(f'<article><div class="meta">@{e(post.get("account"))} · {link(post.get("url"),"原帖")}</div><p>{e(post.get("text"))}</p><div class="thumbs">{thumbs}</div><small>原图：{len(urls)} · 本地归档：{sum(x.get("status")=="archived" for x in post.get("mediaArchive",[]) if isinstance(x,dict))}</small></article>')
  if len(cards)==8: break
 return ''.join(cards) or '<p class="muted">本次合格对标帖没有图片；文本和链接已保留。</p>'
def main():
 state=json.loads(STATE.read_text(encoding='utf-8')); run=state.get('runs',[])[-1] if state.get('runs') else {}; pkg=state.get('packages',[])[-1] if state.get('packages') else {}; post=state.get('posts',[])[-1] if state.get('posts') else {}
 status='PUBLISHED' if post.get('status')=='published' else (run.get('status') or 'blocked').upper(); verified=pkg.get('verificationSources',[]); creative=pkg.get('imagePath','')
 creative_html=f'<img class="creative" src="../{e(creative)}" alt="when2buy published creative">' if creative else '<p class="muted">尚无已完成的 when2buy 成图。</p>'
 OUT.write_text(f'''<!doctype html><html lang="zh-CN"><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1"><title>when2buy｜内容运行面板</title><style>body{{margin:0;background:#0f0f0f;color:#f7f7f5;font:16px/1.55 system-ui,sans-serif}}main{{max-width:1080px;margin:auto;padding:42px 22px}}.brand,a{{color:#61B74E}}.brand{{font-weight:800;letter-spacing:.1em}}.status{{color:#E36547;font-weight:800}}section,article{{background:#191919;border:1px solid #303030;border-radius:14px;padding:18px;margin:14px 0}}.grid{{display:grid;grid-template-columns:repeat(auto-fit,minmax(250px,1fr));gap:14px}}.grid section{{margin:0}}.muted,small{{color:#aaa}}.thumbs{{display:flex;gap:8px;overflow:auto}}.thumbs img{{width:190px;height:145px;object-fit:cover;border-radius:8px;background:#252525}}.creative{{width:min(560px,100%);border-radius:12px}}p{{white-space:pre-line}}h1{{margin:.25em 0}}</style><main><div class="brand">when2buy</div><h1>内容运行面板</h1><p>这是唯一的持续更新页面，不按运行新建页面。状态：<span class="status">{e(status)}</span> · 更新时间：{e(state.get('updatedAt'))}</p><div class="grid"><section><h2>来源</h2><p>{link(pkg.get('benchmarkPostUrl'),"对标原帖") if pkg else '—'}</p></section><section><h2>核验</h2><p>{'<br>'.join(link(x,'一级来源') for x in verified) or '未完成'}</p></section><section><h2>发布</h2><p>{link(post.get('url'),'X 公开链接') if post.get('url') else e(run.get('reason')) or '未完成'}</p></section></div><h2>最新采集原图</h2><p class="muted">图片直接展示原始媒体 URL；点击可打开原图。每张图也会尝试下载到 GitHub Actions artifact。</p>{gallery(state.get('benchmarkPosts',[]))}<h2>when2buy 成图</h2>{creative_html}</main></html>''',encoding='utf-8')
 print(f'Wrote {OUT}')
if __name__=='__main__': main()
