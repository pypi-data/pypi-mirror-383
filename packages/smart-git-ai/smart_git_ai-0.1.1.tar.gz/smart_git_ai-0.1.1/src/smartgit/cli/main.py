"""Main CLI entry point using Click."""

import sys
from pathlib import Path
from typing import Optional

import click
from rich.console import Console
from rich.panel import Panel
from rich.prompt import Confirm
from rich.syntax import Syntax
from rich.table import Table

from smartgit.core.exceptions import GitAIError, GitRepositoryError, NoChangesError
from smartgit.core.repository import GitRepository
from smartgit.services.commit_generator import CommitMessageGenerator
from smartgit.services.config import get_config_manager
from smartgit.services.hooks import HookManager, HookType
from smartgit.utils.git_helpers import GitUtilities

console = Console()


@click.group()
@click.version_option(package_name="smartgit")
@click.option("-v", "--verbose", is_flag=True, help="Enable verbose output")
@click.pass_context
def cli(ctx: click.Context, verbose: bool) -> None:
    """
    Git AI - AI-powered Git assistant with smart commit messages.

    Generate intelligent commit messages, manage git hooks, and access
    helpful git utilities to improve your development workflow.
    """
    ctx.ensure_object(dict)
    ctx.obj["verbose"] = verbose


@cli.command()
@click.option("-c", "--context", help="Additional context about the changes")
@click.option(
    "--dry-run",
    is_flag=True,
    help="Generate message without committing",
)
@click.option(
    "--hook",
    is_flag=True,
    hidden=True,
    help="Running from git hook",
)
@click.option(
    "--output",
    type=click.Path(),
    help="Output file for commit message (for hooks)",
)
@click.option(
    "--edit/--no-edit",
    default=True,
    help="Open editor to review message",
)
@click.pass_context
def generate(
    ctx: click.Context,
    context: Optional[str],
    dry_run: bool,
    hook: bool,
    output: Optional[str],
    edit: bool,
) -> None:
    """Generate an AI commit message for staged changes."""
    try:
        with console.status("[bold green]Analyzing changes..."):
            repo = GitRepository()
            generator = CommitMessageGenerator(repo)

            commit_message = generator.generate_from_staged(context=context)

        # Format the message
        formatted = commit_message.format(style=generator.config.commit_style)

        if hook and output:
            # Write to file for git hook
            Path(output).write_text(formatted)
            console.print("[green]✓[/green] Generated commit message")
            return

        # Display the message
        console.print("\n[bold cyan]Generated Commit Message:[/bold cyan]")
        console.print(Panel(Syntax(formatted, "text", theme="monokai"), expand=False))

        if commit_message.confidence_score < 0.7:
            console.print(
                f"[yellow]⚠[/yellow]  Low confidence: {commit_message.confidence_score:.0%}"
            )

        if dry_run:
            console.print("\n[dim]Dry run mode - not creating commit[/dim]")
            return

        # Confirm commit
        if edit or Confirm.ask("\nCreate commit with this message?", default=True):
            if edit:
                # Let git handle the editing via EDITOR
                temp_file = Path(".git/COMMIT_EDITMSG")
                temp_file.write_text(formatted)
                console.print("[dim]Opening editor...[/dim]")

                # User will edit in their EDITOR
                import subprocess

                editor = subprocess.run(
                    ["git", "commit", "-e", "-F", str(temp_file)],
                    check=False,
                )
                if editor.returncode == 0:
                    console.print("[green]✓[/green] Commit created")
                else:
                    console.print("[red]✗[/red] Commit cancelled")
            else:
                repo.commit(formatted)
                console.print("[green]✓[/green] Commit created")
        else:
            console.print("[yellow]Commit cancelled[/yellow]")

    except NoChangesError:
        console.print("[yellow]No staged changes to commit[/yellow]")
        console.print("Run: [cyan]git add <files>[/cyan] to stage changes")
        sys.exit(1)
    except GitAIError as e:
        console.print(f"[red]✗ Error:[/red] {e.message}")
        if ctx.obj.get("verbose") and e.details:
            console.print(f"[dim]{e.details}[/dim]")
        sys.exit(1)


