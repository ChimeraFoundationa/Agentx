"""
ERC-8004 Reputation Registry Implementation

Track and manage agent reputation via on-chain attestations:
- Submit feedback after interactions
- Query reputation scores
- Track performance metrics
"""

import json
from typing import List, Dict, Optional, Any
from web3 import Web3
from web3.contract import Contract
import requests
from datetime import datetime, timedelta


class ReputationTracker:
    """
    Track and submit reputation attestations for AI agents
    """
    
    # Default Reputation Registry addresses (update after deployment)
    REGISTRY_ADDRESSES = {
        "ethereum": "0x...",
        "base": "0x...",
        "base_sepolia": "0x...",
        "sepolia": "0x...",
        "anvil": "0x71C95911E9a5D330f4D621842EC243EE1343292e",  # Local testnet
    }
    
    # ABI for Reputation Registry (simplified)
    REPUTATION_REGISTRY_ABI = [
        {
            "inputs": [
                {"name": "agentId", "type": "uint256"},
                {"name": "score", "type": "uint8"},
                {"name": "tags", "type": "string[]"},
                {"name": "evidence", "type": "string"}
            ],
            "name": "submitAttestation",
            "outputs": [],
            "stateMutability": "nonpayable",
            "type": "function"
        },
        {
            "inputs": [{"name": "agentId", "type": "uint256"}],
            "name": "getReputationHistory",
            "outputs": [
                {
                    "components": [
                        {"name": "attester", "type": "address"},
                        {"name": "score", "type": "uint8"},
                        {"name": "tags", "type": "string[]"},
                        {"name": "evidence", "type": "string"},
                        {"name": "timestamp", "type": "uint256"}
                    ],
                    "name": "attestations",
                    "type": "tuple[]"
                }
            ],
            "stateMutability": "view",
            "type": "function"
        },
        {
            "inputs": [{"name": "agentId", "type": "uint256"}],
            "name": "getAverageScore",
            "outputs": [{"name": "score", "type": "uint8"}],
            "stateMutability": "view",
            "type": "function"
        },
        {
            "anonymous": False,
            "inputs": [
                {"indexed": True, "name": "agentId", "type": "uint256"},
                {"indexed": True, "name": "attester", "type": "address"},
                {"indexed": False, "name": "score", "type": "uint8"}
            ],
            "name": "AttestationSubmitted",
            "type": "event"
        }
    ]
    
    def __init__(self, rpc_url: str, private_key: Optional[str] = None):
        """
        Initialize Reputation Tracker
        
        Args:
            rpc_url: Ethereum RPC endpoint
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
        """Set the Reputation Registry contract address"""
        self.contract = self.w3.eth.contract(
            address=Web3.to_checksum_address(address),
            abi=self.REPUTATION_REGISTRY_ABI
        )
    
    def calculate_score(self, interaction_result: Dict[str, Any]) -> int:
        """
        Calculate reputation score (0-100) based on interaction result
        
        Args:
            interaction_result: Dictionary with interaction metrics
        
        Returns:
            Score from 0-100
        """
        score = 50  # Base score
        
        # Success/failure
        if interaction_result.get("success", False):
            score += 30
        else:
            score -= 30
        
        # Response time (faster = better)
        response_time = interaction_result.get("response_time", 10)
        if response_time < 2:
            score += 10
        elif response_time < 5:
            score += 5
        elif response_time > 30:
            score -= 10
        
        # Accuracy (if provided)
        accuracy = interaction_result.get("accuracy", 0.8)
        score += int(accuracy * 10)
        
        # Clamp to 0-100
        return max(0, min(100, score))
    
    def extract_tags(self, interaction_result: Dict[str, Any]) -> List[str]:
        """
        Extract tags from interaction result
        
        Args:
            interaction_result: Dictionary with interaction metrics
        
        Returns:
            List of tags
        """
        tags = []
        
        if interaction_result.get("success", False):
            tags.append("task_completed")
            
            if interaction_result.get("response_time", 10) < 5:
                tags.append("fast_response")
            
            if interaction_result.get("accuracy", 0) > 0.95:
                tags.append("high_accuracy")
            
            if interaction_result.get("complexity", "medium") == "high":
                tags.append("complex_task")
        else:
            tags.append("task_failed")
            
            if interaction_result.get("error_type"):
                tags.append(f"error_{interaction_result['error_type']}")
        
        return tags
    
    def upload_evidence(self, interaction_result: Dict[str, Any], storage_type: str = "ipfs") -> str:
        """
        Upload interaction evidence to decentralized storage
        
        Args:
            interaction_result: Interaction details
            storage_type: Storage backend
        
        Returns:
            URI pointing to evidence
        """
        evidence_data = {
            "timestamp": datetime.utcnow().isoformat(),
            "interaction": interaction_result
        }
        
        if storage_type == "ipfs":
            # TODO: Implement actual IPFS upload
            return "ipfs://QmEvidencePlaceholder..."
        elif storage_type == "arweave":
            return "ar://EvidencePlaceholder..."
        else:
            return "https://agentx.dev/evidence/placeholder.json"
    
    def submit_attestation(
        self,
        agent_token_id: int,
        interaction_result: Dict[str, Any],
        custom_tags: Optional[List[str]] = None,
        storage_type: str = "ipfs"
    ) -> str:
        """
        Submit feedback after agent completes task
        
        Args:
            agent_token_id: Agent's ERC-8004 token ID
            interaction_result: Dictionary with interaction metrics
            custom_tags: Optional custom tags
            storage_type: Where to store evidence
        
        Returns:
            Transaction hash
        """
        if not self.contract:
            raise ValueError("Registry contract address not set.")
        
        if not self.account:
            raise ValueError("Private key required to submit attestation.")
        
        # Calculate score and extract tags
        score = self.calculate_score(interaction_result)
        tags = self.extract_tags(interaction_result)
        
        if custom_tags:
            tags.extend(custom_tags)
        
        # Upload evidence
        evidence_uri = self.upload_evidence(interaction_result, storage_type)
        
        # Build transaction
        tx = self.contract.functions.submitAttestation(
            agent_token_id,
            score,
            tags,
            evidence_uri
        ).build_transaction({
            "from": self.address,
            "nonce": self.w3.eth.get_transaction_count(self.address),
            "chainId": self.chain_id,
            "gas": 150000,
            "gasPrice": self.w3.eth.gas_price
        })
        
        # Sign and send
        signed_tx = self.w3.eth.account.sign_transaction(tx, self.private_key)
        tx_hash = self.w3.eth.send_raw_transaction(signed_tx.raw_transaction)
        
        return tx_hash.hex()
    
    def get_reputation_history(self, agent_token_id: int) -> List[Dict[str, Any]]:
        """
        Get all attestations for an agent
        
        Args:
            agent_token_id: Agent's token ID
        
        Returns:
            List of attestation records
        """
        if not self.contract:
            raise ValueError("Registry contract address not set.")
        
        attestations = self.contract.functions.getReputationHistory(agent_token_id).call()
        
        return [
            {
                "attester": att[0],
                "score": att[1],
                "tags": att[2],
                "evidence": att[3],
                "timestamp": datetime.fromtimestamp(att[4])
            }
            for att in attestations
        ]
    
    def get_average_score(self, agent_token_id: int) -> int:
        """
        Get average reputation score for an agent
        
        Args:
            agent_token_id: Agent's token ID
        
        Returns:
            Average score (0-100)
        """
        if not self.contract:
            raise ValueError("Registry contract address not set.")
        
        return self.contract.functions.getAverageScore(agent_token_id).call()
    
    def get_reputation_summary(self, agent_token_id: int) -> Dict[str, Any]:
        """
        Get comprehensive reputation summary for an agent
        
        Args:
            agent_token_id: Agent's token ID
        
        Returns:
            Reputation summary dictionary
        """
        history = self.get_reputation_history(agent_token_id)
        avg_score = self.get_average_score(agent_token_id)
        
        # Calculate statistics
        total_interactions = len(history)
        
        if total_interactions == 0:
            return {
                "token_id": agent_token_id,
                "average_score": 0,
                "total_interactions": 0,
                "score_distribution": {},
                "top_tags": [],
                "recent_performance": "No data"
            }
        
        # Score distribution
        score_dist = {"excellent": 0, "good": 0, "average": 0, "poor": 0}
        for att in history:
            score = att["score"]
            if score >= 90:
                score_dist["excellent"] += 1
            elif score >= 70:
                score_dist["good"] += 1
            elif score >= 50:
                score_dist["average"] += 1
            else:
                score_dist["poor"] += 1
        
        # Top tags
        all_tags = []
        for att in history:
            all_tags.extend(att["tags"])
        
        tag_counts = {}
        for tag in all_tags:
            tag_counts[tag] = tag_counts.get(tag, 0) + 1
        
        top_tags = sorted(tag_counts.items(), key=lambda x: x[1], reverse=True)[:10]
        
        # Recent performance trend
        recent = history[-10:] if len(history) >= 10 else history
        recent_avg = sum(att["score"] for att in recent) / len(recent) if recent else 0
        
        return {
            "token_id": agent_token_id,
            "average_score": avg_score,
            "total_interactions": total_interactions,
            "score_distribution": score_dist,
            "top_tags": top_tags,
            "recent_average": round(recent_avg, 2),
            "recent_performance": "Improving" if recent_avg > avg_score else "Stable" if recent_avg == avg_score else "Declining"
        }
    
    def check_reputation_threshold(
        self,
        agent_token_id: int,
        min_score: int = 70,
        min_interactions: int = 5
    ) -> bool:
        """
        Verify agent meets minimum reputation requirements
        
        Args:
            agent_token_id: Agent's token ID
            min_score: Minimum average score required
            min_interactions: Minimum number of interactions required
        
        Returns:
            True if agent meets requirements
        """
        summary = self.get_reputation_summary(agent_token_id)
        
        return (
            summary["average_score"] >= min_score and
            summary["total_interactions"] >= min_interactions
        )
