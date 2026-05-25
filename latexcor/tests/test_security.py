import pytest
from unittest.mock import MagicMock, patch

from latexcor.cli import app
from latexcor.latex_compiler import LatexCompiler
from typer.testing import CliRunner

runner = CliRunner()


@patch("latexcor.latex_compiler.LatexCompiler.compile_latex")
@patch("latexcor.latex_compiler.LatexCompiler.get_tex_files")
@patch("latexcor.latex_compiler.LatexCompiler.clean_aux")
def test_recompile_shell_escape_flag(
    mock_clean, mock_get_files, mock_compile, tmp_path
):
    """Vérifie que le flag --shell-escape est correctement passé au compilateur."""

    # Mock un fichier LaTeX principal
    mock_file = MagicMock()
    mock_file.name = "main.tex"
    mock_file.is_main_file = True
    mock_get_files.return_value = [mock_file]

    # 1. Test sans --shell-escape (par défaut False)
    runner.invoke(app, ["recompile", "--path", str(tmp_path)])
    mock_compile.assert_called_with("main.tex", "xelatex", shell_escape=False)

    # 2. Test avec --shell-escape
    result = runner.invoke(app, ["recompile", "--path", str(tmp_path), "--shell-escape"])
    assert "-shell-escape is enabled" in result.stdout
    mock_compile.assert_called_with("main.tex", "xelatex", shell_escape=True)


@patch("latexcor.latex_compiler.LatexCompiler.watch")
def test_watch_shell_escape_flag(mock_watch, tmp_path):
    """Vérifie que le flag --shell-escape est passé à la commande watch."""

    # 1. Test sans --shell-escape
    runner.invoke(app, ["watch", "--path", str(tmp_path)])
    mock_watch.assert_called_with(tmp_path, "xelatex", shell_escape=False)

    # 2. Test avec --shell-escape
    result = runner.invoke(app, ["watch", "--path", str(tmp_path), "--shell-escape"])
    assert "-shell-escape is enabled" in result.stdout
    mock_watch.assert_called_with(tmp_path, "xelatex", shell_escape=True)


@patch("subprocess.Popen")
@patch("platform.system")
def test_latex_compiler_shell_escape_cmd(mock_system, mock_popen, tmp_path):
    """Vérifie que la commande Podman inclut ou non -shell-escape."""
    mock_system.return_value = "Linux"

    # Mock Popen pour ne pas exécuter podman
    process_mock = MagicMock()
    process_mock.stdout.readline.return_value = ""
    process_mock.poll.return_value = 0
    process_mock.wait.return_value = 0
    mock_popen.return_value = process_mock

    tex_file = tmp_path / "test.tex"
    tex_file.touch()

    # 1. Sans shell_escape
    LatexCompiler.compile_latex(tex_file, shell_escape=False)
    args, _ = mock_popen.call_args
    cmd = args[0]
    # -shell-escape ne doit pas être présent dans la commande shell passée à /bin/sh
    assert "-shell-escape" not in cmd[-1]

    # 2. Avec shell_escape
    LatexCompiler.compile_latex(tex_file, shell_escape=True)
    args, _ = mock_popen.call_args
    cmd = args[0]
    # -shell-escape doit être présent dans la commande shell passée à /bin/sh
    assert "-shell-escape" in cmd[-1]
