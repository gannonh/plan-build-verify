#!/usr/bin/env python3
"""Project src/ into host plugin trees and marketplace catalogs.

This script is the only writer of plugins/**, .cursor-plugin/marketplace.json,
.claude-plugin/marketplace.json, and .agents/plugins/marketplace.json.
"""

from __future__ import annotations

import json
import shutil
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SRC = ROOT / "src"
SKILLS = (
    "plan",
    "build",
    "verify",
    "triage",
    "address-pr-comments",
)
HOSTS = ("cursor", "claude", "codex")
GENERATED_TREES = tuple(ROOT / "plugins" / host for host in HOSTS)
MARKETPLACES = {
    "cursor": ROOT / ".cursor-plugin" / "marketplace.json",
    "claude": ROOT / ".claude-plugin" / "marketplace.json",
    "codex": ROOT / ".agents" / "plugins" / "marketplace.json",
}


def normalize_text(data: bytes) -> bytes:
    if data.startswith(b"\xef\xbb\xbf"):
        data = data[3:]
    text = data.decode("utf-8").replace("\r\n", "\n").replace("\r", "\n")
    return (text.rstrip("\n") + "\n").encode("utf-8")


def write_normalized(source: Path, dest: Path) -> None:
    dest.parent.mkdir(parents=True, exist_ok=True)
    dest.write_bytes(normalize_text(source.read_bytes()))


def write_json(source: Path, dest: Path) -> None:
    payload = json.loads(source.read_text(encoding="utf-8"))
    dest.parent.mkdir(parents=True, exist_ok=True)
    dest.write_text(json.dumps(payload, indent=2) + "\n", encoding="utf-8")


def copy_tree(source: Path, dest: Path) -> None:
    dest.mkdir(parents=True, exist_ok=True)
    for path in source.rglob("*"):
        if path.is_dir():
            continue
        target = dest / path.relative_to(source)
        target.parent.mkdir(parents=True, exist_ok=True)
        shutil.copy2(path, target)


def wipe_generated() -> None:
    for tree in GENERATED_TREES:
        if tree.exists():
            shutil.rmtree(tree)
    for catalog in MARKETPLACES.values():
        if catalog.exists():
            catalog.unlink()


def copy_skill(name: str, dest_root: Path) -> None:
    source = SRC / "skills" / name
    dest = dest_root / "skills" / name
    copy_tree(source, dest)
    write_normalized(SRC / "shared" / "conventions.md", dest / "references" / "conventions.md")
    write_normalized(dest / "SKILL.md", dest / "SKILL.md")


def emit_host(host: str) -> Path:
    dest = ROOT / "plugins" / host
    dest.mkdir(parents=True)
    for name in SKILLS:
        copy_skill(name, dest)
    write_json(SRC / "manifests" / host / "plugin.json", dest / f".{host}-plugin" / "plugin.json")
    if host in {"cursor", "claude"}:
        copy_tree(SRC / "agents" / host, dest / "agents")
        copy_tree(SRC / "commands", dest / "commands")
    return dest


def main() -> None:
    wipe_generated()
    for host in HOSTS:
        emit_host(host)
    for host, dest in MARKETPLACES.items():
        write_json(SRC / "manifests" / host / "marketplace.json", dest)
    print("wrote plugins/cursor, plugins/claude, plugins/codex")
    print("wrote .cursor-plugin/marketplace.json")
    print("wrote .claude-plugin/marketplace.json")
    print("wrote .agents/plugins/marketplace.json")


if __name__ == "__main__":
    main()
