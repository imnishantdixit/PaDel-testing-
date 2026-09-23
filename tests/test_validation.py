"""
Unit tests for services/validation.py
"""

import pytest
from services.validation import validate_smiles_text, validate_file_upload


class DummyUploadedFile:
    def __init__(self, name: str, content: bytes):
        self.name = name
        self._content = content
        self.size = len(content)

    def getvalue(self) -> bytes:
        return self._content


def test_validate_smiles_text_valid_with_names():
    text = "CCO Ethanol\nCC(=O)O Acetic_Acid"
    is_valid, msg, count, lines, names = validate_smiles_text(text)
    assert is_valid is True
    assert count == 2
    assert len(lines) == 2
    assert names == ["Ethanol", "Acetic_Acid"]


def test_validate_smiles_text_without_names():
    text = "CCO\nc1ccccc1"
    is_valid, msg, count, lines, names = validate_smiles_text(text)
    assert is_valid is True
    assert count == 2
    assert names == ["Molecule_001", "Molecule_002"]


def test_validate_smiles_text_empty():
    is_valid, msg, count, lines, names = validate_smiles_text("   \n  ")
    assert is_valid is False
    assert count == 0
    assert lines == []
    assert names == []


def test_validate_file_upload_smi():
    f = DummyUploadedFile("test.smi", b"CCO Ethanol\nCC(=O)O Acetic_Acid\n")
    is_valid, msg, count, names = validate_file_upload(f)
    assert is_valid is True
    assert count == 2
    assert names == ["Ethanol", "Acetic_Acid"]


def test_validate_file_upload_invalid_ext():
    f = DummyUploadedFile("test.exe", b"binary content")
    is_valid, msg, count, names = validate_file_upload(f)
    assert is_valid is False
    assert "Unsupported file type" in msg
