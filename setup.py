from setuptools import setup, find_packages

setup(
    name="openhands_py311",
    version="0.1.0",
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
