"""
x402 Payment Protocol Client

HTTP-native payment protocol for micropayments:
- Automatic payments for APIs & services
- Parse 402 Payment Required responses
- Sign and submit payments
"""

import base64
import json
from typing import Dict, Any, Optional, List
from dataclasses import dataclass
import httpx
from web3 import Web3
from eth_account.messages import encode_typed_data


@dataclass
class PaymentRequirements:
    """Parsed payment requirements from 402 response"""
    price: str
    currency: str
    network: str
    recipient: str
    idempotency_key: str
    scheme: str = "exact"
    asset: Optional[str] = None
    description: Optional[str] = None


@dataclass
class PaymentResponse:
    """Payment response from server"""
    settlement_id: str
    status: str
    transaction_hash: Optional[str] = None
    facilitator: Optional[str] = None


class X402Client:
    """
    x402 payment client for AgentX
    
    Enables agent to automatically pay for APIs and services
    via the x402 protocol (HTTP 402 Payment Required)
    """
    
    # Default facilitators for payment settlement
    DEFAULT_FACILITATORS = [
        "https://facilitator.payai.network",
        "https://x402.org/facilitator",
    ]
    
    # Supported networks (CAIP-2 format)
    SUPPORTED_NETWORKS = {
        "eip155:8453": "Base Mainnet",
        "eip155:84532": "Base Sepolia",
        "eip155:1": "Ethereum Mainnet",
        "eip155:11155111": "Ethereum Sepolia",
        "eip155:42161": "Arbitrum One",
    }
    
    def __init__(
        self,
        private_key: str,
        rpc_url: str,
        chain_id: int = 8453,  # Base mainnet default
        facilitator_url: Optional[str] = None
    ):
        """
        Initialize x402 client
        
        Args:
            private_key: Wallet private key for signing payments
            rpc_url: Ethereum RPC endpoint
            chain_id: Chain ID for payments
            facilitator_url: Optional facilitator URL
        """
        self.w3 = Web3(Web3.HTTPProvider(rpc_url))
        self.account = self.w3.eth.account.from_key(private_key)
        self.address = self.account.address
        self.chain_id = chain_id
        self.facilitator_url = facilitator_url or self.DEFAULT_FACILITATORS[0]
        
        # HTTP client
        self.http = httpx.AsyncClient(timeout=30.0)
    
    def _decode_base64(self, data: str) -> Dict[str, Any]:
        """Decode base64-encoded payment data"""
        try:
            decoded = base64.b64decode(data).decode('utf-8')
            return json.loads(decoded)
        except Exception as e:
            raise ValueError(f"Failed to decode payment data: {e}")
    
    def _encode_base64(self, data: Dict[str, Any]) -> str:
        """Encode data to base64"""
        json_str = json.dumps(data)
        return base64.b64encode(json_str.encode('utf-8')).decode('utf-8')
    
    def parse_payment_requirements(self, headers: Dict[str, str]) -> PaymentRequirements:
        """
        Parse payment requirements from 402 response headers
        
        Args:
            headers: HTTP response headers
        
        Returns:
            PaymentRequirements object
        """
        payment_required_header = headers.get("PAYMENT-REQUIRED") or headers.get("X-PAYMENT-REQUIRED")
        
        if not payment_required_header:
            raise ValueError("No PAYMENT-REQUIRED header found")
        
        # Decode requirements
        requirements_data = self._decode_base64(payment_required_header)
        
        return PaymentRequirements(
            price=requirements_data.get("price", "0.001"),
            currency=requirements_data.get("currency", "USDC"),
            network=requirements_data.get("network", "eip155:8453"),
            recipient=requirements_data.get("payTo"),
            idempotency_key=requirements_data.get("idempotencyKey"),
            scheme=requirements_data.get("scheme", "exact"),
            asset=requirements_data.get("asset"),
            description=requirements_data.get("description")
        )
    
    def create_payment_payload(
        self,
        requirements: PaymentRequirements,
        resource_url: str
    ) -> Dict[str, Any]:
        """
        Create payment payload for signing
        
        Args:
            requirements: Payment requirements
            resource_url: URL of resource being purchased
        
        Returns:
            Payment payload dictionary
        """
        # EIP-712 typed data for payment
        payment_data = {
            "types": {
                "EIP712Domain": [
                    {"name": "name", "type": "string"},
                    {"name": "version", "type": "string"},
                    {"name": "chainId", "type": "uint256"},
                ],
                "Payment": [
                    {"name": "price", "type": "uint256"},
                    {"name": "asset", "type": "address"},
                    {"name": "recipient", "type": "address"},
                    {"name": "idempotencyKey", "type": "bytes32"},
                    {"name": "resource", "type": "string"},
                ],
            },
            "primaryType": "Payment",
            "domain": {
                "name": "x402 Payment",
                "version": "1",
                "chainId": self.chain_id,
            },
            "message": {
                "price": self._parse_price(requirements.price),
                "asset": self._get_asset_address(requirements.asset, requirements.network),
                "recipient": requirements.recipient,
                "idempotencyKey": Web3.keccak(text=requirements.idempotency_key),
                "resource": resource_url,
            },
        }
        
        return payment_data
    
    def _parse_price(self, price: str) -> int:
        """Parse price string to wei/smallest unit"""
        # Remove $ sign and parse
        if price.startswith("$"):
            price = price[1:]
        
        # Convert to smallest unit (e.g., USDC has 6 decimals)
        price_float = float(price)
        return int(price_float * 1e6)  # USDC decimals
    
    def _get_asset_address(self, asset: Optional[str], network: str) -> str:
        """Get token address for given asset and network"""
        # USDC addresses by network
        usdc_addresses = {
            "eip155:8453": "0x833589fCD6eDb6E08f4c7C32D4f71b54bdA02913",  # Base
            "eip155:84532": "0x036CbD53842c5426634e7929541eC2318f3dCF7e",  # Base Sepolia
            "eip155:1": "0xA0b86991c6218b36c1d19D4a2e9Eb0cE3606eB48",  # ETH Mainnet
        }
        
        if not asset or asset == "USDC":
            return usdc_addresses.get(network, usdc_addresses["eip155:8453"])
        
        return asset  # Assume it's already an address
    
    def sign_payment(self, payment_data: Dict[str, Any]) -> str:
        """
        Sign payment payload with wallet
        
        Args:
            payment_data: EIP-712 typed data
        
        Returns:
            Signature string
        """
        # Sign typed data
        signed_message = self.account.sign_message(
            encode_typed_data(
                full_message=payment_data
            )
        )
        
        return signed_message.signature.hex()
    
    async def fetch_paid_resource(
        self,
        url: str,
        method: str = "GET",
        headers: Optional[Dict[str, str]] = None,
        json_data: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """
        Fetch resource with automatic x402 payment
        
        Args:
            url: Resource URL
            method: HTTP method
            headers: Optional headers
            json_data: Optional JSON body
        
        Returns:
            Resource data
        """
        # First attempt without payment
        response = await self.http.request(
            method=method,
            url=url,
            headers=headers,
            json=json_data
        )
        
        # Check if payment required
        if response.status_code == 402:
            # Parse payment requirements
            requirements = self.parse_payment_requirements(dict(response.headers))
            
            # Create payment payload
            payment_data = self.create_payment_payload(requirements, url)
            
            # Sign payment
            signature = self.sign_payment(payment_data)
            
            # Retry with payment signature
            retry_headers = headers.copy() if headers else {}
            retry_headers["PAYMENT-SIGNATURE"] = signature
            
            response = await self.http.request(
                method=method,
                url=url,
                headers=retry_headers,
                json=json_data
            )
            
            # Verify payment response
            if response.status_code != 200:
                raise ValueError(f"Payment failed: {response.status_code}")
        
        # Parse and return response
        return response.json()
    
    async def pay_for_mcp_tool(
        self,
        tool_url: str,
        tool_name: str,
        tool_args: Dict[str, Any],
        expected_price: str = "$0.005"
    ) -> Dict[str, Any]:
        """
        Pay for MCP tool execution via x402
        
        Args:
            tool_url: MCP tool endpoint URL
            tool_name: Name of tool
            tool_args: Tool arguments
            expected_price: Expected price
        
        Returns:
            Tool execution result
        """
        result = await self.fetch_paid_resource(
            url=tool_url,
            method="POST",
            json={
                "tool": tool_name,
                "arguments": tool_args
            }
        )
        
        return result
    
    def get_balance(self, token_address: Optional[str] = None) -> float:
        """
        Get wallet balance (ETH or token)
        
        Args:
            token_address: Optional token contract address
        
        Returns:
            Balance
        """
        if not token_address:
            # ETH balance
            balance_wei = self.w3.eth.get_balance(self.address)
            return self.w3.from_wei(balance_wei, 'ether')
        else:
            # ERC-20 token balance
            # Simplified - in production, use proper ERC-20 ABI
            return 0.0
    
    async def close(self):
        """Close HTTP client"""
        await self.http.aclose()
