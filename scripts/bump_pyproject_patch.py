#!/usr/bin/env python3
from __future__ import annotations

import argparse
import re
import sys
from pathlib import Path


VERSION_RE = re.compile(
    r"^(?P<prefix>\s*version\s*=\s*)(?P<quote>[\"'])(?P<version>[^\"']+)(?P=quote)(?P<suffix>\s*(?:#.*)?)$"
)
SECTION_RE = re.compile(r"^\s*\[(?P<section>[^\]]+)\]\s*$")


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Increment the patch segment of [project].version in pyproject.toml."
    )
    parser.add_argument(
        "--pyproject",
        default="pyproject.toml",
        type=Path,
        help="Path to pyproject.toml.",
    )
    return parser.parse_args()


def bump_patch(version: str) -> str:
    parts = version.split(".")
    if len(parts) != 3 or not all(part.isdigit() for part in parts):
        raise ValueError(f"Expected semantic version MAJOR.MINOR.PATCH, got {version!r}.")
    major, minor, patch = parts
    return f"{major}.{minor}.{int(patch) + 1}"


def bump_pyproject_patch(pyproject: Path) -> tuple[str, str]:
    if not pyproject.exists():
        raise FileNotFoundError(f"{pyproject} does not exist.")

    lines = pyproject.read_text(encoding="utf-8").splitlines(keepends=True)
    in_project = False

    for index, line in enumerate(lines):
        section_match = SECTION_RE.match(line.strip())
        if section_match:
            in_project = section_match.group("section").strip() == "project"
            continue

        if not in_project:
            continue

        version_match = VERSION_RE.match(line.rstrip("\n\r"))
        if not version_match:
            continue

        old_version = version_match.group("version")
        new_version = bump_patch(old_version)
        line_ending = ""
        if line.endswith("\r\n"):
            line_ending = "\r\n"
        elif line.endswith("\n"):
            line_ending = "\n"

        lines[index] = (
            f"{version_match.group('prefix')}"
            f"{version_match.group('quote')}{new_version}{version_match.group('quote')}"
            f"{version_match.group('suffix')}{line_ending}"
        )
        pyproject.write_text("".join(lines), encoding="utf-8")
        return old_version, new_version

    raise ValueError("Could not find [project] version in pyproject.toml.")


def main() -> int:
    args = parse_args()
    try:
        old_version, new_version = bump_pyproject_patch(args.pyproject)
    except Exception as exc:
        print(f"error: {exc}", file=sys.stderr)
        return 1

    print(f"old_version={old_version}")
    print(f"new_version={new_version}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
