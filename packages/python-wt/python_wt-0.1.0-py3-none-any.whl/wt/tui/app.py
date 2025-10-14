"""Stunning Textual TUI for the wt package - Git Worktree Manager.

This module provides a beautiful, feature-rich terminal user interface for managing
git worktrees using the Textual framework.
"""

from __future__ import annotations

import asyncio
from pathlib import Path
from typing import TYPE_CHECKING, Any

from textual import on, work
from textual.app import App, ComposeResult
from textual.binding import Binding
from textual.containers import Container, Horizontal, Vertical
from textual.screen import ModalScreen, Screen
from textual.widgets import (
    Button,
    DataTable,
    Footer,
    Header,
    Input,
    Label,
    Static,
)
from wt.core.exceptions import (
    BranchNotFoundError,
    GitCommandError,
    RepositoryNotFoundError,
    WorktreeExistsError,
    WtError,
)
from wt.core.models import WorktreeInfo
from wt.core.repository import Repository

if TYPE_CHECKING:
    from textual.widgets._data_table import RowKey


class StatusBar(Static):
    """Custom status bar showing help text and current state."""

    def __init__(self, message: str = "Ready") -> None:
        """Initialize status bar.

        Args:
            message: Initial status message
        """
        super().__init__(message, id="status-bar")
        self._message = message

    def update_status(self, message: str) -> None:
        """Update the status message.

        Args:
            message: New status message to display
        """
        self._message = message
        self.update(message)


class ConfirmDialog(ModalScreen[bool]):
    """Reusable confirmation modal dialog.

    This modal displays a message and Yes/No buttons, returning True if Yes
    is clicked and False if No is clicked or the dialog is dismissed.
    """

    BINDINGS = [
        Binding("escape", "dismiss(False)", "Cancel", show=False),
        Binding("y", "confirm", "Yes", show=True),
        Binding("n", "dismiss(False)", "No", show=True),
    ]

    def __init__(
        self,
        message: str,
        title: str = "Confirm",
        yes_variant: str = "error",
        no_variant: str = "primary",
    ) -> None:
        """Initialize the confirmation dialog.

        Args:
            message: Message to display in the dialog
            title: Title of the dialog
            yes_variant: Button variant for Yes button
            no_variant: Button variant for No button
        """
        super().__init__()
        self.message = message
        self.title = title
        self.yes_variant = yes_variant
        self.no_variant = no_variant

    def compose(self) -> ComposeResult:
        """Compose the confirmation dialog UI."""
        with Container(id="confirm-dialog"):
            yield Label(self.title, id="confirm-title")
            yield Label(self.message, id="confirm-message")
            with Horizontal(id="confirm-buttons"):
                yield Button("No", variant=self.no_variant, id="no-button")
                yield Button("Yes", variant=self.yes_variant, id="yes-button")

    @on(Button.Pressed, "#yes-button")
    def action_confirm(self) -> None:
        """Handle Yes button press."""
        self.dismiss(True)

    @on(Button.Pressed, "#no-button")
    def action_cancel(self) -> None:
        """Handle No button press."""
        self.dismiss(False)


