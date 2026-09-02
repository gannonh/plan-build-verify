---
name: plan
description: Use this skill when scoping, designing, or specifying work as a GitHub Issue, or when migrating file-based specs under docs/specs/. Runs the plan-build-verify Plan workflow and migrate mode. Default for a new build request even when the user says "build".
---

# Plan

Turn ideas into approved GitHub Issue specs. Migrate mode stays in this skill.

## Read the conventions first

Read `references/conventions.md` completely before any write. It defines the repo preflight, label taxonomy, issue body template, status transitions, sub-issues, dependencies, temporary body files, and coexistence with pstack.

## When to use

- Scoping, designing, or specifying work.
- No `status:approved` issue exists for the request.
- The user asks to migrate `docs/specs/*.md` into issues.

A new build request starts here even when the user says "build". For tiny, clearly bounded edits such as a copy change, do not force the full Plan workflow and do not open an issue. State the assumption and ask whether the user wants the full process.

## Plan workflow

Read `references/plan.md` completely and follow it.

Hard gates:

- Do not draft a spec issue before the user has answered an alignment question or approved a recommended direction.
- Every spec issue must include an exact `## Acceptance criteria` section with observable pass/fail checkboxes.
- Do not invent a second issue tracker. Do not create or maintain product specs under `docs/specs/` except the migration index/archive described in `references/conventions.md`.
- After Plan, the only workflow you invoke is Build. Do not implement product code here.

## Migrate mode

Read `references/migration.md` completely when converting `docs/specs/*.md` into issues.

Migration is assess-first and one-way. Run `scripts/migrate_specs.sh --assess` and settle every unclassified or conflicting file with the user before any write.

## Helper scripts

Resolve paths against the skill directory the runtime actually loaded. If a configured skill path does not exist, stop and ask which installation to use. Never copy skill files into the project working tree to make a path resolve.

- `scripts/ensure_labels.sh`: idempotently creates the label taxonomy. `--dry-run` reports what would change.
- `scripts/migrate_specs.sh`: bulk-converts `docs/specs/*.md` into spec issues, archives the sources, rewrites cross-links, and updates the specs index. Run `--assess`, then `--dry-run`, then apply.
- `scripts/rewrite_spec_links.py`: repoints Markdown links after files move into the archive. Called by the migration script; requires `python3`.

## Requirements

- `gh` CLI, authenticated with issue write access for the target repo.
- `gh sub-issue` extension (`yahsan2/gh-sub-issue`) for decomposed specs.
- A `gh` recent enough for issue dependencies (`gh issue edit --add-blocked-by`).
- `jq`, for reading `gh sub-issue list --json` output.
- `python3`, for link rewriting during migration only.

Run the preflight in `references/conventions.md` before the first `gh` write of a session.

## Shared principles

- Inspect the repo and the issue backlog before making claims about project structure or existing work.
- In Plan, ask focused alignment questions one at a time before drafting the issue.
- Propose 2-3 approaches when more than one viable direction exists.
- Prefer the smallest end-to-end slice a user can see, use, or evaluate.
- Decompose epics by demonstrable behavior, not by architecture layer.
- A spec issue is incomplete unless it has an exact `## Acceptance criteria` section.
- The issue is the spec. Local Markdown exists only as a temporary body file.
- Surface uncertainty instead of filling gaps with guesses.
