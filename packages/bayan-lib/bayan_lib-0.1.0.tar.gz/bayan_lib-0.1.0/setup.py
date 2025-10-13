"""
Setup script for bayan - Bring clarity to research papers.
"""

from setuptools import setup, find_packages
from pathlib import Path

# Read README for long description
readme_file = Path(__file__).parent / "README.md"
long_description = ""
if readme_file.exists():
    long_description = readme_file.read_text(encoding="utf-8")

# Read requirements
requirements_file = Path(__file__).parent / "requirements.txt"
requirements = []
if requirements_file.exists():
    requirements = [
        line.strip()
        for line in requirements_file.read_text(encoding="utf-8").split("\n")
        if line.strip() and not line.startswith("#")
    ]

setup(
    name="bayan-lib",
    version="0.1.0",
    author="Khalil Selmi",
    author_email="khalil.selmi.dev@gmail.com",
    description="Extract structured, meaningful information from academic PDFs",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/atomicKhalil/bayan",
    packages=find_packages(),
    classifiers=[
        "Development Status :: 3 - Alpha",
        "Intended Audience :: Developers",
        "Intended Audience :: Science/Research",
        "Topic :: Scientific/Engineering",
        "Topic :: Text Processing",
        "License :: OSI Approved :: MIT License",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
        "Programming Language :: Python :: 3.12",
    ],
    python_requires=">=3.8",
    install_requires=requirements,
    extras_require={
        "dataframe": [
            "pandas>=1.5.0",
            "matplotlib>=3.5.0",
            "Pillow>=9.0.0",
        ],
        "llm": [
            "openai>=1.0.0",
            "anthropic>=0.7.0",
        ],
        "ml": [
            "transformers>=4.30.0",
            "torch>=2.0.0",
        ],
        "all": [
            "pandas>=1.5.0",
            "matplotlib>=3.5.0",
            "Pillow>=9.0.0",
            "openai>=1.0.0",
            "anthropic>=0.7.0",
        ],
        "dev": [
            "pytest>=7.0.0",
            "black>=23.0.0",
            "flake8>=6.0.0",
            "mypy>=1.0.0",
        ],
    },
    keywords=[
        "pdf",
        "academic",
        "papers",
        "research",
        "extraction",
        "parsing",
        "scientific",
        "publications",
    ],
    project_urls={
        "Bug Reports": "https://github.com/atomicKhalil/bayan/issues",
        "Source": "https://github.com/atomicKhalil/bayan",
        "Documentation": "https://github.com/atomicKhalil/bayan#readme",
    },
)
