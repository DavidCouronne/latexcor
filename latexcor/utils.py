from dataclasses import dataclass
from pathlib import Path


@dataclass
class TexFile:
    """Represents a LaTeX file with its metadata."""

    name: Path
    path: Path
    time_modification: float

    @property
    def is_main_file(self) -> bool:
        """
        Checks if this is a main LaTeX file.
        Reads only the first 2048 bytes to optimize performance.
        """
        try:
            # Optimize: read only the beginning of the file
            with self.name.open("r", encoding="utf-8", errors="ignore") as f:
                content = f.read(2048)
            return all(
                tag in content
                for tag in ["\\documentclass", "\\begin{document}", "\\end{document}"]
            )
        except Exception:
            return False
