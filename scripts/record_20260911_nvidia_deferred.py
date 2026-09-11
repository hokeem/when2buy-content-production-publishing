#!/usr/bin/env python3
"""Persist the safe daily-limit deferral for the current production cycle."""
from datetime import datetime, timezone
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "skills" / "when2buy-content-publisher" / "scripts"))
import state

PACKAGE_ID = "pkg-20260911-nvidia-robotaxis-drive"

now = datetime.now(timezone.utc).isoformat()
document = state.load_state()
document["runs"].append({
    "id": f"run-{datetime.now(timezone.utc).strftime('%Y%m%dT%H%M%SZ')}-deferred",
    "mode": "full", "status": "succeeded", "startedAt": now, "completedAt": now,
    "summary": "Fresh NVIDIA robotaxi package was validated and safely deferred before submission because the rolling daily Postiz limit was exhausted.",
    "reason": "daily_limit", "selectedPackageId": PACKAGE_ID, "outcome": "deferred",
})
errors = state.validate(document)
if errors:
    raise SystemExit("\n".join(errors))
state.atomic_write(document)
print("Recorded deferred outcome for " + PACKAGE_ID)
