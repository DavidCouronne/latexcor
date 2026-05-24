import logging
from pathlib import Path
from typing import Optional

import chardet
from rich.console import Console

console = Console()
logger = logging.getLogger(__name__)


class EncodingConverter:
    """Handles file encoding conversion operations."""

    @staticmethod
    def detect_encoding(content: bytes) -> str:
        """
        Detect the encoding of file content with a robust fallback strategy.
        1. Try UTF-8 first (it's the most common and safest)
        2. Use chardet for other encodings
        3. Fallback to latin-1 if confidence is low
        """
        # Try UTF-8 first
        try:
            content.decode("utf-8")
            return "utf-8"
        except UnicodeDecodeError:
            pass

        try:
            result = chardet.detect(content)
            encoding = result["encoding"] if result and result["encoding"] else "utf-8"
            confidence = result.get("confidence", 0) if result else 0

            # If confidence is low, try latin-1 as it's common for French/Western European
            if confidence < 0.7:
                logger.warning(
                    f"Low confidence ({confidence}) in detected encoding: {encoding}. Trying latin-1 fallback."
                )
                try:
                    content.decode("iso-8859-1")
                    return "iso-8859-1"
                except UnicodeDecodeError:
                    return "utf-8"

            return encoding
        except Exception as e:
            logger.error(f"Error detecting encoding: {e}")
            return "iso-8859-1"

    @classmethod
    def convert_file_to_utf8(cls, file_path: Path) -> bool:
        """
        Convert a single file to UTF-8 encoding.
        Returns True if conversion was successful.
        """
        try:
            # Read file content in binary mode
            content = file_path.read_bytes()

            # Detect current encoding
            current_encoding = cls.detect_encoding(content)

            # If already UTF-8, skip
            if current_encoding.lower().replace("-", "") == "utf8":
                logger.debug(f"{file_path} is already UTF-8")
                return True

            # Decode content with detected encoding
            text = content.decode(current_encoding)

            # Write content in UTF-8
            file_path.write_text(text, encoding="utf-8")

            console.print(
                f"[green]Converted[/] {file_path.name} from {current_encoding} to UTF-8"
            )
            return True

        except Exception as e:
            logger.error(f"Error converting {file_path}: {e}")
            console.print(f"[bold red]Error converting[/] {file_path.name}: {str(e)}")
            return False

    @classmethod
    def convert_utf8(cls, directory: Path) -> None:
        """
        Convert all .tex files in directory to UTF-8 encoding.
        """
        try:
            # Process all .tex files in directory and subdirectories
            tex_files = list(directory.rglob("*.tex"))

            if not tex_files:
                console.print("[yellow]No .tex files found in directory[/]")
                return

            console.print(
                f"[bold blue]Converting {len(tex_files)} files to UTF-8...[/]"
            )

            success_count = 0
            for file_path in tex_files:
                if cls.convert_file_to_utf8(file_path):
                    success_count += 1

            console.print(
                f"[bold green]Successfully converted {success_count}/{len(tex_files)} files to UTF-8[/]"
            )

        except Exception as e:
            logger.error(f"Error processing directory {directory}: {e}")
            console.print(f"[bold red]Error processing directory:[/] {e}")
