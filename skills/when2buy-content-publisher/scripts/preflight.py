#!/usr/bin/env python3
from pathlib import Path
import sys

SKILL = Path(__file__).resolve().parents[1]
required = [
    SKILL / "assets" / "when2buy-logo-reference.png",
    SKILL / "assets" / "style-examples" / "intel-financing.png",
    SKILL / "assets" / "style-examples" / "riot-ai-infrastructure.png",
    SKILL / "assets" / "style-examples" / "us-macro-calendar.png",
    SKILL / "references" / "brand-and-style.md",
    SKILL / "references" / "cases.md",
]
missing = [str(path.relative_to(SKILL)) for path in required if not path.is_file() or path.stat().st_size == 0]
skill_text = (SKILL / "SKILL.md").read_text(encoding="utf-8")
required_workflow_tokens = [
    "https://x.com/WhaleInsider",
    "https://x.com/StockMKTNewz",
    "08:30, 12:30, 18:30, and 22:30",
    "benchmarkPostId",
    "brand-and-style.md",
    "assets/when2buy-logo-reference.png",
]
missing.extend(f"SKILL.md token: {token}" for token in required_workflow_tokens if token not in skill_text)
if missing:
    print("Missing required when2buy production inputs:")
    print("\n".join(missing))
    sys.exit(1)
print("Preflight passed: benchmark workflow, logo, style examples, and text cases are present.")
