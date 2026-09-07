#!/usr/bin/env python3
"""Render and update stable when2buy report pages without registry lookup."""
import argparse
import subprocess
import sys
from pathlib import Path

ROOT=Path(__file__).resolve().parents[1]
TARGETS=(
    (ROOT/'reports'/'run-panel.html','content-run-panel'),
    (ROOT/'reports'/'metrics-dashboard.html','performance-dashboard'),
)
WEEKLY=(ROOT/'reports'/'weekly','weekly-content-analysis')

def publish(path,slug):
    subprocess.run(['report','publish',str(path),'--namespace','when2buy','--slug',slug,'--update'],cwd=ROOT,check=True)

def main():
    parser=argparse.ArgumentParser()
    parser.add_argument('--check-only',action='store_true')
    parser.add_argument('--weekly',action='store_true',help='also regenerate and publish the weekly archive')
    args=parser.parse_args()
    required=[ROOT/'scripts'/'render_metrics_dashboard.py',ROOT/'scripts'/'render_weekly_analysis.py',ROOT/'reports'/'run-panel.html']
    missing=[str(path.relative_to(ROOT)) for path in required if not path.exists()]
    if missing: raise SystemExit('Missing report input: '+', '.join(missing))
    if args.check_only:
        print('Stable content, performance, and weekly publishers are configured.')
        return
    subprocess.run([sys.executable,str(ROOT/'scripts'/'render_metrics_dashboard.py')],cwd=ROOT,check=True)
    if args.weekly: subprocess.run([sys.executable,str(ROOT/'scripts'/'render_weekly_analysis.py')],cwd=ROOT,check=True)
    for path,slug in TARGETS: publish(path,slug)
    if args.weekly: publish(*WEEKLY)

if __name__=='__main__': main()
