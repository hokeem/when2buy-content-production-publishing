#!/usr/bin/env python3
"""Persist the safe deferred Postiz outcome without changing package readiness."""
from datetime import datetime, timezone
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "skills" / "when2buy-content-publisher" / "scripts"))
import state  # noqa: E402

PACKAGE_ID = "pkg-20260910-kermit-grok-robinhood-chain"
now = datetime.now(timezone.utc).replace(microsecond=0)
stamp = now.isoformat().replace("+00:00", "Z")
document = state.load_state()
document["runs"].append({
    "id": f"run-{now.strftime('%Y%m%dT%H%M%SZ')}-publish-deferred",
    "mode": "publish", "status": "succeeded", "startedAt": stamp, "completedAt": stamp,
    "summary": "Newest fresh KERMIT package remained ready; Postiz safely deferred before acceptance because the rolling 24-hour limit is exhausted.",
    "reason": "daily_limit; retryAt=2026-09-10T21:50:00Z",
    "packageId": PACKAGE_ID, "outcome": "deferred", "selectedPackageIds": [PACKAGE_ID],
})
errors = state.validate(document)
if errors: raise SystemExit("\n".join(errors))
state.atomic_write(document)
print("Recorded safe deferred outcome.")
