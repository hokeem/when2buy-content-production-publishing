#!/usr/bin/env python3
"""Render and publish one explicitly selected When2Buy report surface."""
import argparse
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
TARGETS = {
    "content": {
        "renderer": ROOT / "scripts" / "render_run_panel.py",
        "artifact": ROOT / "reports" / "run-panel.html",
        "slug": "content-run-panel",
    },
    "performance": {
        "renderer": ROOT / "scripts" / "render_metrics_dashboard.py",
        "artifact": ROOT / "reports" / "metrics-dashboard.html",
        "slug": "performance-dashboard",
    },
    "weekly": {
        "renderer": ROOT / "scripts" / "render_weekly_analysis.py",
        "artifact": ROOT / "reports" / "weekly",
        "slug": "weekly-content-analysis",
    },
}


def render_and_publish(name):
    target = TARGETS[name]
    subprocess.run([sys.executable, str(target["renderer"])], cwd=ROOT, check=True)
    artifact = target["artifact"]
    if not artifact.exists():
        raise SystemExit(f"Missing generated artifact: {artifact.relative_to(ROOT)}")
    subprocess.run(
        [
            "report", "publish", str(artifact),
            "--namespace", "when2buy",
            "--slug", target["slug"],
            "--update",
        ],
        cwd=ROOT,
        check=True,
    )


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--target",
        action="append",
        choices=tuple(TARGETS),
        help="report surface to render and publish; repeat for multiple surfaces",
    )
    parser.add_argument("--check-only", action="store_true")
    parser.add_argument(
        "--weekly",
        action="store_true",
        help="deprecated compatibility alias that adds the weekly target",
    )
    args = parser.parse_args()

    targets = list(dict.fromkeys(args.target or ["content", "performance"]))
    if args.weekly and "weekly" not in targets:
        targets.append("weekly")

    missing = [
        str(TARGETS[name]["renderer"].relative_to(ROOT))
        for name in targets
        if not TARGETS[name]["renderer"].is_file()
    ]
    if missing:
        raise SystemExit("Missing report renderer: " + ", ".join(missing))
    if args.check_only:
        print("Configured report targets: " + ", ".join(targets))
        return
    for name in targets:
        render_and_publish(name)


if __name__ == "__main__":
    main()
