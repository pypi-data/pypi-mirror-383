"""
Multiagent Core Utilities

Provides core functionality for the multiagent framework including:
- Automatic memory tracking
- Command execution hooks
- Session management
"""

__version__ = "1.0.0"

from .memory_manager import MemoryManager, get_memory_manager

__all__ = ['MemoryManager', 'get_memory_manager']
