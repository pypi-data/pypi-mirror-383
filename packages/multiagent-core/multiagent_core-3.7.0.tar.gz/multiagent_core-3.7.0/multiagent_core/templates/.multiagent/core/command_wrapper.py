#!/usr/bin/env python3
"""
Command wrapper for automatic memory tracking.

Provides decorators and utilities to wrap slash commands with automatic
memory tracking without requiring agents to manage memory manually.

Usage:
    from multiagent.core.command_wrapper import with_memory_tracking

    @with_memory_tracking("deployment", extract_context=extract_deploy_context)
    def deploy_command(spec_dir):
        # Command logic here
        return {"files": 10}
"""

import sys
from datetime import datetime
from typing import Callable, Any, Dict, Optional
from functools import wraps

try:
    from .memory_manager import get_memory_manager
except ImportError:
    # Fallback for standalone execution
    from memory_manager import get_memory_manager


def with_memory_tracking(
    subsystem: str,
    extract_context: Optional[Callable] = None
):
    """
    Decorator to add automatic memory tracking to commands.

    Args:
        subsystem: Name of subsystem (deployment, testing, etc.)
        extract_context: Optional function to extract context from args

    Returns:
        Decorated function with automatic memory tracking

    Example:
        @with_memory_tracking("deployment", extract_context=extract_deploy_context)
        def deploy_prepare(spec_dir):
            # Generate deployment configs
            return {"files": 10, "stack": "fastapi"}
    """
    def decorator(func: Callable) -> Callable:
        @wraps(func)
        def wrapper(*args, **kwargs):
            # Get memory manager
            memory = get_memory_manager(subsystem)

            # Generate session ID
            timestamp = datetime.now().strftime("%Y%m%d-%H%M%S")
            session_id = f"{subsystem}-{timestamp}"

            # Extract context from arguments
            context = {}
            if extract_context:
                try:
                    context = extract_context(*args, **kwargs)
                except Exception as e:
                    context = {"error_extracting_context": str(e)}
            else:
                # Default context
                context = {
                    "args": args,
                    "kwargs": kwargs
                }

            # Start session tracking
            memory.start_session(session_id, context)

            try:
                # Execute command
                result = func(*args, **kwargs)

                # End session with success
                memory.end_session(result or {}, success=True)

                return result

            except Exception as e:
                # End session with failure
                memory.end_session(
                    {
                        "error": str(e),
                        "error_type": type(e).__name__,
                        "traceback": _get_traceback_string()
                    },
                    success=False
                )
                raise

        return wrapper
    return decorator


def _get_traceback_string() -> str:
    """
    Get current traceback as string.

    Returns:
        Formatted traceback string
    """
    import traceback
    return ''.join(traceback.format_exception(*sys.exc_info()))


# Context extractors for each subsystem

def extract_deployment_context(*args, **kwargs) -> Dict[str, Any]:
    """
    Extract context from deployment command arguments.

    Args:
        *args: Positional arguments
        **kwargs: Keyword arguments

    Returns:
        Context dictionary with spec_dir and command
    """
    spec_dir = args[0] if args else kwargs.get("spec_dir", "unknown")

    # Normalize spec_dir path
    if isinstance(spec_dir, str):
        spec_dir = spec_dir.rstrip("/")

    return {
        "spec_dir": spec_dir,
        "command": kwargs.get("command", "deploy-prepare"),
        "platform": kwargs.get("platform", "unknown")
    }


def extract_testing_context(*args, **kwargs) -> Dict[str, Any]:
    """
    Extract context from testing command arguments.

    Args:
        *args: Positional arguments
        **kwargs: Keyword arguments

    Returns:
        Context dictionary with spec_dir and test type
    """
    spec_dir = args[0] if args else kwargs.get("spec_dir", "unknown")

    # Normalize spec_dir path
    if isinstance(spec_dir, str):
        spec_dir = spec_dir.rstrip("/")

    return {
        "spec_dir": spec_dir,
        "command": kwargs.get("command", "test-generate"),
        "test_type": kwargs.get("test_type", "all")
    }


def extract_docs_context(*args, **kwargs) -> Dict[str, Any]:
    """
    Extract context from docs command arguments.

    Args:
        *args: Positional arguments
        **kwargs: Keyword arguments

    Returns:
        Context dictionary with command and project type
    """
    return {
        "command": kwargs.get("command", "docs-init"),
        "project_type": kwargs.get("project_type", "unknown"),
        "project_root": kwargs.get("project_root", ".")
    }


def extract_iterate_context(*args, **kwargs) -> Dict[str, Any]:
    """
    Extract context from iterate command arguments.

    Args:
        *args: Positional arguments
        **kwargs: Keyword arguments

    Returns:
        Context dictionary with spec_dir and phase
    """
    spec_dir = args[0] if args else kwargs.get("spec_dir", "unknown")

    # Normalize spec_dir path
    if isinstance(spec_dir, str):
        spec_dir = spec_dir.rstrip("/")

    phase = kwargs.get("phase", "unknown")

    return {
        "spec_dir": spec_dir,
        "phase": phase,
        "command": f"iterate-{phase}"
    }


def extract_supervisor_context(*args, **kwargs) -> Dict[str, Any]:
    """
    Extract context from supervisor command arguments.

    Args:
        *args: Positional arguments
        **kwargs: Keyword arguments

    Returns:
        Context dictionary with spec_dir and phase
    """
    spec_dir = args[0] if args else kwargs.get("spec_dir", "unknown")

    # Normalize spec_dir path
    if isinstance(spec_dir, str):
        spec_dir = spec_dir.rstrip("/")

    phase = kwargs.get("phase", "start")

    return {
        "spec_dir": spec_dir,
        "phase": phase,
        "command": f"supervisor-{phase}"
    }


