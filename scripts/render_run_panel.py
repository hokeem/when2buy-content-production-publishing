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
LOGO_URL = REPO_RAW + 'skills/when2buy-content-publisher/assets/when2buy-logo-reference.png'

def e(value): return html.escape(str(value or '—'), quote=True)
def text(value): return e(value).replace('\n', '<br>')
def link(url, label): return f'<a href="{e(url)}" target="_blank" rel="noreferrer">{e(label)}</a>' if url else '—'
def asset(path): return REPO_RAW + '/'.join(str(path or '').split('/')) if path else ''
def thumb(url, label, cls): return f'<a href="{e(url)}" target="_blank" rel="noreferrer"><img class="{cls}" loading="lazy" referrerpolicy="no-referrer" src="{e(url)}" alt="{e(label)}"></a>' if url else '—'
def crawl_time(value): return str(value or '—').replace('T', ' ').replace('+00:00', ' UTC')
def day(value): return str(value or 'unknown')[:10]
def metric(value): return f'{value:,}' if isinstance(value, (int, float)) else '—'

def metric_chip(icon, label, value):
    return f'<span class="metric-chip" title="{e(label)}"><span class="metric-icon" aria-hidden="true">{icon}</span><span class="metric-label">{e(label)}</span><strong>{metric(value)}</strong></span>'

def as_datetime(value):
    if not value: return None
    try: return datetime.fromisoformat(str(value).replace('Z', '+00:00'))
    except ValueError: return None

def source_media(post):
    urls = [url for url in post.get('mediaUrls', []) if isinstance(url, str) and url.startswith('https://')]
    return '<div class="source-images">' + ''.join(thumb(url, 'Original source image', 'source-image') for url in urls) + '</div>' if urls else '<span class="muted">No source image</span>'

def usable_snapshot(item):
    return any(item.get(field) is not None for field in ('views', 'replies', 'reposts', 'likes'))

def snapshot_line(item):
    source = (item.get('evidence') or {}).get('source') or 'legacy capture'
    values = f'V {metric(item.get("views"))} · L {metric(item.get("likes"))} · B {metric(item.get("bookmarks"))} · R {metric(item.get("replies"))} · RP {metric(item.get("reposts"))}'
    suffix = '' if usable_snapshot(item) else ' · no metrics recorded'
    return f'{e(crawl_time(item.get("observedAt")))} · {values} · {e(source)}{suffix}'

def first_day_history(post, snapshots):
    published_at = as_datetime(post.get('publishedAt'))
    if not published_at:
        return '<span class="muted">No publication timestamp</span>'
    cutoff = published_at + timedelta(hours=24)
    first_day = [item for item in snapshots if as_datetime(item.get('observedAt')) and published_at <= as_datetime(item.get('observedAt')) <= cutoff and usable_snapshot(item)]
    if not first_day:
        return '<span class="muted">No first-24h metrics captured</span>'
    return '<ol class="snapshots">' + ''.join(f'<li>{snapshot_line(item)}</li>' for item in first_day) + '</ol>'

def metric_cell(post, snapshots):
    ordered = sorted(snapshots, key=lambda item: str(item.get('observedAt', '')))
    measured = [item for item in ordered if usable_snapshot(item)]
    latest = measured[-1] if measured else {}
    tracking = post.get('metricsTracking') or {}
    first_count = 0
    published_at = as_datetime(post.get('publishedAt'))
    if published_at:
        cutoff = published_at + timedelta(hours=24)
        first_count = sum(1 for item in measured if as_datetime(item.get('observedAt')) and published_at <= as_datetime(item.get('observedAt')) <= cutoff)
    checked_at = tracking.get('lastAttemptAt') or latest.get('observedAt')
    summary = ''.join((
        metric_chip('◉', 'Views', latest.get('views')),
        metric_chip('♥', 'Likes', latest.get('likes')),
        metric_chip('▱', 'Bookmarks', latest.get('bookmarks')),
        metric_chip('↩', 'Replies', latest.get('replies')),
        metric_chip('↻', 'Reposts', latest.get('reposts')),
    ))
    status = tracking.get('status', 'not initialized').upper()
    history = '<span class="muted">No snapshots</span>' if not ordered else '<ol class="snapshots">' + ''.join(f'<li>{snapshot_line(item)}</li>' for item in ordered) + '</ol>'
    return f'''<div class="tracking-cell"><div class="tracking-values">{summary}</div><div class="tracking-meta">Checked {e(crawl_time(checked_at))}<br><span class="tracking-state">72h {e(status)}</span> · First 24h {first_count}</div><details class="metric-details"><summary>First 24h history</summary>{first_day_history(post, ordered)}</details><details class="metric-details"><summary>All snapshots ({len(ordered)})</summary>{history}</details></div>'''

