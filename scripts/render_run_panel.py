#!/usr/bin/env python3
'''Render one continuously updated, history-preserving when2buy operations panel.'''
import html
import json
from collections import defaultdict
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
STATE = ROOT / 'data/state.json'
OUT = ROOT / 'reports/run-panel.html'
REPO_RAW = 'https://raw.githubusercontent.com/hokeem/when2buy-content-production-publishing/main/'

def e(value): return html.escape(str(value or '').replace('\\n', ' '), quote=True)
def multiline(value): return html.escape(str(value or '—'), quote=True).replace('\\n', '<br>')
def link(url, label): return f'<a href="{e(url)}" target="_blank" rel="noreferrer">{e(label)}</a>' if url else '—'
def raw_repo_url(path): return REPO_RAW + '/'.join(str(path or '').split('/')) if path else ''
def stamp(value): return str(value or '—').replace('T', ' ').replace('+00:00', ' UTC')
def tag(value):
    v=str(value or 'unknown').lower(); cls='ok' if v in {'succeeded','published','ready'} else ('warn' if v in {'blocked','failed'} else 'neutral')
    return f'<span class="tag {cls}">{e(v)}</span>'
def batch_key(post):
    captured=str(post.get('capturedAt') or 'unknown')
    return captured[:19] if captured != 'unknown' else '历史导入（未记录采集时间）'
def benchmark_card(post):
    media=[u for u in post.get('mediaUrls',[]) if isinstance(u,str) and u.startswith('https://')]
    thumbs=''.join(f'<a href="{e(url)}" target="_blank" rel="noreferrer"><img loading="lazy" referrerpolicy="no-referrer" src="{e(url)}" alt="@{e(post.get("account"))} 原始媒体"></a>' for url in media[:4])
    archived=sum(1 for x in post.get('mediaArchive',[]) if isinstance(x,dict) and x.get('status')=='archived')
    return f'''<article class="benchmark-card"><div class="row"><strong>@{e(post.get('account'))}</strong>{link(post.get('url'),'打开原帖')}</div><p>{multiline(post.get('text'))}</p><div class="thumbs">{thumbs or '<span class="muted">无原帖媒体</span>'}</div><small>发布：{e(post.get('postedAt'))} · 原图 {len(media)} · 已归档 {archived}</small></article>'''
def crawl_history(posts, runs):
    groups=defaultdict(list)
    for post in posts: groups[batch_key(post)].append(post)
    radar_runs=[r for r in runs if r.get('mode')=='radar']; blocks=[]
    for when in sorted(groups,reverse=True):
        items=sorted(groups[when],key=lambda x:str(x.get('postedAt','')),reverse=True)
        matching=next((r for r in reversed(radar_runs) if str(r.get('startedAt',''))[:16]==when[:16]),None)
        run_note=f'<p class="run-note">{tag(matching.get("status"))} {multiline(matching.get("summary"))} {multiline(matching.get("reason"))}</p>' if matching else ''
        blocks.append(f'''<details class="history"><summary><span>采集批次 · {e(when)}</span><b>{len(items)} 条原帖</b></summary>{run_note}<div class="cards">{''.join(benchmark_card(x) for x in items)}</div></details>''')
    return ''.join(blocks) or '<p class="muted">暂无采集历史。</p>'
def package_history(packages):
    blocks=[]
    for pkg in reversed(packages):
        image=raw_repo_url(pkg.get('imagePath')); creative=f'<a href="{e(image)}" target="_blank" rel="noreferrer"><img class="creative" loading="lazy" src="{e(image)}" alt="{e(pkg.get("title"))}"></a>' if image else '<span class="muted">未成图</span>'
        verify='<br>'.join(link(x,'核验来源') for x in pkg.get('verificationSources',[])) or '—'
        facts='\\n'.join('• '+str(x) for x in pkg.get('mirroredFacts',[]))
        blocks.append(f'''<details class="history"><summary><span>{tag(pkg.get('status'))} {e(pkg.get('title'))}</span><b>{stamp(pkg.get('createdAt'))}</b></summary><div class="package"><div>{creative}</div><div><p><b>对标：</b>{link(pkg.get('benchmarkPostUrl'),'对标原帖')}</p><p><b>核验：</b>{verify}</p><p><b>文案：</b><br>{multiline(pkg.get('postText'))}</p><p><b>映射事实：</b><br>{multiline(facts)}</p></div></div></details>''')
    return ''.join(blocks) or '<p class="muted">暂无制作包。</p>'
def post_history(posts,packages):
    by_id={x.get('id'):x for x in packages}; rows=[]
    for post in reversed(posts):
        pkg=by_id.get(post.get('packageId'),{}); image=raw_repo_url(pkg.get('imagePath'))
        thumb=f'<a href="{e(image)}" target="_blank" rel="noreferrer"><img class="post-thumb" loading="lazy" src="{e(image)}" alt="发布配图"></a>' if image else '—'
        rows.append(f'<tr><td>{thumb}</td><td><b>{e(post.get("title"))}</b><br><small>{e(post.get("packageId"))}</small></td><td>{stamp(post.get("publishedAt"))}</td><td>{tag(post.get("status"))}</td><td>{link(post.get("url"),"打开 X")}</td></tr>')
    return ''.join(rows) or '<tr><td colspan="5" class="muted">暂无已发布内容。</td></tr>'
