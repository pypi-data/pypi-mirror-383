from setuptools import setup, find_packages

# Read the README.md for PyPI long description
with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()

setup(
    name="PolyY",
    version="0.1.0b",
    packages=find_packages(),
    install_requires=[
        "plotly",
        "matplotlib",
        "pandas"
    ],
    author="Nashat Jumaah Omar",
    description="A Multi Y axis Plotting Library based on Plotly",
    long_description=long_description,
    long_description_content_type="text/markdown",  # <-- This is important
    url="https://github.com/Nashat90/",
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    python_requires='>=3.8',
)
