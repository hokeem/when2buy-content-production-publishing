#!/usr/bin/env python3
"""Keep package delivery status consistent with verified public post records."""

import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "skills" / "when2buy-content-publisher" / "scripts"))
import state  # noqa: E402


def main():
    current = state.load_state()
    published_package_ids = {
        post.get("packageId")
        for post in current.get("posts", [])
        if post.get("status") == "published" and post.get("url")
    }
    repaired = []
    for package in current.get("packages", []):
        if package.get("id") not in published_package_ids or package.get("status") == "published":
            continue
        package["status"] = "published"
        package.pop("expiredAt", None)
        package.pop("expiryReason", None)
        package.pop("sourceExpiresAt", None)
        repaired.append(package.get("id"))
    errors = state.validate(current)
    if errors:
        raise SystemExit("\n".join(errors))
    if repaired:
        state.atomic_write(current)
    print(f"Reconciled {len(repaired)} package status(es).")


if __name__ == "__main__":
    main()
