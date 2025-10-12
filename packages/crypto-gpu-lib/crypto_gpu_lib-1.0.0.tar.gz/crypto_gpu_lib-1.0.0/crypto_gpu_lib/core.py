"""
Core wallet generation engine with GPU acceleration
High-performance batch processing for cryptocurrency wallet generation
"""

import time
import logging
from typing import List, Dict, Optional, Tuple, Union
from dataclasses import dataclass
from concurrent.futures import ThreadPoolExecutor, as_completed
import numpy as np

from .cuda_engine import CUDAEngine
from .networks import NetworkManager, SupportedNetworks
from .utils import entropy_to_mnemonic, mnemonic_to_seed, derive_key_from_seed

logger = logging.getLogger(__name__)

@dataclass
class Wallet:
    """Individual wallet data structure"""
    mnemonic: str
    seed: bytes
    networks: Dict[SupportedNetworks, Dict[str, str]]
    entropy: bytes
    
    def get_address(self, network: SupportedNetworks) -> Optional[str]:
        """Get address for specific network"""
        return self.networks.get(network, {}).get('address')
    
    def get_private_key(self, network: SupportedNetworks) -> Optional[str]:
        """Get private key for specific network"""
        return self.networks.get(network, {}).get('private_key')
    
    def to_dict(self) -> dict:
        """Convert wallet to dictionary"""
        return {
            'mnemonic': self.mnemonic,
            'seed': self.seed.hex(),
            'entropy': self.entropy.hex(),
            'networks': {
                network.value: data for network, data in self.networks.items()
            }
        }

@dataclass 
class WalletBatch:
    """Batch of generated wallets with metadata"""
    wallets: List[Wallet]
    generation_time: float
    batch_size: int
    networks_generated: List[SupportedNetworks]
    
    def __len__(self) -> int:
        return len(self.wallets)
    
    def get_wallets_for_network(self, network: SupportedNetworks) -> List[Wallet]:
        """Get wallets that have addresses for specific network"""
        return [w for w in self.wallets if network in w.networks]
    
    def to_dict(self) -> dict:
        """Convert batch to dictionary"""
        return {
            'wallets': [w.to_dict() for w in self.wallets],
            'generation_time': self.generation_time,
            'batch_size': self.batch_size,
            'networks_generated': [n.value for n in self.networks_generated],
            'success_rate': len(self.wallets) / self.batch_size if self.batch_size > 0 else 0
        }

