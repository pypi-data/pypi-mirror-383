from setuptools import setup, find_packages

with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()

setup(
    name="nexusdelta-sdk",
    version="2.0.2",
    author="Nexus Delta Team",
    author_email="team@nexusdelta.ai",
    description="Official Python SDK for the Nexus Delta AI Agent Marketplace",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/nexusdelta/nexusdelta-sdk",
    packages=find_packages(),
    classifiers=[
        "Development Status :: 4 - Beta",
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
        "Topic :: Internet :: WWW/HTTP",
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
            "mypy>=0.900",
        ],
        "crypto": [
            "web3>=6.0.0",
            "eth-account>=0.8.0",
        ],
        "full": [
            "fastapi>=0.100.0",
            "uvicorn>=0.20.0",
            "firebase-admin>=6.0.0",
        ],
    },
    keywords="ai agents marketplace sdk autonomous artificial-intelligence blockchain crypto",
    project_urls={
        "Bug Reports": "https://github.com/nexusdelta/nexusdelta-sdk/issues",
        "Source": "https://github.com/nexusdelta/nexusdelta-sdk",
        "Documentation": "https://github.com/nexusdelta/nexusdelta-sdk#readme",
        "Marketplace": "https://nexus-delta.web.app",
    },
)