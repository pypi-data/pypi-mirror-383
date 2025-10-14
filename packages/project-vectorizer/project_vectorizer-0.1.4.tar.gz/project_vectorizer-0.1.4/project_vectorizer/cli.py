#!/usr/bin/env python3
"""CLI for Project Vectorizer."""

import asyncio
import sys
from pathlib import Path
from typing import Optional

import click
from rich.console import Console
from rich.progress import Progress, SpinnerColumn, TextColumn, BarColumn, TaskProgressColumn
from rich.table import Table
from rich.panel import Panel
from rich import box

from .core.config import Config
from .core.project import ProjectManager
from .vector_mcp.server import MCPServer
from . import __version__

console = Console()


@click.group()
@click.version_option(version=__version__)
@click.option("--verbose", "-v", is_flag=True, help="Enable verbose output")
@click.pass_context
def cli(ctx, verbose: bool):
    """Project Vectorizer - Vectorize and search codebases with AI."""
    ctx.ensure_object(dict)
    ctx.obj["verbose"] = verbose
    if verbose:
        console.print("[dim]Verbose mode enabled[/dim]")


@cli.command()
@click.argument("project_path", type=click.Path(path_type=Path))
@click.option("--name", "-n", default=None, help="Project name")
@click.option("--embedding-model", "-m", default="all-MiniLM-L6-v2", help="Embedding model to use")
@click.option("--embedding-provider", "-p", default="sentence-transformers",
              type=click.Choice(["sentence-transformers", "openai"]), help="Embedding provider")
@click.option("--chunk-size", "-c", default=256, type=int, help="Chunk size in tokens")
@click.option("--chunk-overlap", "-o", default=32, type=int, help="Chunk overlap in tokens")
@click.option("--optimize", is_flag=True, help="Auto-optimize workers and memory settings based on system resources")
@click.pass_context
def init(ctx, project_path: Path, name: Optional[str], embedding_model: str,
         embedding_provider: str, chunk_size: int, chunk_overlap: int, optimize: bool):
    """Initialize a new project for vectorization."""
    verbose = ctx.obj.get("verbose", False)

    try:
        # Create project directory if it doesn't exist
        project_path = Path(project_path)
        if not project_path.exists():
            console.print(f"[yellow]Creating directory: {project_path}[/yellow]")
            project_path.mkdir(parents=True, exist_ok=True)

        # Determine project name
        if not name:
            name = project_path.name

        with Progress(
            SpinnerColumn(),
            TextColumn("[progress.description]{task.description}"),
            console=console,
        ) as progress:
            task = progress.add_task("Initializing project...", total=None)

            # Create config (optimized or standard)
            if optimize:
                console.print("[cyan]Using optimized configuration based on system resources...[/cyan]")
                config = Config.create_optimized(
                    embedding_model=embedding_model,
                    embedding_provider=embedding_provider,
                    chunk_size=chunk_size,
                    chunk_overlap=chunk_overlap
                )
            else:
                config = Config(
                    embedding_model=embedding_model,
                    embedding_provider=embedding_provider,
                    chunk_size=chunk_size,
                    chunk_overlap=chunk_overlap
                )

            # Initialize project
            project_manager = ProjectManager(project_path, config)
            asyncio.run(project_manager.initialize(name))

            progress.update(task, completed=True)

        # Build success message
        success_msg = (
            f"[green]✓[/green] Project initialized successfully!\n\n"
            f"[bold]Name:[/bold] {name}\n"
            f"[bold]Path:[/bold] {project_path}\n"
            f"[bold]Model:[/bold] {embedding_model}\n"
            f"[bold]Provider:[/bold] {embedding_provider}\n"
            f"[bold]Chunk Size:[/bold] {chunk_size} tokens\n"
        )

        # Add optimization details if enabled
        if optimize:
            success_msg += (
                f"\n[bold cyan]Optimized Settings:[/bold cyan]\n"
                f"  • Workers: {config.max_workers}\n"
                f"  • Batch Size: {config.batch_size}\n"
                f"  • Embedding Batch: {config.embedding_batch_size}\n"
                f"  • Memory Monitoring: {'Enabled' if config.memory_monitoring_enabled else 'Disabled'}\n"
                f"  • GC Interval: {config.gc_interval} files\n"
            )

        success_msg += (
            f"\n[dim]Next steps:[/dim]\n"
            f"  • Run [cyan]pv index {project_path}[/cyan] to index the codebase\n"
            f"  • Run [cyan]pv search {project_path} \"your query\"[/cyan] to search"
        )

        console.print(Panel.fit(
            success_msg,
            title="Project Initialized",
            border_style="green"
        ))

    except Exception as e:
        console.print(f"[red]✗ Error initializing project: {e}[/red]")
        if verbose:
            console.print_exception()
        sys.exit(1)


