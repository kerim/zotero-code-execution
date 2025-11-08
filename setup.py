"""Setup script for Zotero Code Execution Library."""

from setuptools import setup, find_packages
from pathlib import Path

# Read README for long description
readme_file = Path(__file__).parent / "README.md"
long_description = readme_file.read_text() if readme_file.exists() else ""

setup(
    name="zotero-code-execution",
    version="0.1.0",
    description="Python library wrapper for Zotero MCP enabling efficient code-based search orchestration",
    long_description=long_description,
    long_description_content_type="text/markdown",
    author="Your Name",
    author_email="your.email@example.com",
    url="https://github.com/yourusername/zotero-code-execution",
    py_modules=["zotero_lib"],
    python_requires=">=3.8",
    install_requires=[
        # These should already be installed via zotero-mcp
        "pyzotero",
        "python-dotenv",
        "markitdown",
        "chromadb",
        "sentence-transformers",
    ],
    classifiers=[
        "Development Status :: 3 - Alpha",
        "Intended Audience :: Developers",
        "Intended Audience :: Science/Research",
        "License :: OSI Approved :: MIT License",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
        "Programming Language :: Python :: 3.12",
        "Topic :: Scientific/Engineering :: Information Analysis",
    ],
    keywords="zotero mcp code-execution anthropic claude research bibliography",
)
