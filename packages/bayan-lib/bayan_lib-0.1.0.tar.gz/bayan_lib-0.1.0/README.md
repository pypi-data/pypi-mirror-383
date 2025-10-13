# بيان bayan

**Bring clarity to research papers.**

`bayan` is a Python library that extracts structured, meaningful information from academic PDFs — including metadata, sections, references, tables, and figures — with clean, consistent output formats.

Designed for researchers, developers, and data scientists who need to transform unstructured papers into readable or machine-processable data.

✨ **Features:** Runs locally, requires no API keys (optional LLM integration available), and works with any research PDF.

---

## Features

| Feature | Description |
|---------|-------------|
| 🧾 **Metadata Extraction** | Title, authors, affiliations, DOI, publication year |
| 📑 **Section Detection** | Identify Abstract, Introduction, Methodology, Results, Discussion, Conclusion |
| 🔍 **Reference Parsing** | Extract and format citations into structured JSON |
| 📊 **Table & Figure Extraction** | Detect and extract tables with context and captions |
| 🐼 **pandas DataFrames** | Convert tables to DataFrames for easy analysis |
| 📈 **matplotlib Plotting** | Visualize figures directly with matplotlib |
| 🧹 **Text Cleaning** | Normalize spacing, remove artifacts, preserve layout |
| 💾 **Exports** | JSON, Markdown, CSV, TXT, and BibTeX |
| 🧠 **Optional AI Layer** | Summarization and paper-type detection via OpenAI, Claude, or local models |

---

## Installation

### Basic Installation

```bash
pip install bayan
```

### With LLM Support

```bash
# For OpenAI/Claude integration
pip install bayan[llm]

# For HuggingFace models
pip install bayan[ml]

# Everything
pip install bayan[all]
```

### From Source

```bash
git clone https://github.com/atomicKhalil/bayan.git
cd bayan
pip install -e .
```

---

## Quick Start

### Basic Usage

```python
from bayan import Paper

# Load a paper
paper = Paper("research_paper.pdf")

# Extract metadata
meta = paper.extract_metadata()
print(f"Title: {meta['title']}")
print(f"Authors: {', '.join(meta['authors'])}")
print(f"Year: {meta['year']}")

# Extract sections
sections = paper.extract_sections()
print("\nAbstract:")
print(sections.get("abstract", "Not found"))

# Extract references
references = paper.extract_references()
print(f"\nFound {len(references)} references")

# Extract tables and figures
tables = paper.extract_tables()
figures = paper.extract_figures()
print(f"Tables: {len(tables)}, Figures: {len(figures)}")

# Export everything
paper.export("json", "output.json")
paper.export("markdown", "output.md")
```

### With Context Manager

```python
from bayan import Paper

with Paper("paper.pdf") as paper:
    data = paper.extract_all()
    paper.export("json", "paper_data.json")
```

### Export Formats

```python
paper = Paper("paper.pdf")

# JSON (structured data)
paper.export("json", "paper.json")

# Markdown (readable format)
paper.export("markdown", "paper.md")

# CSV (flattened data)
paper.export("csv", "paper.csv")

# Plain text
paper.export("txt", "paper.txt")
```

---

## Advanced Features

### LLM Integration

Enable AI-powered summarization and classification:

```python
from bayan import Paper

paper = Paper("paper.pdf")

# Enable OpenAI
paper.enable_llm(provider="openai", api_key="sk-...")

# Summarize a section
summary = paper.summarize("methodology", max_length=150)
print(summary)

# Classify the paper
classification = paper.classify()
print(f"Type: {classification['paper_type']}")
print(f"Domain: {classification['domain']}")
```

#### Supported LLM Providers

```python
# OpenAI
paper.enable_llm(provider="openai", api_key="sk-...")

# Anthropic Claude
paper.enable_llm(provider="anthropic", api_key="sk-ant-...")

# HuggingFace
paper.enable_llm(provider="huggingface", model_name="facebook/bart-large-cnn")

# Local (Ollama)
paper.enable_llm(provider="local", base_url="http://localhost:11434", model_name="llama2")
```

### Extract Specific Elements

```python
paper = Paper("paper.pdf")

# Get just the abstract
abstract = paper.extract_abstract()

# Get a quick summary
summary = paper.get_paper_summary()

# Extract specific table
table = paper.table_extractor.extract_table_by_number("1")

# Export table to CSV
csv_data = paper.table_extractor.export_table_to_csv("1")
```

### Working with Sections

```python
sections = paper.extract_sections()

# Available sections (when detected)
print(sections.keys())
# ['abstract', 'introduction', 'methodology', 'results', 'conclusion', ...]

# Access specific sections
print(sections['abstract'])
print(sections['methodology'])
```

### Tables as pandas DataFrames

**NEW FEATURE!** Convert tables to pandas DataFrames for easy analysis:

```python
from bayan import Paper

paper = Paper("paper.pdf")

# Get a specific table as DataFrame
df = paper.table_extractor.get_table_as_dataframe("1")
print(df)

# Access metadata
print(df.attrs['caption'])  # Table caption
print(df.attrs['page'])     # Page number

# Use all pandas operations
print(df.describe())
print(df.head())
df.to_csv("table_1.csv")

# Get all tables as DataFrames
tables_df = paper.table_extractor.get_all_tables_as_dataframes()
for table_num, df in tables_df.items():
    print(f"Table {table_num}: {df.shape}")
```

### Plot Figures with matplotlib

**NEW FEATURE!** Visualize figures directly from the PDF:

```python
from bayan import Paper

paper = Paper("paper.pdf")

# Plot a specific figure
fig = paper.table_extractor.plot_figure(
    "1",                      # Figure number
    figsize=(12, 8),          # Size in inches
    save_path="figure1.png"   # Save location (optional)
)

# Plot all figures
figs = paper.table_extractor.plot_all_figures(
    figsize=(10, 8),
    save_dir="figures/"  # Save to directory
)

# Save raw image
paper.table_extractor.save_figure_image("1", "fig1_raw.png")
```

**Installation for DataFrame & Plotting Features:**
```bash
pip install pandas matplotlib Pillow
```

---

## Example Output

### JSON Format

```json
{
  "metadata": {
    "title": "SecureBERT: Hash-Based Tampering Detection",
    "authors": ["John Doe", "Khalil Selmi"],
    "year": 2025,
    "doi": "10.1000/xyz123",
    "affiliations": ["MIT", "Stanford University"],
    "keywords": ["BERT", "security", "NLP"]
  },
  "sections": {
    "abstract": "This paper presents...",
    "introduction": "Natural language processing...",
    "methodology": "We propose a novel approach..."
  },
  "references": [
    {
      "id": 1,
      "text": "Devlin J. et al., BERT: Pre-training, 2019",
      "year": 2019
    }
  ],
  "tables": [
    {
      "number": "1",
      "caption": "Performance comparison",
      "content": [
        ["Model", "Accuracy"],
        ["BERT", "91.2%"]
      ]
    }
  ]
}
```

---

## Command Line Interface

```bash
# Extract and export to JSON
bayan extract paper.pdf --format json --output output.json

# Extract with metadata only
bayan extract paper.pdf --metadata-only --output meta.json

# Batch process
bayan batch papers/*.pdf --output-dir results/
```

---

## Use Cases

### Research Workflows

```python
from bayan import Paper
import glob

# Process multiple papers
papers = glob.glob("papers/*.pdf")

results = []
for pdf_path in papers:
    paper = Paper(pdf_path)
    meta = paper.extract_metadata()
    results.append({
        "title": meta["title"],
        "authors": meta["authors"],
        "year": meta["year"]
    })

# Create bibliography
import json
with open("bibliography.json", "w") as f:
    json.dump(results, f, indent=2)
```

### Literature Review

```python
from bayan import Paper

# Extract key information
paper = Paper("paper.pdf")
paper.enable_llm(provider="openai", api_key="...")

# Get structured summary
summary = paper.get_paper_summary()
abstract = paper.extract_abstract()

# Export to markdown for notes
paper.export("markdown", "notes.md")
```

### Data Extraction

```python
from bayan import Paper

# Extract tables for analysis
paper = Paper("paper.pdf")
tables = paper.extract_tables()

# Export each table
for table in tables:
    csv_data = paper.table_extractor.export_table_to_csv(table["number"])
    with open(f"table_{table['number']}.csv", "w") as f:
        f.write(csv_data)
```

---

## Architecture

```
bayan/
├── __init__.py          # Main Paper interface
├── parser.py            # PDF parsing (PyMuPDF)
├── extractor.py         # Metadata, sections, references
├── tables.py            # Table and figure extraction
├── cleaner.py           # Text normalization
├── exporter.py          # JSON, Markdown, CSV exports
├── utils.py             # Shared utilities
└── llm_client.py        # Optional LLM integration
```

---

## Design Principles

| Principle | Explanation |
|-----------|-------------|
| **Lightweight** | No dependencies on external servers or keys (core features) |
| **Modular** | Use or extend specific modules independently |
| **Universal** | Works on any research PDF, regardless of layout |
| **Transparent** | Clean, interpretable JSON outputs |
| **Expandable** | Optional LLM interface for advanced features |

---

## Requirements

- Python 3.8+
- PyMuPDF (fitz)
- pdfminer.six

**Optional:**
- pandas (for DataFrame support)
- matplotlib (for figure plotting)
- Pillow (for image handling)
- openai (for OpenAI integration)
- anthropic (for Claude integration)
- transformers + torch (for HuggingFace models)

---

## Development

### Running Tests

```bash
pytest tests/
```

### Code Formatting

```bash
black bayan/
flake8 bayan/
```

### Type Checking

```bash
mypy bayan/
```

---

## Roadmap

- [ ] CLI implementation
- [ ] Batch processing support
- [ ] Advanced table parsing (complex layouts)
- [ ] Citation graph extraction
- [ ] PDF generation from extracted data
- [ ] Web interface
- [ ] Support for arXiv direct downloads
- [ ] Multi-language support

---

## Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

1. Fork the repository
2. Create your feature branch (`git checkout -b feature/AmazingFeature`)
3. Commit your changes (`git commit -m 'Add some AmazingFeature'`)
4. Push to the branch (`git push origin feature/AmazingFeature`)
5. Open a Pull Request

---

## License

MIT License - free for all academic and commercial use.

---

## Citation

If you use `bayan` in your research, please cite:

```bibtex
@software{bayan2025,
  author = {Selmi, Khalil},
  title = {bayan: Bring clarity to research papers},
  year = {2025},
  url = {https://github.com/atomicKhalil/bayan}
}
```

---

## Acknowledgments

Built with:
- [PyMuPDF](https://pymupdf.readthedocs.io/) for PDF parsing
- [pdfminer.six](https://github.com/pdfminer/pdfminer.six) for text extraction
- Support for OpenAI, Anthropic, and HuggingFace models

---

## Support

- **Documentation:** [GitHub Wiki](https://github.com/atomicKhalil/bayan/wiki)
- **Issues:** [GitHub Issues](https://github.com/atomicKhalil/bayan/issues)
- **Discussions:** [GitHub Discussions](https://github.com/atomicKhalil/bayan/discussions)

---

**بيان bayan** — *From PDFs to structured knowledge.*
