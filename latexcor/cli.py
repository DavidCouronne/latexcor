from enum import Enum
from pathlib import Path
from typing import Optional

import typer
from rich.console import Console

from .__version__ import __version__
from .encoding_converter import EncodingConverter
from .file_manager import FileManager
from .latex_compiler import LatexCompiler

console = Console()


class LatexEngine(str, Enum):
    XELATEX = "xelatex"
    LUALATEX = "lualatex"


app = typer.Typer(
    name="latexcor",
    help="LaTeX Compiler and File Manager - Automate your LaTeX workflow",
    no_args_is_help=True,
)


def get_version() -> str:
    """Get version from pyproject.toml."""
    return __version__


def get_current_path() -> Path:
    """Get current working directory."""
    return Path.cwd()


@app.command()
def version():
    """Show the application version."""
    console.print(f"[bold blue]latexcor version:[/] {get_version()}")


@app.command()
def clean(
    path: Path = typer.Option(
        None,
        "--path",
        "-p",
        help="Path to clean (defaults to current directory)",
        exists=True,
        dir_okay=True,
        file_okay=False,
    ),
):
    """Clean auxiliary LaTeX files."""
    work_path = path or get_current_path()
    LatexCompiler.clean_aux(work_path)
    console.print(f"[bold green]Cleaned auxiliary files in[/] {work_path}")


@app.command()
def recompile(
    engine: LatexEngine = typer.Option(
        LatexEngine.XELATEX,
        "--engine",
        "-e",
        help="LaTeX engine to use",
    ),
    path: Path = typer.Option(
        None,
        "--path",
        "-p",
        help="Path to process (defaults to current directory)",
        exists=True,
        dir_okay=True,
        file_okay=False,
    ),
    confirm: bool = typer.Option(
        False,
        "--confirm",
        "-c",
        help="Confirm before recompiling each file",
    ),
    shell_escape: bool = typer.Option(
        False,
        "--shell-escape",
        "-s",
        help="Allow LaTeX to run external commands (Warning: Security Risk)",
    ),
):
    """Recompile all LaTeX files."""
    work_path = path or get_current_path()

    if shell_escape:
        console.print(
            "[bold yellow]Warning:[/] -shell-escape is enabled. This allows LaTeX to run external commands."
        )

    tex_files = [
        tex_file.name
        for tex_file in LatexCompiler.get_tex_files(work_path)
        if tex_file.is_main_file
    ]

    with typer.progressbar(tex_files) as progress:
        for file in progress:
            if confirm:
                should_compile = typer.confirm(
                    f"\nDo you want to recompile:\n {file}?\n", default=False
                )
                if not should_compile:
                    continue
            LatexCompiler.compile_latex(file, engine.value, shell_escape=shell_escape)

    LatexCompiler.clean_aux(work_path)
    console.print("[bold green]Recompilation complete[/]")


@app.command()
def convert_utf8(
    path: Path = typer.Option(
        None,
        "--path",
        "-p",
        help="Path to process (defaults to current directory)",
        exists=True,
        dir_okay=True,
        file_okay=False,
    ),
):
    """Convert .tex files to UTF-8."""
    work_path = path or get_current_path()
    EncodingConverter.convert_utf8(work_path)
    console.print("[bold green]UTF-8 conversion complete[/]")


@app.command()
def slugify(
    path: Path = typer.Option(
        None,
        "--path",
        "-p",
        help="Path to process (defaults to current directory)",
        exists=True,
        dir_okay=True,
        file_okay=False,
    ),
    confirm: bool = typer.Option(
        True,
        "--confirm/--no-confirm",
        "-c/-C",
        help="Confirm before renaming each file",
    ),
    preview: bool = typer.Option(
        True,
        "--preview/--no-preview",
        "-v/-V",
        help="Show preview of all changes before processing",
    ),
):
    """Slugify file and directory names."""
    work_path = path or get_current_path()
    FileManager.slugify_files(work_path, confirm=confirm, preview=preview)


@app.command()
def watch(
    engine: LatexEngine = typer.Option(
        LatexEngine.XELATEX,
        "--engine",
        "-e",
        help="LaTeX engine to use",
    ),
    path: Path = typer.Option(
        None,
        "--path",
        "-p",
        help="Path to watch (defaults to current directory)",
        exists=True,
        dir_okay=True,
        file_okay=False,
    ),
    shell_escape: bool = typer.Option(
        False,
        "--shell-escape",
        "-s",
        help="Allow LaTeX to run external commands (Warning: Security Risk)",
    ),
):
    """Watch directory and compile LaTeX files on changes."""
    work_path = path or get_current_path()

    if shell_escape:
        console.print(
            "[bold yellow]Warning:[/] -shell-escape is enabled. This allows LaTeX to run external commands."
        )

    console.print(f"[bold blue]Starting watch mode in[/] {work_path}")
    LatexCompiler.watch(work_path, engine.value, shell_escape=shell_escape)


def main() -> None:
    app()


if __name__ == "__main__":
    main()
