#!/usr/bin/env python

"""The setup script for pocong."""

from os import path
from setuptools import setup, find_packages
import versioneer

here = path.abspath(path.dirname(__file__))

# Get the long description from the README file
with open(path.join(here, "README.md"), encoding="utf-8") as f:
    long_description = f.read()

install_requires = [
    "Scrapy>=2.5.0",
    "pandas>=1.3.0",
    "requests>=2.25.0",
    "Click>=7.0",
    "mechanize>=0.4.0",
    "html2text>=2020.1.16",
    "fake-useragent>=1.1.0",
    "beautifulsoup4>=4.9.0",
]

extras_require = {
    "dev": [
        "pytest",
        "pytest-mock",
        "pytest-cov",
        "moto",
        "tox",
        "flake8",
        "flake8-import-order",
        "flake8-print",
        "flake8-builtins",
        "pep8-naming",
        "pre-commit",
        "rope",
    ]
}

setup(
    name="pocong",  # must be unique in PyPI
    version=versioneer.get_version(),
    cmdclass=versioneer.get_cmdclass(),
    description="Python Oriented Crawling Ongoing (POCONG): a simple crawling framework",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://gitlab.com/mohsin3107/pocong",  # <-- Update this
    author="Singgih",
    author_email="singgih@alkode.id",
    license="MIT",  # <-- add a license for PyPI metadata
    package_dir={"": "src"},
    packages=find_packages(where="src"),
    python_requires=">=3.8",  # ✅ recommend lowering from 3.12 for wider adoption
    install_requires=install_requires,
    extras_require=extras_require,
    entry_points={
        "console_scripts": [
            "pocong=pocong.cli:main",
        ]
    },
    include_package_data=True,
    classifiers=[
        "Development Status :: 3 - Alpha",  # You can change to Beta/Production
        "Intended Audience :: Developers",
        "License :: OSI Approved :: MIT License",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
        "Programming Language :: Python :: 3.12",
        "Operating System :: OS Independent",
        "Topic :: Software Development :: Libraries",
        "Topic :: Internet :: WWW/HTTP",
    ]
)
