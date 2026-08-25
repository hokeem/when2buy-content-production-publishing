#!/usr/bin/env python3
"""Collect the two when2buy benchmark feeds through Apify only.

The script never publishes to X. It stores only eligible original posts with a
canonical status URL, so later editorial steps retain one-to-one provenance.
"""

import argparse
import json
import os
import sys
from datetime import datetime, timedelta, timezone
from pathlib import Path
from urllib.error import HTTPError, URLError
from urllib.parse import quote
from urllib.request import Request, urlopen

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "skills" / "when2buy-content-publisher" / "scripts"))
import state  # noqa: E402

ACTOR_DEFAULT = "apidojo/twitter-profile-scraper"
BENCHMARKS = ("WhaleInsider", "StockMKTNewz")


def utc_now():
    return datetime.now(timezone.utc).replace(microsecond=0).isoformat().replace("+00:00", "Z")


def actor_path(actor_id):
    # Apify's API path accepts owner~actor-name. It avoids an ambiguous slash.
    return quote(actor_id.replace("/", "~"), safe="~")


def run_actor(token, actor_id, max_posts):
    url = f"https://api.apify.com/v2/acts/{actor_path(actor_id)}/run-sync-get-dataset-items?token={quote(token, safe='')}"
    all_items = []
    for handle in BENCHMARKS:
        payload = json.dumps({
            "startUrls": [f"https://x.com/{handle}"],
            "maxItems": max_posts,
            "start": (datetime.now(timezone.utc) - timedelta(hours=48)).strftime("%Y-%m-%d_%H:%M:%S_UTC"),
            "getReplies": False,
            "includeNativeRetweets": False,
        }).encode("utf-8")
        request = Request(url, data=payload, headers={"Content-Type": "application/json"}, method="POST")
        try:
            with urlopen(request, timeout=300) as response:
                data = json.load(response)
        except HTTPError as exc:
            detail = exc.read(400).decode("utf-8", "replace")
            raise RuntimeError(f"Apify request for @{handle} failed with HTTP {exc.code}: {detail}") from exc
        except URLError as exc:
            raise RuntimeError(f"Apify request for @{handle} could not be completed: {exc.reason}") from exc
        if not isinstance(data, list):
            raise RuntimeError(f"Apify returned an unexpected dataset payload for @{handle} (expected a JSON list).")
        all_items.extend({**item, "_requestedAccount": handle} for item in data if isinstance(item, dict))
    return all_items


def value(item, *keys):
    for key in keys:
        if item.get(key) is not None:
            return item[key]
    return None


def media_urls(item):
    collected = []
    media = value(item, "media", "photos", "videos") or []
    if isinstance(media, list):
        for entry in media:
            if isinstance(entry, str) and entry.startswith("http"):
                collected.append(entry)
            elif isinstance(entry, dict):
                for key in ("url", "mediaUrl", "media_url_https", "previewUrl"):
                    url = entry.get(key)
                    if isinstance(url, str) and url.startswith("http"):
                        collected.append(url)
    return list(dict.fromkeys(collected))



def number(value):
    if isinstance(value, bool) or value is None:
        return 0
    if isinstance(value, (int, float)):
        return int(value)
    if isinstance(value, str):
        try:
            return int(float(value.replace(",", "").strip()))
        except ValueError:
            return 0
    return 0


def engagement(item):
    nested = item.get("engagement") if isinstance(item.get("engagement"), dict) else {}
    return {
        "likes": number(value(item, "likeCount", "likes", "favorite_count") or nested.get("likes")),
        "replies": number(value(item, "replyCount", "replies", "reply_count") or nested.get("replies")),
        "reposts": number(value(item, "retweetCount", "retweets", "reposts", "retweet_count") or nested.get("reposts")),
        "quotes": number(value(item, "quoteCount", "quotes", "quote_count") or nested.get("quotes")),
        "views": number(value(item, "viewCount", "views", "view_count") or nested.get("views")),
    }

def normalize(item):
    post_id = str(value(item, "id", "tweetId", "tweet_id") or "")
    author = item.get("author") if isinstance(item.get("author"), dict) else {}
    raw_handle = value(item, "username", "userName", "screen_name", "_requestedAccount") or author.get("userName") or author.get("username")
    handle = str(raw_handle or "").lstrip("@")
    if not post_id.isdigit() or handle.lower() not in {name.lower() for name in BENCHMARKS}:
        return None
    if bool(value(item, "isReply", "is_reply")) or bool(value(item, "isRetweet", "is_retweet", "retweeted")):
        return None
    text = str(value(item, "text", "fullText", "full_text") or "").strip()
    if not text:
        return None
    url = str(value(item, "url", "tweetUrl", "tweet_url") or f"https://x.com/{handle}/status/{post_id}")
    if not url.startswith("https://x.com/") or "/status/" not in url:
        url = f"https://x.com/{handle}/status/{post_id}"
    return {
        "id": post_id,
        "account": next(name for name in BENCHMARKS if name.lower() == handle.lower()),
        "url": url.split("?")[0],
        "postedAt": value(item, "createdAt", "created_at", "timestamp", "time") or "",
        "text": text,
        "mediaType": "media" if value(item, "media", "photos", "videos") else "text",
        "mediaUrls": media_urls(item),
        "engagement": engagement(item),
        "source": "apify",
        "capturedAt": utc_now(),
    }


def main():
    parser = argparse.ArgumentParser(description="Collect when2buy benchmarks from Apify.")
    parser.add_argument("--max-posts", type=int, default=5, choices=range(1, 101), metavar="1..100")
    parser.add_argument("--input-json", type=Path, help="Use a saved Apify dataset JSON file instead of the network (test only).")
    parser.add_argument("--dry-run", action="store_true", help="Print eligible normalized posts without changing state.")
    args = parser.parse_args()

    if args.input_json:
        raw = json.loads(args.input_json.read_text(encoding="utf-8"))
    else:
        token = os.environ.get("APIFY_TOKEN")
        if not token:
            raise SystemExit("APIFY_TOKEN is required. Set it in the environment; never commit it.")
        raw = run_actor(token, os.environ.get("APIFY_ACTOR_ID", ACTOR_DEFAULT), args.max_posts)

    normalized = [post for item in raw if isinstance(item, dict) for post in [normalize(item)] if post]
    normalized.sort(key=lambda post: (post["postedAt"], post["id"]), reverse=True)
    if args.dry_run:
        print(json.dumps(normalized, ensure_ascii=False, indent=2))
        return

    current = state.load_state()
    known = {str(post.get("id")) for post in current["benchmarkPosts"]}
    new_posts = [post for post in normalized if post["id"] not in known]
    current["benchmarkPosts"].extend(new_posts)
    run_id = f"run-{datetime.now(timezone.utc).strftime('%Y%m%dT%H%M%SZ')}-radar"
    current["runs"].append({
        "id": run_id,
        "mode": "radar",
        "status": "succeeded" if normalized else "blocked",
        "startedAt": utc_now(),
        "completedAt": utc_now(),
        "summary": f"Apify scanned both benchmark accounts; captured {len(normalized)} eligible originals and added {len(new_posts)} new post(s).",
        "reason": "" if normalized else "Apify returned no eligible original posts from either benchmark account.",
        "collector": {"provider": "Apify", "actor": os.environ.get("APIFY_ACTOR_ID", ACTOR_DEFAULT)},
    })
    errors = state.validate(current)
    if errors:
        raise SystemExit("\n".join(errors))
    state.atomic_write(current)
    print(f"Apify scan complete: {len(new_posts)} new eligible benchmark post(s).")


if __name__ == "__main__":
    main()