@cli.command()
@click.option(
    "--force",
    is_flag=True,
    help="Overwrite existing hooks",
)
def install(force: bool) -> None:
    """Install git hooks for automatic commit message generation."""
    try:
        repo = GitRepository()
        hook_manager = HookManager(repo)

        with console.status("[bold green]Installing hooks..."):
            hook_manager.install_hook(HookType.PREPARE_COMMIT_MSG, force=force)

        console.print("[green]✓[/green] Git hooks installed successfully")
        console.print("\nThe prepare-commit-msg hook will now generate AI commit messages")
        console.print("when you run: [cyan]git commit[/cyan] (without -m)")

    except GitRepositoryError:
        console.print("[red]✗ Error:[/red] Not a git repository")
        sys.exit(1)
    except GitAIError as e:
        console.print(f"[red]✗ Error:[/red] {e.message}")
        sys.exit(1)


@cli.command()
@click.option(
    "--restore",
    is_flag=True,
    help="Restore backed up hooks",
)
def uninstall(restore: bool) -> None:
    """Uninstall git hooks."""
    try:
        repo = GitRepository()
        hook_manager = HookManager(repo)

        hook_manager.uninstall_hook(HookType.PREPARE_COMMIT_MSG, restore_backup=restore)

        console.print("[green]✓[/green] Git hooks uninstalled")

    except GitAIError as e:
        console.print(f"[red]✗ Error:[/red] {e.message}")
        sys.exit(1)


@cli.command()
def status() -> None:
    """Show git status and AI configuration."""
    try:
        repo = GitRepository()
        git_status = repo.get_status()
        repo_info = repo.get_repository_info()
        config = get_config_manager().config
        hook_manager = HookManager(repo)

        # Repository info
        console.print("\n[bold cyan]Repository:[/bold cyan]")
        console.print(f"  Path: {repo_info.root_path}")
        console.print(f"  Branch: {repo_info.current_branch}")
        if repo_info.remote_url:
            console.print(f"  Remote: {repo_info.remote_url}")

        # Git status
        console.print("\n[bold cyan]Status:[/bold cyan]")
        if git_status.is_clean:
            console.print("  [green]✓ Working tree clean[/green]")
        else:
            if git_status.staged_files:
                console.print(f"  Staged files: {len(git_status.staged_files)}")
            if git_status.unstaged_files:
                console.print(f"  Unstaged files: {len(git_status.unstaged_files)}")
            if git_status.untracked_files:
                console.print(f"  Untracked files: {len(git_status.untracked_files)}")

        # Hooks status
        console.print("\n[bold cyan]Hooks:[/bold cyan]")
        installed = hook_manager.list_installed_hooks()
        if installed:
            console.print(f"  [green]✓ Installed:[/green] {', '.join(installed)}")
        else:
            console.print("  [yellow]Not installed[/yellow]")

        # AI configuration
        console.print("\n[bold cyan]AI Configuration:[/bold cyan]")
        console.print(f"  Provider: {config.provider}")
        console.print(f"  Model: {config.model or 'default'}")
        console.print(f"  Style: {config.commit_style}")

    except GitRepositoryError:
        console.print("[red]✗ Error:[/red] Not a git repository")
        sys.exit(1)


@cli.group()
def config() -> None:
    """Manage smartgit configuration."""
    pass


@config.command("set")
@click.argument("key")
@click.argument("value")
@click.option("--global", "is_global", is_flag=True, help="Set global config")
def config_set(key: str, value: str, is_global: bool) -> None:
    """Set a configuration value."""
    try:
        config_manager = get_config_manager()

        config_updates = {key: value}

        if is_global:
            config_manager.save_user_config(config_updates)
            console.print(f"[green]✓[/green] Set global config: {key} = {value}")
        else:
            config_manager.save_repo_config(config_updates)
            console.print(f"[green]✓[/green] Set repo config: {key} = {value}")

    except GitAIError as e:
        console.print(f"[red]✗ Error:[/red] {e.message}")
        sys.exit(1)


@config.command("show")
def config_show() -> None:
    """Show current configuration."""
    try:
        config = get_config_manager().config

        table = Table(title="Git AI Configuration")
        table.add_column("Setting", style="cyan")
        table.add_column("Value", style="green")

        table.add_row("Provider", config.provider)
        table.add_row("Model", config.model or "default")
        table.add_row("Commit Style", config.commit_style)
        table.add_row("Auto Add", str(config.auto_add))
        table.add_row("Hook Enabled", str(config.hook_enabled))
        table.add_row("Max Subject Length", str(config.max_subject_length))

        console.print(table)

    except GitAIError as e:
        console.print(f"[red]✗ Error:[/red] {e.message}")
        sys.exit(1)


