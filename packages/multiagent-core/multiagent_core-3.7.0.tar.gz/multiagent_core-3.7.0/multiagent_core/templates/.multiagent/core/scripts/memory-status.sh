#!/usr/bin/env bash
#
# Memory Status Command
#
# Shows memory usage statistics across all subsystems.
#
# Usage:
#   /memory:status [subsystem]
#   /memory:status deployment
#   /memory:status all --json
#

set -e

# Get script directory
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
REPO_ROOT="$(cd "$SCRIPT_DIR/../../.." && pwd)"

# Parse arguments
SUBSYSTEM="all"
JSON_MODE=false

while [[ $# -gt 0 ]]; do
    case $1 in
        --json)
            JSON_MODE=true
            shift
            ;;
        *)
            SUBSYSTEM="$1"
            shift
            ;;
    esac
done

echo "=== Memory Status ==="
echo "Subsystem: $SUBSYSTEM"
echo ""

# Python status script
python3 <<'EOF'
import sys
import json
import os

# Add multiagent core to path
sys.path.insert(0, os.path.join(os.environ['REPO_ROOT'], '.multiagent'))

from core.memory_manager import get_memory_manager, get_all_subsystem_stats

subsystem = os.environ.get('SUBSYSTEM', 'all')
json_mode = os.environ.get('JSON_MODE', 'false') == 'true'

if subsystem == 'all':
    stats = get_all_subsystem_stats()
else:
    memory = get_memory_manager(subsystem)
    stats = {subsystem: memory.get_stats()}

if json_mode:
    print(json.dumps(stats, indent=2))
else:
    # Human-readable output
    print("📊 **Memory Usage Statistics**\n")

    for sub, stat in stats.items():
        if sub == '_totals':
            continue

        if 'error' in stat:
            print(f"❌ {sub}: {stat['error']}")
            continue

        active = stat.get('active_sessions', 0)
        archived = stat.get('archived_sessions', 0)
        total = stat.get('total_sessions', 0)
        size_mb = stat.get('total_size_mb', 0)

        # Status indicator
        if active == 0 and archived == 0:
            indicator = '⚪'
        elif active > 10:
            indicator = '🔴'  # High usage
        elif active > 5:
            indicator = '🟡'  # Medium usage
        else:
            indicator = '🟢'  # Normal usage

        print(f"{indicator} **{sub}**")
        print(f"   Active: {active} sessions")
        print(f"   Archived: {archived} sessions")
        print(f"   Total: {total} sessions")
        print(f"   Size: {size_mb} MB")
        print()

    # Show totals if viewing all subsystems
    if '_totals' in stats:
        totals = stats['_totals']
        print("=" * 50)
        print(f"📈 **Overall Totals**")
        print(f"   Active: {totals.get('active_sessions', 0)} sessions")
        print(f"   Archived: {totals.get('archived_sessions', 0)} sessions")
        print(f"   Total Size: {totals.get('total_size_mb', 0)} MB")
        print()

        # Recommendations
        total_active = totals.get('active_sessions', 0)
        if total_active > 50:
            print("⚠️  **Recommendation**: High session count. Consider running /memory:cleanup")
        elif total_active > 100:
            print("🔴 **Action Required**: Very high session count. Run /memory:cleanup immediately")
EOF

echo ""
echo "💡 **Tip**: Use /memory:cleanup to reduce session count"
echo "   Example: /memory:cleanup all --keep 10"
