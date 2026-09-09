#!/usr/bin/env python3
"""Record the newly captured Brent alert as a duplicate of a verified release."""

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
    source = next(item for item in document["benchmarkPosts"] if str(item.get("id")) == "2097651141337100444")
    source["duplicateOf"] = "2097618775214276775"
    source["duplicateReason"] = "Same Brent-above-$100 event already covered by verified release 2097621274306789488."
    document["runs"].append({
        "id": f"run-{datetime.now(timezone.utc).strftime('%Y%m%dT%H%M%SZ')}-dedupe",
        "mode": "radar",
        "status": "succeeded",
        "startedAt": stamp(),
        "completedAt": stamp(),
        "summary": "Excluded one newly captured Brent-above-$100 duplicate from fresh production.",
        "reason": "The same event already has a verified public when2buy release.",
    })
    errors = state.validate(document)
    if errors:
        raise SystemExit("\n".join(errors))
    state.atomic_write(document)


if __name__ == "__main__":
    main()
