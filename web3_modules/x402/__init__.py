"""
x402 Payment Protocol Module

HTTP-native payment protocol for micropayments:
- Client: Automatic payments for APIs & services
- Server: Accept payments for your agent services
- Schemes: Exact payment, pay-per-request
"""

__version__ = "0.1.0"
__author__ = "AgentX Team"

from .client import X402Client
from .server import X402Server

__all__ = [
    "X402Client",
    "X402Server",
]
