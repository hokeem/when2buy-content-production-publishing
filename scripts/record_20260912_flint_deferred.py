from datetime import datetime, timezone
from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "skills/when2buy-content-publisher/scripts"))
import state

now = datetime.now(timezone.utc).replace(microsecond=0).isoformat().replace("+00:00", "Z")
doc = state.load_state()
doc["runs"].append({
    "id": "run-" + now.replace("-", "").replace(":", "") + "-publish-deferred",
    "mode": "publish", "status": "succeeded", "startedAt": now, "completedAt": now,
    "summary": "Newest fresh Flint-area $2.9M home package was safely deferred by the Postiz daily account limit; no accepted task was created and no retry is permitted.",
    "reason": "daily_limit; retryAt=2026-09-12T13:19:26Z",
    "selectedPackageId": "pkg-20260912-flint-29m-home", "outcome": "deferred",
})
errors = state.validate(doc)
if errors:
    raise SystemExit("\n".join(errors))
state.atomic_write(doc)
print("Deferred outcome persisted.")
