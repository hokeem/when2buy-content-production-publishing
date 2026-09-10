#!/usr/bin/env python3
"""Persist the safe pending-reconciliation outcome for this run."""
from datetime import datetime, timezone
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "skills" / "when2buy-content-publisher" / "scripts"))
import state  # noqa: E402

document = state.load_state()
stamp = datetime.now(timezone.utc).replace(microsecond=0).isoformat().replace("+00:00", "Z")
run_id = f"run-{stamp.replace('-', '').replace(':', '')}-publish"
document["runs"].append({
    "id": run_id,
    "mode": "publish",
    "status": "succeeded",
    "startedAt": stamp,
    "completedAt": stamp,
    "summary": "The newest fresh OpenAI government-access package was safely deferred because an accepted Postiz task remains within delayed-success reconciliation grace; no submission was accepted and the package remains recoverable.",
    "reason": "pending_delivery_reconciliation for pkg-20260910-walmart-papa-johns-delivery; no retry was made.",
    "selectedPackageIds": ["pkg-20260910-openai-government-access"],
    "outcome": "deferred",
})
errors = state.validate(document)
if errors:
    raise SystemExit("\n".join(errors))
state.atomic_write(document)
print(f"Recorded deferred delivery outcome: {run_id}")
