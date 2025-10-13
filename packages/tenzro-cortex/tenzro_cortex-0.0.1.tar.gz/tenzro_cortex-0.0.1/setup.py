from setuptools import setup, find_packages

with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()

setup(
    name="tenzro-cortex",
    version="0.0.1",
    author="Tenzro Team",
    author_email="team@tenzro.network",
    description="Universal LLM Training Platform - Train any model on any hardware",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://cortex.tenzro.network",
    project_urls={
        "Documentation": "https://docs.tenzro.network",
        "Source": "https://github.com/tenzro/tenzro-cortex",
    },
    packages=find_packages(),
    classifiers=[
        "Development Status :: 4 - Beta",
        "Intended Audience :: Developers",
        "Topic :: Scientific/Engineering :: Artificial Intelligence",
        "License :: OSI Approved :: Apache Software License",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
    ],
    python_requires=">=3.9",
    install_requires=[
        "click>=8.0.0,!=8.3.0",
        "requests>=2.28.0",
        "rich>=13.0.0",
        "pyyaml>=6.0",
    ],
    entry_points={
        "console_scripts": [
            "tenzro-cortex=tenzro_cortex_cli.cli:cli",
        ],
    },
    license="Apache-2.0",
)
