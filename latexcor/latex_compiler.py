import logging
import platform
import re
import shutil
import subprocess
import threading
import time
from concurrent.futures import ThreadPoolExecutor
from dataclasses import dataclass
from pathlib import Path
from typing import Dict, Iterator, List, Literal, Optional, Tuple

from rich.console import Console
from rich.panel import Panel
from rich.progress import BarColumn, Progress, SpinnerColumn, TaskID, TextColumn
from watchdog.events import FileSystemEventHandler
from watchdog.observers import Observer

from latexcor.config import CLEAN_PATHS, CLEAN_UP_EXTENSIONS, WATCH_COOLDOWN
from latexcor.utils import TexFile

console = Console()
logger = logging.getLogger(__name__)

LatexEngine = Literal["xelatex", "pdflatex", "lualatex"]


@dataclass
class CompilationProgress:
    """Tracks LaTeX compilation progress."""

    total_steps: int = 2  # Two passes for packages like lastpage
    current_step: int = 0
    current_phase: str = ""
    errors: List[str] = None

    def __post_init__(self):
        self.errors = []

    def update(self, line: str) -> bool:
        """Updates progress based on LaTeX output."""
        if any(pattern in line for pattern in ["! ", "Error:", "Fatal error"]):
            self.errors.append(line)
            return True
        if "Output written on" in line or "Transcript written on" in line:
            self.current_step += 1
            return True
        return False