class CreateWorktreeScreen(ModalScreen[WorktreeInfo | None]):
    """Modal form for creating a new worktree.

    Allows users to specify branch name, optional path, and base branch
    with validation and progress indication during creation.
    """

    BINDINGS = [
        Binding("escape", "dismiss(None)", "Cancel", show=False),
        Binding("ctrl+s", "submit", "Create", show=True),
    ]

    def __init__(self, repository: Repository) -> None:
        """Initialize the create worktree screen.

        Args:
            repository: Repository instance for git operations
        """
        super().__init__()
        self.repository = repository

    def compose(self) -> ComposeResult:
        """Compose the create worktree form UI."""
        with Container(id="create-dialog"):
            yield Label("Create New Worktree", id="create-title")
            with Vertical(id="create-form"):
                yield Label("Branch Name *")
                yield Input(
                    placeholder="feature/awesome-feature",
                    id="branch-input",
                )
                yield Label("Worktree Path (optional)")
                yield Input(
                    placeholder="Leave empty for default",
                    id="path-input",
                )
                yield Label("Base Branch (optional)")
                yield Input(
                    placeholder="main",
                    id="base-branch-input",
                )
                yield Label("", id="create-error")
            with Horizontal(id="create-buttons"):
                yield Button("Cancel", variant="default", id="cancel-button")
                yield Button("Create", variant="success", id="create-button")

    def on_mount(self) -> None:
        """Focus the branch input when the screen mounts."""
        self.query_one("#branch-input", Input).focus()

    @on(Button.Pressed, "#cancel-button")
    def action_cancel(self) -> None:
        """Handle cancel button press."""
        self.dismiss(None)

    @on(Button.Pressed, "#create-button")
    def action_submit(self) -> None:
        """Handle create button press and start worktree creation."""
        branch_input = self.query_one("#branch-input", Input)
        path_input = self.query_one("#path-input", Input)
        base_input = self.query_one("#base-branch-input", Input)
        error_label = self.query_one("#create-error", Label)

        branch_name = branch_input.value.strip()
        worktree_path = path_input.value.strip()
        base_branch = base_input.value.strip()

        # Validation
        error_label.update("")
        if not branch_name:
            error_label.update("[red]Branch name is required[/]")
            branch_input.focus()
            return

        # Validate branch name format
        invalid_chars = [" ", "~", "^", ":", "?", "*", "[", "\\", ".."]
        for char in invalid_chars:
            if char in branch_name:
                error_label.update(f"[red]Branch name cannot contain '{char}'[/]")
                branch_input.focus()
                return

        # Determine path
        if not worktree_path:
            # Default: create in parent directory of repository
            repo_parent = self.repository.root.parent
            worktree_path = str(repo_parent / branch_name.replace("/", "-"))

        # Start async creation
        self._create_worktree(branch_name, worktree_path, base_branch)

    @work(exclusive=True, thread=False)
    async def _create_worktree(
        self, branch_name: str, worktree_path: str, base_branch: str
    ) -> None:
        """Create worktree asynchronously with progress indication.

        Args:
            branch_name: Name of the branch to create/checkout
            worktree_path: Path where worktree will be created
            base_branch: Optional base branch to branch from
        """
        error_label = self.query_one("#create-error", Label)
        create_button = self.query_one("#create-button", Button)

        try:
            # Disable button and show progress
            create_button.disabled = True
            error_label.update("[yellow]Creating worktree...[/]")

            # Create the worktree
            worktree = await self.repository.create_worktree(
                branch=branch_name,
                path=worktree_path,
                base_branch=base_branch if base_branch else None,
                force=False,
            )

            # Success
            self.dismiss(worktree)

        except WorktreeExistsError as e:
            error_label.update(f"[red]Error: {e.message}[/]")
            create_button.disabled = False
        except BranchNotFoundError as e:
            error_label.update(f"[red]Error: {e.message}[/]")
            create_button.disabled = False
        except GitCommandError as e:
            error_label.update(f"[red]Git error: {e.stderr[:100]}[/]")
            create_button.disabled = False
        except WtError as e:
            error_label.update(f"[red]Error: {e}[/]")
            create_button.disabled = False


