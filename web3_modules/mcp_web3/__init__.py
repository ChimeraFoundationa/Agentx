"""
MCP Web3 Tools

GoldRush integration and custom Web3 tools for AgentX:
- GoldRush MCP: 100+ blockchain data tools
- Wallet Tools: Balance check, transfers, approvals
- Swap Tools: DEX swaps via Uniswap, 1inch
- NFT Tools: Portfolio tracking, valuation
- DeFi Tools: Yield farming, staking, lending
"""

__version__ = "0.1.0"
__author__ = "AgentX Team"

from .goldrush import GoldRushMCP
from .wallet_tools import WalletTools
from .swap_tools import SwapTools
from .nft_tools import NFTTools
from .defi_tools import DeFiTools

__all__ = [
    "GoldRushMCP",
    "WalletTools",
    "SwapTools",
    "NFTTools",
    "DeFiTools",
]
