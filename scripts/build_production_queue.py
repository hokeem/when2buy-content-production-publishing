#!/usr/bin/env python3
"""Turn captured benchmark originals into a deterministic, one-to-one production queue."""
import json
import re
import sys
from datetime import datetime, timedelta, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "skills" / "when2buy-content-publisher" / "scripts"))
import state  # noqa: E402
QUEUE_PATH = ROOT / "data" / "production-queue.json"
KEYWORDS = ("earnings", "guidance", "revenue", "nvidia", "chip", "semiconductor", "ai", "robot", "ipo", "funding", "valuation", "fed", "cpi", "ppi", "jobs", "tariff", "stock", "shares", "nasdaq", "s&p", "tesla", "xpeng", "rocket lab")

def now(): return datetime.now(timezone.utc)
def iso(): return now().replace(microsecond=0).isoformat().replace("+00:00", "Z")
def parse(value):
    raw = str(value)
    try:
        return datetime.fromisoformat(raw.replace("Z", "+00:00"))
    except ValueError:
        try:
            return datetime.strptime(raw, "%a %b %d %H:%M:%S %z %Y")
        except ValueError:
            return None

def title(text):
    clean = re.sub(r"\s+", " ", text).strip()
    return clean[:92] + ("…" if len(clean) > 92 else "")

def score(post):
    text = post["text"].lower()
    posted = parse(post.get("postedAt"))
    age = (now() - posted).total_seconds() / 3600 if posted else 72
    freshness = 5 if age <= 4 else 4 if age <= 12 else 3 if age <= 24 else 2 if age <= 48 else 1
    fit = min(5, sum(word in text for word in KEYWORDS))
    market = 5 if any(word in text for word in ("$", "billion", "earnings", "fed", "cpi", "tariff")) else 3
    visual = 5 if re.search(r"\$?\d+(?:\.\d+)?\s?(?:billion|million|b|m|%)", text) else 3
    clarity = 4 if len(text) >= 60 else 3
    total = freshness + fit + market + visual + clarity
    return total, {"freshness": freshness, "when2buyFit": fit, "marketImpact": market, "visualPotential": visual, "factualClarity": clarity}

def main():
    current = state.load_state()
    covered = {str(x.get("benchmarkPostId")) for x in current.get("packages", [])}
    known_radar = {str(x.get("benchmarkPostId")) for x in current.get("radar", [])}
    candidates = []
    for post in current.get("benchmarkPosts", []):
        posted = parse(post.get("postedAt"))
        if str(post.get("id")) in covered or (posted and now() - posted > timedelta(hours=72)):
            continue
        total, breakdown = score(post)
        # Every eligible captured original receives an output.  Reframe weak or
        # unverified claims as attributed radar/context; do not discard them.
        candidates.append((total, post, breakdown))
    candidates.sort(key=lambda item: (item[0], item[1].get("postedAt", "")), reverse=True)
    for rank, (total, post, breakdown) in enumerate(candidates, start=1):
        if str(post["id"]) not in known_radar:
            current["radar"].append({
                "id": f"radar-{post['id']}", "rank": rank,
                "title": title(post["text"]), "benchmarkPostId": post["id"],
                "sourceAccount": post["account"], "sourcePostUrl": post["url"],
                "score": total, "whyNow": "Fresh benchmark signal; create an original attributed market-radar or context post when independent verification is unavailable.",
                "status": "queued", "createdAt": iso(), "scoreBreakdown": breakdown,
            })
    queue = {"generatedAt": iso(), "timezone": "Asia/Shanghai", "items": [
        {"rank": rank, "benchmarkPostId": post["id"], "benchmarkAccount": post["account"],
         "benchmarkUrl": post["url"], "originalText": post["text"], "originalMediaUrls": post.get("mediaUrls", []),
         "archivedMedia": [x for x in post.get("mediaArchive", []) if x.get("status") == "archived"],
         "engagement": post.get("engagement", {}), "postedAt": post.get("postedAt", ""),
         "score": total, "scoreBreakdown": breakdown,
         "productionInstruction": "Verify the factual payload against a primary source, then make one original 1:1 when2buy visual and an independently worded English X post. Preserve this exact source mapping; do not publish without action-time confirmation."}
        for rank, (total, post, breakdown) in enumerate(candidates, start=1)
    ]}
    QUEUE_PATH.write_text(json.dumps(queue, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    current["runs"].append({"id": f"run-{now().strftime('%Y%m%dT%H%M%SZ')}-queue", "mode": "queue", "status": "succeeded", "startedAt": iso(), "completedAt": iso(), "summary": f"Prepared {len(queue['items'])} one-to-one production candidate(s).", "reason": ""})
    errors = state.validate(current)
    if errors: raise SystemExit("\n".join(errors))
    state.atomic_write(current)
    print(f"Production queue: {len(queue['items'])} candidate(s).")
if __name__ == "__main__": main()
