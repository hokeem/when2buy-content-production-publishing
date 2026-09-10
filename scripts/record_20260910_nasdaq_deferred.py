#!/usr/bin/env python3
"""Persist the safe Postiz delivery deferral for the current fresh package."""
from datetime import datetime, timezone
from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "skills" / "when2buy-content-publisher" / "scripts"))
import state  # noqa: E402

PACKAGE_ID = "pkg-20260910-nasdaq-payward-21b-valuation"

document = state.load_state()
stamp = datetime.now(timezone.utc).replace(microsecond=0).isoformat().replace("+00:00", "Z")
run_id = f"run-{stamp.replace('-', '').replace(':', '')}-publish"
if not any(item.get("packageId") == PACKAGE_ID and item.get("outcome") == "deferred" for item in document["runs"]):
    document["runs"].append({
        "id": run_id,
        "mode": "publish",
        "status": "succeeded",
        "startedAt": stamp,
        "completedAt": stamp,
        "summary": "The single newest fresh package was safely deferred by the enforced rolling 24-hour Postiz limit; no submission was accepted and the package remains recoverable before source expiry.",
        "reason": "daily_limit; retryAt=2026-09-10T12:14:00Z",
        "packageId": PACKAGE_ID,
        "outcome": "deferred",
    })
errors = state.validate(document)
if errors:
    raise SystemExit("\n".join(errors))
state.atomic_write(document)
print(f"Recorded safe deferred outcome: {PACKAGE_ID}")
