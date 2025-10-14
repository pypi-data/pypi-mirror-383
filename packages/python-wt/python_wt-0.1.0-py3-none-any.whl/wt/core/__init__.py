"""Core functionality for the wt (worktree) package.

This module provides the core data models and exception hierarchy for
git worktree management operations.
"""

from __future__ import annotations

from wt.core.exceptions import (
    BranchExistsError,
    BranchInUseError,
    BranchNotFoundError,
    ConfigurationError,
    GitCommandError,
    InvalidPathError,
    RemoteNotFoundError,
    RepositoryNotFoundError,
    WorktreeExistsError,
    WorktreeLockedError,
    WorktreeNotFoundError,
    WtError,
)
from wt.core.models import BranchInfo, RemoteInfo, RepositoryInfo, WorktreeInfo
from wt.core.repository import Repository

__all__ = [
    # Models
    "WorktreeInfo",
    "BranchInfo",
    "RemoteInfo",
    "RepositoryInfo",
    "Repository",
    # Exceptions
    "WtError",
    "RepositoryNotFoundError",
    "WorktreeExistsError",
    "WorktreeNotFoundError",
    "BranchExistsError",
    "BranchNotFoundError",
    "BranchInUseError",
    "GitCommandError",
    "RemoteNotFoundError",
    "InvalidPathError",
    "WorktreeLockedError",
    "ConfigurationError",
]
