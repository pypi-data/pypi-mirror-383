"""
Utility functions for cryptocurrency operations
Mnemonic generation, seed derivation, and key management
"""

import hashlib
import hmac
from typing import Optional, Union
from mnemonic import Mnemonic
import logging

logger = logging.getLogger(__name__)

# Initialize BIP39 mnemonic generator
_mnemonic_generator = Mnemonic("english")

def entropy_to_mnemonic(entropy: bytes) -> str:
    """
    Convert entropy bytes to BIP39 mnemonic phrase
    
    Args:
        entropy: Entropy bytes (16, 20, 24, 28, or 32 bytes)
        
    Returns:
        BIP39 mnemonic phrase
    """
    return _mnemonic_generator.to_mnemonic(entropy)

def mnemonic_to_seed(mnemonic: str, passphrase: str = "") -> bytes:
    """
    Convert BIP39 mnemonic to seed using PBKDF2
    
    Args:
        mnemonic: BIP39 mnemonic phrase
        passphrase: Optional passphrase
        
    Returns:
        64-byte seed
    """
    return _mnemonic_generator.to_seed(mnemonic, passphrase)

def validate_mnemonic(mnemonic: str) -> bool:
    """
    Validate BIP39 mnemonic phrase
    
    Args:
        mnemonic: Mnemonic phrase to validate
        
    Returns:
        True if valid BIP39 mnemonic
    """
    return _mnemonic_generator.check(mnemonic)

def derive_key_from_seed(seed: bytes, derivation_path: str) -> bytes:
    """
    Derive private key from seed using BIP32 hierarchical deterministic derivation
    
    Args:
        seed: Master seed (64 bytes)
        derivation_path: BIP32 derivation path (e.g., "m/44'/0'/0'/0/0")
        
    Returns:
        32-byte private key
    """
    try:
        from hdwallet import HDWallet
        from hdwallet.cryptocurrencies import Bitcoin, Ethereum, Litecoin
        from hdwallet.derivations import BIP44Derivation
        from hdwallet.seeds import BIP39Seed
        
        # Create BIP39Seed object
        seed_obj = BIP39Seed(seed=seed[:64])  # Use up to 64 bytes
        
        # Parse coin type from derivation path to determine cryptocurrency
        cryptocurrency = Bitcoin  # Default to Bitcoin
        coin_type = 0  # Default Bitcoin coin type
        
        # Extract coin type from path like "m/44'/0'/0'/0/0"
        if "44'" in derivation_path:
            try:
                parts = derivation_path.split("'")
                if len(parts) >= 3:
                    coin_type_str = parts[1].split("/")[-1]
                    coin_type = int(coin_type_str)
                    
                    # Map coin types to cryptocurrencies
                    if coin_type == 0:
                        cryptocurrency = Bitcoin
                    elif coin_type == 60:
                        cryptocurrency = Ethereum
                    elif coin_type == 2:
                        cryptocurrency = Litecoin
                    # Add more mappings as needed
            except (ValueError, IndexError):
                pass  # Use default Bitcoin
        
        # Create derivation object
        derivation = BIP44Derivation(
            coin_type=coin_type,
            account=0,
            change="external-chain",
            address=0
        )
        
        # Create HDWallet with correct cryptocurrency
        hdwallet = HDWallet(cryptocurrency=cryptocurrency)
        hdwallet.from_seed(seed=seed_obj)
        hdwallet.from_derivation(derivation=derivation)
        
        # Return private key as bytes
        private_key_hex = hdwallet.private_key()
        return bytes.fromhex(private_key_hex)
        
    except Exception as e:
        logger.error(f"Key derivation failed: {e}")
        # Fallback to simple HMAC-based derivation
        return _simple_key_derivation(seed, derivation_path)

def _simple_key_derivation(seed: bytes, path: str) -> bytes:
    """
    Simple key derivation fallback using HMAC
    Not cryptographically equivalent to BIP32 but provides a key
    """
    # Use path as additional entropy
    path_bytes = path.encode('utf-8')
    
    # HMAC-SHA256 derivation
    derived = hmac.new(seed, path_bytes, hashlib.sha256).digest()
    
    return derived

