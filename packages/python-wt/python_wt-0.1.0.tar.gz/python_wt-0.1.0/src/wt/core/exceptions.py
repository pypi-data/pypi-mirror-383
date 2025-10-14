"""Exception hierarchy for the wt (worktree) package.

This module provides a comprehensive set of exceptions for handling errors
in git operations, worktree management, and repository interactions.
"""

from __future__ import annotations

from collections.abc import Sequence
from pathlib import Path


class WtError(Exception):
    """Base exception for all wt package errors.

    This is the root exception that all other wt exceptions inherit from,
    allowing users to catch all package-specific errors with a single handler.

    Example:
        >>> try:
        ...     # Some wt operation
        ...     pass
        ... except WtError as e:
        ...     print(f"An error occurred: {e}")
    """

    def __init__(self, message: str, *args: object) -> None:
        """Initialize the base error.

        Args:
            message: Human-readable error message
            *args: Additional arguments passed to Exception
        """
        super().__init__(message, *args)
        self.message = message

    def __str__(self) -> str:
        """Return the error message."""
        return self.message


class RepositoryNotFoundError(WtError):
    """Raised when a git repository cannot be found at the specified path.

    This error occurs when trying to perform git operations in a directory
    that is not part of a git repository.

    Attributes:
        path: The path where the repository was expected to be found

    Example:
        >>> raise RepositoryNotFoundError("/invalid/path")
        Traceback (most recent call last):
        ...
        RepositoryNotFoundError: Git repository not found at /invalid/path
    """

    def __init__(self, path: Path | str) -> None:
        """Initialize the repository not found error.

        Args:
            path: Path where the repository was expected
        """
        self.path = Path(path) if isinstance(path, str) else path
        message = (
            f"Git repository not found at {self.path}. "
            "Make sure you're in a git repository or initialize one with 'git init'."
        )
        super().__init__(message)


class WorktreeExistsError(WtError):
    """Raised when attempting to create a worktree that already exists.

    This error occurs when trying to create a new worktree at a path that
    is already occupied by another worktree.

    Attributes:
        path: The path where the worktree already exists
        branch: The branch name (if any) associated with the existing worktree

    Example:
        >>> raise WorktreeExistsError("/existing/worktree", "feature-branch")
        Traceback (most recent call last):
        ...
        WorktreeExistsError: Worktree already exists at /existing/worktree (branch: feature-branch)
    """

    def __init__(self, path: Path | str, branch: str | None = None) -> None:
        """Initialize the worktree exists error.

        Args:
            path: Path where the worktree already exists
            branch: Branch name associated with the worktree
        """
        self.path = Path(path) if isinstance(path, str) else path
        self.branch = branch
        message = f"Worktree already exists at {self.path}"
        if branch:
            message += f" (branch: {branch})"
        message += ". Use a different path or remove the existing worktree first."
        super().__init__(message)


class WorktreeNotFoundError(WtError):
    """Raised when a worktree cannot be found.

    This error occurs when trying to perform operations on a worktree
    that doesn't exist or has been removed.

    Attributes:
        identifier: The path or branch name used to identify the worktree

    Example:
        >>> raise WorktreeNotFoundError("/missing/worktree")
        Traceback (most recent call last):
        ...
        WorktreeNotFoundError: Worktree not found: /missing/worktree
    """

    def __init__(self, identifier: Path | str) -> None:
        """Initialize the worktree not found error.

        Args:
            identifier: Path or branch name of the missing worktree
        """
        self.identifier = str(identifier)
        message = (
            f"Worktree not found: {self.identifier}. "
            "Check the path or branch name and try again."
        )
        super().__init__(message)


