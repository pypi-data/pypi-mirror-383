"""
Setup script for SuluvAI package
"""

from setuptools import setup, find_packages
from pathlib import Path

# Read the README file
this_directory = Path(__file__).parent
long_description = (this_directory / "README.md").read_text(encoding='utf-8')

setup(
    name="suluvai",
    version="2.0.0",
    author="SuluvAI Team",
    author_email="contact@suluvai.com",
    description="Production-ready Deep Agents with streaming and local storage support",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/suluvai/suluvai",
    packages=find_packages(exclude=["tests", "examples"]),
    classifiers=[
        "Development Status :: 4 - Beta",
        "Intended Audience :: Developers",
        "Topic :: Software Development :: Libraries :: Python Modules",
        "Topic :: Scientific/Engineering :: Artificial Intelligence",
        "License :: OSI Approved :: MIT License",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
        "Programming Language :: Python :: 3.12",
    ],
    python_requires=">=3.9",
    install_requires=[
        "langchain-core>=0.3.0",
        "langgraph>=0.2.0",
        "pydantic>=2.0.0",
        "typing-extensions>=4.0.0",
    ],
    extras_require={
        "dev": [
            "pytest>=7.0.0",
            "pytest-asyncio>=0.21.0",
            "black>=23.0.0",
            "flake8>=6.0.0",
            "mypy>=1.0.0",
        ],
        "openai": [
            "langchain-openai>=0.2.0",
            "openai>=1.0.0",
        ],
        "anthropic": [
            "langchain-anthropic>=0.2.0",
            "anthropic>=0.20.0",
        ],
        "tracing": [
            "langsmith>=0.1.0",
        ],
    },
    keywords="langchain langgraph agents ai llm streaming deep-agents suluvai",
    project_urls={
        "Bug Reports": "https://github.com/suluvai/suluvai/issues",
        "Source": "https://github.com/suluvai/suluvai",
        "Documentation": "https://github.com/suluvai/suluvai#readme",
    },
)
