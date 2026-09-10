#!/usr/bin/env python3
"""Persist the safe deferred outcome for the ECB freshness run."""
from datetime import datetime, timezone
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "skills" / "when2buy-content-publisher" / "scripts"))
import state  # noqa: E402

RUN_ID = "run-20260910T150340Z-publish"
PACKAGE_ID = "pkg-20260910-ecb-three-rate-hikes"

document = state.load_state()
if not any(item.get("id") == RUN_ID for item in document["runs"]):
    stamp = datetime.now(timezone.utc).replace(microsecond=0).isoformat().replace("+00:00", "Z")
    document["runs"].append({
        "id": RUN_ID, "mode": "publish", "status": "succeeded",
        "startedAt": stamp, "completedAt": stamp,
        "summary": "The sole newest ECB package was safely deferred during the existing 60-minute Postiz reconciliation window; no task was accepted and the fresh package remains recoverable.",
        "reason": "pending_delivery_reconciliation; retryAt=2026-09-10T15:51:04Z",
        "packageId": PACKAGE_ID, "outcome": "deferred",
    })
errors = state.validate(document)
if errors:
    raise SystemExit("\n".join(errors))
state.atomic_write(document)
print(f"Recorded safe deferred outcome: {RUN_ID}")
