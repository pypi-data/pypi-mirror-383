"""
Setup configuration for Arc Flow.
"""

from setuptools import setup, find_packages
from pathlib import Path

# Read README
readme_file = Path(__file__).parent / "README.md"
long_description = readme_file.read_text(encoding="utf-8") if readme_file.exists() else ""

# Read requirements
requirements_file = Path(__file__).parent / "requirements.txt"
requirements = []
if requirements_file.exists():
    with open(requirements_file) as f:
        requirements = [line.strip() for line in f if line.strip() and not line.startswith("#")]

setup(
    name="arc-flow",
    version="0.1.1",
    author="Arc Team",
    author_email="info@azrianlabs.com",
    description="A professional hierarchical multi-agent framework built on python.",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/pinilDissanayaka/Arc-Framework-v2",
    packages=find_packages(exclude=["tests", "tests.*", "examples", "examples.*"]),
    classifiers=[
        "Development Status :: 4 - Beta",
        "Intended Audience :: Developers",
        "Topic :: Software Development :: Libraries :: Application Frameworks",
        "Topic :: Scientific/Engineering :: Artificial Intelligence",
        "License :: OSI Approved :: MIT License",
        "Programming Language :: Python :: 3.12",
    ],
    python_requires=">=3.12",
    install_requires=requirements,
    extras_require={
        "dev": [
            "pytest>=7.0.0",
            "pytest-cov>=4.0.0",
            "pytest-asyncio>=0.21.0",
            "black>=23.0.0",
            "flake8>=6.0.0",
            "mypy>=1.0.0",
        ],
        "mcp": [
            "langchain-mcp-adapters>=0.1.0",
        ],
    },
    entry_points={
        "console_scripts": [
            "arc-framework=arc_flow.cli:main",
        ],
    },
    include_package_data=True,
    package_data={
        "arc": ["py.typed"],
    },
    zip_safe=False,
    keywords="Multi-agent agents ai framework hierarchical arc reinforcement-learning",
    project_urls={
        "Bug Reports": "https://github.com/pinilDissanayaka/Arc-Framework-v2/issues",
        "Source": "https://github.com/pinilDissanayaka/Arc-Framework-v2",
        "Documentation": "https://github.com/pinilDissanayaka/Arc-Framework-v2",
    },
)
