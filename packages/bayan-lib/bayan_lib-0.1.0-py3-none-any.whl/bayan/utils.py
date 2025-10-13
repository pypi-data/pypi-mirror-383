"""
Shared utilities and regex patterns for bayan.
"""

import re
from typing import List, Optional, Tuple
from datetime import datetime


class RegexPatterns:
    """
    Collection of regex patterns for extracting information from academic papers.
    """

    # DOI patterns
    DOI = re.compile(
        r'\b(10\.\d{4,}(?:\.\d+)?/(?:(?!["&\'<>])\S)+)\b',
        re.IGNORECASE
    )

    # arXiv ID patterns
    ARXIV = re.compile(
        r'\barXiv:(\d{4}\.\d{4,5}(?:v\d+)?)\b',
        re.IGNORECASE
    )

    # Email addresses
    EMAIL = re.compile(
        r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b'
    )

    # URLs
    URL = re.compile(
        r'http[s]?://(?:[a-zA-Z]|[0-9]|[$-_@.&+]|[!*\\(\\),]|(?:%[0-9a-fA-F][0-9a-fA-F]))+'
    )

    # Year patterns (1900-2099)
    YEAR = re.compile(r'\b(19|20)\d{2}\b')

    # Common section headers
    SECTION_HEADERS = re.compile(
        r'^(?:abstract|introduction|related\s+work|background|methodology|methods?|'
        r'experimental?\s+(?:setup|results?)|evaluation|results?|discussion|'
        r'conclusion|references|acknowledgments?|appendix|supplementary)',
        re.IGNORECASE | re.MULTILINE
    )

    # Reference patterns (various styles)
    REFERENCE_NUMBERED = re.compile(
        r'^\s*\[?(\d+)\]?\s*(.+?)$',
        re.MULTILINE
    )

    REFERENCE_AUTHOR_YEAR = re.compile(
        r'^([A-Z][a-zA-Z\s,\.\-]+?)\s*\((\d{4})\)',
        re.MULTILINE
    )

    # Table and figure captions
    TABLE_CAPTION = re.compile(
        r'(?:Table|TABLE)\s+(\d+|[IVX]+)[:\.]?\s*(.+?)(?=(?:Table|TABLE|Figure|FIGURE|\n\n|$))',
        re.IGNORECASE | re.DOTALL
    )

    FIGURE_CAPTION = re.compile(
        r'(?:Figure|Fig\.|FIG\.?)\s+(\d+|[IVX]+)[:\.]?\s*(.+?)(?=(?:Table|TABLE|Figure|FIGURE|Fig\.|\n\n|$))',
        re.IGNORECASE | re.DOTALL
    )

    # Author name patterns
    AUTHOR_NAME = re.compile(
        r'\b([A-Z][a-z]+(?:\s+[A-Z]\.?)?\s+[A-Z][a-z]+)\b'
    )

    # Common affiliations markers
    AFFILIATION_MARKER = re.compile(r'[0-9*†‡§¶,]+')

    # ISBN patterns
    ISBN = re.compile(
        r'ISBN(?:-1[03])?:?\s*(?:97[89][\s-]?)?\d{1,5}[\s-]?\d{1,7}[\s-]?\d{1,7}[\s-]?\d{1,7}[\s-]?\d'
    )

    # Common abbreviations in papers
    ABBREVIATIONS = re.compile(
        r'\b(?:e\.g\.|i\.e\.|et al\.|cf\.|vs\.|viz\.)\b',
        re.IGNORECASE
    )


