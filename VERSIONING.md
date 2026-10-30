# Mandatory update/version policy

**Official team repo version starts at `V1.000`.** This is a fresh repository baseline, not a claim that there were no earlier prototype iterations. Existing files with `V9`, `V10`, `V11`, `V12` in the names are historical snapshots.

1. **Every update merged into `main` increments exactly once**: `V1.000` → `V1.001` → `V1.002` → `V1.003`.
2. One pull request = one update. Editing multiple files in that pull request still advances only one increment.
3. The PR author must run `python tools/version.py bump --message "What changed"` **once, before opening the PR**; this edits `VERSION`, `version.json`, `CHANGELOG.md`, and the Mnemosyne repo handoff together.
4. GitHub Actions checks on PRs require the submitted version to equal the destination branch version **plus exactly 1**. If parallel PRs both choose the same next version, the later PR must update from `main` and bump again before merging.
5. The shared version is a **repository revision**, not a hardware readiness score, and it does not mean the physical car is working.
6. Rebuild offline progress/roster snapshots if their JSON source is changed. `project_progress.json` tracks *milestones*, separately from code version.
7. At merge, record the changes and any test evidence. When handing work to Claude, update the Mnemosyne handoff note with version and changed interfaces.
8. For fixes requested in chat but not merged into GitHub, mark them `draft`/`unreleased`; **do not** advance the official deployed version until the change is merged.
9. For `V1.999` rollover, coordinate a new `V2.000` baseline with the team; do not silently reset the counter.

## Manual command

```bash
python tools/version.py bump --message "Updated the hallway map"
python tools/version.py check
```

Check current version with `cat VERSION`; optionally tag merged `main` commits: `git tag V1.001 && git push origin V1.001`.

**Important:** GitHub cannot automatically edit and commit files from a PR validation workflow; the CI here enforces the policy rather than silently rewriting code.
