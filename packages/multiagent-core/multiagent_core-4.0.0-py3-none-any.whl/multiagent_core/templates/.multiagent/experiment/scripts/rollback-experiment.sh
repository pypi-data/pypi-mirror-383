#!/bin/bash
# Rollback to pre-experiment safety tag

set -e

# Get current branch to determine experiment name
CURRENT_BRANCH=$(git branch --show-current 2>/dev/null)

if [[ ! "$CURRENT_BRANCH" =~ ^experiment/ ]]; then
    echo "❌ Error: Not on an experiment branch"
    echo "Current branch: ${CURRENT_BRANCH}"
    echo ""
    echo "To rollback manually, find your tag:"
    echo "  git tag --list 'pre-experiment/*'"
    echo "  git reset --hard <tag-name>"
    exit 1
fi

# Extract experiment name from branch
EXPERIMENT_NAME="${CURRENT_BRANCH#experiment/}"

# Find matching tag
SAFETY_TAG=$(git tag --list "pre-experiment/${EXPERIMENT_NAME}-*" | head -1)

if [ -z "$SAFETY_TAG" ]; then
    echo "❌ Error: No safety tag found for experiment: ${EXPERIMENT_NAME}"
    echo ""
    echo "Available tags:"
    git tag --list "pre-experiment/*"
    exit 1
fi

echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "⚠️  Experiment Rollback"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo ""
echo "Experiment: ${EXPERIMENT_NAME}"
echo "Current branch: ${CURRENT_BRANCH}"
echo "Safety tag: ${SAFETY_TAG}"
echo ""
echo "This will:"
echo "  - Reset to: ${SAFETY_TAG}"
echo "  - DISCARD all uncommitted changes"
echo "  - DISCARD all commits after the tag"
echo ""

# Check for uncommitted changes
if ! git diff-index --quiet HEAD -- 2>/dev/null; then
    echo "⚠️  WARNING: You have uncommitted changes:"
    git status --short
    echo ""
fi

read -p "Proceed with rollback? [y/N] " -n 1 -r
echo
if [[ ! $REPLY =~ ^[Yy]$ ]]; then
    echo "Cancelled."
    exit 1
fi

# Perform rollback
echo ""
echo "🔄 Resetting to ${SAFETY_TAG}..."
git reset --hard "${SAFETY_TAG}"

echo ""
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "✅ Rollback Complete"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo ""
echo "Current state:"
git log -1 --oneline
echo ""
echo "Still on branch: ${CURRENT_BRANCH}"
echo ""
echo "To clean up experiment:"
echo "  /experiment:cleanup"
echo ""
echo "To switch back to main:"
echo "  git checkout main"
