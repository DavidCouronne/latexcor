from pathlib import Path

import pytest

from latexcor.latex_compiler import CompilationProgress, LatexCompiler, TexFile


def test_main_file_detection(tmp_path):
    """Vérifie la détection correcte des fichiers LaTeX principaux."""

    # 1. Cas nominal : Un fichier principal valide
    main_file = tmp_path / "main.tex"
    main_file.write_text(
        "\\documentclass{article}\n\\begin{document}\nHello\n\\end{document}",
        encoding="utf-8",
    )
    tex_main = TexFile(name=main_file, path=tmp_path, time_modification=0.0)
    assert tex_main.is_main_file is True

    # 2. Cas négatif : Un fichier inclus (pas de documentclass)
    include_file = tmp_path / "chapter1.tex"
    include_file.write_text(
        "Ceci est un chapitre sans structure complète.", encoding="utf-8"
    )
    tex_include = TexFile(name=include_file, path=tmp_path, time_modification=0.0)
    assert tex_include.is_main_file is False

    # 3. Cas limite : Fichier vide
    empty_file = tmp_path / "empty.tex"
    empty_file.touch()
    tex_empty = TexFile(name=empty_file, path=tmp_path, time_modification=0.0)
    assert tex_empty.is_main_file is False

    # 4. Cas de sécurité : Fichier binaire ou corrompu
    bin_file = tmp_path / "binary.tex"
    bin_file.write_bytes(b"\xff\xfe\xfd\x00")
    tex_bin = TexFile(name=bin_file, path=tmp_path, time_modification=0.0)
    assert tex_bin.is_main_file is False


@pytest.mark.xfail(
    reason="La détection actuelle ne gère pas les commentaires LaTeX (LOGIC #3)"
)
def test_main_file_detection_comments(tmp_path):
    """Vérifie que les tags commentés ne déclenchent pas la détection (Bug connu)."""
    commented_file = tmp_path / "commented.tex"
    commented_file.write_text(
        "% \\documentclass{article}\n% \\begin{document}\n% \\end{document}\nContenu quelconque.",
        encoding="utf-8",
    )
    tex_commented = TexFile(name=commented_file, path=tmp_path, time_modification=0.0)
    assert tex_commented.is_main_file is False


def test_latex_output_parser():
    """Vérifie que le parser de sortie LaTeX nettoie correctement les lignes."""
    raw_output = "  \nLine 1  \n\n  Line 2\n  "
    parsed = list(LatexCompiler.parse_latex_output(raw_output))
    assert parsed == ["Line 1", "Line 2"]


def test_compilation_progress_logic():
    """Vérifie la détection des étapes et des erreurs dans CompilationProgress."""
    from latexcor.latex_compiler import CompilationProgress

    prog = CompilationProgress()

    # 1. Détection d'erreur
    assert prog.update("! LaTeX Error: File `missing.sty' not found.") is True
    assert len(prog.errors) == 1
    assert "! LaTeX Error" in prog.errors[0]

    # 2. Détection de fin de passe
    assert prog.update("Output written on main.pdf (1 page).") is True
    assert prog.current_step == 1

    # 3. Ligne banale (pas de changement)
    assert prog.update("This is just a log line.") is False
    assert prog.current_step == 1
    assert len(prog.errors) == 1


def test_get_tex_files(tmp_path):
    """Vérifie que get_tex_files trouve les bons fichiers et ignore les autres."""
    # 1. Créer une structure de fichiers complexe
    (tmp_path / "main.tex").touch()
    (tmp_path / "chapter1.tex").touch()
    (tmp_path / "image.png").touch()  # Doit être ignoré
    (
        tmp_path / ".hidden.tex"
    ).touch()  # Doit être ignoré (car rglob "*.tex" ne prend pas les cachés par défaut ou on veut vérifier le comportement)

    subdir = tmp_path / "sections"
    subdir.mkdir()
    (subdir / "intro.tex").touch()
    (subdir / "notes.txt").touch()  # Doit être ignoré

    # 2. Scanner
    files = LatexCompiler.get_tex_files(tmp_path)

    # 3. Vérifier
    assert len(files) == 3
    file_names = {f.name.name for f in files}
    assert "main.tex" in file_names
    assert "chapter1.tex" in file_names
    assert "intro.tex" in file_names
    assert ".hidden.tex" not in file_names

    # 4. Vérifier les types et attributs
    for f in files:
        assert isinstance(f, TexFile)
        assert f.name.suffix == ".tex"
        assert f.path.is_dir()
        assert isinstance(f.time_modification, float)


def test_clean_aux_files(tmp_path):
    """Vérifie que clean_aux supprime les fichiers auxiliaires mais garde les .tex."""
    # 1. Créer des fichiers
    (tmp_path / "main.tex").touch()
    (tmp_path / "main.aux").touch()
    (tmp_path / "main.log").touch()
    (tmp_path / "other.pdf").touch()  # Ne doit pas être supprimé (par défaut)

    # 2. Nettoyer
    LatexCompiler.clean_aux(tmp_path)

    # 3. Vérifier
    assert (tmp_path / "main.tex").exists()
    assert (tmp_path / "other.pdf").exists()
    assert not (tmp_path / "main.aux").exists()
    assert not (tmp_path / "main.log").exists()


def test_clean_aux_directories(tmp_path):
    """Vérifie la suppression des dossiers temporaires (minted, etc.)."""
    # 1. Créer un dossier temporaire avec du contenu
    minted_dir = tmp_path / "_minted-main"
    minted_dir.mkdir()
    (minted_dir / "style.py").touch()

    # 2. Nettoyer
    # Ce test risque d'échouer si le dossier n'est pas vide (rmdir vs rmtree)
    LatexCompiler.clean_aux(tmp_path)

    # 3. Vérifier
    assert not minted_dir.exists()
