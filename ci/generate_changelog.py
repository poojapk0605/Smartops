#!/usr/bin/env python3
"""
generate_changelog.py <new_version>

Generates:
  - CHANGELOG_RELEASE.md  (notes for this single release)

It groups commits since the last tag by simple prefixes:
  feat:, fix:, docs:, refactor:, test:, ci:, perf:

This is good enough for a learning project + looks professional.
"""

import subprocess
import sys
from datetime import date
from pathlib import Path

CATEGORIES = {
    "feat:": "Added",
    "fix:": "Fixed",
    "docs:": "Docs",
    "refactor:": "Changed",
    "perf:": "Performance",
    "test:": "Tests",
    "ci:": "CI/CD",
}


def run_git(args: list[str]) -> str:
    return subprocess.check_output(["git"] + args, text=True).strip()


def get_previous_tag() -> str | None:
    try:
        return run_git(["describe", "--tags", "--abbrev=0"])
    except subprocess.CalledProcessError:
        return None


def main() -> int:
    if len(sys.argv) != 2:
        print(f"Usage: {sys.argv[0]} <new_version>", file=sys.stderr)
        return 1

    new_version = sys.argv[1]
    prev_tag = get_previous_tag()

    if prev_tag:
        rev_range = f"{prev_tag}..HEAD"
    else:
        # No previous tags: use full history
        rev_range = "HEAD"

    log_output = run_git(["log", rev_range, "--pretty=format:%s"])

    if not log_output:
        notes = f"No new commits since {prev_tag or 'repo init'}.\n"
    else:
        commits = log_output.splitlines()
        buckets: dict[str, list[str]] = {v: [] for v in CATEGORIES.values()}
        others: list[str] = []

        for msg in commits:
            matched = False
            for prefix, cat in CATEGORIES.items():
                if msg.startswith(prefix):
                    buckets[cat].append(msg[len(prefix):].strip())
                    matched = True
                    break
            if not matched:
                others.append(msg)

        lines = []
        lines.append(f"## v{new_version} — {date.today().isoformat()}\n")

        for category, items in buckets.items():
            if not items:
                continue
            lines.append(f"### {category}")
            for item in items:
                lines.append(f"- {item}")
            lines.append("")  # blank line

        if others:
            lines.append("### Other")
            for item in others:
                lines.append(f"- {item}")
            lines.append("")

        notes = "\n".join(lines) + "\n"

    # Write only this release's notes for GitHub Release body
    Path("CHANGELOG_RELEASE.md").write_text(notes)
    print("Generated CHANGELOG_RELEASE.md")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
