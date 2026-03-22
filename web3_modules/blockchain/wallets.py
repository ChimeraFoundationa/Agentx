"""
Wallet Management

Secure wallet handling with spending limits and allowlists
"""

from typing import Dict, List, Optional, Any
from web3 import Web3
from eth_account import Account
from eth_account.signers.local import LocalAccount
import json
import os


class WalletManager:
    """
    Manage wallet operations with security features:
    - Spending limits
    - Allowlists
    - Transaction logging
    """
    
    def __init__(
        self,
        private_key: Optional[str] = None,
        spending_limit_usd: float = 10.0,
        allowlist: Optional[List[str]] = None
    ):
        """
        Initialize Wallet Manager
        
        Args:
            private_key: Wallet private key (optional for read-only)
            spending_limit_usd: Daily spending limit in USD
            allowlist: List of allowed recipient addresses
        """
        self.spending_limit_usd = spending_limit_usd
        self.allowlist = allowlist or []
        self.spent_today_usd = 0.0
        self.account: Optional[LocalAccount] = None
        self.address: Optional[str] = None
        
        if private_key:
            self.set_private_key(private_key)
    
    def set_private_key(self, private_key: str):
        """
        Set wallet private key
        
        Args:
            private_key: Private key string
        """
        # Validate private key
        if not private_key.startswith("0x"):
            private_key = "0x" + private_key
        
        self.account = Account.from_key(private_key)
        self.address = self.account.address
    
    def import_from_keystore(self, keystore_path: str, password: str):
        """
        Import wallet from keystore file
        
        Args:
            keystore_path: Path to keystore file
            password: Keystore password
        """
        with open(keystore_path, 'r') as f:
            keystore = json.load(f)
        
        self.account = Account.decrypt_keystore(keystore, password)
        self.address = self.account.address
    
    def export_to_keystore(self, keystore_path: str, password: str) -> str:
        """
        Export wallet to keystore file
        
        Args:
            keystore_path: Path to save keystore
            password: Keystore password
        
        Returns:
            Path to keystore file
        """
        if not self.account:
            raise ValueError("No private key set")
        
        keystore = Account.encrypt_keystore(self.account.key, password)
        
        os.makedirs(os.path.dirname(keystore_path), exist_ok=True)
        
        with open(keystore_path, 'w') as f:
            json.dump(keystore, f)
        
        return keystore_path
    
    def check_spending_limit(self, amount_usd: float) -> bool:
        """
        Check if transaction is within spending limit
        
        Args:
            amount_usd: Transaction amount in USD
        
        Returns:
            True if within limit
        """
        return (self.spent_today_usd + amount_usd) <= self.spending_limit_usd
    
    def check_allowlist(self, address: str) -> bool:
        """
        Check if address is in allowlist
        
        Args:
            address: Address to check
        
        Returns:
            True if allowed (or allowlist is empty)
        """
        if not self.allowlist:
            return True  # Empty allowlist = all allowed
        
        return Web3.to_checksum_address(address) in [
            Web3.to_checksum_address(a) for a in self.allowlist
        ]
    
    def can_send_transaction(
        self,
        recipient: str,
        amount_usd: float
    ) -> tuple[bool, str]:
        """
        Check if transaction can be sent
        
        Args:
            recipient: Recipient address
            amount_usd: Amount in USD
        
        Returns:
            (can_send, reason)
        """
        if not self.account:
            return False, "No private key set"
        
        if not self.check_allowlist(recipient):
            return False, "Recipient not in allowlist"
        
        if not self.check_spending_limit(amount_usd):
            return False, f"Exceeds spending limit (${self.spending_limit_usd}/day)"
        
        return True, "OK"
    
    def record_transaction(self, amount_usd: float):
        """
        Record a transaction for spending limit tracking
        
        Args:
            amount_usd: Transaction amount in USD
        """
        self.spent_today_usd += amount_usd
    
    def reset_spending_tracking(self):
        """Reset daily spending tracking"""
        self.spent_today_usd = 0.0
    
    def sign_transaction(self, transaction: Dict[str, Any]) -> str:
        """
        Sign a transaction
        
        Args:
            transaction: Transaction dictionary
        
        Returns:
            Signed transaction (hex)
        """
        if not self.account:
            raise ValueError("No private key set")
        
        signed_tx = self.account.sign_transaction(transaction)
        return signed_tx.raw_transaction.hex()
    
    def sign_message(self, message: str) -> str:
        """
        Sign a message
        
        Args:
            message: Message to sign
        
        Returns:
            Signature (hex)
        """
        if not self.account:
            raise ValueError("No private key set")
        
        message_hash = Web3.keccak(text=message)
        signed_message = self.account.signHash(message_hash)
        return signed_message.signature.hex()
    
    def get_balance(self, w3: Web3) -> int:
        """
        Get ETH balance
        
        Args:
            w3: Web3 instance
        
        Returns:
            Balance in wei
        """
        if not self.address:
            raise ValueError("No address set")
        
        return w3.eth.get_balance(self.address)
    
    def get_token_balance(self, w3: Web3, token_address: str) -> int:
        """
        Get ERC-20 token balance
        
        Args:
            w3: Web3 instance
            token_address: Token contract address
        
        Returns:
            Token balance (smallest unit)
        """
        if not self.address:
            raise ValueError("No address set")
        
        # Simplified - in production, use proper ERC-20 ABI
        # This is a placeholder
        return 0
