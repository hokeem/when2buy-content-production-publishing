from datetime import datetime, timezone
from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "skills/when2buy-content-publisher/scripts"))
import state

now = datetime.now(timezone.utc)
doc = state.load_state()
doc["runs"].append({
    "id": f"run-{now.strftime('%Y%m%dT%H%M%SZ')}-deferred",
    "mode": "full", "status": "succeeded", "startedAt": now.isoformat(), "completedAt": now.isoformat(),
    "summary": "Newest Micron package was safely deferred because the minimum Postiz submission interval was active.",
    "reason": "minimum_interval", "selectedPackageId": "pkg-20260911-micron-taiwan-bonus", "outcome": "deferred"
})
errors = state.validate(doc)
if errors:
    raise SystemExit("\n".join(errors))
state.atomic_write(doc)
print("recorded")
