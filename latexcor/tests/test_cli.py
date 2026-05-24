import pytest
from typer.testing import CliRunner

from latexcor.__version__ import __version__
from latexcor.cli import app

runner = CliRunner()


def test_cli_version():
    """Vérifie que la commande 'version' retourne la bonne version."""
    result = runner.invoke(app, ["version"])
    assert result.exit_code == 0
    assert __version__ in result.stdout


def test_cli_help():
    """Vérifie que l'aide s'affiche correctement."""
    result = runner.invoke(app, ["--help"])
    assert result.exit_code == 0
    assert "LaTeX Compiler and File Manager" in result.stdout


def test_cli_clean_invalid_path():
    """Vérifie le comportement avec un chemin inexistant."""
    # Note: Typer valide le paramètre 'exists=True' avant d'entrer dans la fonction
    # Les erreurs de validation d'arguments sont envoyées sur stderr par Typer
    result = runner.invoke(
        app, ["clean", "--path", "/tmp/non_existent_directory_12345"]
    )
    assert result.exit_code != 0
    # On vérifie stderr si disponible, sinon result.output (qui combine les deux)
    output = result.stderr if result.stderr else result.output
    assert "does not exist" in output.lower()


def test_cli_no_args_shows_help():
    """Vérifie que lancer sans argument affiche l'aide (no_args_is_help=True)."""
    result = runner.invoke(app)
    assert "Usage: " in result.stdout
