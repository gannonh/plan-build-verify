# Cursor local install

Cursor local install is the README copy of `plugins/cursor` into `~/.cursor/plugins/local/plan-build-verify`. After Allow Local Plugin Imports is on, the plugin details list skills `plan`, `build`, `review`, `verify`, and `triage`, agents `plan-agent`, `build-agent`, and `verify-agent`, and commands `/plan`, `/build`, and `/verify`.

## Sub-features

- `cursor-copy` copies the Cursor tree into the local plugin path.
- `cursor-skills` exposes `plan`, `build`, `review`, `verify`, and `triage` in the installed copy.
- `cursor-agents` exposes `plan-agent`, `build-agent`, and `verify-agent`.
- `cursor-commands` exposes `/plan`, `/build`, and `/verify` with the required descriptions.
- `cursor-manifest` keeps only `.cursor-plugin/plugin.json` as the host manifest.

## How to get to it (user POV)

- Copy `plugins/cursor` to `~/.cursor/plugins/local/plan-build-verify` as the README says.
- Enable Allow Local Plugin Imports, then enable `plan-build-verify`.
- Open the plugin details and the command palette for `/plan`, `/build`, and `/verify`.

## Driving it with control-pbv

Preconditions:

- A launched run whose doctor output is `ready`.
- The Cursor install path is under that run's `home/`, not the operator home.

- **Copy tree.** Launch already copied `plugins/cursor` to `$HOME/.cursor/plugins/local/plan-build-verify` inside the throwaway home. Read `run.json` `cursor_install`. That path ends with `.cursor/plugins/local/plan-build-verify`.
- **Drive install.** Run `.cursor/skills/verify-plan-build-verify/scripts/control-pbv drive cursor-local-install`. Exit code `0`. `evidence/cursor-local-install/result.txt` is `ok`.
- **Skills.** Open `evidence/cursor-local-install/listing.txt`. The skills line lists `build, plan, review, triage, verify`.
- **Agents.** The same listing lists `build-agent.md, plan-agent.md, verify-agent.md`.
- **Commands.** `evidence/cursor-local-install/commands/plan.md` contains `description: Run the plan-build-verify Plan workflow`. `build.md` and `verify.md` contain the Build and Verify twins.
- **Manifest.** `evidence/cursor-local-install/plugin.json` has `"name": "plan-build-verify"` and `"skills": "./skills/"`. The listing manifests line is `.cursor-plugin` only.
- **Proof.** Re-read `cursor_install` from `run.json` and confirm the files still exist after the drive. Capture `listing.txt` and `plugin.json`.

## Gotchas

- The operator machine already has a live copy at `~/.cursor/plugins/local/plan-build-verify`. Driving that path corrupts the user's plugin. Refuse it.
- Team marketplace import is Teams or Enterprise only. It is not this gate.
- Cursor plugin UI screenshots need a human Cursor session. Isolated drive proves the copied tree. Record the UI screenshot as `verified-unreachable` unless that session is in use.
- `review` and `triage` must exist in the tree even when the plugin UI highlights only Plan, Build, and Verify.
