# Git Collaboration Workflow

This repository uses an evidence-first Git workflow for both humans and agents.

## Current repository baseline

- The remote default branch is `main`.
- There is no remote `dev` branch as of 2026-05-27.
- If a user, issue, or future repo policy names a different baseline branch, that instruction takes precedence for the task.

## Required flow for every task

1. Identify the baseline branch before editing.
2. Create a dedicated task branch from that baseline.
3. Keep all changes and commits on the task branch.
4. Request review before any merge to `main`.
5. Merge to `main` only after explicit user approval.

## Task branch naming

Use a readable prefix plus scope:

- `feature/<scope>` for product or engineering work
- `fix/<scope>` for bug fixes
- `docs/<scope>` for documentation-only changes
- `chore/<scope>` for maintenance work

Example names:

- `feature/myw-21-api-setup`
- `fix/login-error-message`
- `docs/myw-26-git-workflow-guard`

## Multica-specific rule

`multica repo checkout` creates a temporary working branch such as `agent/agent/<id>`.
That branch is acceptable as a staging checkout, but it is not the final delivery branch.
Before the first commit, switch to a readable task branch derived from the approved baseline.

## Minimum delivery evidence

A completion report is incomplete unless it includes all of the following:

- repository name
- baseline branch
- task branch
- commit hash, or explicit `local only, uncommitted`
- modified file paths
- current landing location such as branch head or PR URL

## Review and merge policy

- Never commit directly on `main`.
- Never merge directly to `main` without explicit approval.
- If a future `dev` or other integration branch is introduced, tasks should land there first unless the user says otherwise.

## Ready-to-use report template

```text
Repo: gemshin_nb
Baseline: <baseline-branch>
Task branch: <task-branch>
Commit: <hash | local only, uncommitted>
Files: <path1>, <path2>, <path3>
Landing target: <branch head | PR URL | local only>
```
