#!/usr/bin/env python3
"""Select older patch tags superseded by the current release tag."""

from __future__ import annotations

import argparse
import re
import sys
from collections.abc import Iterable


SEMVER_TAG = re.compile(
    r"^v(0|[1-9]\d*)\.(0|[1-9]\d*)\.(0|[1-9]\d*)$"
)


def parse_tag(tag: str) -> tuple[int, int, int] | None:
    match = SEMVER_TAG.fullmatch(tag)
    if not match:
        return None
    return tuple(int(part) for part in match.groups())


def obsolete_patch_tags(current_tag: str, candidates: Iterable[str]) -> list[str]:
    current = parse_tag(current_tag)
    if current is None:
        raise ValueError(
            f"current tag must use exact vMAJOR.MINOR.PATCH syntax: {current_tag!r}"
        )

    obsolete: dict[tuple[int, int, int], str] = {}
    for candidate in candidates:
        tag = candidate.strip()
        version = parse_tag(tag)
        if version is None:
            continue
        if version[:2] == current[:2] and version[2] < current[2]:
            obsolete[version] = tag
    return [obsolete[version] for version in sorted(obsolete)]


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--current-tag", required=True)
    args = parser.parse_args(argv)
    try:
        tags = obsolete_patch_tags(args.current_tag, sys.stdin)
    except ValueError as exc:
        parser.error(str(exc))
    for tag in tags:
        print(tag)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
