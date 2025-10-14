"""Beautiful cyclopts-based CLI for the wt package.

This module provides a comprehensive command-line interface for managing git worktrees
with Rich formatting, interactive prompts, and async support.
"""

from __future__ import annotations

import asyncio
import sys
from pathlib import Path
from typing import Annotated, Any

import cyclopts
from pydantic import Field, field_validator
from rich.console import Console
from rich.panel import Panel
from rich.progress import BarColumn, Progress, SpinnerColumn, TextColumn, TimeElapsedColumn
from rich.prompt import Confirm, Prompt
from rich.table import Table

from wt.config import load_config
from wt.core import (
    BranchNotFoundError,
    GitCommandError,
    Repository,
    RepositoryNotFoundError,
    WorktreeExistsError,
    WtError,
)

# Initialize Rich console
console = Console()

# Create the main app
app = cyclopts.App(
    name="wt",
    help="The ultimate git worktree manager with beautiful TUI and modern CLI",
    version="1.0.0",
)


class GlobalOptions:
    """Global options available to all commands.

    Attributes:
        verbose: Enable verbose output with detailed logging
        repo: Path to git repository (defaults to current directory)
        dry_run: Show what would be done without actually doing it
        no_color: Disable colored output
    """

    verbose: Annotated[
        bool,
        Field(description="Enable verbose output"),
    ] = False

    repo: Annotated[
        Path | None,
        Field(description="Path to git repository"),
    ] = None

    dry_run: Annotated[
        bool,
        Field(description="Show what would be done without executing"),
    ] = False

    no_color: Annotated[
        bool,
        Field(description="Disable colored output"),
    ] = False

    @field_validator("repo")
    @classmethod
    def validate_repo_path(cls, v: Path | None) -> Path | None:
        """Validate repository path."""
        if v is not None and not v.exists():
            console.print(f"[red]Error:[/red] Repository path does not exist: {v}")
            sys.exit(1)
        return v


def _get_repository(global_opts: GlobalOptions) -> Repository:
    """Get a Repository instance from global options.

    Args:
        global_opts: Global command options

    Returns:
        Repository instance

    Raises:
        SystemExit: If repository cannot be found
    """
    try:
        repo_path = global_opts.repo or Path.cwd()
        return Repository(repo_path)
    except RepositoryNotFoundError as e:
        console.print(f"[red]Error:[/red] {e}")
        console.print("\n[yellow]Hint:[/yellow] Make sure you're in a git repository or use --repo to specify one")
        sys.exit(1)


def _handle_error(error: Exception, verbose: bool = False) -> None:
    """Handle and display errors consistently.

    Args:
        error: Exception to handle
        verbose: Whether to show detailed error information
    """
    if isinstance(error, WtError):
        console.print(f"[red]Error:[/red] {error}")
        if verbose and isinstance(error, GitCommandError):
            if error.stderr:
                console.print(f"[dim]Git stderr:[/dim] {error.stderr}")
            if error.stdout:
                console.print(f"[dim]Git stdout:[/dim] {error.stdout}")
    else:
        console.print(f"[red]Unexpected error:[/red] {error}")
        if verbose:
            import traceback
            console.print(f"[dim]{traceback.format_exc()}[/dim]")


