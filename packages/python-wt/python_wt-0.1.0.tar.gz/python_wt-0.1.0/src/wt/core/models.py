"""Core Pydantic models for the wt (worktree) package.

This module provides type-safe, validated data models for git worktrees, branches,
repositories, and remotes using Pydantic v2.
"""

from __future__ import annotations

from collections.abc import Sequence
from pathlib import Path
from typing import Any

from pydantic import BaseModel, ConfigDict, Field, field_validator, computed_field


class WorktreeInfo(BaseModel):
    """Represents a git worktree with its current state.

    A worktree is a working directory linked to a repository, allowing multiple
    branches to be checked out simultaneously in different directories.

    Attributes:
        path: Absolute path to the worktree directory
        branch: Name of the currently checked out branch (None for detached HEAD)
        commit: SHA-1 hash of the current commit
        is_locked: Whether the worktree is locked (prevents pruning)
        is_prunable: Whether the worktree can be pruned (missing/corrupted)
        lock_reason: Optional reason why the worktree is locked

    Example:
        >>> wt = WorktreeInfo(
        ...     path="/home/user/repo",
        ...     branch="main",
        ...     commit="abc123def456",
        ...     is_locked=False,
        ...     is_prunable=False
        ... )
        >>> wt.is_main_worktree
        True
    """

    model_config = ConfigDict(
        frozen=True,
        strict=True,
        validate_assignment=True,
        str_strip_whitespace=True,
        use_enum_values=True,
    )

    path: Path = Field(
        ...,
        description="Absolute path to the worktree directory",
    )
    branch: str | None = Field(
        default=None,
        description="Currently checked out branch name (None for detached HEAD)",
        min_length=1,
    )
    commit: str = Field(
        ...,
        description="SHA-1 hash of the current commit",
        min_length=7,
        max_length=40,
    )
    is_locked: bool = Field(
        default=False,
        description="Whether the worktree is locked",
    )
    is_prunable: bool = Field(
        default=False,
        description="Whether the worktree can be pruned",
    )
    lock_reason: str | None = Field(
        default=None,
        description="Reason why the worktree is locked",
    )

    @field_validator("path", mode="before")
    @classmethod
    def validate_path(cls, v: Any) -> Path:
        """Ensure path is absolute and converted to Path object."""
        if isinstance(v, str):
            v = Path(v)
        if not isinstance(v, Path):
            msg = f"Path must be a string or Path object, got {type(v)}"
            raise TypeError(msg)
        return v.resolve()

    @field_validator("commit")
    @classmethod
    def validate_commit(cls, v: str) -> str:
        """Validate commit hash is hexadecimal."""
        if not v:
            msg = "Commit hash cannot be empty"
            raise ValueError(msg)
        if not all(c in "0123456789abcdef" for c in v.lower()):
            msg = f"Invalid commit hash: {v}"
            raise ValueError(msg)
        return v.lower()

    @field_validator("branch")
    @classmethod
    def validate_branch(cls, v: str | None) -> str | None:
        """Validate branch name if present."""
        if v is not None and not v.strip():
            msg = "Branch name cannot be empty or whitespace"
            raise ValueError(msg)
        return v

    @computed_field  # type: ignore[prop-decorator]
    @property
    def is_main_worktree(self) -> bool:
        """Check if this is the main worktree.

        The main worktree is typically named '.git' in its parent directory
        and serves as the primary repository location.
        """
        return (self.path / ".git").is_file() or (self.path / ".git").is_symlink()

    @computed_field  # type: ignore[prop-decorator]
    @property
    def is_detached(self) -> bool:
        """Check if the worktree has a detached HEAD (no branch)."""
        return self.branch is None

    @computed_field  # type: ignore[prop-decorator]
    @property
    def short_commit(self) -> str:
        """Get the short version of the commit hash (first 7 characters)."""
        return self.commit[:7]

    @computed_field  # type: ignore[prop-decorator]
    @property
    def display_name(self) -> str:
        """Get a human-readable display name for the worktree."""
        if self.branch:
            return self.branch
        return f"(detached {self.short_commit})"

    def __str__(self) -> str:
        """Return a string representation of the worktree."""
        status_parts = []
        if self.is_locked:
            status_parts.append("locked")
        if self.is_prunable:
            status_parts.append("prunable")
        status = f" [{', '.join(status_parts)}]" if status_parts else ""
        return f"{self.path} -> {self.display_name}{status}"


