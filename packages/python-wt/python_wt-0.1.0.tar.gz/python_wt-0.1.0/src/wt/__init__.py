"""wt - The ultimate git worktree manager.

A modern Python package for managing git worktrees with a beautiful TUI and powerful CLI.
"""

from wt.core.models import WorktreeInfo, BranchInfo, RepositoryInfo
from wt.core.exceptions import (
    WtError,
    RepositoryNotFoundError,
    WorktreeExistsError,
    BranchNotFoundError,
    GitCommandError,
)
from wt.core.repository import Repository

__version__ = "1.0.0"
__all__ = [
    "WorktreeInfo",
    "BranchInfo",
    "RepositoryInfo",
    "WtError",
    "RepositoryNotFoundError",
    "WorktreeExistsError",
    "BranchNotFoundError",
    "GitCommandError",
    "Repository",
]
