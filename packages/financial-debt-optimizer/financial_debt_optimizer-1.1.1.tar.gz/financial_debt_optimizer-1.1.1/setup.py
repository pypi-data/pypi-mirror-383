from setuptools import setup, find_packages
import os
import sys

# Add src to path to import version
src_path = os.path.join(os.path.dirname(__file__), 'src')
sys.path.insert(0, src_path)

try:
    from __version__ import (
        __version__, __title__, __description__, __author__, 
        __author_email__, __license__, __url__
    )
except ImportError:
    __version__ = "1.1.1"
    __title__ = "Financial Debt Optimizer"
    __description__ = "A comprehensive tool for analyzing and optimizing debt repayment strategies"
    __author__ = "Bryan Kemp"
    __author_email__ = "bryan@kempville.com"
    __license__ = "BSD-3-Clause"
    __url__ = "https://github.com/bryankemp/financial-debt-optimizer"

# Read README if it exists
try:
    with open("README.md", "r", encoding="utf-8") as fh:
        long_description = fh.read()
except FileNotFoundError:
    long_description = __description__

# Read requirements if it exists
try:
    with open("requirements.txt", "r", encoding="utf-8") as fh:
        requirements = [line.strip() for line in fh if line.strip() and not line.startswith("#")]
except FileNotFoundError:
    requirements = [
        "pandas>=1.3.0",
        "numpy>=1.21.0",
        "xlsxwriter>=3.0.0",
        "openpyxl>=3.0.0",
        "click>=8.0.0",
        "matplotlib>=3.5.0"
    ]

setup(
    name="financial-debt-optimizer",
    version=__version__,
    author=__author__,
    author_email=__author_email__,
    description=__description__,
    long_description=long_description,
    long_description_content_type="text/markdown",
    url=__url__,
    project_urls={
        "Bug Reports": f"{__url__}/issues",
        "Source": __url__,
        "Documentation": f"{__url__}#readme",
    },
    packages=find_packages(where="src"),
    package_dir={"": "src"},
    classifiers=[
        "Development Status :: 5 - Production/Stable",
        "Intended Audience :: End Users/Desktop",
        "Intended Audience :: Financial and Insurance Industry",
        "License :: OSI Approved :: BSD License",
        "Operating System :: OS Independent",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
        "Programming Language :: Python :: 3.12",
        "Topic :: Office/Business :: Financial",
        "Topic :: Office/Business :: Financial :: Accounting",
        "Topic :: Scientific/Engineering :: Mathematics",
    ],
    keywords="debt optimization finance calculator repayment strategy",
    python_requires=">=3.8",
    install_requires=[req.split(">=")[0] for req in requirements if not req.startswith(("pytest", "black", "pylint"))],
    extras_require={
        "dev": ["pytest>=6.2.5", "black>=21.5b2", "pylint>=2.8.2", "mypy>=0.910"],
        "test": ["pytest>=6.2.5", "pytest-cov>=2.12.0"],
    },
    entry_points={
        "console_scripts": [
            "debt-optimizer=cli.commands:main",
        ],
    },
    include_package_data=True,
    zip_safe=False,
)
