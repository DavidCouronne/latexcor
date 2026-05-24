import pytest

from latexcor.config import CLEAN_PATHS, CLEAN_UP_EXTENSIONS


def test_config_integrity():
    """Vérifie l'intégrité des constantes de configuration chargées."""
    # Vérification des extensions à nettoyer
    assert isinstance(CLEAN_UP_EXTENSIONS, list)
    assert len(CLEAN_UP_EXTENSIONS) > 0
    assert ".aux" in CLEAN_UP_EXTENSIONS
    assert ".log" in CLEAN_UP_EXTENSIONS
    assert (
        ".tex" not in CLEAN_UP_EXTENSIONS
    )  # Sécurité : on ne doit jamais supprimer les sources

    # Vérification des dossiers à nettoyer
    assert isinstance(CLEAN_PATHS, list)
    assert "mermaid" in CLEAN_PATHS
    assert "_minted-*" in CLEAN_PATHS


def test_config_types():
    """Vérifie que les types de données sont corrects pour l'utilisation dans le code."""
    for ext in CLEAN_UP_EXTENSIONS:
        assert isinstance(ext, str)
        assert ext.startswith(".")

    for path in CLEAN_PATHS:
        assert isinstance(path, str)
