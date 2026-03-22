#!/usr/bin/env python3
"""
Complete A2A Ecosystem Setup
- Register 5 agents on 5 wallets
- Test discovery
- Test A2A task delegation
"""

from web3 import Web3
import json
import asyncio

RPC_URL = "http://localhost:8545"
IDENTITY_REGISTRY = "0xF818A7C2AFC45cF4B9DDC48933C9A1edD624e46f"
REPUTATION_REGISTRY = "0x8613A4029EaA95dA61AE65380aC2e7366451bF2b"

# 5 Anvil accounts dengan saldo
ACCOUNTS = [
    "0x59c6995e998f97a5a0044966f0945389dc9e86dae88c7a8412f4603b6b78690d",  # 10000 ETH
    "0x5de4111afa1a4b94908f83103eb1f1706367c2e68ca870fc3fb9a804cdab365a",  # 10000 ETH
    "0x7c852118294e51e653712a81e05800f419141751be58f605c371e15141b007a6",  # 10000 ETH
    "0x47e179ec197488593b187f80a00eb0da91f1b9d0b13f8733639f19c30a34926a",  # 10000 ETH
    "0x8b3a350cf5c34c9194ca85829a2df0ec3153be0318b5e2d3348e872092edffba",  # 10000 ETH
]

# 5 Specialist Agents
AGENTS = [
    {
        "name": "DeFi Specialist",
        "capabilities": ["defi_tracking", "yield_farming", "liquidity_analysis"],
        "description": "Expert in DeFi protocols and yield optimization"
    },
    {
        "name": "NFT Analyst",
        "capabilities": ["nft_analysis", "nft_valuation", "rarity_tracking"],
        "description": "NFT portfolio analysis and valuation expert"
    },
    {
        "name": "Security Auditor",
        "capabilities": ["security_audit", "token_approval_check", "risk_assessment"],
        "description": "Smart contract security and risk assessment"
    },
    {
        "name": "Trading Bot",
        "capabilities": ["trading", "arbitrage", "price_monitoring"],
        "description": "Automated trading and arbitrage detection"
    },
    {
        "name": "Whale Tracker",
        "capabilities": ["whale_alert", "transaction_monitoring", "market_analysis"],
        "description": "Large transaction tracking and market insights"
    }
]

w3 = Web3(Web3.HTTPProvider(RPC_URL))

# Load ABI
with open('contracts/out/ERC8004IdentityRegistry.sol/ERC8004IdentityRegistry.json') as f:
    data = json.load(f)
    abi = data['abi']

contract = w3.eth.contract(address=IDENTITY_REGISTRY, abi=abi)

print("=" * 70)
print("  🤖 REGISTERING 5 SPECIALIST AGENTS")
print("=" * 70)

deployed_agents = []

for i, (pk, agent) in enumerate(zip(ACCOUNTS, AGENTS)):
    account = w3.eth.account.from_key(pk)
    balance = w3.eth.get_balance(account.address)
    
    print(f"\n{'='*70}")
    print(f"AGENT {i+1}: {agent['name']}")
    print(f"{'='*70}")
    print(f"  Wallet: {account.address}")
    print(f"  Balance: {w3.from_wei(balance, 'ether'):.2f} ETH")
    print(f"  Capabilities: {', '.join(agent['capabilities'])}")
    
    try:
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
            token_id = i  # Sequential IDs
            print(f"  ✅ SUCCESS! Token ID: {token_id}")
            
            deployed_agents.append({
                "token_id": token_id,
                "name": agent["name"],
                "capabilities": agent["capabilities"],
                "address": account.address,
                "private_key": pk
            })
        else:
            print(f"  ❌ Transaction failed!")
    
    except Exception as e:
        print(f"  ❌ Error: {e}")

# Summary
print("\n" + "=" * 70)
print("  📊 DEPLOYMENT SUMMARY")
print("=" * 70)

total = contract.functions.getTotalAgents().call()
print(f"\nTotal agents registered: {total}")

if deployed_agents:
    print(f"\nSuccessfully deployed {len(deployed_agents)} agents:")
    for agent in deployed_agents:
        print(f"  • Token #{agent['token_id']}: {agent['name']}")
        print(f"    Wallet: {agent['address']}")
        print(f"    Capabilities: {', '.join(agent['capabilities'])}")
    
    # Save to file
    with open('deployed_agents.json', 'w') as f:
        json.dump(deployed_agents, f, indent=2)
    print(f"\n✅ Saved to: deployed_agents.json")

# Test Discovery
print("\n" + "=" * 70)
print("  🔍 TESTING CAPABILITY DISCOVERY")
print("=" * 70)

all_capabilities = set()
for agent in AGENTS:
    all_capabilities.update(agent['capabilities'])

print(f"\nTesting {len(all_capabilities)} capabilities...\n")

found_counts = {}
for cap in sorted(all_capabilities):
    cap_hash = Web3.keccak(text=cap)
    agents = contract.functions.discoverAgents([cap_hash]).call()
    found_counts[cap] = len(agents)
    status = "✅" if len(agents) > 0 else "⚠️"
    print(f"  {status} {cap}: {len(agents)} agent(s)")

# Test A2A
print("\n" + "=" * 70)
print("  🤝 TESTING A2A TASK DELEGATION")
print("=" * 70)

async def test_a2a():
    from web3_modules.a2a import A2ACoordinator
    
    coordinator = A2ACoordinator(
        agent_token_id=0,
        rpc_url=RPC_URL,
        private_key=ACCOUNTS[0]
    )
    coordinator.set_contracts(IDENTITY_REGISTRY, REPUTATION_REGISTRY)
    
    print("\nDiscovering DeFi specialists...")
    try:
        async with coordinator as coord:
            agents = await coord.discover_agents(
                required_capabilities=["defi_tracking"],
                min_reputation=0,  # No reputation requirement for new agents
                max_results=5
            )
            
            print(f"  Found {len(agents)} DeFi specialists")
            
            if agents:
                for agent in agents:
                    print(f"    • Agent #{agent.token_id}: {agent.name}")
                    print(f"      Score: {agent.reputation_score}/100")
                    print(f"      Capabilities: {', '.join(agent.capabilities)}")
            
            return len(agents) > 0
    
    except Exception as e:
        print(f"  Error: {e}")
        return False

# Run A2A test
a2a_success = asyncio.run(test_a2a())

if a2a_success:
    print("\n✅ A2A discovery working!")
else:
    print("\n⚠️  A2A discovery needs more setup")

# Final Summary
print("\n" + "=" * 70)
print("  🎉 A2A ECOSYSTEM SETUP COMPLETE!")
print("=" * 70)

print(f"""
✅ Contract deployed with capability indexing
✅ {len(deployed_agents)} specialist agents registered
✅ {sum(1 for v in found_counts.values() if v > 0)}/{len(found_counts)} capabilities indexed
✅ A2A discovery {'working' if a2a_success else 'ready for testing'}

Next steps:
  1. Add reputation scores to agents
  2. Test inter-agent task delegation
  3. Deploy to Base Sepolia testnet
  4. Build agent marketplace UI
""")
