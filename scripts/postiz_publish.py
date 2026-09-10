#!/usr/bin/env python3
"""Submit one fresh package to Postiz and reconcile delayed X delivery safely."""

import argparse
import fcntl
import json
import mimetypes
import os
import subprocess
import sys
import time
import uuid
from datetime import datetime, timedelta
from pathlib import Path
from urllib.parse import urlencode

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "skills" / "when2buy-content-publisher" / "scripts"))
import state  # noqa: E402
sys.path.insert(0, str(ROOT / "scripts"))
from freshness_policy import freshness  # noqa: E402
from postiz_api import request_json  # noqa: E402
from postiz_delivery_policy import iso, limits_from_env, rate_limit_decision, utc_now  # noqa: E402
from validate_content_standard import validate_package  # noqa: E402

EXPECTED_HANDLE = os.getenv("WHEN2BUY_POSTIZ_HANDLE", "_When2buy")
STATE_LOCK = Path("/tmp/when2buy-state.lock")
SUBMIT_LOCK = Path("/tmp/when2buy-postiz-submit.lock")


def upload(path):
    boundary = "----when2buy" + uuid.uuid4().hex
    mime = mimetypes.guess_type(path.name)[0] or "application/octet-stream"
    body = (
        f'--{boundary}\r\nContent-Disposition: form-data; name="file"; filename="{path.name}"\r\n'
        f"Content-Type: {mime}\r\n\r\n"
    ).encode() + path.read_bytes() + f"\r\n--{boundary}--\r\n".encode()
    return request_json("/upload", method="POST", data=body, content_type=f"multipart/form-data; boundary={boundary}")


def is_x_delivery(item):
    integration = item.get("integration") or item.get("integrations") or {}
    encoded = json.dumps(integration).lower()
    return (
        '"identifier": "x"' in encoded
        or '"identifier":"x"' in encoded
        or '"provideridentifier": "x"' in encoded
        or '"provideridentifier":"x"' in encoded
        or "x.com" in str(item.get("releaseURL", ""))
        or "twitter.com" in str(item.get("releaseURL", ""))
    )


def recent_x_deliveries(minutes=60):
    end = utc_now()
    query = urlencode({"startDate": iso(end - timedelta(minutes=minutes)), "endDate": iso(end + timedelta(minutes=5))})
    return [item for item in request_json("/posts?" + query).get("posts", []) if is_x_delivery(item)]


def update_package(package_id, **fields):
    with STATE_LOCK.open("a+", encoding="utf-8") as lock:
        fcntl.flock(lock.fileno(), fcntl.LOCK_EX)
        document = state.load_state()
        package = next((item for item in document.get("packages", []) if item.get("id") == package_id), None)
        if not package:
            raise SystemExit(f"Package disappeared from state: {package_id}")
        package.update(fields)
        errors = state.validate(document)
        if errors:
            raise SystemExit("\n".join(errors))
        state.atomic_write(document)


def record_accepted(package_id, postiz_id, submitted_at, delivery_state="QUEUE", error=None):
    limits = limits_from_env()
    fields = {
        "status": "publishing",
        "postizPostId": postiz_id,
        "postizSubmissionAt": iso(submitted_at),
        "deliveryState": delivery_state,
        "deliveryCheckedAt": iso(utc_now()),
        "deliveryGraceUntil": iso(submitted_at + timedelta(minutes=limits["errorGraceMinutes"])),
    }
    if error:
        fields["deliveryError"] = error
        fields["firstDeliveryErrorAt"] = iso(utc_now())
    update_package(package_id, **fields)


