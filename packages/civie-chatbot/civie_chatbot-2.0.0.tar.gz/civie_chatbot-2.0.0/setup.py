"""
Setup configuration for civie-chatbot package
"""

from setuptools import setup, find_packages
from pathlib import Path

# Read the contents of README file
this_directory = Path(__file__).parent
long_description = (this_directory / "README.md").read_text(encoding='utf-8') if (this_directory / "README.md").exists() else ""

# Read requirements
requirements = []
requirements_file = this_directory / "requirements-docker.txt"
if requirements_file.exists():
    with open(requirements_file, encoding='utf-8') as f:
        requirements = [line.strip() for line in f if line.strip() and not line.startswith('#')]

setup(
    name="civie-chatbot",
    version="2.0.0",
    author="Civie Team",
    author_email="support@civie.com",
    description="A comprehensive chatbot API with RAG capabilities, document ingestion, and customer support features",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/civie/civie-chatbot",
    project_urls={
        "Bug Tracker": "https://github.com/civie/civie-chatbot/issues",
        "Documentation": "https://docs.civie.com",
        "Source Code": "https://github.com/civie/civie-chatbot",
    },
    packages=find_packages(exclude=["tests", "tests.*", "logs", "temp_pdfs", "chart"]),
    classifiers=[
        "Development Status :: 4 - Beta",
        "Intended Audience :: Developers",
        "Topic :: Software Development :: Libraries :: Application Frameworks",
        "Topic :: Internet :: WWW/HTTP :: HTTP Servers",
        "Topic :: Scientific/Engineering :: Artificial Intelligence",
        "License :: OSI Approved :: MIT License",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
        "Programming Language :: Python :: 3.12",
        "Operating System :: OS Independent",
        "Framework :: FastAPI",
    ],
    python_requires=">=3.8",
    install_requires=requirements,
    extras_require={
        "dev": [
            "pytest>=7.0.0",
            "pytest-asyncio>=0.21.0",
            "pytest-cov>=4.0.0",
            "black>=23.0.0",
            "flake8>=6.0.0",
            "mypy>=1.0.0",
            "isort>=5.12.0",
        ],
        "docs": [
            "sphinx>=5.0.0",
            "sphinx-rtd-theme>=1.2.0",
            "sphinx-autodoc-typehints>=1.23.0",
        ],
    },
    entry_points={
        "console_scripts": [
            "civie-chatbot=app:app",
        ],
    },
    include_package_data=True,
    package_data={
        "": ["*.json", "*.yaml", "*.yml", "*.txt", "*.md"],
        "src.static": ["*"],
    },
    keywords=[
        "chatbot",
        "fastapi",
        "rag",
        "llm",
        "ai",
        "machine-learning",
        "natural-language-processing",
        "customer-support",
        "document-ingestion",
        "vector-database",
        "embeddings",
        "langchain",
        "openai",
    ],
    zip_safe=False,
)
