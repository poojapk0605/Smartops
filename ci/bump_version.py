#!/usr/bin/env python3
"""
bump_version.py [major|minor|patch]

Reads the VERSION file in the repo root, bumps it, writes it back,
and prints the new version to stdout.

Example:
    python3 ci/bump_version.py patch
"""

import sys
from pathlib import Path

VALID_BUMPS = {"major", "minor", "patch"}


def main() -> int:
    if len(sys.argv) != 2 or sys.argv[1] not in VALID_BUMPS:
        print(f"Usage: {sys.argv[0]} [major|minor|patch]", file=sys.stderr)
        return 1

    bump_type = sys.argv[1]
    version_file = Path("VERSION")

    if not version_file.exists():
        print("VERSION file not found in repo root.", file=sys.stderr)
        return 1

    current = version_file.read_text().strip()
    try:
        major, minor, patch = map(int, current.split("."))
    except ValueError:
        print(f"VERSION file contents '{current}' are not in MAJOR.MINOR.PATCH format.", file=sys.stderr)
        return 1

    if bump_type == "major":
        major += 1
        minor = 0
        patch = 0
    elif bump_type == "minor":
        minor += 1
        patch = 0
    elif bump_type == "patch":
        patch += 1

    new_version = f"{major}.{minor}.{patch}"
    version_file.write_text(new_version + "\n")

    # Jenkins will read this from stdout
    print(new_version)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
