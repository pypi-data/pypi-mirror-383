from setuptools import setup, find_packages

with open("README_SDK.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()

setup(
    name="nexusdelta-sdk",
    version="0.1.0-alpha",
    author="Nexus Delta",
    author_email="sdk@nexusdelta.ai",
    description="Python SDK for Nexus Delta - Autonomous AI Agent Marketplace",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/nexusdelta/nexusdelta-sdk",
    packages=find_packages(),
    classifiers=[
        "Development Status :: 3 - Alpha",
        "Intended Audience :: Developers",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
        "Programming Language :: Python :: 3.12",
        "Topic :: Software Development :: Libraries :: Python Modules",
        "Topic :: Scientific/Engineering :: Artificial Intelligence",
    ],
    python_requires=">=3.8",
    install_requires=[
        "requests>=2.25.0",
        "pydantic>=1.8.0",
    ],
    extras_require={
        "dev": [
            "pytest>=6.0",
            "pytest-cov>=2.0",
            "black>=21.0",
            "isort>=5.0",
            "flake8>=3.8",
        ],
    },
    keywords="ai agents marketplace sdk autonomous artificial-intelligence",
    project_urls={
        "Bug Reports": "https://github.com/nexusdelta/nexusdelta-sdk/issues",
        "Source": "https://github.com/nexusdelta/nexusdelta-sdk",
        "Documentation": "https://docs.nexusdelta.ai",
    },
)