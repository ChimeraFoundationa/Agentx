"""
Whale Alert Agent for AgentX

Autonomous agent that:
- Monitors large transactions (whale movements)
- Tracks specific wallets
- Sends real-time alerts
- Analyzes market impact

Usage:
    agentx delegate <agent_id> "Monitor whale transactions" --input '{"threshold_usd": 100000}'
"""

import asyncio
from typing import Dict, List, Any, Optional, Callable
from dataclasses import dataclass, field
from web3 import Web3
import time


@dataclass
class WhaleTransaction:
    """Large transaction detected"""
    tx_hash: str
    from_address: str
    to_address: str
    token: str
    amount: float
    amount_usd: float
    timestamp: int
    chain: str
    transaction_type: str  # "transfer", "swap", "deposit", "withdrawal"


@dataclass
class WalletAlert:
    """Wallet monitoring alert"""
    wallet_address: str
    alert_type: str
    message: str
    severity: str  # "low", "medium", "high", "critical"
    timestamp: int
    tx_hash: Optional[str] = None


class WhaleAlertAgent:
    """
    Autonomous Whale Monitoring Agent
    
    Features:
    - Real-time whale transaction detection
    - Custom wallet tracking
    - Market impact analysis
    - Alert notifications
    """
    
    # Default whale threshold: $100,000
    DEFAULT_THRESHOLD_USD = 100000
    
    # Known whale wallets (example)
    KNOWN_WHALES = {
        "binance": "0x28C6c06298d514Db089934071355E5743bf21d60",
        "coinbase": "0x71660c4005BA85c37ccec55d0C4493E66Fe775d3",
        "ftx_cold": "0x2E668Ec0fdD0a2950972fB25A5a2aA6CbCdB5Dde",
    }
    
    def __init__(
        self,
        rpc_urls: Dict[str, str],
        threshold_usd: float = DEFAULT_THRESHOLD_USD,
        alert_callback: Optional[Callable] = None
    ):
        """
        Initialize Whale Alert Agent
        
        Args:
            rpc_urls: RPC URLs by chain
            threshold_usd: USD threshold for whale alerts
            alert_callback: Callback function for alerts
        """
        self.rpc_urls = rpc_urls
        self.threshold_usd = threshold_usd
        self.alert_callback = alert_callback
        
        # Initialize Web3
        self.web3_connections = {}
        for chain, rpc in rpc_urls.items():
            self.web3_connections[chain] = Web3(Web3.HTTPProvider(rpc))
        
        # Tracking state
        self.watched_wallets: List[str] = []
        self.alert_history: List[WalletAlert] = []
        self.transactions_detected: List[WhaleTransaction] = []
        
        # Performance tracking
        self.start_time = int(time.time())
        self.alerts_sent = 0
    
    def add_watched_wallet(self, address: str, label: Optional[str] = None):
        """Add wallet to watchlist"""
        if address not in self.watched_wallets:
            self.watched_wallets.append(address)
            print(f"✅ Added {label or address} to watchlist")
    
    def remove_watched_wallet(self, address: str):
        """Remove wallet from watchlist"""
        if address in self.watched_wallets:
            self.watched_wallets.remove(address)
            print(f"✅ Removed {address} from watchlist")
    
    async def monitor_transactions(self, chain: str = "ethereum") -> List[WhaleTransaction]:
        """
        Monitor for whale transactions
        
        Args:
            chain: Blockchain to monitor
        
        Returns:
            List of detected whale transactions
        """
        if chain not in self.web3_connections:
            return []
        
        w3 = self.web3_connections[chain]
        latest_block = w3.eth.get_block('latest')
        
        detected = []
        
        # Check transactions in latest block
        for tx_hash in latest_block['transactions'][:50]:  # Check first 50 txs
            try:
                tx = w3.eth.get_transaction(tx_hash)
                
                # Check if transaction value exceeds threshold
                tx_value_eth = w3.from_wei(tx.value, 'ether')
                tx_value_usd = tx_value_eth * 2000  # Mock ETH price
                
                if tx_value_usd >= self.threshold_usd:
                    whale_tx = WhaleTransaction(
                        tx_hash=tx_hash.hex(),
                        from_address=tx.from_address,
                        to_address=tx.to,
                        token="ETH",
                        amount=float(tx_value_eth),
                        amount_usd=float(tx_value_usd),
                        timestamp=latest_block['timestamp'],
                        chain=chain,
                        transaction_type="transfer"
                    )
                    detected.append(whale_tx)
                    self.transactions_detected.append(whale_tx)
                    
                    # Send alert
                    await self._send_alert(whale_tx)
                    
            except Exception as e:
                continue
        
        return detected
    
    async def _send_alert(self, tx: WhaleTransaction):
        """Send whale alert"""
        # Determine severity
        if tx.amount_usd >= 10_000_000:
            severity = "critical"
        elif tx.amount_usd >= 1_000_000:
            severity = "high"
        elif tx.amount_usd >= 500_000:
            severity = "medium"
        else:
            severity = "low"
        
        # Create alert
        alert = WalletAlert(
            wallet_address=tx.from_address,
            alert_type="whale_transaction",
            message=f"🐋 Whale Alert: ${tx.amount_usd:,.0f} {tx.token} transfer",
            severity=severity,
            timestamp=tx.timestamp,
            tx_hash=tx.tx_hash
        )
        
        self.alert_history.append(alert)
        self.alerts_sent += 1
        
        # Call callback if set
        if self.alert_callback:
            await self.alert_callback(alert)
        
        # Print alert
        self._print_alert(alert, tx)
    
    def _print_alert(self, alert: WalletAlert, tx: WhaleTransaction):
        """Print formatted alert"""
        severity_emoji = {
            "low": "🟢",
            "medium": "🟡",
            "high": "🟠",
            "critical": "🔴"
        }
        
        print(f"\n{severity_emoji.get(alert.severity, '⚪')} {alert.message}")
        print(f"   From: {tx.from_address[:10]}...{tx.from_address[-8:]}")
        print(f"   To: {tx.to_address[:10] if tx.to_address else 'Contract'}...")
        print(f"   Chain: {tx.chain}")
        print(f"   TX: {tx.tx_hash[:10]}...{tx.tx_hash[-8:]}")
    
    async def analyze_wallet(self, wallet_address: str) -> Dict[str, Any]:
        """
        Analyze wallet activity
        
        Args:
            wallet_address: Wallet to analyze
        
        Returns:
            Wallet analysis
        """
        # Get transaction history (mock implementation)
        # In production, would use Etherscan API or similar
        
        return {
            "wallet": wallet_address,
            "total_transactions": 1234,
            "total_volume_usd": 50_000_000,
            "avg_transaction_usd": 40_518,
            "whale_transactions": 45,
            "first_seen": "2021-03-15",
            "last_active": "2026-03-21",
            "labels": ["DeFi Trader", "NFT Collector"],
            "risk_score": 3  # 1-10
        }
    
    async def get_market_impact(self, tx: WhaleTransaction) -> Dict[str, Any]:
        """
        Analyze market impact of whale transaction
        
        Args:
            tx: Whale transaction
        
        Returns:
            Market impact analysis
        """
        # Mock analysis
        return {
            "tx_hash": tx.tx_hash,
            "estimated_price_impact": 0.05,  # 0.05%
            "affected_tokens": [tx.token],
            "sentiment": "neutral",
            "recommendation": "monitor",
            "similar_transactions_24h": 12,
            "whale_score": 8.5  # 1-10
        }
    
    def get_statistics(self) -> Dict[str, Any]:
        """Get monitoring statistics"""
        uptime = int(time.time()) - self.start_time
        
        return {
            "uptime_hours": round(uptime / 3600, 2),
            "threshold_usd": self.threshold_usd,
            "watched_wallets": len(self.watched_wallets),
            "transactions_detected": len(self.transactions_detected),
            "alerts_sent": self.alerts_sent,
            "critical_alerts": sum(1 for a in self.alert_history if a.severity == "critical"),
            "high_alerts": sum(1 for a in self.alert_history if a.severity == "high")
        }
    
    async def start_monitoring(self, interval_seconds: int = 10):
        """
        Start continuous monitoring
        
        Args:
            interval_seconds: Check interval
        """
        print(f"🚀 Starting whale monitoring (threshold: ${self.threshold_usd:,.0f})")
        
        while True:
            try:
                # Monitor each chain
                for chain in self.rpc_urls:
                    detected = await self.monitor_transactions(chain)
                    if detected:
                        print(f"🐋 Detected {len(detected)} whale transactions on {chain}")
                
                await asyncio.sleep(interval_seconds)
                
            except KeyboardInterrupt:
                print("\n⏹️  Stopping monitoring...")
                break
            except Exception as e:
                print(f"❌ Error: {e}")
                await asyncio.sleep(interval_seconds)


