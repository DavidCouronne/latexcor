import pytest

from latexcor.file_manager import FileManager


@pytest.mark.parametrize(
    "input_text, expected",
    [
        ("Hello World", "hello-world"),
        ("L'été à Paris (2024)", "l-ete-a-paris-2024"),
        ("Multiple   Spaces", "multiple-spaces"),
        ("---Already-Slugified---", "already-slugified"),
        ("Special!@#$%^&*()Chars", "specialchars"),
        ("dot.file.name", "dot.file.name"),
        ("undescore_file_name", "undescore_file_name"),
        ("Mixed-Case_With Spaces", "mixed-case_with-spaces"),
        ("  leading and trailing  ", "leading-and-trailing"),
        ("accentué-é-à-ç", "accentue-e-a-c"),
        ("l'oncle d'Amérique", "l-oncle-d-amerique"),
        pytest.param(
            "Complex (Nested) - [Brackets]! .dot",
            "complex-nested-brackets.dot",
            marks=pytest.mark.xfail(reason="Dash before dot not collapsed"),
        ),
        pytest.param(
            "multiple...dots...and---dashes",
            "multiple.dots.and-dashes",
            marks=pytest.mark.xfail(reason="Repeated dots not collapsed"),
        ),
    ],
)
def test_slugify_robustness(input_text, expected):
    """Vérifie que la fonction slugify gère correctement divers cas complexes."""
    assert FileManager.slugify(input_text) == expected
