from datetime import datetime, timezone
from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "skills/when2buy-content-publisher/scripts"))
import state

now = datetime.now(timezone.utc).isoformat()
document = state.load_state()
document["runs"].append({
    "id": f"run-{datetime.now(timezone.utc).strftime('%Y%m%dT%H%M%SZ')}-deferred",
    "mode": "full",
    "status": "succeeded",
    "startedAt": now,
    "completedAt": now,
    "summary": "Fresh ETH package was safely deferred because the 15-minute Postiz minimum interval was active.",
    "reason": "minimum_interval",
    "selectedPackageId": "pkg-20260911-eth-75-percent-move",
    "outcome": "deferred",
})
errors = state.validate(document)
if errors:
    raise SystemExit("\n".join(errors))
state.atomic_write(document)
print("recorded deferred outcome")
