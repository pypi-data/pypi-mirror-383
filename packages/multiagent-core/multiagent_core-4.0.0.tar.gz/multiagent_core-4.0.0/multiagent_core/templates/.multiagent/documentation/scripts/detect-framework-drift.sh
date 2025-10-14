#!/bin/bash
# Framework-specific doc drift detection for multiagent-core development
# Called by post-commit hook to detect when framework docs need updating

# Get the last commit changes
CHANGED_FILES=$(git diff HEAD~1 --name-only 2>/dev/null)

# Track if any drift detected
DRIFT_DETECTED=0

echo "🔍 Checking framework documentation drift..."

# Check if framework core changed
if echo "$CHANGED_FILES" | grep -q "multiagent_core/templates/.multiagent/"; then
    echo "⚠️  Framework templates changed"
    echo "   → Consider updating: multiagent_core/templates/.multiagent/README.md"
    DRIFT_DETECTED=1
fi

# Check if CLI changed
if echo "$CHANGED_FILES" | grep -q "multiagent_core/cli.py"; then
    echo "⚠️  CLI commands changed"
    echo "   → Consider updating: README.md (Core Commands section)"
    echo "   → Consider updating: docs/architecture/03-build-system.md"
    DRIFT_DETECTED=1
fi

# Check if architecture docs changed but overview wasn't updated
if echo "$CHANGED_FILES" | grep -q "docs/architecture/" && ! echo "$CHANGED_FILES" | grep -q "docs/architecture/01-overview.md"; then
    echo "⚠️  Architecture docs changed"
    echo "   → Consider updating: docs/architecture/01-overview.md"
    DRIFT_DETECTED=1
fi

# Check if new subsystem added
if echo "$CHANGED_FILES" | grep -q "multiagent_core/templates/.multiagent/[^/]*/README.md"; then
    echo "⚠️  Subsystem README changed"
    echo "   → Consider updating: multiagent_core/templates/.multiagent/README.md (Subsystem Overview)"
    DRIFT_DETECTED=1
fi

# Check if slash command templates added
if echo "$CHANGED_FILES" | grep -q ".claude/commands/" && ! echo "$CHANGED_FILES" | grep -q "multiagent_core/templates/.multiagent/README.md"; then
    echo "⚠️  Slash commands changed"
    echo "   → Consider updating: multiagent_core/templates/.multiagent/README.md"
    DRIFT_DETECTED=1
fi

if [ $DRIFT_DETECTED -eq 1 ]; then
    echo ""
    echo "📝 To review and update docs, run:"
    echo "   /docs:update-check"
    echo ""
else
    echo "✓ No documentation drift detected"
fi

exit 0
