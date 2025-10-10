"""CLI interface for SFTP uploader."""

import asyncio
from pathlib import Path
from typing import Optional

import typer
from rich.console import Console
from rich.progress import (
    Progress,
    SpinnerColumn,
    TextColumn,
    BarColumn,
    TaskProgressColumn,
    TimeRemainingColumn,
)

from .uploader import SFTPUploader, UploadStats

app = typer.Typer(help="Async SFTP uploader with parallel uploads and retry logic")
console = Console()


@app.command()
def upload(
    local_folder: Path = typer.Argument(
        ...,
        help="Local folder to upload",
        exists=True,
        file_okay=False,
        dir_okay=True,
        readable=True,
    ),
    remote_folder: str = typer.Argument(
        ...,
        help="Remote SFTP folder path to upload files to",
    ),
    host: str = typer.Option(
        ...,
        "--host",
        "-h",
        help="SFTP server hostname",
        envvar="SFTP_HOST",
    ),
    port: int = typer.Option(
        22,
        "--port",
        "-p",
        help="SFTP server port",
        envvar="SFTP_PORT",
    ),
    username: str = typer.Option(
        ...,
        "--username",
        "-u",
        help="SFTP username",
        envvar="SFTP_USERNAME",
    ),
    password: Optional[str] = typer.Option(
        None,
        "--password",
        help="SFTP password",
        envvar="SFTP_PASSWORD",
    ),
    key_file: Optional[Path] = typer.Option(
        None,
        "--key-file",
        "-k",
        help="SSH private key file path",
        exists=True,
        file_okay=True,
        dir_okay=False,
        readable=True,
        envvar="SFTP_KEY_FILE",
    ),
    max_workers: int = typer.Option(
        10,
        "--max-workers",
        "-w",
        help="Maximum number of parallel uploads",
        min=1,
        max=50,
    ),
    max_retries: int = typer.Option(
        3,
        "--max-retries",
        "-r",
        help="Maximum number of retries per file",
        min=0,
        max=10,
    ),
    recursive: bool = typer.Option(
        True,
        "--recursive/--no-recursive",
        help="Upload folders recursively",
    ),
) -> None:
    """
    Upload a local folder to SFTP server with parallel async uploads.
    
    The tool will upload all files from the local folder to the remote SFTP folder,
    maintaining the directory structure. Failed uploads are automatically retried.
    
    Example:
        upload-sftp /path/to/local/folder /remote/folder \\
            --host sftp.example.com \\
            --username myuser \\
            --password mypass \\
            --max-workers 20
    """
    # Validate authentication
    if not password and not key_file:
        console.print(
            "[red]Error:[/red] Either --password or --key-file must be provided",
            style="bold",
        )
        raise typer.Exit(1)

    console.print(f"[bold cyan]Starting SFTP Upload[/bold cyan]")
    console.print(f"Local folder: [green]{local_folder}[/green]")
    console.print(f"Remote folder: [green]{remote_folder}[/green]")
    console.print(f"SFTP host: [green]{host}:{port}[/green]")
    console.print(f"Max parallel workers: [green]{max_workers}[/green]")
    console.print(f"Max retries per file: [green]{max_retries}[/green]")
    console.print()

    # Create uploader instance
    uploader = SFTPUploader(
        host=host,
        port=port,
        username=username,
        password=password,
        key_file=str(key_file) if key_file else None,
        max_workers=max_workers,
        max_retries=max_retries,
    )

    # Run upload with progress bar
    try:
        with Progress(
            SpinnerColumn(),
            TextColumn("[progress.description]{task.description}"),
            BarColumn(),
            TaskProgressColumn(),
            TimeRemainingColumn(),
            console=console,
        ) as progress:
            task = progress.add_task("Uploading files...", total=None)

            async def upload_with_progress() -> UploadStats:
                stats = await uploader.upload_folder(
                    local_folder=str(local_folder),
                    remote_folder=remote_folder,
                    recursive=recursive,
                    progress_callback=lambda current, total: progress.update(
                        task, completed=current, total=total
                    ),
                )
                return stats

            stats = asyncio.run(upload_with_progress())

    except KeyboardInterrupt:
        console.print("\n[yellow]Upload cancelled by user[/yellow]")
        raise typer.Exit(1)
    except Exception as e:
        console.print(f"\n[red]Error:[/red] {e}", style="bold")
        raise typer.Exit(1)

    # Print summary
    console.print("\n[bold cyan]Upload Summary[/bold cyan]")
    console.print(f"Total files found: [yellow]{stats.total_files}[/yellow]")
    console.print(f"Successfully uploaded: [green]{stats.successful}[/green]")
    console.print(f"Failed: [red]{stats.failed}[/red]")
    console.print(f"Skipped: [yellow]{stats.skipped}[/yellow]")
    console.print(
        f"Total time: [cyan]{stats.duration:.2f}[/cyan] seconds"
    )

    if stats.failed_files:
        console.print("\n[bold red]Failed Files:[/bold red]")
        for file_path, error in stats.failed_files.items():
            console.print(f"  • {file_path}: [red]{error}[/red]")

    # Exit with error code if there were failures
    if stats.failed > 0:
        raise typer.Exit(1)

    console.print("\n[bold green]✓ Upload completed successfully![/bold green]")


if __name__ == "__main__":
    app()