def finalize_published(package_id, released):
    with STATE_LOCK.open("a+", encoding="utf-8") as lock:
        fcntl.flock(lock.fileno(), fcntl.LOCK_EX)
        document = state.load_state()
        package = next((item for item in document.get("packages", []) if item.get("id") == package_id), None)
        if not package:
            raise SystemExit(f"Package disappeared from state: {package_id}")
        postiz_id = released["id"]
        existing = next((item for item in document.get("posts", []) if item.get("postizPostId") == postiz_id), None)
        if existing:
            return existing["url"]
        published_at = released.get("publishDate") or iso(utc_now())
        published_dt = datetime.fromisoformat(published_at.replace("Z", "+00:00"))
        public_url = released["releaseURL"].replace("twitter.com", "x.com")
        package.update({
            "status": "published", "postizPostId": postiz_id, "publishedAt": published_at,
            "deliveryState": "PUBLISHED", "deliveryCheckedAt": iso(utc_now()),
        })
        for key in ("deliveryError", "firstDeliveryErrorAt", "deliveryGraceUntil"):
            package.pop(key, None)
        document.setdefault("posts", []).append({
            "id": str(released["releaseId"]), "packageId": package["id"], "title": package.get("title", ""),
            "text": package.get("postText", ""), "status": "published", "publishedAt": published_at,
            "url": public_url, "postizPostId": postiz_id,
            "metricsTracking": {
                "status": "active", "windowStart": published_at,
                "windowEnd": iso(published_dt + timedelta(hours=72)),
                "lastAttemptAt": None, "lastAttemptSource": None, "lastAttemptResult": None,
            },
        })
        now = utc_now()
        document.setdefault("runs", []).append({
            "id": now.strftime("run-%Y%m%dT%H%M%SZ-publish"), "mode": "publish", "status": "succeeded",
            "startedAt": iso(now), "completedAt": iso(now),
            "summary": "Published through Postiz and verified a public X release URL.", "reason": "",
        })
        errors = state.validate(document)
        if errors:
            raise SystemExit("\n".join(errors))
        state.atomic_write(document)
        return public_url


def delivery_check_only():
    decision = rate_limit_decision(state.load_state())
    deliveries = recent_x_deliveries(60)
    unsafe = []
    now = utc_now()
    for item in deliveries:
        if item.get("state") in ("ERROR", "FAILED"):
            unsafe.append(item)
        elif item.get("state") == "QUEUE" and not item.get("releaseURL"):
            published = datetime.fromisoformat(str(item.get("publishDate", "")).replace("Z", "+00:00")) if item.get("publishDate") else now
            if now - published > timedelta(minutes=10):
                unsafe.append(item)
    def compact(item):
        return {key: item.get(key) for key in ("id", "state", "releaseURL", "publishDate")}
    result = {
        "windowMinutes": 60, "safe": decision["allowed"] and not unsafe, "rateLimit": decision,
        "xDeliveries": [compact(item) for item in deliveries], "unsafeDeliveries": [compact(item) for item in unsafe],
    }
    print(json.dumps(result, ensure_ascii=False))
    if not result["safe"]:
        raise SystemExit("Recent X delivery or account-level rate limit is unsafe; defer publication.")


