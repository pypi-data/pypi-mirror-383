"""
CryptoGPU - High-Performance GPU-Accelerated Cryptocurrency Wallet Generation Library
Supports Bitcoin, Ethereum, Litecoin, Solana and other cryptocurrencies
Uses CUDA for NVIDIA GPUs for maximum performance
"""

from .core import GPUWalletGenerator, WalletBatch
from .networks import NetworkManager, SupportedNetworks
from .cuda_engine import CUDAEngine
from .utils import entropy_to_mnemonic, validate_mnemonic

__version__ = "1.0.1"
__author__ = "CryptoGPU Team"

__all__ = [
    'GPUWalletGenerator',
    'WalletBatch', 
    'NetworkManager',
    'SupportedNetworks',
    'CUDAEngine',
    'entropy_to_mnemonic',
    'validate_mnemonic'
]