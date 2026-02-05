---
name: closeBranch
description: Close out a branch after its PR is closed/merged - switches to main, pulls latest, deletes local and remote branch
argument-hint: ""
allowed-tools: ["Bash"]
---

Clean up after a merged or closed PR by switching to main and deleting the branch.

## Instructions

Execute these steps in order, stopping immediately if any check fails:

### Step 1: Get current branch

```bash
git branch --show-current
```

Save this as the branch to delete. If on `main` or `master`, stop and report: "Already on main branch, nothing to close."

### Step 2: Check for PR

```bash
gh pr view --json state,number,title
```

If this fails with "no pull requests found", stop and report: "No PR found for branch `{branch}`."

### Step 3: Check PR state

From the JSON output, check the `state` field. Valid closed states are `MERGED` or `CLOSED`.

If state is `OPEN`, stop and report: "PR #{number} is still open. Close or merge it first."

### Step 4: Switch to main

```bash
git checkout main
```

### Step 5: Pull latest

```bash
git pull
```

### Step 6: Delete local branch

```bash
git branch -D {branch}
```

Use `-D` to force delete (the branch may not be fully merged if PR was closed without merging).

### Step 7: Delete remote branch

```bash
git push origin --delete {branch}
```

This may fail if the remote branch was already deleted (common after merge). That's fine - just note it was already gone.

### Step 8: Report success

Report: "Branch `{branch}` cleaned up. Now on main with latest changes."
