#!/usr/bin/env python3
"""
Command hook integration for automatic memory tracking.

This module integrates memory tracking hooks into the slash command execution
flow. Commands are automatically wrapped with memory tracking without requiring
any changes to agent code.

Usage:
    from multiagent.core.command_hooks import install_hooks

    install_hooks()  # Installs memory tracking for all commands
"""

import sys
from typing import Callable, Dict, Any, Optional
from functools import wraps

try:
    from .memory_manager import get_memory_manager
    from .command_wrapper import COMMAND_HOOKS
except ImportError:
    # Fallback for standalone execution
    from memory_manager import get_memory_manager
    from command_wrapper import COMMAND_HOOKS


class CommandHookRegistry:
    """
    Central registry for command hooks.

    Manages pre-command and post-command hooks for automatic memory tracking.
    """

    def __init__(self):
        self._pre_hooks: Dict[str, Callable] = {}
        self._post_hooks: Dict[str, Callable] = {}
        self._active_sessions: Dict[str, Dict[str, Any]] = {}

    def register_pre_hook(self, command: str, hook: Callable) -> None:
        """
        Register a pre-command hook.

        Args:
            command: Command name (e.g., "/deployment:deploy-prepare")
            hook: Function to call before command execution
        """
        self._pre_hooks[command] = hook

    def register_post_hook(self, command: str, hook: Callable) -> None:
        """
        Register a post-command hook.

        Args:
            command: Command name
            hook: Function to call after command execution
        """
        self._post_hooks[command] = hook

    def execute_pre_hooks(self, command: str, *args, **kwargs) -> None:
        """
        Execute pre-command hooks.

        Args:
            command: Command being executed
            *args: Command arguments
            **kwargs: Command keyword arguments
        """
        if command in self._pre_hooks:
            try:
                self._pre_hooks[command](*args, **kwargs)
            except Exception as e:
                print(f"Warning: Pre-hook for {command} failed: {e}", file=sys.stderr)

    def execute_post_hooks(
        self,
        command: str,
        result: Any = None,
        error: Optional[Exception] = None
    ) -> None:
        """
        Execute post-command hooks.

        Args:
            command: Command that was executed
            result: Result from command execution
            error: Exception if command failed
        """
        if command in self._post_hooks:
            try:
                self._post_hooks[command](result=result, error=error)
            except Exception as e:
                print(f"Warning: Post-hook for {command} failed: {e}", file=sys.stderr)


# Global hook registry
_hook_registry = CommandHookRegistry()


def create_memory_pre_hook(subsystem: str, context_extractor: Callable) -> Callable:
    """
    Create a pre-command hook for memory tracking.

    Args:
        subsystem: Subsystem name (deployment, testing, etc.)
        context_extractor: Function to extract context from arguments

    Returns:
        Pre-hook function
    """
    def pre_hook(*args, **kwargs):
        from datetime import datetime

        # Get memory manager
        memory = get_memory_manager(subsystem)

        # Generate session ID
        timestamp = datetime.now().strftime("%Y%m%d-%H%M%S")
        session_id = f"{subsystem}-{timestamp}"

        # Extract context
        try:
            context = context_extractor(*args, **kwargs)
        except Exception as e:
            context = {
                "error_extracting_context": str(e),
                "args": args,
                "kwargs": kwargs
            }

        # Start session
        memory.start_session(session_id, context)

        # Store session info for post-hook
        _hook_registry._active_sessions[subsystem] = {
            "session_id": session_id,
            "memory": memory
        }

    return pre_hook


def create_memory_post_hook(subsystem: str) -> Callable:
    """
    Create a post-command hook for memory tracking.

    Args:
        subsystem: Subsystem name

    Returns:
        Post-hook function
    """
    def post_hook(result: Any = None, error: Optional[Exception] = None):
        # Get active session
        session_info = _hook_registry._active_sessions.get(subsystem)

        if not session_info:
            print(f"Warning: No active session for {subsystem}", file=sys.stderr)
            return

        memory = session_info["memory"]

        # Prepare result data
        if error:
            result_data = {
                "error": str(error),
                "error_type": type(error).__name__,
                "success": False
            }
            success = False
        else:
            result_data = result or {}
            success = True

        # End session
        try:
            memory.end_session(result_data, success=success)
        finally:
            # Clean up active session
            _hook_registry._active_sessions.pop(subsystem, None)

    return post_hook


def install_memory_hooks() -> None:
    """
    Install memory tracking hooks for all registered commands.

    This should be called during framework initialization.
    """
    for command, config in COMMAND_HOOKS.items():
        subsystem = config["subsystem"]
        context_extractor = config["context_extractor"]

        # Create and register hooks
        pre_hook = create_memory_pre_hook(subsystem, context_extractor)
        post_hook = create_memory_post_hook(subsystem)

        _hook_registry.register_pre_hook(command, pre_hook)
        _hook_registry.register_post_hook(command, post_hook)


def wrap_command(command: str) -> Callable:
    """
    Wrap a command function with automatic memory tracking.

    Args:
        command: Command name (e.g., "/deployment:deploy-prepare")

    Returns:
        Decorator function

    Example:
        @wrap_command("/deployment:deploy-prepare")
        def deploy_prepare(spec_dir):
            # Command logic
            return {"files": 10}
    """
    def decorator(func: Callable) -> Callable:
        @wraps(func)
        def wrapper(*args, **kwargs):
            # Execute pre-hooks
            _hook_registry.execute_pre_hooks(command, *args, **kwargs)

            result = None
            error = None

            try:
                # Execute command
                result = func(*args, **kwargs)
                return result
            except Exception as e:
                error = e
                raise
            finally:
                # Execute post-hooks (always runs)
                _hook_registry.execute_post_hooks(command, result=result, error=error)

        return wrapper
    return decorator


def get_hook_registry() -> CommandHookRegistry:
    """
    Get the global hook registry.

    Returns:
        CommandHookRegistry instance
    """
    return _hook_registry


if __name__ == "__main__":
    # Example usage
    print("Command Hooks - Example Usage")
    print("=" * 50)

    # Install hooks
    install_memory_hooks()

    # Show registered hooks
    registry = get_hook_registry()
    print(f"\nRegistered pre-hooks: {len(registry._pre_hooks)}")
    print(f"Registered post-hooks: {len(registry._post_hooks)}")

    # Example of wrapping a command
    @wrap_command("/deployment:deploy-prepare")
    def example_deploy(spec_dir):
        print(f"Deploying {spec_dir}...")
        return {"files_generated": 10, "stack": "fastapi"}

    # Execute (hooks run automatically)
    print("\nExecuting example command...")
    result = example_deploy("specs/002-system-context-we")
    print(f"Result: {result}")

    # Check memory was created
    from .memory_manager import get_memory_manager
    memory = get_memory_manager("deployment")
    sessions = memory.search_sessions(limit=1)

    if sessions:
        print(f"\nMemory tracking confirmed:")
        print(f"  Session: {sessions[0]['session_id']}")
        print(f"  Status: {sessions[0]['status']}")
        print(f"  Duration: {sessions[0]['duration_seconds']}s")
