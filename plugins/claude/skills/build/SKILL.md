---
name: build
description: Use this skill when executing a named, approved GitHub spec issue. Runs the plan-build-verify Build workflow with bundled TDD through implementation, review gates, a pushed branch, and a Build completion report. Does not open the pull request.
---

# Build

Execute an approved spec issue through small implementation tasks, review gates, and a pushed branch.

## Read the conventions first

Read `references/conventions.md` completely before any write.

## When to use

- The user named an approved spec issue, or Plan just handed off an approved issue.
- Build must not start from a `status:draft` issue unless the user explicitly overrides the approval gate.

## Build workflow

Read `references/build.md` completely and follow it.

Required bundled TDD:

1. Read `references/tdd/workflow.md` completely.
2. Follow linked files under `references/tdd/` as needed.
3. Do not substitute ad hoc TDD guidance when the bundled workflow applies.

Hard gates:

- Confirm `status:approved` and that the body's `## Status` section says `Approved`, or confirm an explicit user override. A Draft body is unapproved even if the label is `status:approved`.
- Confirm `## Acceptance criteria` with concrete checkbox criteria.
- Do not open the pull request. Verify owns PR creation.
- After the Build completion report, continue directly into Verify. Do not ask permission.

## Shared principles

- Keep scope tied to the selected issue and its acceptance criteria.
- Prefer the smallest end-to-end slice a user can see, use, or evaluate.
- Do not silently implement a different spec.
- Record approved deviations as issue comments starting with `## Approved deviation`.
- Do not close the spec issue from Build.
