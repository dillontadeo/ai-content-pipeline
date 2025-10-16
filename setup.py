"""
Setup script for easy installation of the AI Content Pipeline.
"""
from setuptools import setup, find_packages

with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()

setup(
    name="ai-content-pipeline",
    version="1.0.0",
    author="Dillon Thompson",
    author_email="your.email@example.com",
    description="AI-powered marketing content pipeline with automated generation, distribution, and analysis",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/yourusername/ai-content-pipeline",
    packages=find_packages(),
    classifiers=[
        "Development Status :: 4 - Beta",
        "Intended Audience :: Developers",
        "Topic :: Software Development :: Libraries :: Python Modules",
        "License :: OSI Approved :: MIT License",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
    ],
    python_requires=">=3.8",
    install_requires=[
        "openai>=1.12.0",
        "python-dotenv>=1.0.0",
        "requests>=2.31.0",
        "hubspot-api-client>=8.3.0",
        "pandas>=2.1.0",
        "numpy>=1.24.0",
        "flask>=3.0.0",
        "flask-cors>=4.0.0",
        "python-dateutil>=2.8.2",
        "pytz>=2023.3",
    ],
    extras_require={
        "dev": [
            "pytest>=7.4.0",
            "black>=23.7.0",
            "flake8>=6.0.0",
            "mypy>=1.4.0",
        ],
    },
    entry_points={
        "console_scripts": [
            "content-pipeline=main:main",
            "content-dashboard=dashboard:main",
        ],
    },
)

