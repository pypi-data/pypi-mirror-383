"""
Setup script for CryptoGPU library
High-performance GPU-accelerated cryptocurrency wallet generation
"""

from setuptools import setup, find_packages

# Read README
try:
    with open("README.md", "r", encoding="utf-8") as fh:
        long_description = fh.read()
except:
    long_description = "High-performance GPU-accelerated cryptocurrency wallet generation library"

setup(
    name="crypto-gpu-lib",
    version="1.0.0",
    author="CryptoGPU Team",
    author_email="team@cryptogpu.dev",
    description="High-performance GPU-accelerated cryptocurrency wallet generation library",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/cryptogpu/crypto-gpu-lib",
    packages=find_packages(),
    classifiers=[
        "Development Status :: 4 - Beta",
        "Intended Audience :: Developers",
        "Intended Audience :: Financial and Insurance Industry",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
        "Topic :: Software Development :: Libraries :: Python Modules",
        "Topic :: Security :: Cryptography",
        "Topic :: Office/Business :: Financial",
    ],
    python_requires=">=3.8",
    install_requires=[
        "numpy>=1.21.0",
        "mnemonic>=0.20",
        "hdwallet>=2.2.1",
        "eth-account>=0.8.0",
        "ecdsa>=0.18.0",
        "base58>=2.1.1",
        "solders>=0.18.0",
        "aiohttp>=3.8.0",
        "requests>=2.28.0",
        "psutil>=5.9.0"
    ],
    extras_require={
        "gpu": [
            "cupy-cuda12x>=12.0.0",
        ],
        "dev": [
            "pytest>=7.0.0",
            "black>=22.0.0",
            "flake8>=4.0.0",
            "mypy>=0.950",
            "bandit>=1.7.0",
            "safety>=2.0.0",
        ],
        "torch": [
            "torch>=2.0.0",
        ],
        "all": [
            "cupy-cuda12x>=12.0.0",
            "torch>=2.0.0",
            "pytest>=7.0.0",
            "black>=22.0.0",
            "flake8>=4.0.0",
            "mypy>=0.950",
            "bandit>=1.7.0",
            "safety>=2.0.0",
        ],
    },
    keywords="cryptocurrency, wallet, gpu, cuda, bitcoin, ethereum, blockchain, bip39, bip44",
    project_urls={
        "Homepage": "https://github.com/cryptogpu/crypto-gpu-lib",
        "Bug Reports": "https://github.com/cryptogpu/crypto-gpu-lib/issues",
        "Source": "https://github.com/cryptogpu/crypto-gpu-lib",
        "Documentation": "https://github.com/cryptogpu/crypto-gpu-lib#readme",
    },
)