#!/usr/bin/env bash
#
# Memory Search Command
#
# Searches memory sessions across subsystems with filtering support.
#
# Usage:
#   /memory:search [query]
#   /memory:search deployment --spec "002-*" --status success
#   /memory:search testing --limit 5
#

set -e

# Get script directory
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
REPO_ROOT="$(cd "$SCRIPT_DIR/../../.." && pwd)"

# Parse arguments
SUBSYSTEM=""
QUERY=""
SPEC_FILTER=""
STATUS_FILTER=""
LIMIT=10
JSON_MODE=false

while [[ $# -gt 0 ]]; do
    case $1 in
        --spec)
            SPEC_FILTER="$2"
            shift 2
            ;;
        --status)
            STATUS_FILTER="$2"
            shift 2
            ;;
        --limit)
            LIMIT="$2"
            shift 2
            ;;
        --json)
            JSON_MODE=true
            shift
            ;;
        *)
            if [[ -z "$SUBSYSTEM" ]]; then
                SUBSYSTEM="$1"
            else
                QUERY="$QUERY $1"
            fi
            shift
            ;;
    esac
done

# If no subsystem specified, search all
if [[ -z "$SUBSYSTEM" ]]; then
    SUBSYSTEM="all"
fi

echo "=== Memory Search ==="
echo "Subsystem: $SUBSYSTEM"
echo "Limit: $LIMIT"
[[ -n "$SPEC_FILTER" ]] && echo "Spec Filter: $SPEC_FILTER"
[[ -n "$STATUS_FILTER" ]] && echo "Status Filter: $STATUS_FILTER"
echo ""

# Python search script
python3 <<'EOF'
import sys
import json
from pathlib import Path
import fnmatch
import os

# Add multiagent core to path
sys.path.insert(0, os.path.join(os.environ['REPO_ROOT'], '.multiagent'))

from core.memory_manager import get_memory_manager, get_all_subsystem_stats

subsystem = os.environ.get('SUBSYSTEM', 'all')
spec_filter = os.environ.get('SPEC_FILTER', '')
status_filter = os.environ.get('STATUS_FILTER', '')
limit = int(os.environ.get('LIMIT', '10'))
json_mode = os.environ.get('JSON_MODE', 'false') == 'true'

results = []

# Search across subsystems
if subsystem == 'all':
    subsystems = ['deployment', 'testing', 'documentation', 'iterate', 'supervisor', 'github', 'security']
else:
    subsystems = [subsystem]

for sub in subsystems:
    try:
        memory = get_memory_manager(sub)

        # Build filters
        filters = {}
        if spec_filter:
            filters['context__spec_dir'] = spec_filter
        if status_filter:
            filters['status'] = status_filter

        # Search
        sessions = memory.search_sessions(
            active_only=True,
            limit=limit,
            **filters
        )

        for session in sessions:
            session['_subsystem'] = sub
            results.append(session)

    except Exception as e:
        if json_mode:
            print(json.dumps({"error": str(e), "subsystem": sub}), file=sys.stderr)

# Sort by timestamp (newest first)
results.sort(key=lambda x: x.get('start_time', ''), reverse=True)

# Limit total results
results = results[:limit]

if json_mode:
    print(json.dumps(results, indent=2))
else:
    if not results:
        print("No matching sessions found.")
    else:
        print(f"Found {len(results)} session(s):\n")

        for i, session in enumerate(results, 1):
            subsys = session.get('_subsystem', 'unknown')
            session_id = session.get('session_id', 'unknown')
            status = session.get('status', 'unknown')
            duration = session.get('duration_seconds', 0)
            context = session.get('context', {})

            # Status emoji
            status_emoji = '✅' if status == 'success' else '❌' if status == 'failed' else '⏳'

            print(f"{i}. {status_emoji} [{subsys}] {session_id}")
            print(f"   Status: {status} | Duration: {duration:.2f}s")

            # Show context
            if 'spec_dir' in context:
                print(f"   Spec: {context['spec_dir']}")
            if 'command' in context:
                print(f"   Command: {context['command']}")

            # Show result summary
            result = session.get('result', {})
            if result:
                if 'files_generated' in result:
                    print(f"   Files: {result['files_generated']}")
                if 'error' in result:
                    print(f"   Error: {result['error'][:80]}...")

            print()
EOF

echo ""
echo "💡 **Tip**: Use --spec, --status, and --limit to refine searches"
echo "   Example: /memory:search deployment --spec \"002-*\" --status success --limit 5"
