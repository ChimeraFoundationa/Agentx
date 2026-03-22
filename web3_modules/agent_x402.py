"""
AgentX x402 Payment Protocol

Native x402 implementation for AgentX agents:
- Autonomous agent payments
- HTTP 402 Payment Required handling
- Facilitator integration for settlement
- Multi-chain support (Base, Ethereum, etc.)
"""

import base64
import json
import time
from typing import Dict, Any, Optional, List
from dataclasses import dataclass, asdict
from web3 import Web3
from eth_account.messages import encode_typed_data
import httpx


@dataclass
class PaymentRequirements:
    """x402 Payment Requirements"""
    price: str  # e.g., "$0.001"
    currency: str  # e.g., "USDC"
    network: str  # e.g., "eip155:8453" (Base)
    recipient: str  # Wallet address
    idempotency_key: str  # Unique key to prevent double-spend
    scheme: str = "exact"  # Payment scheme
    asset: Optional[str] = None  # Token address
    description: Optional[str] = None
    expires_at: Optional[int] = None  # Unix timestamp


@dataclass
class PaymentSignature:
    """Signed x402 Payment"""
    signature: str
    payload: Dict[str, Any]
    signer: str


@dataclass
class PaymentResponse:
    """x402 Payment Response"""
    settlement_id: str
    status: str  # "pending", "completed", "failed"
    transaction_hash: Optional[str] = None
    facilitator: Optional[str] = None
    timestamp: int = 0


