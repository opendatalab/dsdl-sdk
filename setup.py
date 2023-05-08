#!/usr/bin/env python3
#
# Copyright DSDL Team of OpenDatalab. All rights reserved.
#

"""Setup file."""

from setuptools import setup, find_packages


def readme():
    with open('README.md', encoding='utf-8') as f:
        content = f.read()
    return content


version = {}
with open("dsdl/__version__.py") as version_file:
    exec(version_file.read(), version)

setup(
    name="dsdl",
    version=version["__version__"],
    description="Python SDK for DSDL",
    long_description=readme(),
    long_description_content_type='text/markdown',
    author="DSDL team",
    author_email="dsdl-team@pjlab.org.cn",
    packages=find_packages(),
    package_data={"dsdl": ["geometry/source/Arial_Font.ttf"]},
    include_package_data=True,
    install_requires=[
        "pyyaml>=6.0",
        "click>=8.1.3",
        "networkx>=2.8.4",
        "Pillow>=9.1.0",
        "prettytable>=3.3.0",
        "opencv-python>=4.6.0.66",
        "jsonmodels==2.6.0",
        "environs==9.5.0",
        "pylint>=2.15.5",
        "fastjsonschema>=2.16.3",
        # "pycocotools>=2.0.6",
        "tqdm>=4.65.0",
        # "scikit-image>=0.19.3",
        "tifffile",
        "terminaltables>=3.1.10",
    ],
    classifiers=[
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
    ],
    python_requires=">=3.8",
    entry_points={
        "console_scripts": [
            "dsdl = dsdl.cli:cli",
        ],
    },
)
