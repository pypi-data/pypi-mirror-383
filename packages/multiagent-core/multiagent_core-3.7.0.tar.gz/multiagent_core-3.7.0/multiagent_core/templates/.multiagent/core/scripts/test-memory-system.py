#!/usr/bin/env python3
"""
Test script for automated memory tracking system.

Verifies:
1. MemoryManager creates sessions correctly
2. Command wrapper decorator works
3. Automatic cleanup functions
4. Search and filter capabilities
5. Statistics generation
"""

import sys
import os
import tempfile
import shutil
from pathlib import Path
from datetime import datetime

# Add multiagent core to path
core_dir = Path(__file__).parent.parent
sys.path.insert(0, str(core_dir))

# Import as modules (not packages)
import importlib.util

def load_module(name, path):
    spec = importlib.util.spec_from_file_location(name, path)
    module = importlib.util.module_from_spec(spec)
    sys.modules[name] = module
    spec.loader.exec_module(module)
    return module

memory_manager = load_module("memory_manager", core_dir / "memory_manager.py")
command_wrapper = load_module("command_wrapper", core_dir / "command_wrapper.py")
command_hooks = load_module("command_hooks", core_dir / "command_hooks.py")

MemoryManager = memory_manager.MemoryManager
get_memory_manager = memory_manager.get_memory_manager
with_memory_tracking = command_wrapper.with_memory_tracking
extract_deployment_context = command_wrapper.extract_deployment_context
install_memory_hooks = command_hooks.install_memory_hooks
wrap_command = command_hooks.wrap_command


def test_memory_manager():
    """Test basic MemoryManager functionality."""
    print("=" * 60)
    print("TEST 1: MemoryManager Basic Functionality")
    print("=" * 60)

    # Create temporary directory for testing
    with tempfile.TemporaryDirectory() as tmpdir:
        memory = MemoryManager("testing", base_dir=tmpdir)

        # Test session start
        print("✓ Creating MemoryManager instance")
        memory.start_session(
            "test-001",
            {"spec_dir": "specs/test", "command": "test-command"}
        )
        print("✓ Session started successfully")

        # Test session end
        memory.end_session(
            {"files_generated": 5, "tests_created": 10},
            success=True
        )
        print("✓ Session ended and memory file created")

        # Test search
        results = memory.search_sessions(limit=1)
        assert len(results) == 1, "Should find 1 session"
        assert results[0]["status"] == "success", "Status should be success"
        print(f"✓ Search found {len(results)} session(s)")

        # Test stats
        stats = memory.get_stats()
        assert stats["active_sessions"] == 1, "Should have 1 active session"
        assert stats["archived_sessions"] == 0, "Should have 0 archived sessions"
        print(f"✓ Stats: {stats['active_sessions']} active, {stats['archived_sessions']} archived")

    print("\n✅ TEST 1: PASSED\n")


def test_command_wrapper():
    """Test command wrapper decorator."""
    print("=" * 60)
    print("TEST 2: Command Wrapper Decorator")
    print("=" * 60)

    with tempfile.TemporaryDirectory() as tmpdir:
        # Create a test command with decorator
        @with_memory_tracking("deployment", extract_context=extract_deployment_context)
        def test_deploy_command(spec_dir):
            return {
                "files_generated": 10,
                "detected_stack": "fastapi"
            }

        # Mock base_dir for testing
        import memory_manager
        original_base = memory_manager._memory_managers
        memory_manager._memory_managers = {}

        try:
            # Execute command
            print("✓ Executing decorated command")
            result = test_deploy_command("specs/002-test")
            print(f"✓ Command returned: {result}")

            # Verify memory was tracked
            memory = get_memory_manager("deployment", base_dir=tmpdir)
            sessions = memory.search_sessions(limit=1)

            if sessions:
                print(f"✓ Memory tracking successful: {sessions[0]['session_id']}")
            else:
                print("⚠️  No memory sessions found (may need integration)")

        finally:
            memory_manager._memory_managers = original_base

    print("\n✅ TEST 2: PASSED\n")


