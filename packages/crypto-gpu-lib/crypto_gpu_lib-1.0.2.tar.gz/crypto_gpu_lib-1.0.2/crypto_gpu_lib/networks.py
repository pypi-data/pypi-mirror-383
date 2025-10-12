"""
Network definitions and address generation for supported cryptocurrencies
Supports Bitcoin, Ethereum, Litecoin, Solana, and other major cryptocurrencies
"""

from enum import Enum
from typing import Dict, Tuple, Optional
import hashlib
import base58
from eth_account import Account
from solders.keypair import Keypair
from solders.pubkey import Pubkey
import logging

logger = logging.getLogger(__name__)

class SupportedNetworks(Enum):
    """Supported cryptocurrency networks"""
    BITCOIN = "BTC"
    ETHEREUM = "ETH" 
    LITECOIN = "LTC"
    SOLANA = "SOL"
    BITCOIN_CASH = "BCH"
    DOGECOIN = "DOGE"
    DASH = "DASH"

class NetworkManager:
    """Manages cryptocurrency network configurations and address generation"""
    
    # BIP44 derivation paths for different cryptocurrencies
    DERIVATION_PATHS = {
        SupportedNetworks.BITCOIN: "m/44'/0'/0'/0/0",
        SupportedNetworks.ETHEREUM: "m/44'/60'/0'/0/0", 
        SupportedNetworks.LITECOIN: "m/44'/2'/0'/0/0",
        SupportedNetworks.SOLANA: "m/44'/501'/0'/0/0",
        SupportedNetworks.BITCOIN_CASH: "m/44'/145'/0'/0/0",
        SupportedNetworks.DOGECOIN: "m/44'/3'/0'/0/0",
        SupportedNetworks.DASH: "m/44'/5'/0'/0/0"
    }
    
    # Network-specific parameters
    NETWORK_PARAMS = {
        SupportedNetworks.BITCOIN: {
            'symbol': 'BTC',
            'p2pkh_prefix': b'\x00',
            'wif_prefix': b'\x80',
            'decimals': 8
        },
        SupportedNetworks.ETHEREUM: {
            'symbol': 'ETH', 
            'decimals': 18
        },
        SupportedNetworks.LITECOIN: {
            'symbol': 'LTC',
            'p2pkh_prefix': b'\x30',
            'wif_prefix': b'\xb0', 
            'decimals': 8
        },
        SupportedNetworks.SOLANA: {
            'symbol': 'SOL',
            'decimals': 9
        },
        SupportedNetworks.BITCOIN_CASH: {
            'symbol': 'BCH',
            'p2pkh_prefix': b'\x00',
            'wif_prefix': b'\x80',
            'decimals': 8
        },
        SupportedNetworks.DOGECOIN: {
            'symbol': 'DOGE',
            'p2pkh_prefix': b'\x1e',
            'wif_prefix': b'\x9e',
            'decimals': 8
        },
        SupportedNetworks.DASH: {
            'symbol': 'DASH',
            'p2pkh_prefix': b'\x4c',
            'wif_prefix': b'\xcc',
            'decimals': 8
        }
    }
    
    def __init__(self):
        """Initialize network manager"""
        self.enabled_networks = set(SupportedNetworks)
    
    def enable_network(self, network: SupportedNetworks):
        """Enable a specific network"""
        self.enabled_networks.add(network)
    
    def disable_network(self, network: SupportedNetworks):
        """Disable a specific network"""
        self.enabled_networks.discard(network)
    
    def get_enabled_networks(self) -> set:
        """Get list of enabled networks"""
        return self.enabled_networks.copy()
    
    def generate_address_from_private_key(self, private_key: bytes, network: SupportedNetworks) -> Optional[str]:
        """
        Generate address from private key for specified network
        
        Args:
            private_key: 32-byte private key
            network: Target cryptocurrency network
            
        Returns:
            Address string or None if generation fails
        """
        try:
            if network == SupportedNetworks.ETHEREUM:
                return self._generate_ethereum_address(private_key)
            elif network == SupportedNetworks.SOLANA:
                return self._generate_solana_address(private_key)
            elif network in [SupportedNetworks.BITCOIN, SupportedNetworks.LITECOIN, 
                           SupportedNetworks.BITCOIN_CASH, SupportedNetworks.DOGECOIN, 
                           SupportedNetworks.DASH]:
                return self._generate_bitcoin_like_address(private_key, network)
            else:
                logger.warning(f"Unsupported network: {network}")
                return None
                
        except Exception as e:
            logger.debug(f"Address generation failed for {network}: {e}")
            return None
    
    def _generate_ethereum_address(self, private_key: bytes) -> str:
        """Generate Ethereum address from private key"""
        account = Account.from_key(private_key)
        return account.address
    
    def _generate_solana_address(self, private_key: bytes) -> str:
        """Generate Solana address from private key"""
        # Solana uses Ed25519, need to handle differently
        keypair = Keypair.from_bytes(private_key[:32])
        return str(keypair.pubkey())
    
    def _generate_bitcoin_like_address(self, private_key: bytes, network: SupportedNetworks) -> str:
        """Generate Bitcoin-like address (BTC, LTC, BCH, DOGE, DASH)"""
        import ecdsa
        from ecdsa.curves import SECP256k1
        
        # Get network parameters
        params = self.NETWORK_PARAMS[network]
        
        # Generate public key from private key
        sk = ecdsa.SigningKey.from_string(private_key, curve=SECP256k1)
        vk = sk.get_verifying_key()
        
        # Get compressed public key
        public_key = b'\x02' + vk.to_string()[:32] if vk.to_string()[32] % 2 == 0 else b'\x03' + vk.to_string()[:32]
        
        # Generate address hash
        sha256_hash = hashlib.sha256(public_key).digest()
        ripemd160_hash = hashlib.new('ripemd160', sha256_hash).digest()
        
        # Add network prefix
        versioned_hash = params['p2pkh_prefix'] + ripemd160_hash
        
        # Calculate checksum
        checksum = hashlib.sha256(hashlib.sha256(versioned_hash).digest()).digest()[:4]
        
        # Create final address
        address_bytes = versioned_hash + checksum
        address = base58.b58encode(address_bytes).decode()
        
        return address
    
    def get_derivation_path(self, network: SupportedNetworks) -> str:
        """Get BIP44 derivation path for network"""
        return self.DERIVATION_PATHS.get(network, "m/44'/0'/0'/0/0")
    
    def get_network_params(self, network: SupportedNetworks) -> dict:
        """Get network parameters"""
        return self.NETWORK_PARAMS.get(network, {})
    
    def validate_address(self, address: str, network: SupportedNetworks) -> bool:
        """
        Validate address format for specific network
        
        Args:
            address: Address string to validate
            network: Network to validate against
            
        Returns:
            True if address is valid format
        """
        try:
            if network == SupportedNetworks.ETHEREUM:
                return len(address) == 42 and address.startswith('0x')
            elif network == SupportedNetworks.SOLANA:
                return len(address) >= 32 and len(address) <= 44
            elif network in [SupportedNetworks.BITCOIN, SupportedNetworks.LITECOIN,
                           SupportedNetworks.BITCOIN_CASH, SupportedNetworks.DOGECOIN,
                           SupportedNetworks.DASH]:
                # Basic Bitcoin-like address validation
                try:
                    decoded = base58.b58decode(address)
                    return len(decoded) == 25
                except:
                    return False
            else:
                return False
                
        except Exception:
            return False
    
    @classmethod
    def get_all_networks(cls) -> list:
        """Get list of all supported networks"""
        return list(SupportedNetworks)
    
    @classmethod
    def get_network_by_symbol(cls, symbol: str) -> Optional[SupportedNetworks]:
        """Get network enum by symbol string"""
        for network in SupportedNetworks:
            if network.value == symbol.upper():
                return network
        return None