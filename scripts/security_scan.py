#!/usr/bin/env python3
from pathlib import Path
import re
import sys

ROOT = Path(__file__).resolve().parents[1]
patterns = {
    "GitHub token": re.compile(r"gh[pousr]_[A-Za-z0-9_]{20,}"),
    "OpenAI key": re.compile(r"sk-(?:proj-)?[A-Za-z0-9_-]{20,}"),
    "X auth token": re.compile(r"auth_token\s*[=:]\s*[^\s]+", re.I),
}
findings = []
for path in ROOT.rglob("*"):
    if not path.is_file() or ".git" in path.parts:
        continue
    try:
        content = path.read_text(encoding="utf-8")
    except (UnicodeDecodeError, OSError):
        continue
    for label, pattern in patterns.items():
        if pattern.search(content):
            findings.append(f"{label}: {path.relative_to(ROOT)}")
if findings:
    print("Credential-like material detected:")
    print("\n".join(findings))
    sys.exit(1)
print("Security scan passed: no credential-like material detected.")
