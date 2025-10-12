#!/usr/bin/env python3
"""Setup script for vibe-engineering CLI."""

from setuptools import setup, find_packages
import os

# Read the README file
def read_readme():
    with open("README.md", "r", encoding="utf-8") as f:
        return f.read()

# Read requirements
def read_requirements():
    requirements = []
    if os.path.exists("requirements.txt"):
        with open("requirements.txt", "r") as f:
            requirements = [line.strip() for line in f if line.strip() and not line.startswith("#")]
    return requirements

setup(
    name="vibe-engineering",
    version="0.1.8",
    description="A CLI tool for managing specifications with VoyageAI embeddings and MongoDB vector search",
    long_description=read_readme(),
    long_description_content_type="text/markdown",
    author="Vibe Engineering Team",
    author_email="team@vibeengineering.com",
    url="https://github.com/vibeengineering/vibe-engineering",
    packages=find_packages(),
    include_package_data=True,
    install_requires=[
        "certifi>=2024.12.14",
        "fireworks-ai>=0.19.19",
        "pydantic>=2.12.0",
        "pymongo>=4.15.3",
        "python-dotenv>=1.1.1",
        "requests>=2.32.0",
        "rich>=14.2.0",
        "typer>=0.19.2",
        "voyageai>=0.2.0",
    ],
    extras_require={
        "dev": [
            "pytest>=7.0.0",
            "black>=22.0.0",
            "flake8>=4.0.0",
            "mypy>=0.950",
        ]
    },
    entry_points={
        "console_scripts": [
            "vibe=src.cli.commands:app",
            "vibe-engineering=src.cli.commands:app",
        ],
    },
    classifiers=[
        "Development Status :: 3 - Alpha",
        "Intended Audience :: Developers",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
        "Programming Language :: Python :: 3.12",
        "Programming Language :: Python :: 3.13",
    ],
    python_requires=">=3.10",
    keywords="cli, specifications, ai, mongodb, vector-search, documentation",
    project_urls={
        "Bug Reports": "https://github.com/vibeengineering/vibe-engineering/issues",
        "Source": "https://github.com/vibeengineering/vibe-engineering",
        "Documentation": "https://github.com/vibeengineering/vibe-engineering#readme",
    },
)