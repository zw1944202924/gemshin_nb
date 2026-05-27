# Repository Instructions

Use `git-branch-discipline` for any task that edits files in this repository or reports delivery status.
Read `git-branch-discipline` before starting those tasks. This is a strict prerequisite, not an optional reference.
If you delegate those tasks to another agent, explicitly instruct that agent to read `git-branch-discipline` before doing any analysis, edits, commits, or delivery reporting.

## Baseline branch

- Follow the user or issue if a baseline branch is explicitly named.
- If no baseline is specified, use the repository's real default branch.
- For `gemshin_nb`, the remote default branch is `main` as of 2026-05-27, and there is no remote `dev` branch.

## Branch rules

- Do not edit directly on `main`.
- Before the first commit, create a readable task branch from the approved baseline, even if checkout started on `agent/agent/...`.
- Preferred names: `feature/<scope>`, `fix/<scope>`, `docs/<scope>`, `chore/<scope>`.

## Merge and approval rules

- Do not merge to `main` without explicit user approval.
- If the project later introduces an integration branch such as `dev`, land there first unless the user says otherwise.

## Completion evidence

Any completion update for a code or docs task must include:

- repository name
- baseline branch
- task branch
- commit hash, or explicit `local only, uncommitted`
- modified file paths
- current landing location such as branch head or PR

If those details are missing, the task is not ready to be reported as complete.
