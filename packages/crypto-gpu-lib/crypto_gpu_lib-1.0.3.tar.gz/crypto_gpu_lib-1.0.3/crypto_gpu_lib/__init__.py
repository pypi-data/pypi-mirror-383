"""
CryptoGPU - High-Performance GPU-Accelerated Cryptocurrency Wallet Generation Library
Supports Bitcoin, Ethereum, Litecoin, Solana and other cryptocurrencies
Uses CUDA for NVIDIA GPUs for maximum performance
"""

from .core import GPUWalletGenerator, WalletBatch
from .networks import NetworkManager, SupportedNetworks
from .cuda_engine import CUDAEngine
from .utils import entropy_to_mnemonic, validate_mnemonic

# High-performance components
try:
    from .fast_core import UltraFastWalletGenerator, FastWallet, FastWalletBatch, quick_performance_test
    from .gpu_crypto import HighPerformanceWalletGenerator, GPUCrypto
    FAST_MODE_AVAILABLE = True
except ImportError:
    FAST_MODE_AVAILABLE = False

__version__ = "1.0.3"
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

# Add fast components if available
if FAST_MODE_AVAILABLE:
    __all__.extend([
        'UltraFastWalletGenerator',
        'FastWallet',
        'FastWalletBatch',
        'HighPerformanceWalletGenerator',
        'GPUCrypto',
        'quick_performance_test'
    ])