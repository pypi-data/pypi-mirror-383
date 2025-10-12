"""
MIT License

Copyright (c) 2025 Saleem Ahmad (Elite India Org Team)
Email: team@eliteindia.org

Permission is hereby granted, free of charge, to any person obtaining a copy
of this software and associated documentation files (the "Software"), to deal
in the Software without restriction, including without limitation the rights
to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
copies of the Software, and to permit persons to whom the Software is
furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in all
copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
SOFTWARE.
"""

"""
PowerScript - A fully structured development language that transpiles to Python

Setup script for installing PowerScript
"""

from setuptools import setup, find_packages
from pathlib import Path

# Read README
this_directory = Path(__file__).parent
long_description = (this_directory / "README.md").read_text()

setup(
    name="eitps",
    version="1.0.0b1",
    description="Typed PowerScript (TPS) - A fully structured development language that transpiles to Python",
    long_description=long_description,
    long_description_content_type="text/markdown",
    author="Saleem Ahmad (Elite India Org Team)",
    author_email="team@eliteindia.org",
    url="https://github.com/SaleemLww/Python-PowerScript",
    license="MIT",
    packages=find_packages(),
    classifiers=[
        "Development Status :: 4 - Beta",
        "Intended Audience :: Developers",
        "License :: OSI Approved :: MIT License",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
        "Topic :: Software Development :: Compilers",
        "Topic :: Software Development :: Code Generators",
    ],
    python_requires=">=3.8",
    install_requires=[
        "beartype>=0.10.0",
        "lark>=1.1.0",
        "watchdog>=2.1.0",
        "rich>=10.0.0",
        "click>=8.0.0",
        "typing-extensions>=4.0.0",
    ],
    extras_require={
        "dev": [
            "pytest>=6.0.0",
            "pytest-cov>=2.10.0",
            "black>=21.0.0",
            "flake8>=3.8.0",
            "mypy>=0.910",
        ],
        "lsp": [
            "pygls>=0.11.0",
            "pyright>=1.1.0",
        ],
        "ai": [
            "numpy>=1.21.0",
            "pandas>=1.3.0",
            "scikit-learn>=1.0.0",
            "torch>=1.9.0",
        ],
        "web": [
            "flask>=2.0.0",
            "fastapi>=0.70.0",
            "uvicorn>=0.15.0",
        ]
    },
    entry_points={
        'console_scripts': [
            'tps=powerscript.cli.cli:main',
            'ps=powerscript.cli.cli:ps_smart_command',
            'tps-run=powerscript.cli.cli:run_command',
            'tps-compile=powerscript.cli.cli:compile_command',
            'tps-create=powerscript.cli.cli:create_command',
            'tps-build=powerscript.cli.cli:smart_compile',
            # Legacy commands for backward compatibility
            'powerscriptc=powerscript.cli.cli:main',
            'ps-run=powerscript.cli.cli:main', 
            'ps-create=powerscript.cli.cli:main',
            'psc=powerscript.cli.cli:main',
        ],
    },
    include_package_data=True,
    package_data={
        "powerscript": [
            "vscode-extension/**/*",
            "examples/**/*",
            "docs/**/*",
        ],
    },
    keywords="tps powerscript typed python transpiler compiler language ai",
    project_urls={
        "Bug Reports": "https://github.com/powerscript/powerscript/issues",
        "Source": "https://github.com/powerscript/powerscript",
        "Documentation": "https://powerscript.dev/docs",
    },
)