class GPUWalletGenerator:
    """
    High-performance GPU-accelerated cryptocurrency wallet generator
    
    Based on the approach described in the Medium article for checking
    trillions of mnemonics using GPU parallelization
    """
    
    def __init__(self, 
                 cuda_device: int = 0,
                 batch_size: int = 10000,
                 networks: Optional[List[SupportedNetworks]] = None,
                 cpu_threads: int = 8):
        """
        Initialize GPU wallet generator
        
        Args:
            cuda_device: CUDA device ID to use
            batch_size: Number of wallets to generate per batch
            networks: List of networks to generate addresses for
            cpu_threads: Number of CPU threads for fallback operations
        """
        self.batch_size = batch_size
        self.cpu_threads = cpu_threads
        
        # Initialize CUDA engine
        try:
            self.cuda_engine = CUDAEngine(cuda_device)
            self.gpu_available = True
            logger.info("GPU acceleration enabled")
        except Exception as e:
            logger.warning(f"GPU initialization failed: {e}")
            self.cuda_engine = None
            self.gpu_available = False
            logger.info("Falling back to CPU mode")
        
        # Initialize network manager
        self.network_manager = NetworkManager()
        
        # Set enabled networks
        if networks:
            # Disable all networks first
            for network in SupportedNetworks:
                self.network_manager.disable_network(network)
            # Enable specified networks
            for network in networks:
                self.network_manager.enable_network(network)
        
        self.enabled_networks = list(self.network_manager.get_enabled_networks())
        
        # Performance tracking
        self.total_generated = 0
        self.total_time = 0.0
        self.start_time = time.time()
        
        logger.info(f"Initialized with batch size: {batch_size}")
        logger.info(f"Enabled networks: {[n.value for n in self.enabled_networks]}")
    
    def generate_batch(self, 
                      batch_size: Optional[int] = None,
                      entropy_bits: int = 128,
                      passphrase: str = "") -> WalletBatch:
        """
        Generate a batch of cryptocurrency wallets
        
        Args:
            batch_size: Override default batch size
            entropy_bits: Bits of entropy (128, 160, 192, 224, 256)
            passphrase: Optional BIP39 passphrase
            
        Returns:
            WalletBatch containing generated wallets
        """
        start_time = time.time()
        
        if batch_size is None:
            batch_size = self.batch_size
        
        logger.debug(f"Generating batch of {batch_size} wallets")
        
        # Generate entropy
        if self.gpu_available:
            entropy_batch = self._generate_entropy_gpu(batch_size, entropy_bits)
        else:
            entropy_batch = self._generate_entropy_cpu(batch_size, entropy_bits)
        
        # Convert entropy to mnemonics and seeds
        wallets = self._process_entropy_batch(entropy_batch, passphrase)
        
        generation_time = time.time() - start_time
        self.total_generated += len(wallets)
        self.total_time += generation_time
        
        logger.debug(f"Generated {len(wallets)} wallets in {generation_time:.2f}s")
        
        return WalletBatch(
            wallets=wallets,
            generation_time=generation_time,
            batch_size=batch_size,
            networks_generated=self.enabled_networks
        )
    
    def _generate_entropy_gpu(self, batch_size: int, entropy_bits: int) -> np.ndarray:
        """Generate entropy using GPU"""
        import cupy as cp
        
        entropy_array = self.cuda_engine.generate_entropy_batch(batch_size, entropy_bits)
        # Convert to CPU numpy array for processing
        return cp.asnumpy(entropy_array)
    
    def _generate_entropy_cpu(self, batch_size: int, entropy_bits: int) -> np.ndarray:
        """Generate entropy using CPU with threading"""
        entropy_bytes = entropy_bits // 8
        
        def generate_chunk(size):
            return np.random.randint(0, 256, size=(size, entropy_bytes), dtype=np.uint8)
        
        if self.cpu_threads > 1:
            chunk_size = max(1, batch_size // self.cpu_threads)
            results = []
            
            with ThreadPoolExecutor(max_workers=self.cpu_threads) as executor:
                futures = []
                remaining = batch_size
                
                for _ in range(self.cpu_threads):
                    chunk = min(chunk_size, remaining)
                    if chunk > 0:
                        futures.append(executor.submit(generate_chunk, chunk))
                        remaining -= chunk
                
                for future in as_completed(futures):
                    results.append(future.result())
            
            return np.vstack(results) if results else generate_chunk(batch_size)
        else:
            return generate_chunk(batch_size)
    
    def _process_entropy_batch(self, entropy_batch: np.ndarray, passphrase: str) -> List[Wallet]:
        """Process entropy batch into wallets"""
        wallets = []
        
        # Use threading for CPU-bound operations
        with ThreadPoolExecutor(max_workers=self.cpu_threads) as executor:
            futures = []
            
            for entropy_bytes in entropy_batch:
                future = executor.submit(self._create_wallet_from_entropy, entropy_bytes, passphrase)
                futures.append(future)
            
            for future in as_completed(futures):
                try:
                    wallet = future.result()
                    if wallet:
                        wallets.append(wallet)
                except Exception as e:
                    logger.debug(f"Wallet creation failed: {e}")
                    continue
        
        return wallets
    
    def _create_wallet_from_entropy(self, entropy_bytes: np.ndarray, passphrase: str) -> Optional[Wallet]:
        """Create wallet from entropy bytes"""
        try:
            # Convert entropy to mnemonic
            mnemonic = entropy_to_mnemonic(entropy_bytes.tobytes())
            
            # Generate seed from mnemonic
            seed = mnemonic_to_seed(mnemonic, passphrase)
            
            # Generate addresses for all enabled networks
            networks = {}
            
            for network in self.enabled_networks:
                try:
                    # Derive private key for this network
                    derivation_path = self.network_manager.get_derivation_path(network)
                    private_key = derive_key_from_seed(seed, derivation_path)
                    
                    # Generate address
                    address = self.network_manager.generate_address_from_private_key(
                        private_key, network
                    )
                    
                    if address:
                        networks[network] = {
                            'address': address,
                            'private_key': private_key.hex(),
                            'derivation_path': derivation_path
                        }
                        
                except Exception as e:
                    logger.debug(f"Failed to generate {network.value} address: {e}")
                    continue
            
            # Only return wallet if at least one network succeeded
            if networks:
                return Wallet(
                    mnemonic=mnemonic,
                    seed=seed,
                    networks=networks,
                    entropy=entropy_bytes.tobytes()
                )
            
        except Exception as e:
            logger.debug(f"Wallet creation failed: {e}")
        
        return None
    
    def generate_single_wallet(self, 
                             entropy_bits: int = 128,
                             passphrase: str = "",
                             networks: Optional[List[SupportedNetworks]] = None) -> Optional[Wallet]:
        """
        Generate a single wallet
        
        Args:
            entropy_bits: Bits of entropy
            passphrase: Optional BIP39 passphrase  
            networks: Override networks for this wallet
            
        Returns:
            Single Wallet or None if generation fails
        """
        # Temporarily override networks if specified
        original_networks = self.enabled_networks.copy()
        
        if networks:
            self.enabled_networks = networks
        
        try:
            batch = self.generate_batch(batch_size=1, entropy_bits=entropy_bits, passphrase=passphrase)
            return batch.wallets[0] if batch.wallets else None
        finally:
            # Restore original networks
            self.enabled_networks = original_networks
    
    def get_performance_stats(self) -> dict:
        """Get performance statistics"""
        elapsed = time.time() - self.start_time
        avg_rate = self.total_generated / self.total_time if self.total_time > 0 else 0
        
        stats = {
            'total_generated': self.total_generated,
            'total_time': self.total_time,
            'elapsed_time': elapsed,
            'average_rate': avg_rate,
            'gpu_enabled': self.gpu_available,
            'batch_size': self.batch_size,
            'enabled_networks': [n.value for n in self.enabled_networks]
        }
        
        if self.gpu_available and self.cuda_engine:
            gpu_stats = self.cuda_engine.get_performance_stats()
            stats.update({'gpu_stats': gpu_stats})
        
        return stats
    
    def cleanup(self):
        """Clean up resources"""
        if self.cuda_engine:
            self.cuda_engine.cleanup()
        
        logger.info("Generator resources cleaned up")
    
    def __del__(self):
        """Destructor"""
        try:
            self.cleanup()
        except:
            pass