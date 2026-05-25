import logging
import re
import unicodedata
from pathlib import Path
from typing import Set

from rich.console import Console
from rich.prompt import Confirm

console = Console()
logger = logging.getLogger(__name__)


class FileManager:
    """Manages file operations including name cleaning and slugification."""

    # Characters to preserve during slugification
    PRESERVED_CHARS: Set[str] = {"-", "_", "."}

    @staticmethod
    def slugify(text: str) -> str:
        """
        Convert text to slug format.
        Example: "Hello World! (2023)" -> "hello-world-2023"
        """
        # Normalize unicode characters
        text = unicodedata.normalize("NFKD", text)

        # Treat apostrophes as word separators by replacing them with spaces
        text = text.replace("'", " ")

        # Keep only ascii characters, preserved chars and spaces (to be replaced later)
        text = "".join(
            c
            for c in text
            if c.isascii()
            and (c.isalnum() or c in FileManager.PRESERVED_CHARS or c.isspace())
        ).strip()

        # Replace spaces and repeated dashes with single dash
        text = re.sub(r"[-\s]+", "-", text)

        # Convert to lowercase and remove leading/trailing dashes
        return text.lower().strip("-")

    @classmethod
    def slugify_file(cls, file_path: Path, confirm: bool = True) -> Path:
        """
        Slugify a file name while preserving its extension.

        Args:
            file_path: Path to the file to slugify
            confirm: Whether to ask for confirmation before renaming

        Returns:
            Path: The new path (even if unchanged)
        """
        # Split name and extension
        stem = file_path.stem
        suffix = file_path.suffix

        # Slugify the name part
        new_stem = cls.slugify(stem)

        # If name hasn't changed, return original path
        if new_stem == stem:
            return file_path

        # Create new path with slugified name
        new_path = file_path.with_name(new_stem + suffix)

        # Handle naming conflicts
        if new_path.exists() and new_path.resolve() != file_path.resolve():
            logger.warning(
                f"Cannot rename {file_path.name} to {new_path.name}: target already exists."
            )
            console.print(
                f"[bold red]Conflict:[/] {new_path.name} already exists. Skipping..."
            )
            return file_path

        try:
            # Show the proposed change
            console.print(f"[yellow]Proposed rename:[/]")
            console.print(f"  From: [blue]{file_path.name}[/]")
            console.print(f"  To:   [green]{new_path.name}[/]")

            # Ask for confirmation if required
            if confirm:
                should_rename = Confirm.ask(
                    "Do you want to rename this file?", default=False
                )
                if not should_rename:
                    console.print("[yellow]Skipping file...[/]")
                    return file_path

            # Rename the file
            file_path.rename(new_path)
            console.print(f"[bold green]Successfully renamed file[/]")
            return new_path

        except Exception as e:
            logger.error(f"Error renaming {file_path}: {e}")
            console.print(f"[bold red]Error:[/] {str(e)}")
            return file_path

    @classmethod
    def slugify_files(
        cls, directory: Path, confirm: bool = True, preview: bool = True
    ) -> None:
        """
        Recursively slugify all file names in a directory.

        Args:
            directory: Directory to process
            confirm: Whether to ask for confirmation for each file
            preview: Whether to show a preview of all changes first
        """
        try:
            # Get all files
            files = list(directory.rglob("*"))
            files = [f for f in files if f.is_file()]

            if not files:
                console.print("[yellow]No files found in directory[/]")
                return

            console.print(f"[bold blue]Found {len(files)} files to process[/]")

            # Preview changes if requested
            if preview:
                console.print("\n[bold]Preview of changes:[/]")
                preview_changes = []
                for file_path in files:
                    new_stem = cls.slugify(file_path.stem)
                    if new_stem != file_path.stem:
                        preview_changes.append(
                            (file_path.name, f"{new_stem}{file_path.suffix}")
                        )

                if not preview_changes:
                    console.print("[yellow]No files need renaming[/]")
                    return

                for old, new in preview_changes:
                    console.print(f"  [blue]{old}[/] → [green]{new}[/]")

                # Ask to continue with the preview
                if not Confirm.ask(
                    "\nDo you want to see these changes in detail?", default=True
                ):
                    console.print("[yellow]Operation cancelled[/]")
                    return

            # Process files
            success_count = 0
            for file_path in files:
                new_path = cls.slugify_file(file_path, confirm=confirm)
                if new_path != file_path:
                    success_count += 1

            if success_count > 0:
                console.print(
                    f"[bold green]Successfully renamed {success_count} files[/]"
                )
            else:
                console.print("[yellow]No files were renamed[/]")

        except Exception as e:
            logger.error(f"Error processing directory {directory}: {e}")
            console.print(f"[bold red]Error processing directory:[/] {str(e)}")
