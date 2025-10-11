#!/usr/bin/env python3
"""
Setup configuration for frappeye - Frappe hooks analyzer and conflict detector.
Optimized for performance and comprehensive hook analysis.
"""

from setuptools import setup, find_packages
import os

# Read README for long description
def read_readme():
    """Read README.md for PyPI long description."""
    readme_path = os.path.join(os.path.dirname(__file__), 'README.md')
    if os.path.exists(readme_path):
        with open(readme_path, 'r', encoding='utf-8') as f:
            return f.read()
    return "Advanced Frappe hooks analyzer and conflict detector"

# Read requirements
def read_requirements():
    """Read requirements.txt for dependencies."""
    req_path = os.path.join(os.path.dirname(__file__), 'requirements.txt')
    if os.path.exists(req_path):
        with open(req_path, 'r', encoding='utf-8') as f:
            return [line.strip() for line in f if line.strip() and not line.startswith('#')]
    return []

setup(
    name="frappeye",
    version="1.0.0",
    author="Sharath Kumar",
    author_email="imsharathkumarv@gmail.com",
    description="Advanced Frappe hooks analyzer and conflict detector for multi-app environments",
    long_description=read_readme(),
    long_description_content_type="text/markdown",
    url="https://github.com/thisissharath/frappeye",
    packages=find_packages(),
    classifiers=[
        "Development Status :: 5 - Production/Stable",
        "Intended Audience :: Developers",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
        "Programming Language :: Python :: 3.12",
        "Topic :: Software Development :: Libraries :: Python Modules",
        "Topic :: Software Development :: Quality Assurance",
        "Topic :: System :: Systems Administration",
    ],
    python_requires=">=3.8",
    install_requires=read_requirements(),
    extras_require={
        "dev": [
            "pytest>=7.0.0",
            "pytest-cov>=4.0.0",
            "black>=23.0.0",
            "flake8>=6.0.0",
            "mypy>=1.0.0",
        ],
        "docs": [
            "sphinx>=5.0.0",
            "sphinx-rtd-theme>=1.0.0",
        ],
    },
    entry_points={
        "console_scripts": [
            "frappeye=frappeye.cli.main:main",
        ],
    },
    include_package_data=True,
    zip_safe=False,
    keywords="frappe hooks analyzer conflict detector multi-app bench",
    project_urls={
        "Bug Reports": "https://github.com/thisissharath/frappeye/issues",
        "Source": "https://github.com/thisissharath/frappeye",
        "Documentation": "https://frappeye.readthedocs.io/",
    },
)