#!/usr/bin/env python3
"""
Universal AI Memory - Setup Script
Install with: pip install universal-ai-memory
"""

from setuptools import setup, find_packages
import os

# Read README for long description
with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()

# Read requirements
with open("requirements.txt", "r", encoding="utf-8") as fh:
    requirements = [line.strip() for line in fh if line.strip() and not line.startswith("#")]

setup(
    name="ragmax",
    version="1.0.0",
    author="Vish Siddharth",
    author_email="your.email@example.com",
    description="RAGMax - Advanced RAG memory system for AI platforms via MCP",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/yourusername/ragmax",
    packages=find_packages(where="python"),
    package_dir={"": "python"},
    classifiers=[
        "Development Status :: 4 - Beta",
        "Intended Audience :: Developers",
        "Topic :: Software Development :: Libraries :: Python Modules",
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
    entry_points={
        "console_scripts": [
            "ragmax=universal_memory.cli:main",
            "rmx=universal_memory.cli:main",  # Short alias
        ],
    },
    include_package_data=True,
    package_data={
        "universal_memory": [
            "templates/*",
            "config/*",
        ],
    },
    extras_require={
        "dev": [
            "pytest>=7.0.0",
            "black>=22.0.0",
            "flake8>=4.0.0",
            "mypy>=0.950",
        ],
    },
)
