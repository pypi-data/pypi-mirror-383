"""
Basic tests for bayan library.

Note: These tests require actual PDF files to run.
Place test PDFs in tests/fixtures/ directory.
"""

import pytest
from pathlib import Path


class TestImports:
    """Test that all modules can be imported."""

    def test_import_main(self):
        """Test importing main Paper class."""
        from bayan import Paper
        assert Paper is not None

    def test_import_parser(self):
        """Test importing PDFParser."""
        from bayan.parser import PDFParser
        assert PDFParser is not None

    def test_import_extractor(self):
        """Test importing PaperExtractor."""
        from bayan.extractor import PaperExtractor
        assert PaperExtractor is not None

    def test_import_cleaner(self):
        """Test importing TextCleaner."""
        from bayan.cleaner import TextCleaner
        assert TextCleaner is not None

    def test_import_utils(self):
        """Test importing utilities."""
        from bayan.utils import TextUtils, RegexPatterns
        assert TextUtils is not None
        assert RegexPatterns is not None

    def test_import_exporter(self):
        """Test importing PaperExporter."""
        from bayan.exporter import PaperExporter
        assert PaperExporter is not None

    def test_import_tables(self):
        """Test importing TableExtractor."""
        from bayan.tables import TableExtractor
        assert TableExtractor is not None


class TestTextCleaner:
    """Test TextCleaner functionality."""

    def test_clean_basic(self):
        """Test basic text cleaning."""
        from bayan.cleaner import TextCleaner

        cleaner = TextCleaner()
        text = "This  has   multiple    spaces"
        cleaned = cleaner.clean(text)

        assert "  " not in cleaned
        assert cleaned == "This has multiple spaces"

    def test_clean_ligatures(self):
        """Test ligature replacement."""
        from bayan.cleaner import TextCleaner

        cleaner = TextCleaner()
        text = "ﬁle with ligatures ﬂows"
        cleaned = cleaner.clean(text)

        assert "ﬁ" not in cleaned
        assert "ﬂ" not in cleaned
        assert "file" in cleaned
        assert "flows" in cleaned

    def test_clean_title(self):
        """Test title cleaning."""
        from bayan.cleaner import TextCleaner

        cleaner = TextCleaner()
        title = "  A Great  Paper\nTitle  "
        cleaned = cleaner.clean_title(title)

        assert cleaned == "A Great Paper Title"


class TestTextUtils:
    """Test TextUtils functionality."""

    def test_extract_dois(self):
        """Test DOI extraction."""
        from bayan.utils import TextUtils

        text = "See doi:10.1234/test.123 for more info"
        dois = TextUtils.extract_dois(text)

        assert len(dois) > 0
        assert "10.1234/test.123" in dois[0]

    def test_extract_years(self):
        """Test year extraction."""
        from bayan.utils import TextUtils

        text = "Published in 2020 and updated in 2021"
        years = TextUtils.extract_years(text)

        assert 2020 in years
        assert 2021 in years

    def test_extract_emails(self):
        """Test email extraction."""
        from bayan.utils import TextUtils

        text = "Contact: author@example.com"
        emails = TextUtils.extract_emails(text)

        assert len(emails) > 0
        assert "author@example.com" in emails


class TestPaperWithFixture:
    """Tests that require actual PDF fixtures."""

    @pytest.fixture
    def sample_pdf_path(self):
        """Path to sample PDF for testing."""
        fixtures_dir = Path(__file__).parent / "fixtures"
        pdf_path = fixtures_dir / "sample.pdf"

        if not pdf_path.exists():
            pytest.skip("Sample PDF not found in tests/fixtures/")

        return str(pdf_path)

    def test_paper_loading(self, sample_pdf_path):
        """Test loading a paper."""
        from bayan import Paper

        paper = Paper(sample_pdf_path)
        assert paper is not None
        assert paper.parser is not None
        paper.close()

    def test_metadata_extraction(self, sample_pdf_path):
        """Test metadata extraction."""
        from bayan import Paper

        with Paper(sample_pdf_path) as paper:
            meta = paper.extract_metadata()

            assert "title" in meta
            assert "authors" in meta
            assert isinstance(meta["authors"], list)

    def test_sections_extraction(self, sample_pdf_path):
        """Test section extraction."""
        from bayan import Paper

        with Paper(sample_pdf_path) as paper:
            sections = paper.extract_sections()

            assert isinstance(sections, dict)

    def test_export_json(self, sample_pdf_path, tmp_path):
        """Test JSON export."""
        from bayan import Paper
        import json

        output_path = tmp_path / "test_output.json"

        with Paper(sample_pdf_path) as paper:
            paper.export("json", str(output_path))

        assert output_path.exists()

        # Verify it's valid JSON
        with open(output_path) as f:
            data = json.load(f)
            assert "metadata" in data


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
