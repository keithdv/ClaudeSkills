---
name: AllRecursiveReposClean
description: Check if all git repositories in subdirectories are fully committed to main/master with no pending changes or worktrees.
allowed-tools: Bash(find:*, git:*)
---

# All Recursive Repos Clean Check

Scan for all git repositories under the current working directory and verify each is in a clean state.

## What to Check

For each discovered git repository:

1. **Branch** - Is it on `main` or `master`?
2. **Pending changes** - Any modified, staged, or untracked files?
3. **Worktrees** - Any extra worktrees beyond the main one?

## Execution

Run the following commands to discover and check all repositories:

```bash
# Find all git repositories in current directory (max depth 4)
find . -maxdepth 4 -type d -name ".git" 2>/dev/null
```

For each discovered repo, check status:

```bash
# For each repo directory (parent of .git):
cd "$repo"
echo "=== $repo ==="
echo "Branch: $(git branch --show-current)"
echo "Status:"
git status --short
echo "Worktrees:"
git worktree list
```

## Report Format

Provide a summary table:

| Repository | Status | Issue |
|------------|--------|-------|
| repo-name | Clean / Pending / Branch | Description of issue |

Then list repos with issues:

**Repos with work hanging:**
1. **RepoName** - description of the issue

## Clean Criteria

A repo is considered "clean" if:
- On `main` or `master` branch
- No output from `git status --short` (no modified/untracked files)
- Only one worktree listed (the main one)

A repo with issues should be flagged with:
- **Pending** - has uncommitted changes
- **Branch** - not on main/master
- **Worktree** - has additional worktrees
