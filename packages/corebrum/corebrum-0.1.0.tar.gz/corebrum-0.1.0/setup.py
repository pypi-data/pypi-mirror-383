#!/usr/bin/env python3
"""
Setup script for corebrum package.
"""

from setuptools import setup, find_packages
import os

# Read the contents of your README file
this_directory = os.path.abspath(os.path.dirname(__file__))
with open(os.path.join(this_directory, 'README.md'), encoding='utf-8') as f:
    long_description = f.read()

# Read version from __init__.py
def get_version():
    with open(os.path.join(this_directory, 'corebrum', '__init__.py'), 'r') as f:
        for line in f:
            if line.startswith('__version__'):
                return line.split('=')[1].strip().strip('"').strip("'")
    return '0.1.0'

setup(
    name="corebrum",
    version=get_version(),
    author="Corebrum",
    author_email="hello@corebrum.com",
    description="A basic Python package for demonstration purposes",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/corebrum/corebrum-pip",
    packages=find_packages(),
    classifiers=[
        "Development Status :: 3 - Alpha",
        "Intended Audience :: Developers",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.7",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
        "Programming Language :: Python :: 3.12",
    ],
    python_requires=">=3.7",
    keywords="python package corebrum demo",
    project_urls={
        "Bug Reports": "https://github.com/corebrum/corebrum-pip/issues",
        "Source": "https://github.com/corebrum/corebrum-pip",
    },
)