class BranchInfo(BaseModel):
    """Represents a git branch with its tracking information.

    Attributes:
        name: Branch name (e.g., 'main', 'feature/new-ui')
        commit: SHA-1 hash of the branch's current commit
        remote: Remote repository name this branch tracks (e.g., 'origin')
        is_current: Whether this is the currently checked out branch
        upstream: Upstream branch reference (e.g., 'origin/main')
        is_head_detached: Whether HEAD is detached on this branch

    Example:
        >>> branch = BranchInfo(
        ...     name="feature/awesome",
        ...     commit="abc123",
        ...     remote="origin",
        ...     is_current=True,
        ...     upstream="origin/main"
        ... )
        >>> branch.full_name
        'refs/heads/feature/awesome'
    """

    model_config = ConfigDict(
        frozen=True,
        strict=True,
        validate_assignment=True,
        str_strip_whitespace=True,
    )

    name: str = Field(
        ...,
        description="Branch name",
        min_length=1,
    )
    commit: str = Field(
        ...,
        description="SHA-1 hash of the branch's HEAD commit",
        min_length=7,
        max_length=40,
    )
    remote: str | None = Field(
        default=None,
        description="Remote repository this branch tracks",
    )
    is_current: bool = Field(
        default=False,
        description="Whether this is the currently checked out branch",
    )
    upstream: str | None = Field(
        default=None,
        description="Upstream branch reference (e.g., 'origin/main')",
    )
    is_head_detached: bool = Field(
        default=False,
        description="Whether HEAD is detached",
    )

    @field_validator("name")
    @classmethod
    def validate_name(cls, v: str) -> str:
        """Validate branch name is not empty and doesn't contain invalid characters."""
        if not v.strip():
            msg = "Branch name cannot be empty or whitespace"
            raise ValueError(msg)
        # Git branch names cannot contain certain characters
        invalid_chars = [" ", "~", "^", ":", "?", "*", "[", "\\", ".."]
        for char in invalid_chars:
            if char in v:
                msg = f"Branch name cannot contain '{char}'"
                raise ValueError(msg)
        return v

    @field_validator("commit")
    @classmethod
    def validate_commit(cls, v: str) -> str:
        """Validate commit hash is hexadecimal."""
        if not v:
            msg = "Commit hash cannot be empty"
            raise ValueError(msg)
        if not all(c in "0123456789abcdef" for c in v.lower()):
            msg = f"Invalid commit hash: {v}"
            raise ValueError(msg)
        return v.lower()

    @computed_field  # type: ignore[prop-decorator]
    @property
    def short_commit(self) -> str:
        """Get the short version of the commit hash (first 7 characters)."""
        return self.commit[:7]

    @computed_field  # type: ignore[prop-decorator]
    @property
    def full_name(self) -> str:
        """Get the fully qualified branch reference (refs/heads/<name>)."""
        return f"refs/heads/{self.name}"

    @computed_field  # type: ignore[prop-decorator]
    @property
    def has_upstream(self) -> bool:
        """Check if the branch has an upstream tracking branch."""
        return self.upstream is not None

    @computed_field  # type: ignore[prop-decorator]
    @property
    def is_remote_tracking(self) -> bool:
        """Check if this branch tracks a remote branch."""
        return self.remote is not None and self.upstream is not None

    def __str__(self) -> str:
        """Return a string representation of the branch."""
        current = "* " if self.is_current else "  "
        upstream_info = f" -> {self.upstream}" if self.upstream else ""
        return f"{current}{self.name} ({self.short_commit}){upstream_info}"


