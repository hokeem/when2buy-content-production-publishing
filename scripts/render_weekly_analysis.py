#!/usr/bin/env python3
'''Generate an archived weekly content analysis from the latest seven days.'''
import html
import shutil
import statistics
from collections import defaultdict
from datetime import datetime, timedelta
from pathlib import Path
from zoneinfo import ZoneInfo

from analytics_common import category, cohort, cohort_stats, load_state, strengths, time_band

ROOT=Path(__file__).resolve().parents[1]
OUT_DIR=ROOT/'reports'/'weekly'
TZ=ZoneInfo('Asia/Shanghai')
LOGO='https://raw.githubusercontent.com/hokeem/when2buy-content-production-publishing/main/skills/when2buy-content-publisher/assets/when2buy-logo-reference.png'
FACTORY='https://reports.aitist.ai/when2buy/content-run-panel/'
PERFORMANCE='https://reports.aitist.ai/when2buy/performance-dashboard/'

def e(value): return html.escape(str(value if value is not None else '—'),quote=True)
def num(value):
    if not isinstance(value, (int, float)):
        return '—'
    return f'{int(value):,}' if float(value).is_integer() else f'{value:,.1f}'
def pct(value): return f'{value*100:.0f}%' if isinstance(value,(int,float)) else '—'
def delta(current,previous):
    if not previous: return '—'
    value=(current-previous)/previous
    return ('+' if value>=0 else '')+f'{value*100:.1f}%'

def grouped_medians(items,key):
    grouped=defaultdict(list)
    for row in items:
        views=row['metrics'].get('views')
        if isinstance(views,int): grouped[key(row)].append(views)
    return sorted(((label,len(values),statistics.median(values)) for label,values in grouped.items()),key=lambda x:x[2],reverse=True)

