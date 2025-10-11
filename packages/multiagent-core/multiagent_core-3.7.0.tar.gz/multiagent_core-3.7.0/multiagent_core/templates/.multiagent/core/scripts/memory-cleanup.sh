#!/usr/bin/env bash
#
# Memory Cleanup Command
#
# Cleans up old memory sessions and archives them.
#
# Usage:
#   /memory:cleanup [subsystem] [options]
#   /memory:cleanup deployment --keep 5
#   /memory:cleanup all --archive-days 90
#   /memory:cleanup testing --dry-run
#

set -e

# Get script directory
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
REPO_ROOT="$(cd "$SCRIPT_DIR/../../.." && pwd)"

# Parse arguments
SUBSYSTEM="all"
KEEP_LAST=10
ARCHIVE_DAYS=90
DRY_RUN=false
JSON_MODE=false

while [[ $# -gt 0 ]]; do
    case $1 in
        --keep)
            KEEP_LAST="$2"
            shift 2
            ;;
        --archive-days)
            ARCHIVE_DAYS="$2"
            shift 2
            ;;
        --dry-run)
            DRY_RUN=true
            shift
            ;;
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

echo "=== Memory Cleanup ==="
echo "Subsystem: $SUBSYSTEM"
echo "Keep Last: $KEEP_LAST sessions"
echo "Archive Days: Delete archives older than $ARCHIVE_DAYS days"
[[ "$DRY_RUN" == "true" ]] && echo "Mode: DRY RUN (no changes will be made)"
echo ""

# Python cleanup script
python3 <<'EOF'
import sys
import json
import os
from pathlib import Path
import shutil

# Add multiagent core to path
sys.path.insert(0, os.path.join(os.environ['REPO_ROOT'], '.multiagent'))

from core.memory_manager import get_memory_manager

subsystem = os.environ.get('SUBSYSTEM', 'all')
keep_last = int(os.environ.get('KEEP_LAST', '10'))
archive_days = int(os.environ.get('ARCHIVE_DAYS', '90'))
dry_run = os.environ.get('DRY_RUN', 'false') == 'true'
json_mode = os.environ.get('JSON_MODE', 'false') == 'true'

results = {}

# Determine subsystems to clean
if subsystem == 'all':
    subsystems = ['deployment', 'testing', 'documentation', 'iterate', 'supervisor', 'github', 'security']
else:
    subsystems = [subsystem]

for sub in subsystems:
    try:
        memory = get_memory_manager(sub)

        # Get stats before cleanup
        before_stats = memory.get_stats()

        if not dry_run:
            # Perform cleanup
            # Note: _cleanup_old_sessions is called automatically by end_session,
            # but we can manually trigger it by simulating a session end

            # Get all session files
            memory_dir = memory.memory_dir
            session_files = sorted(
                [f for f in memory_dir.glob("*.json") if f.is_file()],
                key=lambda p: p.stat().st_mtime,
                reverse=True
            )

            # Archive files beyond keep_last
            archived_count = 0
            for old_file in session_files[keep_last:]:
                archive_path = memory.archive_dir / old_file.name
                shutil.move(str(old_file), str(archive_path))
                archived_count += 1

            # Delete old archives
            deleted_count = memory.cleanup_archive(days_old=archive_days)
        else:
            # Dry run - just count what would be archived/deleted
            memory_dir = memory.memory_dir
            session_files = sorted(
                [f for f in memory_dir.glob("*.json") if f.is_file()],
                key=lambda p: p.stat().st_mtime,
                reverse=True
            )
            archived_count = max(0, len(session_files) - keep_last)

            # Count old archives
            import time
            cutoff = time.time() - (archive_days * 24 * 60 * 60)
            deleted_count = len([
                f for f in memory.archive_dir.glob("*.json")
                if f.stat().st_mtime < cutoff
            ])

        # Get stats after cleanup
        after_stats = memory.get_stats()

        results[sub] = {
            "before": before_stats,
            "after": after_stats,
            "archived": archived_count,
            "deleted": deleted_count,
            "dry_run": dry_run
        }

    except Exception as e:
        results[sub] = {
            "error": str(e)
        }

if json_mode:
    print(json.dumps(results, indent=2))
else:
    total_archived = 0
    total_deleted = 0

    for sub, result in results.items():
        if "error" in result:
            print(f"❌ {sub}: {result['error']}")
            continue

        before = result['before']
        after = result['after']
        archived = result['archived']
        deleted = result['deleted']

        total_archived += archived
        total_deleted += deleted

        if archived > 0 or deleted > 0:
            print(f"📦 {sub}:")
            print(f"   Active Sessions: {before['active_sessions']} → {after['active_sessions']}")
            print(f"   Archived: {archived} sessions")
            print(f"   Deleted: {deleted} old archives")
            print(f"   Space: {before['total_size_mb']} MB → {after['total_size_mb']} MB")
            print()

    print(f"✅ Cleanup Summary:")
    print(f"   Total Archived: {total_archived} sessions")
    print(f"   Total Deleted: {total_deleted} old archives")

    if dry_run:
        print(f"\n💡 This was a dry run. Run without --dry-run to perform cleanup.")
EOF

echo ""
echo "💡 **Tip**: Use --dry-run to preview changes before cleanup"
echo "   Example: /memory:cleanup deployment --keep 5 --dry-run"