def extract_github_context(*args, **kwargs) -> Dict[str, Any]:
    """
    Extract context from GitHub command arguments.

    Args:
        *args: Positional arguments
        **kwargs: Keyword arguments

    Returns:
        Context dictionary with PR/issue number
    """
    pr_number = kwargs.get("pr_number") or kwargs.get("pr")
    issue_number = kwargs.get("issue_number") or kwargs.get("issue")

    context = {
        "command": kwargs.get("command", "unknown")
    }

    if pr_number:
        context["pr_number"] = pr_number
    if issue_number:
        context["issue_number"] = issue_number

    return context


def extract_security_context(*args, **kwargs) -> Dict[str, Any]:
    """
    Extract context from security command arguments.

    Args:
        *args: Positional arguments
        **kwargs: Keyword arguments

    Returns:
        Context dictionary with scan type
    """
    return {
        "command": kwargs.get("command", "security-scan"),
        "scan_type": kwargs.get("scan_type", "full"),
        "target": args[0] if args else kwargs.get("target", ".")
    }


# Command hook registry
COMMAND_HOOKS = {
    # Deployment commands
    "/deployment:deploy-prepare": {
        "subsystem": "deployment",
        "context_extractor": extract_deployment_context
    },
    "/deployment:deploy": {
        "subsystem": "deployment",
        "context_extractor": extract_deployment_context
    },
    "/deployment:deploy-validate": {
        "subsystem": "deployment",
        "context_extractor": extract_deployment_context
    },
    "/deployment:deploy-run": {
        "subsystem": "deployment",
        "context_extractor": extract_deployment_context
    },
    "/deployment:prod-ready": {
        "subsystem": "deployment",
        "context_extractor": extract_deployment_context
    },

    # Testing commands
    "/testing:test-generate": {
        "subsystem": "testing",
        "context_extractor": extract_testing_context
    },
    "/testing:test": {
        "subsystem": "testing",
        "context_extractor": extract_testing_context
    },
    "/testing:test-prod": {
        "subsystem": "testing",
        "context_extractor": extract_testing_context
    },

    # Documentation commands
    "/docs:init": {
        "subsystem": "documentation",
        "context_extractor": extract_docs_context
    },
    "/docs:update": {
        "subsystem": "documentation",
        "context_extractor": extract_docs_context
    },
    "/docs:validate": {
        "subsystem": "documentation",
        "context_extractor": extract_docs_context
    },

    # Iterate commands
    "/iterate:tasks": {
        "subsystem": "iterate",
        "context_extractor": lambda *a, **k: extract_iterate_context(*a, **k, phase="tasks")
    },
    "/iterate:sync": {
        "subsystem": "iterate",
        "context_extractor": lambda *a, **k: extract_iterate_context(*a, **k, phase="sync")
    },
    "/iterate:adjust": {
        "subsystem": "iterate",
        "context_extractor": lambda *a, **k: extract_iterate_context(*a, **k, phase="adjust")
    },

    # Supervisor commands
    "/supervisor:start": {
        "subsystem": "supervisor",
        "context_extractor": lambda *a, **k: extract_supervisor_context(*a, **k, phase="start")
    },
    "/supervisor:mid": {
        "subsystem": "supervisor",
        "context_extractor": lambda *a, **k: extract_supervisor_context(*a, **k, phase="mid")
    },
    "/supervisor:end": {
        "subsystem": "supervisor",
        "context_extractor": lambda *a, **k: extract_supervisor_context(*a, **k, phase="end")
    },

    # GitHub commands
    "/github:pr-review": {
        "subsystem": "github",
        "context_extractor": lambda *a, **k: extract_github_context(*a, **k, command="pr-review")
    },
    "/github:issue-review": {
        "subsystem": "github",
        "context_extractor": lambda *a, **k: extract_github_context(*a, **k, command="issue-review")
    },
    "/github:create-issue": {
        "subsystem": "github",
        "context_extractor": lambda *a, **k: extract_github_context(*a, **k, command="create-issue")
    },

    # Security commands (future)
    "/security:scan": {
        "subsystem": "security",
        "context_extractor": extract_security_context
    },
}


def get_hook_for_command(command: str) -> Optional[Dict[str, Any]]:
    """
    Get hook configuration for a command.

    Args:
        command: Command name (e.g., "/deployment:deploy-prepare")

    Returns:
        Hook configuration dict or None if not found
    """
    return COMMAND_HOOKS.get(command)


if __name__ == "__main__":
    # Example usage
    print("Command Wrapper - Example Usage")
    print("=" * 50)

    # Define a sample command
    @with_memory_tracking("deployment", extract_context=extract_deployment_context)
    def deploy_prepare(spec_dir):
        print(f"Deploying {spec_dir}...")
        return {
            "files_generated": 10,
            "detected_stack": "backend:fastapi::aws::"
        }

    # Execute command (memory tracking happens automatically)
    result = deploy_prepare("specs/002-system-context-we")
    print(f"\nResult: {result}")

    # Check memory file was created
    from .memory_manager import get_memory_manager
    memory = get_memory_manager("deployment")
    sessions = memory.search_sessions(limit=1)
    if sessions:
        print(f"\nMemory file created:")
        print(f"  Session: {sessions[0]['session_id']}")
        print(f"  Status: {sessions[0]['status']}")
        print(f"  Duration: {sessions[0]['duration_seconds']}s")
