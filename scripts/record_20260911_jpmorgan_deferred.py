from datetime import datetime, timezone
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "skills/when2buy-content-publisher/scripts"))
import state

now = datetime.now(timezone.utc).replace(microsecond=0).isoformat().replace("+00:00", "Z")
doc = state.load_state()
doc["runs"].append({
    "id": "run-" + now.replace("-", "").replace(":", "") + "-publish-deferred",
    "mode": "publish", "status": "succeeded", "startedAt": now, "completedAt": now,
    "summary": "Newest fresh JPMorgan/Situational Awareness package remained ready; Postiz safely deferred before acceptance because the 15-minute submission interval was active.",
    "reason": "minimum_interval; retryAt=2026-09-11T21:04:06Z",
    "selectedPackageId": "pkg-20260911-jpmorgan-situational-awareness-lending", "outcome": "deferred",
})
errors = state.validate(doc)
if errors:
    raise SystemExit("\n".join(errors))
state.atomic_write(doc)
print("Deferred outcome persisted.")
