#!/bin/bash
# Start a new experiment with safety tag and tracking

set -e

EXPERIMENT_NAME="$1"

if [ -z "$EXPERIMENT_NAME" ]; then
    echo "❌ Error: Experiment name required"
    echo "Usage: /experiment:start <name>"
    exit 1
fi

# Validate we're in a git repository
if ! git rev-parse --git-dir > /dev/null 2>&1; then
    echo "❌ Error: Not a git repository"
    exit 1
fi

# Check for uncommitted changes
if ! git diff-index --quiet HEAD -- 2>/dev/null; then
    echo "⚠️  Warning: You have uncommitted changes"
    echo ""
    git status --short
    echo ""
    read -p "Continue anyway? [y/N] " -n 1 -r
    echo
    if [[ ! $REPLY =~ ^[Yy]$ ]]; then
        echo "Cancelled. Commit or stash your changes first."
        exit 1
    fi
fi

# Get current state
CURRENT_BRANCH=$(git branch --show-current)
CURRENT_COMMIT=$(git rev-parse --short HEAD)
TIMESTAMP=$(date +%Y%m%d-%H%M%S)
SAFETY_TAG="pre-experiment/${EXPERIMENT_NAME}-${TIMESTAMP}"
EXPERIMENT_BRANCH="experiment/${EXPERIMENT_NAME}"

echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "🧪 Starting Experiment: ${EXPERIMENT_NAME}"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo ""

# 1. Create safety tag on current commit
echo "📍 Creating safety tag: ${SAFETY_TAG}"
git tag -a "${SAFETY_TAG}" -m "Safety snapshot before experiment: ${EXPERIMENT_NAME}"
echo "✅ Safety tag created at ${CURRENT_COMMIT}"
echo ""

# 2. Create and checkout experiment branch
echo "🌿 Creating experiment branch: ${EXPERIMENT_BRANCH}"
git checkout -b "${EXPERIMENT_BRANCH}"
echo "✅ Switched to ${EXPERIMENT_BRANCH}"
echo ""

# 3. Create experiment directory
EXPERIMENT_DIR="experiments/${EXPERIMENT_NAME}"
mkdir -p "${EXPERIMENT_DIR}"
echo "📁 Created: ${EXPERIMENT_DIR}/"
echo ""

# 4. Generate EXPERIMENT_LOG.md from template
TEMPLATE_PATH="$HOME/.multiagent/experiment/templates/EXPERIMENT_LOG.md"
LOG_PATH="${EXPERIMENT_DIR}/EXPERIMENT_LOG.md"

if [ -f "${TEMPLATE_PATH}" ]; then
    # Replace placeholders
    sed -e "s/{{EXPERIMENT_NAME}}/${EXPERIMENT_NAME}/g" \
        -e "s/{{DATE}}/$(date +%Y-%m-%d)/g" \
        -e "s/{{SAFETY_TAG}}/${SAFETY_TAG}/g" \
        -e "s/{{CURRENT_BRANCH}}/${CURRENT_BRANCH}/g" \
        -e "s/{{CURRENT_COMMIT}}/${CURRENT_COMMIT}/g" \
        -e "s/{{HAS_UNCOMMITTED}}/$(if git diff-index --quiet HEAD --; then echo 'No'; else echo 'Yes'; fi)/g" \
        -e "s/{{HYPOTHESIS}}/[Document your hypothesis here]/g" \
        -e "s/{{LEARNINGS}}/[Will document as you progress]/g" \
        -e "s/{{NEXT_STEPS}}/[Will determine based on results]/g" \
        "${TEMPLATE_PATH}" > "${LOG_PATH}"

    echo "📝 Created: ${LOG_PATH}"
else
    echo "⚠️  Warning: Template not found, creating basic log"
    cat > "${LOG_PATH}" <<EOF
# Experiment: ${EXPERIMENT_NAME}

**Started:** $(date +%Y-%m-%d)
**Branch:** ${EXPERIMENT_BRANCH}
**Safety Tag:** ${SAFETY_TAG}

## Progress

Document your experiment progress here.
EOF
fi

# 5. Create initial commit
git add "${EXPERIMENT_DIR}/"
git commit -m "[EXPERIMENT] Start: ${EXPERIMENT_NAME}

Safety tag: ${SAFETY_TAG}
Branched from: ${CURRENT_BRANCH} @ ${CURRENT_COMMIT}

🤖 Generated with [Claude Code](https://claude.com/claude-code)

Co-Authored-By: Claude <noreply@anthropic.com>"

echo ""
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "✅ Experiment Started Successfully"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo ""
echo "📍 Rollback point: ${SAFETY_TAG}"
echo "🌿 Working branch: ${EXPERIMENT_BRANCH}"
echo "📝 Experiment log: ${LOG_PATH}"
echo ""
echo "Next steps:"
echo "  1. Edit ${LOG_PATH} with your hypothesis"
echo "  2. Make changes and commit to this branch"
echo "  3. When done: /experiment:archive or /experiment:integrate"
echo "  4. If needed: /experiment:rollback"
echo ""
echo "🔒 Safe to experiment - you can always rollback!"
