import pytest
from pathlib import Path
from latexcor.file_manager import FileManager
from latexcor.latex_compiler import LatexCompiler
from latexcor.utils import TexFile

def test_extract_error_context_robustness(tmp_path):
    """Vérifie que extract_error_context capture correctement différents formats d'erreurs."""
    log_file = tmp_path / "test.log"
    log_content = r"""
This is some header
! Undefined control sequence.
l.5 \invalidcommand
                   
Some other text

! LaTeX Error: File `missing.sty' not found.

Type X to quit or <RETURN> to proceed,
(aka magic message)

! Another error without line number
Still part of the error
"""
    log_file.write_text(log_content, encoding="utf-8")
    
    errors = LatexCompiler.extract_error_context(log_file)
    
    assert len(errors) == 3
    assert "! Undefined control sequence." in errors[0]
    assert "\\invalidcommand" in errors[0]
    assert "! LaTeX Error: File `missing.sty' not found." in errors[1]
    assert "! Another error without line number" in errors[2]
    assert "Still part of the error" in errors[2]

def test_slugify_conflict(tmp_path):
    """Vérifie que slugify_file gère les conflits de nommage."""
    # Créer deux fichiers
    file1 = tmp_path / "Hello World.tex"
    file1.write_text("content1")
    
    file2 = tmp_path / "hello-world.tex"
    file2.write_text("content2")
    
    # Tenter de slugifier file1, ce qui devrait donner hello-world.tex
    # Le fichier cible existe déjà, donc il ne doit pas être renommé.
    new_path = FileManager.slugify_file(file1, confirm=False)
    
    assert new_path == file1
    assert file1.exists()
    assert file2.exists()
    assert file2.read_text() == "content2"

def test_slugify_success(tmp_path):
    """Vérifie que slugify_file renomme correctement quand il n'y a pas de conflit."""
    file1 = tmp_path / "Hello World.tex"
    file1.write_text("content1")
    
    new_path = FileManager.slugify_file(file1, confirm=False)
    
    assert new_path.name == "hello-world.tex"
    assert not file1.exists()
    assert new_path.exists()

def test_is_main_file_included_chapter(tmp_path):
    """Un fichier inclus via include ne doit pas être compilé."""
    chapter = tmp_path / "intro.tex"
    chapter.write_text(
        "\\section{Introduction}\nSome content here.\n" * 50
    )
    tf = TexFile(chapter, tmp_path, chapter.stat().st_mtime)
    assert tf.is_main_file is False  # pas de \documentclass ni \end{document}

def test_is_main_file_standalone(tmp_path):
    """Un fichier standalone avec son propre documentclass doit être compilé."""
    standalone = tmp_path / "diagram.tex"
    standalone.write_text(
        "\\documentclass[tikz]{standalone}\n"
        "\\begin{document}\n"
        "\\begin{tikzpicture}\\end{tikzpicture}\n"
        "\\end{document}\n"
    )
    tf = TexFile(standalone, tmp_path, standalone.stat().st_mtime)
    assert tf.is_main_file is True

def test_is_main_file_large_document(tmp_path):
    """Régression : end{document} doit être trouvé même sur un grand fichier."""
    padding = "\\section{test} some content\n" * 200  # >> 2048 chars
    large_main = tmp_path / "main.tex"
    large_main.write_text(
        "\\documentclass{article}\n"
        "\\begin{document}\n"
        + padding +
        "\\end{document}\n"
    )
    tf = TexFile(large_main, tmp_path, large_main.stat().st_mtime)
    assert tf.is_main_file is True  # échoue sur la version "fonctionnelle"
