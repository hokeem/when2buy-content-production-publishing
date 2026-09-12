#!/usr/bin/env python3
"""Persist a safe Postiz defer without creating a retryable delivery."""
from datetime import datetime, timezone
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "skills" / "when2buy-content-publisher" / "scripts"))
import state  # noqa: E402

now = datetime.now(timezone.utc).replace(microsecond=0).isoformat().replace("+00:00", "Z")
doc = state.load_state()
doc["runs"].append({
    "id": "run-" + now.replace("-", "").replace(":", "") + "-deferred",
    "mode": "full",
    "status": "succeeded",
    "startedAt": now,
    "completedAt": now,
    "summary": "Newest Anthropic slowdown package was safely deferred before submission because the rolling 24-hour Postiz limit was exhausted; no accepted task was created and no retry is permitted.",
    "reason": "daily_limit; retryAt 2026-09-12T16:18:39Z",
    "selectedPackageId": "pkg-20260912-anthropic-slowdown-rogue-agents",
    "outcome": "deferred",
})
errors = state.validate(doc)
if errors:
    raise SystemExit("\n".join(errors))
state.atomic_write(doc)
print("Deferred outcome persisted.")
