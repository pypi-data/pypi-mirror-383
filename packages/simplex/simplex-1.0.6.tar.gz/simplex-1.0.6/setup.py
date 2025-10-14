"""
Setup configuration for the Simplex Python SDK.
"""

from setuptools import setup, find_packages

with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()

setup(
    name="simplex",
    version="1.0.7",
    author="Simplex",
    author_email="support@simplex.sh",
    description="Official Python SDK for the Simplex API",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/yourusername/simplex-python-sdk",
    project_urls={
        "Bug Tracker": "https://github.com/yourusername/simplex-python-sdk/issues",
        "Documentation": "https://docs.simplex.sh",
        "Source Code": "https://github.com/yourusername/simplex-python-sdk",
    },
    packages=find_packages(exclude=["tests*", "examples*"]),
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
        "Programming Language :: Python :: 3.12",
        "Operating System :: OS Independent",
    ],
    python_requires=">=3.8",
    install_requires=[
        "requests>=2.25.0",
        "urllib3>=1.26.0",
    ],
    extras_require={
        "dev": [
            "pytest>=7.0.0",
            "pytest-cov>=3.0.0",
            "black>=22.0.0",
            "flake8>=4.0.0",
            "mypy>=0.950",
            "python-dotenv>=0.19.0",
        ],
    },
    keywords="simplex api sdk workflow automation browser",
)