class BranchExistsError(WtError):
    """Raised when attempting to create a branch that already exists.

    This error occurs when trying to create a new branch with a name
    that is already in use.

    Attributes:
        branch_name: The name of the existing branch

    Example:
        >>> raise BranchExistsError("main")
        Traceback (most recent call last):
        ...
        BranchExistsError: Branch 'main' already exists
    """

    def __init__(self, branch_name: str) -> None:
        """Initialize the branch exists error.

        Args:
            branch_name: Name of the branch that already exists
        """
        self.branch_name = branch_name
        message = (
            f"Branch '{branch_name}' already exists. "
            "Use a different name or delete the existing branch."
        )
        super().__init__(message)


class BranchNotFoundError(WtError):
    """Raised when a branch cannot be found.

    This error occurs when trying to perform operations on a branch
    that doesn't exist in the repository.

    Attributes:
        branch_name: The name of the missing branch

    Example:
        >>> raise BranchNotFoundError("nonexistent-branch")
        Traceback (most recent call last):
        ...
        BranchNotFoundError: Branch 'nonexistent-branch' not found
    """

    def __init__(self, branch_name: str) -> None:
        """Initialize the branch not found error.

        Args:
            branch_name: Name of the branch that couldn't be found
        """
        self.branch_name = branch_name
        message = (
            f"Branch '{branch_name}' not found. "
            "Check the branch name and try again."
        )
        super().__init__(message)


class BranchInUseError(WtError):
    """Raised when attempting to delete or modify a branch that is in use.

    This error occurs when a branch is checked out in a worktree and
    cannot be deleted or modified without first removing the worktree.

    Attributes:
        branch_name: The name of the branch in use
        worktree_path: Path to the worktree using the branch

    Example:
        >>> raise BranchInUseError("feature", "/path/to/worktree")
        Traceback (most recent call last):
        ...
        BranchInUseError: Branch 'feature' is checked out in worktree at /path/to/worktree
    """

    def __init__(self, branch_name: str, worktree_path: Path | str) -> None:
        """Initialize the branch in use error.

        Args:
            branch_name: Name of the branch in use
            worktree_path: Path to the worktree using the branch
        """
        self.branch_name = branch_name
        self.worktree_path = Path(worktree_path) if isinstance(worktree_path, str) else worktree_path
        message = (
            f"Branch '{branch_name}' is checked out in worktree at {self.worktree_path}. "
            "Remove the worktree first before deleting the branch."
        )
        super().__init__(message)


class GitCommandError(WtError):
    """Raised when a git command execution fails.

    This error provides detailed information about the failed git command,
    including the command itself, return code, and output streams.

    Attributes:
        command: The git command that was executed
        returncode: The exit code returned by the command
        stdout: Standard output from the command
        stderr: Standard error output from the command

    Example:
        >>> raise GitCommandError(
        ...     command=["git", "status"],
        ...     returncode=128,
        ...     stdout="",
        ...     stderr="fatal: not a git repository"
        ... )
        Traceback (most recent call last):
        ...
        GitCommandError: Git command failed with exit code 128: git status
    """

    def __init__(
        self,
        command: str | Sequence[str],
        returncode: int,
        stdout: str = "",
        stderr: str = "",
    ) -> None:
        """Initialize the git command error.

        Args:
            command: The git command that failed (as string or list)
            returncode: Exit code from the command
            stdout: Standard output from the command
            stderr: Standard error output from the command
        """
        self.command = command if isinstance(command, str) else " ".join(command)
        self.returncode = returncode
        self.stdout = stdout.strip()
        self.stderr = stderr.strip()

        # Build a helpful error message
        message_parts = [f"Git command failed with exit code {returncode}: {self.command}"]

        if self.stderr:
            message_parts.append(f"\nError output: {self.stderr}")
        elif self.stdout:
            message_parts.append(f"\nOutput: {self.stdout}")

        super().__init__("".join(message_parts))

    def __str__(self) -> str:
        """Return a formatted string representation of the error."""
        parts = [f"GitCommandError: {self.message}"]
        if self.stderr:
            # Show first few lines of stderr for context
            stderr_lines = self.stderr.split("\n")
            if len(stderr_lines) > 5:
                stderr_preview = "\n".join(stderr_lines[:5]) + "\n..."
            else:
                stderr_preview = self.stderr
            parts.append(f"\nStderr:\n{stderr_preview}")
        return "\n".join(parts)