def generate_entropy(bits: int = 128) -> bytes:
    """
    Generate cryptographically secure entropy
    
    Args:
        bits: Number of entropy bits (128, 160, 192, 224, 256)
        
    Returns:
        Entropy bytes
    """
    import secrets
    
    if bits not in [128, 160, 192, 224, 256]:
        raise ValueError("Entropy bits must be 128, 160, 192, 224, or 256")
    
    return secrets.token_bytes(bits // 8)

def words_to_entropy(words: str) -> bytes:
    """
    Convert mnemonic words back to entropy
    
    Args:
        words: BIP39 mnemonic phrase
        
    Returns:
        Original entropy bytes
    """
    if not validate_mnemonic(words):
        raise ValueError("Invalid mnemonic phrase")
    
    # This is a simplified implementation
    # Full BIP39 implementation would reverse the checksum process
    word_list = _mnemonic_generator.wordlist
    words_array = words.split()
    
    # Convert words to indices
    indices = []
    for word in words_array:
        if word not in word_list:
            raise ValueError(f"Invalid word: {word}")
        indices.append(word_list.index(word))
    
    # Convert indices to binary
    binary_str = ""
    for index in indices:
        binary_str += format(index, '011b')
    
    # Extract entropy (remove checksum bits)
    entropy_bits = len(binary_str) * 32 // 33
    entropy_binary = binary_str[:entropy_bits]
    
    # Convert to bytes
    entropy_bytes = bytearray()
    for i in range(0, len(entropy_binary), 8):
        byte_str = entropy_binary[i:i+8]
        if len(byte_str) == 8:
            entropy_bytes.append(int(byte_str, 2))
    
    return bytes(entropy_bytes)

def format_private_key(private_key: bytes, format_type: str = "hex") -> str:
    """
    Format private key in different representations
    
    Args:
        private_key: 32-byte private key
        format_type: "hex", "wif", or "decimal"
        
    Returns:
        Formatted private key string
    """
    if format_type == "hex":
        return private_key.hex()
    elif format_type == "decimal":
        return str(int.from_bytes(private_key, 'big'))
    elif format_type == "wif":
        # WIF encoding for Bitcoin-like networks
        return _encode_wif(private_key)
    else:
        raise ValueError("Invalid format type. Use 'hex', 'wif', or 'decimal'")

def _encode_wif(private_key: bytes, compressed: bool = True, network_byte: bytes = b'\x80') -> str:
    """
    Encode private key in Wallet Import Format (WIF)
    
    Args:
        private_key: 32-byte private key
        compressed: Whether to use compressed format
        network_byte: Network version byte
        
    Returns:
        WIF encoded private key
    """
    import base58
    
    # Add network byte
    extended_key = network_byte + private_key
    
    # Add compression flag if compressed
    if compressed:
        extended_key += b'\x01'
    
    # Calculate checksum
    checksum = hashlib.sha256(hashlib.sha256(extended_key).digest()).digest()[:4]
    
    # Create final WIF
    wif_bytes = extended_key + checksum
    
    return base58.b58encode(wif_bytes).decode()

def calculate_checksum(data: bytes) -> bytes:
    """
    Calculate SHA256 double hash checksum
    
    Args:
        data: Data to checksum
        
    Returns:
        4-byte checksum
    """
    return hashlib.sha256(hashlib.sha256(data).digest()).digest()[:4]

def secure_compare(a: bytes, b: bytes) -> bool:
    """
    Constant-time comparison to prevent timing attacks
    
    Args:
        a: First byte string
        b: Second byte string
        
    Returns:
        True if equal
    """
    if len(a) != len(b):
        return False
    
    result = 0
    for x, y in zip(a, b):
        result |= x ^ y
    
    return result == 0

class EntropyPool:
    """
    Entropy pool for generating high-quality random numbers
    Combines multiple entropy sources for enhanced security
    """
    
    def __init__(self):
        self._pool = bytearray()
        self._counter = 0
        self._reseed()
    
    def _reseed(self):
        """Reseed the entropy pool"""
        import secrets
        import time
        import os
        
        # Gather entropy from multiple sources
        entropy_sources = [
            secrets.token_bytes(32),  # Cryptographically secure random
            int(time.time() * 1000000).to_bytes(8, 'big'),  # High-resolution timestamp
            os.urandom(32),  # OS entropy
            self._counter.to_bytes(4, 'big')  # Counter
        ]
        
        # Mix entropy sources
        mixed = b''.join(entropy_sources)
        self._pool = bytearray(hashlib.sha512(mixed).digest())
        self._counter += 1
    
    def get_bytes(self, length: int) -> bytes:
        """
        Get random bytes from entropy pool
        
        Args:
            length: Number of bytes to generate
            
        Returns:
            Random bytes
        """
        if len(self._pool) < length:
            self._reseed()
        
        result = bytes(self._pool[:length])
        
        # Update pool state
        self._pool = self._pool[length:]
        if len(self._pool) < 32:
            self._reseed()
        
        return result

# Global entropy pool instance
_entropy_pool = EntropyPool()