#!/usr/bin/env python3
"""
Automatic memory tracking for multiagent subsystems.

This module provides centralized, automatic memory tracking for all subsystems
without requiring agents to manually manage memory files.

Usage:
    from multiagent.core import get_memory_manager

    memory = get_memory_manager("deployment")
    memory.start_session("deploy-001", {"spec": "specs/002"})
    # ... work happens ...
    memory.end_session({"files": 10}, success=True)
"""

import json
import os
import shutil
from datetime import datetime
from pathlib import Path
from typing import Dict, Any, Optional, List
import fnmatch


class MemoryManager:
    """
    Centralized memory tracking for subsystems.

    Automatically tracks sessions, manages cleanup, and provides search.
    """

    def __init__(self, subsystem: str, base_dir: str = ".multiagent"):
        """
        Initialize memory manager for a subsystem.

        Args:
            subsystem: Name of subsystem (deployment, testing, etc.)
            base_dir: Base directory for multiagent structure
        """
        self.subsystem = subsystem
        self.base_dir = Path(base_dir)
        self.memory_dir = self.base_dir / subsystem / "memory"

        # Ensure directory exists
        self.memory_dir.mkdir(parents=True, exist_ok=True)

        # Archive directory for old sessions
        self.archive_dir = self.memory_dir / "archive"
        self.archive_dir.mkdir(exist_ok=True)

        # Session tracking
        self.current_session: Optional[Dict[str, Any]] = None
        self.session_start: Optional[datetime] = None

    def start_session(self, session_id: str, context: Dict[str, Any]) -> None:
        """
        Begin tracking a new session.

        Called automatically by pre-command hook.

        Args:
            session_id: Unique identifier for session
            context: Context data (spec_dir, command, etc.)
        """
        self.current_session = {
            "session_id": session_id,
            "subsystem": self.subsystem,
            "start_time": datetime.now().isoformat(),
            "context": context,
            "status": "running"
        }
        self.session_start = datetime.now()

    def update_session(self, **kwargs) -> None:
        """
        Update session with intermediate data.

        Called during command execution if needed.

        Args:
            **kwargs: Additional data to add to session
        """
        if self.current_session:
            self.current_session.update(kwargs)

    def end_session(self, result: Dict[str, Any], success: bool = True) -> str:
        """
        Finish session and write memory file.

        Called automatically by post-command hook.

        Args:
            result: Result data from command execution
            success: Whether command succeeded

        Returns:
            Path to written memory file
        """
        if not self.current_session:
            raise RuntimeError("No active session to end")

        # Calculate duration
        duration = (datetime.now() - self.session_start).total_seconds()

        # Finalize session data
        self.current_session.update({
            "end_time": datetime.now().isoformat(),
            "duration_seconds": duration,
            "status": "success" if success else "failed",
            "result": result
        })

        # Write memory file
        filename = f"{self.current_session['session_id']}.json"
        filepath = self.memory_dir / filename

        with open(filepath, 'w') as f:
            json.dump(self.current_session, f, indent=2)

        # Cleanup old sessions
        self._cleanup_old_sessions()

        # Reset
        session_path = str(filepath)
        self.current_session = None
        self.session_start = None

        return session_path

    def _cleanup_old_sessions(self, keep_last: int = 10) -> None:
        """
        Keep only the last N sessions per subsystem.

        Archives older sessions automatically to memory/archive/.

        Args:
            keep_last: Number of recent sessions to keep active
        """
        # Get all session files sorted by modification time (newest first)
        session_files = sorted(
            [f for f in self.memory_dir.glob("*.json") if f.is_file()],
            key=lambda p: p.stat().st_mtime,
            reverse=True
        )

        # Archive files beyond keep_last
        for old_file in session_files[keep_last:]:
            archive_path = self.archive_dir / old_file.name
            shutil.move(str(old_file), str(archive_path))

    def search_sessions(
        self,
        active_only: bool = True,
        limit: Optional[int] = None,
        **filters
    ) -> List[Dict[str, Any]]:
        """
        Search memory files by filters.

        Args:
            active_only: Search only active sessions (not archived)
            limit: Maximum number of results
            **filters: Key-value pairs to filter by

        Examples:
            # Find successful deployments
            search_sessions(status="success")

            # Find sessions for specific spec
            search_sessions(context__spec_dir="specs/002-*")

            # Get last 5 sessions
            search_sessions(limit=5)

        Returns:
            List of matching session dictionaries
        """
        results = []

        # Determine which directory to search
        search_dir = self.memory_dir if active_only else self.memory_dir.parent

        # Find all session files
        if active_only:
            session_files = list(self.memory_dir.glob("*.json"))
        else:
            session_files = (
                list(self.memory_dir.glob("*.json")) +
                list(self.archive_dir.glob("*.json"))
            )

        # Sort by modification time (newest first)
        session_files.sort(key=lambda p: p.stat().st_mtime, reverse=True)

        for session_file in session_files:
            try:
                with open(session_file) as f:
                    session = json.load(f)

                # Apply filters
                if self._matches_filters(session, filters):
                    results.append(session)

                    # Check limit
                    if limit and len(results) >= limit:
                        break

            except (json.JSONDecodeError, IOError):
                # Skip corrupted files
                continue

        return results

    def _matches_filters(self, session: Dict[str, Any], filters: Dict[str, Any]) -> bool:
        """
        Check if session matches all filters.

        Supports nested key access with __ notation (context__spec_dir).
        Supports glob patterns for string values.

        Args:
            session: Session data to check
            filters: Filter criteria

        Returns:
            True if session matches all filters
        """
        for key, value in filters.items():
            # Handle nested keys (context__spec_dir)
            if "__" in key:
                parts = key.split("__")
                current = session

                try:
                    for part in parts:
                        current = current[part]
                except (KeyError, TypeError):
                    return False

                # Check value
                if isinstance(value, str) and "*" in value:
                    # Glob pattern matching
                    if not fnmatch.fnmatch(str(current), value):
                        return False
                elif current != value:
                    return False
            else:
                # Simple key lookup
                if key not in session:
                    return False

                session_value = session[key]

                # Glob pattern matching for strings
                if isinstance(value, str) and "*" in value:
                    if not fnmatch.fnmatch(str(session_value), value):
                        return False
                elif session_value != value:
                    return False

        return True

    def get_stats(self) -> Dict[str, Any]:
        """
        Get statistics about memory usage.

        Returns:
            Dictionary with active/archived counts and sizes
        """
        # Count active sessions
        active_files = list(self.memory_dir.glob("*.json"))
        active_count = len(active_files)
        active_size = sum(f.stat().st_size for f in active_files)

        # Count archived sessions
        archived_files = list(self.archive_dir.glob("*.json"))
        archived_count = len(archived_files)
        archived_size = sum(f.stat().st_size for f in archived_files)

        return {
            "subsystem": self.subsystem,
            "active_sessions": active_count,
            "archived_sessions": archived_count,
            "total_sessions": active_count + archived_count,
            "active_size_bytes": active_size,
            "archived_size_bytes": archived_size,
            "total_size_bytes": active_size + archived_size,
            "active_size_mb": round(active_size / 1024 / 1024, 2),
            "archived_size_mb": round(archived_size / 1024 / 1024, 2),
            "total_size_mb": round((active_size + archived_size) / 1024 / 1024, 2)
        }

    def cleanup_archive(self, days_old: int = 90) -> int:
        """
        Delete archived sessions older than specified days.

        Args:
            days_old: Delete archives older than this many days

        Returns:
            Number of files deleted
        """
        import time

        deleted = 0
        cutoff = time.time() - (days_old * 24 * 60 * 60)

        for archive_file in self.archive_dir.glob("*.json"):
            if archive_file.stat().st_mtime < cutoff:
                archive_file.unlink()
                deleted += 1

        return deleted

    def export_sessions(
        self,
        output_path: str,
        include_archived: bool = False
    ) -> None:
        """
        Export sessions to a single JSON file.

        Args:
            output_path: Path to write export file
            include_archived: Include archived sessions in export
        """
        sessions = self.search_sessions(
            active_only=not include_archived,
            limit=None
        )

        export_data = {
            "subsystem": self.subsystem,
            "export_time": datetime.now().isoformat(),
            "session_count": len(sessions),
            "sessions": sessions
        }

        with open(output_path, 'w') as f:
            json.dump(export_data, f, indent=2)