@cli.group()
def utils() -> None:
    """Git utility functions."""
    pass


@utils.command("undo")
@click.option(
    "--hard",
    is_flag=True,
    help="Discard changes (default: keep as staged)",
)
def undo_commit(hard: bool) -> None:
    """Undo the last commit."""
    try:
        repo = GitRepository()

        if not Confirm.ask(
            "Undo the last commit?" + (" [red](changes will be lost!)[/red]" if hard else "")
        ):
            return

        repo.undo_last_commit(keep_changes=not hard)
        console.print("[green]✓[/green] Last commit undone")

    except GitAIError as e:
        console.print(f"[red]✗ Error:[/red] {e.message}")
        sys.exit(1)


@utils.command("cleanup")
@click.option("--remote", default="origin", help="Remote name")
def cleanup_branches(remote: str) -> None:
    """Delete local branches that have been merged."""
    try:
        repo = GitRepository()

        deleted = repo.clean_merged_branches(remote=remote)

        if deleted:
            console.print(f"[green]✓[/green] Deleted {len(deleted)} merged branches:")
            for branch in deleted:
                console.print(f"  - {branch}")
        else:
            console.print("[dim]No merged branches to clean up[/dim]")

    except GitAIError as e:
        console.print(f"[red]✗ Error:[/red] {e.message}")
        sys.exit(1)


@utils.command("stale")
@click.option("--days", default=30, help="Days to consider a branch stale")
def find_stale(days: int) -> None:
    """Find stale branches that haven't been updated recently."""
    try:
        repo = GitRepository()
        utils_service = GitUtilities(repo)

        stale = utils_service.find_stale_branches(days=days)

        if stale:
            table = Table(title=f"Branches not updated in {days} days")
            table.add_column("Branch", style="cyan")
            table.add_column("Last Updated", style="yellow")

            for branch in stale:
                last_updated = (
                    branch.last_commit_date.strftime("%Y-%m-%d")
                    if branch.last_commit_date
                    else "Unknown"
                )
                table.add_row(branch.name, last_updated)

            console.print(table)
        else:
            console.print("[dim]No stale branches found[/dim]")

    except GitAIError as e:
        console.print(f"[red]✗ Error:[/red] {e.message}")
        sys.exit(1)


@utils.command("large-files")
@click.option("--size", default=10.0, help="Size threshold in MB")
def find_large(size: float) -> None:
    """Find large files in the repository."""
    try:
        repo = GitRepository()
        utils_service = GitUtilities(repo)

        large = utils_service.find_large_files(size_mb=size)

        if large:
            table = Table(title=f"Files larger than {size} MB")
            table.add_column("File", style="cyan")
            table.add_column("Size (MB)", style="yellow", justify="right")

            for file_path, file_size in large:
                table.add_row(str(file_path), f"{file_size:.2f}")

            console.print(table)
        else:
            console.print(f"[dim]No files larger than {size} MB[/dim]")

    except GitAIError as e:
        console.print(f"[red]✗ Error:[/red] {e.message}")
        sys.exit(1)


@utils.command("suggest-gitignore")
def suggest_gitignore() -> None:
    """Suggest .gitignore entries based on untracked files."""
    try:
        repo = GitRepository()
        utils_service = GitUtilities(repo)

        suggestions = utils_service.suggest_gitignore_entries()

        if suggestions:
            console.print("[bold cyan]Suggested .gitignore entries:[/bold cyan]\n")
            for suggestion in suggestions:
                console.print(f"  {suggestion}")

            if Confirm.ask("\nAdd these to .gitignore?"):
                gitignore = repo.root_path / ".gitignore"
                existing = gitignore.read_text() if gitignore.exists() else ""

                with open(gitignore, "a") as f:
                    if existing and not existing.endswith("\n"):
                        f.write("\n")
                    f.write("\n# Added by smartgit\n")
                    for suggestion in suggestions:
                        f.write(f"{suggestion}\n")

                console.print("[green]✓[/green] Updated .gitignore")
        else:
            console.print("[dim]No suggestions[/dim]")

    except GitAIError as e:
        console.print(f"[red]✗ Error:[/red] {e.message}")
        sys.exit(1)


if __name__ == "__main__":
    cli()
