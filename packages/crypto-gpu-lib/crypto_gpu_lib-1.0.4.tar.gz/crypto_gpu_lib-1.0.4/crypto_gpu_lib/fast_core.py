"""
Ultra-fast core wallet generation engine
Bypasses HDWallet for maximum performance using GPU-accelerated cryptography
"""

import time
import logging
from typing import List, Dict, Optional
from dataclasses import dataclass
import numpy as np

from .gpu_crypto import HighPerformanceWalletGenerator, GPUCrypto
from .ultra_fast_crypto import UltraFastWalletEngine, ultra_fast_performance_test
from .networks import SupportedNetworks

logger = logging.getLogger(__name__)

@dataclass
class FastWallet:
    """Lightweight wallet data structure for high performance"""
    mnemonic: str
    networks: Dict[str, Dict[str, str]]
    
    def get_address(self, network: str) -> Optional[str]:
        """Get address for network"""
        return self.networks.get(network, {}).get('address')
    
    def get_private_key(self, network: str) -> Optional[str]:
        """Get private key for network"""
        return self.networks.get(network, {}).get('private_key')

@dataclass
class FastWalletBatch:
    """High-performance wallet batch"""
    wallets: List[FastWallet]
    generation_time: float
    batch_size: int
    rate: float
    
    def __len__(self) -> int:
        return len(self.wallets)

class UltraFastWalletGenerator:
    """
    Ultra-high-performance wallet generator
    Optimized for 10,000+ wallets per second using GPU acceleration
    """
    
    def __init__(self, batch_size: int = 10000, networks: List[str] = None):
        """
        Initialize ultra-fast generator
        
        Args:
            batch_size: Number of wallets per batch (larger = faster)
            networks: List of network symbols ['BTC', 'ETH', 'LTC', etc.]
        """
        self.batch_size = batch_size
        self.networks = networks or ['BTC', 'ETH', 'LTC']
        
        # Initialize high-performance generator
        self.hp_generator = HighPerformanceWalletGenerator(batch_size)
        self.gpu_crypto = GPUCrypto()
        
        # Performance tracking
        self.total_generated = 0
        self.total_time = 0.0
        
        print(f"🚀 UltraFast Generator Ready")
        print(f"   Target Networks: {self.networks}")
        print(f"   Batch Size: {batch_size:,}")
        print(f"   GPU Available: {self.gpu_crypto.gpu_available}")
    
    def generate_batch_ultra_fast(self, count: Optional[int] = None) -> FastWalletBatch:
        """
        Generate wallets at maximum speed
        
        Args:
            count: Number of wallets to generate (default: batch_size)
            
        Returns:
            FastWalletBatch with generated wallets
        """
        if count is None:
            count = self.batch_size
        
        start_time = time.time()
        
        # Try ultra-fast engine first (bypasses PBKDF2 bottleneck)
        try:
            ultra_engine = UltraFastWalletEngine()
            result = ultra_engine.generate_wallets_maximum_speed(count, self.networks)
            
            # Convert to FastWallet objects
            fast_wallets = []
            for wallet_data in result['wallets']:
                fast_wallet = FastWallet(
                    mnemonic=wallet_data['mnemonic'],
                    networks=wallet_data['networks']
                )
                fast_wallets.append(fast_wallet)
            
            generation_time = time.time() - start_time
            rate = len(fast_wallets) / generation_time if generation_time > 0 else 0
            
            print(f"🚀 ULTRA-FAST MODE: {rate:,.0f} wallets/second")
            
        except Exception as e:
            print(f"⚠️ Ultra-fast mode failed: {e}")
            print("🔄 Falling back to standard fast mode...")
            
            # Fallback to standard high-performance generator
            result = self.hp_generator.generate_wallets_ultra_fast(count, self.networks)
            
            # Convert to FastWallet objects
            fast_wallets = []
            for wallet_data in result['wallets']:
                fast_wallet = FastWallet(
                    mnemonic=wallet_data['mnemonic'],
                    networks=wallet_data['networks']
                )
                fast_wallets.append(fast_wallet)
            
            generation_time = time.time() - start_time
            rate = len(fast_wallets) / generation_time if generation_time > 0 else 0
        
        # Update stats
        self.total_generated += len(fast_wallets)
        self.total_time += generation_time
        
        return FastWalletBatch(
            wallets=fast_wallets,
            generation_time=generation_time,
            batch_size=count,
            rate=rate
        )
    
    def generate_single_wallet_fast(self) -> Optional[FastWallet]:
        """Generate a single wallet quickly"""
        batch = self.generate_batch_ultra_fast(1)
        return batch.wallets[0] if batch.wallets else None
    
    def benchmark_performance(self, test_counts: List[int] = None) -> Dict:
        """
        Benchmark performance with different batch sizes
        
        Args:
            test_counts: List of wallet counts to test
            
        Returns:
            Performance benchmark results
        """
        if test_counts is None:
            test_counts = [100, 1000, 5000, 10000]
        
        print("🏃 Running Performance Benchmark")
        print("=" * 50)
        
        results = {}
        
        for count in test_counts:
            print(f"\n📊 Testing {count:,} wallets...")
            
            # Run test
            batch = self.generate_batch_ultra_fast(count)
            
            results[count] = {
                'wallets_generated': len(batch.wallets),
                'time_taken': batch.generation_time,
                'rate': batch.rate,
                'success_rate': len(batch.wallets) / count * 100
            }
            
            print(f"   ✅ Generated: {len(batch.wallets):,}")
            print(f"   ⏱️ Time: {batch.generation_time:.2f}s")
            print(f"   ⚡ Rate: {batch.rate:.0f} wallets/second")
        
        # Find best performance
        best_count = max(results.keys(), key=lambda k: results[k]['rate'])
        best_rate = results[best_count]['rate']
        
        print(f"\n🏆 Best Performance: {best_count:,} wallets at {best_rate:.0f}/second")
        
        return results
    
    def get_performance_stats(self) -> Dict:
        """Get overall performance statistics"""
        avg_rate = self.total_generated / self.total_time if self.total_time > 0 else 0
        
        return {
            'total_generated': self.total_generated,
            'total_time': self.total_time,
            'average_rate': avg_rate,
            'gpu_available': self.gpu_crypto.gpu_available,
            'networks': self.networks,
            'batch_size': self.batch_size
        }

