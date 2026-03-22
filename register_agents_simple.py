#!/usr/bin/env python3
"""
Simple script to register 10 agents on 10 different wallets
"""

from web3 import Web3
import json

# Configuration
RPC_URL = "http://localhost:8545"
IDENTITY_REGISTRY = "0x8464135c8F25Da09e49BC8782676a84730C318bC"

# Anvil accounts
ANVIL_ACCOUNTS = [
    "0x59c6995e998f97a5a0044966f0945389dc9e86dae88c7a8412f4603b6b78690d",  # Account 1
    "0x5de4111afa1a4b94908f83103eb1f1706367c2e68ca870fc3fb9a804cdab365a",  # Account 2
    "0x7c852118294e51e653712a81e05800f419141751be58f605c371e15141b007a6",  # Account 3
    "0x47e179ec197488593b187f80a00eb0da91f1b9d0b13f8733639f19c30a34926a",  # Account 4
    "0x8b3a350cf5c34c9194ca85829a2df0ec3153be0318b5e2d3348e872092edffba",  # Account 5
]

# Agent definitions
AGENTS = [
    {"name": "DeFi Agent", "capabilities": ["defi_tracking"]},
    {"name": "NFT Agent", "capabilities": ["nft_analysis"]},
    {"name": "Security Agent", "capabilities": ["security_audit"]},
    {"name": "Trading Agent", "capabilities": ["trading"]},
    {"name": "Whale Agent", "capabilities": ["whale_alert"]},
]

w3 = Web3(Web3.HTTPProvider(RPC_URL))

# Load contract ABI
with open('contracts/out/ERC8004IdentityRegistry.sol/ERC8004IdentityRegistry.json') as f:
    data = json.load(f)
    abi = data['abi']

contract = w3.eth.contract(address=IDENTITY_REGISTRY, abi=abi)

print("=" * 70)
print("  DEPLOYING 5 AGENTS")
print("=" * 70)

for i, (pk, agent) in enumerate(zip(ANVIL_ACCOUNTS, AGENTS)):
    print(f"\nAgent {i+1}: {agent['name']}")
    
    account = w3.eth.account.from_key(pk)
    
    # Check if already registered (simple check by getting total)
    total = contract.functions.getTotalAgents().call()
    
    # Build transaction
    tx = contract.functions.mintAgent(
        account.address,
        f"http://agent-{i+1}.local/card.json"
    ).build_transaction({
        'from': account.address,
        'nonce': w3.eth.get_transaction_count(account.address),
        'gas': 500000,
        'gasPrice': w3.to_wei('1', 'gwei'),
    })
    
    # Sign and send
    signed = w3.eth.account.sign_transaction(tx, pk)
    tx_hash = w3.eth.send_raw_transaction(signed.raw_transaction)
    
    # Wait for receipt
    receipt = w3.eth.wait_for_transaction_receipt(tx_hash)
    
    if receipt['status'] == 1:
        # Get token ID from Transfer event
        token_id = total  # Since we're minting sequentially
        print(f"  ✅ Registered! Token ID: {token_id}")
        print(f"  Wallet: {account.address}")
        print(f"  Capabilities: {agent['capabilities']}")
    else:
        print(f"  ❌ Failed!")

# Show total
total = contract.functions.getTotalAgents().call()
print(f"\n{'='*70}")
print(f"  Total agents: {total}")
print(f"{'='*70}")
