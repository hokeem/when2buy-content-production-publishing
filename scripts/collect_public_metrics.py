#!/usr/bin/env python3
"""Append attributable public-X metrics for Postiz-published posts during their first 72 hours."""
import argparse
import html
import json
import re
import sys
from datetime import datetime, timedelta, timezone
from pathlib import Path
from urllib.error import HTTPError, URLError
from urllib.request import Request, urlopen

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / 'skills' / 'when2buy-content-publisher' / 'scripts'))
import state

FIELDS = ('views', 'replies', 'reposts', 'likes')

def parse_time(value):
    return datetime.fromisoformat(str(value).replace('Z', '+00:00'))

def number(value):
    raw = value.replace(',', '').upper()
    multiplier = {'K': 1_000, 'M': 1_000_000, 'B': 1_000_000_000}.get(raw[-1:], 1)
    return int(float(raw[:-1] if multiplier != 1 else raw) * multiplier)

def visible_metrics(body):
    page = re.sub(r'\s+', ' ', html.unescape(body))
    patterns = {
        'views': r'([\d,.]+[KMB]?)\s+Views\b',
        'replies': r'([\d,.]+[KMB]?)\s+Replies\b',
        'reposts': r'([\d,.]+[KMB]?)\s+Reposts\b',
        'likes': r'([\d,.]+[KMB]?)\s+Likes\b',
    }
    values = {}
    for field, pattern in patterns.items():
        match = re.search(pattern, page, re.I)
        values[field] = number(match.group(1)) if match else None
    return values

def public_check(url, timeout):
    request = Request(url, headers={'User-Agent': 'Mozilla/5.0 (compatible; when2buy-metrics/1.0)'})
    try:
        with urlopen(request, timeout=timeout) as response:
            body = response.read().decode('utf-8', 'replace')
            metrics = visible_metrics(body)
            return metrics, f'HTTP {response.status}; parsed visible public counters only.'
    except HTTPError as error:
        return {field: None for field in FIELDS}, f'HTTP {error.code}; no visible public counters were returned.'
    except URLError as error:
        return {field: None for field in FIELDS}, f'Public X request failed: {error.reason}.'

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--dry-run', action='store_true')
    parser.add_argument('--timeout', type=int, default=20)
    args = parser.parse_args()
    now = datetime.now(timezone.utc)
    snapshot_day = now.date().isoformat()
    data = state.load_state()
    snapshots_by_post = {}
    for snapshot in data.get('metricSnapshots', []):
        snapshots_by_post.setdefault(str(snapshot.get('postId')), []).append(snapshot)
    changed = False
    queried = []
    completed = []
    skipped = []
    for post in data.get('posts', []):
        if post.get('status') != 'published' or not post.get('postizPostId') or not post.get('url') or not post.get('publishedAt'):
            continue
        published_at = parse_time(post['publishedAt'])
        deadline = published_at + timedelta(hours=72)
        tracking = post.setdefault('metricsTracking', {'windowStart': published_at.isoformat(), 'windowEnd': deadline.isoformat(), 'status': 'active'})
        if now > deadline:
            if tracking.get('status') != 'complete':
                tracking.update({'status': 'complete', 'completedAt': now.isoformat(), 'reason': '72-hour public-metrics window elapsed; no further fetches permitted.'})
                changed = True
            completed.append(post['id'])
            continue
        tracking['status'] = 'active'
        tracking['windowStart'] = published_at.isoformat()
        tracking['windowEnd'] = deadline.isoformat()
        existing = snapshots_by_post.get(str(post['id']), [])
        if any(str(item.get('observedAt', '')).startswith(snapshot_day) for item in existing):
            skipped.append(post['id'])
            continue
        if args.dry_run:
            queried.append(post['id'])
            continue
        values, result = public_check(post['url'], args.timeout)
        observed_at = datetime.now(timezone.utc).isoformat()
        snapshot = {
            'id': f"{post['id']}-{datetime.now(timezone.utc).strftime('%Y%m%dT%H%M%SZ')}",
            'postId': str(post['id']),
            'observedAt': observed_at,
            **values,
            'evidence': {'source': 'public X status page', 'url': post['url'], 'checkedAt': observed_at, 'result': result},
            'observation': 'Only visibly attributable public counters were recorded; unavailable counters remain null.',
        }
        data['metricSnapshots'].append(snapshot)
        snapshots_by_post.setdefault(str(post['id']), []).append(snapshot)
        tracking['lastAttemptAt'] = observed_at
        changed = True
        queried.append(post['id'])
    if args.dry_run:
        print(json.dumps({'wouldQuery': queried, 'alreadyCheckedToday': skipped, 'trackingComplete': completed}, indent=2))
        return
    errors = state.validate(data)
    if errors:
        raise SystemExit('\n'.join(errors))
    if changed:
        state.atomic_write(data)
    print(json.dumps({'queried': queried, 'alreadyCheckedToday': skipped, 'trackingComplete': completed, 'stateChanged': changed}, indent=2))

if __name__ == '__main__':
    main()
