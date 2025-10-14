#!/bin/bash
# Cleanup experiment branch and tag

set -e

EXPERIMENT_NAME="$1"

# If no name provided, try to detect from current branch
if [ -z "$EXPERIMENT_NAME" ]; then
    CURRENT_BRANCH=$(git branch --show-current 2>/dev/null)
    if [[ "$CURRENT_BRANCH" =~ ^experiment/ ]]; then
        EXPERIMENT_NAME="${CURRENT_BRANCH#experiment/}"
    else
        echo "❌ Error: Experiment name required"
        echo "Usage: /experiment:cleanup <name>"
        echo ""
        echo "Or run from an experiment branch"
        exit 1
    fi
fi

EXPERIMENT_BRANCH="experiment/${EXPERIMENT_NAME}"
SAFETY_TAG=$(git tag --list "pre-experiment/${EXPERIMENT_NAME}-*" | head -1)

echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "🧹 Cleanup Experiment"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo ""
echo "Experiment: ${EXPERIMENT_NAME}"
echo ""

# Check if on experiment branch
CURRENT_BRANCH=$(git branch --show-current 2>/dev/null)
if [ "$CURRENT_BRANCH" = "$EXPERIMENT_BRANCH" ]; then
    echo "⚠️  Currently on experiment branch"
    echo "Switching to main first..."
    git checkout main
    echo ""
fi

# Delete branch
if git show-ref --verify --quiet "refs/heads/${EXPERIMENT_BRANCH}"; then
    echo "🗑️  Deleting branch: ${EXPERIMENT_BRANCH}"
    git branch -D "${EXPERIMENT_BRANCH}"
    echo "✅ Branch deleted"
else
    echo "ℹ️  Branch not found: ${EXPERIMENT_BRANCH}"
fi

# Delete tag
if [ -n "$SAFETY_TAG" ]; then
    echo "🗑️  Deleting tag: ${SAFETY_TAG}"
    git tag -d "${SAFETY_TAG}"
    echo "✅ Tag deleted"
else
    echo "ℹ️  No safety tag found for: ${EXPERIMENT_NAME}"
fi

# Clean experiment directory if exists
EXPERIMENT_DIR="experiments/${EXPERIMENT_NAME}"
if [ -d "$EXPERIMENT_DIR" ]; then
    echo "🗑️  Removing directory: ${EXPERIMENT_DIR}/"
    rm -rf "$EXPERIMENT_DIR"
    echo "✅ Directory removed"
fi

echo ""
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "✅ Cleanup Complete"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo ""
echo "Experiment '${EXPERIMENT_NAME}' fully removed"
