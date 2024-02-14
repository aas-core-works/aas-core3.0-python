"""A setuptools based setup module.

See:
https://packaging.python.org/en/latest/distributing.html
https://github.com/pypa/sampleproject
"""
import os
import sys

from setuptools import setup, find_packages

# pylint: disable=redefined-builtin

here = os.path.abspath(os.path.dirname(__file__))

with open(os.path.join(here, "README.rst"), encoding="utf-8") as fid:
    long_description = fid.read()

setup(
    name="aas-core3.0",
    # Synchronize with __init__.py and changelog.rst!
    version="1.0.1",
    description="Manipulate, verify and de/serialize Asset Administration Shells.",
    long_description=long_description,
    url="https://github.com/aas-core-works/aas-core3.0-python",
    author="Marko Ristin",
    author_email="marko@ristin.ch",
    classifiers=[
        "Development Status :: 5 - Production/Stable",
        "License :: OSI Approved :: MIT License",
        "Programming Language :: Python :: 3.7",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
    ],
    license="License :: OSI Approved :: MIT License",
    keywords="asset administration shell sdk industry 4.0 industrie i4.0 industry iot iiot",
    packages=find_packages(exclude=["tests", "continuous_integration", "dev_scripts"]),
    install_requires=[] if sys.version_info >= (3, 8) else ["typing_extensions"],
    py_modules=["aas_core3"],
    package_data={"aas_core3": ["py.typed"]},
)
