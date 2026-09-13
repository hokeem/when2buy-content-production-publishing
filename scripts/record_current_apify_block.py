#!/usr/bin/env python3
"""Record a recoverable partial run when the required Apify scan is unavailable."""
from datetime import datetime, timezone
from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "skills" / "when2buy-content-publisher" / "scripts"))
import state  # noqa: E402

now = datetime.now(timezone.utc)
stamp = now.isoformat(timespec="seconds").replace("+00:00", "Z")
run = {
    "id": f"run-{now.strftime('%Y%m%dT%H%M%SZ')}-full",
    "mode": "full",
    "status": "partial",
    "startedAt": stamp,
    "completedAt": stamp,
    "summary": "Preflight, state validation, Postiz reconciliation, and queue rebuild completed; required Apify benchmark collection was blocked before any source or package write.",
    "reason": "Apify returned HTTP 403 platform-feature-disabled: Monthly usage hard limit exceeded while collecting @WhaleInsider. No publication attempted; next scheduled run should retry collection after the external limit is restored.",
    "selectedPackageIds": [],
    "collection": {"accounts": ["WhaleInsider", "StockMKTNewz"], "status": "blocked", "error": "HTTP 403 platform-feature-disabled: Monthly usage hard limit exceeded"},
}
document = state.load_state()
document["runs"].append(run)
errors = state.validate(document)
if errors:
    raise SystemExit("\n".join(errors))
state.atomic_write(document)
print("Recorded recoverable partial run.")
