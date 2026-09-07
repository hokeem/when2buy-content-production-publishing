#!/usr/bin/env python3
"""Record a terminal Postiz failure after safe delivery retries."""
import argparse
from datetime import datetime, timezone
from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "skills" / "when2buy-content-publisher" / "scripts"))
import state  # noqa: E402

parser = argparse.ArgumentParser()
parser.add_argument("--package-id", required=True)
parser.add_argument("--reason", required=True)
args = parser.parse_args()
document = state.load_state()
package = next(x for x in document["packages"] if x.get("id") == args.package_id)
package["status"] = "failed"
package["deliveryError"] = args.reason
now = datetime.now(timezone.utc).isoformat()
document["runs"].append({"id": f"run-{datetime.now(timezone.utc).strftime('%Y%m%dT%H%M%SZ')}-publish", "mode": "publish", "status": "partial", "startedAt": now, "completedAt": now, "summary": "Postiz delivery reached a terminal error after safe retries.", "reason": args.reason})
errors = state.validate(document)
if errors: raise SystemExit("\n".join(errors))
state.atomic_write(document)
print(f"Recorded terminal delivery error: {args.package_id}")
