"""
Extraction module for metadata, sections, and references from academic papers.
"""

import re
from typing import Dict, List, Optional, Tuple
from bayan.parser import PDFParser
from bayan.cleaner import TextCleaner
from bayan.utils import RegexPatterns, TextUtils


class PaperExtractor:
    """
    Extracts structured information from academic papers.
    """

    def __init__(self, parser: PDFParser):
        """
        Initialize extractor with a PDF parser.

        Args:
            parser: PDFParser instance
        """
        self.parser = parser
        self.cleaner = TextCleaner()

    def extract_metadata(self) -> Dict:
        """
        Extract comprehensive metadata from the paper.

        Returns:
            Dictionary containing:
                - title: Paper title
                - authors: List of author names
                - affiliations: List of affiliations
                - doi: DOI if found
                - arxiv_id: arXiv ID if found
                - year: Publication year
                - emails: Contact emails
                - keywords: Keywords if found
        """
        # Get first few pages for metadata extraction
        first_page = self.parser.get_page_text(0, clean=True)
        second_page = ""
        if self.parser.page_count > 1:
            second_page = self.parser.get_page_text(1, clean=True)

        metadata_text = first_page + "\n" + second_page

        # Get PDF metadata
        pdf_meta = self.parser.get_metadata()

        # Extract components
        title = self._extract_title(first_page, pdf_meta)
        authors = self._extract_authors(first_page)
        affiliations = self._extract_affiliations(first_page)
        doi = self._extract_doi(metadata_text)
        arxiv_id = self._extract_arxiv_id(metadata_text)
        year = self._extract_year(metadata_text)
        emails = TextUtils.extract_emails(metadata_text)
        keywords = self._extract_keywords(metadata_text)

        return {
            "title": title,
            "authors": authors,
            "affiliations": affiliations,
            "doi": doi,
            "arxiv_id": arxiv_id,
            "year": year,
            "emails": emails,
            "keywords": keywords,
            "page_count": self.parser.page_count
        }

    def _extract_title(self, first_page: str, pdf_meta: Dict) -> str:
        """Extract paper title using multiple strategies."""
        # Strategy 1: Use PDF metadata if available and seems valid
        if pdf_meta.get("title") and len(pdf_meta["title"]) > 10:
            title = self.cleaner.clean_title(pdf_meta["title"])
            if TextUtils.is_likely_title(title):
                return title

        # Strategy 2: Look for largest text on first page
        if self.parser.page_count > 0:
            spans = self.parser.get_text_with_fonts(0)

            # Group spans by size
            size_groups = {}
            for span in spans:
                size = span["size"]
                text = span["text"].strip()

                if text and len(text) > 10:
                    if size not in size_groups:
                        size_groups[size] = []
                    size_groups[size].append(text)

            # Get largest font size
            if size_groups:
                max_size = max(size_groups.keys())
                candidates = size_groups[max_size]

                # Find the longest candidate
                for candidate in sorted(candidates, key=len, reverse=True):
                    cleaned = self.cleaner.clean_title(candidate)
                    if TextUtils.is_likely_title(cleaned):
                        return cleaned

        # Strategy 3: Extract from first lines
        lines = first_page.split("\n")
        for i, line in enumerate(lines[:10]):
            cleaned = self.cleaner.clean_title(line)
            if TextUtils.is_likely_title(cleaned) and len(cleaned) > 15:
                # Check if next lines continue the title
                full_title = cleaned
                for next_line in lines[i+1:i+3]:
                    next_cleaned = next_line.strip()
                    if next_cleaned and not TextUtils.is_likely_author(next_cleaned):
                        if next_cleaned[0].isupper() or next_cleaned[0].islower():
                            full_title += " " + next_cleaned
                        else:
                            break
                    else:
                        break

                return self.cleaner.clean_title(full_title)

        return "Unknown Title"

    def _extract_authors(self, first_page: str) -> List[str]:
        """Extract author names from first page."""
        lines = first_page.split("\n")
        authors = []

        # Look for author section (usually after title)
        in_author_section = False
        author_lines = []

        for i, line in enumerate(lines[:30]):  # Check first 30 lines
            line = line.strip()

            # Skip empty lines
            if not line:
                continue

            # Check if we're past the author section
            if any(keyword in line.lower() for keyword in ["abstract", "introduction", "@"]):
                break

            # Heuristics for author names
            if TextUtils.is_likely_author(line):
                # Clean affiliation markers
                clean_line = self.cleaner.clean_author_name(line)

                # Split by common delimiters
                if "," in clean_line:
                    parts = [p.strip() for p in clean_line.split(",")]
                    authors.extend([p for p in parts if TextUtils.is_likely_author(p)])
                elif " and " in clean_line.lower():
                    parts = re.split(r'\s+and\s+', clean_line, flags=re.IGNORECASE)
                    authors.extend([p.strip() for p in parts if TextUtils.is_likely_author(p)])
                else:
                    authors.append(clean_line)

        # Deduplicate while preserving order
        seen = set()
        unique_authors = []
        for author in authors:
            if author not in seen and len(author) > 2:
                seen.add(author)
                unique_authors.append(author)

        return unique_authors[:20]  # Reasonable limit

    def _extract_affiliations(self, first_page: str) -> List[str]:
        """Extract institutional affiliations."""
        affiliations = []
        lines = first_page.split("\n")

        # Common affiliation indicators
        affiliation_keywords = [
            "university", "college", "institute", "laboratory", "department",
            "school", "center", "lab", "research", "faculty"
        ]

        for line in lines[:40]:  # Check first 40 lines
            line_lower = line.lower()

            if any(keyword in line_lower for keyword in affiliation_keywords):
                clean_line = line.strip()

                # Remove affiliation markers
                clean_line = re.sub(r'^[0-9*†‡§¶,]+\s*', '', clean_line)

                if len(clean_line) > 5 and clean_line not in affiliations:
                    affiliations.append(clean_line)

        return affiliations[:10]  # Reasonable limit

    def _extract_doi(self, text: str) -> Optional[str]:
        """Extract DOI from text."""
        dois = TextUtils.extract_dois(text)
        return dois[0] if dois else None

    def _extract_arxiv_id(self, text: str) -> Optional[str]:
        """Extract arXiv ID from text."""
        arxiv_ids = TextUtils.extract_arxiv_ids(text)
        return arxiv_ids[0] if arxiv_ids else None

    def _extract_year(self, text: str) -> Optional[int]:
        """Extract publication year."""
        return TextUtils.find_most_likely_year(text, prefer_recent=True)

    def _extract_keywords(self, text: str) -> List[str]:
        """Extract keywords if present."""
        keywords = []

        # Look for explicit keywords section
        match = re.search(
            r'(?:keywords?|index terms)[:\s]+(.+?)(?:\n\n|abstract|introduction|$)',
            text,
            re.IGNORECASE | re.DOTALL
        )

        if match:
            keywords_text = match.group(1)

            # Split by common delimiters
            if "," in keywords_text:
                keywords = [k.strip() for k in keywords_text.split(",")]
            elif ";" in keywords_text:
                keywords = [k.strip() for k in keywords_text.split(";")]
            elif "·" in keywords_text:
                keywords = [k.strip() for k in keywords_text.split("·")]
            else:
                keywords = keywords_text.split()

            # Clean and filter
            keywords = [k.strip(" •·-") for k in keywords if k.strip()]
            keywords = [k for k in keywords if 2 < len(k) < 50]

        return keywords[:20]  # Reasonable limit

    def extract_sections(self) -> Dict[str, str]:
        """
        Extract paper sections.

        Returns:
            Dictionary mapping section names to content
        """
        full_text = self.parser.get_full_text(clean=True)

        # Split by sections
        sections_list = TextUtils.split_by_sections(full_text)

        sections = {}

        # Map to standard section names
        section_mapping = {
            "abstract": ["abstract"],
            "introduction": ["introduction", "intro"],
            "related_work": ["related work", "related works", "literature review", "background"],
            "methodology": ["methodology", "method", "methods", "approach", "proposed method"],
            "experiments": ["experiments", "experimental setup", "experimental results"],
            "results": ["results", "evaluation", "performance"],
            "discussion": ["discussion", "analysis"],
            "conclusion": ["conclusion", "conclusions", "summary"],
            "references": ["references", "bibliography"],
            "acknowledgments": ["acknowledgment", "acknowledgments", "acknowledgements"],
        }

        # Assign sections
        for section_name, content in sections_list:
            normalized_name = section_name.lower().strip()

            # Find matching standard name
            matched = False
            for standard_name, variants in section_mapping.items():
                if any(variant in normalized_name for variant in variants):
                    if standard_name not in sections:  # Take first match
                        sections[standard_name] = self.cleaner.clean_section_text(content)
                    matched = True
                    break

            # If no match, use the original name
            if not matched and content.strip():
                sections[normalized_name] = self.cleaner.clean_section_text(content)

        return sections

    def extract_references(self) -> List[Dict]:
        """
        Extract and parse references/citations.

        Returns:
            List of reference dictionaries
        """
        full_text = self.parser.get_full_text(clean=True)

        # Find references section
        ref_match = re.search(
            r'(?:^|\n)(?:references|bibliography)(?:\n|$)(.+)',
            full_text,
            re.IGNORECASE | re.DOTALL
        )

        if not ref_match:
            return []

        ref_text = ref_match.group(1)

        # Try numbered references first [1] Author et al.
        references = self._parse_numbered_references(ref_text)

        # If that fails, try author-year format
        if not references:
            references = self._parse_author_year_references(ref_text)

        return references

    def _parse_numbered_references(self, text: str) -> List[Dict]:
        """Parse numbered references."""
        references = []

        # Split by reference numbers
        pattern = r'\[(\d+)\]\s*(.+?)(?=\[\d+\]|$)'
        matches = re.findall(pattern, text, re.DOTALL)

        for ref_num, ref_text in matches:
            ref_text = self.cleaner.clean(ref_text, preserve_structure=False)
            ref_text = ref_text.replace("\n", " ").strip()

            if len(ref_text) > 10:
                # Extract year if present
                years = TextUtils.extract_years(ref_text)
                year = years[0] if years else None

                # Extract DOI if present
                dois = TextUtils.extract_dois(ref_text)
                doi = dois[0] if dois else None

                references.append({
                    "id": int(ref_num),
                    "text": ref_text,
                    "year": year,
                    "doi": doi
                })

        return references

    def _parse_author_year_references(self, text: str) -> List[Dict]:
        """Parse author-year style references."""
        references = []
        lines = text.split("\n\n")  # References usually separated by blank lines

        ref_id = 1
        for line in lines:
            line = self.cleaner.clean(line, preserve_structure=False)
            line = line.replace("\n", " ").strip()

            if len(line) > 20:  # Minimum length for a reference
                # Try to extract author and year
                match = re.match(r'^(.+?)\s*\((\d{4})\)', line)

                if match:
                    authors = match.group(1).strip()
                    year = int(match.group(2))

                    # Extract DOI if present
                    dois = TextUtils.extract_dois(line)
                    doi = dois[0] if dois else None

                    references.append({
                        "id": ref_id,
                        "text": line,
                        "authors": authors,
                        "year": year,
                        "doi": doi
                    })

                    ref_id += 1

        return references

    def extract_abstract(self) -> str:
        """
        Extract just the abstract (quick method).

        Returns:
            Abstract text
        """
        sections = self.extract_sections()
        return sections.get("abstract", "")

    def get_paper_summary(self) -> Dict:
        """
        Get a quick summary of the paper.

        Returns:
            Dictionary with key information
        """
        metadata = self.extract_metadata()
        abstract = self.extract_abstract()

        return {
            "title": metadata["title"],
            "authors": metadata["authors"],
            "year": metadata["year"],
            "abstract": abstract[:500] + "..." if len(abstract) > 500 else abstract,
            "doi": metadata["doi"],
            "page_count": metadata["page_count"]
        }