class MainScreen(Screen[None]):
    """Main screen showing worktrees in a beautiful DataTable.

    Features:
    - Keyboard navigation (j/k, arrows, Enter to select)
    - Actions: Create, Delete, Sync, Refresh, Quit
    - Real-time updates and status display
    """

    BINDINGS = [
        Binding("q", "quit", "Quit", show=True),
        Binding("ctrl+c", "quit", "Quit", show=False),
        Binding("r", "refresh", "Refresh", show=True),
        Binding("ctrl+r", "refresh", "Refresh", show=False),
        Binding("n", "new_worktree", "New", show=True),
        Binding("ctrl+n", "new_worktree", "New", show=False),
        Binding("d", "delete_worktree", "Delete", show=True),
        Binding("ctrl+d", "delete_worktree", "Delete", show=False),
        Binding("j", "cursor_down", "Down", show=False),
        Binding("k", "cursor_up", "Up", show=False),
        Binding("enter", "select_worktree", "Open", show=True),
    ]

    def __init__(self, repository: Repository) -> None:
        """Initialize the main screen.

        Args:
            repository: Repository instance for git operations
        """
        super().__init__()
        self.repository = repository
        self.worktrees: list[WorktreeInfo] = []
        self.row_to_worktree: dict[RowKey, WorktreeInfo] = {}

    def compose(self) -> ComposeResult:
        """Compose the main screen UI."""
        yield Header(show_clock=True)
        with Container(id="main-container"):
            yield Label(f"Repository: {self.repository.root}", id="repo-label")
            yield DataTable(id="worktree-table", zebra_stripes=True, cursor_type="row")
        yield StatusBar("Press 'n' to create new worktree, 'd' to delete, 'r' to refresh")
        yield Footer()

    def on_mount(self) -> None:
        """Set up the data table when screen mounts."""
        table = self.query_one(DataTable)
        table.add_columns("Branch", "Path", "Commit", "Status")
        table.focus()

        # Load worktrees
        self.refresh_worktrees()

    def action_cursor_down(self) -> None:
        """Move cursor down in table."""
        table = self.query_one(DataTable)
        table.action_cursor_down()

    def action_cursor_up(self) -> None:
        """Move cursor up in table."""
        table = self.query_one(DataTable)
        table.action_cursor_up()

    def action_select_worktree(self) -> None:
        """Handle Enter key on selected worktree."""
        table = self.query_one(DataTable)
        if table.cursor_row is not None:
            row_key = table.get_row_at(table.cursor_row)[0]
            if row_key in self.row_to_worktree:
                worktree = self.row_to_worktree[row_key]
                status = self.query_one(StatusBar)
                status.update_status(f"Selected: {worktree.path}")

    def action_refresh(self) -> None:
        """Refresh the worktree list."""
        status = self.query_one(StatusBar)
        status.update_status("Refreshing worktrees...")
        self.refresh_worktrees()

    def action_new_worktree(self) -> None:
        """Show the create worktree dialog."""
        self.app.push_screen(
            CreateWorktreeScreen(self.repository),
            self._handle_worktree_created,
        )

    async def _handle_worktree_created(self, worktree: WorktreeInfo | None) -> None:
        """Handle worktree creation result.

        Args:
            worktree: Created worktree info or None if cancelled
        """
        if worktree is not None:
            status = self.query_one(StatusBar)
            status.update_status(f"Created worktree at {worktree.path}")
            self.refresh_worktrees()

    def action_delete_worktree(self) -> None:
        """Delete the currently selected worktree."""
        table = self.query_one(DataTable)
        if table.cursor_row is None:
            status = self.query_one(StatusBar)
            status.update_status("No worktree selected")
            return

        # Get selected worktree
        cursor_row = table.cursor_row
        if cursor_row >= len(table.rows):
            return

        # Find worktree by cursor position
        row_keys = list(table.rows.keys())
        if cursor_row >= len(row_keys):
            return

        row_key = row_keys[cursor_row]
        if row_key not in self.row_to_worktree:
            return

        worktree = self.row_to_worktree[row_key]

        # Prevent deleting main worktree
        if worktree.is_main_worktree:
            status = self.query_one(StatusBar)
            status.update_status("Cannot delete main worktree")
            return

        # Show confirmation dialog
        self.app.push_screen(
            ConfirmDialog(
                message=f"Delete worktree at {worktree.path}?",
                title="Confirm Delete",
                yes_variant="error",
            ),
            lambda confirmed: self._handle_delete_confirmed(confirmed, worktree),
        )

    async def _handle_delete_confirmed(
        self, confirmed: bool, worktree: WorktreeInfo
    ) -> None:
        """Handle deletion confirmation.

        Args:
            confirmed: Whether user confirmed deletion
            worktree: Worktree to delete
        """
        if not confirmed:
            return

        status = self.query_one(StatusBar)
        status.update_status(f"Deleting worktree at {worktree.path}...")

        try:
            await self.repository.delete_worktree(worktree.path, force=False)
            status.update_status(f"Deleted worktree at {worktree.path}")
            self.refresh_worktrees()
        except GitCommandError as e:
            status.update_status(f"Error deleting worktree: {e.stderr[:50]}")
        except WtError as e:
            status.update_status(f"Error: {e}")

    @work(exclusive=True, thread=False)
    async def refresh_worktrees(self) -> None:
        """Refresh worktree list from repository."""
        try:
            self.worktrees = await self.repository.list_worktrees()
            self._update_table()

            status = self.query_one(StatusBar)
            status.update_status(f"Loaded {len(self.worktrees)} worktrees")
        except GitCommandError as e:
            status = self.query_one(StatusBar)
            status.update_status(f"Error loading worktrees: {e.stderr[:50]}")
        except WtError as e:
            status = self.query_one(StatusBar)
            status.update_status(f"Error: {e}")

    def _update_table(self) -> None:
        """Update the data table with current worktrees."""
        table = self.query_one(DataTable)
        table.clear()
        self.row_to_worktree.clear()

        for worktree in self.worktrees:
            # Format data
            branch = worktree.display_name
            path = str(worktree.path)
            commit = worktree.short_commit
            status_parts = []
            if worktree.is_locked:
                status_parts.append("[red]Locked[/]")
            if worktree.is_prunable:
                status_parts.append("[yellow]Prunable[/]")
            if worktree.is_main_worktree:
                status_parts.append("[green]Main[/]")
            status = " ".join(status_parts) if status_parts else "[dim]Active[/]"

            # Add row
            row_key = table.add_row(branch, path, commit, status)
            self.row_to_worktree[row_key] = worktree


