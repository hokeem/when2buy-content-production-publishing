#!/usr/bin/env python3
"""Append attributable metrics for published when2buy posts for their first 72h.

Postiz analytics is the primary source.  Public X status pages are only a
secondary fallback and never create an observation unless a visible numeric
counter was actually parsed.
"""
import argparse
import html
import json
import math
import os
import re
import sys
from datetime import datetime, timedelta, timezone
from pathlib import Path
from urllib.error import HTTPError, URLError
from urllib.parse import urlencode
from urllib.request import Request, urlopen

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / 'skills' / 'when2buy-content-publisher' / 'scripts'))
import state  # noqa: E402

POSTIZ_BASE = os.getenv('POSTIZ_BASE_URL', 'https://api.postiz.com/public/v1').rstrip('/')
CORE_FIELDS = ('views', 'replies', 'reposts', 'likes')
LABEL_MAP = {
    'impressions': 'views', 'views': 'views', 'view': 'views',
    'replies': 'replies', 'reply': 'replies', 'comments': 'replies', 'comment': 'replies',
    'retweets': 'reposts', 'retweet': 'reposts', 'reposts': 'reposts', 'repost': 'reposts',
    'shares': 'reposts', 'share': 'reposts',
    'likes': 'likes', 'like': 'likes',
    'bookmarks': 'bookmarks', 'bookmark': 'bookmarks', 'saves': 'bookmarks', 'save': 'bookmarks',
}


def now_utc():
    return datetime.now(timezone.utc)


def iso(value):
    return value.astimezone(timezone.utc).isoformat().replace('+00:00', 'Z')


def as_datetime(value):
    if not value:
        return None
    try:
        parsed = datetime.fromisoformat(str(value).replace('Z', '+00:00'))
        return parsed if parsed.tzinfo else parsed.replace(tzinfo=timezone.utc)
    except ValueError:
        return None


def parse_number(value):
    if isinstance(value, (int, float)):
        return int(value)
    if not isinstance(value, str):
        return None
    match = re.fullmatch(r'\s*([0-9]+(?:\.[0-9]+)?)\s*([KMBkmb]?)\s*', value.replace(',', ''))
    if not match:
        return None
    multiplier = {'': 1, 'k': 1_000, 'm': 1_000_000, 'b': 1_000_000_000}[match.group(2).lower()]
    return int(float(match.group(1)) * multiplier)


def api_get(path, query):
    key = os.getenv('POSTIZ_API_KEY')
    if not key:
        raise RuntimeError('POSTIZ_API_KEY is unavailable in the local credential paths')
    url = POSTIZ_BASE + path + '?' + urlencode(query)
    request = Request(url, headers={'Authorization': key, 'Accept': 'application/json'})
    with urlopen(request, timeout=25) as response:
        return json.loads(response.read().decode('utf-8'))


def postiz_metrics(postiz_id, days):
    """Fetch Postiz analytics and retain the label-to-dashboard field evidence."""
    endpoint = f'/analytics/post/{postiz_id}'
    try:
        payload = api_get(endpoint, {'date': days})
    except (HTTPError, URLError, RuntimeError, json.JSONDecodeError) as exc:
        return None, {'source': 'Postiz public API', 'endpoint': endpoint, 'query': {'date': days}, 'result': f'failed: {type(exc).__name__}'}, str(exc)

    values = {}
    field_map = {}
    for series in payload if isinstance(payload, list) else []:
        label = str(series.get('label', '')).strip()
        target = LABEL_MAP.get(label.lower())
        points = series.get('data') if isinstance(series.get('data'), list) else []
        valid = [point for point in points if isinstance(point, dict) and parse_number(point.get('total')) is not None]
        if not target or not valid:
            continue
        point = sorted(valid, key=lambda item: str(item.get('date', '')))[-1]
        values[target] = parse_number(point.get('total'))
        field_map[target] = {'sourceLabel': label, 'analyticsDate': point.get('date')}

    evidence = {
        'source': 'Postiz public API', 'endpoint': endpoint, 'query': {'date': days},
        'postizPostId': postiz_id, 'fieldMap': field_map,
        'result': 'analytics labels mapped to dashboard fields',
    }
    if values:
        return values, evidence, None
    evidence['result'] = 'no usable mapped analytics values'
    return None, evidence, 'Postiz returned no usable mapped analytics values'