class RemoteNotFoundError(WtError):
    """Raised when a git remote cannot be found.

    This error occurs when trying to perform operations on a remote
    that doesn't exist in the repository configuration.

    Attributes:
        remote_name: The name of the missing remote

    Example:
        >>> raise RemoteNotFoundError("upstream")
        Traceback (most recent call last):
        ...
        RemoteNotFoundError: Remote 'upstream' not found
    """

    def __init__(self, remote_name: str) -> None:
        """Initialize the remote not found error.

        Args:
            remote_name: Name of the remote that couldn't be found
        """
        self.remote_name = remote_name
        message = (
            f"Remote '{remote_name}' not found. "
            "Check your git remote configuration with 'git remote -v'."
        )
        super().__init__(message)


class InvalidPathError(WtError):
    """Raised when an invalid or inaccessible path is provided.

    This error occurs when a path is invalid, doesn't exist, or cannot
    be accessed due to permissions or other issues.

    Attributes:
        path: The invalid path
        reason: Optional reason why the path is invalid

    Example:
        >>> raise InvalidPathError("/invalid/path", "Path does not exist")
        Traceback (most recent call last):
        ...
        InvalidPathError: Invalid path: /invalid/path (Path does not exist)
    """

    def __init__(self, path: Path | str, reason: str | None = None) -> None:
        """Initialize the invalid path error.

        Args:
            path: The invalid path
            reason: Optional reason why the path is invalid
        """
        self.path = Path(path) if isinstance(path, str) else path
        self.reason = reason
        message = f"Invalid path: {self.path}"
        if reason:
            message += f" ({reason})"
        super().__init__(message)


class WorktreeLockedError(WtError):
    """Raised when attempting to modify or remove a locked worktree.

    This error occurs when trying to perform operations on a worktree
    that has been locked, typically to prevent accidental deletion.

    Attributes:
        path: Path to the locked worktree
        reason: Optional reason why the worktree is locked

    Example:
        >>> raise WorktreeLockedError("/path/to/worktree", "In use by CI")
        Traceback (most recent call last):
        ...
        WorktreeLockedError: Worktree at /path/to/worktree is locked (In use by CI)
    """

    def __init__(self, path: Path | str, reason: str | None = None) -> None:
        """Initialize the worktree locked error.

        Args:
            path: Path to the locked worktree
            reason: Optional reason for the lock
        """
        self.path = Path(path) if isinstance(path, str) else path
        self.reason = reason
        message = f"Worktree at {self.path} is locked"
        if reason:
            message += f" ({reason})"
        message += ". Unlock it first with 'git worktree unlock' or use --force."
        super().__init__(message)


class ConfigurationError(WtError):
    """Raised when there is an issue with configuration.

    This error occurs when the wt configuration is invalid, incomplete,
    or cannot be loaded.

    Attributes:
        config_key: Optional configuration key that caused the error
        reason: Description of the configuration issue

    Example:
        >>> raise ConfigurationError("default_path", "Invalid directory path")
        Traceback (most recent call last):
        ...
        ConfigurationError: Configuration error for 'default_path': Invalid directory path
    """

    def __init__(self, config_key: str | None = None, reason: str = "Invalid configuration") -> None:
        """Initialize the configuration error.

        Args:
            config_key: Optional key that caused the error
            reason: Description of the issue
        """
        self.config_key = config_key
        self.reason = reason
        if config_key:
            message = f"Configuration error for '{config_key}': {reason}"
        else:
            message = f"Configuration error: {reason}"
        super().__init__(message)


# Export all exceptions
__all__ = [
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
