#!/usr/bin/env python3
'''Render a standalone, evidence-backed daily performance dashboard.'''
import html
from datetime import datetime, timedelta
from pathlib import Path
from zoneinfo import ZoneInfo

from analytics_common import cohort, cohort_stats, daily_summary, days_ending, load_state, parse_dt

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / 'reports' / 'metrics-dashboard.html'
TZ = ZoneInfo('Asia/Shanghai')
LOGO = 'https://raw.githubusercontent.com/hokeem/when2buy-content-production-publishing/main/skills/when2buy-content-publisher/assets/when2buy-logo-reference.png'
FACTORY = 'https://reports.aitist.ai/when2buy/content-run-panel/'
WEEKLY = 'https://reports.aitist.ai/when2buy/weekly-content-analysis/'


def e(value): return html.escape(str(value if value is not None else '—'), quote=True)
def number(value):
    if not isinstance(value, (int, float)):
        return '—'
    return f'{int(value):,}' if float(value).is_integer() else f'{value:,.1f}'
def pct(value): return f'{value * 100:.0f}%' if isinstance(value, (int, float)) else '—'


def bar_chart(rows):
    width, height, left, top, bottom = 920, 250, 46, 18, 42
    values = [row['published'] for row in rows]
    peak = max(values + [1]); step = (width - left - 18) / max(len(rows), 1); bars = []
    for index, row in enumerate(rows):
        bar_h = (height - top - bottom) * row['published'] / peak
        x = left + index * step + step * .18; y = height - bottom - bar_h
        bars.append(f'<rect x="{x:.1f}" y="{y:.1f}" width="{step*.64:.1f}" height="{bar_h:.1f}" rx="5" fill="#ef3348"><title>{e(row["date"])}: {row["published"]} posts</title></rect>')
        bars.append(f'<text x="{x+step*.32:.1f}" y="{height-17}" text-anchor="middle">{e(row["date"][5:])}</text>')
        if row['published']: bars.append(f'<text class="value" x="{x+step*.32:.1f}" y="{max(y-7,12):.1f}" text-anchor="middle">{row["published"]}</text>')
    return f'<svg class="chart" viewBox="0 0 {width} {height}" role="img" aria-label="Posts published per day"><line x1="{left}" y1="{height-bottom}" x2="{width-12}" y2="{height-bottom}" stroke="#554a4e"/>{"".join(bars)}</svg>'


def line_chart(rows):
    width, height, left, top, bottom = 920, 250, 58, 24, 42
    values = [row['views'] if row['known'] else 0 for row in rows]
    peak = max(values + [1]); step = (width - left - 22) / max(len(rows) - 1, 1); points = []; labels = []
    for index, row in enumerate(rows):
        x = left + index * step; y = height - bottom - (height-top-bottom) * values[index] / peak
        points.append((x, y, row)); labels.append(f'<text x="{x:.1f}" y="{height-17}" text-anchor="middle">{e(row["date"][5:])}</text>')
    polyline = ' '.join(f'{x:.1f},{y:.1f}' for x,y,_ in points)
    dots = ''.join(f'<circle cx="{x:.1f}" cy="{y:.1f}" r="5" fill="#fff" stroke="#ef3348" stroke-width="3"><title>{e(row["date"])}: {number(row["views"]) if row["known"] else "no measured views"}</title></circle>' for x,y,row in points)
    return f'<svg class="chart" viewBox="0 0 {width} {height}" role="img" aria-label="Current measured views grouped by publication day"><line x1="{left}" y1="{height-bottom}" x2="{width-12}" y2="{height-bottom}" stroke="#554a4e"/><polyline points="{polyline}" fill="none" stroke="#ef3348" stroke-width="4" stroke-linecap="round" stroke-linejoin="round"/>{dots}{"".join(labels)}</svg>'