class LatexCompiler:
    """LaTeX compiler manager with progress tracking using Podman and Path."""

    # File extensions to clean up (from config.yaml)
    CLEAN_EXTENSIONS = set(CLEAN_UP_EXTENSIONS)

    # Temporary folders to clean up (from config.yaml)
    CLEAN_PATHS = set(CLEAN_PATHS)

    @staticmethod
    def parse_latex_output(output: str) -> Iterator[str]:
        """Parses LaTeX output line by line."""
        for line in output.splitlines():
            line = line.strip()
            if line:
                yield line

    @staticmethod
    def extract_error_context(log_file: Path) -> List[str]:
        """Extracts error context from the log file."""
        error_context = []
        if not log_file.exists():
            return error_context

        try:
            with log_file.open("r", encoding="utf-8", errors="ignore") as f:
                content = f.read()
                # More robust error block extraction
                # Matches starting with ! followed by context until a double newline or end of file
                error_blocks = re.finditer(
                    r"^!(.*?)(?=\n\n|\n!|\Z)", content, re.DOTALL | re.MULTILINE
                )
                for block in error_blocks:
                    error_context.append(block.group(0).strip())
        except Exception as e:
            logger.error(f"Error reading log file: {e}")

        return error_context

    @classmethod
    def clean_aux(cls, path: Path) -> None:
        """Cleans up LaTeX auxiliary files."""
        try:
            for item in path.rglob("*"):
                if item.is_file() and item.suffix in cls.CLEAN_EXTENSIONS:
                    try:
                        item.unlink()
                        logger.debug(f"Deleted: {item}")
                    except Exception as e:
                        logger.warning(f"Unable to delete {item}: {e}")

            # Clean temporary directories (like _minted-*, _markdown_*, etc.)
            # These directories are often not empty, so we use shutil.rmtree
            for clean_path in cls.CLEAN_PATHS:
                for item in path.glob(clean_path):
                    if item.is_dir():
                        try:
                            shutil.rmtree(item, ignore_errors=True)
                            logger.debug(f"Directory deleted: {item}")
                        except Exception as e:
                            logger.warning(f"Unable to delete directory {item}: {e}")
        except Exception as e:
            logger.error(f"Error during cleanup: {e}")

    @staticmethod
    def get_tex_files(path: Path) -> List[TexFile]:
        """Gets all LaTeX files in the given path."""
        try:
            return [
                TexFile(
                    name=file, path=file.parent, time_modification=file.stat().st_mtime
                )
                for file in path.rglob("*.tex")
                # Ignore hidden files (starting with .) and ensure it's a file
                if file.is_file() and not file.name.startswith(".")
            ]
        except Exception as e:
            logger.error(f"Error searching for TeX files: {e}")
            return []

    @classmethod
    def compile_latex(
        cls,
        file: Path,
        latex_engine: str = "xelatex",
        progress: Optional[Progress] = None,
        task_id: Optional[TaskID] = None,
        shell_escape: bool = False,
    ) -> bool:
        """Compiles a LaTeX file with progress bar using Podman and pure Path operations."""
        file = Path(file).resolve()
        log_file = file.with_suffix(".log")
        output_dir = file.parent
        compilation_progress = CompilationProgress()

        if progress is None:
            progress = Progress(
                SpinnerColumn(),
                TextColumn("[bold blue]{task.description}"),
                BarColumn(),
                TextColumn("[progress.percentage]{task.percentage:>3.0f}%"),
                console=console,
            )

        try:
            relative_file = file.name

            # Gestion propre du montage de volume selon l'OS sans altérer les objets Path
            if platform.system() == "Windows":
                # Conversion du chemin absolu Windows au format compatible conteneurs posix (ex: /c/Users/...)
                drive = output_dir.drive.lower().replace(":", "")
                pure_path = output_dir.as_posix().replace(output_dir.drive, "")
                container_mount_path = f"/{drive}{pure_path}"
            else:
                container_mount_path = output_dir.as_posix()
                # Remplacement de os.chmod par la méthode native chmod de Path
                try:
                    output_dir.chmod(0o755)
                except Exception as e:
                    logger.warning(f"Could not change permissions on {output_dir}: {e}")

            # Construction de la commande Podman optimisée pour deux passes
            # On utilise sh -c pour enchaîner les deux appels dans le même conteneur
            shell_flags = "-interaction=nonstopmode"
            if shell_escape:
                shell_flags += " -shell-escape"

            # Double pass command chained with &&
            inner_cmd = f"{latex_engine} {shell_flags} {relative_file} && {latex_engine} {shell_flags} {relative_file}"

            cmd = [
                "podman",
                "run",
                "-i",
                "--rm",
                "-v",
                f"{container_mount_path}:/data:Z",
                "infocornouaille/tools:perso",
                "/bin/sh",
                "-c",
                inner_cmd,
            ]

            with progress:
                if task_id is None:
                    task_id = progress.add_task(f"Compiling {file.name}", total=100)

                # Utilisation de cwd=output_dir au lieu de os.chdir() global
                process = subprocess.Popen(
                    cmd,
                    stdout=subprocess.PIPE,
                    stderr=subprocess.PIPE,
                    text=True,
                    bufsize=1,
                    universal_newlines=True,
                    cwd=output_dir,
                )

                while True:
                    line = process.stdout.readline()
                    if not line and process.poll() is not None:
                        break
                    if compilation_progress.update(line):
                        # On avance la barre de progression en fonction du current_step (max 2)
                        progress.update(
                            task_id,
                            completed=min(compilation_progress.current_step * 50, 100),
                            description=f"[bold blue]{file.name}[/] - Pass {min(compilation_progress.current_step + 1, 2)}/2",
                        )

                return_code = process.wait()
                if return_code != 0 or compilation_progress.errors:
                    error_context = cls.extract_error_context(log_file)
                    console.print("\n[bold red]Compilation errors:[/]")
                    for error in compilation_progress.errors + error_context:
                        console.print(f"[red]{error}[/]")
                    return False

                progress.update(task_id, completed=100)

            return True

        except Exception as e:
            console.print(f"\n[bold red]Unexpected error:[/] {str(e)}")
            return False

        finally:
            cls.clean_aux(output_dir)

    @classmethod
    def compile_all(
        cls,
        files: List[Path],
        latex_engine: LatexEngine = "xelatex",
        shell_escape: bool = False,
    ) -> None:
        """Compiles multiple LaTeX files in parallel with multiple progress bars."""
        with Progress(
            SpinnerColumn(),
            TextColumn("[bold blue]{task.description}"),
            BarColumn(),
            TextColumn("[progress.percentage]{task.percentage:>3.0f}%"),
            console=console,
        ) as progress:
            # Parallel execution using ThreadPoolExecutor
            with ThreadPoolExecutor(max_workers=4) as executor:
                futures = []
                for file in files:
                    task_id = progress.add_task(f"[bold blue]{file.name}", total=100)
                    if TexFile(file, file.parent, file.stat().st_mtime).is_main_file:
                        futures.append(
                            executor.submit(
                                cls.compile_latex,
                                file,
                                latex_engine,
                                progress,
                                task_id,
                                shell_escape=shell_escape,
                            )
                        )
                    else:
                        progress.update(
                            task_id, description=f"[dim]{file.name} (skipped)"
                        )
                        progress.advance(task_id, 100)

                # Wait for all tasks to complete
                for future in futures:
                    future.result()

    @classmethod
    def watch(
        cls,
        path_to_watch: Path,
        latex_engine: LatexEngine = "xelatex",
        shell_escape: bool = False,
    ) -> None:
        """Watch LaTeX files for changes and compile them."""
        # Mutation du paramètre initial en Path propre
        path_to_watch = Path(path_to_watch).resolve()

        class DepthLimitedLatexHandler(FileSystemEventHandler):
            def __init__(self):
                self.last_modified = {}
                self.compilation_lock = {}

            def should_process_path(self, file_path: str) -> bool:
                try:
                    path = Path(file_path)

                    if not path.suffix == ".tex":
                        return False

                    try:
                        path.relative_to(path_to_watch)
                    except ValueError:
                        return False

                    depth = len(path.relative_to(path_to_watch).parts)
                    return depth <= 2

                except Exception as e:
                    logger.error(f"Error checking path depth: {e}")
                    return False

            def schedule_compilation(self, path: Path):
                def delayed_compile():
                    time.sleep(
                        max(0, WATCH_COOLDOWN - (time.time() - self.last_modified.get(path, 0)))
                    )
                    if path.is_file():
                        if TexFile(
                            path, path.parent, path.stat().st_mtime
                        ).is_main_file:
                            relative_path = path.relative_to(path_to_watch)
                            console.print(f"\n[bold blue]Compiling:[/] {relative_path}")
                            cls.compile_latex(
                                path, latex_engine, shell_escape=shell_escape
                            )
                        self.compilation_lock[path] = False

                if not self.compilation_lock.get(path, False):
                    self.compilation_lock[path] = True
                    threading.Thread(target=delayed_compile, daemon=True).start()

            def on_modified(self, event):
                if not event.is_directory and self.should_process_path(event.src_path):
                    path = Path(event.src_path)
                    current_time = time.time()

                    if current_time - self.last_modified.get(path, 0) >= WATCH_COOLDOWN:
                        self.last_modified[path] = current_time
                        self.schedule_compilation(path)
                    else:
                        remaining = WATCH_COOLDOWN - (
                            current_time - self.last_modified.get(path, 0)
                        )
                        logger.debug(
                            f"Skipping compilation, {remaining:.1f} seconds remaining in cooldown"
                        )

        observer = Observer()
        handler = DepthLimitedLatexHandler()
        observer.schedule(handler, str(path_to_watch), recursive=True)

        try:
            console.print(f"[bold green]Watching directory:[/] {path_to_watch}")
            console.print(
                "[bold yellow]Note:[/] Only watching current directory and immediate subdirectories"
            )
            console.print("[dim]Press Ctrl+C to stop watching...[/]")
            observer.start()
            while True:
                time.sleep(1)
        except KeyboardInterrupt:
            console.print("\n[bold yellow]Stopping watch mode...[/]")
            observer.stop()
        finally:
            observer.join()
