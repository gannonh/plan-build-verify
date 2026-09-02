#!/usr/bin/env python3
"""Prove generated plugin trees match src/ and host layout rules."""

from __future__ import annotations

import hashlib
import json
import subprocess
import sys
import urllib.request
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
HOSTS = ("cursor", "claude", "codex")
SKILLS = (
    "plan",
    "build",
    "verify",
    "triage",
    "ship",
)
HASHED_RELATIVE = (
    "SKILL.md",
    "references/conventions.md",
)
COMMAND_DESCRIPTIONS = {
    "plan": "Run the plan-build-verify Plan workflow",
    "build": "Run the plan-build-verify Build workflow",
    "verify": "Run the plan-build-verify Verify workflow",
}
CURSOR_PLUGIN_SCHEMA_URL = "https://cursor.com/schemas/cursor-plugin/plugin.json"
CURSOR_MARKETPLACE_SCHEMA_URL = "https://cursor.com/schemas/cursor-plugin/marketplace.json"
GENERATED_GIT_PATHS = (
    "plugins",
    ".cursor-plugin/marketplace.json",
    ".claude-plugin/marketplace.json",
    ".agents/plugins/marketplace.json",
)
FORBIDDEN_HOST_DIRS = {
    "cursor": (".claude-plugin", ".codex-plugin"),
    "claude": (".cursor-plugin", ".codex-plugin"),
    "codex": (".cursor-plugin", ".claude-plugin"),
}
CODEX_PLUGIN_REQUIRED = ("name", "version", "description", "license", "skills")
CODEX_CATALOG_REQUIRED = ("name", "source", "policy", "category")


def normalize_text(data: bytes) -> bytes:
    if data.startswith(b"\xef\xbb\xbf"):
        data = data[3:]
    text = data.decode("utf-8").replace("\r\n", "\n").replace("\r", "\n")
    return (text.rstrip("\n") + "\n").encode("utf-8")


def digest(path: Path) -> str:
    return hashlib.sha256(normalize_text(path.read_bytes())).hexdigest()


def load_json(path: Path) -> object:
    return json.loads(path.read_text(encoding="utf-8"))


def plugin_manifest(host: str, root: Path = ROOT) -> Path:
    return root / "plugins" / host / f".{host}-plugin" / "plugin.json"


def fetch_schema(url: str, fallback: Path) -> dict:
    try:
        request = urllib.request.Request(url, headers={"Accept": "application/schema+json, application/json"})
        with urllib.request.urlopen(request, timeout=10) as response:
            payload = json.loads(response.read().decode("utf-8"))
        if isinstance(payload, dict) and ("$schema" in payload or "properties" in payload):
            return payload
    except (OSError, ValueError, json.JSONDecodeError):
        pass
    return json.loads(fallback.read_text(encoding="utf-8"))


def validate_schema(instance: object, schema: dict, label: str, errors: list[str]) -> None:
    try:
        import jsonschema
    except ImportError:
        if not isinstance(instance, dict):
            errors.append(f"{label}: expected a JSON object")
            return
        for field in schema.get("required", []):
            if field not in instance:
                errors.append(f"{label}: missing {field}")
        return
    try:
        jsonschema.validate(instance, schema)
    except jsonschema.ValidationError as exc:
        errors.append(f"{label}: {exc.message}")


