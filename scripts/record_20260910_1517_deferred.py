#!/usr/bin/env python3
from datetime import datetime, timezone
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "skills" / "when2buy-content-publisher" / "scripts"))
import state

now = datetime.now(timezone.utc).replace(microsecond=0).isoformat().replace("+00:00", "Z")
document = state.load_state()
document["runs"].append({
    "id": f"run-{now.replace('-', '').replace(':', '')}-publish-deferred",
    "mode": "publish", "status": "succeeded", "startedAt": now, "completedAt": now,
    "summary": "Newest fresh ACA-rebate package remained ready; Postiz batch safely deferred without an accepted submission.",
    "reason": "pending_delivery_reconciliation for pkg-20260910-walmart-papa-johns-delivery; no retry was made.",
    "selectedPackageIds": ["pkg-20260910-aca-500-rebates"], "outcome": "deferred",
})
errors = state.validate(document)
if errors:
    raise SystemExit("\n".join(errors))
state.atomic_write(document)
print("Recorded deferred delivery outcome.")