# Global memory managers for each subsystem
_memory_managers: Dict[str, MemoryManager] = {}


def get_memory_manager(subsystem: str, base_dir: str = ".multiagent") -> MemoryManager:
    """
    Get or create memory manager for subsystem.

    Args:
        subsystem: Name of subsystem (deployment, testing, etc.)
        base_dir: Base directory for multiagent structure

    Returns:
        MemoryManager instance for subsystem
    """
    key = f"{subsystem}:{base_dir}"

    if key not in _memory_managers:
        _memory_managers[key] = MemoryManager(subsystem, base_dir)

    return _memory_managers[key]


def get_all_subsystem_stats(base_dir: str = ".multiagent") -> Dict[str, Any]:
    """
    Get memory statistics for all subsystems.

    Args:
        base_dir: Base directory for multiagent structure

    Returns:
        Dictionary with stats for each subsystem
    """
    base_path = Path(base_dir)

    if not base_path.exists():
        return {}

    stats = {}

    # Find all subsystems with memory directories
    for subsystem_dir in base_path.iterdir():
        if not subsystem_dir.is_dir():
            continue

        memory_dir = subsystem_dir / "memory"
        if memory_dir.exists():
            subsystem = subsystem_dir.name
            memory = get_memory_manager(subsystem, base_dir)
            stats[subsystem] = memory.get_stats()

    # Calculate totals
    if stats:
        stats["_totals"] = {
            "active_sessions": sum(s["active_sessions"] for s in stats.values() if isinstance(s, dict)),
            "archived_sessions": sum(s["archived_sessions"] for s in stats.values() if isinstance(s, dict)),
            "total_size_mb": round(sum(s["total_size_mb"] for s in stats.values() if isinstance(s, dict)), 2)
        }

    return stats


if __name__ == "__main__":
    # Example usage
    print("Memory Manager - Example Usage")
    print("=" * 50)

    # Create memory manager
    memory = get_memory_manager("deployment")

    # Start session
    memory.start_session(
        "deploy-test-001",
        {"spec_dir": "specs/002-test", "command": "deploy-prepare"}
    )

    # End session
    memory.end_session(
        {"files_generated": 10, "stack": "fastapi"},
        success=True
    )

    # Search sessions
    results = memory.search_sessions(limit=5)
    print(f"\nFound {len(results)} recent sessions")

    # Get stats
    stats = memory.get_stats()
    print(f"\nMemory Stats:")
    print(f"  Active: {stats['active_sessions']}")
    print(f"  Archived: {stats['archived_sessions']}")
    print(f"  Total Size: {stats['total_size_mb']} MB")
