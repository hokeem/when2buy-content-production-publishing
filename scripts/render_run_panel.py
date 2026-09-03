#!/usr/bin/env python3
'''Render the daily when2buy crawl-to-release table, newest date first.'''
import html
import json
from collections import defaultdict
from datetime import datetime, timedelta
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
STATE = ROOT / 'data' / 'state.json'
OUT = ROOT / 'reports' / 'run-panel.html'
REPO_RAW = 'https://raw.githubusercontent.com/hokeem/when2buy-content-production-publishing/main/'

def e(value): return html.escape(str(value or '—'), quote=True)
def text(value): return e(value).replace('\n', '<br>')
def link(url, label): return f'<a href="{e(url)}" target="_blank" rel="noreferrer">{e(label)}</a>' if url else '—'
def asset(path): return REPO_RAW + '/'.join(str(path or '').split('/')) if path else ''
def thumb(url, label, cls): return f'<a href="{e(url)}" target="_blank" rel="noreferrer"><img class="{cls}" loading="lazy" referrerpolicy="no-referrer" src="{e(url)}" alt="{e(label)}"></a>' if url else '—'
def crawl_time(value): return str(value or '—').replace('T', ' ').replace('+00:00', ' UTC')
def day(value): return str(value or 'unknown')[:10]
def metric(value): return f'{value:,}' if isinstance(value, (int, float)) else '—'

def as_datetime(value):
    if not value: return None
    try: return datetime.fromisoformat(str(value).replace('Z', '+00:00'))
    except ValueError: return None

def source_media(post):
    urls = [url for url in post.get('mediaUrls', []) if isinstance(url, str) and url.startswith('https://')]
    return '<div class="source-images">' + ''.join(thumb(url, 'Original source image', 'source-image') for url in urls) + '</div>' if urls else '<span class="muted">No source image</span>'

def row(post, packages, releases):
    package = packages.get(post.get('id'), {})
    release = releases.get(package.get('id'), {})
    image_url = asset(package.get('imagePath'))
    status = release.get('status') or package.get('status') or 'not produced'
    status_class = 'published' if status == 'published' else 'pending'
    source = f'<b>@{e(post.get("account"))}</b> · {link(post.get("url"), "Open source post")}<p>{text(post.get("text"))}</p>{source_media(post)}'
    copy = text(package.get('postText')) if package else '<span class="muted">No when2buy output</span>'
    image = thumb(image_url, package.get('title', 'when2buy final image'), 'final-image') if image_url else '<span class="muted">No final image</span>'
    output = f'<p class="copy">{copy}</p>{image}'
    release_cell = f'<span class="status {status_class}">{e(status.upper())}</span><br>{link(release.get("url"), "Open confirmed release")}' if release else f'<span class="status {status_class}">{e(status.upper())}</span>'
    return f'<tr><td>{e(crawl_time(post.get("capturedAt")))}</td><td>{source}</td><td>{output}</td><td>{release_cell}</td></tr>'

def first_day_history(post, snapshots):
    published_at = as_datetime(post.get('publishedAt'))
    if not published_at:
        return '<span class="muted">No publication timestamp</span>'
    cutoff = published_at + timedelta(hours=24)
    first_day = [item for item in snapshots if published_at <= as_datetime(item.get('observedAt')) <= cutoff]
    if not first_day:
        return '<span class="muted">No first-24h snapshot captured</span>'
    items = []
    for item in first_day:
        items.append(f'<li>{e(crawl_time(item.get("observedAt")))} · V {metric(item.get("views"))} · R {metric(item.get("replies"))} · RP {metric(item.get("reposts"))} · L {metric(item.get("likes"))}</li>')
    return '<ol class="snapshots">' + ''.join(items) + '</ol>'

def tracker_row(post, snapshots):
    ordered = sorted(snapshots, key=lambda item: str(item.get('observedAt', '')))
    latest = ordered[-1] if ordered else {}
    return f'''<tr><td><b>{e(post.get('title'))}</b><br>{link(post.get('url'), 'Open public X post')}</td>
      <td>{metric(latest.get('views'))}</td><td>{metric(latest.get('replies'))}</td><td>{metric(latest.get('reposts'))}</td><td>{metric(latest.get('likes'))}</td>
      <td>{e(crawl_time(latest.get('observedAt'))) if latest else '—'}</td><td>{first_day_history(post, ordered)}</td></tr>'''

