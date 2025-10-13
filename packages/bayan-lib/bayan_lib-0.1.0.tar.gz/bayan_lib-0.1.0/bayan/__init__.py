"""
bayan - Bring clarity to research papers.

A Python library for extracting structured, meaningful information from academic PDFs.
"""

__version__ = "0.1.0"
__author__ = "Khalil Selmi"
__license__ = "MIT"

from bayan.parser import PDFParser
from bayan.extractor import PaperExtractor
from bayan.exporter import PaperExporter
from bayan.tables import TableExtractor
from bayan.cleaner import TextCleaner
from bayan.llm_client import LLMClient


class Paper:
    """
    Main interface for parsing and extracting information from research papers.

    Example:
        >>> paper = Paper("research_paper.pdf")
        >>> meta = paper.extract_metadata()
        >>> sections = paper.extract_sections()
        >>> paper.export("json", "output.json")
    """

    def __init__(self, pdf_path: str):
        """
        Initialize a Paper object.

        Args:
            pdf_path: Path to the PDF file
        """
        self.pdf_path = pdf_path
        self.parser = PDFParser(pdf_path)
        self.extractor = PaperExtractor(self.parser)
        self.table_extractor = TableExtractor(self.parser)
        self.exporter = PaperExporter()
        self.llm_client = None

        # Cached results
        self._metadata = None
        self._sections = None
        self._references = None
        self._tables = None
        self._figures = None

    def extract_metadata(self, force_refresh: bool = False) -> dict:
        """
        Extract paper metadata (title, authors, affiliations, DOI, year).

        Args:
            force_refresh: If True, re-extract even if cached

        Returns:
            Dictionary containing metadata fields
        """
        if self._metadata is None or force_refresh:
            self._metadata = self.extractor.extract_metadata()
        return self._metadata

    def extract_sections(self, force_refresh: bool = False) -> dict:
        """
        Extract paper sections (abstract, introduction, methodology, etc.).

        Args:
            force_refresh: If True, re-extract even if cached

        Returns:
            Dictionary mapping section names to their content
        """
        if self._sections is None or force_refresh:
            self._sections = self.extractor.extract_sections()
        return self._sections

    def extract_references(self, force_refresh: bool = False) -> list:
        """
        Extract and parse references/citations.

        Args:
            force_refresh: If True, re-extract even if cached

        Returns:
            List of reference dictionaries
        """
        if self._references is None or force_refresh:
            self._references = self.extractor.extract_references()
        return self._references

    def extract_tables(self, force_refresh: bool = False) -> list:
        """
        Extract tables with captions and context.

        Args:
            force_refresh: If True, re-extract even if cached

        Returns:
            List of table dictionaries
        """
        if self._tables is None or force_refresh:
            self._tables = self.table_extractor.extract_tables()
        return self._tables

    def extract_figures(self, force_refresh: bool = False) -> list:
        """
        Extract figures with captions and metadata.

        Args:
            force_refresh: If True, re-extract even if cached

        Returns:
            List of figure dictionaries
        """
        if self._figures is None or force_refresh:
            self._figures = self.table_extractor.extract_figures()
        return self._figures

    def extract_all(self) -> dict:
        """
        Extract all available information from the paper.

        Returns:
            Complete dictionary with all extracted data
        """
        return {
            "metadata": self.extract_metadata(),
            "sections": self.extract_sections(),
            "references": self.extract_references(),
            "tables": self.extract_tables(),
            "figures": self.extract_figures()
        }

    def export(self, format: str, output_path: str, data: dict = None):
        """
        Export extracted data to various formats.

        Args:
            format: Output format ('json', 'markdown', 'csv', 'txt')
            output_path: Path to save the output file
            data: Data to export (defaults to extract_all())
        """
        if data is None:
            data = self.extract_all()

        self.exporter.export(data, format, output_path)

    def enable_llm(self, provider: str = "openai", **kwargs):
        """
        Enable LLM integration for summarization and classification.

        Args:
            provider: LLM provider ('openai', 'huggingface', 'local')
            **kwargs: Provider-specific configuration (api_key, model_name, etc.)
        """
        self.llm_client = LLMClient(provider=provider, **kwargs)

    def summarize(self, section: str = None, max_length: int = 200) -> str:
        """
        Generate a summary using LLM.

        Args:
            section: Specific section to summarize (None for full paper)
            max_length: Maximum length of summary in words

        Returns:
            Summary text

        Raises:
            RuntimeError: If LLM is not enabled
        """
        if self.llm_client is None:
            raise RuntimeError("LLM not enabled. Call enable_llm() first.")

        if section:
            sections = self.extract_sections()
            text = sections.get(section, "")
            if not text:
                raise ValueError(f"Section '{section}' not found")
        else:
            text = self.parser.get_full_text()

        return self.llm_client.summarize(text, max_length=max_length)

    def classify(self) -> dict:
        """
        Classify the paper type using LLM.

        Returns:
            Dictionary with classification results

        Raises:
            RuntimeError: If LLM is not enabled
        """
        if self.llm_client is None:
            raise RuntimeError("LLM not enabled. Call enable_llm() first.")

        metadata = self.extract_metadata()
        sections = self.extract_sections()

        return self.llm_client.classify_paper(metadata, sections)

    def close(self):
        """Close the PDF parser and free resources."""
        self.parser.close()

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.close()


__all__ = [
    "Paper",
    "PDFParser",
    "PaperExtractor",
    "PaperExporter",
    "TableExtractor",
    "TextCleaner",
    "LLMClient",
]
