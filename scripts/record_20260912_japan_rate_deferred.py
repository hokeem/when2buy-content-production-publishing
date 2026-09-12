#!/usr/bin/env python3
from datetime import datetime, timezone
import sys
from pathlib import Path
ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "skills/when2buy-content-publisher/scripts"))
import state

PACKAGE_ID = "pkg-20260912-japan-rate-regime"
now = datetime.now(timezone.utc).replace(microsecond=0).isoformat().replace("+00:00", "Z")
doc = state.load_state()
run_id = "run-" + now.replace("-", "").replace(":", "") + "-deferred"
doc["runs"].append({"id": run_id, "mode": "full", "status": "succeeded", "startedAt": now, "completedAt": now, "summary": "Newest Japan-rate package was safely deferred before submission because the rolling 24-hour Postiz limit was exhausted; no accepted task was created and no retry is permitted.", "reason": "daily_limit; retryAt 2026-09-12T13:19:26Z", "selectedPackageId": PACKAGE_ID, "outcome": "deferred"})
errors = state.validate(doc)
if errors:
    raise SystemExit("\n".join(errors))
state.atomic_write(doc)
print("Deferred outcome persisted.")