def row(post, packages, releases, snapshots):
    package = packages.get(post.get('id'), {})
    release = releases.get(package.get('id'), {})
    image_url = asset(package.get('imagePath'))
    status = release.get('status') or package.get('status') or 'not produced'
    status_class = 'published' if status == 'published' else 'pending'
    source = f'<b>@{e(post.get("account"))}</b> · {link(post.get("url"), "Open source post")}<p>{text(post.get("text"))}</p>{source_media(post)}'
    copy = text(package.get('postText')) if package else '<span class="muted">No when2buy output</span>'
    image = thumb(image_url, package.get('title', 'when2buy final image'), 'final-image') if image_url else '<span class="muted">No final image</span>'
    release_inline = f'<div class="release-inline"><span class="status {status_class}">{e(status.upper())}</span>{link(release.get("url"), "Open confirmed X release")}</div>' if release else f'<div class="release-inline"><span class="status {status_class}">{e(status.upper())}</span></div>'
    output = f'<p class="copy">{copy}</p>{image}{release_inline}'
    release_post = release if release else {}
    return f'<tr><td data-label="Crawl time">{e(crawl_time(post.get("capturedAt")))}</td><td data-label="Original source">{source}</td><td data-label="when2buy output">{output}</td><td data-label="24h data">{metric_cell(release_post, snapshots.get(str(release_post.get("id")), [])) if release_post else "—"}</td></tr>'

