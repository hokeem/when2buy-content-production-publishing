#!/usr/bin/env python3
"""Shared, deterministic freshness rules for benchmark-derived publishing."""

import os
from datetime import datetime, timedelta, timezone


DEFAULT_SOURCE_TTL_MINUTES = 90


def source_ttl_minutes():
    raw = os.environ.get("WHEN2BUY_SOURCE_TTL_MINUTES", str(DEFAULT_SOURCE_TTL_MINUTES))
    try:
        value = int(raw)
    except ValueError as exc:
        raise ValueError("WHEN2BUY_SOURCE_TTL_MINUTES must be an integer") from exc
    if value < 15 or value > 360:
        raise ValueError("WHEN2BUY_SOURCE_TTL_MINUTES must be between 15 and 360")
    return value


def parse_timestamp(value):
    raw = str(value or "").strip()
    if not raw:
        return None
    try:
        parsed = datetime.fromisoformat(raw.replace("Z", "+00:00"))
    except ValueError:
        try:
            parsed = datetime.strptime(raw, "%a %b %d %H:%M:%S %z %Y")
        except ValueError:
            return None
    if parsed.tzinfo is None:
        parsed = parsed.replace(tzinfo=timezone.utc)
    return parsed.astimezone(timezone.utc)


def freshness(posted_at, *, at=None, ttl_minutes=None):
    current = (at or datetime.now(timezone.utc)).astimezone(timezone.utc)
    posted = parse_timestamp(posted_at)
    ttl = source_ttl_minutes() if ttl_minutes is None else ttl_minutes
    if posted is None:
        return {"eligible": False, "reason": "missing_or_invalid_source_timestamp", "ageMinutes": None, "expiresAt": None, "ttlMinutes": ttl}
    expiry = posted + timedelta(minutes=ttl)
    age_minutes = max(0.0, (current - posted).total_seconds() / 60)
    return {
        "eligible": current <= expiry,
        "reason": "fresh" if current <= expiry else "source_ttl_exceeded",
        "ageMinutes": round(age_minutes, 1),
        "expiresAt": expiry.isoformat(timespec="seconds").replace("+00:00", "Z"),
        "ttlMinutes": ttl,
    }


def expire_stale_packages(current, *, at=None, ttl_minutes=None):
    """Expire only unsent work; never rewrite accepted or published deliveries."""
    current_time = (at or datetime.now(timezone.utc)).astimezone(timezone.utc)
    by_id = {str(post.get("id")): post for post in current.get("benchmarkPosts", [])}
    expired = []
    for package in current.get("packages", []):
        if package.get("status") not in {"draft", "ready", "blocked"}:
            continue
        source = by_id.get(str(package.get("benchmarkPostId")))
        check = freshness(source.get("postedAt") if source else None, at=current_time, ttl_minutes=ttl_minutes)
        if check["eligible"]:
            continue
        package.update({
            "status": "expired",
            "expiredAt": current_time.isoformat(timespec="seconds").replace("+00:00", "Z"),
            "expiryReason": check["reason"],
            "sourceExpiresAt": check["expiresAt"],
        })
        expired.append(package.get("id"))
    return expired
