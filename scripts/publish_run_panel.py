#!/usr/bin/env python3
"""Update the one stable when2buy panel without querying the protected registry."""
import argparse
import subprocess
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
PANEL = ROOT / "reports" / "run-panel.html"
COMMAND = [
    "report", "publish", str(PANEL),
    "--namespace", "when2buy",
    "--slug", "content-run-panel",
    "--update",
]


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--check-only", action="store_true")
    args = parser.parse_args()
    if not PANEL.is_file() or PANEL.stat().st_size == 0:
        raise SystemExit("reports/run-panel.html is missing or empty")
    if args.check_only:
        print("Stable panel publisher is configured.")
        return
    subprocess.run(COMMAND, cwd=ROOT, check=True)


if __name__ == "__main__":
    main()
