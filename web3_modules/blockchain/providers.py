"""
Blockchain RPC Providers

Multi-chain RPC connection management with fallback support
"""

from typing import Dict, List, Optional, Any
from web3 import Web3
import random


class RPCProvider:
    """
    Manage RPC connections to multiple blockchain networks
    with automatic fallback support
    """
    
    # Default RPC endpoints by chain
    DEFAULT_RPC_ENDPOINTS = {
        "ethereum": [
            "https://eth-mainnet.g.alchemy.com/v2/",
            "https://mainnet.infura.io/v3/",
            "https://cloudflare-eth.com",
        ],
        "base": [
            "https://base-mainnet.g.alchemy.com/v2/",
            "https://mainnet.base.org",
        ],
        "arbitrum": [
            "https://arb-mainnet.g.alchemy.com/v2/",
            "https://arb1.arbitrum.io/rpc",
        ],
        "optimism": [
            "https://opt-mainnet.g.alchemy.com/v2/",
            "https://mainnet.optimism.io",
        ],
        "polygon": [
            "https://polygon-mainnet.g.alchemy.com/v2/",
            "https://polygon-rpc.com",
        ],
        "base_sepolia": [
            "https://base-sepolia.g.alchemy.com/v2/",
            "https://sepolia.base.org",
        ],
        "sepolia": [
            "https://eth-sepolia.g.alchemy.com/v2/",
            "https://rpc.sepolia.org",
        ],
    }
    
    # Chain IDs
    CHAIN_IDS = {
        "ethereum": 1,
        "base": 8453,
        "arbitrum": 42161,
        "optimism": 10,
        "polygon": 137,
        "base_sepolia": 84532,
        "sepolia": 11155111,
    }
    
    def __init__(self, api_keys: Optional[Dict[str, str]] = None):
        """
        Initialize RPC Provider
        
        Args:
            api_keys: Dictionary of API keys for providers
                     (alchemy_key, infura_key, etc.)
        """
        self.api_keys = api_keys or {}
        self.connections: Dict[str, Web3] = {}
        self.fallback_order: Dict[str, List[str]] = {}
    
    def get_rpc_url(self, chain: str, endpoint_index: int = 0) -> str:
        """
        Get RPC URL for a chain
        
        Args:
            chain: Chain name
            endpoint_index: Index of endpoint to use
        
        Returns:
            RPC URL
        """
        endpoints = self.DEFAULT_RPC_ENDPOINTS.get(chain, [])
        
        if not endpoints:
            raise ValueError(f"Unknown chain: {chain}")
        
        endpoint = endpoints[endpoint_index % len(endpoints)]
        
        # Replace API key placeholders
        if "ALCHEMY_KEY" in endpoint and "alchemy_key" in self.api_keys:
            endpoint = endpoint.replace("${ALCHEMY_KEY}", self.api_keys["alchemy_key"])
        elif "INFURA_KEY" in endpoint and "infura_key" in self.api_keys:
            endpoint = endpoint.replace("${INFURA_KEY}", self.api_keys["infura_key"])
        
        return endpoint
    
    def get_connection(self, chain: str) -> Web3:
        """
        Get Web3 connection for a chain
        
        Args:
            chain: Chain name
        
        Returns:
            Web3 instance
        """
        if chain in self.connections and self.connections[chain].is_connected():
            return self.connections[chain]
        
        # Try to connect with fallback
        endpoints_tried = 0
        while endpoints_tried < len(self.DEFAULT_RPC_ENDPOINTS.get(chain, [])):
            try:
                rpc_url = self.get_rpc_url(chain, endpoints_tried)
                w3 = Web3(Web3.HTTPProvider(rpc_url))
                
                if w3.is_connected():
                    self.connections[chain] = w3
                    return w3
                
                endpoints_tried += 1
            
            except Exception as e:
                endpoints_tried += 1
        
        raise ConnectionError(f"Failed to connect to {chain} RPC")
    
    def is_connected(self, chain: str) -> bool:
        """Check if connected to a chain"""
        try:
            w3 = self.get_connection(chain)
            return w3.is_connected()
        except:
            return False
    
    def get_chain_id(self, chain: str) -> int:
        """Get chain ID"""
        return self.CHAIN_IDS.get(chain, 0)
    
    def get_block_number(self, chain: str) -> int:
        """Get current block number"""
        w3 = self.get_connection(chain)
        return w3.eth.block_number
    
    def get_gas_price(self, chain: str) -> int:
        """Get current gas price"""
        w3 = self.get_connection(chain)
        return w3.eth.gas_price
    
    def get_balance(self, chain: str, address: str) -> int:
        """Get ETH balance for an address"""
        w3 = self.get_connection(chain)
        return w3.eth.get_balance(Web3.to_checksum_address(address))
    
    def send_transaction(self, chain: str, transaction: Dict[str, Any]) -> str:
        """
        Send a transaction
        
        Args:
            chain: Chain name
            transaction: Transaction dictionary
        
        Returns:
            Transaction hash
        """
        w3 = self.get_connection(chain)
        return w3.eth.send_raw_transaction(transaction)