class WorktreeApp(App[None]):
    """The ultimate git worktree manager TUI.

    A beautiful, feature-rich terminal user interface for managing git worktrees
    with keyboard shortcuts, command palette, and multiple themes.
    """

    CSS_PATH = "app.tcss"
    TITLE = "wt - Git Worktree Manager"
    BINDINGS = [
        Binding("ctrl+p", "command_palette", "Command Palette", show=True),
        Binding("ctrl+t", "toggle_theme", "Toggle Theme", show=True),
    ]

    def __init__(
        self,
        repository: Repository,
        theme: str = "nord",
    ) -> None:
        """Initialize the worktree manager app.

        Args:
            repository: Repository instance to manage
            theme: Theme name (nord, gruvbox, or monokai)
        """
        super().__init__()
        self.repository = repository
        self.current_theme = theme
        self.themes = ["nord", "gruvbox", "monokai"]

    def on_mount(self) -> None:
        """Set up the app when it mounts."""
        self.push_screen(MainScreen(self.repository))
        self._apply_theme(self.current_theme)

    def action_command_palette(self) -> None:
        """Show command palette (future enhancement)."""
        # Placeholder for command palette functionality
        pass

    def action_toggle_theme(self) -> None:
        """Toggle between available themes."""
        current_index = self.themes.index(self.current_theme)
        next_index = (current_index + 1) % len(self.themes)
        self.current_theme = self.themes[next_index]
        self._apply_theme(self.current_theme)

    def _apply_theme(self, theme: str) -> None:
        """Apply a theme to the app.

        Args:
            theme: Theme name to apply
        """
        # Theme application happens via CSS classes
        # This is a placeholder for future theme switching logic
        self.sub_title = f"Theme: {theme.title()}"


async def run_tui(repository_path: Path | str | None = None, theme: str = "nord") -> None:
    """Run the worktree manager TUI.

    Args:
        repository_path: Path to git repository (defaults to current directory)
        theme: Theme name (nord, gruvbox, or monokai)

    Raises:
        RepositoryNotFoundError: If no git repository found at path
    """
    # Discover the repository
    repository = await Repository.discover(path=repository_path)
    app = WorktreeApp(repository=repository, theme=theme)
    app.run()


if __name__ == "__main__":
    asyncio.run(run_tui())
