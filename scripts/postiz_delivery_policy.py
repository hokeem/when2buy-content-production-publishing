#!/usr/bin/env python3
"""Deterministic account-level delivery limits for When2Buy X publishing."""

import os
from datetime import datetime, timedelta, timezone


DEFAULT_MIN_INTERVAL_SECONDS = 15 * 60
DEFAULT_HOURLY_LIMIT = 4
DEFAULT_DAILY_LIMIT = 20
DEFAULT_ERROR_GRACE_MINUTES = 60


def utc_now():
    return datetime.now(timezone.utc)


def parse_timestamp(value):
    if not value:
        return None
    try:
        parsed = datetime.fromisoformat(str(value).replace("Z", "+00:00"))
    except ValueError:
        return None
    if parsed.tzinfo is None:
        parsed = parsed.replace(tzinfo=timezone.utc)
    return parsed.astimezone(timezone.utc)


def iso(value):
    return value.astimezone(timezone.utc).isoformat(timespec="seconds").replace("+00:00", "Z")


def limits_from_env():
    return {
        "minIntervalSeconds": max(60, int(os.getenv("WHEN2BUY_POST_MIN_INTERVAL_SECONDS", DEFAULT_MIN_INTERVAL_SECONDS))),
        "hourlyLimit": max(1, int(os.getenv("WHEN2BUY_POST_HOURLY_LIMIT", DEFAULT_HOURLY_LIMIT))),
        "dailyLimit": max(1, int(os.getenv("WHEN2BUY_POST_DAILY_LIMIT", DEFAULT_DAILY_LIMIT))),
        "errorGraceMinutes": max(10, int(os.getenv("WHEN2BUY_POST_ERROR_GRACE_MINUTES", DEFAULT_ERROR_GRACE_MINUTES))),
    }


def package_submission_time(package):
    return parse_timestamp(package.get("postizSubmissionAt") or package.get("publishedAt"))


def pending_packages(document, at=None, error_grace_minutes=DEFAULT_ERROR_GRACE_MINUTES):
    at = at or utc_now()
    pending = []
    for package in document.get("packages", []):
        if package.get("status") != "publishing" or not package.get("postizPostId"):
            continue
        submitted = package_submission_time(package)
        if not submitted or at - submitted < timedelta(minutes=error_grace_minutes):
            pending.append(package)
    return pending


def rate_limit_decision(document, at=None, limits=None):
    """Return a publish/no-publish decision derived from persisted state."""
    at = at or utc_now()
    limits = limits or limits_from_env()
    pending = pending_packages(document, at=at, error_grace_minutes=limits["errorGraceMinutes"])
    if pending:
        submitted = [package_submission_time(item) for item in pending]
        submitted = [item for item in submitted if item]
        retry_at = (
            max(submitted) + timedelta(minutes=limits["errorGraceMinutes"])
            if submitted
            else at + timedelta(minutes=limits["errorGraceMinutes"])
        )
        return {
            "allowed": False,
            "reason": "pending_delivery_reconciliation",
            "retryAt": iso(retry_at),
            "pendingPackageIds": [item.get("id") for item in pending],
        }

    submissions = sorted(
        timestamp
        for timestamp in (package_submission_time(item) for item in document.get("packages", []))
        if timestamp and timestamp <= at
    )
    if submissions:
        retry_at = submissions[-1] + timedelta(seconds=limits["minIntervalSeconds"])
        if at < retry_at:
            return {"allowed": False, "reason": "minimum_interval", "retryAt": iso(retry_at)}

    previous_hour = [timestamp for timestamp in submissions if timestamp > at - timedelta(hours=1)]
    if len(previous_hour) >= limits["hourlyLimit"]:
        return {"allowed": False, "reason": "hourly_limit", "retryAt": iso(previous_hour[0] + timedelta(hours=1))}

    previous_day = [timestamp for timestamp in submissions if timestamp > at - timedelta(hours=24)]
    if len(previous_day) >= limits["dailyLimit"]:
        return {"allowed": False, "reason": "daily_limit", "retryAt": iso(previous_day[0] + timedelta(hours=24))}

    return {
        "allowed": True,
        "reason": "safe",
        "retryAt": None,
        "hourCount": len(previous_hour),
        "dayCount": len(previous_day),
        **limits,
    }


def delivery_error_is_terminal(package, at=None, grace_minutes=DEFAULT_ERROR_GRACE_MINUTES):
    """Postiz ERROR is terminal only after its delayed-success grace window."""
    at = at or utc_now()
    submitted = package_submission_time(package)
    return bool(submitted and at - submitted >= timedelta(minutes=grace_minutes))