class RemoteInfo(BaseModel):
    """Represents a git remote repository configuration.

    Attributes:
        name: Remote name (e.g., 'origin', 'upstream')
        url: Default URL for the remote
        fetch_url: URL used for fetch operations (defaults to url)
        push_url: URL used for push operations (defaults to url)

    Example:
        >>> remote = RemoteInfo(
        ...     name="origin",
        ...     url="https://github.com/user/repo.git"
        ... )
        >>> remote.is_https
        True
    """

    model_config = ConfigDict(
        frozen=True,
        strict=True,
        validate_assignment=True,
        str_strip_whitespace=True,
    )

    name: str = Field(
        ...,
        description="Remote repository name",
        min_length=1,
    )
    url: str = Field(
        ...,
        description="Default URL for the remote repository",
        min_length=1,
    )
    fetch_url: str | None = Field(
        default=None,
        description="URL used for fetch operations",
    )
    push_url: str | None = Field(
        default=None,
        description="URL used for push operations",
    )

    @field_validator("name")
    @classmethod
    def validate_name(cls, v: str) -> str:
        """Validate remote name is not empty."""
        if not v.strip():
            msg = "Remote name cannot be empty or whitespace"
            raise ValueError(msg)
        return v

    @field_validator("url")
    @classmethod
    def validate_url(cls, v: str) -> str:
        """Validate URL is not empty."""
        if not v.strip():
            msg = "Remote URL cannot be empty or whitespace"
            raise ValueError(msg)
        return v

    @computed_field  # type: ignore[prop-decorator]
    @property
    def effective_fetch_url(self) -> str:
        """Get the URL used for fetch operations (falls back to url)."""
        return self.fetch_url or self.url

    @computed_field  # type: ignore[prop-decorator]
    @property
    def effective_push_url(self) -> str:
        """Get the URL used for push operations (falls back to url)."""
        return self.push_url or self.url

    @computed_field  # type: ignore[prop-decorator]
    @property
    def is_https(self) -> bool:
        """Check if the remote uses HTTPS protocol."""
        return self.url.startswith("https://")

    @computed_field  # type: ignore[prop-decorator]
    @property
    def is_ssh(self) -> bool:
        """Check if the remote uses SSH protocol."""
        return self.url.startswith("git@") or self.url.startswith("ssh://")

    @computed_field  # type: ignore[prop-decorator]
    @property
    def is_local(self) -> bool:
        """Check if the remote is a local file path."""
        return (
            self.url.startswith("/")
            or self.url.startswith("file://")
            or self.url.startswith(".")
        )

    def __str__(self) -> str:
        """Return a string representation of the remote."""
        fetch = f" (fetch: {self.fetch_url})" if self.fetch_url else ""
        push = f" (push: {self.push_url})" if self.push_url else ""
        return f"{self.name}: {self.url}{fetch}{push}"


