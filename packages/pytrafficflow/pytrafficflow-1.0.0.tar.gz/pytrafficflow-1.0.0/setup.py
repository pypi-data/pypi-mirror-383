#!/usr/bin/env python3
"""
Setup script for pytrafficflow package.
This file provides backward compatibility for legacy package installation methods.
The main configuration is in pyproject.toml.
"""

from setuptools import setup

try:
    with open("README.md", "r", encoding="utf-8") as fh:
        long_description = fh.read()
except FileNotFoundError:
    long_description = "A Python library for traffic flow simulation with PDE models, particle-based models, and real-world data pipelines"

def get_version():
    """Extract version from pytrafficflow/__init__.py"""
    try:
        with open("pytrafficflow/__init__.py", "r", encoding="utf-8") as f:
            for line in f:
                if line.startswith("__version__"):
                    return line.split("=")[1].strip().strip('"').strip("'")
    except FileNotFoundError:
        pass
    return "1.0.0"

if __name__ == "__main__":
    setup(
        name="pytrafficflow",
        version=get_version(),
        author="Tiago Monteiro",
        author_email="tiagomonteiro0715@gmail.com",
        description="A Python library for traffic flow simulation with PDE models, particle-based models, and real-world data pipelines",
        long_description=long_description,
        long_description_content_type="text/markdown",
        url="https://github.com/tiagomonteiro0715/pytrafficflow",
        project_urls={
            "Bug Reports": "https://github.com/tiagomonteiro0715/pytrafficflow/issues",
            "Source": "https://github.com/tiagomonteiro0715/pytrafficflow.git",
            "Documentation": "https://pytrafficflow.readthedocs.io/",
        },
        
        packages=["pytrafficflow", "pytrafficflow.core", "pytrafficflow.data", 
                 "pytrafficflow.data.synthetic", "pytrafficflow.models", 
                 "pytrafficflow.tests", "pytrafficflow.utils"],
        package_dir={"": "."},
        
        python_requires=">=3.8",
        install_requires=[
            "numpy>=1.20.0",
            "matplotlib>=3.3.0",
        ],
        
        extras_require={
            "dev": [
                "pytest>=6.0",
                "pytest-cov>=2.0",
                "black>=21.0",
                "flake8>=3.8",
                "mypy>=0.800",
                "isort>=5.0",
            ],
            "docs": [
                "sphinx>=4.0",
                "sphinx-rtd-theme>=1.0",
                "nbsphinx>=0.8",
            ],
            "test": [
                "pytest>=6.0",
                "pytest-cov>=2.0",
                "pytest-xdist>=2.0",
            ],
        },
        
        classifiers=[
            "Development Status :: 4 - Beta",
            "Intended Audience :: Science/Research",
            "License :: OSI Approved :: MIT License",
            "Operating System :: OS Independent",
            "Programming Language :: Python :: 3",
            "Programming Language :: Python :: 3.8",
            "Programming Language :: Python :: 3.9",
            "Programming Language :: Python :: 3.10",
            "Programming Language :: Python :: 3.11",
            "Programming Language :: Python :: 3.12",
            "Topic :: Scientific/Engineering :: Physics",
            "Topic :: Scientific/Engineering :: Mathematics",
            "Topic :: Software Development :: Libraries :: Python Modules",
        ],
        keywords="traffic simulation pde particle idm lwr transportation",
        
        include_package_data=True,
        package_data={
            "pytrafficflow": ["*.png", "*.jpg", "*.jpeg", "*.gif", "*.svg"],
        },
        
        entry_points={
            "console_scripts": [
                "pytrafficflow=pytrafficflow.cli:main",
            ],
        },
        
        zip_safe=False,
    )