def load_ready_package(package_id):
    document = state.load_state()
    package = next((item for item in document.get("packages", []) if item.get("id") == package_id), None)
    if not package or package.get("status") != "ready":
        raise SystemExit("Package must exist and be status=ready.")
    source = next((item for item in document.get("benchmarkPosts", []) if str(item.get("id")) == str(package.get("benchmarkPostId"))), None)
    source_freshness = freshness(source.get("postedAt") if source else None)
    if not source_freshness["eligible"]:
        stamp = iso(utc_now())
        package.update({
            "status": "expired", "expiredAt": stamp, "expiryReason": source_freshness["reason"],
            "sourceExpiresAt": source_freshness["expiresAt"],
        })
        document.setdefault("runs", []).append({
            "id": f"run-{utc_now().strftime('%Y%m%dT%H%M%SZ')}-expire", "mode": "publish", "status": "succeeded",
            "startedAt": stamp, "completedAt": stamp,
            "summary": f"Skipped stale package {package['id']}; no Postiz request was made.", "reason": source_freshness["reason"],
        })
        state.atomic_write(document)
        raise SystemExit(f"STALE_PACKAGE: source age {source_freshness['ageMinutes']}m exceeds {source_freshness['ttlMinutes']}m TTL")
    errors = validate_package(package)
    if errors:
        raise SystemExit("Content standard failed before Postiz call: " + "; ".join(errors))
    image = ROOT / package.get("imagePath", "")
    required = (package.get("postText"), package.get("benchmarkPostUrl"), package.get("mirroredFacts"), package.get("verificationSources"))
    if not image.is_file() or not all(required):
        raise SystemExit("Ready package is missing required source, copy, verification, or image fields.")
    return document, package, image


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--package-id")
    parser.add_argument("--confirm", action="store_true")
    parser.add_argument("--wait-seconds", type=int, default=90)
    parser.add_argument("--delivery-check-only", action="store_true")
    args = parser.parse_args()
    if args.delivery_check_only:
        delivery_check_only()
        return 0
    if not args.package_id:
        raise SystemExit("--package-id is required unless --delivery-check-only is used.")
    if not args.confirm:
        raise SystemExit("Refusing to publish without --confirm.")

    with SUBMIT_LOCK.open("a+", encoding="utf-8") as submit_lock:
        fcntl.flock(submit_lock.fileno(), fcntl.LOCK_EX)
        document, package, image = load_ready_package(args.package_id)
        decision = rate_limit_decision(document)
        if not decision["allowed"]:
            print(json.dumps({"status": "deferred", "rateLimit": decision}, ensure_ascii=False))
            return 3
        integrations = request_json("/integrations")
        integration = next((item for item in integrations if item.get("identifier") == "x" and item.get("profile", "").lstrip("@") == EXPECTED_HANDLE.lstrip("@") and not item.get("disabled")), None)
        if not integration:
            raise SystemExit(f"No enabled X integration for @{EXPECTED_HANDLE}.")
        media = upload(image)
        submitted_at = utc_now()
        payload = {
            "type": "now", "date": iso(submitted_at), "shortLink": False, "tags": [],
            "posts": [{
                "integration": {"id": integration["id"]},
                "value": [{"content": package["postText"], "image": [{"id": media["id"], "path": media["path"]}]}],
                "settings": {"__type": "x", "who_can_reply_post": "everyone"},
            }],
        }
        created = request_json("/posts", method="POST", data=json.dumps(payload).encode())
        postiz_id = created[0]["postId"]
        record_accepted(package["id"], postiz_id, submitted_at)

    deadline = time.monotonic() + max(10, args.wait_seconds)
    while time.monotonic() < deadline:
        released = next((item for item in recent_x_deliveries(20) if item.get("id") == postiz_id), None)
        if released and released.get("state") == "PUBLISHED" and released.get("releaseURL") and released.get("releaseId"):
            url = finalize_published(package["id"], released)
            subprocess.run([sys.executable, str(ROOT / "scripts" / "render_report.py")], check=True)
            subprocess.run([sys.executable, str(ROOT / "scripts" / "render_run_panel.py")], check=True)
            print(json.dumps({"status": "published", "postizPostId": postiz_id, "url": url}))
            return 0
        if released and released.get("state") in ("ERROR", "FAILED"):
            record_accepted(package["id"], postiz_id, submitted_at, released["state"], "Postiz reported a downstream delivery error; delayed-success reconciliation remains active.")
            print(json.dumps({"status": "pending_reconciliation", "postizPostId": postiz_id, "deliveryState": released["state"]}))
            return 2
        time.sleep(5)
    update_package(package["id"], deliveryState="QUEUE", deliveryCheckedAt=iso(utc_now()))
    print(json.dumps({"status": "pending_reconciliation", "postizPostId": postiz_id, "deliveryState": "QUEUE"}))
    return 2


if __name__ == "__main__":
    sys.exit(main())
