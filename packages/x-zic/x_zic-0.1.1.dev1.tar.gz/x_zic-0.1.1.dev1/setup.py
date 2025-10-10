#!/usr/bin/env python
from setuptools import setup, find_packages

if __name__ == "__main__":
    setup(
        packages=find_packages(),
        use_scm_version=True,
        setup_requires=["setuptools_scm"],
    )