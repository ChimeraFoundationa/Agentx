"""
AgentX Web3 Skills

Pre-built skills for DeFi tracking, NFT monitoring, whale alerts, and more.
"""

__version__ = "0.1.0"
__author__ = "AgentX Team"

from .defi_tracker import DeFiTracker
from .nft_monitor import NFTMonitor
from .whale_alert import WhaleAlert
from .airdrop_hunter import AirdropHunter
from .security_auditor import SecurityAuditor

__all__ = [
    "DeFiTracker",
    "NFTMonitor",
    "WhaleAlert",
    "AirdropHunter",
    "SecurityAuditor",
]
