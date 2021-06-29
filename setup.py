#!/usr/bin/env python
# -*- coding: utf-8 -*-

try:
    from setuptools import setup
except ImportError:
    from distutils.core import setup

from pathlib import Path

version_path = Path(__file__).parent / "karton/die_classifier/__version__.py"
version_info = {}
exec(version_path.read_text(), version_info)

setup(
    name="karton-die-classifier",
    version=version_info["__version__"],
    description="Detect-It-Easy classifier for the Karton framework",
    namespace_packages=["karton"],
    packages=["karton.die_classifier"],
    url="https://github.com/raw-data/karton-die-classifier",
    long_description=open("README.md", "r").read(),
    long_description_content_type="text/markdown",
    install_requires=open("requirements.txt").read().splitlines(),
    entry_points={
        "console_scripts": [
            "karton-die-classifier=karton.die_classifier:DieClassifier.main"
        ],
    },
    classifiers=["Programming Language :: Python"],
)