class AgentX402:
    """
    x402 Payment Client for AgentX Agents
    
    Features:
    - Automatic payment signing
    - HTTP 402 handling
    - Facilitator integration
    - Spending limits
    - Payment history
    """
    
    # Default facilitators
    FACILITATORS = {
        "base": "https://facilitator.payai.network",
        "ethereum": "https://facilitator.coinbase.com",
        "testnet": "https://facilitator-testnet.payai.network"
    }
    
    # USDC addresses by network
    USDC_ADDRESSES = {
        "eip155:8453": "0x833589fCD6eDb6E08f4c7C32D4f71b54bdA02913",  # Base
        "eip155:84532": "0x036CbD53842c5426634e7929541eC2318f3dCF7e",  # Base Sepolia
        "eip155:1": "0xA0b86991c6218b36c1d19D4a2e9Eb0cE3606eB48",  # ETH Mainnet
        "eip155:11155111": "0x1c7D4B196Cb0C7B01d743Fbc6116a902379C7238",  # Sepolia
    }
    
    def __init__(
        self,
        agent_wallet: str,
        private_key: str,
        rpc_url: str,
        chain_id: int = 8453,  # Base mainnet
        facilitator_url: Optional[str] = None
    ):
        """
        Initialize Agent x402 Client
        
        Args:
            agent_wallet: Agent's wallet address
            private_key: Agent's private key
            rpc_url: RPC endpoint
            chain_id: Chain ID (default: Base)
            facilitator_url: Payment facilitator URL
        """
        self.w3 = Web3(Web3.HTTPProvider(rpc_url))
        self.account = self.w3.eth.account.from_key(private_key)
        self.agent_wallet = agent_wallet
        self.chain_id = chain_id
        self.facilitator_url = facilitator_url or self.FACILITATORS.get("base")
        
        self.http_client = httpx.AsyncClient(timeout=30.0)
        self.payment_history: List[PaymentResponse] = []
        
        # Spending limits
        self.spending_limit_usd = 10.0  # Daily limit
        self.spent_today_usd = 0.0
        self.last_reset = int(time.time())
    
    def _encode_base64(self, data: Dict[str, Any]) -> str:
        """Encode data to base64"""
        json_str = json.dumps(data)
        return base64.b64encode(json_str.encode('utf-8')).decode('utf-8')
    
    def _decode_base64(self, data: str) -> Dict[str, Any]:
        """Decode base64 data"""
        decoded = base64.b64decode(data).decode('utf-8')
        return json.loads(decoded)
    
    def _parse_price(self, price: str) -> int:
        """Parse price string to smallest unit (e.g., cents for USDC)"""
        # Remove $ sign
        if price.startswith('$'):
            price = price[1:]
        
        # Convert to cents (USDC has 6 decimals, but we use cents for simplicity)
        price_float = float(price)
        return int(price_float * 1e6)  # USDC decimals
    
    def _get_asset_address(self, asset: str, network: str) -> str:
        """Get token address for asset"""
        if asset.startswith('0x'):
            return asset  # Already an address
        
        # Look up known assets
        if asset.upper() == "USDC":
            return self.USDC_ADDRESSES.get(network, self.USDC_ADDRESSES["eip155:8453"])
        
        raise ValueError(f"Unknown asset: {asset}")
    
    def create_payment_payload(
        self,
        requirements: PaymentRequirements,
        resource_url: str
    ) -> Dict[str, Any]:
        """
        Create EIP-712 typed data for payment
        
        Args:
            requirements: Payment requirements from 402 response
            resource_url: URL of resource being purchased
        
        Returns:
            EIP-712 typed data
        """
        # Parse network from CAIP-2 format
        network_parts = requirements.network.split(':')
        chain_id = int(network_parts[1]) if len(network_parts) > 1 else self.chain_id
        
        payment_data = {
            "types": {
                "EIP712Domain": [
                    {"name": "name", "type": "string"},
                    {"name": "version", "type": "string"},
                    {"name": "chainId", "type": "uint256"},
                    {"name": "verifyingContract", "type": "address"},
                ],
                "Payment": [
                    {"name": "price", "type": "uint256"},
                    {"name": "asset", "type": "address"},
                    {"name": "recipient", "type": "address"},
                    {"name": "idempotencyKey", "type": "bytes32"},
                    {"name": "resource", "type": "string"},
                    {"name": "expiration", "type": "uint256"},
                ],
            },
            "primaryType": "Payment",
            "domain": {
                "name": "x402 Payment",
                "version": "1",
                "chainId": chain_id,
                "verifyingContract": requirements.recipient,
            },
            "message": {
                "price": self._parse_price(requirements.price),
                "asset": self._get_asset_address(
                    requirements.asset or "USDC",
                    requirements.network
                ),
                "recipient": Web3.to_checksum_address(requirements.recipient),
                "idempotencyKey": Web3.keccak(text=requirements.idempotency_key),
                "resource": resource_url,
                "expiration": requirements.expires_at or (int(time.time()) + 3600),
            },
        }
        
        return payment_data
    
    def sign_payment(self, payment_data: Dict[str, Any]) -> PaymentSignature:
        """
        Sign payment with agent's wallet
        
        Args:
            payment_data: EIP-712 typed data
        
        Returns:
            PaymentSignature object
        """
        # Sign typed data
        signed_message = self.account.sign_message(
            encode_typed_data(full_message=payment_data)
        )
        
        return PaymentSignature(
            signature=signed_message.signature.hex(),
            payload=payment_data,
            signer=self.agent_wallet
        )
    
    async def handle_402_response(
        self,
        response: httpx.Response,
        resource_url: str
    ) -> PaymentSignature:
        """
        Handle HTTP 402 Payment Required response
        
        Args:
            response: 402 response from server
            resource_url: URL of resource
        
        Returns:
            Signed payment
        """
        if response.status_code != 402:
            raise ValueError(f"Expected 402 status, got {response.status_code}")
        
        # Get payment requirements from header
        payment_required_header = response.headers.get("PAYMENT-REQUIRED")
        if not payment_required_header:
            raise ValueError("Missing PAYMENT-REQUIRED header")
        
        # Decode requirements
        requirements_data = self._decode_base64(payment_required_header)
        requirements = PaymentRequirements(**requirements_data)
        
        # Check spending limit
        if not self._check_spending_limit(requirements.price):
            raise ValueError("Payment exceeds spending limit")
        
        # Create and sign payment
        payment_data = self.create_payment_payload(requirements, resource_url)
        signature = self.sign_payment(payment_data)
        
        return signature
    
    def _check_spending_limit(self, price: str) -> bool:
        """Check if payment is within spending limit"""
        # Reset daily spending if needed
        current_time = int(time.time())
        if current_time - self.last_reset > 86400:  # 24 hours
            self.spent_today_usd = 0.0
            self.last_reset = current_time
        
        # Parse price
        price_usd = float(price.replace('$', ''))
        
        # Check limit
        return (self.spent_today_usd + price_usd) <= self.spending_limit_usd
    
    async def pay_for_resource(
        self,
        url: str,
        method: str = "GET",
        headers: Optional[Dict[str, str]] = None,
        json_data: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """
        Pay for and access a protected resource
        
        Args:
            url: Resource URL
            method: HTTP method
            headers: Optional headers
            json_data: Optional JSON body
        
        Returns:
            Resource data
        """
        # First attempt without payment
        response = await self.http_client.request(
            method=method,
            url=url,
            headers=headers or {},
            json=json_data
        )
        
        # Check if payment required
        if response.status_code == 402:
            # Handle 402 and get signed payment
            signature = await self.handle_402_response(response, url)
            
            # Retry with payment signature
            retry_headers = headers.copy() if headers else {}
            retry_headers["PAYMENT-SIGNATURE"] = signature.signature
            
            response = await self.http_client.request(
                method=method,
                url=url,
                headers=retry_headers,
                json=json_data
            )
            
            # Verify payment response
            if response.status_code != 200:
                raise ValueError(f"Payment failed: {response.status_code}")
            
            # Update spending
            payment_header = response.headers.get("PAYMENT-RESPONSE")
            if payment_header:
                payment_response = self._decode_base64(payment_header)
                price = payment_response.get("price", "$0.001")
                self.spent_today_usd += float(price.replace('$', ''))
        
        # Parse and return response
        return response.json()
    
    async def submit_to_facilitator(
        self,
        signature: PaymentSignature
    ) -> PaymentResponse:
        """
        Submit payment to facilitator for settlement
        
        Args:
            signature: Signed payment
        
        Returns:
            Payment response
        """
        try:
            response = await self.http_client.post(
                f"{self.facilitator_url}/settle",
                json={
                    "signature": signature.signature,
                    "payment": signature.payload,
                    "signer": signature.signer
                }
            )
            
            if response.status_code == 200:
                result = response.json()
                
                payment_response = PaymentResponse(
                    settlement_id=result.get("settlementId"),
                    status="completed",
                    transaction_hash=result.get("transactionHash"),
                    facilitator=self.facilitator_url,
                    timestamp=int(time.time())
                )
                
                self.payment_history.append(payment_response)
                
                return payment_response
            else:
                raise ValueError(f"Facilitator error: {response.status_code}")
        
        except Exception as e:
            payment_response = PaymentResponse(
                settlement_id="",
                status="failed",
                timestamp=int(time.time())
            )
            self.payment_history.append(payment_response)
            
            raise e
    
    def get_spending_summary(self) -> Dict[str, Any]:
        """Get spending summary"""
        return {
            "spent_today_usd": round(self.spent_today_usd, 2),
            "daily_limit_usd": self.spending_limit_usd,
            "remaining_usd": round(self.spending_limit_usd - self.spent_today_usd, 2),
            "total_payments": len(self.payment_history),
            "completed_payments": sum(1 for p in self.payment_history if p.status == "completed"),
            "failed_payments": sum(1 for p in self.payment_history if p.status == "failed")
        }
    
    def set_spending_limit(self, limit_usd: float):
        """Set daily spending limit"""
        self.spending_limit_usd = limit_usd
    
    async def close(self):
        """Close HTTP client"""
        await self.http_client.aclose()


# Convenience class for AgentX integration
class AgentX402Integration:
    """
    x402 Integration for AgentX Agents
    
    Simplified interface for agents to make payments
    """
    
    def __init__(self, agent_config: Dict[str, Any]):
        """
        Initialize from agent config
        
        Args:
            agent_config: Agent configuration dictionary
        """
        self.x402 = AgentX402(
            agent_wallet=agent_config["wallet_address"],
            private_key=agent_config["private_key"],
            rpc_url=agent_config.get("rpc_url", "http://localhost:8545"),
            chain_id=agent_config.get("chain_id", 8453),
            facilitator_url=agent_config.get("facilitator_url")
        )
        
        # Set spending limit from config
        if "spending_limit_usd" in agent_config:
            self.x402.set_spending_limit(agent_config["spending_limit_usd"])
    
    async def pay_for_agent_service(
        self,
        service_endpoint: str,
        service_name: str,
        input_data: Dict[str, Any],
        expected_price: str = "$0.01"
    ) -> Dict[str, Any]:
        """
        Pay for an agent service via x402
        
        Args:
            service_endpoint: Agent's service URL
            service_name: Name of service
            input_data: Service input data
            expected_price: Expected price
        
        Returns:
            Service result
        """
        result = await self.x402.pay_for_resource(
            url=service_endpoint,
            method="POST",
            json={
                "service": service_name,
                "input": input_data
            }
        )
        
        return result
    
    async def pay_for_mcp_tool(
        self,
        tool_url: str,
        tool_name: str,
        tool_args: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        Pay for MCP tool execution
        
        Args:
            tool_url: MCP tool endpoint
            tool_name: Tool name
            tool_args: Tool arguments
        
        Returns:
            Tool result
        """
        result = await self.x402.pay_for_resource(
            url=tool_url,
            method="POST",
            json={
                "tool": tool_name,
                "arguments": tool_args
            }
        )
        
        return result
    
    def get_summary(self) -> Dict[str, Any]:
        """Get payment summary"""
        return self.x402.get_spending_summary()


# Example usage
async def example_usage():
    """Example of using Agent x402"""
    # Configuration
    agent_config = {
        "wallet_address": "0xYourAgentWallet",
        "private_key": "0xYourPrivateKey",
        "rpc_url": "http://localhost:8545",
        "chain_id": 8453,  # Base
        "spending_limit_usd": 10.0
    }
    
    # Initialize
    integration = AgentX402Integration(agent_config)
    
    # Pay for agent service
    result = await integration.pay_for_agent_service(
        service_endpoint="http://agent-service.local/api/analyze",
        service_name="defi_analysis",
        input_data={"wallet": "0x123..."},
        expected_price="$0.01"
    )
    
    print(f"Service result: {result}")
    
    # Pay for MCP tool
    tool_result = await integration.pay_for_mcp_tool(
        tool_url="http://mcp-server.local/tools/swap",
        tool_name="execute_swap",
        tool_args={"token_in": "USDC", "token_out": "ETH", "amount": "100"}
    )
    
    print(f"Tool result: {tool_result}")
    
    # Get spending summary
    summary = integration.get_summary()
    print(f"Spending: ${summary['spent_today_usd']}/${summary['daily_limit_usd']}")


if __name__ == "__main__":
    import asyncio
    asyncio.run(example_usage())
