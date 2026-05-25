import pytest
from pathlib import Path
from latexcor.file_manager import FileManager
from latexcor.latex_compiler import LatexCompiler

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
