"""
ERC-8004 Identity & Reputation Module

Provides on-chain identity management for AI agents:
- Identity Registry: Mint agent as ERC-721 NFT
- Reputation Registry: Track attestations & feedback
- Validation Registry: Record task completion proofs
"""

__version__ = "0.1.0"
__author__ = "AgentX Team"

from .identity import ERC8004Identity
from .reputation import ReputationTracker
from .validation import ValidationRecorder

__all__ = [
    "ERC8004Identity",
    "ReputationTracker",
    "ValidationRecorder",
]
