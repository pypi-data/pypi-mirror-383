#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""Setup script for Bloret Launcher API Tool."""

from setuptools import setup, find_packages

with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()

setup(
    name="bloret-api-tool",
    version="0.1.0",
    author="Bloret",
    author_email="contact@bloret.com",
    description="A Python library for interacting with Bloret Launcher API",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/bloret/bloret-api-tool",
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
    ],
    python_requires=">=3.7",
    install_requires=[
        "requests>=2.25.0",
    ],
    entry_points={
        "console_scripts": [
            "BLAPI=bloret_api_tool.cli:main",
        ],
    },
    extras_require={
        "dev": [
            "pytest>=6.0",
            "pytest-cov",
            "flake8",
        ],
    },
)