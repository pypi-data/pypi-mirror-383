"""Textual TUI for the wt package - Git Worktree Manager.

This module provides a beautiful, feature-rich terminal user interface
for managing git worktrees using the Textual framework.
"""

from wt.tui.app import WorktreeApp, run_tui

__all__ = ["WorktreeApp", "run_tui"]