@cli.command()
@click.argument("project_path", type=click.Path(exists=True, path_type=Path))
@click.option("--incremental", "-i", is_flag=True, help="Only index changed files")
@click.option("--smart", "-s", is_flag=True, help="Smart incremental indexing (new/modified/deleted)")
@click.option("--force", "-f", is_flag=True, help="Force re-indexing of all files")
@click.option("--max-resources", is_flag=True, help="Use maximum system resources (auto-detect optimal workers/memory)")
@click.pass_context
def index(ctx, project_path: Path, incremental: bool, smart: bool, force: bool, max_resources: bool):
    """Index the codebase for searching."""
    import time
    verbose = ctx.obj.get("verbose", False)

    try:
        start_time = time.time()
        config = Config.load_from_project(project_path)

        # Override with optimized settings if requested
        if max_resources:
            console.print("[cyan]Using maximum system resources (optimized settings)...[/cyan]")
            optimized = Config.create_optimized()
            # Preserve project-specific settings but override performance settings
            config.max_workers = optimized.max_workers
            config.batch_size = optimized.batch_size
            config.embedding_batch_size = optimized.embedding_batch_size
            config.memory_efficient_search_threshold = optimized.memory_efficient_search_threshold
            config.gc_interval = optimized.gc_interval
            config.memory_monitoring_enabled = optimized.memory_monitoring_enabled

            console.print(f"  • Workers: {config.max_workers}")
            console.print(f"  • Batch Size: {config.batch_size}")
            console.print(f"  • Embedding Batch: {config.embedding_batch_size}")

        project_manager = ProjectManager(project_path, config)

        # Load project
        asyncio.run(project_manager.load())

        mode = "incremental" if incremental else "full"
        if smart:
            mode = "smart incremental"
        if force:
            mode = "forced full"

        with Progress(
            SpinnerColumn(),
            TextColumn("[progress.description]{task.description}"),
            BarColumn(),
            TaskProgressColumn(),
            console=console,
        ) as progress:
            task = progress.add_task(f"Indexing ({mode})...", total=100)

            # Set up progress callback to update the unified progress bar
            def update_progress(current: int, total: int, description: str):
                if total > 0:
                    progress.update(task, completed=current, total=total, description=description)

            project_manager.set_progress_callback(update_progress)

            if smart:
                stats = asyncio.run(project_manager.smart_incremental_index())

                # Calculate elapsed time
                elapsed_time = time.time() - start_time
                time_str = f"{elapsed_time:.2f}s"
                if elapsed_time >= 60:
                    minutes = int(elapsed_time // 60)
                    seconds = int(elapsed_time % 60)
                    time_str = f"{minutes}m {seconds}s"

                # Show detailed stats for smart indexing
                console.print(Panel.fit(
                    f"[green]✓[/green] Smart indexing complete!\n\n"
                    f"[bold cyan]New files:[/bold cyan] {stats['new']}\n"
                    f"[bold yellow]Modified files:[/bold yellow] {stats['modified']}\n"
                    f"[bold red]Deleted files:[/bold red] {stats['deleted']}\n"
                    f"[bold]Time taken:[/bold] {time_str}\n\n"
                    f"[dim]Next:[/dim] [cyan]pv search {project_path} \"your query\"[/cyan]",
                    title="Smart Indexing Complete",
                    border_style="green"
                ))
                return

            elif incremental:
                asyncio.run(project_manager.index_changes())
            else:
                asyncio.run(project_manager.index_all())

        # Get stats
        status = asyncio.run(project_manager.get_status())

        # Calculate elapsed time
        elapsed_time = time.time() - start_time
        time_str = f"{elapsed_time:.2f}s"
        if elapsed_time >= 60:
            minutes = int(elapsed_time // 60)
            seconds = int(elapsed_time % 60)
            time_str = f"{minutes}m {seconds}s"

        console.print(Panel.fit(
            f"[green]✓[/green] Indexing complete!\n\n"
            f"[bold]Files indexed:[/bold] {status['indexed_files']}/{status['total_files']}\n"
            f"[bold]Total chunks:[/bold] {status['total_chunks']}\n"
            f"[bold]Model:[/bold] {status['embedding_model']}\n"
            f"[bold]Time taken:[/bold] {time_str}\n\n"
            f"[dim]You can now search with:[/dim] [cyan]pv search {project_path} \"your query\"[/cyan]",
            title="Indexing Complete",
            border_style="green"
        ))

    except Exception as e:
        console.print(f"[red]✗ Error indexing project: {e}[/red]")
        if verbose:
            console.print_exception()
        sys.exit(1)


@cli.command()
@click.argument("project_path", type=click.Path(exists=True, path_type=Path))
@click.argument("query", type=str)
@click.option("--limit", "-l", default=10, type=int, help="Number of results to return")
@click.option("--threshold", "-t", default=0.3, type=float, help="Similarity threshold (0.0-1.0)")
@click.pass_context
def search(ctx, project_path: Path, query: str, limit: int, threshold: float):
    """Search through the vectorized codebase."""
    verbose = ctx.obj.get("verbose", False)

    try:
        config = Config.load_from_project(project_path)
        project_manager = ProjectManager(project_path, config)

        # Load project
        asyncio.run(project_manager.load())

        with Progress(
            SpinnerColumn(),
            TextColumn("[progress.description]{task.description}"),
            console=console,
        ) as progress:
            task = progress.add_task("Searching...", total=None)

            results = asyncio.run(project_manager.search(query, limit=limit, threshold=threshold))

            progress.update(task, completed=True)

        if not results:
            console.print(f"[yellow]No results found for: {query}[/yellow]")
            console.print(f"[dim]Try lowering the threshold (current: {threshold})[/dim]")
            return

        # Display results
        console.print(f"\n[bold]Search Results for:[/bold] [cyan]{query}[/cyan]")
        console.print(f"[dim]Found {len(results)} result(s) with threshold >= {threshold}[/dim]\n")

        for i, result in enumerate(results, 1):
            similarity_color = "green" if result['similarity'] >= 0.8 else "yellow" if result['similarity'] >= 0.5 else "white"

            console.print(Panel(
                f"[bold]{result['file_path']}[/bold]\n"
                f"[dim]Lines {result.get('start_line', '?')}-{result.get('end_line', '?')} | "
                f"Similarity: [{similarity_color}]{result['similarity']:.3f}[/{similarity_color}][/dim]\n\n"
                f"{result['content'][:300]}{'...' if len(result['content']) > 300 else ''}",
                title=f"Result {i}",
                border_style=similarity_color,
                box=box.ROUNDED
            ))

    except Exception as e:
        console.print(f"[red]✗ Error searching: {e}[/red]")
        if verbose:
            console.print_exception()
        sys.exit(1)


@cli.command()
@click.argument("project_path", type=click.Path(exists=True, path_type=Path))
@click.option("--watch", "-w", is_flag=True, help="Watch for file changes and auto-index")
@click.option("--debounce", "-d", default=2.0, type=float, help="Debounce delay in seconds (default: 2.0)")
@click.pass_context
def sync(ctx, project_path: Path, watch: bool, debounce: float):
    """Sync changes from git or watch for file changes."""
    verbose = ctx.obj.get("verbose", False)

    try:
        config = Config.load_from_project(project_path)
        project_manager = ProjectManager(project_path, config)

        # Load project
        asyncio.run(project_manager.load())

        if watch:
            console.print(f"[cyan]👀 Watching for changes in: {project_path}[/cyan]")
            console.print(f"[dim]Debounce delay: {debounce}s | Press Ctrl+C to stop[/dim]\n")

            try:
                asyncio.run(project_manager.start_watching(debounce_seconds=debounce))
            except KeyboardInterrupt:
                console.print("\n[yellow]Stopped watching[/yellow]")
        else:
            with Progress(
                SpinnerColumn(),
                TextColumn("[progress.description]{task.description}"),
                console=console,
            ) as progress:
                task = progress.add_task("Syncing changes...", total=None)

                asyncio.run(project_manager.sync_changes())

                progress.update(task, completed=True)

            status = asyncio.run(project_manager.get_status())
            console.print(f"[green]✓[/green] Sync complete! "
                         f"({status['indexed_files']}/{status['total_files']} files indexed)")

    except KeyboardInterrupt:
        console.print("\n[yellow]Sync interrupted[/yellow]")
    except Exception as e:
        console.print(f"[red]✗ Error syncing: {e}[/red]")
        if verbose:
            console.print_exception()
        sys.exit(1)


@cli.command(name="index-git")
@click.argument("project_path", type=click.Path(exists=True, path_type=Path))
@click.option("--since", "-s", default="HEAD~1", help="Git reference to compare against (default: HEAD~1)")
@click.option("--max-resources", is_flag=True, help="Use maximum system resources (auto-detect optimal workers/memory)")
@click.pass_context
def index_git(ctx, project_path: Path, since: str, max_resources: bool):
    """
    Index only files changed in git commits.

    Examples:
        pv index-git . --since HEAD~1      # Last commit
        pv index-git . --since HEAD~5      # Last 5 commits
        pv index-git . --since main        # Since main branch
        pv index-git . --since abc123      # Since specific commit
    """
    import time
    verbose = ctx.obj.get("verbose", False)

    try:
        start_time = time.time()
        config = Config.load_from_project(project_path)

        # Override with optimized settings if requested
        if max_resources:
            console.print("[cyan]Using maximum system resources (optimized settings)...[/cyan]")
            optimized = Config.create_optimized()
            config.max_workers = optimized.max_workers
            config.batch_size = optimized.batch_size
            config.embedding_batch_size = optimized.embedding_batch_size
            config.memory_efficient_search_threshold = optimized.memory_efficient_search_threshold
            config.gc_interval = optimized.gc_interval
            config.memory_monitoring_enabled = optimized.memory_monitoring_enabled

            console.print(f"  • Workers: {config.max_workers}")
            console.print(f"  • Batch Size: {config.batch_size}")

        project_manager = ProjectManager(project_path, config)

        # Load project
        asyncio.run(project_manager.load())

        with Progress(
            SpinnerColumn(),
            TextColumn("[progress.description]{task.description}"),
            BarColumn(),
            TaskProgressColumn(),
            console=console,
        ) as progress:
            task = progress.add_task(f"Indexing git changes since {since}...", total=100)

            # Set up progress callback to update the unified progress bar
            def update_progress(current: int, total: int, description: str):
                if total > 0:
                    progress.update(task, completed=current, total=total, description=description)

            project_manager.set_progress_callback(update_progress)

            indexed_count = asyncio.run(project_manager.index_git_changes(since))

        # Calculate elapsed time
        elapsed_time = time.time() - start_time
        time_str = f"{elapsed_time:.2f}s"
        if elapsed_time >= 60:
            minutes = int(elapsed_time // 60)
            seconds = int(elapsed_time % 60)
            time_str = f"{minutes}m {seconds}s"

        if indexed_count == 0:
            console.print(f"[yellow]No files to index since {since}[/yellow]")
        else:
            console.print(Panel.fit(
                f"[green]✓[/green] Git-aware indexing complete!\n\n"
                f"[bold]Files indexed:[/bold] {indexed_count}\n"
                f"[bold]Git reference:[/bold] {since}\n"
                f"[bold]Time taken:[/bold] {time_str}\n\n"
                f"[dim]Indexed only files changed since {since}[/dim]",
                title="Git Indexing Complete",
                border_style="green"
            ))

    except Exception as e:
        console.print(f"[red]✗ Error indexing git changes: {e}[/red]")
        if verbose:
            console.print_exception()
        sys.exit(1)


@cli.command()
@click.argument("project_path", type=click.Path(exists=True, path_type=Path))
@click.pass_context
def status(ctx, project_path: Path):
    """Show project status and statistics."""
    verbose = ctx.obj.get("verbose", False)

    try:
        config = Config.load_from_project(project_path)
        project_manager = ProjectManager(project_path, config)

        # Load project
        asyncio.run(project_manager.load())

        # Get status
        status_info = asyncio.run(project_manager.get_status())

        # Create status table
        table = Table(title="Project Status", box=box.ROUNDED, show_header=False)
        table.add_column("Property", style="cyan", width=20)
        table.add_column("Value", style="white")

        table.add_row("Name", status_info['name'])
        table.add_row("Path", str(status_info['path']))
        table.add_row("Embedding Model", status_info['embedding_model'])
        table.add_row("", "")
        table.add_row("Total Files", str(status_info['total_files']))
        table.add_row("Indexed Files", str(status_info['indexed_files']))
        table.add_row("Total Chunks", str(status_info['total_chunks']))
        table.add_row("", "")

        if status_info.get('git_branch'):
            table.add_row("Git Branch", status_info['git_branch'])

        if status_info.get('last_updated'):
            last_updated = status_info['last_updated']
            if hasattr(last_updated, 'strftime'):
                last_updated_str = last_updated.strftime('%Y-%m-%d %H:%M:%S')
            else:
                last_updated_str = str(last_updated)
            table.add_row("Last Updated", last_updated_str)

        created_at = status_info['created_at']
        if hasattr(created_at, 'strftime'):
            created_at_str = created_at.strftime('%Y-%m-%d %H:%M:%S')
        else:
            created_at_str = str(created_at)
        table.add_row("Created", created_at_str)

        console.print(table)

        # Show indexing progress
        if status_info['indexed_files'] < status_info['total_files']:
            console.print(f"\n[yellow]⚠ {status_info['total_files'] - status_info['indexed_files']} "
                         f"file(s) need indexing[/yellow]")
            console.print(f"[dim]Run: pv index {project_path}[/dim]")
        else:
            console.print(f"\n[green]✓ All files are indexed![/green]")

    except Exception as e:
        console.print(f"[red]✗ Error getting status: {e}[/red]")
        if verbose:
            console.print_exception()
        sys.exit(1)


@cli.command()
@click.argument("project_path", type=click.Path(exists=True, path_type=Path))
@click.option("--port", "-p", default=8000, type=int, help="Port to run MCP server on")
@click.option("--host", "-h", default="localhost", help="Host to bind MCP server to")
@click.pass_context
def serve(ctx, project_path: Path, port: int, host: str):
    """Start MCP server for the project."""
    _serve_project(project_path, host, port)


def _serve_project(project_path: Path, host: str, port: int):
    """Start MCP server (synchronous wrapper)."""
    try:
        config = Config.load_from_project(project_path)
        project_manager = ProjectManager(project_path, config)

        # ProjectManager.load() is async, so run it explicitly once
        asyncio.run(project_manager.load())

        server = MCPServer(project_manager, host, port)

        console.print(Panel.fit(
            f"[bold]MCP Server Starting[/bold]\n\n"
            f"[bold]Host:[/bold] {host}\n"
            f"[bold]Port:[/bold] {port}\n"
            f"[bold]Project:[/bold] {project_path}\n\n"
            f"[dim]Press Ctrl+C to stop[/dim]",
            title="🚀 Server Running",
            border_style="green"
        ))

        # ✅ Now call synchronously
        server.start()

    except KeyboardInterrupt:
        console.print("\n[yellow]🛑 Server stopped[/yellow]")
    except Exception as e:
        console.print(f"[red]✗ Error starting server: {e}[/red]")
        sys.exit(1)


def main():
    """Entry point for the CLI."""
    cli()


if __name__ == "__main__":
    main()
