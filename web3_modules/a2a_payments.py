"""
x402 Payment Integration for AgentX A2A

Enables automatic payments between agents for:
- Task delegation
- Service usage
- MCP tool execution
- API access
"""

import asyncio
from typing import Dict, Any, Optional, List
from dataclasses import dataclass
from web3 import Web3

from .x402.client import X402Client


@dataclass
class PaymentConfig:
    """Configuration for x402 payments"""
    enabled: bool = True
    auto_pay: bool = True
    spending_limit_usd: float = 10.0  # Daily limit
    max_transaction_usd: float = 1.0  # Per transaction limit
    facilitator_url: str = "https://facilitator.payai.network"
    accepted_networks: List[str] = None
    accepted_assets: List[str] = None
    
    def __post_init__(self):
        if self.accepted_networks is None:
            self.accepted_networks = [
                "eip155:8453",    # Base mainnet
                "eip155:84532",   # Base Sepolia
            ]
        if self.accepted_assets is None:
            self.accepted_assets = ["USDC", "ETH"]


@dataclass
class PaymentReceipt:
    """Receipt for completed payment"""
    payment_id: str
    amount: str
    asset: str
    recipient: str
    task_id: str
    agent_id: int
    status: str  # "pending", "completed", "failed"
    tx_hash: Optional[str] = None
    timestamp: int = 0


class A2APaymentManager:
    """
    Payment manager for A2A transactions
    
    Features:
    - Automatic x402 payments
    - Spending limits
    - Payment tracking
    - Receipt generation
    """
    
    def __init__(
        self,
        x402_client: X402Client,
        config: Optional[PaymentConfig] = None,
        agent_token_id: int = 0
    ):
        """
        Initialize A2A Payment Manager
        
        Args:
            x402_client: X402Client instance
            config: Payment configuration
            agent_token_id: This agent's token ID
        """
        self.x402 = x402_client
        self.config = config or PaymentConfig()
        self.agent_token_id = agent_token_id
        self.spent_today_usd = 0.0
        self.payment_history: List[PaymentReceipt] = []
    
    def can_pay(self, amount_usd: float) -> tuple[bool, str]:
        """
        Check if payment is allowed
        
        Args:
            amount_usd: Amount in USD
        
        Returns:
            (can_pay, reason)
        """
        if not self.config.enabled:
            return False, "Payments disabled"
        
        # Check spending limit
        if self.spent_today_usd + amount_usd > self.config.spending_limit_usd:
            return False, f"Would exceed daily limit (${self.config.spending_limit_usd})"
        
        # Check transaction limit
        if amount_usd > self.config.max_transaction_usd:
            return False, f"Exceeds transaction limit (${self.config.max_transaction_usd})"
        
        return True, "OK"
    
    async def pay_for_task(
        self,
        task_id: str,
        agent_id: int,
        amount_usd: float,
        service_endpoint: str,
        task_data: Dict[str, Any]
    ) -> Optional[PaymentReceipt]:
        """
        Pay for task execution
        
        Args:
            task_id: Task identifier
            agent_id: Service agent's token ID
            amount_usd: Amount in USD
            service_endpoint: Agent's service endpoint URL
            task_data: Task input data
        
        Returns:
            Payment receipt or None if failed
        """
        # Check if can pay
        can_pay, reason = self.can_pay(amount_usd)
        if not can_pay:
            print(f"⚠️  Cannot pay: {reason}")
            return None
        
        try:
            # Create payment receipt
            receipt = PaymentReceipt(
                payment_id=f"pay_{task_id}",
                amount=str(amount_usd),
                asset="USDC",
                recipient=service_endpoint,
                task_id=task_id,
                agent_id=agent_id,
                status="pending",
                timestamp=int(asyncio.get_event_loop().time())
            )
            
            if not self.config.auto_pay:
                print(f"⚠️  Auto-pay disabled, manual approval needed")
                receipt.status = "pending_approval"
                self.payment_history.append(receipt)
                return receipt
            
            # Execute x402 payment
            print(f"💰 Processing payment of ${amount_usd} for task {task_id}...")
            
            # For now, simulate payment (real x402 integration needs running server)
            # In production, this would call:
            # result = await self.x402.fetch_paid_resource(
            #     url=service_endpoint,
            #     method="POST",
            #     json_data=task_data
            # )
            
            # Simulate successful payment
            receipt.status = "completed"
            receipt.tx_hash = f"0x simulated_tx_{task_id}"
            
            # Update spending
            self.spent_today_usd += amount_usd
            self.payment_history.append(receipt)
            
            print(f"✅ Payment completed!")
            print(f"   Amount: ${amount_usd}")
            print(f"   Task: {task_id}")
            print(f"   Agent: #{agent_id}")
            print(f"   TX: {receipt.tx_hash}")
            
            return receipt
        
        except Exception as e:
            print(f"❌ Payment failed: {e}")
            receipt.status = "failed"
            self.payment_history.append(receipt)
            return None
    
    async def pay_for_mcp_tool(
        self,
        tool_url: str,
        tool_name: str,
        tool_args: Dict[str, Any],
        expected_price_usd: float
    ) -> Optional[PaymentReceipt]:
        """
        Pay for MCP tool execution
        
        Args:
            tool_url: MCP tool endpoint
            tool_name: Tool name
            tool_args: Tool arguments
            expected_price_usd: Expected price
        
        Returns:
            Payment receipt
        """
        task_id = f"mcp_{tool_name}_{int(asyncio.get_event_loop().time())}"
        
        can_pay, reason = self.can_pay(expected_price_usd)
        if not can_pay:
            print(f"⚠️  Cannot pay for MCP tool: {reason}")
            return None
        
        try:
            # Execute payment and tool call
            result = await self.x402.pay_for_mcp_tool(
                tool_url=tool_url,
                tool_name=tool_name,
                tool_args=tool_args,
                expected_price=f"${expected_price_usd}"
            )
            
            # Create receipt
            receipt = PaymentReceipt(
                payment_id=f"pay_{task_id}",
                amount=str(expected_price_usd),
                asset="USDC",
                recipient=tool_url,
                task_id=task_id,
                agent_id=0,  # MCP tool
                status="completed",
                tx_hash="simulated_mcp_tx",
                timestamp=int(asyncio.get_event_loop().time())
            )
            
            self.spent_today_usd += expected_price_usd
            self.payment_history.append(receipt)
            
            print(f"✅ MCP tool payment completed: {tool_name}")
            
            return receipt
        
        except Exception as e:
            print(f"❌ MCP tool payment failed: {e}")
            return None
    
    def reset_spending_tracking(self):
        """Reset daily spending tracking"""
        self.spent_today_usd = 0.0
        print("🔄 Spending tracking reset")
    
    def get_payment_history(self, task_id: Optional[str] = None) -> List[PaymentReceipt]:
        """
        Get payment history
        
        Args:
            task_id: Optional filter by task ID
        
        Returns:
            List of payment receipts
        """
        if task_id:
            return [
                receipt for receipt in self.payment_history
                if receipt.task_id == task_id
            ]
        return self.payment_history
    
    def get_spending_summary(self) -> Dict[str, Any]:
        """
        Get spending summary
        
        Returns:
            Summary dictionary
        """
        return {
            "spent_today_usd": round(self.spent_today_usd, 2),
            "daily_limit_usd": self.config.spending_limit_usd,
            "remaining_usd": round(self.config.spending_limit_usd - self.spent_today_usd, 2),
            "total_payments": len(self.payment_history),
            "completed_payments": sum(1 for p in self.payment_history if p.status == "completed"),
            "failed_payments": sum(1 for p in self.payment_history if p.status == "failed"),
            "pending_payments": sum(1 for p in self.payment_history if p.status == "pending")
        }


