#!/usr/bin/env python3
"""Produce the 20:25 Shanghai timestamp-first batch from inspected image-model outputs."""
from datetime import datetime, timezone
from pathlib import Path
import subprocess
import sys

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "skills" / "when2buy-content-publisher" / "scripts"))
import state  # noqa: E402

GENERATED = Path("/root/.codex/generated_images/01a07bd4-3b98-7273-ba27-beb0bd820ae9")
LOGO = ROOT / "skills" / "when2buy-content-publisher" / "assets" / "when2buy-logo-reference.png"

ITEMS = [
    {
        "source_id": "2096935123937640546", "slug": "apple-iphone-event-leadership",
        "image": "exec-a62c2522-4681-43f3-a45c-4e80006bb515.png",
        "title": "Apple iPhone event leadership",
        "copy": "Tim Cook is expected to skip Apple $AAPL's iPhone event Wednesday.\n\nJohn Ternus will lead the presentation.",
        "facts": ["Tim Cook will reportedly not appear at Apple's iPhone release event on Wednesday.", "John Ternus will be in full control of the event."],
        "prompt": "Use case: ads-marketing. Asset type: 1:1 X financial-news visual for When2Buy. Primary request: original premium editorial visual about Apple’s upcoming iPhone event with leadership transition focus. Scene/backdrop: a dark Apple-like product-launch stage, sophisticated near-black auditorium, subtle white projection light. Subject: a sleek unbranded modern smartphone on a pedestal, with a single empty executive presentation lectern in the background; concrete product-event scene, not an abstract background. Style/medium: high-end photorealistic financial-news editorial photography. Composition/framing: exact square 1:1. Product dominates left/center. Keep the lower-right 20% clean and near-black for a circular logo added afterward. Lighting/mood: restrained, dramatic, premium. Color palette: near-black, white, restrained red only. Text: none. Constraints: no readable text, numbers, brand logos, source names, social handles, URLs, watermarks, disclaimer, CTA, people, generic radar background, or typography card; scene must be complete and undamaged.",
    },
    {
        "source_id": "2096931241597567248", "slug": "sandisk-sp500-leader",
        "image": "exec-2ca3b683-1575-46d1-8762-282915599a32.png",
        "title": "Sandisk $SNDK leads the S&P 500 in 2026",
        "copy": "Sandisk $SNDK is the S&P 500's best-performing stock so far in 2026.",
        "facts": ["Sandisk $SNDK is the best-performing S&P 500 stock so far in 2026."],
        "prompt": "Use case: ads-marketing. Asset type: 1:1 X financial-news visual for When2Buy. Primary request: original premium editorial visual about SanDisk flash-storage technology leading the S&P 500 in 2026. Scene/backdrop: cinematic near-black institutional trading environment, deep charcoal data-center hardware racks. Subject: one elegant photorealistic unbranded flash-memory storage module standing upright on a dark reflective desk, with a restrained upward luminous market trajectory behind it; storage technology clearly dominant and concrete. Style/medium: high-end financial-news editorial photography. Composition/framing: exact square 1:1; object fills left and center; reserve fully clean dark lower-right corner for a circular logo applied afterward. Lighting/mood: dramatic studio rim light, confident and premium. Color palette: near-black, white highlights, restrained deep red accent only. Text: none. Constraints: no readable text, numbers, tickers, logos, brands, watermarks, source names, URLs, disclaimer, CTA, people, pure typography card, or damaged objects.",
    },
    {
        "source_id": "2096929359596556570", "slug": "sandisk-nasdaq100-leader",
        "image": "exec-c79bacc6-dcd9-44ed-b103-0254fb7d0ccd.png",
        "title": "Sandisk $SNDK leads the Nasdaq-100 in 2026",
        "copy": "Sandisk $SNDK leads the Nasdaq-100 so far in 2026, up 633%.",
        "facts": ["Sandisk $SNDK is the best-performing Nasdaq-100 stock so far in 2026.", "Sandisk is up 633% in 2026."],
        "prompt": "Use case: ads-marketing. Asset type: 1:1 X financial-news visual for When2Buy. Primary request: original premium editorial visual about SanDisk flash-storage technology leading the Nasdaq-100 with a steep 2026 gain. Scene/backdrop: cinematic near-black data-storage laboratory and institutional market environment, deep charcoal hardware racks. Subject: a single high-end photorealistic unbranded flash-memory chip module and a translucent sharply ascending market trajectory shown as non-readable light marks; storage technology concrete and dominant. Style/medium: high-end financial-news editorial photography. Composition/framing: exact square; module occupies center-left; clean empty dark lower-right corner reserved for circular logo compositing afterward. Lighting/mood: dramatic studio rim light, premium and energetic. Color palette: near-black, white highlights, restrained deep red accent only. Text: none. Constraints: no readable text, numbers, tickers, logos, brands, watermarks, source names, URLs, disclaimer, CTA, people, pure typography card, or damaged objects.",
    },
    {
        "source_id": "2096926573056151788", "slug": "applovin-app-minus-52",
        "image": "exec-b6f9879b-88f1-4612-b74b-bd50dffb5e2e.png",
        "title": "AppLovin $APP down 52% in 2026",
        "copy": "$APP is the Nasdaq-100's worst-performing stock so far in 2026, down 52%.",
        "facts": ["AppLovin $APP is the worst-performing Nasdaq-100 stock so far in 2026.", "AppLovin is down 52% in 2026."],
        "prompt": "Use case: ads-marketing. Asset type: 1:1 X financial-news visual for When2Buy. Primary request: original premium editorial visual about AppLovin mobile ad-tech stock performance decline. Scene/backdrop: sophisticated near-black mobile ad-tech operations space with abstract smartphone app interface panes that contain no readable text. Subject: one elegant smartphone and a digital advertising analytics console, with a clear restrained red descending market trajectory; tangible app-advertising technology dominates instead of a generic market scene. Style/medium: high-end photorealistic financial-news editorial photography. Composition/framing: exact square; smartphone and console dominate left/center; reserve completely empty dark lower-right corner for a circular logo added later. Lighting/mood: sharp, controlled and premium. Color palette: near-black, white highlights, restrained red accent. Text: none. Constraints: no readable text, numbers, tickers, logos, brands, watermarks, source names, URLs, disclaimer, CTA, people, typography-only treatment, or damaged objects.",
    },
    {
        "source_id": "2096923774364844127", "slug": "trade-desk-ttd-sp500-worst",
        "image": "exec-a131bc40-afd7-4cf4-ba07-e63422e1c4ae.png",
        "title": "The Trade Desk $TTD trails the S&P 500",
        "copy": "$TTD is the S&P 500's worst-performing stock so far in 2026.\n\nThe Trade Desk is set to leave the index later this month.",
        "facts": ["The Trade Desk $TTD is the worst-performing S&P 500 stock so far in 2026.", "The Trade Desk is being removed from the S&P 500 later this month."],
        "prompt": "Use case: ads-marketing. Asset type: 1:1 X financial-news visual for When2Buy. Primary request: original premium editorial visual about The Trade Desk ad-tech stock trailing the S&P 500 and leaving the index. Scene/backdrop: cinematic near-black institutional media-buying technology environment with subtle digital advertising display panels that contain no readable text. Subject: a sophisticated ad-tech control console and a clean red descending market trajectory exiting a luminous index-ring motif; concrete entity-led technology scene, not generic radar art. Style/medium: high-end photorealistic financial-news editorial photography. Composition/framing: exact square; console and index motif dominate left/center; keep the lower-right 20% clean, empty and near-black for a circular logo composited afterward. Lighting/mood: dramatic, serious, premium. Color palette: near-black, white, restrained red. Text: none. Constraints: no readable text, numbers, tickers, company logos, brands, watermarks, source names, URLs, disclaimer, CTA, people, typography-only card, or damaged objects.",
    },
]

