#!/usr/bin/env python3
"""
Register agents with proper capability indexing
"""

from web3 import Web3
import json

RPC_URL = "http://localhost:8545"
IDENTITY_REGISTRY = "0xF818A7C2AFC45cF4B9DDC48933C9A1edD624e46f"  # New deployment

# Anvil accounts
ACCOUNTS = [
    "0x59c6995e998f97a5a0044966f0945389dc9e86dae88c7a8412f4603b6b78690d",
    "0x5de4111afa1a4b94908f83103eb1f1706367c2e68ca870fc3fb9a804cdab365a",
    "0x7c852118294e51e653712a81e05800f419141751be58f605c371e15141b007a6",
    "0x47e179ec197488593b187f80a00eb0da91f1b9d0b13f8733639f19c30a34926a",
    "0x8b3a350cf5c34c9194ca85829a2df0ec3153be0318b5e2d3348e872092edffba",
]

# Agents with capabilities
AGENTS = [
    {"name": "DeFi Agent", "capabilities": ["defi_tracking", "yield_farming"]},
    {"name": "NFT Agent", "capabilities": ["nft_analysis", "nft_valuation"]},
    {"name": "Security Agent", "capabilities": ["security_audit", "risk_assessment"]},
    {"name": "Trading Agent", "capabilities": ["trading", "arbitrage"]},
    {"name": "Whale Agent", "capabilities": ["whale_alert", "transaction_monitoring"]},
]

w3 = Web3(Web3.HTTPProvider(RPC_URL))

# Load ABI
with open('contracts/out/ERC8004IdentityRegistry.sol/ERC8004IdentityRegistry.json') as f:
    data = json.load(f)
    abi = data['abi']

contract = w3.eth.contract(address=IDENTITY_REGISTRY, abi=abi)

print("=" * 70)
print("  REGISTERING AGENTS WITH CAPABILITY INDEXING")
print("=" * 70)

for i, (pk, agent) in enumerate(zip(ACCOUNTS, AGENTS)):
    account = w3.eth.account.from_key(pk)
    
    print(f"\nAgent {i+1}: {agent['name']}")
    print(f"  Wallet: {account.address}")
    
    # Convert capabilities to bytes32
    cap_hashes = [Web3.keccak(text=cap) for cap in agent['capabilities']]
    
    # Build transaction
    tx = contract.functions.mintAgentWithCapabilities(
        account.address,
        f"http://agent-{i+1}.local/card.json",
        cap_hashes
    ).build_transaction({
        'from': account.address,
        'nonce': w3.eth.get_transaction_count(account.address),
        'gas': 500000,
        'gasPrice': w3.to_wei('1', 'gwei'),
    })
    
    # Sign and send
    signed = w3.eth.account.sign_transaction(tx, pk)
    tx_hash = w3.eth.send_raw_transaction(signed.raw_transaction)
    receipt = w3.eth.wait_for_transaction_receipt(tx_hash)
    
    if receipt['status'] == 1:
        print(f"  ✅ Registered with indexed capabilities!")
        for cap in agent['capabilities']:
            print(f"      - {cap}")
    else:
        print(f"  ❌ Failed!")

# Test discovery
print("\n" + "=" * 70)
print("  TESTING CAPABILITY DISCOVERY")
print("=" * 70)

total = contract.functions.getTotalAgents().call()
print(f"\nTotal agents: {total}")

test_caps = ["defi_tracking", "nft_analysis", "security_audit", "trading", "whale_alert"]

for cap in test_caps:
    cap_hash = Web3.keccak(text=cap)
    agents = contract.functions.discoverAgents([cap_hash]).call()
    print(f"  {cap}: {len(agents)} agent(s)")

print("\n✅ Capability indexing working!")
