---
name: closeBranch
description: Close out a branch after its PR is merged/closed - switches to the PR's base branch (main, or the todo's arc branch), pulls latest, deletes local and remote branch
argument-hint: ""
allowed-tools: ["Bash"]
---

Clean up after a merged or closed PR by switching to the branch the PR targeted and deleting the branch.

Under the iterative-todo branch model a plan or punchlist branch PRs into the todo's **arc branch** (`{id}-arc` — e.g. `lcr-rewrite`), and the arc PRs into `main` when the todo closes. This command follows the PR's base rather than assuming `main`, so it serves both cases: closing a plan branch lands you on the arc, freshly pulled and ready to cut the next plan; closing the arc lands you on `main`.

## Instructions

Execute these steps in order, stopping immediately if any check fails.

### Step 1: Get the current branch and confirm the tree is clean

```bash
git branch --show-current
git status --porcelain
```

Save the branch as the one to delete. If it is `main` or `master`, stop and report: "Already on main, nothing to close." If `git status --porcelain` prints anything, stop and report: "Working tree has uncommitted changes on `{branch}`; commit or stash them first."

### Step 2: Find the PR and its base

```bash
gh pr view --json state,number,title,baseRefName
```

If this fails with "no pull requests found", stop and report: "No PR found for branch `{branch}`."

Save `baseRefName` as `{base}`. This is where you will land: `main` when closing an arc branch, the arc branch when closing a plan or punchlist branch.

### Step 3: Check the PR state

`state` must be `MERGED` or `CLOSED`. If it is `OPEN`, stop and report: "PR #{number} is still open. Merge or close it first." Never merge it yourself — merging is the user's.

### Step 4: Switch to the base

```bash
git switch {base}
```

`git switch` creates a local tracking branch from `origin/{base}` if none exists yet.

### Step 5: Pull latest

```bash
git pull
```

### Step 6: Delete the local branch

```bash
git branch -D {branch}
```

`-D` because a branch whose PR was closed without merging is not fully merged.

### Step 7: Delete the remote branch

```bash
git push origin --delete {branch}
git fetch --prune
```

The push may fail if the remote branch was already deleted (GitHub's delete-on-merge). That is fine — note it was already gone. The prune drops the stale remote ref either way.

### Step 8: Report

- Plan or punchlist branch (`{base}` is not `main`): "Branch `{branch}` cleaned up (PR #{number} {merged|closed}). Now on `{base}` with latest changes — the next plan branches from here."
- Arc branch (`{base}` is `main`): "Arc `{branch}` closed into main (PR #{number}). Now on main with latest changes."
