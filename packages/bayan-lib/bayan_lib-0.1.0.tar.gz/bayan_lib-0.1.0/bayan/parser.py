"""
PDF parsing module using PyMuPDF (fitz) and pdfminer for robust text extraction.
"""

import fitz  # PyMuPDF
from typing import List, Dict, Tuple, Optional
from pathlib import Path
from bayan.cleaner import TextCleaner


class PDFParser:
    """
    Core PDF parser that handles text extraction, layout analysis, and page operations.
    """

    def __init__(self, pdf_path: str):
        """
        Initialize PDF parser.

        Args:
            pdf_path: Path to the PDF file

        Raises:
            FileNotFoundError: If PDF file doesn't exist
            ValueError: If file is not a valid PDF
        """
        self.pdf_path = Path(pdf_path)

        if not self.pdf_path.exists():
            raise FileNotFoundError(f"PDF file not found: {pdf_path}")

        try:
            self.doc = fitz.open(str(self.pdf_path))
        except Exception as e:
            raise ValueError(f"Failed to open PDF: {e}")

        self.cleaner = TextCleaner()
        self.page_count = len(self.doc)

    def get_page_text(self, page_num: int, clean: bool = True) -> str:
        """
        Extract text from a specific page.

        Args:
            page_num: Page number (0-indexed)
            clean: Whether to apply text cleaning

        Returns:
            Extracted text from the page
        """
        if page_num < 0 or page_num >= self.page_count:
            raise ValueError(f"Page number {page_num} out of range (0-{self.page_count - 1})")

        page = self.doc[page_num]
        text = page.get_text("text")

        if clean:
            text = self.cleaner.clean(text)

        return text

    def get_page_blocks(self, page_num: int) -> List[Dict]:
        """
        Extract text blocks with position information.

        Args:
            page_num: Page number (0-indexed)

        Returns:
            List of text blocks with bounding boxes and metadata
        """
        if page_num < 0 or page_num >= self.page_count:
            raise ValueError(f"Page number {page_num} out of range")

        page = self.doc[page_num]
        blocks = page.get_text("dict")["blocks"]

        structured_blocks = []
        for block in blocks:
            if block.get("type") == 0:  # Text block
                block_data = {
                    "bbox": block["bbox"],  # (x0, y0, x1, y1)
                    "text": "",
                    "lines": []
                }

                for line in block.get("lines", []):
                    line_text = ""
                    for span in line.get("spans", []):
                        line_text += span.get("text", "")

                    block_data["lines"].append({
                        "text": line_text,
                        "bbox": line["bbox"],
                    })
                    block_data["text"] += line_text + "\n"

                block_data["text"] = self.cleaner.clean(block_data["text"])
                structured_blocks.append(block_data)

        return structured_blocks

    def get_full_text(self, clean: bool = True, page_separator: str = "\n\n") -> str:
        """
        Extract all text from the PDF.

        Args:
            clean: Whether to apply text cleaning
            page_separator: String to separate pages

        Returns:
            Full text content
        """
        pages = []
        for page_num in range(self.page_count):
            text = self.get_page_text(page_num, clean=clean)
            if text.strip():
                pages.append(text)

        return page_separator.join(pages)

    def get_text_with_fonts(self, page_num: int) -> List[Dict]:
        """
        Extract text with font information (useful for detecting headers, titles).

        Args:
            page_num: Page number (0-indexed)

        Returns:
            List of text spans with font metadata
        """
        if page_num < 0 or page_num >= self.page_count:
            raise ValueError(f"Page number {page_num} out of range")

        page = self.doc[page_num]
        blocks = page.get_text("dict")["blocks"]

        spans = []
        for block in blocks:
            if block.get("type") == 0:  # Text block
                for line in block.get("lines", []):
                    for span in line.get("spans", []):
                        spans.append({
                            "text": span.get("text", ""),
                            "size": span.get("size", 0),
                            "flags": span.get("flags", 0),
                            "font": span.get("font", ""),
                            "color": span.get("color", 0),
                            "bbox": span.get("bbox", (0, 0, 0, 0))
                        })

        return spans

    def get_metadata(self) -> Dict:
        """
        Extract PDF metadata.

        Returns:
            Dictionary containing PDF metadata
        """
        metadata = self.doc.metadata

        return {
            "title": metadata.get("title", ""),
            "author": metadata.get("author", ""),
            "subject": metadata.get("subject", ""),
            "keywords": metadata.get("keywords", ""),
            "creator": metadata.get("creator", ""),
            "producer": metadata.get("producer", ""),
            "creation_date": metadata.get("creationDate", ""),
            "modification_date": metadata.get("modDate", ""),
            "page_count": self.page_count
        }

    def search_text(self, query: str, case_sensitive: bool = False) -> List[Tuple[int, List]]:
        """
        Search for text across all pages.

        Args:
            query: Text to search for
            case_sensitive: Whether search should be case-sensitive

        Returns:
            List of (page_num, instances) tuples
        """
        results = []

        for page_num in range(self.page_count):
            page = self.doc[page_num]
            flags = 0 if case_sensitive else fitz.TEXT_PRESERVE_WHITESPACE

            instances = page.search_for(query, flags=flags)

            if instances:
                results.append((page_num, instances))

        return results

    def get_page_images(self, page_num: int) -> List[Dict]:
        """
        Extract images from a specific page.

        Args:
            page_num: Page number (0-indexed)

        Returns:
            List of image metadata dictionaries
        """
        if page_num < 0 or page_num >= self.page_count:
            raise ValueError(f"Page number {page_num} out of range")

        page = self.doc[page_num]
        images = []

        for img_index, img in enumerate(page.get_images(full=True)):
            xref = img[0]
            base_image = self.doc.extract_image(xref)

            images.append({
                "index": img_index,
                "xref": xref,
                "width": base_image.get("width"),
                "height": base_image.get("height"),
                "colorspace": base_image.get("colorspace"),
                "bpc": base_image.get("bpc"),  # bits per component
                "ext": base_image.get("ext"),  # extension
                "image_data": base_image.get("image")  # binary data
            })

        return images

    def get_first_page_text(self, clean: bool = True) -> str:
        """
        Get text from the first page (often contains title and authors).

        Args:
            clean: Whether to apply text cleaning

        Returns:
            First page text
        """
        return self.get_page_text(0, clean=clean)

    def get_toc(self) -> List[Dict]:
        """
        Extract table of contents if available.

        Returns:
            List of TOC entries with level, title, and page number
        """
        toc = self.doc.get_toc()

        structured_toc = []
        for entry in toc:
            level, title, page = entry
            structured_toc.append({
                "level": level,
                "title": title.strip(),
                "page": page
            })

        return structured_toc

    def close(self):
        """Close the PDF document and free resources."""
        if self.doc:
            self.doc.close()

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.close()

    def __repr__(self):
        return f"PDFParser('{self.pdf_path.name}', pages={self.page_count})"