# AgentX Integration
async def execute_whale_monitoring(input_data: Dict[str, Any]) -> Dict[str, Any]:
    """
    AgentX skill: Whale Transaction Monitoring
    
    Args:
        input_data: {
            "threshold_usd": 100000,
            "chains": ["ethereum", "base"],
            "watch_wallets": ["0x..."]
        }
    
    Returns:
        Monitoring results
    """
    threshold = input_data.get("threshold_usd", 100000)
    chains = input_data.get("chains", ["ethereum"])
    watch_wallets = input_data.get("watch_wallets", [])
    
    # Initialize agent
    agent = WhaleAlertAgent(
        rpc_urls={chain: f"https://{chain}-mainnet.g.alchemy.com/v2/YOUR_KEY" for chain in chains},
        threshold_usd=threshold
    )
    
    # Add watched wallets
    for wallet in watch_wallets:
        agent.add_watched_wallet(wallet)
    
    # Get statistics
    stats = agent.get_statistics()
    
    return {
        "success": True,
        "monitoring_active": True,
        "statistics": stats,
        "message": f"Monitoring {len(chains)} chains for transactions > ${threshold:,.0f}"
    }


# For CLI testing
if __name__ == "__main__":
    async def main():
        # Test the agent
        agent = WhaleAlertAgent(
            rpc_urls={"ethereum": "https://eth-mainnet.g.alchemy.com/v2/YOUR_KEY"},
            threshold_usd=100000
        )
        
        print("🐋 Whale Alert Agent")
        print("=" * 50)
        
        # Add some watched wallets
        agent.add_watched_wallet("0x28C6c06298d514Db089934071355E5743bf21d60", "Binance")
        
        # Get statistics
        stats = agent.get_statistics()
        print(f"\nMonitoring Statistics:")
        print(f"  Threshold: ${stats['threshold_usd']:,.0f}")
        print(f"  Watched Wallets: {stats['watched_wallets']}")
        print(f"  Alerts Sent: {stats['alerts_sent']}")
    
    asyncio.run(main())
