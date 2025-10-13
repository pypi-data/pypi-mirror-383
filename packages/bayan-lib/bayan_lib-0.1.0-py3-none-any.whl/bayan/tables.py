"""
Table and figure extraction module for academic papers.
"""

import re
from typing import List, Dict, Optional, Tuple
from bayan.parser import PDFParser
from bayan.cleaner import TextCleaner
from bayan.utils import RegexPatterns

# Optional imports for pandas and matplotlib
try:
    import pandas as pd
    HAS_PANDAS = True
except ImportError:
    HAS_PANDAS = False

try:
    import matplotlib.pyplot as plt
    from matplotlib.figure import Figure
    import numpy as np
    HAS_MATPLOTLIB = True
except ImportError:
    HAS_MATPLOTLIB = False

try:
    from PIL import Image
    import io
    HAS_PIL = True
except ImportError:
    HAS_PIL = False


class TableExtractor:
    """
    Extracts tables and figures with captions and context from academic papers.
    """

    def __init__(self, parser: PDFParser):
        """
        Initialize table extractor.

        Args:
            parser: PDFParser instance
        """
        self.parser = parser
        self.cleaner = TextCleaner()

    def extract_tables(self) -> List[Dict]:
        """
        Extract tables with captions and content.

        Returns:
            List of table dictionaries containing:
                - number: Table number
                - caption: Table caption
                - content: Table content (list of rows)
                - page: Page number
                - raw_text: Raw text of the table
        """
        tables = []
        full_text = self.parser.get_full_text(clean=True)

        # Find table captions
        caption_matches = list(RegexPatterns.TABLE_CAPTION.finditer(full_text))

        for match in caption_matches:
            table_num = match.group(1)
            caption = match.group(2).strip()

            # Clean caption
            caption = self.cleaner.clean(caption, preserve_structure=False)
            caption = caption.replace("\n", " ")

            # Find which page this table is on
            page_num = self._find_page_for_text(match.group(0)[:100])

            # Try to extract table content near the caption
            table_content = self._extract_table_content(match.end(), full_text, page_num)

            tables.append({
                "number": table_num,
                "caption": caption,
                "content": table_content["rows"],
                "page": page_num,
                "raw_text": table_content["raw_text"]
            })

        return tables

    def extract_figures(self) -> List[Dict]:
        """
        Extract figures with captions and metadata.

        Returns:
            List of figure dictionaries containing:
                - number: Figure number
                - caption: Figure caption
                - page: Page number
                - image_data: Image metadata if available
        """
        figures = []
        full_text = self.parser.get_full_text(clean=True)

        # Find figure captions
        caption_matches = list(RegexPatterns.FIGURE_CAPTION.finditer(full_text))

        for match in caption_matches:
            fig_num = match.group(1)
            caption = match.group(2).strip()

            # Clean caption
            caption = self.cleaner.clean(caption, preserve_structure=False)
            caption = caption.replace("\n", " ")

            # Find which page this figure is on
            page_num = self._find_page_for_text(match.group(0)[:100])

            # Try to get image data
            image_data = None
            if page_num is not None:
                images = self.parser.get_page_images(page_num)
                if images:
                    # Get the largest image on the page (likely the figure)
                    image_data = max(images, key=lambda x: x["width"] * x["height"])
                    # Remove binary data for the summary
                    image_data = {k: v for k, v in image_data.items() if k != "image_data"}

            figures.append({
                "number": fig_num,
                "caption": caption,
                "page": page_num,
                "image_metadata": image_data
            })

        return figures

    def _find_page_for_text(self, text: str) -> Optional[int]:
        """
        Find which page contains specific text.

        Args:
            text: Text to search for

        Returns:
            Page number (0-indexed) or None
        """
        # Search first 100 characters for efficiency
        search_text = text[:100]

        for page_num in range(self.parser.page_count):
            page_text = self.parser.get_page_text(page_num, clean=True)
            if search_text in page_text:
                return page_num

        return None

    def _extract_table_content(self, start_pos: int, full_text: str, page_num: Optional[int]) -> Dict:
        """
        Extract table content following a caption.

        Args:
            start_pos: Position in text where table should start
            full_text: Full paper text
            page_num: Page number where table is located

        Returns:
            Dictionary with table rows and raw text
        """
        # Get text following the caption (next ~1000 characters)
        table_region = full_text[start_pos:start_pos + 1000]

        # Stop at next section marker or figure/table
        end_markers = [
            "\nTable ", "\nFigure ", "\nFig. ",
            "\n\n\n",  # Multiple blank lines
        ]

        end_pos = len(table_region)
        for marker in end_markers:
            pos = table_region.find(marker)
            if pos != -1 and pos < end_pos:
                end_pos = pos

        table_text = table_region[:end_pos].strip()

        # Try to parse as rows
        rows = self._parse_table_rows(table_text)

        return {
            "rows": rows,
            "raw_text": table_text
        }

    def _parse_table_rows(self, text: str) -> List[List[str]]:
        """
        Attempt to parse table text into rows and columns.

        Args:
            text: Raw table text

        Returns:
            List of rows (each row is a list of cell values)
        """
        rows = []
        lines = text.split("\n")

        for line in lines:
            line = line.strip()
            if not line:
                continue

            # Try different delimiters
            cells = None

            # Tab-separated
            if "\t" in line:
                cells = [c.strip() for c in line.split("\t")]

            # Multiple spaces (common in plain text tables)
            elif "  " in line:
                cells = [c.strip() for c in re.split(r'\s{2,}', line)]

            # Pipe-separated
            elif "|" in line:
                cells = [c.strip() for c in line.split("|") if c.strip()]

            # Single words per line (vertical table)
            else:
                cells = [line]

            if cells and any(cells):  # At least one non-empty cell
                rows.append(cells)

        # Filter out likely header separators
        rows = [row for row in rows if not self._is_separator_row(row)]

        return rows

    def _is_separator_row(self, row: List[str]) -> bool:
        """
        Check if a row is likely a separator (e.g., "---" or "===").

        Args:
            row: Table row

        Returns:
            True if row is a separator
        """
        if not row:
            return True

        # Check if all cells are made of separator characters
        separator_chars = set("-=_")

        for cell in row:
            if cell and not all(c in separator_chars or c.isspace() for c in cell):
                return False

        return True

    def extract_table_by_number(self, table_num: str) -> Optional[Dict]:
        """
        Extract a specific table by its number.

        Args:
            table_num: Table number (e.g., "1", "I", "A")

        Returns:
            Table dictionary or None if not found
        """
        tables = self.extract_tables()

        for table in tables:
            if table["number"] == str(table_num):
                return table

        return None

    def extract_figure_by_number(self, fig_num: str) -> Optional[Dict]:
        """
        Extract a specific figure by its number.

        Args:
            fig_num: Figure number (e.g., "1", "2a")

        Returns:
            Figure dictionary or None if not found
        """
        figures = self.extract_figures()

        for figure in figures:
            if figure["number"] == str(fig_num):
                return figure

        return None

    def get_table_summary(self) -> List[Dict]:
        """
        Get a summary of all tables (without full content).

        Returns:
            List of table summaries
        """
        tables = self.extract_tables()

        summaries = []
        for table in tables:
            summaries.append({
                "number": table["number"],
                "caption": table["caption"],
                "page": table["page"],
                "row_count": len(table["content"])
            })

        return summaries

    def get_figure_summary(self) -> List[Dict]:
        """
        Get a summary of all figures.

        Returns:
            List of figure summaries
        """
        figures = self.extract_figures()

        summaries = []
        for figure in figures:
            summaries.append({
                "number": figure["number"],
                "caption": figure["caption"],
                "page": figure["page"]
            })

        return summaries

    def export_table_to_csv(self, table_num: str) -> Optional[str]:
        """
        Export a specific table to CSV format.

        Args:
            table_num: Table number

        Returns:
            CSV string or None if table not found
        """
        table = self.extract_table_by_number(table_num)

        if not table or not table["content"]:
            return None

        # Convert rows to CSV
        csv_lines = []
        for row in table["content"]:
            # Escape cells with commas or quotes
            escaped_row = []
            for cell in row:
                if "," in cell or '"' in cell:
                    cell = '"' + cell.replace('"', '""') + '"'
                escaped_row.append(cell)

            csv_lines.append(",".join(escaped_row))

        return "\n".join(csv_lines)

    def extract_equations(self) -> List[Dict]:
        """
        Extract mathematical equations from the paper.

        Returns:
            List of equation dictionaries
        """
        equations = []
        full_text = self.parser.get_full_text(clean=False)

        # Look for LaTeX-style equations
        # Inline equations: $...$
        inline_matches = re.finditer(r'\$([^\$]+)\$', full_text)
        for match in inline_matches:
            equations.append({
                "type": "inline",
                "content": match.group(1).strip(),
                "position": match.start()
            })

        # Display equations: $$...$$ or \[...\] or equation environment
        display_patterns = [
            r'\$\$([^\$]+)\$\$',
            r'\\\[(.+?)\\\]',
            r'\\begin\{equation\}(.+?)\\end\{equation\}',
        ]

        for pattern in display_patterns:
            matches = re.finditer(pattern, full_text, re.DOTALL)
            for match in matches:
                equations.append({
                    "type": "display",
                    "content": match.group(1).strip(),
                    "position": match.start()
                })

        # Number equations
        numbered_eq_pattern = r'\((\d+)\)\s*$'
        for eq in equations:
            # Check if equation has a number
            match = re.search(numbered_eq_pattern, eq["content"])
            if match:
                eq["number"] = match.group(1)
                eq["content"] = eq["content"][:match.start()].strip()

        return equations

    def get_table_as_dataframe(self, table_num: str) -> Optional['pd.DataFrame']:
        """
        Get a table as a pandas DataFrame.

        Args:
            table_num: Table number (e.g., "1", "I", "A")

        Returns:
            pandas DataFrame or None if table not found or pandas not installed

        Raises:
            ImportError: If pandas is not installed
        """
        if not HAS_PANDAS:
            raise ImportError(
                "pandas is required for DataFrame support. "
                "Install with: pip install pandas"
            )

        table = self.extract_table_by_number(table_num)

        if not table or not table["content"]:
            return None

        rows = table["content"]

        if len(rows) == 0:
            return pd.DataFrame()

        # Use first row as headers if it looks like headers
        if len(rows) > 1:
            # Check if first row contains mostly text (not numbers)
            first_row_text = sum(1 for cell in rows[0] if not cell.replace('.', '').replace('-', '').isdigit())
            if first_row_text > len(rows[0]) / 2:
                # First row is likely headers
                df = pd.DataFrame(rows[1:], columns=rows[0])
            else:
                # No clear headers, use default column names
                df = pd.DataFrame(rows)
        else:
            df = pd.DataFrame(rows)

        # Add metadata as attributes
        df.attrs['table_number'] = table['number']
        df.attrs['caption'] = table['caption']
        df.attrs['page'] = table['page']

        return df

    def get_all_tables_as_dataframes(self) -> Dict[str, 'pd.DataFrame']:
        """
        Get all tables as pandas DataFrames.

        Returns:
            Dictionary mapping table numbers to DataFrames

        Raises:
            ImportError: If pandas is not installed
        """
        if not HAS_PANDAS:
            raise ImportError(
                "pandas is required for DataFrame support. "
                "Install with: pip install pandas"
            )

        tables = self.extract_tables()
        dataframes = {}

        for table in tables:
            table_num = table["number"]
            rows = table["content"]

            if len(rows) == 0:
                continue

            # Use first row as headers if it looks like headers
            if len(rows) > 1:
                first_row_text = sum(1 for cell in rows[0] if not cell.replace('.', '').replace('-', '').isdigit())
                if first_row_text > len(rows[0]) / 2:
                    df = pd.DataFrame(rows[1:], columns=rows[0])
                else:
                    df = pd.DataFrame(rows)
            else:
                df = pd.DataFrame(rows)

            # Add metadata
            df.attrs['table_number'] = table['number']
            df.attrs['caption'] = table['caption']
            df.attrs['page'] = table['page']

            dataframes[table_num] = df

        return dataframes

    def plot_figure(self, fig_num: str, figsize: Tuple[int, int] = (10, 8),
                   save_path: Optional[str] = None) -> Optional[Figure]:
        """
        Plot a figure using matplotlib.

        Args:
            fig_num: Figure number (e.g., "1", "2a")
            figsize: Figure size as (width, height) in inches
            save_path: Optional path to save the figure

        Returns:
            matplotlib Figure object or None if figure not found

        Raises:
            ImportError: If matplotlib or PIL is not installed
        """
        if not HAS_MATPLOTLIB:
            raise ImportError(
                "matplotlib is required for figure plotting. "
                "Install with: pip install matplotlib"
            )

        if not HAS_PIL:
            raise ImportError(
                "Pillow (PIL) is required for image handling. "
                "Install with: pip install Pillow"
            )

        figure = self.extract_figure_by_number(fig_num)

        if not figure:
            return None

        # Get the image data from the PDF
        page_num = figure.get("page")
        if page_num is None:
            print(f"Warning: Could not determine page for Figure {fig_num}")
            return None

        images = self.parser.get_page_images(page_num)

        if not images:
            print(f"Warning: No images found on page {page_num} for Figure {fig_num}")
            return None

        # Get the largest image (likely the figure)
        image_data = max(images, key=lambda x: x["width"] * x["height"])

        # Convert image bytes to PIL Image
        img_bytes = image_data["image_data"]
        img = Image.open(io.BytesIO(img_bytes))

        # Create matplotlib figure
        fig, ax = plt.subplots(figsize=figsize)
        ax.imshow(img)
        ax.axis('off')

        # Add title with caption
        caption = figure.get("caption", "")
        title = f"Figure {fig_num}"
        if caption:
            title += f": {caption[:100]}{'...' if len(caption) > 100 else ''}"
        fig.suptitle(title, fontsize=12, wrap=True)

        plt.tight_layout()

        # Save if requested
        if save_path:
            fig.savefig(save_path, dpi=300, bbox_inches='tight')
            print(f"Figure saved to {save_path}")

        return fig

    def plot_all_figures(self, figsize: Tuple[int, int] = (10, 8),
                        save_dir: Optional[str] = None) -> List[Figure]:
        """
        Plot all figures in the paper.

        Args:
            figsize: Figure size as (width, height) in inches
            save_dir: Optional directory to save figures

        Returns:
            List of matplotlib Figure objects

        Raises:
            ImportError: If matplotlib or PIL is not installed
        """
        if not HAS_MATPLOTLIB:
            raise ImportError(
                "matplotlib is required for figure plotting. "
                "Install with: pip install matplotlib"
            )

        if not HAS_PIL:
            raise ImportError(
                "Pillow (PIL) is required for image handling. "
                "Install with: pip install Pillow"
            )

        figures = self.extract_figures()
        plot_figures = []

        for figure in figures:
            fig_num = figure["number"]

            save_path = None
            if save_dir:
                import os
                os.makedirs(save_dir, exist_ok=True)
                save_path = os.path.join(save_dir, f"figure_{fig_num}.png")

            fig = self.plot_figure(fig_num, figsize=figsize, save_path=save_path)

            if fig:
                plot_figures.append(fig)

        return plot_figures

    def save_figure_image(self, fig_num: str, output_path: str) -> bool:
        """
        Save a figure's raw image to file.

        Args:
            fig_num: Figure number
            output_path: Path to save the image

        Returns:
            True if successful, False otherwise

        Raises:
            ImportError: If PIL is not installed
        """
        if not HAS_PIL:
            raise ImportError(
                "Pillow (PIL) is required for image saving. "
                "Install with: pip install Pillow"
            )

        figure = self.extract_figure_by_number(fig_num)

        if not figure:
            return False

        page_num = figure.get("page")
        if page_num is None:
            return False

        images = self.parser.get_page_images(page_num)

        if not images:
            return False

        # Get the largest image
        image_data = max(images, key=lambda x: x["width"] * x["height"])
        img_bytes = image_data["image_data"]

        # Save directly
        with open(output_path, 'wb') as f:
            f.write(img_bytes)

        return True
