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
        r"""
        Checks if this is a main LaTeX file.
        Reads the beginning and end of the file to locate \documentclass,
        \begin{document} and \end{document} efficiently.
        """
        try:
            read_size = 2048
            file_size = self.name.stat().st_size

            with self.name.open("rb") as f:
                if file_size <= read_size * 2:
                    raw = f.read()
                else:
                    raw = f.read(read_size)
                    f.seek(-read_size, 2)  # seek depuis la fin, propre en mode binaire
                    raw += f.read(read_size)

            content = raw.decode("utf-8", errors="ignore")

            return all(
                tag in content
                for tag in ["\\documentclass", "\\begin{document}", "\\end{document}"]
            )
        except Exception:
            return False