def tracker(posts, snapshots):
    by_post = defaultdict(list)
    for item in snapshots:
        if item.get('postId'): by_post[str(item['postId'])].append(item)
    rows = ''.join(tracker_row(post, by_post.get(str(post.get('id')), [])) for post in sorted(posts, key=lambda item: str(item.get('publishedAt', '')), reverse=True) if post.get('status') == 'published')
    empty = '<tr><td colspan="7" class="muted">No published posts.</td></tr>'
    return f'<section><h2>Publication metrics</h2><p class="muted">Public X observations only. V = views, R = replies, RP = reposts, L = likes. First-24h history is chronological and uses captured snapshots only.</p><div class="table-wrap"><table class="metrics"><thead><tr><th>Published post</th><th>Views</th><th>Replies</th><th>Reposts</th><th>Likes</th><th>Last checked</th><th>First 24h snapshots</th></tr></thead><tbody>{rows or empty}</tbody></table></div></section>'

def main():
    state = json.loads(STATE.read_text(encoding='utf-8'))
    packages = {item.get('benchmarkPostId'): item for item in state.get('packages', []) if item.get('benchmarkPostId')}
    releases = {item.get('packageId'): item for item in state.get('posts', []) if item.get('packageId')}
    grouped = defaultdict(list)
    for post in state.get('benchmarkPosts', []): grouped[day(post.get('capturedAt'))].append(post)
    sections = []
    for captured_day in sorted(grouped, reverse=True):
        body = ''.join(row(post, packages, releases) for post in sorted(grouped[captured_day], key=lambda post: str(post.get('capturedAt', '')), reverse=True))
        sections.append(f'<section><h2>{e(captured_day)}</h2><div class="table-wrap"><table><thead><tr><th>Crawl time</th><th>Original source</th><th>when2buy output</th><th>Confirmed release</th></tr></thead><tbody>{body}</tbody></table></div></section>')
    out = f'''<!doctype html><html lang="en"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1"><title>when2buy daily table</title><style>
      :root{{--bg:#0c0d10;--panel:#14161b;--line:#30343b;--text:#f6f7f9;--muted:#a8b0bd;--green:#75c66a}}*{{box-sizing:border-box}}body{{margin:0;background:var(--bg);color:var(--text);font:14px/1.5 ui-sans-serif,system-ui,-apple-system,"Segoe UI",sans-serif}}main{{max-width:1440px;margin:auto;padding:32px 18px 60px}}h1{{margin:0 0 6px;font-size:30px}}h2{{margin:34px 0 10px;font-size:20px}}p{{margin:8px 0}}a{{color:var(--green)}}.muted{{color:var(--muted)}}.table-wrap{{overflow:auto;border:1px solid var(--line);border-radius:10px}}table{{width:100%;min-width:1050px;border-collapse:collapse;background:var(--panel)}}th,td{{padding:14px;vertical-align:top;text-align:left;border-bottom:1px solid var(--line)}}th{{font-size:12px;letter-spacing:.04em;text-transform:uppercase;color:var(--muted);background:#101217}}td:first-child{{white-space:nowrap;color:var(--muted);width:165px}}td:nth-child(2){{width:34%}}td:nth-child(3){{width:37%}}.source-images{{display:flex;gap:8px;flex-wrap:wrap;margin-top:10px}}.source-image{{width:94px;height:94px;object-fit:cover;border-radius:6px;border:1px solid var(--line)}}.final-image{{display:block;width:180px;height:180px;object-fit:cover;border-radius:8px;border:1px solid var(--line);margin-top:12px}}.copy{{max-width:560px}}.status{{display:inline-block;padding:2px 8px;border-radius:999px;font-size:12px;font-weight:800;letter-spacing:.04em}}.published{{background:#183b20;color:#a5e898}}.pending{{background:#472522;color:#ffb2a8}}.metrics{{min-width:1120px}}.metrics td:first-child{{white-space:normal;width:28%}}.metrics td{{white-space:nowrap}}.metrics td:last-child{{white-space:normal;min-width:260px}}.snapshots{{margin:0;padding-left:20px;color:var(--muted);font-size:12px}}@media(max-width:700px){{main{{padding:22px 12px}}h1{{font-size:25px}}}}
      </style></head><body><main><h1>when2buy daily crawl → release</h1><p class="muted">Full history by crawl date. Newest first.</p>{''.join(sections) or '<p class="muted">No source posts captured.</p>'}{tracker(state.get('posts', []), state.get('metricSnapshots', []))}</main></body></html>'''
    OUT.parent.mkdir(parents=True, exist_ok=True)
    OUT.write_text(out + '\n', encoding='utf-8')
    print(f'Wrote {OUT}')

if __name__ == '__main__': main()