@app.command
def add(
    branch: Annotated[str | None, cyclopts.Parameter(help="Branch name to checkout")] = None,
    path: Annotated[Path | None, cyclopts.Parameter(help="Path for new worktree")] = None,
    *,
    create: Annotated[bool, cyclopts.Parameter(help="Create new branch")] = False,
    force: Annotated[bool, cyclopts.Parameter(help="Force creation")] = False,
    interactive: Annotated[bool, cyclopts.Parameter(name=["-i", "--interactive"], help="Interactive mode")] = False,
    **global_opts: Any,
) -> None:
    """Create a new git worktree.

    Examples:
        wt add feature-branch ./worktrees/feature
        wt add --create new-feature ./worktrees/new-feature
        wt add -i  # Interactive mode
    """
    globals_obj = GlobalOptions(**global_opts)

    # Handle no-color option
    if globals_obj.no_color:
        console.no_color = True

    try:
        repo = _get_repository(globals_obj)

        # Interactive mode
        if interactive or (branch is None and path is None):
            console.print(Panel.fit(
                "[bold cyan]Create New Worktree[/bold cyan]",
                border_style="cyan",
            ))

            # Get branch name
            if branch is None:
                with Progress(
                    SpinnerColumn(),
                    TextColumn("[progress.description]{task.description}"),
                    transient=True,
                ) as progress:
                    progress.add_task(description="Loading branches...", total=None)
                    branches = asyncio.run(repo.list_branches())

                # Display available branches
                console.print("\n[bold]Available branches:[/bold]")
                for i, b in enumerate(branches[:10], 1):
                    marker = "[green]*[/green]" if b.is_head else " "
                    console.print(f"{marker} {i}. {b.short_name} [dim]({b.short_commit})[/dim]")

                if len(branches) > 10:
                    console.print(f"[dim]...and {len(branches) - 10} more[/dim]")

                branch = Prompt.ask("\n[cyan]Enter branch name[/cyan]")

                if not branch:
                    console.print("[yellow]No branch specified. Aborting.[/yellow]")
                    return

                # Ask if creating new branch
                create = Confirm.ask(f"Create new branch '{branch}'?", default=False)

            # Get path
            if path is None:
                default_path = Path.cwd() / "worktrees" / branch
                path_str = Prompt.ask(
                    "[cyan]Enter worktree path[/cyan]",
                    default=str(default_path),
                )
                path = Path(path_str)

        # Dry run mode
        if globals_obj.dry_run:
            console.print(Panel(
                f"[bold]Would create worktree:[/bold]\n"
                f"  Branch: {branch}\n"
                f"  Path: {path}\n"
                f"  Create branch: {create}\n"
                f"  Force: {force}",
                title="Dry Run",
                border_style="yellow",
            ))
            return

        # Create the worktree
        with Progress(
            SpinnerColumn(),
            TextColumn("[progress.description]{task.description}"),
            BarColumn(),
            TimeElapsedColumn(),
        ) as progress:
            task = progress.add_task(
                description=f"Creating worktree for '{branch}'...",
                total=None,
            )

            try:
                worktree = asyncio.run(
                    repo.create_worktree(
                        path=path,
                        branch=branch,
                        new_branch=branch if create else None,
                        force=force,
                    )
                )
                progress.update(task, completed=True)
            except (WorktreeExistsError, BranchNotFoundError) as e:
                progress.stop()
                _handle_error(e, globals_obj.verbose)
                sys.exit(1)

        # Success message
        console.print(Panel(
            f"[green]Successfully created worktree[/green]\n\n"
            f"[bold]Path:[/bold] {worktree.path}\n"
            f"[bold]Branch:[/bold] {worktree.branch or '(detached)'}\n"
            f"[bold]Commit:[/bold] {worktree.commit[:7]}",
            title="Worktree Created",
            border_style="green",
        ))

    except Exception as e:
        _handle_error(e, globals_obj.verbose)
        sys.exit(1)


