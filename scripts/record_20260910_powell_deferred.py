#!/usr/bin/env python3
"""Persist the safe account-limiter deferral for the Powell package."""
from datetime import datetime, timezone
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "skills" / "when2buy-content-publisher" / "scripts"))
import state  # noqa: E402

document = state.load_state()
run_id = f"run-{datetime.now(timezone.utc).strftime('%Y%m%dT%H%M%SZ')}-publish-deferred"
stamp = datetime.now(timezone.utc).replace(microsecond=0).isoformat().replace("+00:00", "Z")
document["runs"].append({
    "id": run_id, "mode": "publish", "status": "succeeded", "startedAt": stamp, "completedAt": stamp,
    "summary": "The newest fresh package was safely deferred by the enforced minimum submission interval; no Postiz task was accepted and the ready package remains recoverable.",
    "reason": "minimum_interval; retryAt=2026-09-10T14:34:21Z",
    "packageId": "pkg-20260910-powell-maryland-waterfront-home", "outcome": "deferred",
})
errors = state.validate(document)
if errors: raise SystemExit("\n".join(errors))
state.atomic_write(document)
print(f"Recorded safe deferred outcome: {run_id}")