class TextUtils:
    """
    Text processing utilities.
    """

    @staticmethod
    def extract_dois(text: str) -> List[str]:
        """
        Extract DOIs from text.

        Args:
            text: Text containing DOIs

        Returns:
            List of DOI strings
        """
        return RegexPatterns.DOI.findall(text)

    @staticmethod
    def extract_arxiv_ids(text: str) -> List[str]:
        """
        Extract arXiv IDs from text.

        Args:
            text: Text containing arXiv IDs

        Returns:
            List of arXiv ID strings
        """
        return RegexPatterns.ARXIV.findall(text)

    @staticmethod
    def extract_emails(text: str) -> List[str]:
        """
        Extract email addresses from text.

        Args:
            text: Text containing emails

        Returns:
            List of email addresses
        """
        return RegexPatterns.EMAIL.findall(text)

    @staticmethod
    def extract_years(text: str) -> List[int]:
        """
        Extract years from text.

        Args:
            text: Text containing years

        Returns:
            List of years as integers
        """
        years = RegexPatterns.YEAR.findall(text)
        return [int(y) for y in years]

    @staticmethod
    def extract_urls(text: str) -> List[str]:
        """
        Extract URLs from text.

        Args:
            text: Text containing URLs

        Returns:
            List of URLs
        """
        return RegexPatterns.URL.findall(text)

    @staticmethod
    def find_most_likely_year(text: str, prefer_recent: bool = True) -> Optional[int]:
        """
        Find the most likely publication year from text.

        Args:
            text: Text to search
            prefer_recent: Whether to prefer more recent years if multiple found

        Returns:
            Most likely year or None
        """
        years = TextUtils.extract_years(text)

        if not years:
            return None

        # Filter to reasonable publication years
        current_year = datetime.now().year
        valid_years = [y for y in years if 1950 <= y <= current_year + 1]

        if not valid_years:
            return None

        if prefer_recent:
            return max(valid_years)
        else:
            return min(valid_years)

    @staticmethod
    def split_by_sections(text: str) -> List[Tuple[str, str]]:
        """
        Split text into sections based on common headers.

        Args:
            text: Full paper text

        Returns:
            List of (section_name, section_content) tuples
        """
        sections = []
        lines = text.split("\n")

        current_section = "header"
        current_content = []

        for line in lines:
            # Check if line is a section header
            match = RegexPatterns.SECTION_HEADERS.match(line.strip())

            if match and len(line.strip()) < 50:  # Likely a header
                # Save previous section
                if current_content:
                    sections.append((
                        current_section,
                        "\n".join(current_content).strip()
                    ))

                # Start new section
                current_section = line.strip().lower()
                current_content = []
            else:
                current_content.append(line)

        # Add final section
        if current_content:
            sections.append((
                current_section,
                "\n".join(current_content).strip()
            ))

        return sections

    @staticmethod
    def calculate_text_similarity(text1: str, text2: str) -> float:
        """
        Calculate simple word-overlap similarity between two texts.

        Args:
            text1: First text
            text2: Second text

        Returns:
            Similarity score (0.0 to 1.0)
        """
        words1 = set(text1.lower().split())
        words2 = set(text2.lower().split())

        if not words1 or not words2:
            return 0.0

        intersection = words1.intersection(words2)
        union = words1.union(words2)

        return len(intersection) / len(union)

    @staticmethod
    def truncate_text(text: str, max_words: int = 100, suffix: str = "...") -> str:
        """
        Truncate text to a maximum number of words.

        Args:
            text: Text to truncate
            max_words: Maximum number of words
            suffix: Suffix to add if truncated

        Returns:
            Truncated text
        """
        words = text.split()

        if len(words) <= max_words:
            return text

        return " ".join(words[:max_words]) + suffix

    @staticmethod
    def is_likely_title(text: str, max_length: int = 200) -> bool:
        """
        Heuristic to determine if text is likely a paper title.

        Args:
            text: Text to check
            max_length: Maximum expected title length

        Returns:
            True if likely a title
        """
        # Remove whitespace
        text = text.strip()

        # Check length
        if len(text) > max_length or len(text) < 10:
            return False

        # Should not end with common sentence-ending patterns
        if text.endswith((".", ",", ":", ";")):
            # Unless it's an abbreviation
            if not any(text.endswith(abbr) for abbr in ["Jr.", "Sr.", "Inc.", "Ltd."]):
                return False

        # Should have some capital letters (but not all)
        capitals = sum(1 for c in text if c.isupper())
        if capitals == 0 or capitals == len([c for c in text if c.isalpha()]):
            return False

        # Should not have reference markers
        if re.search(r'\[\d+\]', text):
            return False

        return True

    @staticmethod
    def is_likely_author(text: str) -> bool:
        """
        Heuristic to determine if text is likely an author name.

        Args:
            text: Text to check

        Returns:
            True if likely an author name
        """
        text = text.strip()

        # Basic length check
        if len(text) < 3 or len(text) > 100:
            return False

        # Should contain at least one capital letter
        if not any(c.isupper() for c in text):
            return False

        # Should not contain numbers (except affiliation markers)
        text_no_markers = RegexPatterns.AFFILIATION_MARKER.sub("", text)
        if any(c.isdigit() for c in text_no_markers):
            return False

        # Should not contain common non-name words
        non_name_words = ["abstract", "introduction", "university", "department", "email"]
        if any(word in text.lower() for word in non_name_words):
            return False

        return True

    @staticmethod
    def normalize_whitespace_inline(text: str) -> str:
        """
        Normalize whitespace while preserving single line structure.

        Args:
            text: Text to normalize

        Returns:
            Normalized text
        """
        # Replace newlines with spaces
        text = text.replace("\n", " ")

        # Collapse multiple spaces
        text = re.sub(r'\s+', ' ', text)

        return text.strip()


class FormatUtils:
    """
    Formatting and conversion utilities.
    """

    @staticmethod
    def format_author_list(authors: List[str], max_display: int = 3) -> str:
        """
        Format author list for display.

        Args:
            authors: List of author names
            max_display: Maximum authors to display before using "et al."

        Returns:
            Formatted author string
        """
        if not authors:
            return "Unknown"

        if len(authors) <= max_display:
            return ", ".join(authors)

        return ", ".join(authors[:max_display]) + " et al."

    @staticmethod
    def format_citation(metadata: dict, style: str = "apa") -> str:
        """
        Format citation in common styles.

        Args:
            metadata: Paper metadata dictionary
            style: Citation style ("apa", "mla", "chicago")

        Returns:
            Formatted citation string
        """
        title = metadata.get("title", "Unknown Title")
        authors = metadata.get("authors", ["Unknown"])
        year = metadata.get("year", "n.d.")

        if style == "apa":
            author_str = FormatUtils.format_author_list(authors)
            return f"{author_str} ({year}). {title}."
        elif style == "mla":
            author_str = ", ".join(authors) if authors else "Unknown"
            return f'{author_str}. "{title}." {year}.'
        elif style == "chicago":
            author_str = ", ".join(authors) if authors else "Unknown"
            return f'{author_str}. "{title}." {year}.'
        else:
            return f"{title} ({year})"

    @staticmethod
    def bytes_to_human_readable(num_bytes: int) -> str:
        """
        Convert bytes to human-readable format.

        Args:
            num_bytes: Number of bytes

        Returns:
            Human-readable string (e.g., "1.5 MB")
        """
        for unit in ['B', 'KB', 'MB', 'GB', 'TB']:
            if num_bytes < 1024.0:
                return f"{num_bytes:.1f} {unit}"
            num_bytes /= 1024.0
        return f"{num_bytes:.1f} PB"