@app.command
def list(
    *,
    verbose: Annotated[bool, cyclopts.Parameter(name=["-v", "--verbose"], help="Show detailed information")] = False,
    all: Annotated[bool, cyclopts.Parameter(name=["-a", "--all"], help="Show all worktrees including locked")] = False,
    **global_opts: Any,
) -> None:
    """List all worktrees with beautiful table formatting.

    Examples:
        wt list
        wt list --verbose
        wt list --all
    """
    globals_obj = GlobalOptions(**global_opts)

    # Handle no-color option
    if globals_obj.no_color:
        console.no_color = True

    try:
        repo = _get_repository(globals_obj)

        with Progress(
            SpinnerColumn(),
            TextColumn("[progress.description]{task.description}"),
            transient=True,
        ) as progress:
            progress.add_task(description="Loading worktrees...", total=None)
            worktrees = asyncio.run(repo.list_worktrees())

        if not worktrees:
            console.print("[yellow]No worktrees found.[/yellow]")
            return

        # Filter locked worktrees if not showing all
        if not all:
            worktrees = [wt for wt in worktrees if not wt.is_locked]

        # Create table
        table = Table(
            title="[bold cyan]Git Worktrees[/bold cyan]",
            show_header=True,
            header_style="bold magenta",
            border_style="cyan",
        )

        table.add_column("Path", style="cyan", no_wrap=False)
        table.add_column("Branch", style="green")
        table.add_column("Commit", style="yellow", justify="center")

        if verbose:
            table.add_column("Status", style="blue")

        # Add rows
        for wt in worktrees:
            branch_display = wt.branch or "[dim](detached)[/dim]"
            commit_display = wt.commit[:7] if wt.commit else "?"

            if verbose:
                status_parts = []
                if wt.is_locked:
                    status_parts.append("[red]locked[/red]")
                if wt.is_prunable:
                    status_parts.append("[yellow]prunable[/yellow]")
                status_display = ", ".join(status_parts) if status_parts else "[green]active[/green]"

                table.add_row(
                    str(wt.path),
                    branch_display,
                    commit_display,
                    status_display,
                )
            else:
                table.add_row(
                    str(wt.path),
                    branch_display,
                    commit_display,
                )

        console.print(table)
        console.print(f"\n[dim]Total: {len(worktrees)} worktrees[/dim]")

    except Exception as e:
        _handle_error(e, globals_obj.verbose)
        sys.exit(1)


@app.command
def remove(
    path: Annotated[Path, cyclopts.Parameter(help="Path to worktree to remove")],
    *,
    force: Annotated[bool, cyclopts.Parameter(name=["-f", "--force"], help="Force removal")] = False,
    **global_opts: Any,
) -> None:
    """Remove a git worktree.

    Examples:
        wt remove ./worktrees/feature
        wt remove --force ./worktrees/feature
    """
    globals_obj = GlobalOptions(**global_opts)

    # Handle no-color option
    if globals_obj.no_color:
        console.no_color = True

    try:
        repo = _get_repository(globals_obj)

        # Confirm deletion
        if not force and not globals_obj.dry_run:
            if not Confirm.ask(f"[yellow]Remove worktree at {path}?[/yellow]"):
                console.print("[dim]Aborted.[/dim]")
                return

        # Dry run mode
        if globals_obj.dry_run:
            console.print(Panel(
                f"[bold]Would remove worktree:[/bold]\n"
                f"  Path: {path}\n"
                f"  Force: {force}",
                title="Dry Run",
                border_style="yellow",
            ))
            return

        # Remove the worktree
        with Progress(
            SpinnerColumn(),
            TextColumn("[progress.description]{task.description}"),
            transient=False,
        ) as progress:
            task = progress.add_task(description=f"Removing worktree at {path}...", total=None)
            asyncio.run(repo.remove_worktree(path, force=force))
            progress.update(task, completed=True)

        console.print(f"[green]Successfully removed worktree at {path}[/green]")

    except Exception as e:
        _handle_error(e, globals_obj.verbose)
        sys.exit(1)


@app.command
def checkout(
    branch: Annotated[str, cyclopts.Parameter(help="Branch name to checkout")],
    path: Annotated[Path | None, cyclopts.Parameter(help="Path for worktree")] = None,
    **global_opts: Any,
) -> None:
    """Checkout an existing remote branch in a new worktree.

    This command creates a worktree for an existing branch, typically from a remote.

    Examples:
        wt checkout feature-branch
        wt checkout origin/feature ./worktrees/feature
    """
    globals_obj = GlobalOptions(**global_opts)

    # Handle no-color option
    if globals_obj.no_color:
        console.no_color = True

    try:
        repo = _get_repository(globals_obj)

        # Remove remote prefix if present for local branch name
        local_branch = branch
        if "/" in branch:
            local_branch = branch.split("/", 1)[1]

        # Default path if not specified
        if path is None:
            path = Path.cwd() / "worktrees" / local_branch

        # Dry run mode
        if globals_obj.dry_run:
            console.print(Panel(
                f"[bold]Would checkout branch:[/bold]\n"
                f"  Branch: {branch} -> {local_branch}\n"
                f"  Path: {path}",
                title="Dry Run",
                border_style="yellow",
            ))
            return

        # Create worktree for existing branch
        with Progress(
            SpinnerColumn(),
            TextColumn("[progress.description]{task.description}"),
            transient=False,
        ) as progress:
            task = progress.add_task(
                description=f"Checking out '{branch}'...",
                total=None,
            )

            try:
                worktree = asyncio.run(
                    repo.create_worktree(path=path, branch=branch, new_branch=None, force=False)
                )
                progress.update(task, completed=True)
            except BranchNotFoundError as e:
                progress.stop()
                _handle_error(e, globals_obj.verbose)
                sys.exit(1)

        console.print(Panel(
            f"[green]Successfully checked out branch[/green]\n\n"
            f"[bold]Path:[/bold] {worktree.path}\n"
            f"[bold]Branch:[/bold] {worktree.branch}\n"
            f"[bold]Commit:[/bold] {worktree.commit[:7]}",
            title="Branch Checked Out",
            border_style="green",
        ))

    except Exception as e:
        _handle_error(e, globals_obj.verbose)
        sys.exit(1)