# Convenience function for quick testing
def quick_performance_test(count: int = 10000, networks: List[str] = None) -> Dict:
    """
    Quick performance test function
    
    Args:
        count: Number of wallets to generate
        networks: Networks to test
        
    Returns:
        Test results
    """
    if networks is None:
        networks = ['BTC', 'ETH', 'LTC']
    
    print(f"🚀 Quick Performance Test: {count:,} wallets")
    print(f"Networks: {networks}")
    
    generator = UltraFastWalletGenerator(batch_size=count, networks=networks)
    batch = generator.generate_batch_ultra_fast(count)
    
    print(f"\n📊 Results:")
    print(f"   Generated: {len(batch.wallets):,} wallets")
    print(f"   Time: {batch.generation_time:.2f} seconds")
    print(f"   Rate: {batch.rate:.0f} wallets/second")
    
    # Show sample wallets
    if batch.wallets:
        print(f"\n📋 Sample Wallets:")
        for i, wallet in enumerate(batch.wallets[:3]):
            print(f"   Wallet {i+1}:")
            print(f"     Mnemonic: {wallet.mnemonic[:50]}...")
            for network, data in wallet.networks.items():
                print(f"     {network}: {data['address']}")
    
    return {
        'count': len(batch.wallets),
        'time': batch.generation_time,
        'rate': batch.rate,
        'wallets': batch.wallets
    }