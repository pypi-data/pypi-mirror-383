#!/bin/bash
# Full reset: rollback + cleanup in one command

set -e

EXPERIMENT_NAME="$1"

if [ -z "$EXPERIMENT_NAME" ]; then
    # Try to detect from current branch
    CURRENT_BRANCH=$(git branch --show-current 2>/dev/null)
    if [[ "$CURRENT_BRANCH" =~ ^experiment/ ]]; then
        EXPERIMENT_NAME="${CURRENT_BRANCH#experiment/}"
    else
        echo "❌ Error: Experiment name required or run from experiment branch"
        echo "Usage: /experiment:full-reset <name>"
        exit 1
    fi
fi

echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "🔄 Full Experiment Reset"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo ""
echo "This will:"
echo "  1. Rollback to safety tag"
echo "  2. Cleanup branch and tag"
echo "  3. Return to main branch"
echo ""
echo "Experiment: ${EXPERIMENT_NAME}"
echo ""

read -p "Proceed with full reset? [y/N] " -n 1 -r
echo
if [[ ! $REPLY =~ ^[Yy]$ ]]; then
    echo "Cancelled."
    exit 1
fi

echo ""
echo "Step 1/3: Rolling back..."
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"

# Get script directory
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"

# Run rollback (suppress interactive prompt)
SAFETY_TAG=$(git tag --list "pre-experiment/${EXPERIMENT_NAME}-*" | head -1)
if [ -n "$SAFETY_TAG" ]; then
    git reset --hard "${SAFETY_TAG}"
    echo "✅ Rolled back to ${SAFETY_TAG}"
else
    echo "⚠️  No safety tag found, skipping rollback"
fi

echo ""
echo "Step 2/3: Switching to main..."
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
git checkout main
echo "✅ On main branch"

echo ""
echo "Step 3/3: Cleaning up..."
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"

# Delete branch
EXPERIMENT_BRANCH="experiment/${EXPERIMENT_NAME}"
if git show-ref --verify --quiet "refs/heads/${EXPERIMENT_BRANCH}"; then
    git branch -D "${EXPERIMENT_BRANCH}"
    echo "✅ Deleted branch: ${EXPERIMENT_BRANCH}"
fi

# Delete tag
if [ -n "$SAFETY_TAG" ]; then
    git tag -d "${SAFETY_TAG}"
    echo "✅ Deleted tag: ${SAFETY_TAG}"
fi

# Delete directory
EXPERIMENT_DIR="experiments/${EXPERIMENT_NAME}"
if [ -d "$EXPERIMENT_DIR" ]; then
    rm -rf "$EXPERIMENT_DIR"
    echo "✅ Deleted directory: ${EXPERIMENT_DIR}/"
fi

echo ""
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "✅ Full Reset Complete"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo ""
echo "You're back on main with clean state"
echo "Experiment '${EXPERIMENT_NAME}' fully removed"
