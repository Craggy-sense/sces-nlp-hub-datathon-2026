# Organiser review and submission record

Only organisers should have write/admin access. Students contribute through forks. Team directories are an organisational convention, not an access-control boundary. Forks cannot change the upstream repository until a maintainer accepts the PR.

## Before accepting a submission

1. Verify the submitting team and inspect every changed path. All changes must be in one assigned `teams/team-XX/` directory. Reject unrelated files, other team changes, root or workflow changes, deletions outside that directory and suspicious renames.
2. Inspect the team README, required materials and runnable instructions. Open the presentation/demo video and confirm access. Never treat the automated check as a quality, rights or completeness assessment.
3. Record the PR URL, opening time, latest included commit time and the exact PR head SHA assessed. Compare with the deadline: **12 November 2026, 23:59 EAT / 20:59 UTC**. Record late changes separately; use organiser decisions for exceptions.
4. Retain the team's original source-repository commit SHA. Archive an exact source snapshot and any permitted externally stored data/model/video evidence needed for judging in organiser-controlled storage. Do not rely on a branch name or a mutable external link.
5. Give feedback, approve and merge only the reviewed commit. Do not merge PRs with changes to another team folder. A merge acknowledges receipt, not a judging score or data-release approval.

## Repository controls

- Protect `main`: require PRs, one code-owner approval, dismiss stale approvals, and prevent force pushes/deletion. Keep bypass access limited.
- `.github/CODEOWNERS` names the repository owner for all paths. CODEOWNERS requests/requires review when protected-branch settings enforce it; it does not create directory-level write permissions.
- The validation workflow reads PR file metadata only. It does not check out, import, install or execute student code. Its token is read-only.
- The automated check flags scope, README and file-size problems. It does not prove team identity, correctness, reviewer competence, video access, privacy or permission.
- Do not broaden student permissions to solve fork/PR problems. Help them correct their fork or use an explicitly recorded organiser-approved fallback.

The submission deadline extension leaves final review and moderation on **13 November** if the previously announced finalist date is retained. Organise parallel review rather than assuming the old two-full-day window still exists.
