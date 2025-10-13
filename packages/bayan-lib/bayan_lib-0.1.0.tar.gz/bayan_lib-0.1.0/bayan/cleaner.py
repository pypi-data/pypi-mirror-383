"""
Text cleaning and normalization module for academic papers.
"""

import re
from typing import Optional


class TextCleaner:
    """
    Handles text normalization, artifact removal, and layout preservation.
    """

    def __init__(self):
        """Initialize text cleaner with common patterns."""
        # Common PDF artifacts and patterns
        self.patterns = {
            # Multiple spaces to single space
            "multiple_spaces": re.compile(r" {2,}"),

            # Hyphenated line breaks (e.g., "com-\nputer" -> "computer")
            "hyphenated_linebreak": re.compile(r"(\w+)-\s*\n\s*(\w+)"),

            # Common ligatures
            "ligatures": {
                "ﬁ": "fi",
                "ﬂ": "fl",
                "ﬀ": "ff",
                "ﬃ": "ffi",
                "ﬄ": "ffl",
                "ﬆ": "st",
            },

            # Header/footer patterns (page numbers, common headers)
            "page_numbers": re.compile(r"^\s*\d+\s*$", re.MULTILINE),

            # Excessive newlines
            "excessive_newlines": re.compile(r"\n{3,}"),

            # Unicode normalization issues
            "unicode_dashes": {
                "\u2010": "-",  # Hyphen
                "\u2011": "-",  # Non-breaking hyphen
                "\u2012": "-",  # Figure dash
                "\u2013": "-",  # En dash
                "\u2014": "--", # Em dash
                "\u2015": "--", # Horizontal bar
            },

            "unicode_quotes": {
                "\u2018": "'",  # Left single quote
                "\u2019": "'",  # Right single quote
                "\u201a": "'",  # Single low quote
                "\u201b": "'",  # Single high-reversed quote
                "\u201c": '"',  # Left double quote
                "\u201d": '"',  # Right double quote
                "\u201e": '"',  # Double low quote
                "\u201f": '"',  # Double high-reversed quote
            },

            # Common reference markers
            "reference_markers": re.compile(r"\[\d+(?:,\s*\d+)*\]"),

            # Bullet points and list markers
            "bullets": re.compile(r"^[•◦▪▫→⇒]\s*", re.MULTILINE),
        }

    def clean(self, text: str, preserve_structure: bool = True) -> str:
        """
        Clean and normalize text.

        Args:
            text: Raw text to clean
            preserve_structure: Whether to preserve paragraph structure

        Returns:
            Cleaned text
        """
        if not text:
            return ""

        # Fix ligatures
        for ligature, replacement in self.patterns["ligatures"].items():
            text = text.replace(ligature, replacement)

        # Fix unicode dashes
        for dash, replacement in self.patterns["unicode_dashes"].items():
            text = text.replace(dash, replacement)

        # Fix unicode quotes
        for quote, replacement in self.patterns["unicode_quotes"].items():
            text = text.replace(quote, replacement)

        # Fix hyphenated line breaks
        text = self.patterns["hyphenated_linebreak"].sub(r"\1\2", text)

        # Normalize multiple spaces
        text = self.patterns["multiple_spaces"].sub(" ", text)

        # Remove excessive newlines but preserve paragraph structure
        if preserve_structure:
            text = self.patterns["excessive_newlines"].sub("\n\n", text)
        else:
            text = self.patterns["excessive_newlines"].sub("\n", text)

        # Strip leading/trailing whitespace from each line
        lines = [line.strip() for line in text.split("\n")]
        text = "\n".join(lines)

        return text.strip()

    def remove_headers_footers(self, text: str, header_pattern: Optional[str] = None,
                               footer_pattern: Optional[str] = None) -> str:
        """
        Remove common headers and footers.

        Args:
            text: Text to process
            header_pattern: Custom regex pattern for headers
            footer_pattern: Custom regex pattern for footers

        Returns:
            Text with headers/footers removed
        """
        lines = text.split("\n")
        cleaned_lines = []

        for line in lines:
            # Skip page numbers
            if self.patterns["page_numbers"].match(line):
                continue

            # Skip custom patterns
            if header_pattern and re.match(header_pattern, line):
                continue

            if footer_pattern and re.match(footer_pattern, line):
                continue

            cleaned_lines.append(line)

        return "\n".join(cleaned_lines)

    def normalize_whitespace(self, text: str) -> str:
        """
        Normalize all whitespace to standard spaces and newlines.

        Args:
            text: Text to normalize

        Returns:
            Normalized text
        """
        # Replace tabs with spaces
        text = text.replace("\t", " ")

        # Replace non-breaking spaces
        text = text.replace("\xa0", " ")

        # Replace other unicode spaces
        text = text.replace("\u2000", " ")  # En quad
        text = text.replace("\u2001", " ")  # Em quad
        text = text.replace("\u2002", " ")  # En space
        text = text.replace("\u2003", " ")  # Em space
        text = text.replace("\u2004", " ")  # Three-per-em space
        text = text.replace("\u2005", " ")  # Four-per-em space
        text = text.replace("\u2006", " ")  # Six-per-em space
        text = text.replace("\u2007", " ")  # Figure space
        text = text.replace("\u2008", " ")  # Punctuation space
        text = text.replace("\u2009", " ")  # Thin space
        text = text.replace("\u200a", " ")  # Hair space

        # Normalize multiple spaces
        text = self.patterns["multiple_spaces"].sub(" ", text)

        return text

    def remove_reference_markers(self, text: str) -> str:
        """
        Remove inline reference markers like [1], [2,3], etc.

        Args:
            text: Text containing reference markers

        Returns:
            Text with markers removed
        """
        return self.patterns["reference_markers"].sub("", text)

    def normalize_bullets(self, text: str) -> str:
        """
        Normalize bullet points to a standard format.

        Args:
            text: Text with various bullet styles

        Returns:
            Text with normalized bullets
        """
        return self.patterns["bullets"].sub("• ", text)

    def clean_section_text(self, text: str) -> str:
        """
        Special cleaning for section content (more aggressive).

        Args:
            text: Section text

        Returns:
            Cleaned section text
        """
        # Apply standard cleaning
        text = self.clean(text, preserve_structure=True)

        # Remove reference markers for cleaner reading
        text = self.remove_reference_markers(text)

        # Normalize bullets
        text = self.normalize_bullets(text)

        return text

    def extract_sentences(self, text: str) -> list:
        """
        Split text into sentences.

        Args:
            text: Text to split

        Returns:
            List of sentences
        """
        # Simple sentence splitting (can be enhanced with NLTK if needed)
        # Handle common abbreviations
        text = re.sub(r"\b(Dr|Mr|Mrs|Ms|Prof|Sr|Jr|vs|etc|e\.g|i\.e)\.", r"\1<PERIOD>", text)

        # Split on sentence boundaries
        sentences = re.split(r'[.!?]+\s+', text)

        # Restore periods in abbreviations
        sentences = [s.replace("<PERIOD>", ".").strip() for s in sentences]

        return [s for s in sentences if s]

    def clean_title(self, title: str) -> str:
        """
        Clean and normalize paper title.

        Args:
            title: Raw title text

        Returns:
            Cleaned title
        """
        # Basic cleaning
        title = self.clean(title, preserve_structure=False)

        # Remove line breaks
        title = title.replace("\n", " ")

        # Normalize spaces
        title = self.patterns["multiple_spaces"].sub(" ", title)

        # Remove trailing/leading punctuation (except periods at the end)
        title = title.strip("- \t")

        return title.strip()

    def clean_author_name(self, name: str) -> str:
        """
        Clean and normalize author name.

        Args:
            name: Raw author name

        Returns:
            Cleaned name
        """
        # Basic cleaning
        name = self.clean(name, preserve_structure=False)

        # Remove line breaks
        name = name.replace("\n", " ")

        # Remove numbers and special markers
        name = re.sub(r"[0-9*†‡§¶]", "", name)

        # Normalize spaces
        name = self.patterns["multiple_spaces"].sub(" ", name)

        return name.strip()