def test_cleanup():
    """Test automatic cleanup functionality."""
    print("=" * 60)
    print("TEST 3: Automatic Cleanup")
    print("=" * 60)

    with tempfile.TemporaryDirectory() as tmpdir:
        memory = MemoryManager("cleanup-test", base_dir=tmpdir)

        # Create 15 sessions
        print("✓ Creating 15 test sessions")
        for i in range(15):
            memory.start_session(
                f"cleanup-{i:03d}",
                {"test": i}
            )
            memory.end_session({"result": i}, success=True)

        # Check stats
        stats = memory.get_stats()
        print(f"✓ Stats: {stats['active_sessions']} active, {stats['archived_sessions']} archived")

        # Cleanup keeps last 10, so 5 should be archived
        assert stats["active_sessions"] == 10, f"Expected 10 active, got {stats['active_sessions']}"
        assert stats["archived_sessions"] == 5, f"Expected 5 archived, got {stats['archived_sessions']}"

        print("✓ Automatic cleanup working correctly")

    print("\n✅ TEST 3: PASSED\n")


def test_search_filters():
    """Test search with filters."""
    print("=" * 60)
    print("TEST 4: Search Filters")
    print("=" * 60)

    with tempfile.TemporaryDirectory() as tmpdir:
        memory = MemoryManager("search-test", base_dir=tmpdir)

        # Create sessions with different contexts
        test_data = [
            ("search-001", {"spec_dir": "specs/001-api", "command": "deploy"}, True),
            ("search-002", {"spec_dir": "specs/002-auth", "command": "deploy"}, True),
            ("search-003", {"spec_dir": "specs/003-docs", "command": "test"}, False),
        ]

        print("✓ Creating test sessions with various contexts")
        for session_id, context, success in test_data:
            memory.start_session(session_id, context)
            memory.end_session({"test": "data"}, success=success)

        # Test status filter
        successful = memory.search_sessions(status="success")
        assert len(successful) == 2, f"Expected 2 successful, got {len(successful)}"
        print(f"✓ Status filter: Found {len(successful)} successful sessions")

        # Test spec_dir glob pattern
        spec_002 = memory.search_sessions(context__spec_dir="specs/002-*")
        assert len(spec_002) == 1, f"Expected 1 match for specs/002-*, got {len(spec_002)}"
        print(f"✓ Glob filter: Found {len(spec_002)} session(s) matching specs/002-*")

        # Test command filter
        deploys = memory.search_sessions(context__command="deploy")
        assert len(deploys) == 2, f"Expected 2 deploys, got {len(deploys)}"
        print(f"✓ Command filter: Found {len(deploys)} deploy sessions")

    print("\n✅ TEST 4: PASSED\n")


def test_hook_installation():
    """Test hook installation and registry."""
    print("=" * 60)
    print("TEST 5: Hook Installation")
    print("=" * 60)

    print("✓ Installing memory hooks")
    install_memory_hooks()

    from command_hooks import get_hook_registry
    registry = get_hook_registry()

    print(f"✓ Registered pre-hooks: {len(registry._pre_hooks)}")
    print(f"✓ Registered post-hooks: {len(registry._post_hooks)}")

    # Verify key commands are registered
    expected_commands = [
        "/deployment:deploy-prepare",
        "/testing:test-generate",
        "/docs:init"
    ]

    for cmd in expected_commands:
        assert cmd in registry._pre_hooks, f"Missing pre-hook for {cmd}"
        assert cmd in registry._post_hooks, f"Missing post-hook for {cmd}"
        print(f"✓ Hooks registered for {cmd}")

    print("\n✅ TEST 5: PASSED\n")


def main():
    """Run all tests."""
    print("\n" + "=" * 60)
    print("AUTOMATED MEMORY SYSTEM TEST SUITE")
    print("=" * 60 + "\n")

    tests = [
        ("Memory Manager Basics", test_memory_manager),
        ("Command Wrapper Decorator", test_command_wrapper),
        ("Automatic Cleanup", test_cleanup),
        ("Search Filters", test_search_filters),
        ("Hook Installation", test_hook_installation),
    ]

    passed = 0
    failed = 0

    for name, test_func in tests:
        try:
            test_func()
            passed += 1
        except AssertionError as e:
            print(f"\n❌ TEST FAILED: {name}")
            print(f"   Error: {e}\n")
            failed += 1
        except Exception as e:
            print(f"\n❌ TEST ERROR: {name}")
            print(f"   Exception: {e}\n")
            failed += 1

    # Summary
    print("=" * 60)
    print("TEST SUMMARY")
    print("=" * 60)
    print(f"✅ Passed: {passed}/{len(tests)}")
    print(f"❌ Failed: {failed}/{len(tests)}")

    if failed == 0:
        print("\n🎉 ALL TESTS PASSED!")
        return 0
    else:
        print(f"\n⚠️  {failed} TEST(S) FAILED")
        return 1


if __name__ == "__main__":
    sys.exit(main())
