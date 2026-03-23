"""
Security Audit Agent for AgentX

Autonomous agent that:
- Scans token approvals for risks
- Detects suspicious contracts
- Analyzes smart contract security
- Provides security recommendations

Usage:
    agentx delegate <agent_id> "Audit my wallet security" --input '{"wallet": "0x..."}'
"""

import asyncio
from typing import Dict, List, Any, Optional
from dataclasses import dataclass
from web3 import Web3
from enum import Enum


class RiskLevel(Enum):
    """Risk level classification"""
    SAFE = "safe"
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    CRITICAL = "critical"


@dataclass
class TokenApproval:
    """Token approval data"""
    token: str
    token_address: str
    spender: str
    spender_name: Optional[str]
    amount: float
    amount_usd: float
    is_unlimited: bool
    age_days: int
    risk_level: RiskLevel


@dataclass
class SecurityFinding:
    """Security audit finding"""
    finding_type: str
    severity: RiskLevel
    title: str
    description: str
    recommendation: str
    affected_address: Optional[str] = None
    cvss_score: float = 0.0


class SecurityAuditAgent:
    """
    Autonomous Security Audit Agent
    
    Features:
    - Token approval scanning
    - Risk assessment
    - Contract analysis
    - Security recommendations
    """
    
    # Known risky contracts (example)
    RISKY_CONTRACTS = {
        "0x...": {"name": "Known Scam", "risk": RiskLevel.CRITICAL},
    }
    
    # Trusted protocols
    TRUSTED_PROTOCOLS = [
        "uniswap", "aave", "compound", "curve", "lido",
        "opensea", "blur", "metamask", "coinbase"
    ]
    
    def __init__(
        self,
        rpc_urls: Dict[str, str],
        wallet_address: Optional[str] = None
    ):
        """
        Initialize Security Audit Agent
        
        Args:
            rpc_urls: RPC URLs by chain
            wallet_address: Wallet to audit
        """
        self.rpc_urls = rpc_urls
        self.wallet_address = wallet_address
        
        # Initialize Web3
        self.web3_connections = {}
        for chain, rpc in rpc_urls.items():
            self.web3_connections[chain] = Web3(Web3.HTTPProvider(rpc))
        
        # Audit results
        self.findings: List[SecurityFinding] = []
        self.approvals: List[TokenApproval] = []
    
    async def audit_wallet(self) -> Dict[str, Any]:
        """
        Perform comprehensive wallet security audit
        
        Returns:
            Audit report
        """
        if not self.wallet_address:
            return {"error": "Wallet address not set"}
        
        # Reset findings
        self.findings = []
        self.approvals = []
        
        # Scan token approvals
        await self._scan_approvals()
        
        # Check for risky interactions
        await self._check_risky_interactions()
        
        # Analyze portfolio risk
        portfolio_risk = await self._analyze_portfolio_risk()
        
        # Generate security score
        security_score = self._calculate_security_score()
        
        return {
            "wallet": self.wallet_address,
            "security_score": security_score,
            "risk_level": self._get_overall_risk_level(security_score).value,
            "findings_count": len(self.findings),
            "critical_findings": sum(1 for f in self.findings if f.severity == RiskLevel.CRITICAL),
            "high_findings": sum(1 for f in self.findings if f.severity == RiskLevel.HIGH),
            "approvals": {
                "total": len(self.approvals),
                "unlimited": sum(1 for a in self.approvals if a.is_unlimited),
                "risky": sum(1 for a in self.approvals if a.risk_level in [RiskLevel.HIGH, RiskLevel.CRITICAL])
            },
            "findings": [self._finding_to_dict(f) for f in self.findings],
            "recommendations": self._generate_recommendations()
        }
    
    async def _scan_approvals(self):
        """Scan token approvals for wallet"""
        # Mock implementation - in production would use Etherscan API or RPC calls
        
        # Example mock approvals
        self.approvals.append(TokenApproval(
            token="USDC",
            token_address="0xA0b86991c6218b36c1d19D4a2e9Eb0cE3606eB48",
            spender="0x7a250d5630B4cF539739dF2C5dAcb4c659F2488D",
            spender_name="Uniswap V2 Router",
            amount=999999999.99,
            amount_usd=999999999.99,
            is_unlimited=True,
            age_days=180,
            risk_level=RiskLevel.MEDIUM
        ))
        
        self.approvals.append(TokenApproval(
            token="USDT",
            token_address="0xdAC17F958D2ee523a2206206994597C13D831ec7",
            spender="0x...",
            spender_name="Unknown Contract",
            amount=50000.0,
            amount_usd=50000.0,
            is_unlimited=False,
            age_days=365,
            risk_level=RiskLevel.HIGH
        ))
        
        # Generate findings for risky approvals
        unlimited_approvals = [a for a in self.approvals if a.is_unlimited and a.age_days > 90]
        for approval in unlimited_approvals:
            self.findings.append(SecurityFinding(
                finding_type="unlimited_approval",
                severity=RiskLevel.HIGH,
                title=f"Unlimited {approval.token} Approval",
                description=f"Unlimited approval for {approval.spender_name or approval.spender} ({approval.age_days} days old)",
                recommendation="Revoke unlimited approval and set specific amount",
                affected_address=approval.token_address,
                cvss_score=7.5
            ))
    
    async def _check_risky_interactions(self):
        """Check for risky contract interactions"""
        # Mock implementation
        # In production, would analyze transaction history
        
        # Example finding
        self.findings.append(SecurityFinding(
            finding_type="old_approval",
            severity=RiskLevel.MEDIUM,
            title="Old Token Approval",
            description="Token approval older than 1 year detected",
            recommendation="Review and revoke if no longer needed",
            cvss_score=5.0
        ))
    
    async def _analyze_portfolio_risk(self) -> Dict[str, Any]:
        """Analyze portfolio risk"""
        return {
            "diversification_score": 8.0,
            "protocol_risk": "medium",
            "smart_contract_risk": "low",
            "liquidity_risk": "low"
        }
    
    def _calculate_security_score(self) -> int:
        """Calculate overall security score (0-100)"""
        if not self.findings:
            return 100
        
        # Deduct points for findings
        score = 100
        for finding in self.findings:
            if finding.severity == RiskLevel.CRITICAL:
                score -= 30
            elif finding.severity == RiskLevel.HIGH:
                score -= 20
            elif finding.severity == RiskLevel.MEDIUM:
                score -= 10
            elif finding.severity == RiskLevel.LOW:
                score -= 5
        
        return max(0, min(100, score))
    
    def _get_overall_risk_level(self, score: int) -> RiskLevel:
        """Get overall risk level from score"""
        if score >= 90:
            return RiskLevel.SAFE
        elif score >= 70:
            return RiskLevel.LOW
        elif score >= 50:
            return RiskLevel.MEDIUM
        elif score >= 30:
            return RiskLevel.HIGH
        else:
            return RiskLevel.CRITICAL
    
    def _generate_recommendations(self) -> List[Dict[str, Any]]:
        """Generate security recommendations"""
        recommendations = []
        
        # Check for unlimited approvals
        unlimited = [a for a in self.approvals if a.is_unlimited]
        if unlimited:
            recommendations.append({
                "priority": "high",
                "action": "revoke_approvals",
                "message": f"Revoke {len(unlimited)} unlimited token approvals",
                "estimated_time": "5 minutes"
            })
        
        # Check for old approvals
        old = [a for a in self.approvals if a.age_days > 180]
        if old:
            recommendations.append({
                "priority": "medium",
                "action": "review_approvals",
                "message": f"Review {len(old)} approvals older than 6 months",
                "estimated_time": "10 minutes"
            })
        
        # Check critical findings
        critical = [f for f in self.findings if f.severity == RiskLevel.CRITICAL]
        if critical:
            recommendations.append({
                "priority": "critical",
                "action": "immediate_action",
                "message": f"Address {len(critical)} critical security issues immediately",
                "estimated_time": "30 minutes"
            })
        
        return recommendations
    
    def _finding_to_dict(self, finding: SecurityFinding) -> Dict[str, Any]:
        """Convert SecurityFinding to dict"""
        return {
            "type": finding.finding_type,
            "severity": finding.severity.value,
            "title": finding.title,
            "description": finding.description,
            "recommendation": finding.recommendation,
            "affected_address": finding.affected_address,
            "cvss_score": finding.cvss_score
        }
    
    async def revoke_approval(
        self,
        token_address: str,
        spender_address: str
    ) -> Dict[str, Any]:
        """
        Revoke token approval
        
        Args:
            token_address: Token contract address
            spender_address: Spender address to revoke
        
        Returns:
            Transaction result
        """
        if not self.wallet_address or not self.private_key:
            return {"error": "Wallet not configured"}
        
        # In production, would execute actual transaction
        return {
            "success": True,
            "token": token_address,
            "spender": spender_address,
            "tx_hash": "0x...",  # Mock TX hash
            "gas_used": 50000,
            "message": "Approval revoked successfully"
        }
    
    async def get_security_tips(self) -> List[str]:
        """Get security best practices tips"""
        return [
            "✅ Regularly review and revoke unused token approvals",
            "✅ Use hardware wallets for large amounts",
            "✅ Never share your private key or seed phrase",
            "✅ Verify contract addresses before interacting",
            "✅ Use separate wallets for different risk levels",
            "✅ Enable 2FA on all centralized accounts",
            "✅ Keep software and wallets updated",
            "✅ Be cautious of phishing attempts"
        ]


