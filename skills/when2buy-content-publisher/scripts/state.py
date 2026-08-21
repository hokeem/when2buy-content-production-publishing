#!/usr/bin/env python3
import argparse
import json
import os
import re
import tempfile
from datetime import datetime, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parents[3]
STATE_PATH = ROOT / "data" / "state.json"
REQUIRED_ARRAYS = ("benchmarks", "radar", "packages", "posts", "metricSnapshots", "experiments", "runs")

def load_state():
    return json.loads(STATE_PATH.read_text(encoding="utf-8"))

def validate(state):
    errors = []
    if state.get("version") != 1:
        errors.append("version must be 1")
    if not isinstance(state.get("updatedAt"), str):
        errors.append("updatedAt must be a string")
    account = state.get("account")
    if not isinstance(account, dict) or not account.get("handle") or not account.get("timezone"):
        errors.append("account.handle and account.timezone are required")
    for key in REQUIRED_ARRAYS:
        if not isinstance(state.get(key), list):
            errors.append(f"{key} must be an array")
    for post in state.get("posts", []):
        if post.get("status") == "published" and not re.fullmatch(r"https://x\.com/[^/]+/status/\d+", post.get("url", "")):
            errors.append(f"published post {post.get('id', '<unknown>')} lacks a valid X status URL")
    seen = set()
    for snap in state.get("metricSnapshots", []):
        sid = snap.get("id")
        if not sid or sid in seen:
            errors.append(f"metric snapshot id is missing or duplicated: {sid}")
        seen.add(sid)
    return errors

def atomic_write(state):
    state["updatedAt"] = datetime.now(timezone.utc).isoformat()
    STATE_PATH.parent.mkdir(parents=True, exist_ok=True)
    fd, name = tempfile.mkstemp(prefix="state-", suffix=".json", dir=STATE_PATH.parent)
    try:
        with os.fdopen(fd, "w", encoding="utf-8") as handle:
            json.dump(state, handle, ensure_ascii=False, indent=2)
            handle.write("\n")
        os.replace(name, STATE_PATH)
    finally:
        if os.path.exists(name):
            os.unlink(name)

def append_record(collection, payload_path):
    state = load_state()
    payload = json.loads(Path(payload_path).read_text(encoding="utf-8"))
    if not isinstance(payload, dict) or not payload.get("id"):
        raise SystemExit("payload must be an object with an id")
    if any(item.get("id") == payload["id"] for item in state[collection]):
        raise SystemExit(f"duplicate id in {collection}: {payload['id']}")
    state[collection].append(payload)
    errors = validate(state)
    if errors:
        raise SystemExit("\n".join(errors))
    atomic_write(state)
    print(f"appended {payload['id']} to {collection}")

def main():
    parser = argparse.ArgumentParser(description="Validate or append to when2buy state")
    sub = parser.add_subparsers(dest="command", required=True)
    sub.add_parser("validate")
    append = sub.add_parser("append")
    append.add_argument("collection", choices=("radar", "packages", "posts", "metricSnapshots", "experiments", "runs"))
    append.add_argument("json_file")
    args = parser.parse_args()
    if args.command == "validate":
        errors = validate(load_state())
        if errors:
            raise SystemExit("\n".join(errors))
        print(f"State valid: {STATE_PATH}")
    else:
        append_record(args.collection, args.json_file)

if __name__ == "__main__":
    main()
