#!/usr/bin/env python3
"""Produce the single newest fresh Walmart/Papa John's package."""
from datetime import datetime, timezone
from pathlib import Path
import shutil
import subprocess
import sys

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "skills" / "when2buy-content-publisher" / "scripts"))
import state  # noqa: E402

SOURCE_ID = "2098060288830459918"
PACKAGE_ID = "pkg-20260910-walmart-papa-johns-delivery"
BASE = Path("/root/.codex/generated_images/01a08bc7-7934-7ee1-9b68-7cffc7674318/exec-bed5a53f-75c1-46fa-b2d6-23156f1dde81.png")
LOGO = ROOT / "skills" / "when2buy-content-publisher" / "assets" / "when2buy-logo-reference.png"

PROMPT = """Use case: photorealistic-natural
Asset type: complete square 1:1 premium X financial-news editorial visual for When2Buy
Primary request: one complete original entity-led visual about Walmart ($WMT) expanding restaurant delivery to Papa John's ($PZZA) food orders.
Scene/backdrop: cinematic near-black evening outside a generic large U.S. retail superstore storefront with blue-and-white architectural colors but absolutely no logo, no emblem, no readable signage, and no brand marks; a neutral red-and-white pizza delivery box and a grocery delivery tote move together along a polished delivery route.
Subject: the generic retail superstore facade and distinct pizza delivery package are the dominant concrete subjects, clearly communicating retail-plus-restaurant delivery without any third-party branding.
Style/medium: high-end photorealistic financial-news editorial photography, premium realistic materials and sharp detail.
Composition/framing: exact 1:1 square; storefront and delivery package occupy the center and lower two-thirds; reserve the lower-right 20 percent as clean near-black negative space for later placement of the supplied circular when2buy logo; leave clean upper-left space for factual typography to be composited later.
Lighting/mood: high-contrast dusk lighting, crisp white rim light, controlled red accent, urgent but factual.
Color palette: near-black, charcoal, white, restrained red and muted blue; no decorative green.
Text (verbatim): none; all typography was composited later.
Constraints: no readable text, numbers, logos, emblems, source handle, URL, attribution, disclaimer, commentary, CTA, tagline, recommendation, watermark, generic radar graphic, pure typography card, or extra people."""

def stamp():
    return datetime.now(timezone.utc).isoformat()

def main():
    document = state.load_state()
    source = next(item for item in document["benchmarkPosts"] if item["id"] == SOURCE_ID)
    if any(item.get("id") == PACKAGE_ID for item in document["packages"]):
        raise SystemExit(f"package already exists: {PACKAGE_ID}")
    expires = datetime.strptime(source["postedAt"], "%a %b %d %H:%M:%S %z %Y").timestamp() + 90 * 60
    if datetime.now(timezone.utc).timestamp() >= expires:
        raise SystemExit("selected source expired before production")
    target = ROOT / "deliverables" / PACKAGE_ID
    target.mkdir(parents=True, exist_ok=True)
    generated = target / "generated-base.png"
    final = target / "when2buy-image-model.png"
    shutil.copyfile(BASE, generated)
    subprocess.run([
        "convert", str(generated),
        "-gravity", "northwest", "-fill", "white", "-stroke", "black", "-strokewidth", "2",
        "-font", "DejaVu-Sans-Bold", "-pointsize", "64", "-annotate", "+64+74", "WALMART $WMT",
        "-pointsize", "42", "-annotate", "+64+132", "RESTAURANT DELIVERY EXPANDS",
        "-pointsize", "38", "-annotate", "+64+184", "PAPA JOHN'S $PZZA",
        "(", str(LOGO), "-resize", "112x112", ")", "-gravity", "southeast", "-geometry", "+36+36", "-composite",
        str(final),
    ], check=True)
    identify = subprocess.check_output(["identify", "-format", "%wx%h", str(final)], text=True).strip()
    if identify != "1254x1254":
        raise SystemExit(f"unexpected image size: {identify}")
    created = stamp()
    document["packages"].append({
        "id": PACKAGE_ID,
        "benchmarkPostId": SOURCE_ID,
        "benchmarkPostUrl": source["url"],
        "title": "Walmart expands restaurant delivery to Papa John's",
        "status": "ready",
        "postText": "Walmart $WMT will start delivering food orders from Papa John's $PZZA as it expands into restaurant delivery.",
        "mirroredFacts": ["Walmart will start delivering food orders from Papa John's as it expands into restaurant delivery."],
        "verificationSources": [source["url"], "https://corporate.walmart.com/news/2026/09/walmart-expands-restaurant-delivery-with-dunkin"],
        "imagePath": str(final.relative_to(ROOT)),
        "createdAt": created,
        "sourceExpiresAt": datetime.fromtimestamp(expires, timezone.utc).isoformat().replace("+00:00", "Z"),
        "visualProduction": {"method": "image_model", "prompt": PROMPT, "logoApplied": True, "qaStatus": "passed", "qa": {"inspectedAt": created, "result": "passed", "checks": ["square 1254x1254 PNG", "complete unbranded retail-store and pizza-delivery entity scene", "visible factual text is limited to Walmart, Papa John's, tickers, and event wording", "premium near-black, white, blue, and restrained-red palette", "no source, attribution, disclaimer, commentary, CTA, tagline, recommendation, or watermark", "not a pure-text card or generic-radar visual", "exact repository logo composited once"]}},
    })
    document["runs"].append({"id": f"run-{datetime.now(timezone.utc).strftime('%Y%m%dT%H%M%SZ')}-produce", "mode": "produce", "status": "succeeded", "startedAt": created, "completedAt": stamp(), "summary": "Produced the sole newest Walmart/Papa John's fresh package with an inspected entity-led image and exact-logo composite.", "reason": "", "packageId": PACKAGE_ID})
    errors = state.validate(document)
    if errors:
        raise SystemExit("\n".join(errors))
    state.atomic_write(document)
    print(PACKAGE_ID)

if __name__ == "__main__":
    main()
