#!/usr/bin/env python3
"""Resolve and apply a release version to source manifests."""
import argparse
import json
import re
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


def parse_version(value: str) -> tuple[int, int, int]:
    if not re.fullmatch(r"(0|[1-9][0-9]*)\.(0|[1-9][0-9]*)\.(0|[1-9][0-9]*)", value):
        raise ValueError(f"invalid version: {value}")
    return tuple(map(int, value.split(".")))


def release(repo: Path, requested: str = "", apply: bool = False) -> str:
    paths = [repo / "src/manifests" / host / "plugin.json" for host in ("claude", "cursor", "codex")]
    payloads = {p: json.loads(p.read_text()) for p in paths}
    versions = {p["version"] for p in payloads.values()}
    if len(versions) != 1:
        raise ValueError("source plugin versions disagree")
    current = versions.pop()
    major, minor, patch = parse_version(current)
    next_version = requested.strip() or f"{major}.{minor}.{patch + 1}"
    if parse_version(next_version) <= parse_version(current):
        raise ValueError(f"release version {next_version} must exceed {current}")
    for path in (repo / "src/manifests").glob("*/marketplace.json"):
        payload = json.loads(path.read_text())
        for plugin in payload.get("plugins", []):
            if "version" in plugin:
                if plugin["version"] != current:
                    raise ValueError(f"marketplace version disagrees: {path}")
                plugin["version"] = next_version
        payloads[path] = payload
    for path in paths:
        payloads[path]["version"] = next_version
    if apply:
        for path, payload in payloads.items():
            path.write_text(json.dumps(payload, indent=2) + "\n")
    return next_version


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--repo", type=Path, default=ROOT)
    parser.add_argument("--requested", default="")
    parser.add_argument("--apply", action="store_true")
    args = parser.parse_args()
    try:
        print(release(args.repo, args.requested, args.apply))
    except (ValueError, KeyError) as exc:
        parser.exit(1, f"{exc}\n")
