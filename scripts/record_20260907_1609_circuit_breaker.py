#!/usr/bin/env python3
"""Record the still-active Postiz circuit breaker without retrying an accepted task."""
from datetime import datetime, timezone
from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "skills" / "when2buy-content-publisher" / "scripts"))
import state  # noqa: E402


def stamp():
    return datetime.now(timezone.utc).isoformat().replace("+00:00", "Z")


def main():
    document = state.load_state()
    now = stamp()
    document["runs"].append({
        "id": f"run-{datetime.now(timezone.utc).strftime('%Y%m%dT%H%M%SZ')}-publish",
        "mode": "publish", "status": "partial", "startedAt": now, "completedAt": now,
        "summary": "No Postiz submission: the required 60-minute X delivery circuit breaker remains active; the newest gasoline package remains ready.",
        "reason": "Postiz query at 2026-09-07T16:09:01Z returned no X deliveries in its supplied window, but the accepted X delivery cmtreano20dp3lm0y93qswru7 was previously observed ERROR at 2026-09-07T15:28:00Z with releaseURL null. The recorded 60-minute breaker remains active until 2026-09-07T16:28:00Z; do not submit or retry an accepted task.",
        "circuitBreaker": {
            "active": True, "observedAt": now, "expiresAt": "2026-09-07T16:28:00Z",
            "deliveryReason": "ERROR delivery without a public release URL",
        },
    })
    errors = state.validate(document)
    if errors:
        raise SystemExit("\n".join(errors))
    state.atomic_write(document)


if __name__ == "__main__":
    main()
