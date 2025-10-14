"""Project packaging command."""

import tarfile
import tempfile
import shutil
from pathlib import Path
import click
from rich.console import Console
from rich.panel import Panel
from rich.progress import Progress, SpinnerColumn, TextColumn, BarColumn, TaskProgressColumn

console = Console()


def package_project(project_path: str, output: str = None, version: str = None):
    """Package an agent project for deployment.

    Args:
        project_path: Path to the project directory
        output: Output file path (optional)
        version: Version tag (optional)
    """
    project_dir = Path(project_path).resolve()

    # Validate project exists
    if not project_dir.exists():
        console.print()
        console.print(f"[red]✗[/red] Project directory not found: {project_dir}")
        console.print()
        raise click.Abort()

    # Determine output filename
    if output:
        output_file = Path(output)
    else:
        project_name = project_dir.name
        output_file = Path.cwd() / f"{project_name}.ncp"

    console.print()
    console.print(f"[cyan]Packaging:[/cyan] {project_dir.name}")
    console.print()

    try:
        # Files and directories to include
        include_patterns = [
            "ncp.toml",
            "requirements.txt",
            "apt-requirements.txt",
            "agents/**/*.py",
            "tools/**/*.py",
            "README.md",
        ]

        # Create temporary directory for staging
        with tempfile.TemporaryDirectory() as temp_dir:
            temp_path = Path(temp_dir)
            package_root = temp_path / project_dir.name

            # Copy files to staging area
            files_included = []

            with Progress(
                SpinnerColumn(),
                TextColumn("[progress.description]{task.description}"),
                BarColumn(),
                TaskProgressColumn(),
                console=console
            ) as progress:
                task = progress.add_task("Collecting files...", total=None)

                # Required files
                for pattern in ["ncp.toml", "requirements.txt"]:
                    files = list(project_dir.glob(pattern))
                    for src_file in files:
                        dst_file = package_root / src_file.relative_to(project_dir)
                        dst_file.parent.mkdir(parents=True, exist_ok=True)
                        shutil.copy2(src_file, dst_file)
                        files_included.append(src_file.relative_to(project_dir))

                # Optional files
                for pattern in ["apt-requirements.txt", "README.md"]:
                    files = list(project_dir.glob(pattern))
                    for src_file in files:
                        dst_file = package_root / src_file.relative_to(project_dir)
                        dst_file.parent.mkdir(parents=True, exist_ok=True)
                        shutil.copy2(src_file, dst_file)
                        files_included.append(src_file.relative_to(project_dir))

                # Agent and tool files
                for pattern in ["agents/**/*.py", "tools/**/*.py"]:
                    files = list(project_dir.glob(pattern))
                    for src_file in files:
                        dst_file = package_root / src_file.relative_to(project_dir)
                        dst_file.parent.mkdir(parents=True, exist_ok=True)
                        shutil.copy2(src_file, dst_file)
                        files_included.append(src_file.relative_to(project_dir))

            if not files_included:
                console.print()
                console.print("[red]✗[/red] No files to package")
                console.print()
                raise click.Abort()

            # Show collected files
            console.print("[dim]Files collected:[/dim]")
            for f in files_included[:5]:  # Show first 5
                console.print(f"  [green]✓[/green] {f}")
            if len(files_included) > 5:
                console.print(f"  [dim]... and {len(files_included) - 5} more[/dim]")
            console.print()

            # Create archive
            with Progress(
                SpinnerColumn(),
                TextColumn("[progress.description]{task.description}"),
                console=console
            ) as progress:
                task = progress.add_task("Creating package archive...", total=None)
                with tarfile.open(output_file, "w:gz") as tar:
                    tar.add(package_root, arcname=project_dir.name)

            # Get file size
            file_size = output_file.stat().st_size
            size_kb = file_size / 1024
            size_display = f"{size_kb:.1f} KB" if size_kb < 1024 else f"{size_kb/1024:.1f} MB"

            # Success message
            success_text = f"[green]Package:[/green] {output_file.name}\n"
            success_text += f"[green]Size:[/green]    {size_display}\n"
            success_text += f"[green]Files:[/green]   {len(files_included)}\n\n"
            success_text += f"[dim]Deploy your agent:[/dim]\n"
            success_text += f"  [cyan]ncp deploy {output_file.name}[/cyan]"

            console.print(Panel(
                success_text,
                title="[bold green]✓ Package Ready for Deployment[/bold green]",
                border_style="green"
            ))
            console.print()

    except Exception as e:
        console.print()
        console.print(f"[red]✗[/red] Error packaging project: {e}")
        console.print()
        if output_file.exists():
            output_file.unlink()
        raise click.Abort()
