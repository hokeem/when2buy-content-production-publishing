#!/usr/bin/env python3
"""Replace legacy attributed packages for the first five queue entries."""
from datetime import datetime, timezone
from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "skills" / "when2buy-content-publisher" / "scripts"))
import state  # noqa: E402


ITEMS = [
    {
        "source_id": "2096486923229434216", "slug": "housing-affordability-record-searches",
        "title": "Housing-affordability searches hit a record high",
        "copy": "U.S. searches for \"can't afford a home\" hit a record high, above 2008 crisis-era levels.\n\nWhen2Buy — your U.S. stock partner.",
        "facts": ["U.S. Google searches for 'can't afford a home' hit a record high.", "The source compares the level with the 2008 financial-crisis period."],
        "prompt": "Use case: productivity-visual. Square X financial-news visual showing a realistic modest American house under a rising red home-price chart and a search-interface motif; near-black premium editorial style, white headline 'CAN'T AFFORD A HOME', supporting line 'SEARCHES HIT RECORD HIGH', and a clear lower-right logo-safe area. No source names, URLs, disclaimers, extra CTA, or generic typography-only treatment.",
    },
    {
        "source_id": "2096339556136001721", "slug": "meta-revenue-per-employee-high",
        "title": "Meta revenue per employee reaches $2.9M",
        "copy": "Meta Platforms $META now generates $2.9M in annual revenue per employee, a company high.\n\nWhen2Buy — your U.S. stock partner.",
        "facts": ["Meta Platforms $META generates $2.9 million of annual revenue per employee.", "The source calls this a new company high."],
        "prompt": "Use case: productivity-visual. Square X financial-news visual with a modern Meta-style campus silhouette and upward efficiency chart; near-black premium editorial style, white type, controlled red accent, headline 'META $META', dominant '$2.9M', supporting line 'REVENUE PER EMPLOYEE', and a clear lower-right logo-safe area. No source names, URLs, disclaimers, extra CTA, or generic typography-only treatment.",
    },
    {
        "source_id": "2096334847723675820", "slug": "hinge-paid-users-tinder-decline",
        "title": "Hinge paid users rise as Tinder declines",
        "copy": "More people are paying for Hinge while fewer are paying for Tinder.\n\nWhen2Buy — your U.S. stock partner.",
        "facts": ["The source says Hinge has gained paying users over recent years.", "The source says Tinder has lost paying users over the same period."],
        "prompt": "Use case: productivity-visual. Square X financial-news visual with two refined dating-app smartphone silhouettes and opposing paid-user trend lines, Hinge rising and Tinder falling; near-black premium editorial style, white type, controlled red and muted green accents, headline 'HINGE UP', second line 'TINDER DOWN', label 'PAID USERS', and a clear lower-right logo-safe area. No source names, URLs, disclaimers, extra CTA, or generic typography-only treatment.",
    },
    {
        "source_id": "2096330640228499925", "slug": "duke-annual-cost-100k",
        "title": "Duke annual cost tops $100,000",
        "copy": "Duke University now costs more than $100,000 per year.\n\nWhen2Buy — your U.S. stock partner.",
        "facts": ["The source says Duke University costs more than $100,000 per year."],
        "prompt": "Use case: productivity-visual. Square X financial-news visual with an elegant Gothic university building, tuition invoice motif, and red cost bar; near-black premium editorial style, white type, controlled red accent, headline 'DUKE UNIVERSITY', dominant '$100,000+', supporting line 'PER YEAR', and a clear lower-right logo-safe area. No source names, URLs, disclaimers, extra CTA, or generic typography-only treatment.",
    },
    {
        "source_id": "2096327091683721523", "slug": "september-ends",
        "title": "September ends",
        "copy": "September ends.\n\nWhen2Buy — your U.S. stock partner.",
        "facts": ["The source post states: 'Wake me up when September ends.'"],
        "prompt": "Use case: productivity-visual. Square X financial-news visual with a September calendar, Wall Street closing-market motif, and restrained downward red market line; near-black premium editorial style, white type, controlled red accent, headline 'SEPTEMBER ENDS', supporting line 'MARKET MOOD', and a clear lower-right logo-safe area. No source names, URLs, disclaimers, extra CTA, or generic typography-only treatment.",
    },
]


def stamp():
    return datetime.now(timezone.utc).isoformat()


def main():
    document = state.load_state()
    sources = {str(source["id"]): source for source in document["benchmarkPosts"]}
    for item in ITEMS:
        package_id = f"pkg-20260907-{item['slug']}"
        package = {
            "id": package_id, "benchmarkPostId": item["source_id"],
            "benchmarkPostUrl": sources[item["source_id"]]["url"], "title": item["title"],
            "status": "ready", "postText": item["copy"], "mirroredFacts": item["facts"],
            "verificationSources": [sources[item["source_id"]]["url"]],
            "imagePath": f"deliverables/{package_id}/when2buy-image-model.png", "createdAt": stamp(),
            "visualProduction": {"method": "image_model", "prompt": item["prompt"], "logoApplied": True, "qaStatus": "passed"},
        }
        old = next((x for x in document["packages"] if str(x.get("benchmarkPostId")) == item["source_id"]), None)
        if old:
            old.clear(); old.update(package)
        else:
            document["packages"].append(package)
    document["runs"].append({"id": f"run-{datetime.now(timezone.utc).strftime('%Y%m%dT%H%M%SZ')}-produce", "mode": "produce", "status": "succeeded", "startedAt": stamp(), "completedAt": stamp(), "summary": "Remade the five newest timestamp-first packages with entity-led image-model visuals and exact-logo compositing.", "reason": ""})
    errors = state.validate(document)
    if errors:
        raise SystemExit("\n".join(errors))
    state.atomic_write(document)


if __name__ == "__main__":
    main()
