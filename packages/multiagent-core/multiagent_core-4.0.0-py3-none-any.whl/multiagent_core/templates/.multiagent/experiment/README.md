# Experiment Integrity System

**Simple git safety tags - never lose your place again**

## Purpose

Prevents what happened today (wrong commit hash, hours lost recovering):
- Tag exact commit before branching
- Rollback to exact place anytime
- Clean up when done

## The Problem

```bash
# Today's disaster
git merge-base main feature  # ❌ Found old commit (3.4.3)
git reset --hard 35203ee6    # ❌ Lost weeks of work
# Hours spent recovering...
```

## The Solution

```bash
# Simple safety system
/experiment:start new-feature
# ✅ Tags THIS exact commit
# ✅ Creates experiment/new-feature branch
# ✅ Can always rollback to tag

# Work freely
git commit -m "trying new approach"

# Didn't work out?
/experiment:full-reset new-feature
# ✅ Back to exact starting point
# ✅ Branch and tag cleaned up
```

## Commands

### `/experiment:start <name>`
**What it does:**
```bash
git tag pre-experiment/<name>-<timestamp>  # Safety point
git checkout -b experiment/<name>           # New branch
mkdir experiments/<name>/                   # Tracking dir
```

### `/experiment:rollback`
**What it does:**
```bash
git reset --hard pre-experiment/<name>-<timestamp>
```

### `/experiment:cleanup <name>`
**What it does:**
```bash
git checkout main
git branch -D experiment/<name>
git tag -d pre-experiment/<name>-<timestamp>
rm -rf experiments/<name>/
```

### `/experiment:full-reset <name>` (orchestrator)
**What it does:**
Runs rollback → cleanup → switch to main in sequence

## Workflow

```bash
# 1. Before trying something risky
/experiment:start refactor-auth

# 2. Work on experiment
git add . && git commit -m "feat: new approach"

# 3. Decide outcome

# Option A: Experiment worked
git checkout main
git merge experiment/refactor-auth
/experiment:cleanup refactor-auth

# Option B: Experiment failed
/experiment:full-reset refactor-auth
# Back to exact starting point, everything cleaned up
```

## Safety Tags

Every experiment creates: `pre-experiment/<name>-<timestamp>`

These are your exact rollback points - not merge-base, not guesses.

## Integration with Git

This doesn't replace git - it's just safe wrappers:
- Uses standard git commands
- Creates standard git tags
- Creates standard git branches
- Just prevents human error