class RepositoryInfo(BaseModel):
    """Represents a git repository with its worktrees and configuration.

    This is the main model that aggregates all repository information including
    worktrees, branches, remotes, and the repository structure.

    Attributes:
        root: Absolute path to the repository root directory
        git_dir: Absolute path to the .git directory
        current_branch: Name of the currently checked out branch (None if detached)
        worktrees: List of all worktrees in the repository
        branches: List of all branches in the repository
        remotes: List of all configured remotes
        is_bare: Whether this is a bare repository

    Example:
        >>> repo = RepositoryInfo(
        ...     root="/home/user/project",
        ...     git_dir="/home/user/project/.git",
        ...     current_branch="main",
        ...     worktrees=[],
        ... )
        >>> repo.worktree_count
        0
    """

    model_config = ConfigDict(
        frozen=True,
        strict=True,
        validate_assignment=True,
        str_strip_whitespace=True,
    )

    root: Path = Field(
        ...,
        description="Absolute path to the repository root",
    )
    git_dir: Path = Field(
        ...,
        description="Absolute path to the .git directory",
    )
    current_branch: str | None = Field(
        default=None,
        description="Currently checked out branch name",
    )
    worktrees: Sequence[WorktreeInfo] = Field(
        default_factory=list,
        description="List of all worktrees",
    )
    branches: Sequence[BranchInfo] = Field(
        default_factory=list,
        description="List of all branches",
    )
    remotes: Sequence[RemoteInfo] = Field(
        default_factory=list,
        description="List of all remotes",
    )
    is_bare: bool = Field(
        default=False,
        description="Whether this is a bare repository",
    )

    @field_validator("root", "git_dir", mode="before")
    @classmethod
    def validate_path(cls, v: Any) -> Path:
        """Ensure paths are absolute and converted to Path objects."""
        if isinstance(v, str):
            v = Path(v)
        if not isinstance(v, Path):
            msg = f"Path must be a string or Path object, got {type(v)}"
            raise TypeError(msg)
        return v.resolve()

    @field_validator("current_branch")
    @classmethod
    def validate_branch(cls, v: str | None) -> str | None:
        """Validate branch name if present."""
        if v is not None and not v.strip():
            msg = "Branch name cannot be empty or whitespace"
            raise ValueError(msg)
        return v

    @computed_field  # type: ignore[prop-decorator]
    @property
    def worktree_count(self) -> int:
        """Get the total number of worktrees."""
        return len(self.worktrees)

    @computed_field  # type: ignore[prop-decorator]
    @property
    def branch_count(self) -> int:
        """Get the total number of branches."""
        return len(self.branches)

    @computed_field  # type: ignore[prop-decorator]
    @property
    def remote_count(self) -> int:
        """Get the total number of remotes."""
        return len(self.remotes)

    @computed_field  # type: ignore[prop-decorator]
    @property
    def has_worktrees(self) -> bool:
        """Check if the repository has any additional worktrees."""
        return len(self.worktrees) > 0

    @computed_field  # type: ignore[prop-decorator]
    @property
    def has_remotes(self) -> bool:
        """Check if the repository has any configured remotes."""
        return len(self.remotes) > 0

    @computed_field  # type: ignore[prop-decorator]
    @property
    def is_detached(self) -> bool:
        """Check if HEAD is detached (no current branch)."""
        return self.current_branch is None

    @computed_field  # type: ignore[prop-decorator]
    @property
    def main_worktree(self) -> WorktreeInfo | None:
        """Get the main worktree (if any)."""
        for worktree in self.worktrees:
            if worktree.is_main_worktree:
                return worktree
        return None

    @computed_field  # type: ignore[prop-decorator]
    @property
    def active_worktrees(self) -> Sequence[WorktreeInfo]:
        """Get all worktrees that are not prunable."""
        return [wt for wt in self.worktrees if not wt.is_prunable]

    @computed_field  # type: ignore[prop-decorator]
    @property
    def locked_worktrees(self) -> Sequence[WorktreeInfo]:
        """Get all locked worktrees."""
        return [wt for wt in self.worktrees if wt.is_locked]

    def get_worktree_by_path(self, path: Path | str) -> WorktreeInfo | None:
        """Get a worktree by its path.

        Args:
            path: Path to the worktree directory

        Returns:
            The worktree info if found, None otherwise
        """
        if isinstance(path, str):
            path = Path(path)
        path = path.resolve()
        for worktree in self.worktrees:
            if worktree.path == path:
                return worktree
        return None

    def get_worktree_by_branch(self, branch: str) -> WorktreeInfo | None:
        """Get a worktree by its branch name.

        Args:
            branch: Branch name to search for

        Returns:
            The worktree info if found, None otherwise
        """
        for worktree in self.worktrees:
            if worktree.branch == branch:
                return worktree
        return None

    def get_branch_by_name(self, name: str) -> BranchInfo | None:
        """Get a branch by its name.

        Args:
            name: Branch name to search for

        Returns:
            The branch info if found, None otherwise
        """
        for branch in self.branches:
            if branch.name == name:
                return branch
        return None

    def get_remote_by_name(self, name: str) -> RemoteInfo | None:
        """Get a remote by its name.

        Args:
            name: Remote name to search for

        Returns:
            The remote info if found, None otherwise
        """
        for remote in self.remotes:
            if remote.name == name:
                return remote
        return None

    def __str__(self) -> str:
        """Return a string representation of the repository."""
        branch = self.current_branch or "(detached)"
        return (
            f"Repository at {self.root} "
            f"[{branch}] "
            f"({self.worktree_count} worktrees, "
            f"{self.branch_count} branches, "
            f"{self.remote_count} remotes)"
        )
