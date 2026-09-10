#!/usr/bin/env python3
"""Record a safe Postiz deferral without changing the ready package."""
from datetime import datetime, timezone
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "skills" / "when2buy-content-publisher" / "scripts"))
import state  # noqa: E402

PACKAGE_ID = "pkg-20260910-robloxians-traction"

doc = state.load_state()
stamp = datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%SZ")
now = datetime.now(timezone.utc).isoformat()
doc["runs"].append({
    "id": f"run-{stamp}-publish",
    "mode": "publish",
    "status": "succeeded",
    "startedAt": now,
    "completedAt": now,
    "summary": "Safely deferred the newest fresh Roblox-themed package because the rolling 24-hour Postiz limit was exhausted; no submission was accepted.",
    "reason": "daily_limit; retryAt=2026-09-10T19:32:00Z",
    "selectedPackageIds": [PACKAGE_ID],
    "publishOutcome": "deferred",
    "retryAt": "2026-09-10T19:32:00Z",
})
errors = state.validate(doc)
if errors:
    raise SystemExit("\n".join(errors))
state.atomic_write(doc)
print("recorded deferred outcome")
