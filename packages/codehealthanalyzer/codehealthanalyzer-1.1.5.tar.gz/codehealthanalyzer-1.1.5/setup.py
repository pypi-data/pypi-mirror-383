"""Setup script para CodeHealthAnalyzer.

Este script permite instalar a biblioteca CodeHealthAnalyzer usando pip.
"""

from pathlib import Path

from setuptools import find_packages, setup

# Lê o README para a descrição longa (português + inglês)
this_directory = Path(__file__).parent
readme_pt = (
    (this_directory / "README.md").read_text(encoding="utf-8")
    if (this_directory / "README.md").exists()
    else ""
)
readme_en = (
    (this_directory / "README_EN.md").read_text(encoding="utf-8")
    if (this_directory / "README_EN.md").exists()
    else ""
)

# Combina ambas as versões
if readme_pt and readme_en:
    long_description = readme_pt + "\n\n---\n\n" + readme_en
elif readme_pt:
    long_description = readme_pt
elif readme_en:
    long_description = readme_en
else:
    long_description = ""

# Lê os requirements
requirements = []
requirements_file = this_directory / "requirements.txt"
if requirements_file.exists():
    with open(requirements_file, "r", encoding="utf-8") as f:
        requirements = [
            line.strip() for line in f if line.strip() and not line.startswith("#")
        ]

setup(
    name="codehealthanalyzer",
    version="1.1.5",
    author="Luarco Team",
    author_email="contato@luarco.com.br",
    description="Biblioteca Python para análise de qualidade e saúde de código",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/imparcialista/codehealthanalyzer",
    packages=find_packages(include=["codehealthanalyzer", "codehealthanalyzer.*"]),
    classifiers=[
        "Development Status :: 4 - Beta",
        "Intended Audience :: Developers",
        "Topic :: Software Development :: Quality Assurance",
        "Topic :: Software Development :: Testing",
        "License :: OSI Approved :: MIT License",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
        "Programming Language :: Python :: 3.12",
    ],
    python_requires=">=3.8",
    install_requires=requirements
    or [
        "ruff>=0.1.0",
        "click>=8.0.0",
        "rich>=12.0.0",
    ],
    extras_require={
        "dev": [
            "pytest>=7.0.0",
            "pytest-cov>=4.0.0",
            "black>=22.0.0",
            "isort>=5.0.0",
            "bandit>=1.7.4",
            "nox>=2024.4.15",
            "mypy>=1.0.0",
        ],
        "docs": [
            "sphinx>=5.0.0",
            "sphinx-rtd-theme>=1.0.0",
        ],
        "web": [
            "fastapi>=0.104.0",
            "uvicorn[standard]>=0.24.0",
            "jinja2>=3.1.0",
            "python-multipart>=0.0.6",
            "websockets>=12.0",
        ],
    },
    entry_points={
        "console_scripts": [
            "codehealthanalyzer=codehealthanalyzer.cli.main:main",
            "cha=codehealthanalyzer.cli.main:main",  # Alias curto
        ],
    },
    include_package_data=True,
    package_data={
        "codehealthanalyzer": [
            "*.md",
            "*.txt",
            "*.json",
            # Web assets and templates for dashboard
            "web/templates/*.html",
            "web/static/css/*.css",
            "web/static/js/*.js",
            "locale/**/*.po",
            "locale/**/*.mo",
        ],
    },
    keywords=[
        "code-quality",
        "static-analysis",
        "code-health",
        "linting",
        "python",
        "html",
        "css",
        "javascript",
        "ruff",
        "analysis",
        "metrics",
        "reporting",
    ],
    project_urls={
        "Bug Reports": "https://github.com/imparcialista/codehealthanalyzer/issues",
        "Source": "https://github.com/imparcialista/codehealthanalyzer",
        "Documentation": "https://codehealthanalyzer.readthedocs.io/",
    },
)
