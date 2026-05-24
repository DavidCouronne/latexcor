import pytest

from latexcor.config import CLEAN_PATHS, CLEAN_UP_EXTENSIONS
from latexcor.latex_compiler import LatexCompiler


def test_config_consistency():
    """Vérifie que LatexCompiler utilise les extensions de la configuration."""
    config_extensions = set(CLEAN_UP_EXTENSIONS)
    class_extensions = LatexCompiler.CLEAN_EXTENSIONS

    # Vérification du sous-ensemble (permet à la classe d'en avoir plus si nécessaire,
    # mais pas moins que la config YAML)
    assert config_extensions.issubset(class_extensions)
    assert set(CLEAN_PATHS).issubset(LatexCompiler.CLEAN_PATHS)


def test_config_load():
    """Vérifie que la configuration YAML est chargée correctement."""
    assert isinstance(CLEAN_UP_EXTENSIONS, list)
    assert ".aux" in CLEAN_UP_EXTENSIONS
    assert "minted" in CLEAN_PATHS
