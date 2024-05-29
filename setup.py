from setuptools import setup, find_packages, Extension
import os

classifiers = [
    "Development Status :: 2 - Pre-Alpha",
    "Intended Audience :: Science/Research",
    "License :: OSI Approved :: MIT License",
    "Natural Language :: English",
    "Operating System :: OS Independent",
    "Programming Language :: Python :: 3",
    "Topic :: Scientific/Engineering :: Atmospheric Science"
    ]

with open("README.rst", "r") as fp:
    long_description = fp.read()

setup(
    name="obsaq",
    version="0.0.0",
    author="Haofan Wang",
    author_email="cuitwhf@gmail.com",
    url="https://github.com/envdes/obsaq",
    description="A Python package for accessing observational air quality data",
    long_description=long_description,
    license="MIT",
    classifiers=classifiers,
    install_requires=['pandas', 'numpy', 'pyreadr'],
    packages=find_packages(),
    )