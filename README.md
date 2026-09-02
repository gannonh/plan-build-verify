# plan-build-verify

Plan, Build, and Verify as a Cursor, Claude Code, and Codex plugin. Specs live in GitHub Issues. This repository is the canonical source for plugin version **0.1.0**.

Epic: [Install plan-build-verify as a Cursor, Claude, and Codex plugin](https://github.com/gannonh/plan-build-verify/issues/1).

pstack stays a separate Cursor plugin. This plugin owns specs, labels, and Plan / Build / Verify.

## Install

Public Cursor Marketplace and Claude plugin directory listings are not live. Listing copy is in [docs/marketplace-listings.md](docs/marketplace-listings.md) and on [issue #6](https://github.com/gannonh/plan-build-verify/issues/6). The Anysphere and Claude forms still need a human account.

Listing submitted. Listings are not public yet.

Cursor listing URL: _submitted, not public yet_

Claude listing URL: _submitted, not public yet_

### Cursor

Copy the generated Cursor tree into the local plugin directory:

```bash
cp -R plugins/cursor ~/.cursor/plugins/local/plan-build-verify
```

Enable **Allow Local Plugin Imports**, then enable `plan-build-verify`. The plugin details should list skills `plan`, `build`, `verify`, `triage`, and `ship` plus agents `plan-agent`, `build-agent`, and `verify-agent`. Commands `/plan`, `/build`, and `/verify` load the matching skill.

Team marketplace import is Teams/Enterprise only and is not the Verify gate.

### Claude Code

```text
/plugin marketplace add gannonh/plan-build-verify
/plugin install plan-build-verify@plan-build-verify
```

Claude should surface the same five skills and three agents. `/plan`, `/build`, and `/verify` load the matching skill.

### Codex

```text
codex plugin marketplace add gannonh/plan-build-verify
codex plugin add plan-build-verify@plan-build-verify
```

Codex binds `.agents/plugins/marketplace.json` first, so the installed tree is `plugins/codex`. That tree ships skills `plan`, `build`, `verify`, `triage`, and `ship`. It has no `agents/` or `commands/` directory. v1 has no Codex public-directory listing.

If a sparse checkout is used, it must be:

```text
--sparse .agents/plugins --sparse plugins/codex
```

Do not use `--sparse .agents/plugins` alone. That omits `plugins/codex`.

## Runtime dependency

The `ship` skill lands a PR. It calls [`npx agent-reviews`](https://github.com/pbakaus/agent-reviews) to list, filter, reply, and watch review comments (human and bot). Node.js 18+ is required at runtime. This repository does not vendor `agent-reviews` and does not add it to a package.json. `npx` fetches the published CLI when the skill runs.

## Build

Authoring source is `src/`. Generated plugin trees and marketplace catalogs are projections. The build is the only writer of those outputs.

```bash
python3 scripts/build.py
```

That command writes:

- `plugins/cursor` with `.cursor-plugin/plugin.json`
- `plugins/claude` with `.claude-plugin/plugin.json`
- `plugins/codex` with `.codex-plugin/plugin.json`
- `.cursor-plugin/marketplace.json` (`source`: `plugins/cursor`)
- `.claude-plugin/marketplace.json` (`source`: `./plugins/claude`)
- `.agents/plugins/marketplace.json` (`source.path`: `./plugins/codex`)

Skill bodies are copied from `src/skills/*/SKILL.md`. Do not edit files under `plugins/` by hand. Bump `version` in `src/manifests/` when skill bodies or generated manifests change. The first ship is `0.1.0`.

## How CI proves the trees

The default-branch workflow runs the same command a reviewer can run locally:

```bash
python3 scripts/build.py
python3 scripts/check.py
python3 -m pytest
claude plugin validate ./plugins/claude --strict
```

`scripts/check.py` fails when any of these are true:

- Generated paths are dirty after the build (`git status` on `plugins/`, `.cursor-plugin/marketplace.json`, `.claude-plugin/marketplace.json`, and `.agents/plugins/marketplace.json`).
- Hashed `skills/*/SKILL.md` or `skills/*/references/conventions.md` bodies diverge across Cursor, Claude, and Codex after newline normalization.
- The three `plugin.json` `version` strings disagree.
- A Cursor `plugin.json` or marketplace catalog fails the Cursor JSON Schema (live URL, vendored fallback).
- A host tree contains the wrong host's plugin.json directory, a `hooks/` directory, `mcp.json`, or `.mcp.json`.
- The Codex tree has `agents/` or `commands/`, or `.codex-plugin/` contains any file other than `plugin.json`.
- The Codex catalog is missing required `name`, `source`, `policy.installation`, `policy.authentication`, or `category` fields.

Ported pack unit tests cover migrate helpers and user-acceptance evidence scripts. Those tests live in `tests/` and are not copied into the plugin trees.

## License

MIT. See [LICENSE](LICENSE).