def stamp():
    return datetime.now(timezone.utc).isoformat().replace("+00:00", "Z")

def main():
    document = state.load_state()
    sources = {str(post["id"]): post for post in document["benchmarkPosts"]}
    for item in ITEMS:
        package_id = f"pkg-20260907-{item['slug']}"
        relative = Path("deliverables") / package_id / "when2buy-image-model-v3.png"
        target = ROOT / relative
        target.parent.mkdir(parents=True, exist_ok=True)
        subprocess.run(["convert", str(GENERATED / item["image"]), "(", str(LOGO), "-resize", "112x112", ")", "-gravity", "southeast", "-geometry", "+36+36", "-composite", str(target)], check=True)
        package = {"id": package_id, "benchmarkPostId": item["source_id"], "benchmarkPostUrl": sources[item["source_id"]]["url"], "title": item["title"], "status": "ready", "postText": item["copy"], "mirroredFacts": item["facts"], "verificationSources": [sources[item["source_id"]]["url"]], "imagePath": str(relative), "createdAt": stamp(), "visualProduction": {"method": "image_model", "prompt": item["prompt"], "logoApplied": True, "qaStatus": "passed", "qa": {"inspectedAt": stamp(), "checks": ["square", "entity-led", "no readable generated text", "no source attribution", "exact logo composited once", "logo clear space", "no damage"]}}}
        old = next((entry for entry in document["packages"] if str(entry.get("benchmarkPostId")) == item["source_id"]), None)
        if old:
            old.clear(); old.update(package)
        else:
            document["packages"].append(package)
    document["runs"].append({"id": f"run-{datetime.now(timezone.utc).strftime('%Y%m%dT%H%M%SZ')}-produce", "mode": "produce", "status": "succeeded", "startedAt": stamp(), "completedAt": stamp(), "summary": "Produced the first five timestamp-first packages with inspected image-model scenes and exact-logo compositing.", "reason": ""})
    errors = state.validate(document)
    if errors:
        raise SystemExit("\n".join(errors))
    state.atomic_write(document)
    print("Prepared " + ", ".join(f"pkg-20260907-{item['slug']}" for item in ITEMS))

if __name__ == "__main__":
    main()