def main():
    state = json.loads(STATE.read_text(encoding='utf-8'))
    packages = {item.get('benchmarkPostId'): item for item in state.get('packages', []) if item.get('benchmarkPostId')}
    releases = {item.get('packageId'): item for item in state.get('posts', []) if item.get('packageId')}
    snapshots = defaultdict(list)
    for item in state.get('metricSnapshots', []):
        if item.get('postId'): snapshots[str(item.get('postId'))].append(item)
    grouped = defaultdict(list)
    # The dashboard is an output ledger: captured sources without a package stay
    # in durable state, but are intentionally not displayed as empty rows.
    for post in state.get('benchmarkPosts', []):
        if post.get('id') in packages:
            grouped[day(post.get('capturedAt'))].append(post)
    def sections_for(kind):
        sections = []
        for captured_day in sorted(grouped, reverse=True):
            items = [post for post in grouped[captured_day] if (packages.get(post.get('id'), {}).get('status') == 'published') == (kind == 'completed')]
            if not items: continue
            body = ''.join(row(post, packages, releases, snapshots) for post in sorted(items, key=lambda post: str(post.get('capturedAt', '')), reverse=True))
            sections.append(f'<section class="day-card"><h2>{e(captured_day)}</h2><div class="table-wrap"><table><thead><tr><th>Crawl time</th><th>Original source</th><th>when2buy output</th><th>24h data</th></tr></thead><tbody>{body}</tbody></table></div></section>')
        return ''.join(sections) or '<p class="muted">No packages in this view.</p>'
    completed, ready = sections_for('completed'), sections_for('ready')
    out = f'''<!doctype html><html lang="en"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1"><title>WHEN2BUY X CONTENT FACTORY</title><style>
      :root{{--ink:#f8f7f7;--muted:#a5a0a2;--red:#ec2638;--red-soft:rgba(236,38,56,.15);--glass:rgba(22,20,22,.72);--line:rgba(255,255,255,.12);--shadow:0 24px 64px rgba(0,0,0,.36)}}*{{box-sizing:border-box}}body{{margin:0;min-height:100vh;color:var(--ink);background:radial-gradient(circle at 8% -8%,#491019 0,transparent 30rem),radial-gradient(circle at 100% 2%,#241015 0,transparent 28rem),linear-gradient(135deg,#080809 0%,#111012 55%,#070708 100%);font:14px/1.55 ui-sans-serif,system-ui,-apple-system,"Segoe UI",sans-serif}}main{{max-width:1660px;margin:auto;padding:42px 24px 72px}}.masthead{{display:flex;align-items:center;gap:18px;margin:0 0 22px;padding:20px 22px;border:1px solid var(--line);border-radius:20px;background:var(--glass);box-shadow:var(--shadow);backdrop-filter:blur(18px)}}.brand-logo{{width:58px;height:58px;object-fit:contain;border-radius:14px;background:#000;border:1px solid rgba(236,38,56,.55);padding:5px}}h1{{margin:0;font-size:clamp(30px,4vw,54px);line-height:.98;letter-spacing:-.055em;font-weight:850}}.eyebrow{{margin:6px 0 0;color:var(--muted);font-size:12px;letter-spacing:.12em;text-transform:uppercase}}h2{{margin:0 0 12px;font-size:15px;letter-spacing:.1em;text-transform:uppercase}}a{{color:#ff6573;text-decoration:none}}.muted{{color:var(--muted)}}.tabs{{display:flex;gap:8px;margin:0 0 8px}}.tab{{border:1px solid var(--line);background:var(--glass);color:var(--muted);border-radius:999px;padding:9px 14px;font-weight:800;cursor:pointer}}.tab.active{{background:var(--red-soft);border-color:rgba(236,38,56,.5);color:#fff}}.tab-panel[hidden]{{display:none}}.day-card{{margin-top:20px;padding:18px;border:1px solid var(--line);border-radius:18px;background:var(--glass);box-shadow:var(--shadow);backdrop-filter:blur(18px)}}.table-wrap{{overflow:auto;border:1px solid var(--line);border-radius:12px}}table{{width:100%;min-width:1120px;border-collapse:collapse;background:rgba(7,7,8,.38)}}th,td{{padding:16px;vertical-align:top;text-align:left;border-bottom:1px solid rgba(255,255,255,.08)}}th{{font-size:11px;letter-spacing:.1em;text-transform:uppercase;color:#bbb3b6;background:rgba(255,255,255,.045)}}td:first-child{{white-space:nowrap;color:var(--muted);width:165px}}td:nth-child(2){{width:31%}}td:nth-child(3){{width:35%}}.source-images{{display:flex;gap:8px;flex-wrap:wrap;margin-top:10px}}.source-image{{width:84px;height:84px;object-fit:cover;border-radius:8px;border:1px solid var(--line)}}.final-image{{display:block;width:172px;height:172px;object-fit:cover;border-radius:10px;border:1px solid rgba(236,38,56,.42);margin-top:12px}}.copy{{max-width:540px}}.release-inline{{display:flex;align-items:center;gap:9px;flex-wrap:wrap;margin-top:12px}}.status{{display:inline-block;padding:3px 8px;border-radius:999px;font-size:10px;font-weight:850;letter-spacing:.08em}}.published{{background:var(--red-soft);color:#ff8993;border:1px solid rgba(236,38,56,.35)}}.pending{{background:rgba(255,255,255,.08);color:#d0cbcd}}.tracking-cell{{min-width:292px;font-size:12px}}.tracking-values{{display:flex;gap:5px;flex-wrap:wrap}}.metric-chip{{display:inline-flex;align-items:center;gap:4px;padding:4px 6px;border:1px solid rgba(255,255,255,.12);border-radius:7px;background:rgba(255,255,255,.045);white-space:nowrap}}.metric-icon{{color:#ff5a69}}.metric-label{{font-size:10px;color:var(--muted)}}.tracking-meta{{color:var(--muted);margin-top:8px;font-size:11px}}.tracking-state{{color:#ff8a95;font-weight:800}}.snapshots{{margin:7px 0;padding-left:18px;color:var(--muted);font-size:11px}}.metric-details{{margin-top:8px;border-top:1px solid rgba(255,255,255,.1);padding-top:7px}}.metric-details summary{{cursor:pointer;color:#ff8792;font-weight:750}}@media(max-width:700px){{main{{padding:20px 12px 44px}}.masthead{{padding:15px;gap:12px}}.brand-logo{{width:43px;height:43px}}h1{{font-size:31px}}.day-card{{padding:10px}}.table-wrap{{overflow:visible;border:0}}table{{min-width:0;background:transparent}}thead{{display:none}}tbody,tr,td{{display:block;width:100%!important}}tbody tr{{padding:12px 0;border-bottom:1px solid rgba(255,255,255,.12)}}td{{padding:8px 2px;border:0}}td:before{{content:attr(data-label);display:block;margin-bottom:4px;color:#aaa1a5;font-size:10px;font-weight:800;letter-spacing:.09em;text-transform:uppercase}}td:first-child{{white-space:normal}}.final-image{{width:148px;height:148px}}.tracking-cell{{min-width:0}}}}
    </style></head><body><main><header class="masthead"><img class="brand-logo" src="{e(LOGO_URL)}" alt="when2buy logo"><div><h1>WHEN2BUY X CONTENT FACTORY</h1><p class="eyebrow">Daily source-to-release ledger · Postiz API-first metrics</p></div></header><nav class="tabs" aria-label="Package status"><button class="tab active" data-tab="completed">Completed</button><button class="tab" data-tab="ready">Ready / unpublished</button></nav><div class="tab-panel" id="completed">{completed}</div><div class="tab-panel" id="ready" hidden>{ready}</div></main><script>document.querySelectorAll('.tab').forEach(b=>b.onclick=()=>{{document.querySelectorAll('.tab').forEach(x=>x.classList.toggle('active',x===b));document.querySelectorAll('.tab-panel').forEach(x=>x.hidden=x.id!==b.dataset.tab)}})</script></body></html>'''
    OUT.parent.mkdir(parents=True, exist_ok=True)
    OUT.write_text(out + '\n', encoding='utf-8')
    print(f'Wrote {OUT}')

if __name__ == '__main__': main()