def collect_errors(root: Path = ROOT, *, require_git_clean: bool = True) -> list[str]:
    errors: list[str] = []

    versions = []
    for host in HOSTS:
        path = plugin_manifest(host, root)
        if not path.is_file():
            errors.append(f"missing {path.relative_to(root)}")
            continue
        try:
            manifest = load_json(path)
        except json.JSONDecodeError as exc:
            errors.append(f"{path.relative_to(root)}: {exc}")
            continue
        if not isinstance(manifest, dict):
            errors.append(f"{path.relative_to(root)}: expected a JSON object")
            continue
        version = manifest.get("version")
        if not isinstance(version, str):
            errors.append(f"{path.relative_to(root)}: missing version")
        else:
            versions.append(version)
        for field in ("name", "description", "license"):
            if field not in manifest:
                errors.append(f"{path.relative_to(root)}: missing {field}")
        if manifest.get("name") != "plan-build-verify":
            errors.append(f"{path.relative_to(root)}: name must be plan-build-verify")
        if host == "codex":
            for field in CODEX_PLUGIN_REQUIRED:
                if field not in manifest:
                    errors.append(f"{path.relative_to(root)}: missing {field}")
            author = manifest.get("author")
            if not isinstance(author, dict) or "url" not in author:
                errors.append(f"{path.relative_to(root)}: Codex author must include url")
            interface = manifest.get("interface")
            if not isinstance(interface, dict) or interface.get("displayName") != "Plan Build Verify":
                errors.append(f"{path.relative_to(root)}: Codex interface.displayName must be Plan Build Verify")
            if "hooks" in manifest:
                errors.append(f"{path.relative_to(root)}: v1 ships no hooks field")
        else:
            author = manifest.get("author")
            if not isinstance(author, dict) or "name" not in author or "email" not in author:
                errors.append(f"{path.relative_to(root)}: author must be an object with name and email")
            if "interface" in manifest:
                errors.append(f"{path.relative_to(root)}: Cursor/Claude manifests must not include Codex interface")
            for key in ("skills", "agents", "commands"):
                rel = manifest.get(key)
                values = [rel] if isinstance(rel, str) else rel if isinstance(rel, list) else None
                if values is None:
                    errors.append(f"{path.relative_to(root)}: {key} must be a path or list of paths")
                    continue
                for item in values:
                    if not isinstance(item, str):
                        errors.append(f"{path.relative_to(root)}: {key} entries must be strings")
                        continue
                    target = (path.parent.parent / item).resolve()
                    if not target.exists():
                        errors.append(f"{path.relative_to(root)}: {key} path does not exist: {item}")

    if versions and len(set(versions)) != 1:
        errors.append(f"plugin.json version mismatch: {versions}")

    hashes: dict[tuple[str, str], dict[str, str]] = {}
    for host in HOSTS:
        tree = root / "plugins" / host
        if not tree.is_dir():
            errors.append(f"missing plugins/{host}")
            continue
        skills_root = tree / "skills"
        if skills_root.is_dir():
            observed = sorted(p.name for p in skills_root.iterdir() if p.is_dir())
            expected = sorted(SKILLS)
            if observed != expected:
                errors.append(
                    f"plugins/{host}/skills must be {', '.join(expected)}; found {', '.join(observed) or '(none)'}"
                )
        for skill in SKILLS:
            skill_dir = tree / "skills" / skill
            if not skill_dir.is_dir():
                errors.append(f"missing plugins/{host}/skills/{skill}")
                continue
            for rel in HASHED_RELATIVE:
                path = skill_dir / rel
                if not path.is_file():
                    errors.append(f"missing {path.relative_to(root)}")
                    continue
                hashes.setdefault((skill, rel), {})[host] = digest(path)
        for forbidden in FORBIDDEN_HOST_DIRS[host]:
            if (tree / forbidden).exists():
                errors.append(f"plugins/{host} must not contain {forbidden}/")
        for path in tree.rglob("*"):
            if path.name in {"mcp.json", ".mcp.json"}:
                errors.append(f"forbidden file {path.relative_to(root)}")
            if path.is_dir() and path.name == "hooks":
                errors.append(f"forbidden directory {path.relative_to(root)}")

    for (skill, rel), observed in hashes.items():
        missing = [host for host in HOSTS if host not in observed]
        if missing:
            errors.append(f"hashed identity missing {skill}/{rel} on {missing}")
            continue
        if len(set(observed.values())) != 1:
            errors.append(f"hashed identity drift for skills/{skill}/{rel}: {observed}")

    cursor_tree = root / "plugins" / "cursor"
    claude_tree = root / "plugins" / "claude"
    codex_tree = root / "plugins" / "codex"
    for agent in ("plan-agent.md", "build-agent.md", "verify-agent.md"):
        if not (cursor_tree / "agents" / agent).is_file():
            errors.append(f"missing plugins/cursor/agents/{agent}")
        if not (claude_tree / "agents" / agent).is_file():
            errors.append(f"missing plugins/claude/agents/{agent}")
    if (codex_tree / "agents").exists():
        errors.append("plugins/codex/agents must not exist")
    if (codex_tree / "commands").exists():
        errors.append("plugins/codex/commands must not exist")
    codex_plugin_dir = codex_tree / ".codex-plugin"
    if codex_plugin_dir.is_dir():
        extra = sorted(p.name for p in codex_plugin_dir.iterdir() if p.name != "plugin.json")
        if extra:
            errors.append(f".codex-plugin/ must contain only plugin.json; found {extra}")
    elif not (codex_plugin_dir / "plugin.json").is_file():
        errors.append("missing plugins/codex/.codex-plugin/plugin.json")

    for host in ("cursor", "claude"):
        for name, expected in COMMAND_DESCRIPTIONS.items():
            path = root / "plugins" / host / "commands" / f"{name}.md"
            if not path.is_file():
                errors.append(f"missing {path.relative_to(root)}")
                continue
            text = path.read_text(encoding="utf-8")
            if f"description: {expected}" not in text:
                errors.append(f"{path.relative_to(root)}: description must be {expected!r}")

    cursor_plugin = fetch_schema(CURSOR_PLUGIN_SCHEMA_URL, root / "scripts" / "schemas" / "cursor-plugin.json")
    cursor_marketplace = fetch_schema(
        CURSOR_MARKETPLACE_SCHEMA_URL,
        root / "scripts" / "schemas" / "cursor-marketplace.json",
    )
    if plugin_manifest("cursor", root).is_file():
        validate_schema(
            load_json(plugin_manifest("cursor", root)),
            cursor_plugin,
            "plugins/cursor/.cursor-plugin/plugin.json",
            errors,
        )
    catalog = root / ".cursor-plugin" / "marketplace.json"
    if catalog.is_file():
        payload = load_json(catalog)
        validate_schema(payload, cursor_marketplace, ".cursor-plugin/marketplace.json", errors)
        if isinstance(payload, dict):
            if payload.get("name") != "plan-build-verify":
                errors.append(".cursor-plugin/marketplace.json: name must be plan-build-verify")
            plugins = payload.get("plugins")
            if isinstance(plugins, list) and plugins:
                source = plugins[0].get("source") if isinstance(plugins[0], dict) else None
                if source != "plugins/cursor":
                    errors.append(".cursor-plugin/marketplace.json: source must be plugins/cursor")

    claude_catalog = root / ".claude-plugin" / "marketplace.json"
    if not claude_catalog.is_file():
        errors.append("missing .claude-plugin/marketplace.json")
    else:
        payload = load_json(claude_catalog)
        if not isinstance(payload, dict):
            errors.append(".claude-plugin/marketplace.json: expected a JSON object")
        else:
            if payload.get("name") != "plan-build-verify":
                errors.append(".claude-plugin/marketplace.json: name must be plan-build-verify")
            plugins = payload.get("plugins")
            if not isinstance(plugins, list) or not plugins or not isinstance(plugins[0], dict):
                errors.append(".claude-plugin/marketplace.json: missing plugin entry")
            else:
                source = plugins[0].get("source")
                if source != "./plugins/claude":
                    errors.append(".claude-plugin/marketplace.json: source must be ./plugins/claude")
                resolved = (root / "plugins" / "claude" / ".claude-plugin" / "plugin.json")
                if not resolved.is_file():
                    errors.append("Claude marketplace source does not resolve to .claude-plugin/plugin.json")

    codex_catalog = root / ".agents" / "plugins" / "marketplace.json"
    if not codex_catalog.is_file():
        errors.append("missing .agents/plugins/marketplace.json")
    else:
        payload = load_json(codex_catalog)
        if not isinstance(payload, dict) or payload.get("name") != "plan-build-verify":
            errors.append(".agents/plugins/marketplace.json: name must be plan-build-verify")
        else:
            plugins = payload.get("plugins")
            if not isinstance(plugins, list) or not plugins or not isinstance(plugins[0], dict):
                errors.append(".agents/plugins/marketplace.json: missing plugin entry")
            else:
                entry = plugins[0]
                for field in CODEX_CATALOG_REQUIRED:
                    if field not in entry:
                        errors.append(f".agents/plugins/marketplace.json: missing {field}")
                source = entry.get("source")
                if not isinstance(source, dict) or source.get("source") != "local" or source.get("path") != "./plugins/codex":
                    errors.append(".agents/plugins/marketplace.json: source must be local ./plugins/codex")
                policy = entry.get("policy")
                if not isinstance(policy, dict) or "installation" not in policy or "authentication" not in policy:
                    errors.append(".agents/plugins/marketplace.json: policy must include installation and authentication")

    if require_git_clean:
        proc = subprocess.run(
            ["git", "status", "--porcelain", "--", *GENERATED_GIT_PATHS],
            cwd=root,
            capture_output=True,
            text=True,
            check=False,
        )
        dirty = proc.stdout.strip()
        if dirty:
            errors.append(f"generated paths are dirty after build:\n{dirty}")

    return errors


def main() -> int:
    errors = collect_errors()
    if errors:
        for error in errors:
            print(error, file=sys.stderr)
        return 1
    print("plugin trees match src/ and host layout rules")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
