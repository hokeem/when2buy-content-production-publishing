#!/usr/bin/env python3
"""Persist the safe delivery-throttle outcome for the 2026-09-10 run."""
from datetime import datetime, timezone
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "skills" / "when2buy-content-publisher" / "scripts"))
import state  # noqa: E402

RUN_ID = "run-20260910T094951Z-publish"

document = state.load_state()
if not any(item.get("id") == RUN_ID for item in document["runs"]):
    stamp = datetime.now(timezone.utc).replace(microsecond=0).isoformat().replace("+00:00", "Z")
    document["runs"].append({
        "id": RUN_ID,
        "mode": "publish",
        "status": "succeeded",
        "startedAt": stamp,
        "completedAt": stamp,
        "summary": "The sole fresh package was safely deferred by the enforced rolling 24-hour Postiz limit; no submission was accepted and the ready package remains recoverable for the next eligible cycle.",
        "reason": "daily_limit; retryAt=2026-09-10T10:21:00Z",
        "packageId": "pkg-20260910-palantir-nvidia-critical-supply-chains",
        "outcome": "deferred",
    })
errors = state.validate(document)
if errors:
    raise SystemExit("\n".join(errors))
state.atomic_write(document)
print(f"Recorded safe deferred outcome: {RUN_ID}")
