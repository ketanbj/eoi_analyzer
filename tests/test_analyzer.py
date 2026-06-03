from pathlib import Path

from eoi_analyzer.analyzer import EOIAnalyzer
from eoi_analyzer.results import DocumentAnalysis


class FolderSelectionAnalyzer(EOIAnalyzer):
    def __init__(self):
        super().__init__("test-key")
        self.seen = []

    def analyze_document(self, document_path, include_letter=False):
        path = Path(document_path)
        self.seen.append((path.name, include_letter))
        return DocumentAnalysis(
            source_path=str(path),
            source_name=path.name,
            text_char_count=0,
            engagement_snapshot="profile",
            recommendation="recommendation",
            project_plan="project plan",
            letter_of_intent="loi" if include_letter else None,
        )


def test_analyze_folder_filters_to_pdfs_and_includes_letters(tmp_path: Path):
    (tmp_path / "first.pdf").write_bytes(b"%PDF-placeholder")
    (tmp_path / "second.pdf").write_bytes(b"%PDF-placeholder")
    (tmp_path / "notes.md").write_text("not selected", encoding="utf-8")

    analyzer = FolderSelectionAnalyzer()
    batch = analyzer.analyze_folder(tmp_path, include_letter=True, extensions={".pdf"})

    assert [analysis.source_name for analysis in batch.analyses] == ["first.pdf", "second.pdf"]
    assert [seen[1] for seen in analyzer.seen] == [True, True]
    assert all(analysis.letter_of_intent == "loi" for analysis in batch.analyses)
    assert batch.failures == []


def test_analyze_folder_records_per_document_failures(tmp_path: Path):
    (tmp_path / "ok.pdf").write_bytes(b"%PDF-placeholder")
    (tmp_path / "bad.pdf").write_bytes(b"%PDF-placeholder")

    class PartiallyFailingAnalyzer(FolderSelectionAnalyzer):
        def analyze_document(self, document_path, include_letter=False):
            if Path(document_path).name == "bad.pdf":
                raise RuntimeError("boom")
            return super().analyze_document(document_path, include_letter=include_letter)

    batch = PartiallyFailingAnalyzer().analyze_folder(tmp_path, extensions={".pdf"})

    assert [analysis.source_name for analysis in batch.analyses] == ["ok.pdf"]
    assert len(batch.failures) == 1
    assert batch.failures[0].source_name == "bad.pdf"
    assert "boom" in batch.failures[0].error
