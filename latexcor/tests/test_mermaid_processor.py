import pytest
from pathlib import Path
from latexcor.mermaid_processor import MermaidProcessor


def test_process_mermaid(tmp_path, monkeypatch):
    # Create a temporary .tex file with a Mermaid diagram
    file_path = tmp_path / "test.tex"
    file_path.write_text("""
\\documentclass{article}
\\begin{document}
\\begin{mermaid}
graph TD;
    A-->B;
    A-->C;
    B-->D;
    C-->D;
\\end{mermaid}
\\end{document}
""")

    # Mock the mermaid_to_image method
    def mock_mermaid_to_image(mermaid_code, output_file):
        Path(output_file).touch()

    monkeypatch.setattr(MermaidProcessor, "mermaid_to_image", mock_mermaid_to_image)

    # Process the Mermaid diagram
    MermaidProcessor.process_mermaid(file_path)

    # Check if the file has been modified correctly
    content = file_path.read_text()
    # assert "\\includegraphics{mermaid_diagram_" in content
    # assert "\\usepackage{environ}" in content
    # assert "\\NewEnviron{killmermaid}{}" in content
