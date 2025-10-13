"""
Export module for converting extracted data to various formats.
"""

import json
import csv
from pathlib import Path
from typing import Dict, Any, List
from datetime import datetime


class PaperExporter:
    """
    Exports paper data to JSON, Markdown, CSV, and TXT formats.
    """

    def __init__(self):
        """Initialize exporter."""
        pass

    def export(self, data: Dict, format: str, output_path: str):
        """
        Export data to specified format.

        Args:
            data: Extracted paper data
            format: Output format ('json', 'markdown', 'csv', 'txt')
            output_path: Path to save the output

        Raises:
            ValueError: If format is not supported
        """
        format = format.lower()

        exporters = {
            "json": self.to_json,
            "markdown": self.to_markdown,
            "md": self.to_markdown,
            "csv": self.to_csv,
            "txt": self.to_txt,
            "text": self.to_txt,
        }

        if format not in exporters:
            raise ValueError(
                f"Unsupported format: {format}. "
                f"Supported formats: {', '.join(exporters.keys())}"
            )

        exporters[format](data, output_path)

    def to_json(self, data: Dict, output_path: str):
        """
        Export to JSON format.

        Args:
            data: Paper data
            output_path: Output file path
        """
        # Ensure output directory exists
        Path(output_path).parent.mkdir(parents=True, exist_ok=True)

        with open(output_path, "w", encoding="utf-8") as f:
            json.dump(data, f, indent=2, ensure_ascii=False)

    def to_markdown(self, data: Dict, output_path: str):
        """
        Export to Markdown format.

        Args:
            data: Paper data
            output_path: Output file path
        """
        Path(output_path).parent.mkdir(parents=True, exist_ok=True)

        lines = []

        # Title
        metadata = data.get("metadata", {})
        title = metadata.get("title", "Unknown Title")
        lines.append(f"# {title}\n")

        # Authors
        authors = metadata.get("authors", [])
        if authors:
            lines.append("## Authors\n")
            for author in authors:
                lines.append(f"- {author}")
            lines.append("")

        # Metadata
        lines.append("## Metadata\n")

        if metadata.get("year"):
            lines.append(f"**Year:** {metadata['year']}")

        if metadata.get("doi"):
            lines.append(f"**DOI:** {metadata['doi']}")

        if metadata.get("arxiv_id"):
            lines.append(f"**arXiv:** {metadata['arxiv_id']}")

        if metadata.get("affiliations"):
            lines.append(f"\n**Affiliations:**")
            for affiliation in metadata["affiliations"]:
                lines.append(f"- {affiliation}")

        if metadata.get("keywords"):
            keywords = ", ".join(metadata["keywords"])
            lines.append(f"\n**Keywords:** {keywords}")

        lines.append("")

        # Sections
        sections = data.get("sections", {})
        if sections:
            lines.append("## Sections\n")

            # Priority order for sections
            priority_sections = [
                "abstract", "introduction", "related_work",
                "methodology", "experiments", "results",
                "discussion", "conclusion"
            ]

            # Add priority sections first
            for section_name in priority_sections:
                if section_name in sections:
                    title = section_name.replace("_", " ").title()
                    lines.append(f"### {title}\n")
                    lines.append(sections[section_name])
                    lines.append("")

            # Add remaining sections
            for section_name, content in sections.items():
                if section_name not in priority_sections:
                    title = section_name.replace("_", " ").title()
                    lines.append(f"### {title}\n")
                    lines.append(content)
                    lines.append("")

        # Tables
        tables = data.get("tables", [])
        if tables:
            lines.append("## Tables\n")
            for table in tables:
                lines.append(f"### Table {table['number']}: {table['caption']}\n")

                if table.get("content"):
                    # Format as markdown table
                    rows = table["content"]
                    if rows:
                        # Header row
                        lines.append("| " + " | ".join(rows[0]) + " |")
                        lines.append("| " + " | ".join(["---"] * len(rows[0])) + " |")

                        # Data rows
                        for row in rows[1:]:
                            # Pad row if needed
                            padded_row = row + [""] * (len(rows[0]) - len(row))
                            lines.append("| " + " | ".join(padded_row) + " |")

                lines.append("")

        # Figures
        figures = data.get("figures", [])
        if figures:
            lines.append("## Figures\n")
            for figure in figures:
                lines.append(f"### Figure {figure['number']}: {figure['caption']}\n")

        # References
        references = data.get("references", [])
        if references:
            lines.append("## References\n")
            for ref in references:
                ref_id = ref.get("id", "?")
                ref_text = ref.get("text", "")
                lines.append(f"{ref_id}. {ref_text}")
            lines.append("")

        # Write to file
        with open(output_path, "w", encoding="utf-8") as f:
            f.write("\n".join(lines))

    def to_csv(self, data: Dict, output_path: str):
        """
        Export to CSV format (flattened structure).

        Args:
            data: Paper data
            output_path: Output file path
        """
        Path(output_path).parent.mkdir(parents=True, exist_ok=True)

        metadata = data.get("metadata", {})
        sections = data.get("sections", {})

        # Flatten data
        rows = []

        # Basic metadata
        rows.append(["Field", "Value"])
        rows.append(["Title", metadata.get("title", "")])
        rows.append(["Authors", "; ".join(metadata.get("authors", []))])
        rows.append(["Year", metadata.get("year", "")])
        rows.append(["DOI", metadata.get("doi", "")])
        rows.append(["arXiv ID", metadata.get("arxiv_id", "")])
        rows.append(["Keywords", "; ".join(metadata.get("keywords", []))])
        rows.append(["Page Count", metadata.get("page_count", "")])

        # Sections
        rows.append([])
        rows.append(["Section", "Content"])

        for section_name, content in sections.items():
            # Truncate long content for CSV
            truncated = content[:500] + "..." if len(content) > 500 else content
            rows.append([section_name, truncated.replace("\n", " ")])

        # Tables
        if data.get("tables"):
            rows.append([])
            rows.append(["Table Number", "Caption", "Page"])
            for table in data["tables"]:
                rows.append([
                    table.get("number", ""),
                    table.get("caption", ""),
                    table.get("page", "")
                ])

        # Figures
        if data.get("figures"):
            rows.append([])
            rows.append(["Figure Number", "Caption", "Page"])
            for figure in data["figures"]:
                rows.append([
                    figure.get("number", ""),
                    figure.get("caption", ""),
                    figure.get("page", "")
                ])

        # Write CSV
        with open(output_path, "w", encoding="utf-8", newline="") as f:
            writer = csv.writer(f)
            writer.writerows(rows)

    def to_txt(self, data: Dict, output_path: str):
        """
        Export to plain text format.

        Args:
            data: Paper data
            output_path: Output file path
        """
        Path(output_path).parent.mkdir(parents=True, exist_ok=True)

        lines = []

        # Header
        lines.append("=" * 80)
        lines.append("PAPER EXTRACTION REPORT")
        lines.append(f"Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        lines.append("=" * 80)
        lines.append("")

        # Metadata
        metadata = data.get("metadata", {})
        lines.append("METADATA")
        lines.append("-" * 80)
        lines.append(f"Title: {metadata.get('title', 'Unknown')}")

        authors = metadata.get("authors", [])
        if authors:
            lines.append(f"Authors: {', '.join(authors)}")

        if metadata.get("year"):
            lines.append(f"Year: {metadata['year']}")

        if metadata.get("doi"):
            lines.append(f"DOI: {metadata['doi']}")

        if metadata.get("arxiv_id"):
            lines.append(f"arXiv: {metadata['arxiv_id']}")

        if metadata.get("keywords"):
            lines.append(f"Keywords: {', '.join(metadata['keywords'])}")

        lines.append(f"Page Count: {metadata.get('page_count', 'Unknown')}")
        lines.append("")

        # Affiliations
        affiliations = metadata.get("affiliations", [])
        if affiliations:
            lines.append("AFFILIATIONS")
            lines.append("-" * 80)
            for i, aff in enumerate(affiliations, 1):
                lines.append(f"{i}. {aff}")
            lines.append("")

        # Sections
        sections = data.get("sections", {})
        if sections:
            priority_sections = [
                "abstract", "introduction", "related_work",
                "methodology", "experiments", "results",
                "discussion", "conclusion"
            ]

            for section_name in priority_sections:
                if section_name in sections:
                    title = section_name.replace("_", " ").upper()
                    lines.append(title)
                    lines.append("-" * 80)
                    lines.append(sections[section_name])
                    lines.append("")

            # Remaining sections
            for section_name, content in sections.items():
                if section_name not in priority_sections:
                    title = section_name.replace("_", " ").upper()
                    lines.append(title)
                    lines.append("-" * 80)
                    lines.append(content)
                    lines.append("")

        # Tables
        tables = data.get("tables", [])
        if tables:
            lines.append("TABLES")
            lines.append("-" * 80)
            for table in tables:
                lines.append(f"\nTable {table['number']}: {table['caption']}")
                if table.get("raw_text"):
                    lines.append(table["raw_text"])
                lines.append("")

        # Figures
        figures = data.get("figures", [])
        if figures:
            lines.append("FIGURES")
            lines.append("-" * 80)
            for figure in figures:
                lines.append(f"Figure {figure['number']}: {figure['caption']}")
            lines.append("")

        # References
        references = data.get("references", [])
        if references:
            lines.append("REFERENCES")
            lines.append("-" * 80)
            for ref in references:
                ref_id = ref.get("id", "?")
                ref_text = ref.get("text", "")
                lines.append(f"[{ref_id}] {ref_text}")
            lines.append("")

        # Footer
        lines.append("=" * 80)
        lines.append("END OF REPORT")
        lines.append("=" * 80)

        # Write to file
        with open(output_path, "w", encoding="utf-8") as f:
            f.write("\n".join(lines))

    def export_metadata_only(self, data: Dict, output_path: str):
        """
        Export only metadata as JSON (lightweight).

        Args:
            data: Paper data
            output_path: Output file path
        """
        metadata = data.get("metadata", {})

        Path(output_path).parent.mkdir(parents=True, exist_ok=True)

        with open(output_path, "w", encoding="utf-8") as f:
            json.dump(metadata, f, indent=2, ensure_ascii=False)

    def export_sections_only(self, data: Dict, output_path: str):
        """
        Export only sections as JSON.

        Args:
            data: Paper data
            output_path: Output file path
        """
        sections = data.get("sections", {})

        Path(output_path).parent.mkdir(parents=True, exist_ok=True)

        with open(output_path, "w", encoding="utf-8") as f:
            json.dump(sections, f, indent=2, ensure_ascii=False)

    def export_bibtex(self, data: Dict, output_path: str):
        """
        Export metadata as BibTeX entry.

        Args:
            data: Paper data
            output_path: Output file path
        """
        metadata = data.get("metadata", {})

        title = metadata.get("title", "Unknown Title")
        authors = metadata.get("authors", [])
        year = metadata.get("year", "")
        doi = metadata.get("doi", "")

        # Create citation key
        first_author = authors[0].split()[-1] if authors else "Unknown"
        cite_key = f"{first_author}{year}".replace(" ", "")

        # Format authors (Last, First and ...)
        author_str = " and ".join(authors)

        lines = [
            f"@article{{{cite_key},",
            f'  title = {{{title}}},',
            f'  author = {{{author_str}}},',
            f'  year = {{{year}}},',
        ]

        if doi:
            lines.append(f'  doi = {{{doi}}},')

        lines.append("}")

        Path(output_path).parent.mkdir(parents=True, exist_ok=True)

        with open(output_path, "w", encoding="utf-8") as f:
            f.write("\n".join(lines))