@app.command
def sync(
    branches: Annotated[
        list[str],
        cyclopts.Parameter(help="Branch names to sync (empty = all)"),
    ] = None,
    *,
    prune: Annotated[bool, cyclopts.Parameter(help="Prune deleted branches")] = True,
    fetch_all: Annotated[bool, cyclopts.Parameter(help="Fetch from all remotes")] = False,
    **global_opts: Any,
) -> None:
    """Sync worktrees with remote repository.

    This command fetches changes from the remote and optionally prunes deleted branches.

    Examples:
        wt sync
        wt sync main develop
        wt sync --fetch-all --prune
    """
    globals_obj = GlobalOptions(**global_opts)

    # Handle no-color option
    if globals_obj.no_color:
        console.no_color = True

    try:
        repo = _get_repository(globals_obj)

        # Dry run mode
        if globals_obj.dry_run:
            console.print(Panel(
                f"[bold]Would sync:[/bold]\n"
                f"  Branches: {', '.join(branches) if branches else 'all'}\n"
                f"  Prune: {prune}\n"
                f"  Fetch all: {fetch_all}",
                title="Dry Run",
                border_style="yellow",
            ))
            return

        with Progress(
            SpinnerColumn(),
            TextColumn("[progress.description]{task.description}"),
            BarColumn(),
            TimeElapsedColumn(),
        ) as progress:
            # Fetch from remote
            fetch_task = progress.add_task(
                description="Fetching from remote...",
                total=None,
            )

            if fetch_all:
                asyncio.run(repo.fetch_async(remote="origin", prune=prune, all_remotes=True))
            else:
                asyncio.run(repo.fetch_async(remote="origin", prune=prune, all_remotes=False))

            progress.update(fetch_task, completed=True)

            # If specific branches specified, pull them
            if branches:
                for branch in branches:
                    pull_task = progress.add_task(
                        description=f"Pulling {branch}...",
                        total=None,
                    )
                    try:
                        repo.pull(remote="origin", branch=branch)
                        progress.update(pull_task, completed=True)
                    except GitCommandError as e:
                        progress.update(pull_task, description=f"[red]Failed to pull {branch}[/red]")
                        if globals_obj.verbose:
                            console.print(f"[yellow]Warning:[/yellow] {e}")

        console.print("[green]Successfully synced with remote[/green]")

    except Exception as e:
        _handle_error(e, globals_obj.verbose)
        sys.exit(1)


@app.command
def tui(**global_opts: Any) -> None:
    """Launch the Textual TUI for interactive worktree management.

    The TUI provides a full-screen interactive interface for managing worktrees.

    Examples:
        wt tui
    """
    globals_obj = GlobalOptions(**global_opts)

    try:
        console.print("[yellow]TUI not yet implemented.[/yellow]")
        console.print("The Textual-based TUI will be available in a future version.")
        console.print("\nFor now, use the CLI commands:")
        console.print("  wt add      - Create worktree")
        console.print("  wt list     - List worktrees")
        console.print("  wt remove   - Remove worktree")
        console.print("  wt sync     - Sync with remote")

    except Exception as e:
        _handle_error(e, globals_obj.verbose)
        sys.exit(1)


