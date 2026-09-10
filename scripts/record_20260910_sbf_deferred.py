#!/usr/bin/env python3
from datetime import datetime, timezone
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "skills" / "when2buy-content-publisher" / "scripts"))
import state

stamp = datetime.now(timezone.utc).replace(microsecond=0).isoformat().replace("+00:00", "Z")
document = state.load_state()
document["runs"].append({
    "id": f"run-{datetime.now(timezone.utc).strftime('%Y%m%dT%H%M%SZ')}-publish-deferred",
    "mode": "publish", "status": "succeeded", "startedAt": stamp, "completedAt": stamp,
    "summary": "Newest fresh SBF Supreme Court package remained ready; Postiz safely deferred before acceptance because the 15-minute submission interval was not open.",
    "reason": "minimum_interval; retryAt=2026-09-10T20:50:31Z; no retry made",
    "selectedPackageIds": ["pkg-20260910-sbf-supreme-court"], "outcome": "deferred",
})
errors = state.validate(document)
if errors:
    raise SystemExit("\n".join(errors))
state.atomic_write(document)
print("Recorded safe deferred outcome.")
