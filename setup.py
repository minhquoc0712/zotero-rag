#!/usr/bin/env python3
"""
Setup script for Zotero RAG Search System
"""

from setuptools import setup, find_packages
import os

# Read README file
def read_readme():
    """Read README.md file."""
    readme_path = os.path.join(os.path.dirname(__file__), 'README.md')
    if os.path.exists(readme_path):
        with open(readme_path, 'r', encoding='utf-8') as f:
            return f.read()
    return "RAG system for searching Zotero PDF library"

# Read requirements
def read_requirements():
    """Read requirements.txt file."""
    req_path = os.path.join(os.path.dirname(__file__), 'requirements.txt')
    requirements = []
    if os.path.exists(req_path):
        with open(req_path, 'r', encoding='utf-8') as f:
            for line in f:
                line = line.strip()
                if line and not line.startswith('#') and not line.startswith('-'):
                    requirements.append(line)
    return requirements

setup(
    name="zotero-rag",
    version="1.0.0",
    author="Your Name",
    author_email="your.email@example.com",
    description="RAG (Retrieval-Augmented Generation) system for searching Zotero PDF library",
    long_description=read_readme(),
    long_description_content_type="text/markdown",
    url="https://github.com/yourusername/zotero-rag",
    project_urls={
        "Bug Reports": "https://github.com/yourusername/zotero-rag/issues",
        "Source": "https://github.com/yourusername/zotero-rag",
        "Documentation": "https://github.com/yourusername/zotero-rag#readme",
    },
    packages=find_packages(exclude=['tests*']),
    py_modules=["zotero_rag"] if not find_packages() else [],
    classifiers=[
        "Development Status :: 4 - Beta",
        "Intended Audience :: Science/Research",
        "Intended Audience :: Education",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
        "Topic :: Scientific/Engineering :: Information Analysis",
        "Topic :: Text Processing :: Indexing",
        "Topic :: Utilities",
    ],
    python_requires=">=3.8",
    install_requires=read_requirements(),
    extras_require={
        "gpu": [
            "torch>=2.0.0",
            "faiss-gpu>=1.7.4",
        ],
        "dev": [
            "pytest>=7.0.0",
            "black>=22.0.0",
            "flake8>=4.0.0",
            "mypy>=0.950",
        ],
    },
    entry_points={
        "console_scripts": [
            "zotero-rag=zotero_rag:main",
            "zrag=zotero_rag:main",
        ],
    },
    keywords="zotero, rag, pdf, search, retrieval, nlp, academic, research",
    include_package_data=True,
    zip_safe=False,
)
