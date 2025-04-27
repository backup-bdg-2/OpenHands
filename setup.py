#!/usr/bin/env python3
from setuptools import find_packages, setup

setup(
    name="openhands-ai",
    version="0.35.0",
    description="Python 3.11 compatibility module for OpenHands",
    author="OpenHands Team",
    author_email="openhands@all-hands.dev",
    packages=find_packages(),
    python_requires=">=3.11",
    install_requires=[],
    classifiers=[
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.11",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
)
