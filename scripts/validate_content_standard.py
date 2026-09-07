#!/usr/bin/env python3
"""Fail closed before publishing content that violates the current when2buy standard."""
import argparse
import struct
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "skills" / "when2buy-content-publisher" / "scripts"))
import state  # noqa: E402

BRAND_LINE = "When2Buy — your U.S. stock partner."
BANNED = (
    "according to",
    "reported by",
    "market radar",
    "not independently verified",
    "not investment advice",
    "@whaleinsider",
    "@stockmktnewz",
)


def png_size(path):
    with path.open("rb") as handle:
        header = handle.read(24)
    if len(header) < 24 or header[:8] != b"\x89PNG\r\n\x1a\n" or header[12:16] != b"IHDR":
        return None
    return struct.unpack(">II", header[16:24])


def validate_package(package, root=ROOT):
    errors = []
    copy = str(package.get("postText") or "").strip()
    lower = copy.lower()
    if not copy:
        errors.append("postText is empty")
    if len(copy) > 280:
        errors.append("postText exceeds the X 280-character limit")
    for phrase in BANNED:
        if phrase in lower:
            errors.append(f"public copy contains banned phrase: {phrase}")
    if copy.count(BRAND_LINE) != 1 or not copy.endswith(BRAND_LINE):
        errors.append(f"public copy must end with exactly one brand line: {BRAND_LINE}")
    first_block = copy.split("\n\n", 1)[0].strip()
    if first_block == BRAND_LINE:
        errors.append("the event must appear before the brand line")
    if not package.get("benchmarkPostId") or not str(package.get("benchmarkPostUrl") or "").startswith("https://x.com/"):
        errors.append("internal benchmark provenance is missing")
    if not package.get("mirroredFacts"):
        errors.append("mirroredFacts is empty")

    production = package.get("visualProduction") if isinstance(package.get("visualProduction"), dict) else {}
    if production.get("method") != "image_model":
        errors.append("visualProduction.method must be image_model")
    if len(str(production.get("prompt") or "").strip()) < 40:
        errors.append("visualProduction.prompt is missing or too short")
    if production.get("logoApplied") is not True:
        errors.append("the exact when2buy logo must be applied after generation")
    if production.get("qaStatus") != "passed":
        errors.append("visualProduction.qaStatus must be passed")

    relative = str(package.get("imagePath") or "")
    image = (root / relative).resolve()
    try:
        image.relative_to(root.resolve())
    except ValueError:
        errors.append("imagePath escapes the repository")
        return errors
    if not image.is_file():
        errors.append("imagePath does not exist")
    else:
        size = png_size(image)
        if not size:
            errors.append("final image must be a PNG")
        elif size[0] != size[1] or size[0] < 900:
            errors.append(f"final image must be a square at least 900px; got {size[0]}x{size[1]}")
    return errors


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--package-id", required=True)
    args = parser.parse_args()
    document = state.load_state()
    package = next((item for item in document.get("packages", []) if item.get("id") == args.package_id), None)
    if not package:
        raise SystemExit("Package not found.")
    errors = validate_package(package)
    if errors:
        raise SystemExit("Content standard failed:\n- " + "\n- ".join(errors))
    print(f"Content standard passed: {args.package_id}")


if __name__ == "__main__":
    main()