def main():
    state = load_state(); today = datetime.now(TZ).date(); dates = days_ending(today, 14); daily = daily_summary(state, dates)
    state_updated = parse_dt(state.get('updatedAt')); updated_label = (state_updated.astimezone(TZ) if state_updated else datetime.now(TZ)).strftime('%Y-%m-%d %H:%M')
    current = cohort(state, today - timedelta(days=6), today); stats = cohort_stats(current)
    top = sorted(current, key=lambda row: (row['metrics'].get('views', -1), row['post'].get('publishedAt', '')), reverse=True)[:10]
    kpis = f'''<section class="kpis"><article><span>Published · 7d</span><b>{stats["published"]:,}</b></article><article><span>Known views · 7d cohort</span><b>{stats["views"]:,}</b></article><article><span>Interactions · latest known</span><b>{stats["interactions"]:,}</b></article><article><span>View-data coverage</span><b>{pct(stats["coverage"])}</b><small>{stats["known"]}/{stats["published"]} posts</small></article></section>'''
    daily_rows = ''.join(f'''<tr><td>{e(row["date"])}</td><td>{row["captured"]:,}</td><td>{row["produced"]:,}</td><td><strong>{row["published"]:,}</strong></td><td>{number(row["views"]) if row["known"] else "—"}</td><td>{number(row["avgViews"])}</td><td>{row["likes"]:,}</td><td>{row["replies"]:,}</td><td>{row["reposts"]:,}</td><td>{pct(row["coverage"])}</td></tr>''' for row in reversed(daily))
    top_rows = ''.join(f'''<tr><td>{index}</td><td><a href="{e(row["post"].get("url"))}" target="_blank" rel="noreferrer">{e(row["package"].get("title") or row["post"].get("title") or row["post"].get("id"))}</a><small>{e(row["post"].get("publishedAt"))}</small></td><td>{number(row["metrics"].get("views"))}</td><td>{number(row["metrics"].get("likes"))}</td><td>{number(row["metrics"].get("replies"))}</td><td>{number(row["metrics"].get("reposts"))}</td></tr>''' for index,row in enumerate(top,1)) or '<tr><td colspan="6">No published posts in this window.</td></tr>'
    out = f'''<!doctype html><html lang="en"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1"><link rel="icon" type="image/png" href="{LOGO}"><title>WHEN2BUY PERFORMANCE</title><style>
:root{{--bg:#080809;--ink:#f7f4f5;--muted:#a69da0;--red:#ef3348;--glass:rgba(24,20,22,.72);--line:rgba(255,255,255,.11);--shadow:0 24px 70px rgba(0,0,0,.38)}}*{{box-sizing:border-box}}body{{margin:0;background:radial-gradient(circle at 5% 0,#4b111b 0,transparent 28rem),radial-gradient(circle at 100% 5%,#271015 0,transparent 30rem),linear-gradient(145deg,#070708,#111012 55%,#070708);color:var(--ink);font:14px/1.55 ui-sans-serif,system-ui,-apple-system,"Segoe UI",sans-serif}}main{{max-width:1420px;margin:auto;padding:36px 22px 70px}}header,.panel,.kpis article{{border:1px solid var(--line);background:var(--glass);backdrop-filter:blur(20px);box-shadow:var(--shadow)}}header{{display:flex;gap:16px;align-items:center;flex-wrap:wrap;padding:20px 22px;border-radius:22px}}header img{{width:58px;height:58px;object-fit:contain;background:#050506;border:1px solid rgba(239,51,72,.45);border-radius:15px;padding:5px}}h1{{font-size:clamp(31px,5vw,58px);letter-spacing:-.055em;line-height:.94;margin:0}}.eyebrow,small{{display:block;color:var(--muted)}}nav{{display:flex;gap:8px;margin-left:auto;flex-wrap:wrap}}nav a{{color:#fff;text-decoration:none;padding:9px 13px;border:1px solid var(--line);border-radius:999px;background:rgba(255,255,255,.05)}}nav a.active{{border-color:var(--red);background:rgba(239,51,72,.15)}}.kpis{{display:grid;grid-template-columns:repeat(4,1fr);gap:10px;margin:18px 0}}.kpis article{{padding:17px;border-radius:16px}}.kpis span{{color:var(--muted);font-size:12px;text-transform:uppercase;letter-spacing:.08em}}.kpis b{{display:block;font-size:34px;margin-top:7px}}.grid{{display:grid;grid-template-columns:1fr 1fr;gap:14px}}.panel{{padding:19px;border-radius:19px;margin-top:14px;overflow:hidden}}h2{{margin:0 0 4px;font-size:18px}}.note{{margin:0 0 12px;color:var(--muted);font-size:12px}}.chart{{width:100%;height:auto;overflow:visible}}.chart text{{fill:#988f92;font-size:11px}}.chart .value{{fill:#fff;font-weight:800}}.table-wrap{{overflow:auto;border:1px solid var(--line);border-radius:12px}}table{{width:100%;border-collapse:collapse;min-width:850px}}th,td{{padding:12px 13px;text-align:left;border-bottom:1px solid rgba(255,255,255,.08)}}th{{font-size:10px;letter-spacing:.08em;text-transform:uppercase;color:#afa6a9;background:rgba(255,255,255,.04)}}td a{{color:#ff6e7d;text-decoration:none}}footer{{color:var(--muted);font-size:12px;margin:18px 4px}}@media(max-width:850px){{.grid{{grid-template-columns:1fr}}.kpis{{grid-template-columns:repeat(2,1fr)}}nav{{width:100%;margin-left:0}}}}@media(max-width:520px){{main{{padding:18px 10px 44px}}.kpis{{grid-template-columns:1fr 1fr}}.kpis b{{font-size:26px}}}}
</style></head><body><main><header><img src="{LOGO}" alt="when2buy logo"><div><div class="eyebrow">Evidence-backed daily analytics</div><h1>WHEN2BUY PERFORMANCE</h1><small>Updated {e(updated_label)} Asia/Shanghai</small></div><nav><a href="{FACTORY}">Content Factory</a><a class="active" href="#">Performance</a><a href="{WEEKLY}">Weekly Analysis</a></nav></header>{kpis}<section class="grid"><article class="panel"><h2>Daily publishing volume</h2><p class="note">Published posts by Asia/Shanghai calendar day · last 14 days</p>{bar_chart(daily)}</article><article class="panel"><h2>Views by publication day</h2><p class="note">Latest attributable views for posts released that day; missing metrics are not converted to zero in totals.</p>{line_chart(daily)}</article></section><section class="panel"><h2>Daily operating detail</h2><p class="note">Captured, produced and published counts are exact state totals. Performance uses the latest numeric, source-attributed snapshot per post.</p><div class="table-wrap"><table><thead><tr><th>Date</th><th>Captured</th><th>Produced</th><th>Published</th><th>Views</th><th>Avg views</th><th>Likes</th><th>Replies</th><th>Reposts</th><th>Coverage</th></tr></thead><tbody>{daily_rows}</tbody></table></div></section><section class="panel"><h2>Top content · latest 7 days</h2><p class="note">Ranked only by latest known views. A dash means no attributable metric is currently available.</p><div class="table-wrap"><table><thead><tr><th>#</th><th>Post</th><th>Views</th><th>Likes</th><th>Replies</th><th>Reposts</th></tr></thead><tbody>{top_rows}</tbody></table></div></section><footer>Method: newest source-attributed numeric observation per post. Metrics are collected during the first 72 hours; coverage is shown beside every aggregate so missing data cannot inflate or silently depress reported results.</footer></main></body></html>'''
    OUT.parent.mkdir(parents=True, exist_ok=True); OUT.write_text(out + '\n', encoding='utf-8'); print(f'Wrote {OUT}')

if __name__ == '__main__': main()
