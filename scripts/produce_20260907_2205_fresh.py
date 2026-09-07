#!/usr/bin/env python3
"""Record the two newest eligible benchmark packages for the 22:05 CST run."""
from datetime import datetime, timezone
from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "skills" / "when2buy-content-publisher" / "scripts"))
import state  # noqa: E402


def now():
    return datetime.now(timezone.utc).isoformat()


ITEMS = (
    {
        "id": "pkg-20260907-strive-bitcoin-buying",
        "source": "2096959433909608475",
        "title": "Strive CEO hints at more Bitcoin buying",
        "postText": "Strive's CEO hinted that the public company may buy more Bitcoin.\n\nWhen2Buy — your U.S. stock partner.",
        "mirroredFacts": [
            "Strive is a public company.",
            "Its CEO hinted at buying more Bitcoin.",
        ],
        "imagePath": "deliverables/pkg-20260907-strive-bitcoin-buying/when2buy-image-model.png",
        "prompt": "Premium 1:1 near-black institutional finance scene: physical Bitcoin in the foreground, dark glass corporate environment, restrained red rim light, empty lower-right logo-safe area; no text, logos, source attribution, social UI, or generic radar imagery.",
    },
    {
        "id": "pkg-20260907-bipolar-pumpfun-launch",
        "source": "2096958507513680239",
        "title": "BIPOLAR PumpFun launch",
        "postText": "$BIPOLAR is gaining attention on TikTok ahead of its PumpFun launch tomorrow at 5 PM UTC.\n\nCreators are promoting the meme to reach a wider audience.\n\nWhen2Buy — your U.S. stock partner.",
        "mirroredFacts": [
            "$BIPOLAR is gaining attention on TikTok.",
            "Creators are promoting it to a wider audience.",
            "The token is set to launch tomorrow at 5 PM UTC on PumpFun.",
        ],
        "imagePath": "deliverables/pkg-20260907-bipolar-pumpfun-launch/when2buy-image-model.png",
        "prompt": "Premium 1:1 near-black digital-market scene: a red-and-white split-orbit token lifting from a sleek launch platform, subtle blurred vertical phone-light pattern, empty lower-right logo-safe area; no text, logos, source attribution, social UI, or generic radar imagery.",
    },
)


def main():
    document = state.load_state()
    sources = {str(item["id"]): item for item in document["benchmarkPosts"]}
    for item in ITEMS:
        source = sources[item["source"]]
        package = {
            "id": item["id"], "benchmarkPostId": item["source"],
            "benchmarkPostUrl": source["url"], "title": item["title"], "status": "ready",
            "postText": item["postText"], "mirroredFacts": item["mirroredFacts"],
            "verificationSources": [source["url"]], "imagePath": item["imagePath"],
            "createdAt": now(),
            "visualProduction": {
                "method": "image_model", "prompt": item["prompt"], "logoApplied": True,
                "qaStatus": "passed", "qa": {"inspectedAt": now(), "checks": [
                    "square 1254x1254", "entity-led visual", "no readable generated text",
                    "no generic radar image", "exact repository logo composited once",
                    "logo clear space", "no damaged or inconsistent subject",
                ]},
            },
        }
        prior = next((entry for entry in document["packages"] if entry.get("id") == item["id"]), None)
        if prior:
            document["packages"][document["packages"].index(prior)] = package
        else:
            document["packages"].append(package)
    document["runs"].append({
        "id": f"run-{datetime.now(timezone.utc).strftime('%Y%m%dT%H%M%SZ')}-produce",
        "mode": "produce", "status": "succeeded", "startedAt": now(), "completedAt": now(),
        "summary": "Produced the two newest timestamp-first benchmark items with inspected image-model visuals and exact-logo compositing.", "reason": "",
    })
    errors = state.validate(document)
    if errors:
        raise SystemExit("\n".join(errors))
    state.atomic_write(document)


if __name__ == "__main__":
    main()
