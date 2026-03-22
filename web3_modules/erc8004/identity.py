"""
ERC-8004 Identity Registry Implementation

Manages AI agent identity on Ethereum via ERC-8004 standard:
- Mint agent identity as ERC-721 NFT
- Store Agent Card metadata (capabilities, endpoints, payment info)
- Discover agents by capabilities
"""

import json
import os
from typing import List, Dict, Optional, Any
from web3 import Web3
from web3.contract import Contract
import requests


class ERC8004Identity:
    """
    Manage AI agent identity on Ethereum via ERC-8004
    """
    
    # Default ERC-8004 Identity Registry addresses (update after deployment)
    REGISTRY_ADDRESSES = {
        "ethereum": "0x...",  # Mainnet deployment
        "base": "0x...",       # Base mainnet
        "base_sepolia": "0x...",  # Base Sepolia testnet
        "sepolia": "0x...",    # Ethereum Sepolia testnet
        "anvil": "0xF818A7C2AFC45cF4B9DDC48933C9A1edD624e46f",  # Latest deployment with indexing
    }
    
    # ABI for Identity Registry (loaded from compiled contracts)
    IDENTITY_REGISTRY_ABI = [
        {
            "inputs": [
                {"name": "owner", "type": "address"},
                {"name": "agentCardURI", "type": "string"}
            ],
            "name": "mintAgent",
            "outputs": [{"name": "tokenId", "type": "uint256"}],
            "stateMutability": "nonpayable",
            "type": "function"
        },
        {
            "inputs": [
                {"name": "owner", "type": "address"},
                {"name": "agentCardURI", "type": "string"},
                {"name": "capabilities", "type": "bytes32[]"}
            ],
            "name": "mintAgentWithCapabilities",
            "outputs": [{"name": "tokenId", "type": "uint256"}],
            "stateMutability": "nonpayable",
            "type": "function"
        },
        {
            "inputs": [{"name": "tokenId", "type": "uint256"}],
            "name": "getAgentCard",
            "outputs": [{"name": "agentCardURI", "type": "string"}],
            "stateMutability": "view",
            "type": "function"
        },
        {
            "inputs": [{"name": "tokenId", "type": "uint256"}],
            "name": "ownerOf",
            "outputs": [{"name": "owner", "type": "address"}],
            "stateMutability": "view",
            "type": "function"
        },
        {
            "inputs": [
                {"name": "capabilities", "type": "bytes32[]"}
            ],
            "name": "discoverAgents",
            "outputs": [{"name": "tokenIds", "type": "uint256[]"}],
            "stateMutability": "view",
            "type": "function"
        },
        {
            "inputs": [],
            "name": "getTotalAgents",
            "outputs": [{"name": "", "type": "uint256"}],
            "stateMutability": "view",
            "type": "function"
        },
        {
            "inputs": [{"name": "owner", "type": "address"}],
            "name": "getAgentsByOwner",
            "outputs": [{"name": "", "type": "uint256[]"}],
            "stateMutability": "view",
            "type": "function"
        },
        {
            "anonymous": False,
            "inputs": [
                {"indexed": True, "name": "from", "type": "address"},
                {"indexed": True, "name": "to", "type": "address"},
                {"indexed": True, "name": "tokenId", "type": "uint256"}
            ],
            "name": "Transfer",
            "type": "event"
        },
        {
            "anonymous": False,
            "inputs": [
                {"indexed": True, "name": "agentId", "type": "uint256"},
                {"indexed": True, "name": "owner", "type": "address"},
                {"indexed": False, "name": "agentCardURI", "type": "string"},
                {"indexed": False, "name": "capabilities", "type": "bytes32[]"}
            ],
            "name": "AgentRegistered",
            "type": "event"
        }
    ]
    
    def __init__(self, rpc_url: str, private_key: Optional[str] = None):
        """
        Initialize ERC-8004 Identity manager
        
        Args:
            rpc_url: Ethereum RPC endpoint (e.g., Alchemy, Infura)
            private_key: Optional private key for signing transactions
        """
        self.w3 = Web3(Web3.HTTPProvider(rpc_url))
        self.private_key = private_key
        
        if private_key:
            self.account = self.w3.eth.account.from_key(private_key)
            self.address = self.account.address
        else:
            self.account = None
            self.address = None
        
        self.contract = None
        self.chain_id = self.w3.eth.chain_id
    
    def set_registry_address(self, address: str):
        """
        Set the Identity Registry contract address
        
        Args:
            address: Contract address
        """
        self.contract = self.w3.eth.contract(
            address=Web3.to_checksum_address(address),
            abi=self.IDENTITY_REGISTRY_ABI
        )
    
    def create_agent_card(
        self,
        agent_name: str,
        capabilities: List[str],
        description: str = "",
        service_endpoints: Optional[Dict[str, str]] = None,
        payment_address: Optional[str] = None,
        x402_accepted: bool = True,
        metadata: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """
        Create Agent Card metadata
        
        Args:
            agent_name: Name of the agent
            capabilities: List of capabilities (e.g., ["defi_tracking", "nft_analysis"])
            description: Agent description
            service_endpoints: Dict of service endpoints (MCP, HTTP, etc.)
            payment_address: Wallet address for receiving payments
            x402_accepted: Whether agent accepts x402 payments
            metadata: Additional metadata
        
        Returns:
            Agent Card dictionary
        """
        agent_card = {
            "name": agent_name,
            "description": description or f"Web3 AI Agent: {agent_name}",
            "capabilities": capabilities,
            "serviceEndpoints": service_endpoints or {},
            "paymentAddress": payment_address or self.address,
            "x402Accepted": x402_accepted,
            "metadata": metadata or {},
            "version": "1.0.0"
        }
        
        return agent_card
    
    def upload_agent_card(self, agent_card: Dict[str, Any], storage_type: str = "ipfs") -> str:
        """
        Upload Agent Card to decentralized storage
        
        Args:
            agent_card: Agent Card dictionary
            storage_type: Storage backend ("ipfs", "arweave", "http")
        
        Returns:
            URI pointing to Agent Card (e.g., "ipfs://...")
        """
        if storage_type == "ipfs":
            # Upload to IPFS via Pinata or similar
            # For now, return placeholder
            agent_card_json = json.dumps(agent_card)
            # TODO: Implement actual IPFS upload
            # response = requests.post("https://api.pinata.cloud/pinning/pinJSONToIPFS", ...)
            return "ipfs://QmPlaceholder..."
        
        elif storage_type == "arweave":
            # Upload to Arweave
            # TODO: Implement Arweave upload
            return "ar://Placeholder..."
        
        else:  # http
            # Host on HTTP server
            return "https://agentx.dev/agent-cards/placeholder.json"
    
    def register_agent(
        self,
        agent_name: str,
        capabilities: List[str],
        description: str = "",
        service_endpoints: Optional[Dict[str, str]] = None,
        storage_type: str = "ipfs"
    ) -> int:
        """
        Register new agent identity and mint ERC-721 NFT
        
        Args:
            agent_name: Name of the agent
            capabilities: List of capabilities
            description: Agent description
            service_endpoints: Service endpoints
            storage_type: Where to store Agent Card
        
        Returns:
            Token ID (agent ID)
        """
        if not self.contract:
            raise ValueError("Registry contract address not set. Call set_registry_address() first.")
        
        if not self.account:
            raise ValueError("Private key required to register agent.")
        
        # Create and upload Agent Card
        agent_card = self.create_agent_card(
            agent_name=agent_name,
            capabilities=capabilities,
            description=description,
            service_endpoints=service_endpoints,
            payment_address=self.address
        )
        
        agent_card_uri = self.upload_agent_card(agent_card, storage_type)
        
        # Build transaction
        tx = self.contract.functions.mintAgent(
            self.address,
            agent_card_uri
        ).build_transaction({
            "from": self.address,
            "nonce": self.w3.eth.get_transaction_count(self.address),
            "chainId": self.chain_id,
            "gas": 500000,
            "gasPrice": self.w3.eth.gas_price
        })
        
        # Sign and send transaction
        signed_tx = self.w3.eth.account.sign_transaction(tx, self.private_key)
        tx_hash = self.w3.eth.send_raw_transaction(signed_tx.raw_transaction)
        
        # Wait for receipt
        receipt = self.w3.eth.wait_for_transaction_receipt(tx_hash)
        
        # Extract token ID from event logs
        token_id = self._extract_token_id_from_logs(receipt)
        
        return token_id
    
    def _extract_token_id_from_logs(self, receipt) -> int:
        """
        Extract token ID from Transfer event logs
        """
        # Try to extract from contract events first
        for log in receipt["logs"]:
            try:
                event = self.contract.events.Transfer().process_log(log)
                return event["args"]["tokenId"]
            except:
                continue
        
        # Fallback: parse from topics directly
        # Transfer event has 4 topics: [event_signature, from, to, tokenId]
        for log in receipt["logs"]:
            if len(log["topics"]) == 4:
                # Event signature for Transfer(address,address,uint256)
                if log["topics"][0] == "0xddf252ad1be2c89b69c2b068fc378daa952ba7f163c4a11628f55a4df523b3ef":
                    token_id = int(log["topics"][3], 16)
                    return token_id
        
        # Last fallback: check AgentRegistered event
        for log in receipt["logs"]:
            try:
                event = self.contract.events.AgentRegistered().process_log(log)
                return event["args"]["agentId"]
            except:
                continue
        
        raise ValueError("Could not extract token ID from transaction logs")
    
    def get_agent_card(self, token_id: int) -> Dict[str, Any]:
        """
        Get Agent Card metadata for a given token ID
        
        Args:
            token_id: Agent token ID
        
        Returns:
            Agent Card dictionary
        """
        if not self.contract:
            raise ValueError("Registry contract address not set.")
        
        # Get Agent Card URI from contract
        uri = self.contract.functions.getAgentCard(token_id).call()
        
        # Fetch and parse Agent Card
        # For IPFS, you'd need a gateway like ipfs.io
        if uri.startswith("ipfs://"):
            uri = uri.replace("ipfs://", "https://ipfs.io/ipfs/")
        
        # Handle placeholder URLs
        if "placeholder" in uri.lower():
            # Return mock data for testing
            return {
                "name": "Test Agent",
                "description": "Test agent for ERC-8004 validation",
                "capabilities": ["defi_tracking", "nft_analysis", "whale_alert"],
                "serviceEndpoints": {
                    "mcp": "http://localhost:8080/mcp",
                    "http": "http://localhost:8080/api"
                },
                "paymentAddress": self.address,
                "x402Accepted": True,
                "metadata": {},
                "version": "1.0.0"
            }
        
        try:
            response = requests.get(uri)
            response.raise_for_status()
            return response.json()
        except Exception as e:
            # Return mock data if fetch fails
            return {
                "name": f"Agent {token_id}",
                "description": "Agent registered on ERC-8004",
                "capabilities": [],
                "uri": uri,
                "error": str(e)
            }
    
    def get_owner(self, token_id: int) -> str:
        """
        Get owner address of an agent
        
        Args:
            token_id: Agent token ID
        
        Returns:
            Owner address
        """
        if not self.contract:
            raise ValueError("Registry contract address not set.")
        
        return self.contract.functions.ownerOf(token_id).call()
    
    def discover_agents(self, capabilities: List[str]) -> List[int]:
        """
        Discover agents by capabilities
        
        Args:
            capabilities: List of capabilities to search for (e.g., ["defi_tracking"])
        
        Returns:
            List of token IDs (as Python ints)
        """
        if not self.contract:
            raise ValueError("Registry contract address not set.")
        
        # Convert capabilities to bytes32 hashes
        capability_hashes = []
        for cap in capabilities:
            # Hash the capability string to bytes32 and convert to hex string
            capability_hash = Web3.keccak(text=cap)
            # Convert HexBytes to hex string to avoid encoding issues
            capability_hashes.append(Web3.to_hex(capability_hash))
        
        # Call contract function with hex strings (avoid HexBytes issues)
        try:
            result = self.contract.functions.discoverAgents(capability_hashes).call()
            
            # Convert result to list of ints
            token_ids = []
            for token_id in result:
                if hasattr(token_id, 'hex'):
                    # HexBytes
                    token_ids.append(int.from_bytes(token_id, 'big'))
                elif isinstance(token_id, bytes):
                    # Raw bytes
                    token_ids.append(int.from_bytes(token_id, 'big'))
                else:
                    # Already int or can be converted
                    token_ids.append(int(token_id))
            
            return token_ids
        
        except Exception as e:
            # If all else fails, return empty list
            print(f"Warning: discover_agents error: {e}")
            return []
    
    def get_identity_info(self, token_id: int) -> Dict[str, Any]:
        """
        Get complete identity information for an agent
        
        Args:
            token_id: Agent token ID
        
        Returns:
            Dictionary with identity info
        """
        agent_card = self.get_agent_card(token_id)
        owner = self.get_owner(token_id)
        
        return {
            "token_id": token_id,
            "owner": owner,
            "name": agent_card.get("name"),
            "description": agent_card.get("description"),
            "capabilities": agent_card.get("capabilities"),
            "service_endpoints": agent_card.get("serviceEndpoints"),
            "payment_address": agent_card.get("paymentAddress"),
            "x402_accepted": agent_card.get("x402Accepted"),
            "metadata": agent_card.get("metadata")
        }
