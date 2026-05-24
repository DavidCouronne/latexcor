from pathlib import Path

import pytest

from latexcor.encoding_converter import EncodingConverter


def test_encoding_detection():
    """Vérifie la détection d'encodage via chardet."""
    # UTF-8
    assert EncodingConverter.detect_encoding("Hélo".encode("utf-8")).lower() == "utf-8"

    # ISO-8859-1 (Latin-1)
    content_latin1 = "L'été à Paris".encode("iso-8859-1")
    detected = EncodingConverter.detect_encoding(content_latin1).lower()
    # chardet peut être imprécis sur de courtes chaînes, on accepte les encodages compatibles
    assert detected in ["iso-8859-1", "windows-1252", "utf-8", "ascii"]


def test_convert_file_to_utf8(tmp_path):
    """Vérifie la conversion physique d'un fichier vers UTF-8."""
    # 1. Créer un fichier en Latin-1
    test_file = tmp_path / "latin1.tex"
    content = "C'est l'été à Paris."
    test_file.write_bytes(content.encode("iso-8859-1"))

    # 2. Convertir
    result = EncodingConverter.convert_file_to_utf8(test_file)
    assert result is True

    # 3. Vérifier le résultat
    new_content = test_file.read_text(encoding="utf-8")
    assert new_content == content


def test_convert_already_utf8(tmp_path):
    """Vérifie qu'un fichier déjà en UTF-8 n'est pas altéré."""
    test_file = tmp_path / "utf8.tex"
    content = "Déjà en UTF-8."
    test_file.write_text(content, encoding="utf-8")

    result = EncodingConverter.convert_file_to_utf8(test_file)
    assert result is True
    assert test_file.read_text(encoding="utf-8") == content
