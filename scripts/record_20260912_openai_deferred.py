from datetime import datetime, timezone
import sys
from pathlib import Path
ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "skills/when2buy-content-publisher/scripts"))
import state
now = datetime.now(timezone.utc).replace(microsecond=0).isoformat().replace("+00:00", "Z")
doc = state.load_state()
doc["runs"].append({"id": "run-" + now.replace("-", "").replace(":", "") + "-full", "mode": "full", "status": "succeeded", "startedAt": now, "completedAt": now, "summary": "Newest OpenAI public-listing package was produced and safely deferred by the Postiz account limit; no accepted task was created.", "reason": "daily_limit", "selectedPackageId": "pkg-20260912-openai-public-listing", "outcome": "deferred", "metrics": "not first run of hour; no new observations required"})
errors = state.validate(doc)
if errors: raise SystemExit("\n".join(errors))
state.atomic_write(doc)
print("Deferred full-run outcome persisted.")
