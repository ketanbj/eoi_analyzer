from pathlib import Path

import pytest

from eoi_analyzer.exceptions import EmptyDocumentError, UnsupportedDocumentError
from eoi_analyzer.utils import extract_text_from_document, iter_document_paths


def test_iter_document_paths_filters_to_pdfs_recursively(tmp_path: Path):
    root_pdf = tmp_path / "root.pdf"
    nested_dir = tmp_path / "nested"
    nested_pdf = nested_dir / "nested.pdf"
    markdown = tmp_path / "notes.md"
    nested_dir.mkdir()
    root_pdf.write_bytes(b"%PDF-placeholder")
    nested_pdf.write_bytes(b"%PDF-placeholder")
    markdown.write_text("not an EoI", encoding="utf-8")

    paths = list(iter_document_paths(tmp_path, extensions={".pdf"}))

    assert sorted(path.name for path in paths) == ["nested.pdf", "root.pdf"]


def test_iter_document_paths_can_be_non_recursive(tmp_path: Path):
    root_pdf = tmp_path / "root.pdf"
    nested_dir = tmp_path / "nested"
    nested_pdf = nested_dir / "nested.pdf"
    nested_dir.mkdir()
    root_pdf.write_bytes(b"%PDF-placeholder")
    nested_pdf.write_bytes(b"%PDF-placeholder")

    paths = list(iter_document_paths(tmp_path, recursive=False, extensions={".pdf"}))

    assert [path.name for path in paths] == ["root.pdf"]


def test_extract_text_from_text_document_normalizes_content(tmp_path: Path):
    document = tmp_path / "eoi.txt"
    document.write_text("first line  \nsecond line\n", encoding="utf-8")

    assert extract_text_from_document(document) == "first line\nsecond line"


def test_extract_text_from_document_rejects_empty_text(tmp_path: Path):
    document = tmp_path / "empty.md"
    document.write_text("\n\n", encoding="utf-8")

    with pytest.raises(EmptyDocumentError):
        extract_text_from_document(document)


def test_extract_text_from_document_rejects_unsupported_extension(tmp_path: Path):
    document = tmp_path / "eoi.csv"
    document.write_text("name,value", encoding="utf-8")

    with pytest.raises(UnsupportedDocumentError):
        extract_text_from_document(document)