# AgentX Integration
async def execute_security_audit(input_data: Dict[str, Any]) -> Dict[str, Any]:
    """
    AgentX skill: Wallet Security Audit
    
    Args:
        input_data: {"wallet": "0x...", "chains": ["ethereum"]}
    
    Returns:
        Audit report
    """
    wallet = input_data.get("wallet")
    chains = input_data.get("chains", ["ethereum"])
    
    # Initialize agent
    agent = SecurityAuditAgent(
        rpc_urls={chain: f"https://{chain}-mainnet.g.alchemy.com/v2/YOUR_KEY" for chain in chains},
        wallet_address=wallet
    )
    
    # Perform audit
    report = await agent.audit_wallet()
    
    return report


# For CLI testing
if __name__ == "__main__":
    async def main():
        # Test the agent
        agent = SecurityAuditAgent(
            rpc_urls={"ethereum": "https://eth-mainnet.g.alchemy.com/v2/YOUR_KEY"},
            wallet_address="0x1234567890123456789012345678901234567890"
        )
        
        print("🔒 Security Audit Agent")
        print("=" * 50)
        
        report = await agent.audit_wallet()
        
        print(f"\nSecurity Score: {report['security_score']}/100")
        print(f"Risk Level: {report['risk_level']}")
        print(f"Findings: {report['findings_count']}")
        print(f"  - Critical: {report['critical_findings']}")
        print(f"  - High: {report['high_findings']}")
        print(f"\nApprovals: {report['approvals']['total']}")
        print(f"  - Unlimited: {report['approvals']['unlimited']}")
        print(f"  - Risky: {report['approvals']['risky']}")
        
        if report['recommendations']:
            print(f"\nTop Recommendations:")
            for rec in report['recommendations'][:3]:
                print(f"  [{rec['priority'].upper()}] {rec['message']}")
    
    asyncio.run(main())
