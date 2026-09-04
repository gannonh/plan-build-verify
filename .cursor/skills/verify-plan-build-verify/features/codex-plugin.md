# Codex plugin

The Codex tree is `plugins/codex`. A Codex install surfaces skills `plan`, `build`, `review`, `verify`, and `triage`. The tree has no `agents/` and no `commands/`. `.codex-plugin/` contains only `plugin.json`.

## Sub-features

- `codex-skills` exposes the same five skills as the other hosts.
- `codex-no-agents` keeps `agents/` absent.
- `codex-no-commands` keeps `commands/` absent.
- `codex-manifest` keeps `.codex-plugin/plugin.json` as the only file in that directory.

## How to get to it (user POV)

- Run `codex plugin marketplace add gannonh/plan-build-verify`, then `codex plugin add plan-build-verify@plan-build-verify`.
- Inspect the installed tree or `plugins/codex` in this checkout.

## Driving it with control-pbv

Preconditions:

- A launched run whose doctor output is `ready`.
- The Codex install path is under that run's `home/`.

- **Stage copy.** Launch copied `plugins/codex` to `$HOME/.codex/plugins/cache/plan-build-verify/plan-build-verify/<version>/` inside the throwaway home. Read `run.json` `codex_install`.
- **Drive install.** Run `.cursor/skills/verify-plan-build-verify/scripts/control-pbv drive codex-plugin`. Exit code `0`. `evidence/codex-plugin/result.txt` is `ok`.
- **Skills.** `evidence/codex-plugin/listing.txt` lists skills `build, plan, review, triage, verify`.
- **Layout.** The same listing says `agents (absent)` and `commands (absent)`. Manifests are `.codex-plugin` only.
- **Proof.** `evidence/codex-plugin/plugin.json` has `"name": "plan-build-verify"` and `"interface": { "displayName": "Plan Build Verify" }`. Re-read `codex_install` and confirm `.codex-plugin/` contains only `plugin.json`.

## Gotchas

- Do not run `codex plugin marketplace add` or `codex plugin add` with `control-pbv`. Those commands write the operator Codex cache.
- Codex binds `.agents/plugins/marketplace.json` first. A sparse checkout of only `.agents/plugins` omits `plugins/codex` and is not a valid install source.
- There is no published Codex JSON Schema. Layout and required fields are the proof, not `claude plugin validate`.
