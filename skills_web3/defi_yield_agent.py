"""
DeFi Yield Agent for AgentX

Autonomous agent that:
- Monitors DeFi yields across protocols (Aave, Compound, Uniswap, Curve)
- Auto-compounds rewards for maximum APY
- Rebalances portfolio based on risk/reward
- Tracks performance and submits attestations

Usage:
    agentx delegate <agent_id> "Optimize my DeFi yields" --input '{"wallet": "0x..."}'
"""

import asyncio
from typing import Dict, List, Any, Optional
from dataclasses import dataclass
from web3 import Web3
import aiohttp

# Import AgentX modules
import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))


@dataclass
class YieldPosition:
    """DeFi yield position"""
    protocol: str
    pool: str
    asset: str
    amount: float
    apy: float
    rewards_earned: float
    claimable: bool


@dataclass
class YieldOpportunity:
    """Yield farming opportunity"""
    protocol: str
    pool: str
    assets: List[str]
    apy: float
    tvl: float
    risk_score: int  # 1-10 (1=lowest risk)
    reward_tokens: List[str]


class DeFiYieldAgent:
    """
    Autonomous DeFi Yield Optimization Agent
    
    Features:
    - Multi-protocol yield monitoring
    - Auto-compounding
    - Portfolio rebalancing
    - Risk management
    - Performance tracking
    """
    
    # Supported protocols
    PROTOCOLS = {
        "aave": {
            "name": "Aave",
            "type": "lending",
            "chains": ["ethereum", "base", "avalanche"]
        },
        "compound": {
            "name": "Compound",
            "type": "lending",
            "chains": ["ethereum", "base"]
        },
        "uniswap": {
            "name": "Uniswap V3",
            "type": "dex",
            "chains": ["ethereum", "base", "arbitrum"]
        },
        "curve": {
            "name": "Curve",
            "type": "dex",
            "chains": ["ethereum", "base", "arbitrum"]
        },
        "lido": {
            "name": "Lido",
            "type": "staking",
            "chains": ["ethereum"]
        }
    }
    
    def __init__(
        self,
        rpc_urls: Dict[str, str],
        wallet_address: Optional[str] = None,
        private_key: Optional[str] = None
    ):
        """
        Initialize DeFi Yield Agent
        
        Args:
            rpc_urls: RPC URLs by chain
            wallet_address: User's wallet address
            private_key: Private key for transactions (optional)
        """
        self.rpc_urls = rpc_urls
        self.wallet_address = wallet_address
        self.private_key = private_key
        
        # Initialize Web3 connections
        self.web3_connections = {}
        for chain, rpc in rpc_urls.items():
            self.web3_connections[chain] = Web3(Web3.HTTPProvider(rpc))
        
        # Performance tracking
        self.performance_history = []
        self.total_earned = 0.0
    
    async def analyze_portfolio(self) -> Dict[str, Any]:
        """
        Analyze current DeFi portfolio
        
        Returns:
            Portfolio analysis with positions and recommendations
        """
        if not self.wallet_address:
            return {"error": "Wallet address not set"}
        
        # Get positions across all protocols
        positions = await self._get_all_positions()
        
        # Calculate total value
        total_value = sum(pos.amount for pos in positions)
        
        # Calculate average APY
        if positions:
            avg_apy = sum(pos.apy * pos.amount for pos in positions) / total_value
        else:
            avg_apy = 0
        
        # Find optimization opportunities
        opportunities = await self._find_opportunities()
        
        return {
            "total_value_usd": total_value,
            "positions": [self._position_to_dict(p) for p in positions],
            "average_apy": round(avg_apy, 2),
            "total_rewards_earned": sum(p.rewards_earned for p in positions),
            "opportunities": [self._opportunity_to_dict(o) for o in opportunities[:5]],
            "recommendations": self._generate_recommendations(positions, opportunities)
        }
    
    async def _get_all_positions(self) -> List[YieldPosition]:
        """Get all yield positions across protocols"""
        positions = []
        
        # Check each protocol
        for protocol in self.PROTOCOLS:
            try:
                protocol_positions = await self._get_protocol_positions(protocol)
                positions.extend(protocol_positions)
            except Exception as e:
                print(f"Error fetching {protocol} positions: {e}")
                continue
        
        return positions
    
    async def _get_protocol_positions(self, protocol: str) -> List[YieldPosition]:
        """Get positions for specific protocol"""
        # This would integrate with actual protocol contracts
        # For now, return mock data
        positions = []
        
        if protocol == "aave":
            # Mock Aave positions
            positions.append(YieldPosition(
                protocol="Aave",
                pool="USDC Lending",
                asset="USDC",
                amount=1000.0,
                apy=5.2,
                rewards_earned=52.0,
                claimable=True
            ))
        
        elif protocol == "uniswap":
            # Mock Uniswap positions
            positions.append(YieldPosition(
                protocol="Uniswap V3",
                pool="ETH/USDC 0.3%",
                asset="ETH-USDC LP",
                amount=500.0,
                apy=15.5,
                rewards_earned=77.5,
                claimable=True
            ))
        
        return positions
    
    async def _find_opportunities(self) -> List[YieldOpportunity]:
        """Find yield farming opportunities"""
        opportunities = []
        
        # Mock opportunities (would fetch from API in production)
        opportunities.append(YieldOpportunity(
            protocol="Aave",
            pool="USDC Lending",
            assets=["USDC"],
            apy=5.5,
            tvl=1_000_000_000,
            risk_score=2,
            reward_tokens=["AAVE"]
        ))
        
        opportunities.append(YieldOpportunity(
            protocol="Curve",
            pool="3pool (DAI/USDC/USDT)",
            assets=["DAI", "USDC", "USDT"],
            apy=8.2,
            tvl=500_000_000,
            risk_score=3,
            reward_tokens=["CRV"]
        ))
        
        opportunities.append(YieldOpportunity(
            protocol="Uniswap V3",
            pool="ETH/USDC 0.3%",
            assets=["ETH", "USDC"],
            apy=18.5,
            tvl=300_000_000,
            risk_score=5,
            reward_tokens=[]
        ))
        
        # Sort by APY
        opportunities.sort(key=lambda x: x.apy, reverse=True)
        
        return opportunities
    
    def _generate_recommendations(
        self,
        positions: List[YieldPosition],
        opportunities: List[YieldOpportunity]
    ) -> List[Dict[str, Any]]:
        """Generate portfolio recommendations"""
        recommendations = []
        
        # Check for low APY positions
        for pos in positions:
            if pos.apy < 3.0:
                recommendations.append({
                    "type": "rebalance",
                    "priority": "high",
                    "message": f"Move {pos.asset} from {pos.protocol} (APY: {pos.apy}%) to higher yield opportunity",
                    "action": "withdraw_and_reinvest"
                })
        
        # Check for claimable rewards
        claimable = [p for p in positions if p.claimable and p.rewards_earned > 10]
        if claimable:
            recommendations.append({
                "type": "claim_rewards",
                "priority": "medium",
                "message": f"Claim ${sum(p.rewards_earned for p in claimable):.2f} in rewards",
                "action": "claim_all"
            })
        
        # Check for high APY opportunities
        high_apy = [o for o in opportunities if o.apy > 15 and o.risk_score <= 5]
        if high_apy and not any(p.apy > 15 for p in positions):
            recommendations.append({
                "type": "new_position",
                "priority": "medium",
                "message": f"Consider investing in {high_apy[0].protocol} {high_apy[0].pool} (APY: {high_apy[0].apy}%)",
                "action": "open_position"
            })
        
        return recommendations
    
    def _position_to_dict(self, pos: YieldPosition) -> Dict[str, Any]:
        """Convert YieldPosition to dict"""
        return {
            "protocol": pos.protocol,
            "pool": pos.pool,
            "asset": pos.asset,
            "amount": pos.amount,
            "apy": pos.apy,
            "rewards_earned": pos.rewards_earned,
            "claimable": pos.claimable
        }
    
    def _opportunity_to_dict(self, opp: YieldOpportunity) -> Dict[str, Any]:
        """Convert YieldOpportunity to dict"""
        return {
            "protocol": opp.protocol,
            "pool": opp.pool,
            "assets": opp.assets,
            "apy": opp.apy,
            "tvl": opp.tvl,
            "risk_score": opp.risk_score,
            "reward_tokens": opp.reward_tokens
        }
    
    async def auto_compound(self) -> Dict[str, Any]:
        """
        Auto-compound all claimable rewards
        
        Returns:
            Transaction results
        """
        if not self.private_key:
            return {"error": "Private key not set - cannot execute transactions"}
        
        # Get claimable positions
        positions = await self._get_all_positions()
        claimable = [p for p in positions if p.claimable and p.rewards_earned > 0]
        
        if not claimable:
            return {"message": "No rewards to claim"}
        
        # Claim and reinvest (mock implementation)
        results = []
        for pos in claimable:
            # In production, this would:
            # 1. Claim rewards from protocol
            # 2. Swap rewards to base asset (if needed)
            # 3. Reinvest in same pool
            
            results.append({
                "protocol": pos.protocol,
                "pool": pos.pool,
                "claimed": pos.rewards_earned,
                "reinvested": pos.rewards_earned,
                "tx_hash": "0x..."  # Mock TX hash
            })
        
        return {
            "success": True,
            "total_claimed": sum(r["claimed"] for r in results),
            "total_reinvested": sum(r["reinvested"] for r in results),
            "transactions": results
        }
    
    async def rebalance_portfolio(self, target_risk: int = 5) -> Dict[str, Any]:
        """
        Rebalance portfolio based on risk tolerance
        
        Args:
            target_risk: Target risk score (1-10)
        
        Returns:
            Rebalancing results
        """
        if not self.private_key:
            return {"error": "Private key not set"}
        
        # Get current positions
        positions = await self._get_all_positions()
        
        # Calculate current risk
        current_risk = sum(p.apy * 0.5 for p in positions) / len(positions) if positions else 0
        
        # Generate rebalancing plan
        plan = {
            "current_risk": current_risk,
            "target_risk": target_risk,
            "actions": []
        }
        
        # If current risk > target, move to safer positions
        if current_risk > target_risk:
            high_risk = [p for p in positions if p.apy > target_risk * 2]
            for pos in high_risk:
                plan["actions"].append({
                    "type": "withdraw",
                    "protocol": pos.protocol,
                    "pool": pos.pool,
                    "amount": pos.amount * 0.5,  # Withdraw 50%
                    "reason": "Reduce risk exposure"
                })
        
        # If current risk < target, move to higher yield
        elif current_risk < target_risk:
            opportunities = await self._find_opportunities()
            safe_high_yield = [o for o in opportunities if o.apy > 10 and o.risk_score <= target_risk]
            for opp in safe_high_yield[:2]:
                plan["actions"].append({
                    "type": "invest",
                    "protocol": opp.protocol,
                    "pool": opp.pool,
                    "amount": 100.0,  # Mock amount
                    "reason": "Increase yield"
                })
        
        return plan
    
    async def get_performance_report(self) -> Dict[str, Any]:
        """Get performance report"""
        positions = await self._get_all_positions()
        
        total_value = sum(p.amount for p in positions)
        total_rewards = sum(p.rewards_earned for p in positions)
        
        # Calculate APY
        if total_value > 0:
            avg_apy = sum(p.apy * p.amount for p in positions) / total_value
        else:
            avg_apy = 0
        
        return {
            "total_value_usd": total_value,
            "total_rewards_earned": total_rewards,
            "average_apy": round(avg_apy, 2),
            "positions_count": len(positions),
            "protocols_used": list(set(p.protocol for p in positions)),
            "best_performer": max(positions, key=lambda x: x.apy).protocol if positions else None,
            "performance_history": self.performance_history
        }


