"""
Setup script for Corally calculator suite.

This file is kept for backward compatibility and development purposes.
The main configuration is in pyproject.toml.
"""

from setuptools import setup, find_packages
from pathlib import Path

# Read the README file
this_directory = Path(__file__).parent
long_description = (this_directory / "README.md").read_text(encoding="utf-8")

setup(
    name="corally",
    version="2.0.0",
    author="Corally Team",
    author_email="contact@corally.dev",
    description="A comprehensive calculator suite with GUI and API support",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/yourusername/corally",
    project_urls={
        "Bug Tracker": "https://github.com/yourusername/corally/issues",
        "Documentation": "https://github.com/yourusername/corally#readme",
        "Source Code": "https://github.com/yourusername/corally",
    },
    package_dir={"": "src"},
    packages=find_packages(where="src"),
    classifiers=[
        "Development Status :: 4 - Beta",
        "Intended Audience :: Developers",
        "Intended Audience :: Education",
        "Intended Audience :: End Users/Desktop",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
        "Programming Language :: Python :: 3.12",
        "Topic :: Office/Business :: Financial :: Spreadsheet",
        "Topic :: Scientific/Engineering :: Mathematics",
        "Topic :: Software Development :: Libraries :: Python Modules",
        "Topic :: Utilities",
    ],
    python_requires=">=3.8",
    install_requires=[
        "fastapi>=0.68.0",
        "uvicorn>=0.15.0",
        "httpx>=0.24.0",
        "requests>=2.25.0",
        "python-dotenv>=0.19.0",
    ],
    extras_require={
        "gui": [],  # tkinter is usually included with Python
        "dev": [
            "pytest>=6.0",
            "pytest-cov",
            "black",
            "flake8",
            "mypy",
            "build",
            "twine",
        ],
    },
    entry_points={
        "console_scripts": [
            "corally=corally.cli.main:main_cli",
            "corally-calc=corally.cli.calculator:calculator_cli",
            "corally-currency=corally.cli.currency:currency_cli",
            "corally-gui=corally.gui.launcher:launch_gui",
        ],
    },
    include_package_data=True,
    zip_safe=False,
    keywords=[
        "calculator",
        "currency",
        "converter",
        "interest",
        "gui",
        "api",
        "finance",
        "math",
        "tkinter",
        "fastapi",
    ],
)