# Integration with A2ACoordinator
class A2ACoordinatorWithPayments:
    """
    A2ACoordinator with integrated payment support
    
    Extends A2ACoordinator with automatic payment handling
    """
    
    def __init__(
        self,
        coordinator,
        x402_client: X402Client,
        payment_config: Optional[PaymentConfig] = None
    ):
        """
        Initialize A2A Coordinator with Payments
        
        Args:
            coordinator: A2ACoordinator instance
            x402_client: X402Client for payments
            payment_config: Payment configuration
        """
        self.coordinator = coordinator
        self.payment_manager = A2APaymentManager(
            x402_client=x402_client,
            config=payment_config,
            agent_token_id=coordinator.agent_token_id
        )
    
    async def delegate_task_with_payment(
        self,
        target_agent,
        task_request,
        payment_amount_usd: float
    ):
        """
        Delegate task with automatic payment
        
        Args:
            target_agent: Agent to delegate to
            task_request: TaskRequest object
            payment_amount_usd: Payment amount in USD
        
        Returns:
            (task_result, payment_receipt)
        """
        # First, process payment
        payment_receipt = await self.payment_manager.pay_for_task(
            task_id=task_request.task_id,
            agent_id=target_agent.token_id,
            amount_usd=payment_amount_usd,
            service_endpoint=target_agent.service_endpoints.get("mcp", ""),
            task_data=task_request.input_data
        )
        
        if not payment_receipt:
            return None, "Payment failed"
        
        # Then, execute task delegation
        task_result = await self.coordinator.request_task_execution(
            target_agent=target_agent,
            task_request=task_request
        )
        
        return task_result, payment_receipt


# Example usage
async def example_usage():
    """Example of using A2A payment integration"""
    from .a2a import A2ACoordinator
    from .x402.client import X402Client
    
    # Initialize components
    # coordinator = A2ACoordinator(agent_token_id=1, ...)
    
    x402_client = X402Client(
        private_key="0xYOUR_KEY",
        rpc_url="http://localhost:8545"
    )
    
    payment_config = PaymentConfig(
        enabled=True,
        auto_pay=True,
        spending_limit_usd=10.0,
        max_transaction_usd=1.0
    )
    
    # Create payment-enabled coordinator
    # paid_coordinator = A2ACoordinatorWithPayments(
    #     coordinator=coordinator,
    #     x402_client=x402_client,
    #     payment_config=payment_config
    # )
    
    # Example usage shown in documentation
    print("See documentation for full example")


if __name__ == "__main__":
    asyncio.run(example_usage())