# AgentX Integration
async def execute_defi_analysis(input_data: Dict[str, Any]) -> Dict[str, Any]:
    """
    AgentX skill: DeFi Portfolio Analysis
    
    Args:
        input_data: {"wallet": "0x...", "action": "analyze|compound|rebalance"}
    
    Returns:
        Analysis results
    """
    wallet = input_data.get("wallet")
    action = input_data.get("action", "analyze")
    
    # Initialize agent
    agent = DeFiYieldAgent(
        rpc_urls={
            "ethereum": "https://eth-mainnet.g.alchemy.com/v2/YOUR_KEY",
            "base": "https://base-mainnet.g.alchemy.com/v2/YOUR_KEY"
        },
        wallet_address=wallet
    )
    
    # Execute action
    if action == "analyze":
        result = await agent.analyze_portfolio()
    elif action == "compound":
        result = await agent.auto_compound()
    elif action == "rebalance":
        result = await agent.rebalance_portfolio()
    elif action == "performance":
        result = await agent.get_performance_report()
    else:
        result = {"error": f"Unknown action: {action}"}
    
    return result


# For CLI testing
if __name__ == "__main__":
    import asyncio
    
    async def main():
        # Test the agent
        agent = DeFiYieldAgent(
            rpc_urls={"ethereum": "https://eth-mainnet.g.alchemy.com/v2/YOUR_KEY"},
            wallet_address="0x1234567890123456789012345678901234567890"
        )
        
        print("📊 DeFi Portfolio Analysis")
        print("=" * 50)
        
        result = await agent.analyze_portfolio()
        print(f"Total Value: ${result.get('total_value_usd', 0):,.2f}")
        print(f"Average APY: {result.get('average_apy', 0):.2f}%")
        print(f"Rewards Earned: ${result.get('total_rewards_earned', 0):,.2f}")
        print(f"\nOpportunities: {len(result.get('opportunities', []))}")
        print(f"Recommendations: {len(result.get('recommendations', []))}")
    
    asyncio.run(main())