# Config subcommand group
config_app = cyclopts.App(
    name="config",
    help="Configuration management commands",
)
app.command(config_app)


@config_app.command
def get(
    key: Annotated[str, cyclopts.Parameter(help="Configuration key to retrieve")],
    **global_opts: Any,
) -> None:
    """Get a configuration value.

    Examples:
        wt config get global.base_branch
        wt config get ui.colors
    """
    globals_obj = GlobalOptions(**global_opts)

    # Handle no-color option
    if globals_obj.no_color:
        console.no_color = True

    try:
        repo_path = globals_obj.repo or Path.cwd()
        settings = load_config(repo_root=repo_path)

        # Parse the key (e.g., "global.base_branch")
        parts = key.split(".")
        if len(parts) != 2:
            console.print("[red]Error:[/red] Key must be in format 'section.key' (e.g., 'global.base_branch')")
            sys.exit(1)

        section, setting_key = parts

        # Get the section
        section_obj = getattr(settings, section.replace("global", "global_"), None)
        if section_obj is None:
            console.print(f"[red]Error:[/red] Unknown section: {section}")
            sys.exit(1)

        # Get the value
        value = getattr(section_obj, setting_key, None)
        if value is None:
            console.print(f"[red]Error:[/red] Unknown key: {setting_key} in section {section}")
            sys.exit(1)

        console.print(f"[cyan]{key}[/cyan] = [green]{value}[/green]")

    except Exception as e:
        _handle_error(e, globals_obj.verbose)
        sys.exit(1)


@config_app.command
def set(
    key: Annotated[str, cyclopts.Parameter(help="Configuration key to set")],
    value: Annotated[str, cyclopts.Parameter(help="Value to set")],
    *,
    global_config: Annotated[bool, cyclopts.Parameter(name="--global", help="Set in global config")] = False,
    **global_opts: Any,
) -> None:
    """Set a configuration value.

    Examples:
        wt config set global.base_branch main
        wt config set ui.colors true --global
    """
    globals_obj = GlobalOptions(**global_opts)

    # Handle no-color option
    if globals_obj.no_color:
        console.no_color = True

    try:
        console.print("[yellow]Config set not fully implemented yet.[/yellow]")
        console.print(f"Would set [cyan]{key}[/cyan] = [green]{value}[/green]")
        if global_config:
            console.print("[dim](in global config)[/dim]")

    except Exception as e:
        _handle_error(e, globals_obj.verbose)
        sys.exit(1)


@config_app.command
def show(**global_opts: Any) -> None:
    """Show all configuration values.

    Examples:
        wt config show
    """
    globals_obj = GlobalOptions(**global_opts)

    # Handle no-color option
    if globals_obj.no_color:
        console.no_color = True

    try:
        repo_path = globals_obj.repo or Path.cwd()
        settings = load_config(repo_root=repo_path)

        # Create table for configuration
        table = Table(
            title="[bold cyan]wt Configuration[/bold cyan]",
            show_header=True,
            header_style="bold magenta",
            border_style="cyan",
        )

        table.add_column("Section", style="cyan")
        table.add_column("Key", style="yellow")
        table.add_column("Value", style="green")

        # Global settings
        for key, value in settings.global_.model_dump().items():
            table.add_row("global", key, str(value))

        # UI settings
        for key, value in settings.ui.model_dump().items():
            table.add_row("ui", key, str(value))

        # Performance settings
        for key, value in settings.performance.model_dump().items():
            table.add_row("performance", key, str(value))

        # Logging settings
        for key, value in settings.logging.model_dump().items():
            table.add_row("logging", key, str(value))

        # Git settings
        for key, value in settings.git.model_dump().items():
            table.add_row("git", key, str(value))

        console.print(table)

    except Exception as e:
        _handle_error(e, globals_obj.verbose)
        sys.exit(1)


def main() -> None:
    """Main entry point for the wt CLI application."""
    try:
        app()
    except KeyboardInterrupt:
        console.print("\n[yellow]Interrupted by user[/yellow]")
        sys.exit(130)
    except Exception as e:
        console.print(f"[red]Fatal error:[/red] {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()