def public_x_metrics(url):
    """Secondary fallback only; all-null parsing is not an observation."""
    if not isinstance(url, str) or not url.startswith('https://'):
        return None, {'source': 'public X status page', 'result': 'no public URL'}, 'no public URL'
    try:
        request = Request(url, headers={'User-Agent': 'Mozilla/5.0 (compatible; when2buy-metrics/1.0)'})
        with urlopen(request, timeout=25) as response:
            page = html.unescape(response.read().decode('utf-8', errors='replace'))
    except (HTTPError, URLError) as exc:
        return None, {'source': 'public X status page', 'url': url, 'result': f'failed: {type(exc).__name__}'}, str(exc)

    values = {}
    patterns = {
        'views': r'([0-9][0-9,\.]*[KMBkmb]?)\s+(?:Views|views)',
        'replies': r'([0-9][0-9,\.]*[KMBkmb]?)\s+(?:Replies|replies)',
        'reposts': r'([0-9][0-9,\.]*[KMBkmb]?)\s+(?:Reposts|Retweets|reposts|retweets)',
        'likes': r'([0-9][0-9,\.]*[KMBkmb]?)\s+(?:Likes|likes)',
    }
    for field, pattern in patterns.items():
        match = re.search(pattern, page)
        if match:
            parsed = parse_number(match.group(1))
            if parsed is not None:
                values[field] = parsed
    evidence = {'source': 'public X status page', 'url': url, 'result': 'visible numeric counters parsed'}
    if values:
        return values, evidence, None
    evidence['result'] = 'no visible numeric counters parsed; no observation recorded'
    return None, evidence, 'public X did not expose any parseable numeric counters'


def has_successful_snapshot(snapshots, post_id, checked_day):
    for item in snapshots:
        if str(item.get('postId')) != str(post_id):
            continue
        observed = as_datetime(item.get('observedAt'))
        if observed and observed.date().isoformat() == checked_day and any(item.get(field) is not None for field in CORE_FIELDS):
            return True
    return False


def snapshot(post_id, observed_at, values, evidence):
    return {
        'id': f"metric-{post_id}-{observed_at.strftime('%Y%m%dT%H%M%SZ')}",
        'postId': post_id, 'observedAt': iso(observed_at),
        **values, 'evidence': {**evidence, 'checkedAt': iso(observed_at)},
    }


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--dry-run', action='store_true')
    args = parser.parse_args()
    document = state.load_state()
    current = now_utc()
    changed = False
    summary = {'queriedPostiz': 0, 'postizSnapshots': 0, 'xFallbackSnapshots': 0, 'noObservation': 0, 'complete': 0, 'skippedToday': 0}

    for post in document.get('posts', []):
        if post.get('status') != 'published' or not post.get('postizPostId'):
            continue
        published = as_datetime(post.get('publishedAt'))
        if not published:
            continue
        tracking = post.setdefault('metricsTracking', {})
        deadline = published + timedelta(hours=72)
        if current >= deadline:
            if tracking.get('status') != 'complete':
                tracking.update({'status': 'complete', 'windowStart': iso(published), 'windowEnd': iso(deadline), 'completedAt': iso(current), 'completionReason': '72h tracking window ended'})
                changed = True
            summary['complete'] += 1
            continue
        if tracking.get('status') == 'complete':
            summary['complete'] += 1
            continue
        if tracking.get('status') != 'active' or tracking.get('windowStart') != iso(published) or tracking.get('windowEnd') != iso(deadline):
            tracking.update({'status': 'active', 'windowStart': iso(published), 'windowEnd': iso(deadline)})
            changed = True
        if has_successful_snapshot(document.get('metricSnapshots', []), post.get('id'), current.date().isoformat()):
            summary['skippedToday'] += 1
            continue

        age_days = max(1, min(3, math.ceil((current - published).total_seconds() / 86400)))
        if args.dry_run:
            print(f"would query Postiz analytics for {post.get('id')} ({post.get('postizPostId')}, date={age_days})")
            continue
        summary['queriedPostiz'] += 1
        values, evidence, postiz_error = postiz_metrics(post.get('postizPostId'), age_days)
        tracking.update({'lastAttemptAt': iso(current), 'lastAttemptSource': 'Postiz public API'})
        if values is not None:
            document.setdefault('metricSnapshots', []).append(snapshot(post.get('id'), current, values, evidence))
            tracking['lastAttemptResult'] = 'metrics captured from Postiz public API'
            changed = True
            summary['postizSnapshots'] += 1
            continue

        fallback_values, fallback_evidence, fallback_error = public_x_metrics(post.get('url'))
        tracking['lastAttemptSource'] = 'Postiz public API → public X fallback'
        if fallback_values is not None:
            document.setdefault('metricSnapshots', []).append(snapshot(post.get('id'), current, fallback_values, fallback_evidence))
            tracking['lastAttemptResult'] = 'Postiz unavailable/empty; metrics captured from public X fallback'
            changed = True
            summary['xFallbackSnapshots'] += 1
        else:
            tracking['lastAttemptResult'] = f'no observation appended: Postiz={postiz_error}; public X={fallback_error}'
            changed = True
            summary['noObservation'] += 1

    if args.dry_run:
        print(json.dumps(summary, sort_keys=True))
        return
    if changed:
        state.validate(document)
        state.atomic_write(document)
    print(json.dumps({**summary, 'changed': changed}, sort_keys=True))


if __name__ == '__main__':
    main()
