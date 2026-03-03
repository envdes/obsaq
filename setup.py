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
    version="0.0.3",
    author="Jinhui Yu",
    author_email="yjh12586@163.com",
    url="https://github.com/envdes/obsaq",
    description="An open-source framework for fast and scalable air pollution data retrieval",
    long_description=long_description,
    long_description_content_type="text/x-rst",
    license="MIT",
    classifiers=classifiers,
    install_requires=['pandas', 'pyreadr'],
    packages=find_packages(),
    )
