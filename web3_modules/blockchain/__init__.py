"""
Blockchain Integration Module

Core blockchain utilities:
- RPC Providers: Multi-chain RPC connections
- Wallet Management: Secure wallet handling
- Transaction Builder: Craft & sign transactions
"""

__version__ = "0.1.0"
__author__ = "AgentX Team"

from .providers import RPCProvider
from .wallets import WalletManager
from .transactions import TransactionBuilder

__all__ = [
    "RPCProvider",
    "WalletManager",
    "TransactionBuilder",
]
