#!/usr/bin/env python3
"""Record the 11:45 UTC factory result after the delivery safety gate stopped submission."""

from datetime import datetime, timezone
from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "skills" / "when2buy-content-publisher" / "scripts"))
import state  # noqa: E402


def stamp():
    return datetime.now(timezone.utc).isoformat()


def main():
    document = state.load_state()
    document["runs"].append({
        "id": f"run-{datetime.now(timezone.utc).strftime('%Y%m%dT%H%M%SZ')}-full",
        "mode": "full",
        "status": "partial",
        "startedAt": stamp(),
        "completedAt": stamp(),
        "summary": "Apify collection, media archive, duplicate exclusion, freshness queue rebuild, validation, and reporting completed; publication was withheld before submission by the active 60-minute delivery circuit breaker.",
        "reason": "The Postiz delivery guard found a recent verified X release inside the 60-minute safety window; no API submission was attempted.",
        "selectedPackageIds": [
            "pkg-20260909-fidelity-clarity-act-september-15",
            "pkg-20260909-fed-officials-fewer-policy-meetings",
        ],
    })
    errors = state.validate(document)
    if errors:
        raise SystemExit("\n".join(errors))
    state.atomic_write(document)


if __name__ == "__main__":
    main()
