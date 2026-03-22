"""
Transaction Builder

Build and craft blockchain transactions for various purposes
"""

from typing import Dict, List, Any, Optional
from web3 import Web3
from eth_account import Account


class TransactionBuilder:
    """
    Build blockchain transactions for various purposes:
    - ETH transfers
    - ERC-20 transfers
    - Contract calls
    - x402 payments
    """
    
    # ERC-20 ABI (simplified)
    ERC20_ABI = [
        {
            "name": "transfer",
            "type": "function",
            "inputs": [
                {"name": "to", "type": "address"},
                {"name": "amount", "type": "uint256"}
            ],
            "outputs": [{"name": "success", "type": "bool"}]
        },
        {
            "name": "approve",
            "type": "function",
            "inputs": [
                {"name": "spender", "type": "address"},
                {"name": "amount", "type": "uint256"}
            ],
            "outputs": [{"name": "success", "type": "bool"}]
        },
        {
            "name": "balanceOf",
            "type": "function",
            "inputs": [{"name": "account", "type": "address"}],
            "outputs": [{"name": "balance", "type": "uint256"}]
        }
    ]
    
    @staticmethod
    def build_eth_transfer(
        w3: Web3,
        from_address: str,
        to_address: str,
        amount_wei: int,
        gas_price: Optional[int] = None,
        nonce: Optional[int] = None
    ) -> Dict[str, Any]:
        """
        Build ETH transfer transaction
        
        Args:
            w3: Web3 instance
            from_address: Sender address
            to_address: Recipient address
            amount_wei: Amount in wei
            gas_price: Gas price (optional)
            nonce: Nonce (optional)
        
        Returns:
            Transaction dictionary
        """
        tx = {
            "from": Web3.to_checksum_address(from_address),
            "to": Web3.to_checksum_address(to_address),
            "value": amount_wei,
            "chainId": w3.eth.chain_id,
        }
        
        if gas_price:
            tx["gasPrice"] = gas_price
        else:
            tx["gasPrice"] = w3.eth.gas_price
        
        if nonce is None:
            tx["nonce"] = w3.eth.get_transaction_count(
                Web3.to_checksum_address(from_address)
            )
        else:
            tx["nonce"] = nonce
        
        # Estimate gas
        tx["gas"] = w3.eth.estimate_gas(tx)
        
        return tx
    
    @staticmethod
    def build_erc20_transfer(
        w3: Web3,
        from_address: str,
        token_address: str,
        to_address: str,
        amount: int,
        gas_price: Optional[int] = None,
        nonce: Optional[int] = None
    ) -> Dict[str, Any]:
        """
        Build ERC-20 transfer transaction
        
        Args:
            w3: Web3 instance
            from_address: Sender address
            token_address: Token contract address
            to_address: Recipient address
            amount: Amount in token's smallest unit
            gas_price: Gas price (optional)
            nonce: Nonce (optional)
        
        Returns:
            Transaction dictionary
        """
        # Create contract instance
        contract = w3.eth.contract(
            address=Web3.to_checksum_address(token_address),
            abi=TransactionBuilder.ERC20_ABI
        )
        
        # Build transaction data
        tx_data = contract.functions.transfer(
            Web3.to_checksum_address(to_address),
            amount
        ).build_transaction({
            "from": Web3.to_checksum_address(from_address),
            "chainId": w3.eth.chain_id,
        })
        
        if gas_price:
            tx_data["gasPrice"] = gas_price
        else:
            tx_data["gasPrice"] = w3.eth.gas_price
        
        if nonce is not None:
            tx_data["nonce"] = nonce
        
        return tx_data
    
    @staticmethod
    def build_erc20_approve(
        w3: Web3,
        from_address: str,
        token_address: str,
        spender_address: str,
        amount: int,
        gas_price: Optional[int] = None,
        nonce: Optional[int] = None
    ) -> Dict[str, Any]:
        """
        Build ERC-20 approve transaction
        
        Args:
            w3: Web3 instance
            from_address: Sender address
            token_address: Token contract address
            spender_address: Spender address
            amount: Amount to approve
            gas_price: Gas price (optional)
            nonce: Nonce (optional)
        
        Returns:
            Transaction dictionary
        """
        contract = w3.eth.contract(
            address=Web3.to_checksum_address(token_address),
            abi=TransactionBuilder.ERC20_ABI
        )
        
        tx_data = contract.functions.approve(
            Web3.to_checksum_address(spender_address),
            amount
        ).build_transaction({
            "from": Web3.to_checksum_address(from_address),
            "chainId": w3.eth.chain_id,
        })
        
        if gas_price:
            tx_data["gasPrice"] = gas_price
        else:
            tx_data["gasPrice"] = w3.eth.gas_price
        
        if nonce is not None:
            tx_data["nonce"] = nonce
        
        return tx_data
    
    @staticmethod
    def build_x402_payment(
        w3: Web3,
        from_address: str,
        token_address: str,
        recipient: str,
        amount: int,
        idempotency_key: str,
        resource_url: str,
        gas_price: Optional[int] = None,
        nonce: Optional[int] = None
    ) -> Dict[str, Any]:
        """
        Build x402 payment transaction
        
        Args:
            w3: Web3 instance
            from_address: Payer address
            token_address: Token contract address (USDC)
            recipient: Payment recipient
            amount: Amount in token's smallest unit
            idempotency_key: Idempotency key
            resource_url: Resource being purchased
            gas_price: Gas price (optional)
            nonce: Nonce (optional)
        
        Returns:
            Transaction dictionary
        """
        # For x402, we typically use signature-based payments
        # This is a simplified version that does an actual transfer
        return TransactionBuilder.build_erc20_transfer(
            w3=w3,
            from_address=from_address,
            token_address=token_address,
            to_address=recipient,
            amount=amount,
            gas_price=gas_price,
            nonce=nonce
        )
    
    @staticmethod
    def build_contract_call(
        w3: Web3,
        from_address: str,
        contract_address: str,
        contract_abi: List[Dict[str, Any]],
        function_name: str,
        function_args: List[Any],
        value: int = 0,
        gas_price: Optional[int] = None,
        nonce: Optional[int] = None
    ) -> Dict[str, Any]:
        """
        Build contract function call transaction
        
        Args:
            w3: Web3 instance
            from_address: Sender address
            contract_address: Contract address
            contract_abi: Contract ABI
            function_name: Function to call
            function_args: Function arguments
            value: ETH value to send (wei)
            gas_price: Gas price (optional)
            nonce: Nonce (optional)
        
        Returns:
            Transaction dictionary
        """
        contract = w3.eth.contract(
            address=Web3.to_checksum_address(contract_address),
            abi=contract_abi
        )
        
        func = getattr(contract.functions, function_name)
        
        tx_data = func(*function_args).build_transaction({
            "from": Web3.to_checksum_address(from_address),
            "value": value,
            "chainId": w3.eth.chain_id,
        })
        
        if gas_price:
            tx_data["gasPrice"] = gas_price
        else:
            tx_data["gasPrice"] = w3.eth.gas_price
        
        if nonce is not None:
            tx_data["nonce"] = nonce
        
        return tx_data
