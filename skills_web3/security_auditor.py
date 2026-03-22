"""
Security Auditor Skill for AgentX

Audit token approvals and security risks:
- Token approval monitoring
- Risk detection
- Revoke recommendations
"""

from typing import Dict, List, Any, Optional
import asyncio
from datetime import datetime, timedelta


class SecurityAuditor:
    """
    Audit wallet security and token approvals
    """
    
    name = "security_auditor"
    description = "Audit token approvals and detect security risks"
    
    # Risk levels
    RISK_LEVELS = {
        "LOW": {"color": "green", "score_range": (0, 30)},
        "MEDIUM": {"color": "yellow", "score_range": (31, 60)},
        "HIGH": {"color": "orange", "score_range": (61, 80)},
        "CRITICAL": {"color": "red", "score_range": (81, 100)},
    }
    
    def __init__(self, rpc_url: str, goldrush_api_key: Optional[str] = None):
        """
        Initialize Security Auditor
        
        Args:
            rpc_url: Ethereum RPC endpoint
            goldrush_api_key: Optional GoldRush API key
        """
        self.rpc_url = rpc_url
        self.goldrush_api_key = goldrush_api_key
    
    async def get_token_approvals(
        self,
        wallet_address: str,
        min_age_days: int = 30
    ) -> Dict[str, Any]:
        """
        Get token approvals for a wallet
        
        Args:
            wallet_address: Wallet address
            min_age_days: Minimum age of approvals to show
        
        Returns:
            Token approvals dictionary
        """
        cutoff_date = datetime.utcnow() - timedelta(days=min_age_days)
        
        # TODO: Implement via GoldRush token_approvals tool
        return {
            "wallet": wallet_address,
            "total_approvals": 0,
            "risky_approvals": [],
            "recommendations": []
        }
    
    async def calculate_risk_score(self, wallet_address: str) -> Dict[str, Any]:
        """
        Calculate overall security risk score for a wallet
        
        Args:
            wallet_address: Wallet address
        
        Returns:
            Risk score and breakdown
        """
        approvals = await self.get_token_approvals(wallet_address)
        
        # Calculate score based on various factors
        score = 0
        
        # Factor 1: Number of unlimited approvals
        unlimited_count = len([
            a for a in approvals.get("risky_approvals", [])
            if a.get("unlimited")
        ])
        score += min(unlimited_count * 10, 40)
        
        # Factor 2: Age of approvals
        old_approvals = len([
            a for a in approvals.get("risky_approvals", [])
            if a.get("age_days", 0) > 90
        ])
        score += min(old_approvals * 5, 30)
        
        # Factor 3: Risky protocols
        risky_protocols = len([
            a for a in approvals.get("risky_approvals", [])
            if a.get("protocol_risk", "low") == "high"
        ])
        score += min(risky_protocols * 15, 30)
        
        # Clamp to 0-100
        score = min(100, score)
        
        # Determine risk level
        risk_level = self._get_risk_level(score)
        
        return {
            "wallet": wallet_address,
            "score": score,
            "risk_level": risk_level,
            "breakdown": {
                "unlimited_approvals": unlimited_count,
                "old_approvals": old_approvals,
                "risky_protocols": risky_protocols
            },
            "recommendations": self._generate_recommendations(approvals)
        }
    
    def _get_risk_level(self, score: int) -> str:
        """Get risk level from score"""
        for level, config in self.RISK_LEVELS.items():
            if config["score_range"][0] <= score <= config["score_range"][1]:
                return level
        return "LOW"
    
    def _generate_recommendations(
        self,
        approvals: Dict[str, Any]
    ) -> List[Dict[str, Any]]:
        """Generate security recommendations"""
        recommendations = []
        
        for approval in approvals.get("risky_approvals", []):
            if approval.get("unlimited"):
                recommendations.append({
                    "type": "revoke_unlimited",
                    "priority": "high",
                    "message": f"Revoke unlimited approval for {approval.get('token_symbol')}",
                    "token": approval.get("token_address"),
                    "spender": approval.get("spender_address")
                })
            
            if approval.get("age_days", 0) > 180:
                recommendations.append({
                    "type": "revoke_old",
                    "priority": "medium",
                    "message": f"Review old approval for {approval.get('token_symbol')} ({approval.get('age_days')} days)",
                    "token": approval.get("token_address")
                })
        
        return recommendations
    
    async def get_revoke_transactions(
        self,
        wallet_address: str,
        approvals: List[Dict[str, Any]]
    ) -> List[Dict[str, Any]]:
        """
        Generate revoke approval transactions
        
        Args:
            wallet_address: Wallet address
            approvals: List of approvals to revoke
        
        Returns:
            List of revoke transactions
        """
        # TODO: Implement transaction generation
        return []


# Skill export
skill = SecurityAuditor
