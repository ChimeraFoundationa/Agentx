"""
Auto-Attestation System for AgentX

Automatically submits attestations after task completion based on:
- Task success/failure
- Response time
- Quality metrics
- Historical performance
"""

import json
import time
from typing import Dict, Any, Optional, List
from dataclasses import dataclass
from web3 import Web3


@dataclass
class AttestationConfig:
    """Configuration for auto-attestation"""
    enabled: bool = True
    min_score: int = 50
    max_score: int = 100
    auto_submit: bool = True
    require_manual_review: bool = False
    score_thresholds: Dict[str, int] = None
    
    def __post_init__(self):
        if self.score_thresholds is None:
            self.score_thresholds = {
                "excellent": 90,
                "good": 75,
                "average": 60,
                "poor": 0
            }


class AutoAttestationSystem:
    """
    Automatic attestation system for AgentX
    
    Features:
    - Auto-score tasks based on metrics
    - Submit attestations automatically
    - Configurable scoring rules
    - Reputation tracking
    """
    
    def __init__(
        self,
        reputation_contract,
        config: Optional[AttestationConfig] = None,
        private_key: Optional[str] = None
    ):
        """
        Initialize Auto-Attestation System
        
        Args:
            reputation_contract: ReputationTracker instance
            config: Attestation configuration
            private_key: Private key for signing
        """
        self.reputation = reputation_contract
        self.config = config or AttestationConfig()
        self.private_key = private_key
        self.attestation_history = []
    
    def calculate_score(self, task_result: Dict[str, Any]) -> int:
        """
        Calculate attestation score based on task result
        
        Args:
            task_result: Dictionary with task metrics
        
        Returns:
            Score from 0-100
        """
        if not self.config.enabled:
            return 0
        
        base_score = 50  # Start with average
        
        # Factor 1: Success/Failure (±30 points)
        if task_result.get("success", False):
            base_score += 30
        else:
            base_score -= 30
        
        # Factor 2: Response time (±15 points)
        response_time = task_result.get("response_time", 5.0)
        if response_time < 2.0:
            base_score += 15  # Very fast
        elif response_time < 5.0:
            base_score += 10  # Fast
        elif response_time < 10.0:
            base_score += 5   # Average
        elif response_time > 30.0:
            base_score -= 10  # Slow
        
        # Factor 3: Accuracy/Quality (±15 points)
        accuracy = task_result.get("accuracy", 0.8)
        if accuracy >= 0.95:
            base_score += 15  # Excellent
        elif accuracy >= 0.90:
            base_score += 10  # Good
        elif accuracy >= 0.80:
            base_score += 5   # Average
        elif accuracy < 0.60:
            base_score -= 10  # Poor
        
        # Factor 4: Task complexity bonus (±10 points)
        complexity = task_result.get("complexity", "medium")
        if complexity == "high":
            base_score += 10  # Bonus for complex tasks
        elif complexity == "very_high":
            base_score += 15
        
        # Factor 5: Historical performance (±10 points)
        past_performance = task_result.get("past_performance", "average")
        if past_performance == "excellent":
            base_score += 10
        elif past_performance == "good":
            base_score += 5
        elif past_performance == "poor":
            base_score -= 5
        
        # Clamp to 0-100
        final_score = max(0, min(100, base_score))
        
        return final_score
    
    def generate_tags(self, task_result: Dict[str, Any], score: int) -> List[str]:
        """
        Generate descriptive tags based on task result
        
        Args:
            task_result: Task metrics
            score: Calculated score
        
        Returns:
            List of tags
        """
        tags = []
        
        # Success tag
        if task_result.get("success", False):
            tags.append("completed")
        else:
            tags.append("failed")
            return tags  # Don't add more tags for failed tasks
        
        # Performance tags
        response_time = task_result.get("response_time", 5.0)
        if response_time < 2.0:
            tags.append("fast")
        elif response_time < 5.0:
            tags.append("reasonable_speed")
        elif response_time > 30.0:
            tags.append("slow")
        
        # Quality tags
        accuracy = task_result.get("accuracy", 0.8)
        if accuracy >= 0.95:
            tags.append("high_quality")
            tags.append("accurate")
        elif accuracy >= 0.90:
            tags.append("good_quality")
        elif accuracy < 0.70:
            tags.append("needs_improvement")
        
        # Score-based tags
        if score >= 90:
            tags.append("excellent")
            tags.append("recommended")
        elif score >= 75:
            tags.append("good")
        elif score >= 60:
            tags.append("average")
        else:
            tags.append("below_average")
        
        # Task type tags
        task_type = task_result.get("task_type", "general")
        tags.append(f"{task_type}_task")
        
        return tags
    
    def should_auto_submit(self, score: int) -> bool:
        """
        Determine if attestation should be auto-submitted
        
        Args:
            score: Calculated score
        
        Returns:
            True if should auto-submit
        """
        if not self.config.auto_submit:
            return False
        
        if self.config.require_manual_review:
            return False
        
        if score < self.config.min_score:
            return False  # Too low, needs review
        
        return True
    
    def submit_attestation(
        self,
        agent_token_id: int,
        task_result: Dict[str, Any],
        custom_tags: Optional[List[str]] = None
    ) -> Optional[str]:
        """
        Submit attestation for completed task
        
        Args:
            agent_token_id: Agent's token ID
            task_result: Task metrics
            custom_tags: Additional custom tags
        
        Returns:
            Transaction hash or None if not submitted
        """
        if not self.config.enabled:
            print("⚠️  Auto-attestation disabled")
            return None
        
        # Calculate score
        score = self.calculate_score(task_result)
        
        # Generate tags
        tags = self.generate_tags(task_result, score)
        if custom_tags:
            tags.extend(custom_tags)
        
        # Check if should auto-submit
        if not self.should_auto_submit(score):
            print(f"⚠️  Score {score} below threshold or requires review")
            return None
        
        # Prepare attestation data
        attestation_data = {
            "agent_id": agent_token_id,
            "score": score,
            "tags": tags,
            "task_type": task_result.get("task_type", "unknown"),
            "timestamp": int(time.time())
        }
        
        try:
            # Submit to blockchain
            tx_hash = self.reputation.submit_attestation(
                agent_token_id=agent_token_id,
                interaction_result=task_result,
                custom_tags=tags,
                storage_type="http"
            )
            
            # Record in history
            attestation_data["tx_hash"] = tx_hash
            self.attestation_history.append(attestation_data)
            
            print(f"✅ Auto-attestation submitted!")
            print(f"   Agent: #{agent_token_id}")
            print(f"   Score: {score}/100")
            print(f"   Tags: {', '.join(tags)}")
            print(f"   TX: {tx_hash}")
            
            return tx_hash
        
        except Exception as e:
            print(f"❌ Failed to submit attestation: {e}")
            return None
    
    def get_attestation_history(self, agent_id: Optional[int] = None) -> List[Dict[str, Any]]:
        """
        Get attestation history
        
        Args:
            agent_id: Optional filter by agent ID
        
        Returns:
            List of attestation records
        """
        if agent_id:
            return [
                att for att in self.attestation_history
                if att.get("agent_id") == agent_id
            ]
        return self.attestation_history
    
    def get_statistics(self) -> Dict[str, Any]:
        """
        Get attestation statistics
        
        Returns:
            Statistics dictionary
        """
        if not self.attestation_history:
            return {
                "total_attestations": 0,
                "average_score": 0,
                "success_rate": 0
            }
        
        total = len(self.attestation_history)
        avg_score = sum(att.get("score", 0) for att in self.attestation_history) / total
        successes = sum(1 for att in self.attestation_history if att.get("score", 0) >= 75)
        
        return {
            "total_attestations": total,
            "average_score": round(avg_score, 2),
            "success_rate": round(successes / total * 100, 2),
            "excellent_count": sum(1 for att in self.attestation_history if att.get("score", 0) >= 90),
            "good_count": sum(1 for att in self.attestation_history if 75 <= att.get("score", 0) < 90),
            "average_count": sum(1 for att in self.attestation_history if 60 <= att.get("score", 0) < 75),
            "poor_count": sum(1 for att in self.attestation_history if att.get("score", 0) < 60)
        }


# Convenience function for task completion hook
def on_task_complete(
    agent_id: int,
    task_result: Dict[str, Any],
    reputation_contract,
    private_key: str,
    config: Optional[AttestationConfig] = None
) -> Optional[str]:
    """
    Convenience function for task completion hook
    
    Usage:
        @task_complete_handler
        def handle_completion(result):
            return on_task_complete(agent_id=1, task_result=result, ...)
    """
    system = AutoAttestationSystem(
        reputation_contract=reputation_contract,
        config=config,
        private_key=private_key
    )
    
    return system.submit_attestation(agent_id, task_result)
