#!/usr/bin/env python3
"""Shared, evidence-preserving analytics helpers for when2buy reports."""
import json
import re
import statistics
from collections import defaultdict
from datetime import datetime, timedelta, timezone
from pathlib import Path
from zoneinfo import ZoneInfo

ROOT = Path(__file__).resolve().parents[1]
STATE_PATH = ROOT / "data" / "state.json"
TZ = ZoneInfo("Asia/Shanghai")
FIELDS = ("views", "likes", "replies", "reposts", "bookmarks")


def load_state():
    return json.loads(STATE_PATH.read_text(encoding="utf-8"))


def parse_dt(value):
    if not value:
        return None
    try:
        parsed = datetime.fromisoformat(str(value).replace("Z", "+00:00"))
        return parsed if parsed.tzinfo else parsed.replace(tzinfo=timezone.utc)
    except ValueError:
        return None


def local_date(value):
    parsed = parse_dt(value)
    return parsed.astimezone(TZ).date().isoformat() if parsed else None


def latest_metrics(state):
    latest = defaultdict(dict)
    for snapshot in sorted(state.get("metricSnapshots", []), key=lambda item: str(item.get("observedAt", ""))):
        evidence = snapshot.get("evidence") if isinstance(snapshot.get("evidence"), dict) else {}
        if not evidence.get("source"):
            continue
        post_id = str(snapshot.get("postId") or "")
        if not post_id:
            continue
        for field in FIELDS:
            value = snapshot.get(field)
            if isinstance(value, (int, float)) and not isinstance(value, bool):
                latest[post_id][field] = int(value)
                latest[post_id][field + "ObservedAt"] = snapshot.get("observedAt")
                latest[post_id][field + "Source"] = evidence.get("source")
    return latest


def records(state):
    packages = {item.get("id"): item for item in state.get("packages", []) if item.get("id")}
    benchmark = {str(item.get("id")): item for item in state.get("benchmarkPosts", []) if item.get("id")}
    metrics = latest_metrics(state)
    result = []
    for post in state.get("posts", []):
        if post.get("status") != "published":
            continue
        package = packages.get(post.get("packageId"), {})
        source = benchmark.get(str(package.get("benchmarkPostId")), {})
        result.append({"post": post, "package": package, "source": source, "metrics": metrics.get(str(post.get("id")), {})})
    return sorted(result, key=lambda row: str(row["post"].get("publishedAt", "")), reverse=True)


def days_ending(end_date, count):
    return [(end_date - timedelta(days=offset)).isoformat() for offset in range(count - 1, -1, -1)]


def daily_summary(state, dates):
    date_set = set(dates)
    rows = {day: {"date": day, "captured": 0, "produced": 0, "published": 0, "views": 0, "likes": 0, "replies": 0, "reposts": 0, "known": 0} for day in dates}
    for item in state.get("benchmarkPosts", []):
        day = local_date(item.get("capturedAt"))
        if day in date_set:
            rows[day]["captured"] += 1
    for item in state.get("packages", []):
        day = local_date(item.get("createdAt"))
        if day in date_set:
            rows[day]["produced"] += 1
    for record in records(state):
        day = local_date(record["post"].get("publishedAt"))
        if day not in date_set:
            continue
        row = rows[day]
        row["published"] += 1
        values = record["metrics"]
        if isinstance(values.get("views"), int):
            row["known"] += 1
            row["views"] += values["views"]
        for field in ("likes", "replies", "reposts"):
            if isinstance(values.get(field), int):
                row[field] += values[field]
    for row in rows.values():
        row["coverage"] = row["known"] / row["published"] if row["published"] else None
        row["avgViews"] = row["views"] / row["known"] if row["known"] else None
    return [rows[day] for day in dates]


def cohort(state, start_date, end_date):
    return [row for row in records(state) if (day := local_date(row["post"].get("publishedAt"))) and start_date.isoformat() <= day <= end_date.isoformat()]


def cohort_stats(items):
    views = [row["metrics"]["views"] for row in items if isinstance(row["metrics"].get("views"), int)]
    interactions = sum(sum(row["metrics"].get(field, 0) for field in ("likes", "replies", "reposts")) for row in items)
    return {"published": len(items), "known": len(views), "views": sum(views), "medianViews": statistics.median(views) if views else None, "interactions": interactions, "coverage": len(views) / len(items) if items else None}


def category(record):
    text = " ".join((str(record["package"].get("title") or ""), str(record["package"].get("postText") or ""))).lower()
    groups = (
        ("Crypto & digital assets", ("bitcoin", "btc", "crypto", "token", "ethereum", "eth", "blockchain")),
        ("AI & semiconductors", ("nvidia", "nvda", "chip", "semiconductor", " ai ", "compute")),
        ("Macro & policy", ("fed", "rate", "inflation", "treasury", "jobs", "tariff", "dollar")),
        ("Funds & market structure", ("etf", "s&p", "nasdaq", "index", "market", "portfolio")),
    )
    for label, words in groups:
        if any(word in f" {text} " for word in words):
            return label
    return "Companies & events"


def time_band(record):
    parsed = parse_dt(record["post"].get("publishedAt"))
    hour = parsed.astimezone(TZ).hour if parsed else 0
    if 6 <= hour < 12: return "Morning 06–12"
    if 12 <= hour < 18: return "Afternoon 12–18"
    if 18 <= hour < 24: return "Evening 18–24"
    return "Overnight 00–06"


def strengths(record):
    copy = str(record["package"].get("postText") or "")
    result = []
    if re.search(r"[$%]?\\d", copy): result.append("quantified hook")
    if len(copy.split("\\n\\n", 1)[0]) <= 120: result.append("concise event-first lead")
    visual = record["package"].get("visualProduction") if isinstance(record["package"].get("visualProduction"), dict) else {}
    if visual.get("method") == "image_model": result.append("entity-led generated visual")
    if record["source"].get("postedAt"): result.append("one-to-one fast-follow topic")
    return result or ["single-topic focus"]
