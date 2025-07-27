#!/usr/bin/env python3

from setuptools import setup, find_packages

with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()

setup(
    name="bitfinex-api-py-postonly-wrapper",
    version="1.0.0",
    author="0xferit",
    author_email="ferit@example.com",
    description="Python wrapper for bitfinex-api-py that enforces POST_ONLY on limit orders for safe market-making",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/0xferit/bitfinex-api-py-postonly-wrapper",
    packages=find_packages(),
    classifiers=[
        "Development Status :: 4 - Beta",
        "Intended Audience :: Developers",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.12",
        "Topic :: Office/Business :: Financial :: Investment",
        "Topic :: Software Development :: Libraries :: Python Modules",
    ],
    python_requires=">=3.12",
    install_requires=[
        "git+https://github.com/0xferit/bitfinex-api-py.git@heartbeat",
    ],
    extras_require={
        "dev": [
            "pytest>=7.0.0",
            "pytest-asyncio>=0.21.0",
            "black>=23.0.0",
            "isort>=5.0.0",
            "flake8>=5.0.0",
            "mypy>=1.0.0",
        ],
    },
)
