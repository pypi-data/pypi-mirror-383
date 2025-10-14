import setuptools
from pathlib import Path

setuptools.setup(
    name="mhspack",
    version=1.0,
    author="mhs",
    author_email="mhs@example.com", 
    long_description=Path("README.md").read_text(),
    packages=setuptools.find_packages(exclude=['tests','data']), # exclude test and data directories
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    python_requires='>=3.6',
)