def run_history(runs):
    rows=[f'<tr><td>{stamp(run.get("startedAt"))}</td><td>{e(run.get("mode"))}</td><td>{tag(run.get("status"))}</td><td>{multiline(run.get("summary"))}<br><small>{multiline(run.get("reason"))}</small></td></tr>' for run in reversed(runs)]
    return ''.join(rows) or '<tr><td colspan="4" class="muted">暂无运行记录。</td></tr>'
def main():
    state=json.loads(STATE.read_text(encoding='utf-8')); posts=state.get('benchmarkPosts',[]); packages=state.get('packages',[]); published=state.get('posts',[]); runs=state.get('runs',[])
    published_count=sum(1 for x in published if x.get('status')=='published')
    out=f'''<!doctype html><html lang="zh-CN"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1"><title>when2buy｜内容历史面板</title><style>:root{{--bg:#0d0e10;--card:#16181d;--line:#30343b;--text:#f5f7fa;--muted:#9ba2ae;--green:#61b74e}}*{{box-sizing:border-box}}body{{margin:0;background:var(--bg);color:var(--text);font:15px/1.55 ui-sans-serif,system-ui,-apple-system,"Segoe UI",sans-serif}}main{{max-width:1280px;margin:auto;padding:38px 20px 70px}}a{{color:var(--green)}}h1{{font-size:34px;line-height:1.15;margin:.18em 0 .35em}}h2{{margin:36px 0 12px;font-size:21px}}.brand{{color:var(--green);font-weight:850;letter-spacing:.12em;text-transform:uppercase}}.muted,small{{color:var(--muted)}}.summary{{display:grid;grid-template-columns:repeat(4,minmax(0,1fr));gap:12px}}.stat{{background:var(--card);border:1px solid var(--line);border-radius:12px;padding:16px}}.stat b{{display:block;font-size:27px;margin-top:4px}}.tag{{display:inline-block;border-radius:999px;padding:2px 9px;font-size:12px;font-weight:800;letter-spacing:.04em}}.ok{{background:#173519;color:#91dc82}}.warn{{background:#45211f;color:#ff9f8c}}.neutral{{background:#30343b;color:#d4d8de}}details.history{{background:var(--card);border:1px solid var(--line);border-radius:12px;margin:10px 0;overflow:hidden}}summary{{cursor:pointer;display:flex;justify-content:space-between;gap:18px;padding:15px 17px;font-weight:700}}.cards{{display:grid;grid-template-columns:repeat(auto-fit,minmax(270px,1fr));gap:12px;padding:0 14px 14px}}.benchmark-card{{border:1px solid var(--line);border-radius:10px;padding:13px;background:#111317}}.row{{display:flex;justify-content:space-between;gap:10px}}.benchmark-card p{{white-space:pre-line;margin:10px 0}}.thumbs{{display:flex;gap:7px;overflow:auto;margin:9px 0}}.thumbs img{{height:130px;width:170px;object-fit:cover;border-radius:7px;background:#292d34}}.run-note{{padding:0 17px}}.package{{display:grid;grid-template-columns:minmax(180px,360px) 1fr;gap:18px;padding:0 17px 18px}}.creative{{display:block;width:100%;border-radius:9px;border:1px solid var(--line)}}.package p{{margin:0 0 12px}}.table-wrap{{overflow:auto;border:1px solid var(--line);border-radius:12px}}table{{width:100%;border-collapse:collapse;background:var(--card)}}th,td{{padding:12px;text-align:left;border-bottom:1px solid var(--line);vertical-align:middle}}th{{color:var(--muted);font-size:12px;text-transform:uppercase;letter-spacing:.05em}}.post-thumb{{width:78px;height:78px;object-fit:cover;border-radius:8px}}@media(max-width:720px){{main{{padding:26px 13px}}h1{{font-size:28px}}.summary{{grid-template-columns:repeat(2,1fr)}}.package{{grid-template-columns:1fr}}summary{{align-items:flex-start;flex-direction:column;gap:5px}}}}</style></head><body><main><div class="brand">when2buy</div><h1>内容历史面板</h1><p class="muted">单一持续更新页面。页面从版本化状态库累积渲染，保留每轮采集、每个制作包、每次发布和所有运行结论。最新状态：{e(state.get('updatedAt'))}</p><div class="summary"><div class="stat"><small>历史采集原帖</small><b>{len(posts)}</b></div><div class="stat"><small>历史制作包</small><b>{len(packages)}</b></div><div class="stat"><small>已验证发布</small><b>{published_count}</b></div><div class="stat"><small>运行记录</small><b>{len(runs)}</b></div></div><h2>采集历史 · 每轮对标帖子与原图</h2><p class="muted">每个批次保留原文、原帖链接、原图直链与归档数量。点击图片可查看原图。</p>{crawl_history(posts,runs)}<h2>内容制作历史 · 每个 package</h2>{package_history(packages)}<h2>发布历史</h2><div class="table-wrap"><table><thead><tr><th>配图</th><th>内容</th><th>发布时间</th><th>状态</th><th>链接</th></tr></thead><tbody>{post_history(published,packages)}</tbody></table></div><h2>完整运行时间线</h2><div class="table-wrap"><table><thead><tr><th>开始时间</th><th>环节</th><th>状态</th><th>结果 / 阻断原因</th></tr></thead><tbody>{run_history(runs)}</tbody></table></div></main></body></html>'''
    OUT.parent.mkdir(parents=True,exist_ok=True); OUT.write_text('\n'.join(line.rstrip() for line in out.splitlines())+'\n',encoding='utf-8'); print(f'Wrote {OUT}')
if __name__=='__main__': main()
