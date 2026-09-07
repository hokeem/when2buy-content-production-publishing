#!/usr/bin/env python3
"""Persist terminal Postiz delivery errors for this authorized run."""
from datetime import datetime, timezone
from pathlib import Path
import sys
ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "skills" / "when2buy-content-publisher" / "scripts"))
import state

ERROR = "Postiz returned state=ERROR with no releaseURL on two delivery attempts; no public x.com URL was issued."
IDS = {
    "pkg-20260905-howard-lutnick-disclosed-making-at-least-250m-in-80358",
    "pkg-20260905-just-in-fed-s-hammack-says-local-contacts-indica-35660",
}
def now(): return datetime.now(timezone.utc).isoformat()
def main():
    doc = state.load_state()
    for package in doc["packages"]:
        if package.get("id") in IDS:
            package["status"] = "failed"
            package["deliveryError"] = ERROR
            package["deliveryAttempts"] = 2
            package["deliveryFailedAt"] = now()
    doc["runs"].append({"id": f"run-{datetime.now(timezone.utc).strftime('%Y%m%dT%H%M%SZ')}-publish", "mode": "publish", "status": "partial", "startedAt": now(), "completedAt": now(), "summary": "Three packages published and verified; two packages reached terminal Postiz delivery errors.", "reason": ERROR})
    errors = state.validate(doc)
    if errors: raise SystemExit("\n".join(errors))
    state.atomic_write(doc)
if __name__ == "__main__": main()
