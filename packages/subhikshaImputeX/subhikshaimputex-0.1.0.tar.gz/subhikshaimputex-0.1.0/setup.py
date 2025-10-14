"""
Setup configuration for subhikshaSmartImpute.

This file configures the package for distribution on PyPI.
"""

from setuptools import setup, find_packages

with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()

setup(
    name="subhikshaImputeX",
    version="0.1.0",
    author="Subhiksha_Anandhan",
    author_email="subhiksha2404@gmail.com",
    description="Automatic missing value imputation with intelligent strategy selection",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/subi2404/SubhikshaSmartImpute",
    packages=find_packages(),
    classifiers=[
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
        "Intended Audience :: Developers",
        "Intended Audience :: Science/Research",
        "Topic :: Scientific/Engineering :: Artificial Intelligence",
        "Topic :: Scientific/Engineering :: Information Analysis",
        "Development Status :: 4 - Beta",
    ],
    python_requires=">=3.8",
    install_requires=[
        "numpy>=1.21.0",
        "pandas>=1.3.0",
        "scikit-learn>=1.0.0",
    ],
    extras_require={
        "dev": [
            "pytest>=7.0",
            "pytest-cov>=3.0",
            "black>=22.0",
            "flake8>=4.0",
            "mypy>=0.950",
        ],
        "viz": [
            "matplotlib>=3.5.0",
            "seaborn>=0.11.0",
        ],
    },
    keywords=[
        "imputation",
        "missing-values",
        "machine-learning",
        "data-preprocessing",
        "pandas",
        "scikit-learn",
        "knn",
        "regression",
        "strategy-selection",
    ],
    project_urls={
        "Bug Reports": "https://github.com/subi2404/SubhikshaSmartImpute/issues",
        "Source": "https://github.com/subi2404/SubhikshaSmartImpute",
        "Documentation": "https://subhikshasmartimpute.readthedocs.io",
    },
)