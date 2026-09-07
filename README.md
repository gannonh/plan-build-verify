# plan-build-verify

Plan, Build, Review, and Verify as a Cursor, Claude Code, and Codex plugin. Specs live in Linear. GitHub Issues are inbound reports. This repository is the canonical plugin source. The current version is recorded in `src/manifests/claude/plugin.json`.

Project: [Plan Build Verify](https://linear.app/kata-sh/project/plan-build-verify-415bb335f84b). Import historical GitHub issues with Linear's native importer.

## Install

You need a current Cursor, Claude Code, or Codex installation and a connected Linear integration. The plugin provides `plan`, `build`, `review`, `verify`, and `triage` skills.

### Cursor

Install:

```shell
cursor-agent plugin marketplace add https://github.com/gannonh/plan-build-verify
```

Then install `plan-build-verify` from **Settings > Plugins**.

Update:

```shell
cursor-agent plugin marketplace update plan-build-verify
```

### Claude Code

Run these commands inside Claude Code:

```text
/plugin marketplace add gannonh/plan-build-verify
/plugin install plan-build-verify@plan-build-verify
/reload-plugins
```

Or from your shell:

```shell
claude plugin marketplace add gannonh/plan-build-verify
claude plugin install plan-build-verify@plan-build-verify
```

The shell path has no reload step. The plugin loads when the next Claude Code session starts.

### Codex

Install:

```shell
codex plugin marketplace add gannonh/plan-build-verify
codex plugin add plan-build-verify@plan-build-verify
```

Update:

```shell
codex plugin marketplace upgrade plan-build-verify
codex plugin add plan-build-verify@plan-build-verify
```

Turn on Codex subagents in `~/.codex/config.toml` so Build can dispatch implementers and independent reviewers:

```toml
[features]
multi_agent = true
```

Start a new Codex task after install or upgrade so it can discover the skills and setting.

## Runtime dependency

The `review` skill lands a PR during Agent Review. It calls [`npx agent-reviews`](https://github.com/pbakaus/agent-reviews) to list, filter, reply, and watch review comments (human and bot). Node.js 18+ is required at runtime. This repository does not vendor `agent-reviews` and does not add it to a package.json. `npx` fetches the published CLI when the skill runs.

## Build

Authoring source is `src/`. Generated plugin trees and marketplace catalogs are projections. The build is the only writer of those outputs.

```bash
python3 scripts/build.py
```

That command writes:

- `plugins/cursor` with `.cursor-plugin/plugin.json` and `assets/logo.svg`
- `plugins/claude` with `.claude-plugin/plugin.json` and `assets/logo.svg`
- `plugins/codex` with `.codex-plugin/plugin.json` and `assets/logo.svg`
- `.cursor-plugin/marketplace.json` (`source`: `plugins/cursor`)
- `.claude-plugin/marketplace.json` (`source`: `./plugins/claude`)
- `.agents/plugins/marketplace.json` (`source.path`: `./plugins/codex`)

Skill bodies are copied from `src/skills/*/SKILL.md`. Host manifests come from `src/manifests/{host}/plugin.json`. The logo is copied from `assets/logo.svg`. Do not edit files under `plugins/` by hand. Use the Release workflow to bump versions and publish changes.

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

Ported pack unit tests cover user-acceptance evidence scripts and generated-tree contracts. Those tests live in `tests/` and are not copied into the plugin trees.

## License

MIT. See [LICENSE](LICENSE).

## Publishing

Run **Actions → Release → Run workflow** on `main`. Leave `version` empty for a patch bump, or supply a higher `X.Y.Z` version. The workflow validates the current plugin, updates source manifest versions together, regenerates all host outputs, runs tests and Claude validation, and commits the release. It then pushes the commit and tag atomically and creates a GitHub release with generated notes. Publishing uses `GITHUB_TOKEN` with `contents: write`; repository rules must permit the workflow to push to `main`. No npm package is published.

To preview the next version locally, run `python3 scripts/release_version.py`. Adding `--requested X.Y.Z --apply` updates source manifests; follow it with `python3 scripts/build.py`.
