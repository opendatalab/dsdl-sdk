#!/usr/bin/env python3
#
# Copyright DSDL Team of OpenDatalab. All rights reserved.
#

"""Setup file."""

from setuptools import setup, find_packages

version = {}
with open("dsdl/__version__.py") as version_file:
    exec(version_file.read(), version)

setup(
    name="dsdl",
    version=version["__version__"],
    description="Python SDK for DSDL",
    author="DSDL team",
    author_email="dsdl-team@pjlab.org.cn",
    packages=find_packages(),
    package_data={},
    include_package_data=True,
    install_requires=[
        "pyyaml>=6.0",
        "click>=8.1.3",
        "networkx>=2.8.4",
    ],
    classifiers=[
        "Programming Language :: Python :: 3.6",
        "Programming Language :: Python :: 3.7",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
    ],
    python_requires=">=3.6",
    entry_points={
        "console_scripts": [
            "dsdl = dsdl.cli:cli",
        ],
    },
)
