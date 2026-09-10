#!/usr/bin/env python3
"""Publish at most one package per scheduled cycle."""

import argparse
import json
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


def run(command):
    return subprocess.run(command, cwd=ROOT, text=True, capture_output=True)


def last_json(output):
    try:
        return json.loads(output.strip().splitlines()[-1])
    except (IndexError, json.JSONDecodeError):
        return {"output": output[-800:]}


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--package-id", action="append", required=True)
    parser.add_argument("--confirm", action="store_true")
    args = parser.parse_args()
    package_ids = list(dict.fromkeys(args.package_id))
    if not args.confirm:
        raise SystemExit("Refusing to publish without --confirm.")
    if len(package_ids) > 1:
        raise SystemExit("Reliability policy allows at most one X submission per scheduled cycle.")

    reconciliation = run([sys.executable, "scripts/reconcile_postiz_publications.py", "--lookback-hours", "72"])
    if reconciliation.returncode:
        raise SystemExit("Pre-publish Postiz reconciliation failed: " + reconciliation.stderr[-800:])
    guard = run([sys.executable, "scripts/postiz_publish.py", "--delivery-check-only"])
    if guard.returncode:
        result = {"requested": 1, "results": [{"packageId": package_ids[0], "status": "deferred", **last_json(guard.stdout)}]}
        print(json.dumps(result, ensure_ascii=False))
        return 0

    completed = run([sys.executable, "scripts/postiz_publish.py", "--package-id", package_ids[0], "--confirm"])
    if completed.returncode == 2:
        result = {"packageId": package_ids[0], **last_json(completed.stdout)}
    elif completed.returncode == 3:
        result = {"packageId": package_ids[0], **last_json(completed.stdout)}
    elif completed.returncode:
        error = completed.stderr[-800:]
        if "STALE_PACKAGE:" in error:
            result = {"packageId": package_ids[0], "status": "expired", "reason": error.strip()}
        else:
            result = {"packageId": package_ids[0], "status": "failed", "error": error}
    else:
        result = {"packageId": package_ids[0], **last_json(completed.stdout)}

    print(json.dumps({"requested": 1, "results": [result]}, ensure_ascii=False))
    if result.get("status") == "failed":
        return 1
    return 0


if __name__ == "__main__":
    sys.exit(main())
