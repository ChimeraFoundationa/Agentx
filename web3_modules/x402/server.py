"""
x402 Payment Protocol Server

Accept payments for your AgentX services:
- Define payment requirements for endpoints
- Verify payment signatures
- Settle payments via facilitator
"""

import base64
import json
from typing import Dict, Any, Optional, List, Callable
from dataclasses import dataclass, asdict
from web3 import Web3
from eth_account.messages import encode_typed_data
import httpx


@dataclass
class PaymentOption:
    """Payment option for an endpoint"""
    scheme: str
    price: str
    network: str
    payTo: str
    asset: Optional[str] = None
    description: Optional[str] = None


@dataclass
class PaymentConfig:
    """Payment configuration for an endpoint"""
    accepts: List[PaymentOption]
    description: str
    mimeType: str = "application/json"


class X402Server:
    """
    x402 payment server for AgentX
    
    Enables agent to accept payments for services
    via the x402 protocol (HTTP 402 Payment Required)
    """
    
    # Default facilitators
    DEFAULT_FACILITATORS = [
        "https://facilitator.payai.network",
        "https://x402.org/facilitator",
    ]
    
    def __init__(
        self,
        wallet_address: str,
        rpc_url: Optional[str] = None,
        private_key: Optional[str] = None,
        facilitator_url: Optional[str] = None
    ):
        """
        Initialize x402 server
        
        Args:
            wallet_address: Wallet address for receiving payments
            rpc_url: Optional RPC URL for on-chain verification
            private_key: Optional private key for direct settlement
            facilitator_url: Facilitator URL for payment verification
        """
        self.wallet_address = wallet_address
        self.facilitator_url = facilitator_url or self.DEFAULT_FACILITATORS[0]
        
        if rpc_url:
            self.w3 = Web3(Web3.HTTPProvider(rpc_url))
            if private_key:
                self.account = self.w3.eth.account.from_key(private_key)
            else:
                self.account = None
        else:
            self.w3 = None
            self.account = None
        
        # Payment configurations for endpoints
        self.payment_configs: Dict[str, PaymentConfig] = {}
        
        # HTTP client for facilitator
        self.http = httpx.AsyncClient(timeout=30.0)
    
    def _encode_base64(self, data: Dict[str, Any]) -> str:
        """Encode data to base64"""
        json_str = json.dumps(data)
        return base64.b64encode(json_str.encode('utf-8')).decode('utf-8')
    
    def register_endpoint(
        self,
        method: str,
        path: str,
        price: str,
        description: str,
        network: str = "eip155:8453",
        asset: str = "USDC",
        mime_type: str = "application/json"
    ):
        """
        Register an endpoint with payment requirements
        
        Args:
            method: HTTP method (GET, POST, etc.)
            path: Endpoint path
            price: Price (e.g., "$0.01")
            description: Endpoint description
            network: Network in CAIP-2 format
            asset: Asset symbol (USDC, ETH, etc.)
            mime_type: Response MIME type
        """
        key = f"{method} {path}"
        
        payment_option = PaymentOption(
            scheme="exact",
            price=price,
            network=network,
            payTo=self.wallet_address,
            asset=asset,
            description=description
        )
        
        payment_config = PaymentConfig(
            accepts=[payment_option],
            description=description,
            mimeType=mime_type
        )
        
        self.payment_configs[key] = payment_config
    
    def get_payment_header(self, endpoint_key: str) -> str:
        """
        Get PAYMENT-REQUIRED header value for an endpoint
        
        Args:
            endpoint_key: Endpoint key (e.g., "GET /api/analyze")
        
        Returns:
            Base64-encoded payment requirements
        """
        if endpoint_key not in self.payment_configs:
            raise ValueError(f"No payment config for endpoint: {endpoint_key}")
        
        config = self.payment_configs[endpoint_key]
        
        # Convert to dict for encoding
        requirements = {
            "accepts": [asdict(opt) for opt in config.accepts],
            "description": config.description,
            "mimeType": config.mimeType
        }
        
        return self._encode_base64(requirements)
    
    def create_402_response(self, endpoint_key: str) -> Dict[str, Any]:
        """
        Create 402 Payment Required response
        
        Args:
            endpoint_key: Endpoint key
        
        Returns:
            Response dictionary with status and headers
        """
        return {
            "status": 402,
            "headers": {
                "PAYMENT-REQUIRED": self.get_payment_header(endpoint_key)
            },
            "body": {
                "error": "Payment Required",
                "message": "This endpoint requires payment via x402 protocol"
            }
        }
    
    async def verify_payment_signature(
        self,
        signature: str,
        payment_data: Dict[str, Any]
    ) -> bool:
        """
        Verify payment signature via facilitator
        
        Args:
            signature: Payment signature
            payment_data: Original payment data
        
        Returns:
            True if signature is valid
        """
        try:
            # Send to facilitator for verification
            response = await self.http.post(
                f"{self.facilitator_url}/verify",
                json={
                    "signature": signature,
                    "payment": payment_data
                }
            )
            
            if response.status_code == 200:
                result = response.json()
                return result.get("valid", False)
            
            return False
        
        except Exception as e:
            print(f"Payment verification error: {e}")
            return False
    
    async def settle_payment(
        self,
        signature: str,
        payment_data: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        Settle payment via facilitator
        
        Args:
            signature: Payment signature
            payment_data: Original payment data
        
        Returns:
            Settlement result
        """
        try:
            response = await self.http.post(
                f"{self.facilitator_url}/settle",
                json={
                    "signature": signature,
                    "payment": payment_data,
                    "recipient": self.wallet_address
                }
            )
            
            if response.status_code == 200:
                return response.json()
            else:
                raise ValueError(f"Settlement failed: {response.status_code}")
        
        except Exception as e:
            raise ValueError(f"Payment settlement error: {e}")
    
    async def verify_and_settle(
        self,
        signature: str,
        endpoint_key: str,
        resource_url: str
    ) -> Dict[str, Any]:
        """
        Verify and settle payment for a request
        
        Args:
            signature: Payment signature from client
            endpoint_key: Endpoint key
            resource_url: Resource URL
        
        Returns:
            Payment response
        """
        if endpoint_key not in self.payment_configs:
            raise ValueError(f"No payment config for endpoint: {endpoint_key}")
        
        config = self.payment_configs[endpoint_key]
        option = config.accepts[0]  # Use first payment option
        
        # Reconstruct payment data for verification
        payment_data = {
            "price": option.price,
            "asset": option.asset,
            "recipient": option.payTo,
            "resource": resource_url,
            "network": option.network
        }
        
        # Verify signature
        is_valid = await self.verify_payment_signature(signature, payment_data)
        
        if not is_valid:
            return {"valid": False, "error": "Invalid payment signature"}
        
        # Settle payment
        settlement = await self.settle_payment(signature, payment_data)
        
        return {
            "valid": True,
            "settlement_id": settlement.get("settlementId"),
            "transaction_hash": settlement.get("transactionHash"),
            "status": "settled"
        }
    
    def create_payment_response_header(self, payment_result: Dict[str, Any]) -> str:
        """
        Create PAYMENT-RESPONSE header value
        
        Args:
            payment_result: Payment verification/settlement result
        
        Returns:
            Base64-encoded payment response
        """
        return self._encode_base64(payment_result)
    
    async def protect_endpoint(
        self,
        endpoint_key: str,
        request_headers: Dict[str, str],
        resource_url: str,
        execute_handler: Callable
    ) -> Dict[str, Any]:
        """
        Protect an endpoint with x402 payment
        
        Args:
            endpoint_key: Endpoint key
            request_headers: Request headers
            resource_url: Resource URL
            execute_handler: Handler function to execute if payment valid
        
        Returns:
            Response dictionary
        """
        # Check for payment signature
        signature = request_headers.get("PAYMENT-SIGNATURE") or request_headers.get("X-PAYMENT")
        
        if not signature:
            # No payment provided - return 402
            return self.create_402_response(endpoint_key)
        
        # Verify and settle payment
        payment_result = await self.verify_and_settle(
            signature,
            endpoint_key,
            resource_url
        )
        
        if not payment_result.get("valid"):
            return {
                "status": 403,
                "body": {
                    "error": "Payment Failed",
                    "message": payment_result.get("error", "Invalid payment")
                }
            }
        
        # Payment valid - execute handler
        try:
            result = await execute_handler()
            
            # Add payment response header
            payment_response = self.create_payment_response_header(payment_result)
            
            return {
                "status": 200,
                "headers": {
                    "PAYMENT-RESPONSE": payment_response
                },
                "body": result
            }
        
        except Exception as e:
            return {
                "status": 500,
                "body": {
                    "error": "Internal Error",
                    "message": str(e)
                }
            }
    
    async def close(self):
        """Close HTTP client"""
        await self.http.aclose()


# Example usage with FastAPI
"""
from fastapi import FastAPI, Header, HTTPException

app = FastAPI()
x402_server = X402Server(wallet_address="0xYourAddress")

# Register endpoint
x402_server.register_endpoint(
    method="GET",
    path="/api/analyze-wallet",
    price="$0.01",
    description="Analyze wallet holdings and transactions"
)

@app.get("/api/analyze-wallet")
async def analyze_wallet(
    address: str,
    payment_signature: Optional[str] = Header(default=None)
):
    endpoint_key = "GET /api/analyze-wallet"
    
    async def handler():
        # Your actual endpoint logic here
        return {"analysis": "wallet data..."}
    
    result = await x402_server.protect_endpoint(
        endpoint_key=endpoint_key,
        request_headers={"PAYMENT-SIGNATURE": payment_signature} if payment_signature else {},
        resource_url="/api/analyze-wallet",
        execute_handler=handler
    )
    
    if result["status"] == 402:
        raise HTTPException(
            status_code=402,
            detail=result["body"],
            headers={"PAYMENT-REQUIRED": result["headers"]["PAYMENT-REQUIRED"]}
        )
    elif result["status"] == 403:
        raise HTTPException(status_code=403, detail=result["body"])
    elif result["status"] == 500:
        raise HTTPException(status_code=500, detail=result["body"])
    
    return result["body"]
"""
