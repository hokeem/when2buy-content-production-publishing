#!/usr/bin/env python3
"""Publish up to five packages sequentially; never parallelize X delivery."""
import argparse
import json
import subprocess
import sys
import time
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


def run(command):
    return subprocess.run(command, cwd=ROOT, text=True, capture_output=True)


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--package-id', action='append', required=True)
    parser.add_argument('--confirm', action='store_true')
    parser.add_argument('--interval-seconds', type=int, default=90)
    args = parser.parse_args()
    package_ids = list(dict.fromkeys(args.package_id))
    if not args.confirm:
        raise SystemExit('Refusing to publish without --confirm.')
    if len(package_ids) > 5:
        raise SystemExit('A batch may contain at most five packages.')

    reconciliation = run([sys.executable, 'scripts/reconcile_postiz_publications.py', '--lookback-hours', '72'])
    if reconciliation.returncode:
        raise SystemExit('Pre-publish Postiz reconciliation failed: ' + reconciliation.stderr[-800:])
    guard = run([sys.executable, 'scripts/postiz_publish.py', '--delivery-check-only'])
    if guard.returncode:
        raise SystemExit('Pre-publish delivery guard failed: ' + guard.stderr[-800:])

    results = []
    for index, package_id in enumerate(package_ids):
        completed = run([sys.executable, 'scripts/postiz_publish.py', '--package-id', package_id, '--confirm'])
        if completed.returncode:
            results.append({'packageId': package_id, 'status': 'failed', 'error': completed.stderr[-800:]})
            break
        try:
            payload = json.loads(completed.stdout.strip().splitlines()[-1])
        except (IndexError, json.JSONDecodeError):
            payload = {'output': completed.stdout[-800:]}
        results.append({'packageId': package_id, 'status': 'published', **payload})
        if index + 1 < len(package_ids):
            time.sleep(max(30, args.interval_seconds))

    print(json.dumps({'requested': len(package_ids), 'results': results}, ensure_ascii=False))
    if len(results) != len(package_ids) or any(item['status'] != 'published' for item in results):
        raise SystemExit(1)


if __name__ == '__main__':
    main()
