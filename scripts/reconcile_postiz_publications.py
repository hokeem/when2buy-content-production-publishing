#!/usr/bin/env python3
"""Reconcile Postiz deliveries without misclassifying delayed X success."""

import argparse
import fcntl
import json
import sys
from datetime import datetime, timedelta, timezone
from pathlib import Path
from urllib.parse import urlencode

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "skills" / "when2buy-content-publisher" / "scripts"))
import state  # noqa: E402
sys.path.insert(0, str(ROOT / "scripts"))
from postiz_api import request_json  # noqa: E402
from postiz_delivery_policy import delivery_error_is_terminal, iso, limits_from_env  # noqa: E402


def normalized(value):
    return " ".join(str(value or "").split())


def is_x_delivery(item):
    integration = item.get("integration") or {}
    provider = integration.get("providerIdentifier") or integration.get("identifier")
    return provider == "x" or "twitter.com/" in str(item.get("releaseURL", "")) or "x.com/" in str(item.get("releaseURL", ""))


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--lookback-hours", type=int, default=72)
    parser.add_argument("--dry-run", action="store_true")
    args = parser.parse_args()
    now = datetime.now(timezone.utc)
    start = now - timedelta(hours=max(1, args.lookback_hours))
    query = urlencode({"startDate": iso(start), "endDate": iso(now + timedelta(minutes=5))})
    deliveries = request_json("/posts?" + query).get("posts", [])
    grace_minutes = limits_from_env()["errorGraceMinutes"]

    with Path("/tmp/when2buy-state.lock").open("a+", encoding="utf-8") as lock:
        fcntl.flock(lock.fileno(), fcntl.LOCK_EX)
        document = state.load_state()
        known_postiz = {post.get("postizPostId") for post in document.get("posts", [])}
        known_release = {str(post.get("id")) for post in document.get("posts", [])}
        package_by_postiz = {package.get("postizPostId"): package for package in document.get("packages", []) if package.get("postizPostId")}
        package_by_text = {}
        for package in document.get("packages", []):
            package_by_text.setdefault(normalized(package.get("postText")), []).append(package)

        appended = []
        failed = []
        pending = []
        changed = False
        for item in deliveries:
            if not is_x_delivery(item):
                continue
            postiz_id = item.get("id")
            release_id = str(item.get("releaseId") or "")
            exact_package = package_by_postiz.get(postiz_id)
            matches = package_by_text.get(normalized(item.get("content")), [])
            package = exact_package or (matches[0] if matches else None)

            if item.get("state") in ("ERROR", "FAILED") and exact_package and exact_package.get("status") == "publishing":
                first_error = exact_package.get("firstDeliveryErrorAt") or iso(now)
                observations = {
                    "postizPostId": postiz_id,
                    "deliveryState": item.get("state"),
                    "deliveryCheckedAt": iso(now),
                    "firstDeliveryErrorAt": first_error,
                    "deliveryError": "Postiz reported a downstream delivery error; delayed-success reconciliation remains active.",
                }
                if delivery_error_is_terminal(exact_package, at=now, grace_minutes=grace_minutes):
                    observations.update({"status": "failed", "deliveryFailedAt": iso(now)})
                    failed.append(exact_package.get("id"))
                else:
                    observations["status"] = "publishing"
                    pending.append(exact_package.get("id"))
                exact_package.update(observations)
                changed = True
                continue

            if item.get("state") != "PUBLISHED" or not item.get("releaseURL") or not release_id:
                continue
            if postiz_id in known_postiz or release_id in known_release:
                if package and package.get("status") != "published":
                    package.update({
                        "status": "published", "postizPostId": postiz_id,
                        "publishedAt": item.get("publishDate") or iso(now),
                        "deliveryState": "PUBLISHED", "deliveryCheckedAt": iso(now),
                    })
                    changed = True
                continue

            published_at = item.get("publishDate") or iso(now)
            published = datetime.fromisoformat(published_at.replace("Z", "+00:00"))
            public_url = item["releaseURL"].replace("twitter.com", "x.com")
            if package:
                package.update({
                    "status": "published", "postizPostId": postiz_id, "publishedAt": published_at,
                    "deliveryState": "PUBLISHED", "deliveryCheckedAt": iso(now),
                })
                for key in ("deliveryError", "firstDeliveryErrorAt", "deliveryGraceUntil", "deliveryFailedAt", "expiredAt", "expiryReason", "sourceExpiresAt"):
                    package.pop(key, None)
            sibling = next((post for post in document.get("posts", []) if package and post.get("packageId") == package.get("id")), None)
            record = {
                "id": release_id, "packageId": package.get("id") if package else f"postiz-unmapped-{postiz_id}",
                "title": package.get("title", "") if package else "", "text": item.get("content", ""),
                "status": "published", "publishedAt": published_at, "url": public_url, "postizPostId": postiz_id,
                "metricsTracking": {
                    "status": "active" if now < published + timedelta(hours=72) else "complete",
                    "windowStart": published_at, "windowEnd": iso(published + timedelta(hours=72)),
                },
                "reconciledAt": iso(now),
            }
            if sibling:
                record["duplicateOfPostId"] = sibling.get("id")
            document.setdefault("posts", []).append(record)
            known_postiz.add(postiz_id)
            known_release.add(release_id)
            appended.append(release_id)
            changed = True

        if appended or failed:
            document.setdefault("runs", []).append({
                "id": now.strftime("run-%Y%m%dT%H%M%SZ-reconcile"), "mode": "publish", "status": "succeeded",
                "startedAt": iso(now), "completedAt": iso(datetime.now(timezone.utc)),
                "summary": f"Reconciled {len(appended)} published, {len(pending)} pending, and {len(failed)} terminal Postiz deliveries.",
                "reason": "",
            })
        if changed:
            errors = state.validate(document)
            if errors:
                raise SystemExit("\n".join(errors))
            if not args.dry_run:
                state.atomic_write(document)

    print(json.dumps({
        "publishedAdded": len(appended), "pendingObserved": len(pending), "failedUpdated": len(failed),
        "releaseIds": appended, "dryRun": args.dry_run,
    }, sort_keys=True))


if __name__ == "__main__":
    main()
