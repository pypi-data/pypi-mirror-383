"""Async git repository operations for the wt package.

This module provides a comprehensive Repository class for interacting with git repositories,
worktrees, branches, and remotes using async subprocess-based command execution.
"""

from __future__ import annotations

import asyncio
import os
import re
from collections.abc import AsyncIterator, Callable, Sequence
from pathlib import Path
from typing import Any

from wt.core.exceptions import (
    BranchNotFoundError,
    GitCommandError,
    RepositoryNotFoundError,
    WorktreeExistsError,
)
from wt.core.models import BranchInfo, RemoteInfo, RepositoryInfo, WorktreeInfo

# Type alias for progress callbacks
ProgressCallback = Callable[[str], None]


class Repository:
    """Async git repository manager with comprehensive operations support.

    This class provides async methods for git operations including repository discovery,
    worktree management, branch operations, and remote interactions with streaming support.

    Attributes:
        repo_info: Information about the repository structure
        git_dir: Path to the .git directory
        root: Path to the repository root (work tree)
        is_bare: Whether this is a bare repository

    Example:
        >>> import asyncio
        >>> async def main():
        ...     repo = await Repository.discover()
        ...     worktrees = await repo.list_worktrees()
        ...     for wt in worktrees:
        ...         print(f"{wt.path} -> {wt.branch}")
        >>> asyncio.run(main())
    """

    def __init__(self, repo_info: RepositoryInfo) -> None:
        """Initialize a Repository instance.

        Args:
            repo_info: Repository information structure

        Example:
            >>> repo_info = RepositoryInfo(
            ...     root=Path("/home/user/project"),
            ...     git_dir=Path("/home/user/project/.git"),
            ... )
            >>> repo = Repository(repo_info)
        """
        self.repo_info = repo_info
        self.git_dir = repo_info.git_dir
        self.root = repo_info.root
        self.is_bare = repo_info.is_bare

    @classmethod
    async def discover(
        cls, path: Path | str | None = None, *, search_parent: bool = True
    ) -> Repository:
        """Discover and initialize a git repository from a path.

        This method intelligently detects various repository layouts:
        - Normal repositories with .git directory
        - Bare repositories (*.git directories)
        - Worktrees
        - Special patterns like aiperf/aiperf.git

        Args:
            path: Path to start discovery from (defaults to current directory)
            search_parent: Whether to search parent directories for a repository

        Returns:
            Repository instance

        Raises:
            RepositoryNotFoundError: If no repository is found

        Example:
            >>> repo = await Repository.discover()  # Discover from current directory
            >>> repo = await Repository.discover("/path/to/repo")  # Specific path
        """
        if path is None:
            search_path = Path.cwd()
        else:
            search_path = Path(path).resolve()

        # Try to find repository using git rev-parse
        try:
            git_dir_str = await cls._run_git_command(
                ["git", "rev-parse", "--git-dir"],
                cwd=search_path,
                capture_output=True,
            )
            git_dir = (search_path / git_dir_str.strip()).resolve()

            # Check if this is a bare repository
            is_bare_str = await cls._run_git_command(
                ["git", "rev-parse", "--is-bare-repository"],
                cwd=search_path,
                capture_output=True,
            )
            is_bare = is_bare_str.strip().lower() == "true"

            # Get work tree (repository root)
            if not is_bare:
                try:
                    root_str = await cls._run_git_command(
                        ["git", "rev-parse", "--show-toplevel"],
                        cwd=search_path,
                        capture_output=True,
                    )
                    root = Path(root_str.strip())
                except GitCommandError:
                    # Some worktrees might not have a toplevel
                    root = search_path
            else:
                root = git_dir

            # Get current branch
            current_branch: str | None = None
            try:
                branch_str = await cls._run_git_command(
                    ["git", "symbolic-ref", "--short", "HEAD"],
                    cwd=search_path,
                    capture_output=True,
                )
                current_branch = branch_str.strip()
            except GitCommandError:
                # HEAD is detached or other error
                pass

            repo_info = RepositoryInfo(
                root=root,
                git_dir=git_dir,
                current_branch=current_branch,
                is_bare=is_bare,
            )

            return cls(repo_info)

        except GitCommandError as e:
            if not search_parent:
                raise RepositoryNotFoundError(search_path) from e

            # Try special patterns like aiperf/aiperf.git
            if search_path.name.endswith(".git"):
                # This might be a bare repo
                if (search_path / "config").exists() and (search_path / "refs").exists():
                    repo_info = RepositoryInfo(
                        root=search_path,
                        git_dir=search_path,
                        is_bare=True,
                    )
                    return cls(repo_info)

            # Search for *.git pattern in current directory
            git_dirs = list(search_path.glob("*.git"))
            if git_dirs:
                bare_repo = git_dirs[0]
                if (bare_repo / "config").exists() and (bare_repo / "refs").exists():
                    repo_info = RepositoryInfo(
                        root=bare_repo,
                        git_dir=bare_repo,
                        is_bare=True,
                    )
                    return cls(repo_info)

            # Try parent directory
            if search_path.parent != search_path:
                return await cls.discover(search_path.parent, search_parent=True)

            raise RepositoryNotFoundError(search_path) from e

    @staticmethod
    async def _run_git_command(
        cmd: Sequence[str],
        cwd: Path | None = None,
        *,
        capture_output: bool = False,
        env: dict[str, str] | None = None,
    ) -> str:
        """Run a git command and return stdout.

        Args:
            cmd: Command and arguments to run
            cwd: Working directory for the command
            capture_output: Whether to capture and return output
            env: Additional environment variables

        Returns:
            Standard output from the command (if capture_output=True)

        Raises:
            GitCommandError: If the command fails
        """
        # Merge with current environment
        command_env = os.environ.copy()
        if env:
            command_env.update(env)

        process = await asyncio.create_subprocess_exec(
            *cmd,
            cwd=cwd,
            stdout=asyncio.subprocess.PIPE if capture_output else None,
            stderr=asyncio.subprocess.PIPE,
            env=command_env,
        )

        stdout, stderr = await process.communicate()

        if process.returncode != 0:
            stderr_str = stderr.decode("utf-8", errors="replace") if stderr else ""
            stdout_str = stdout.decode("utf-8", errors="replace") if stdout else ""
            raise GitCommandError(
                command=cmd,
                returncode=process.returncode,
                stdout=stdout_str,
                stderr=stderr_str,
            )

        return stdout.decode("utf-8", errors="replace") if stdout else ""

    async def _run_git_in_repo(
        self,
        args: Sequence[str],
        *,
        capture_output: bool = False,
        env: dict[str, str] | None = None,
    ) -> str:
        """Run a git command in the context of this repository.

        Args:
            args: Git arguments (without 'git' prefix)
            capture_output: Whether to capture and return output
            env: Additional environment variables

        Returns:
            Standard output from the command (if capture_output=True)

        Raises:
            GitCommandError: If the command fails
        """
        cmd = ["git", *args]
        cwd = self.root if not self.is_bare else self.git_dir
        return await self._run_git_command(cmd, cwd=cwd, capture_output=capture_output, env=env)

    async def _stream_git_command(
        self,
        args: Sequence[str],
        on_progress: ProgressCallback | None = None,
        *,
        env: dict[str, str] | None = None,
    ) -> None:
        """Run a git command and stream its output to a progress callback.

        Args:
            args: Git arguments (without 'git' prefix)
            on_progress: Callback function to receive output lines
            env: Additional environment variables

        Raises:
            GitCommandError: If the command fails
        """
        cmd = ["git", *args]
        cwd = self.root if not self.is_bare else self.git_dir

        # Merge with current environment
        command_env = os.environ.copy()
        if env:
            command_env.update(env)

        process = await asyncio.create_subprocess_exec(
            *cmd,
            cwd=cwd,
            stdout=asyncio.subprocess.PIPE,
            stderr=asyncio.subprocess.PIPE,
            env=command_env,
        )

        # Stream stderr (where git progress goes) line by line
        async def stream_output(stream: asyncio.StreamReader) -> list[str]:
            lines = []
            while True:
                line_bytes = await stream.readline()
                if not line_bytes:
                    break
                line = line_bytes.decode("utf-8", errors="replace").rstrip()
                lines.append(line)
                if on_progress and line:
                    on_progress(line)
            return lines

        # Stream both stdout and stderr
        stdout_task = asyncio.create_task(stream_output(process.stdout))  # type: ignore[arg-type]
        stderr_task = asyncio.create_task(stream_output(process.stderr))  # type: ignore[arg-type]

        stdout_lines, stderr_lines = await asyncio.gather(stdout_task, stderr_task)
        returncode = await process.wait()

        if returncode != 0:
            stdout_str = "\n".join(stdout_lines)
            stderr_str = "\n".join(stderr_lines)
            raise GitCommandError(
                command=cmd,
                returncode=returncode,
                stdout=stdout_str,
                stderr=stderr_str,
            )

    async def list_worktrees(self) -> list[WorktreeInfo]:
        """List all worktrees in the repository.

        Returns:
            List of WorktreeInfo objects for each worktree

        Raises:
            GitCommandError: If the git command fails

        Example:
            >>> worktrees = await repo.list_worktrees()
            >>> for wt in worktrees:
            ...     print(f"{wt.path} -> {wt.branch}")
        """
        output = await self._run_git_in_repo(
            ["worktree", "list", "--porcelain"], capture_output=True
        )

        worktrees: list[WorktreeInfo] = []
        current_worktree: dict[str, Any] = {}

        for line in output.splitlines():
            line = line.strip()
            if not line:
                if current_worktree:
                    # Process completed worktree entry
                    branch = current_worktree.get("branch")
                    if branch and branch.startswith("refs/heads/"):
                        branch = branch[11:]

                    worktree_info = WorktreeInfo(
                        path=Path(current_worktree["worktree"]),
                        commit=current_worktree["HEAD"],
                        branch=branch,
                        is_locked=current_worktree.get("locked", False),
                        is_prunable=current_worktree.get("prunable", False),
                        lock_reason=current_worktree.get("reason"),
                    )
                    worktrees.append(worktree_info)
                    current_worktree = {}
                continue

            if line.startswith("worktree "):
                current_worktree["worktree"] = line[9:]
            elif line.startswith("HEAD "):
                current_worktree["HEAD"] = line[5:]
            elif line.startswith("branch "):
                current_worktree["branch"] = line[7:]
            elif line.startswith("locked"):
                current_worktree["locked"] = True
                if " " in line:
                    current_worktree["reason"] = line.split(" ", 1)[1]
            elif line.startswith("prunable"):
                current_worktree["prunable"] = True
                if " " in line:
                    current_worktree["reason"] = line.split(" ", 1)[1]

        # Handle last worktree if file doesn't end with blank line
        if current_worktree:
            branch = current_worktree.get("branch")
            if branch and branch.startswith("refs/heads/"):
                branch = branch[11:]

            worktree_info = WorktreeInfo(
                path=Path(current_worktree["worktree"]),
                commit=current_worktree["HEAD"],
                branch=branch,
                is_locked=current_worktree.get("locked", False),
                is_prunable=current_worktree.get("prunable", False),
                lock_reason=current_worktree.get("reason"),
            )
            worktrees.append(worktree_info)

        return worktrees

    async def create_worktree(
        self,
        branch: str,
        path: Path | str,
        base_branch: str | None = None,
        *,
        force: bool = False,
        on_progress: ProgressCallback | None = None,
    ) -> WorktreeInfo:
        """Create a new worktree.

        Args:
            branch: Name of the branch for the worktree
            path: Path where the worktree should be created
            base_branch: Base branch to create the new branch from (if branch doesn't exist)
            force: Force creation even if branch exists
            on_progress: Optional callback for progress updates

        Returns:
            WorktreeInfo for the newly created worktree

        Raises:
            WorktreeExistsError: If the worktree or branch already exists
            GitCommandError: If the git command fails

        Example:
            >>> wt = await repo.create_worktree(
            ...     branch="feature/new-ui",
            ...     path="/home/user/project-feature",
            ...     base_branch="main"
            ... )
        """
        worktree_path = Path(path).resolve()

        # Check if worktree path already exists
        if worktree_path.exists():
            raise WorktreeExistsError(path=worktree_path)

        # Build git command
        cmd = ["worktree", "add"]

        if force:
            cmd.append("--force")

        # Check if branch already exists
        branch_exists = await self.branch_exists(branch)

        if branch_exists and not force:
            raise WorktreeExistsError(path=worktree_path, branch=branch)

        if not branch_exists:
            # Create new branch
            cmd.append("-b")
            cmd.append(branch)
            cmd.append(str(worktree_path))
            if base_branch:
                cmd.append(base_branch)
        else:
            # Use existing branch
            cmd.append(str(worktree_path))
            cmd.append(branch)

        # Execute command with optional progress streaming
        if on_progress:
            await self._stream_git_command(cmd, on_progress=on_progress)
        else:
            await self._run_git_in_repo(cmd, capture_output=True)

        # Get worktree info
        worktrees = await self.list_worktrees()
        for worktree in worktrees:
            if worktree.path == worktree_path:
                return worktree

        # Fallback if we can't find it in the list
        return WorktreeInfo(
            path=worktree_path,
            commit="0" * 40,  # Placeholder
            branch=branch,
            is_locked=False,
            is_prunable=False,
        )

    async def delete_worktree(self, path: Path | str, *, force: bool = False) -> None:
        """Delete a worktree.

        Args:
            path: Path to the worktree to delete
            force: Force deletion even if worktree is dirty or locked

        Raises:
            GitCommandError: If the git command fails

        Example:
            >>> await repo.delete_worktree("/home/user/project-feature")
        """
        worktree_path = Path(path).resolve()

        cmd = ["worktree", "remove", str(worktree_path)]
        if force:
            cmd.append("--force")

        await self._run_git_in_repo(cmd, capture_output=True)

    async def prune_worktrees(self) -> None:
        """Prune worktree information for deleted worktrees.

        This removes worktree information for worktrees that have been manually deleted.

        Raises:
            GitCommandError: If the git command fails

        Example:
            >>> await repo.prune_worktrees()
        """
        await self._run_git_in_repo(["worktree", "prune"], capture_output=True)

    async def list_branches(
        self, *, remote: bool = False, all_branches: bool = False
    ) -> list[BranchInfo]:
        """List branches in the repository.

        Args:
            remote: List remote branches instead of local
            all_branches: List both local and remote branches

        Returns:
            List of BranchInfo objects

        Raises:
            GitCommandError: If the git command fails

        Example:
            >>> branches = await repo.list_branches()
            >>> for branch in branches:
            ...     print(f"{branch.name} @ {branch.short_commit}")
        """
        cmd = [
            "for-each-ref",
            "--format=%(refname:short)|%(objectname)|%(upstream:short)|%(HEAD)",
            "refs/heads",
        ]

        if all_branches:
            cmd[-1] = "refs/"
        elif remote:
            cmd[-1] = "refs/remotes"

        output = await self._run_git_in_repo(cmd, capture_output=True)

        branches: list[BranchInfo] = []
        for line in output.splitlines():
            line = line.strip()
            if not line:
                continue

            parts = line.split("|")
            if len(parts) < 4:  # noqa: PLR2004
                continue

            name, commit, upstream, is_head_str = parts

            # Parse HEAD indicator
            is_current = is_head_str == "*"

            # Parse upstream and remote
            upstream_value = upstream if upstream else None
            remote_value = upstream.split("/")[0] if upstream else None

            branch_info = BranchInfo(
                name=name,
                commit=commit,
                remote=remote_value,
                is_current=is_current,
                upstream=upstream_value,
            )
            branches.append(branch_info)

        return branches

    async def create_branch(
        self, branch_name: str, base: str | None = None, *, force: bool = False
    ) -> None:
        """Create a new branch.

        Args:
            branch_name: Name for the new branch
            base: Base commit/branch to create from (defaults to HEAD)
            force: Force creation even if branch exists

        Raises:
            GitCommandError: If the git command fails

        Example:
            >>> await repo.create_branch("feature/new-thing", base="main")
        """
        cmd = ["branch"]
        if force:
            cmd.append("--force")
        cmd.append(branch_name)
        if base:
            cmd.append(base)

        await self._run_git_in_repo(cmd, capture_output=True)

    async def delete_branch(self, branch_name: str, *, force: bool = False) -> None:
        """Delete a branch.

        Args:
            branch_name: Name of the branch to delete
            force: Force deletion even if not fully merged

        Raises:
            BranchNotFoundError: If the branch doesn't exist
            GitCommandError: If the git command fails

        Example:
            >>> await repo.delete_branch("old-feature")
        """
        cmd = ["branch"]
        cmd.append("-D" if force else "-d")
        cmd.append(branch_name)

        try:
            await self._run_git_in_repo(cmd, capture_output=True)
        except GitCommandError as e:
            if "not found" in e.stderr.lower():
                raise BranchNotFoundError(branch_name) from e
            raise

    async def branch_exists(self, branch_name: str) -> bool:
        """Check if a branch exists.

        Args:
            branch_name: Name of the branch to check

        Returns:
            True if the branch exists, False otherwise

        Example:
            >>> if await repo.branch_exists("main"):
            ...     print("Main branch exists")
        """
        try:
            await self._run_git_in_repo(
                ["rev-parse", "--verify", f"refs/heads/{branch_name}"],
                capture_output=True,
            )
            return True
        except GitCommandError:
            return False

    async def fetch_remote(
        self,
        remote: str = "origin",
        refspec: str | None = None,
        *,
        prune: bool = False,
        on_progress: ProgressCallback | None = None,
    ) -> None:
        """Fetch from a remote repository.

        Args:
            remote: Name of the remote to fetch from
            refspec: Optional refspec to fetch
            prune: Remove remote-tracking references that no longer exist
            on_progress: Optional callback for progress updates

        Raises:
            GitCommandError: If the git command fails

        Example:
            >>> await repo.fetch_remote("origin", on_progress=print)
        """
        cmd = ["fetch", "--progress"]
        if prune:
            cmd.append("--prune")
        cmd.append(remote)
        if refspec:
            cmd.append(refspec)

        if on_progress:
            await self._stream_git_command(cmd, on_progress=on_progress)
        else:
            await self._run_git_in_repo(cmd, capture_output=True)

    async def push_remote(
        self,
        remote: str = "origin",
        refspec: str | None = None,
        *,
        force: bool = False,
        set_upstream: bool = False,
        on_progress: ProgressCallback | None = None,
    ) -> None:
        """Push to a remote repository.

        Args:
            remote: Name of the remote to push to
            refspec: Optional refspec to push
            force: Force push
            set_upstream: Set upstream tracking reference
            on_progress: Optional callback for progress updates

        Raises:
            GitCommandError: If the git command fails

        Example:
            >>> await repo.push_remote("origin", "main")
        """
        cmd = ["push", "--progress"]
        if force:
            cmd.append("--force")
        if set_upstream:
            cmd.append("--set-upstream")
        cmd.append(remote)
        if refspec:
            cmd.append(refspec)

        if on_progress:
            await self._stream_git_command(cmd, on_progress=on_progress)
        else:
            await self._run_git_in_repo(cmd, capture_output=True)

    def branch_to_path(self, branch_name: str, base_path: Path | None = None) -> Path:
        """Convert a branch name to a filesystem path.

        This handles patterns like 'user/feature' -> 'repo_root/user/feature'

        Args:
            branch_name: Branch name to convert (e.g., 'ajc/feature')
            base_path: Base path to use (defaults to repository parent)

        Returns:
            Path for the branch worktree

        Example:
            >>> path = repo.branch_to_path("user/feature")
            >>> print(path)
            /home/user/project/user/feature
        """
        if base_path is None:
            base_path = self.root.parent

        # Clean branch name for filesystem
        # Replace potentially problematic characters
        clean_name = branch_name.replace("\\", "/")

        return base_path / clean_name

    async def get_current_branch(self) -> str | None:
        """Get the current branch name.

        Returns:
            Current branch name, or None if HEAD is detached

        Raises:
            GitCommandError: If the git command fails (other than detached HEAD)

        Example:
            >>> branch = await repo.get_current_branch()
            >>> print(f"On branch: {branch}")
        """
        try:
            output = await self._run_git_in_repo(
                ["symbolic-ref", "--short", "HEAD"], capture_output=True
            )
            return output.strip()
        except GitCommandError:
            # HEAD is detached
            return None

    async def get_commit_sha(self, ref: str = "HEAD") -> str:
        """Get the commit SHA for a reference.

        Args:
            ref: Git reference (branch, tag, HEAD, etc.)

        Returns:
            Full commit SHA

        Raises:
            GitCommandError: If the reference is invalid

        Example:
            >>> sha = await repo.get_commit_sha("main")
            >>> print(sha)
        """
        output = await self._run_git_in_repo(["rev-parse", ref], capture_output=True)
        return output.strip()

    async def get_remote_url(self, remote: str = "origin") -> str | None:
        """Get the URL for a remote.

        Args:
            remote: Name of the remote

        Returns:
            Remote URL, or None if remote doesn't exist

        Raises:
            GitCommandError: If the git command fails (other than remote not found)

        Example:
            >>> url = await repo.get_remote_url("origin")
            >>> print(url)
        """
        try:
            output = await self._run_git_in_repo(
                ["remote", "get-url", remote], capture_output=True
            )
            return output.strip()
        except GitCommandError:
            return None

    async def list_remotes(self) -> list[RemoteInfo]:
        """List all remotes and their URLs.

        Returns:
            List of RemoteInfo objects for each remote

        Raises:
            GitCommandError: If the git command fails

        Example:
            >>> remotes = await repo.list_remotes()
            >>> for remote in remotes:
            ...     print(f"{remote.name}: {remote.url}")
        """
        output = await self._run_git_in_repo(["remote", "-v"], capture_output=True)

        remotes_dict: dict[str, dict[str, str]] = {}
        for line in output.splitlines():
            line = line.strip()
            if not line:
                continue

            # Format: "name url (fetch)" or "name url (push)"
            match = re.match(r"^(\S+)\s+(\S+)\s+\((fetch|push)\)$", line)
            if match:
                name, url, operation = match.groups()
                if name not in remotes_dict:
                    remotes_dict[name] = {"name": name, "url": url}

                if operation == "fetch":
                    remotes_dict[name]["fetch_url"] = url
                elif operation == "push":
                    remotes_dict[name]["push_url"] = url

        remotes: list[RemoteInfo] = []
        for remote_data in remotes_dict.values():
            remote_info = RemoteInfo(
                name=remote_data["name"],
                url=remote_data["url"],
                fetch_url=remote_data.get("fetch_url"),
                push_url=remote_data.get("push_url"),
            )
            remotes.append(remote_info)

        return remotes

    async def stream_log(
        self,
        *,
        max_count: int | None = None,
        format_str: str = "%H|%an|%ae|%at|%s",
    ) -> AsyncIterator[dict[str, str]]:
        """Stream git log entries.

        Args:
            max_count: Maximum number of commits to return
            format_str: Git log format string (pipe-separated)

        Yields:
            Dictionary with commit information

        Raises:
            GitCommandError: If the git command fails

        Example:
            >>> async for commit in repo.stream_log(max_count=10):
            ...     print(f"{commit['hash']}: {commit['subject']}")
        """
        cmd = ["log", f"--format={format_str}"]
        if max_count:
            cmd.append(f"--max-count={max_count}")

        cwd = self.root if not self.is_bare else self.git_dir

        # Merge with current environment
        command_env = os.environ.copy()

        process = await asyncio.create_subprocess_exec(
            "git",
            *cmd,
            cwd=cwd,
            stdout=asyncio.subprocess.PIPE,
            stderr=asyncio.subprocess.PIPE,
            env=command_env,
        )

        if process.stdout:
            while True:
                line_bytes = await process.stdout.readline()
                if not line_bytes:
                    break
                line = line_bytes.decode("utf-8", errors="replace").strip()
                if not line:
                    continue

                parts = line.split("|")
                if len(parts) >= 5:  # noqa: PLR2004
                    yield {
                        "hash": parts[0],
                        "author_name": parts[1],
                        "author_email": parts[2],
                        "timestamp": parts[3],
                        "subject": parts[4],
                    }

        returncode = await process.wait()
        if returncode != 0:
            stderr = await process.stderr.read() if process.stderr else b""
            stderr_str = stderr.decode("utf-8", errors="replace")
            raise GitCommandError(
                command=["git", *cmd],
                returncode=returncode,
                stderr=stderr_str,
            )

    async def get_worktree_for_branch(self, branch_name: str) -> Path | None:
        """Get the worktree path for a branch, if any.

        Args:
            branch_name: Name of the branch

        Returns:
            Path to the worktree using this branch, or None

        Raises:
            GitCommandError: If the git command fails

        Example:
            >>> path = await repo.get_worktree_for_branch("feature/new-ui")
            >>> if path:
            ...     print(f"Branch is checked out at: {path}")
        """
        worktrees = await self.list_worktrees()
        for worktree in worktrees:
            if worktree.branch == branch_name:
                return worktree.path
        return None

    async def is_clean(self) -> bool:
        """Check if the working tree is clean (no uncommitted changes).

        Returns:
            True if the working tree is clean, False otherwise

        Raises:
            GitCommandError: If the git command fails

        Example:
            >>> if await repo.is_clean():
            ...     print("No uncommitted changes")
        """
        if self.is_bare:
            return True

        output = await self._run_git_in_repo(["status", "--porcelain"], capture_output=True)
        return not output.strip()

    def __repr__(self) -> str:
        """Return string representation of the Repository."""
        return f"Repository(root={self.root}, is_bare={self.is_bare})"

    def __str__(self) -> str:
        """Return human-readable string representation."""
        return str(self.repo_info)
