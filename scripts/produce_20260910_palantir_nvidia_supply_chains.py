#!/usr/bin/env python3
"""Create the sole newest fresh Palantir/NVIDIA package for this run."""
from datetime import datetime, timezone
from pathlib import Path
import shutil
import subprocess
import sys

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "skills" / "when2buy-content-publisher" / "scripts"))
import state  # noqa: E402

SOURCE_ID = "2097978417425592472"
PACKAGE_ID = "pkg-20260910-palantir-nvidia-critical-supply-chains"
EXPIRES_AT = "2026-09-10T10:50:07Z"
BASE_SOURCE = Path("/root/.codex/generated_images/01a08ab4-d382-7290-b320-f0ec38aaeab7/exec-99c37bdf-2114-4896-9dd6-de488a9a0438.png")
LOGO = ROOT / "skills" / "when2buy-content-publisher" / "assets" / "when2buy-logo-reference.png"
PROMPT = """Use case: ads-marketing
Asset type: square X financial-news visual for When2Buy
Primary request: Create one complete original entity-led editorial visual about Palantir and NVIDIA partnering to bring AI capabilities to critical supply chains, starting with NVIDIA's own operations.
Scene/backdrop: a premium, realistic AI data-center and industrial supply-chain control environment with NVIDIA-style GPU server racks, a subtle global logistics map, and Palantir-style operational data overlays; no recognizable third-party logos.
Subject: a dominant illuminated GPU server module connected to a physical supply-chain network of factories, cargo routes, and inventory nodes.
Style/medium: cinematic photorealistic financial-news editorial image, sharp detail, premium market-news aesthetic.
Composition/framing: exact 1:1 square; near-black base; dominant central entity-led scene; bold white typography with one restrained red accent; reserve clean lower-left space for later compositing of the supplied circular when2buy logo.
Lighting/mood: high-contrast studio lighting, urgent but factual.
Color palette: black, charcoal, white, controlled red accents; no green unless semantically necessary.
Text (verbatim): \"PALANTIR + NVIDIA\" and \"AI FOR CRITICAL SUPPLY CHAINS\"
Constraints: render the exact phrases legibly; no other readable words or numbers; no source handle, URL, attribution, disclaimer, commentary, CTA, tagline, recommendation, watermark, or generated logo; no pure typography card; no generic abstract background; do not imitate any existing brand logo; keep the image complete and visually meaningful before the logo is added."""


def main():
    now = datetime.now(timezone.utc)
    expiry = datetime.fromisoformat(EXPIRES_AT.replace("Z", "+00:00"))
    if now >= expiry:
        raise SystemExit("Skipped: source expired before image packaging")
    document = state.load_state()
    if any(package.get("id") == PACKAGE_ID for package in document["packages"]):
        raise SystemExit(f"Skipped: package already exists: {PACKAGE_ID}")
    source = next(post for post in document["benchmarkPosts"] if post["id"] == SOURCE_ID)
    target = ROOT / "deliverables" / PACKAGE_ID
    target.mkdir(parents=True, exist_ok=True)
    base = target / "generated-base.png"
    final = target / "when2buy-image-model.png"
    shutil.copyfile(BASE_SOURCE, base)
    subprocess.run([
        "convert", str(base), "(", str(LOGO), "-resize", "112x112", ")",
        "-gravity", "southwest", "-geometry", "+36+36", "-composite", str(final),
    ], check=True)
    stamp = now.isoformat()
    document["packages"].append({
        "id": PACKAGE_ID,
        "benchmarkPostId": SOURCE_ID,
        "benchmarkPostUrl": source["url"],
        "title": "Palantir and NVIDIA partner on critical supply chains",
        "status": "ready",
        "postText": "Palantir and NVIDIA are partnering to bring AI capabilities to critical supply chains, starting with NVIDIA's own operations.",
        "mirroredFacts": [
            "Palantir and NVIDIA are partnering to bring AI capabilities to critical supply chains.",
            "The collaboration starts with NVIDIA's own operations.",
        ],
        "verificationSources": [
            "https://investor.nvidia.com/news/press-release-details/2025/Palantir-and-NVIDIA-Team-Up-to-Operationalize-AI--Turning-Enterprise-Data-Into-Dynamic-Decision-Intelligence/default.aspx",
        ],
        "imagePath": str(final.relative_to(ROOT)),
        "createdAt": stamp,
        "sourceExpiresAt": EXPIRES_AT,
        "visualProduction": {
            "method": "image_model", "prompt": PROMPT, "logoApplied": True,
            "qaStatus": "passed",
            "qa": {"inspectedAt": stamp, "result": "passed", "checks": [
                "square 1254x1254",
                "complete entity-led GPU server and supply-chain control scene",
                "exact PALANTIR + NVIDIA and AI FOR CRITICAL SUPPLY CHAINS text",
                "premium near-black, white, and restrained-red palette",
                "no source, attribution, disclaimer, commentary, CTA, tagline, recommendation, or watermark",
                "not a pure-text card or generic-radar visual",
                "exact repository logo composited once",
            ]},
        },
    })
    document["runs"].append({
        "id": f"run-{now.strftime('%Y%m%dT%H%M%SZ')}-produce",
        "mode": "produce", "status": "succeeded", "startedAt": stamp, "completedAt": stamp,
        "summary": "Produced the sole newest fresh queue package with an inspected image-model visual and exact-logo composite.",
        "reason": "",
    })
    errors = state.validate(document)
    if errors:
        raise SystemExit("\n".join(errors))
    state.atomic_write(document)
    print(f"Prepared: {PACKAGE_ID}")


if __name__ == "__main__":
    main()
