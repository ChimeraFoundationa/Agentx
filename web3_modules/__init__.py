"""
AgentX Web3 Modules

ERC-8004 Identity & Reputation System
x402 Payment Protocol
MCP Web3 Tools
Blockchain Integration
"""

__version__ = "0.1.0"
__author__ = "AgentX Team"

from .erc8004 import identity, reputation, validation
from .x402 import client, server
from .mcp_web3 import goldrush, wallet_tools, swap_tools, nft_tools, defi_tools
from .blockchain import providers, wallets, transactions

__all__ = [
    # ERC-8004
    "identity",
    "reputation",
    "validation",
    # x402
    "client",
    "server",
    # MCP Web3
    "goldrush",
    "wallet_tools",
    "swap_tools",
    "nft_tools",
    "defi_tools",
    # Blockchain
    "providers",
    "wallets",
    "transactions",
]
