#!/usr/bin/env python3
"""Record a fail-closed stable report synchronization result."""
from datetime import datetime, timezone
from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "skills" / "when2buy-content-publisher" / "scripts"))
import state  # noqa: E402

def now(): return datetime.now(timezone.utc).isoformat()

document = state.load_state()
stamp = now()
document["runs"].append({
    "id": f"run-{datetime.now(timezone.utc).strftime('%Y%m%dT%H%M%SZ')}-report",
    "mode": "report", "status": "blocked", "startedAt": stamp, "completedAt": stamp,
    "summary": "Rendered local report artifacts; stable report update did not run.",
    "reason": "Terminal panel blocker: report-hub registry returned HTTP 401 after loading /root/.report-skill/tokens.env; no existing slug could be resolved, so no public destination was created or changed.",
})
errors = state.validate(document)
if errors: raise SystemExit("\n".join(errors))
state.atomic_write(document)
print("Recorded fail-closed stable-report synchronization result.")
