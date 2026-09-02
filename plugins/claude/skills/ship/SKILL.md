---
name: ship
description: Use this skill when landing an open pull request. Owns settled-red CI and unanswered review comments from humans and bots. Calls npx agent-reviews to list, filter, reply, and watch. Do not merge.
---

# Ship

Land an open pull request. Do not merge it. Signoff and merge stay with the user.

This skill owns two landing surfaces:

- Settled-red CI. Checks that have finished and failed. Pending or queued checks are not red yet. Wait until they settle.
- Unanswered review comments from humans and bots.

## Runtime dependency

Review comments go through [agent-reviews](https://github.com/pbakaus/agent-reviews) at runtime.

```bash
npx agent-reviews
```

Do not vendor `agent-reviews` into this repository. Do not add it to a package.json. Do not npm-pack it. `npx` fetches the published CLI when the skill runs. Node.js 18+ is required. If the project prefers another runner, use that runner's equivalent (`pnpm dlx agent-reviews`, `yarn dlx agent-reviews`, or `bunx agent-reviews`).

Auth is the CLI's job. It reads `GITHUB_TOKEN`, then `GH_TOKEN`, then `.env.local`, then `gh auth token`. Run `gh auth status` before the first write if the session has not already.

Do not paginate review comments with raw `gh`. Do not use `gh api graphql` review-thread queries or `gh api` review-comment list endpoints to inventory or reply. Those paths miss replies, drop pages, and invent unresolved state. `npx agent-reviews` is the list, filter, reply, and watch interface.

`gh` remains correct for PR metadata, checks, run logs, and mergeability. Those are not review-comment pagination.

## When to use

- Verify has opened a PR and needs it landed.
- The user asks to land, ship, or drive the current PR to merge-ready.
- CI has settled red, or unanswered review comments are blocking signoff.

Read `references/conventions.md` before any write.

## Preconditions

- An open PR exists for the current branch, or the caller named a PR number.
- `gh` is authenticated.
- Node.js is available so `npx agent-reviews` can run.

If there is no PR, stop and say so. Opening a PR is Verify's job.

## Landing loop

Review comments first. A review fix produces a new commit that retriggers CI. Fixing flakes on a SHA you are about to replace is wasted work.

### 1. Inventory unanswered comments

```bash
npx agent-reviews --unanswered --expanded --json
```

Add `--pr <N>` when the caller named a PR. The CLI auto-detects the current branch's PR otherwise.

Build a ledger before editing. For each comment record `id`, author, human or bot, path, ask, classification, evidence, action, and disposition.

If the JSON list is empty, continue to settled CI.

### 2. Classify against current code

Classify each unanswered comment against the code on HEAD, not the diff the reviewer saw.

- `fix`. Still valid. Patch it. Add a regression test when the comment describes recurring behavior.
- `already-addressed`. Current code already satisfies the ask.
- `false-positive`. The finding is wrong, outdated, or not a defect.
- `question`. Answer it from the code.
- `unsafe-to-change`. The ask contradicts approved acceptance criteria or would be destructive.

Every classification needs evidence. Never silently drop a comment.

Stop and return to Plan when a reviewer asks for a change that contradicts approved acceptance criteria.

### 3. Apply fixes, then reply through agent-reviews

Validate locally after fixes. Commit and push when code changed. Capture the head SHA.

Reply to every processed comment. Prefix the body with `[agent]` so authorship is unambiguous.

```bash
npx agent-reviews --reply <id> "[agent] Fixed in <sha>. <what changed>"
```

```bash
npx agent-reviews --reply <id> "[agent] <disposition>. <evidence-backed rationale>" --resolve
```

Use `--resolve` when closing the conversation (`already-addressed`, `false-positive`, `question`, `unsafe-to-change`). Leave `fix` threads open so the reviewer can confirm. Ignore GitHub `PENDING` reviews.

If the CLI prints that a comment is not part of a review thread, record the outcome and move on. Do not retry with raw `gh`.

### 4. Watch for new comments

After replies are posted:

```bash
npx agent-reviews --watch --unanswered
```

If the watcher exits with new comments, return to step 1. If it completes with no new unanswered comments, continue.

### 5. Wait for CI to settle

```bash
gh pr view --json number,headRefOid,mergeable,mergeStateStatus,statusCheckRollup
gh pr checks --required --watch --fail-fast
```

Drop `--required` when the repo marks nothing as required. Keep consuming the watch output in the same turn. A pending or queued check is not settled. A cancelled skip is not green.

### 6. Act on settled-red CI

When checks have finished and failed:

```bash
gh run view <run-id> --log-failed
```

If a single job failed while the run is still going, pull that job's logs. Do not wait for the whole run when the failure is already visible.

Classify:

- Branch-related. Compile, test, lint, typecheck, or snapshot failures in code this branch touched. Fix, validate locally, commit, push.
- Flaky or infrastructural. Timeouts, runner provisioning, registry or network outages, Actions infra errors. Rerun up to 3 times with `gh run rerun <run-id> --failed`.

Do not edit tests, CI configuration, or dependency pins to hide an unrelated failure. If classification is ambiguous, diagnose once before rerunning.

### 7. Mergeability

Resolve merge conflicts against the base branch by rebasing or merging, per repo convention. Do not force-push over commits you did not create.

### 8. Re-enter

After any push or rerun, return to step 1 on the new SHA in the same turn.

## Exit

Exit only when all of these hold on the current head SHA:

- Every required check is green. Not pending, not queued, not skipped-because-cancelled.
- `npx agent-reviews --unanswered --json` returns no unanswered comments.
- No merge conflict.

A green snapshot while checks are still running is not an exit.

Do not merge. Present the ledger, final SHA, and CI state for signoff.

## Abort

Stop and report when:

- There is no open PR.
- `npx agent-reviews` cannot authenticate or cannot see the PR.
- The flaky-retry budget (3) is exhausted on the same check.
- CI fails for reasons outside the branch that you cannot fix.
- A reviewer asks for a change that contradicts approved acceptance criteria.
- The same check fails 3 times after 3 distinct fix attempts.
- A fix would require force-pushing over commits you did not create.

## Never

- Merge the PR.
- Paginate or reply to review comments with raw `gh`.
- Vendor or npm-pack `agent-reviews`.
- Drop a review comment without a posted disposition.
- Treat pending CI as red.
- End the turn with the landing loop unfinished and no abort condition reached.
