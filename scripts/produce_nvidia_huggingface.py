#!/usr/bin/env python3
"""Create the verified, original when2buy package for the newest NVDA source."""
from datetime import datetime, timezone
from pathlib import Path
import subprocess
import sys

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "skills" / "when2buy-content-publisher" / "scripts"))
import state  # noqa: E402

PACKAGE_ID = "pkg-20260903-nvda-hugging-face-acquisition"
BENCHMARK_ID = "2095486679737946360"
BENCHMARK_URL = "https://x.com/StockMKTNewz/status/2095486679737946360"
SOURCE_URL = "https://blogs.nvidia.com/blog/nvidia-to-acquire-hugging-face/"
IMAGE_RELATIVE = Path("deliverables") / PACKAGE_ID / "when2buy-nvda-hugging-face.png"
LOGO = ROOT / "skills" / "when2buy-content-publisher" / "assets" / "when2buy-logo-reference.png"


def make_image(path: Path):
    path.parent.mkdir(parents=True, exist_ok=True)
    svg = path.with_suffix(".svg")
    nodes = "".join(
        f'<path d="M{x} {y}L{x - 118} {y + 96}"/><circle cx="{x}" cy="{y}" r="6"/>'
        for x in range(625, 1060, 72) for y in range(105, 725, 92)
    )
    svg.write_text(f'''<svg xmlns="http://www.w3.org/2000/svg" width="1080" height="1080" viewBox="0 0 1080 1080">
<rect width="1080" height="1080" fill="#050608"/><g fill="none" stroke="#5b141c" stroke-width="2">{nodes}</g><g fill="none" stroke="#eb2a39" stroke-width="2">{nodes}</g>
<rect x="56" y="58" width="220" height="50" rx="25" fill="#eb2a39"/><g fill="#f8f8f6" font-family="DejaVu Sans" font-weight="700"><text x="83" y="92" font-size="28">MARKET MOVE</text><text x="58" y="216" font-size="72">NVDA +</text><text x="58" y="296" font-size="72">HUGGING FACE</text><text x="53" y="550" font-size="174">$12.93B</text><text x="86" y="748" font-size="28">18M+ developers  ·  3M+ models</text><text x="58" y="924" font-size="28">OPEN PLATFORM. NEW OWNER.</text></g>
<rect x="58" y="347" width="964" height="5" fill="#eb2a39"/><text x="60" y="650" fill="#eb2a39" font-family="DejaVu Sans" font-weight="700" font-size="72">ACQUISITION</text><rect x="58" y="692" width="900" height="122" rx="18" fill="none" stroke="#40444c" stroke-width="2"/><g fill="#a2a8b3" font-family="DejaVu Sans"><text x="86" y="793" font-size="30">NVIDIA says the platform stays open.</text><text x="58" y="966" font-size="30">Source: NVIDIA · Sep. 3, 2026</text></g><path d="M58 874H826" stroke="#40444c" stroke-width="2"/><image href="{LOGO}" x="906" y="906" width="118" height="118" preserveAspectRatio="xMidYMid meet"/></svg>''', encoding="utf-8")
    subprocess.run(["convert", str(svg), str(path)], check=True)
    svg.unlink()


def main():
    image = ROOT / IMAGE_RELATIVE
    make_image(image)
    current = state.load_state()
    package = {
        "id": PACKAGE_ID,
        "benchmarkPostId": BENCHMARK_ID,
        "benchmarkPostUrl": BENCHMARK_URL,
        "title": "NVIDIA to acquire Hugging Face for $12.93B",
        "status": "ready",
        "postText": "$NVDA is buying Hugging Face for $12.93B.\n\nNVIDIA says it will stay open across models, clouds and accelerators—not locked to NVIDIA compute.\n\nThe prize: 18M+ users and 3M+ models. This is a developer-distribution move, not just a chip deal.",
        "mirroredFacts": [
            "NVIDIA agreed to acquire Hugging Face for $12,930,300,000.",
            "NVIDIA says Hugging Face will remain open across models, clouds, inference providers and computing platforms.",
            "NVIDIA says more than 18 million people use Hugging Face and it hosts more than 3 million models."
        ],
        "verificationSources": [SOURCE_URL],
        "imagePath": str(IMAGE_RELATIVE),
        "createdAt": datetime.now(timezone.utc).isoformat(),
    }
    existing = next((item for item in current["packages"] if item.get("id") == PACKAGE_ID), None)
    if existing:
        existing.update(package)
    else:
        current["packages"].append(package)
    current["runs"].append({
        "id": f"run-{datetime.now(timezone.utc).strftime('%Y%m%dT%H%M%SZ')}-produce",
        "mode": "produce",
        "status": "succeeded",
        "startedAt": datetime.now(timezone.utc).isoformat(),
        "completedAt": datetime.now(timezone.utc).isoformat(),
        "summary": "Prepared a verified original NVIDIA/Hugging Face package from the newest uncovered StockMKTNewz source.",
        "reason": "Verified against NVIDIA's September 3, 2026 announcement; copy shortened after Postiz rejected the initial version as too long."
    })
    errors = state.validate(current)
    if errors:
        raise SystemExit("\n".join(errors))
    state.atomic_write(current)
    print(f"Created {PACKAGE_ID}: {IMAGE_RELATIVE}")


if __name__ == "__main__":
    main()
