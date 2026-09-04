# Development lifecycle

Recorded automation policy for this repository's Linear team. Preflight reads this file and resolves the state names through `list_issue_statuses`.

## Team

- Workspace / team: Kata-sh
- Project: Plan Build Verify
- Maintainer: Gannon Hall
- Verification date: 2026-09-04
- Evidence: maintainer screenshot of team workflow settings, attested 2026-09-04

This record documents observed settings. It does not change production Linear automation.

## PR event mappings

| GitHub event | Linear action |
| ------------ | ------------- |
| Draft PR open | Move issue to In Progress |
| PR open | Move issue to Agent Review |
| PR review request or activity | No action |
| PR ready for merge | No action |
| PR merge | Move issue to Done |

## Branch-specific rules

None configured.

## Related team settings

- Parent issues auto-close when their last sub-issue closes.
- Sub-issues do not auto-close with their parent.
- Stale issues move to Canceled after six months.
- Closed items auto-archive after six months.

## Agent-owned transitions

The integration owns the mappings above. Agents still perform these writes when the live state has not already moved:

- Build: Todo to In Progress on explicit start.
- Build: In Progress to Agent Review after draft readiness when the issue is still In Progress.
- Review: Agent Review to Human Review after merge-ready gates.
- Closed PR without merge: move to Todo (lifecycle reconciliation only).

Humans own Backlog to Todo (approval) and the move into Merging (merge permission).

Draft-to-ready behavior is not proven by the screenshot. Observe it on the live issue before assuming PR-open automation fired.

## Verification scope

The maintainer waived the live scratch Linear team and GitHub repo demonstration on 2026-09-04. Routine plugin changes require the four CI commands and isolated installed-candidate checks. No scratch team or manual test transition is required. These checks do not prove live integration behavior.
