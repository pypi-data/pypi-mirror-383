"""
Setup script for prompt-contracts.

This file is primarily for editable installs and backwards compatibility.
All package metadata is defined in pyproject.toml.
"""

from setuptools import find_packages, setup

setup(
    packages=find_packages(),
    package_data={
        "promptcontracts": ["spec/**/*.json", "spec/**/*.md"],
    },
)
