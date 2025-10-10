"""Setup script for markitdown-chunker."""

from setuptools import setup, find_packages
from pathlib import Path

# Read the README file
readme_file = Path(__file__).parent / "README.md"
long_description = readme_file.read_text(encoding="utf-8") if readme_file.exists() else ""

setup(
    name="markitdown-chunker",
    version="0.1.0",
    author="Naveen Kumar Rajarajan",
    author_email="rajarajannaveenkumar@gmail.com",
    description="Convert documents to markdown, chunk them intelligently, and export structured data",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/Naveenkumarar/markitdown-chunker",
    packages=find_packages(exclude=["tests", "tests.*"]),
    classifiers=[
        "Development Status :: 4 - Beta",
        "Intended Audience :: Developers",
        "Topic :: Software Development :: Libraries :: Python Modules",
        "Topic :: Text Processing :: Markup :: Markdown",
        "License :: OSI Approved :: MIT License",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
        "Programming Language :: Python :: 3.12",
    ],
    python_requires=">=3.8",
    install_requires=[
        "markitdown>=0.0.1",
        "langchain>=0.1.0",
        "langchain-text-splitters>=0.0.1",
    ],
    extras_require={
        "dev": [
            "pytest>=7.0.0",
            "pytest-cov>=4.0.0",
            "black>=23.0.0",
            "flake8>=6.0.0",
            "mypy>=1.0.0",
        ],
        "images": [
            "pymupdf>=1.23.0",
            "python-docx>=0.8.11",
            "python-pptx>=0.6.21",
        ],
    },
    entry_points={
        "console_scripts": [
            "markitdown-chunker=markitdown_chunker.cli:main",
        ],
    },
    keywords="markdown converter chunker document-processing langchain markitdown",
    project_urls={
        "Bug Reports": "https://github.com/Naveenkumarar/markitdown-chunker/issues",
        "Source": "https://github.com/Naveenkumarar/markitdown-chunker",
    },
)