def main():
    state=load_state(); today=datetime.now(TZ).date(); start=today-timedelta(days=6); previous_end=start-timedelta(days=1); previous_start=previous_end-timedelta(days=6)
    current=cohort(state,start,today); previous=cohort(state,previous_start,previous_end); now_stats=cohort_stats(current); prev_stats=cohort_stats(previous)
    ranked=sorted(current,key=lambda row:(row['metrics'].get('views',-1),row['post'].get('publishedAt','')),reverse=True)[:10]
    category_stats=grouped_medians(current,category); time_stats=grouped_medians(current,time_band)
    best_category=category_stats[0][0] if category_stats else None; best_band=time_stats[0][0] if time_stats else None
    top_rows=''.join(f'''<tr><td>{index}</td><td><a href="{e(row['post'].get('url'))}" target="_blank" rel="noreferrer">{e(row['package'].get('title') or row['post'].get('title') or row['post'].get('id'))}</a><small>{e(row['post'].get('publishedAt'))} · {e(category(row))}</small></td><td>{num(row['metrics'].get('views'))}</td><td>{num(sum(row['metrics'].get(field,0) for field in ('likes','replies','reposts')))}</td><td>{e(', '.join(strengths(row)))}</td></tr>''' for index,row in enumerate(ranked,1)) or '<tr><td colspan="5">No posts published in this seven-day window.</td></tr>'
    category_rows=''.join(f'<tr><td>{e(label)}</td><td>{count}</td><td>{num(median)}</td></tr>' for label,count,median in category_stats) or '<tr><td colspan="3">Insufficient measured data</td></tr>'
    time_rows=''.join(f'<tr><td>{e(label)}</td><td>{count}</td><td>{num(median)}</td></tr>' for label,count,median in time_stats) or '<tr><td colspan="3">Insufficient measured data</td></tr>'
    actions=[]
    if best_category: actions.append(f'Keep {best_category} as a priority test lane; it has the highest measured median in this sample. Do not infer causality until the sample grows.')
    else: actions.append('Restore metric coverage before changing topic strategy; the current sample cannot support a category conclusion.')
    if best_band: actions.append(f'Concentrate the next timing test around {best_band}, while preserving the newest-first rule.')
    else: actions.append('Keep the 20-minute fast-follow schedule until enough measured posts exist for a timing comparison.')
    if now_stats['coverage'] is None or now_stats['coverage']<.8: actions.append(f'Raise 7-day view coverage from {pct(now_stats["coverage"])} toward 80%+ by keeping Postiz API collection active at 24/48/72 hours.')
    actions.append('Change only one major variable per test—publish timing, copy order, or visual composition—so the following weekly review remains interpretable.')
    action_html=''.join(f'<li>{e(item)}</li>' for item in actions)
    period=f'{start.isoformat()} → {today.isoformat()}'
    week_slug=f'{today.isocalendar().year}-W{today.isocalendar().week:02d}'
    out=f'''<!doctype html><html lang="en"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1"><link rel="icon" type="image/png" href="{LOGO}"><title>WHEN2BUY WEEKLY CONTENT ANALYSIS</title><style>
:root{{--ink:#f8f5f6;--muted:#aaa0a3;--red:#ef3348;--glass:rgba(24,20,22,.74);--line:rgba(255,255,255,.11)}}*{{box-sizing:border-box}}body{{margin:0;background:radial-gradient(circle at 4% 0,#4c111c 0,transparent 30rem),linear-gradient(145deg,#070708,#121012 60%,#070708);color:var(--ink);font:14px/1.58 ui-sans-serif,system-ui,-apple-system,"Segoe UI",sans-serif}}main{{max-width:1320px;margin:auto;padding:36px 22px 70px}}header,.panel,.stat{{border:1px solid var(--line);background:var(--glass);backdrop-filter:blur(20px);box-shadow:0 24px 70px rgba(0,0,0,.38)}}header{{display:flex;align-items:center;gap:16px;flex-wrap:wrap;padding:21px;border-radius:22px}}header img{{width:58px;height:58px;object-fit:contain;border-radius:15px;background:#050506;border:1px solid rgba(239,51,72,.45);padding:5px}}h1{{margin:0;font-size:clamp(30px,5vw,55px);letter-spacing:-.05em;line-height:.95}}.eyebrow,small,.note{{display:block;color:var(--muted)}}nav{{display:flex;gap:8px;margin-left:auto;flex-wrap:wrap}}nav a{{color:#fff;text-decoration:none;border:1px solid var(--line);padding:9px 13px;border-radius:999px;background:rgba(255,255,255,.05)}}nav .active{{border-color:var(--red);background:rgba(239,51,72,.15)}}.stats{{display:grid;grid-template-columns:repeat(4,1fr);gap:10px;margin:18px 0}}.stat{{padding:17px;border-radius:16px}}.stat span{{font-size:11px;text-transform:uppercase;color:var(--muted);letter-spacing:.08em}}.stat b{{display:block;font-size:31px;margin-top:6px}}.stat small{{color:#ff7280}}.panel{{margin-top:14px;padding:19px;border-radius:19px}}h2{{margin:0 0 4px;font-size:19px}}.grid{{display:grid;grid-template-columns:1fr 1fr;gap:14px}}.table-wrap{{overflow:auto;border:1px solid var(--line);border-radius:12px;margin-top:12px}}table{{width:100%;border-collapse:collapse;min-width:650px}}th,td{{padding:12px 13px;text-align:left;border-bottom:1px solid rgba(255,255,255,.08);vertical-align:top}}th{{color:#afa6a9;font-size:10px;text-transform:uppercase;letter-spacing:.08em;background:rgba(255,255,255,.04)}}a{{color:#ff6e7d}}li{{margin:8px 0}}footer{{color:var(--muted);font-size:12px;margin:18px 4px}}@media(max-width:820px){{.stats,.grid{{grid-template-columns:1fr 1fr}}nav{{width:100%;margin-left:0}}}}@media(max-width:560px){{main{{padding:18px 10px 44px}}.stats,.grid{{grid-template-columns:1fr}}}}
</style></head><body><main><header><img src="{LOGO}" alt="when2buy logo"><div><div class="eyebrow">Seven-day evidence review · {e(period)}</div><h1>WEEKLY CONTENT ANALYSIS</h1><small>Generated {e(datetime.now(TZ).strftime('%Y-%m-%d %H:%M'))} Asia/Shanghai</small></div><nav><a href="{FACTORY}">Content Factory</a><a href="{PERFORMANCE}">Performance</a><a class="active" href="#">Weekly Analysis</a></nav></header><section class="stats"><article class="stat"><span>Published</span><b>{now_stats['published']}</b><small>vs prior 7d {delta(now_stats['published'],prev_stats['published'])}</small></article><article class="stat"><span>Known views</span><b>{num(now_stats['views'])}</b><small>vs prior cohort {delta(now_stats['views'],prev_stats['views'])}</small></article><article class="stat"><span>Median views</span><b>{num(now_stats['medianViews'])}</b><small>measured posts only</small></article><article class="stat"><span>View coverage</span><b>{pct(now_stats['coverage'])}</b><small>{now_stats['known']}/{now_stats['published']} posts</small></article></section><section class="panel"><h2>Top 10 content</h2><p class="note">Ranked by latest attributable views inside the seven-day cohort. Strengths describe observable execution traits, not assumed causal drivers.</p><div class="table-wrap"><table><thead><tr><th>#</th><th>Content</th><th>Views</th><th>Interactions</th><th>Observable strengths</th></tr></thead><tbody>{top_rows}</tbody></table></div></section><section class="grid"><article class="panel"><h2>Topic mix performance</h2><p class="note">Median latest views · measured posts only</p><div class="table-wrap"><table><thead><tr><th>Category</th><th>Measured</th><th>Median views</th></tr></thead><tbody>{category_rows}</tbody></table></div></article><article class="panel"><h2>Publishing-window performance</h2><p class="note">Asia/Shanghai time bands · median latest views</p><div class="table-wrap"><table><thead><tr><th>Window</th><th>Measured</th><th>Median views</th></tr></thead><tbody>{time_rows}</tbody></table></div></article></section><section class="panel"><h2>Next-week optimization</h2><ol>{action_html}</ol></section><footer>Method: current seven calendar days versus the preceding seven, Asia/Shanghai. Each post contributes its latest numeric source-attributed snapshot. Metrics are collected for the first 72 hours, so newer posts may be less mature. Coverage and sample size are displayed; missing values are never treated as measured zero.</footer></main></body></html>'''
    OUT_DIR.mkdir(parents=True,exist_ok=True); archive=OUT_DIR/f'{week_slug}.html'; archive.write_text(out+'\n',encoding='utf-8'); shutil.copyfile(archive,OUT_DIR/'latest.html')
    files=sorted((path for path in OUT_DIR.glob('*.html') if path.name not in ('index.html','latest.html')),reverse=True)
    links=''.join(f'<li><a href="{e(path.name)}">{e(path.stem)}</a></li>' for path in files)
    index=f'''<!doctype html><html><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1"><title>WHEN2BUY WEEKLY ARCHIVE</title><style>body{{margin:0;background:#09090a;color:#f6f3f4;font:16px/1.6 system-ui;padding:40px}}main{{max-width:760px;margin:auto}}a{{color:#ff6374}}.card{{padding:24px;border:1px solid #392c30;border-radius:18px;background:#161315}}</style></head><body><main><div class="card"><h1>WHEN2BUY WEEKLY ARCHIVE</h1><p><a href="latest.html">Open latest analysis</a></p><ul>{links}</ul></div></main></body></html>'''
    (OUT_DIR/'index.html').write_text(index+'\n',encoding='utf-8'); print(f'Wrote {archive} and weekly archive index')

if __name__=='__main__': main()
