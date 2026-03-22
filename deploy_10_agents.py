#!/usr/bin/env python3
"""
Deploy 10 Agents on 10 Different Wallets

Creates a multi-agent ecosystem for testing A2A functionality
"""

import asyncio
from web3 import Web3
import json
import sys
import os

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from web3_modules.erc8004.identity import ERC8004Identity

# Configuration
RPC_URL = "http://localhost:8545"
IDENTITY_REGISTRY = "0x8464135c8F25Da09e49BC8782676a84730C318bC"

# Anvil default accounts (10 wallets)
ANVIL_ACCOUNTS = [
    "0xac0974bec39a17e36ba4a6b4d238ff944bacb478cbed5efcae786d7cf4715806",  # Account 0
    "0x59c6995e998f97a5a0044966f0945389dc9e86dae88c7a8412f4603b6b78690d",  # Account 1
    "0x5de4111afa1a4b94908f83103eb1f1706367c2e68ca870fc3fb9a804cdab365a",  # Account 2
    "0x7c852118294e51e653712a81e05800f419141751be58f605c371e15141b007a6",  # Account 3
    "0x47e179ec197488593b187f80a00eb0da91f1b9d0b13f8733639f19c30a34926a",  # Account 4
    "0x8b3a350cf5c34c9194ca85829a2df0ec3153be0318b5e2d3348e872092edffba",  # Account 5
    "0x92db14e403b83dfe3df233f83dfa3a0d7096f21ca9b0d6d6b8d88b2b4ec1564e",  # Account 6
    "0x4bbbf85ce3377467afe5d46f804f221813b2bb87f24d81f60f1fcdbf7cbf4356",  # Account 7
    "0xdbda1821b80551c9d65939329250298aa3472ba22feea921c0cf5d620ea67b97",  # Account 8
    "0x2a871d0798f97d79848a013d4936a73bf4cc922c825d33c1cf7073dff6d409c6",  # Account 9
]

# Agent definitions (10 different specialists)
AGENT_DEFINITIONS = [
    {
        "name": "DeFi Specialist Alpha",
        "capabilities": ["defi_tracking", "yield_farming", "liquidity_analysis"],
        "description": "Expert in DeFi protocols, yield farming, and liquidity analysis"
    },
    {
        "name": "NFT Analyst Beta",
        "capabilities": ["nft_analysis", "nft_valuation", "rarity_tracking"],
        "description": "Specializes in NFT portfolio analysis and valuation"
    },
    {
        "name": "Security Auditor Gamma",
        "capabilities": ["security_audit", "token_approval_check", "risk_assessment"],
        "description": "Security-focused agent for smart contract audits"
    },
    {
        "name": "Trading Bot Delta",
        "capabilities": ["trading", "arbitrage", "price_monitoring"],
        "description": "Automated trading and arbitrage opportunities"
    },
    {
        "name": "Whale Tracker Epsilon",
        "capabilities": ["whale_alert", "transaction_monitoring", "market_analysis"],
        "description": "Tracks whale movements and large transactions"
    },
    {
        "name": "Yield Optimizer Zeta",
        "capabilities": ["yield_optimization", "strategy_analysis", "portfolio_rebalance"],
        "description": "Optimizes yield across multiple protocols"
    },
    {
        "name": "Market Analyst Eta",
        "capabilities": ["market_analysis", "trend_prediction", "sentiment_analysis"],
        "description": "Market trends and sentiment analysis"
    },
    {
        "name": "Portfolio Manager Theta",
        "capabilities": ["portfolio_management", "asset_allocation", "risk_management"],
        "description": "Comprehensive portfolio management"
    },
    {
        "name": "Airdrop Hunter Iota",
        "capabilities": ["airdrop_hunting", "eligibility_check", "claim_optimization"],
        "description": "Finds and optimizes airdrop opportunities"
    },
    {
        "name": "Cross-Chain Kappa",
        "capabilities": ["cross_chain", "bridge_analysis", "multi_chain_tracking"],
        "description": "Cross-chain operations and bridge analysis"
    }
]


def print_header(text):
    print("\n" + "=" * 70)
    print(f"  {text}")
    print("=" * 70 + "\n")


async def deploy_agents():
    """Deploy all 10 agents"""
    print_header("🤖 DEPLOYING 10 AGENTS ON 10 WALLETS")
    
    w3 = Web3(Web3.HTTPProvider(RPC_URL))
    
    deployed_agents = []
    
    for i, (private_key, agent_def) in enumerate(zip(ANVIL_ACCOUNTS, AGENT_DEFINITIONS)):
        print(f"\n{'='*70}")
        print(f"AGENT {i+1}/10: {agent_def['name']}")
        print(f"{'='*70}")
        
        try:
            # Get account info
            account = w3.eth.account.from_key(private_key)
            balance = w3.eth.get_balance(account.address)
            
            print(f"  Wallet: {account.address}")
            print(f"  Balance: {w3.from_wei(balance, 'ether')} ETH")
            print(f"  Capabilities: {', '.join(agent_def['capabilities'])}")
            
            # Check balance
            if balance == 0:
                print(f"  ⚠️  Warning: Zero balance, skipping...")
                continue
            
            # Initialize identity module
            identity = ERC8004Identity(
                rpc_url=RPC_URL,
                private_key=private_key
            )
            identity.set_registry_address(IDENTITY_REGISTRY)
            
            # Register agent
            print(f"  📝 Registering agent on ERC-8004...")
            
            token_id = identity.register_agent(
                agent_name=agent_def['name'],
                capabilities=agent_def['capabilities'],
                description=agent_def['description'],
                service_endpoints={
                    "mcp": f"http://agent-{i+1}.local:8080/mcp",
                    "http": f"http://agent-{i+1}.local:8080/api"
                },
                storage_type="http"  # Use HTTP for testing
            )
            
            print(f"  ✅ Agent registered! Token ID: {token_id}")
            
            # Verify registration
            owner = identity.get_owner(token_id)
            agent_card = identity.get_agent_card(token_id)
            
            print(f"  ✓ Owner: {owner}")
            print(f"  ✓ Name: {agent_card.get('name')}")
            print(f"  ✓ Capabilities: {agent_card.get('capabilities')}")
            
            deployed_agents.append({
                "wallet_index": i,
                "address": account.address,
                "private_key": private_key,
                "token_id": token_id,
                "name": agent_def['name'],
                "capabilities": agent_def['capabilities'],
                "description": agent_def['description']
            })
            
        except Exception as e:
            print(f"  ❌ Failed to deploy: {e}")
            import traceback
            traceback.print_exc()
    
    # Summary
    print_header("📊 DEPLOYMENT SUMMARY")
    
    print(f"\nTotal agents deployed: {len(deployed_agents)}/10")
    
    if deployed_agents:
        print("\nDeployed Agents:")
        print("-" * 70)
        for agent in deployed_agents:
            print(f"  {agent['token_id']}. {agent['name']}")
            print(f"      Wallet: {agent['address']}")
            print(f"      Capabilities: {', '.join(agent['capabilities'])}")
            print()
        
        # Save to file
        output_file = "deployed_agents.json"
        with open(output_file, 'w') as f:
            json.dump(deployed_agents, f, indent=2)
        
        print(f"✅ Agent data saved to: {output_file}")
    else:
        print("\n❌ No agents deployed!")
    
    return deployed_agents


async def test_discovery():
    """Test agent discovery with deployed agents"""
    print_header("🔍 TESTING AGENT DISCOVERY")
    
    # Use first agent to discover others
    if len(ANVIL_ACCOUNTS) > 0:
        identity = ERC8004Identity(
            rpc_url=RPC_URL,
            private_key=ANVIL_ACCOUNTS[0]
        )
        identity.set_registry_address(IDENTITY_REGISTRY)
        
        # Test discovery for each capability
        all_capabilities = set()
        for agent_def in AGENT_DEFINITIONS:
            all_capabilities.update(agent_def['capabilities'])
        
        print(f"Testing discovery for {len(all_capabilities)} capabilities...\n")
        
        for cap in list(all_capabilities)[:5]:  # Test first 5 capabilities
            try:
                agents = identity.discover_agents([cap])
                print(f"  {cap}: {len(agents)} agent(s) found")
            except Exception as e:
                print(f"  {cap}: Error - {e}")
        
        # Get total agents
        try:
            total = identity.contract.functions.getTotalAgents().call()
            print(f"\nTotal agents in registry: {total}")
        except Exception as e:
            print(f"Error getting total: {e}")


async def main():
    """Main function"""
    print_header("AGENTX MULTI-AGENT DEPLOYMENT")
    
    # Check connection
    w3 = Web3(Web3.HTTPProvider(RPC_URL))
    if not w3.is_connected():
        print("❌ Failed to connect to Anvil!")
        return 1
    
    print(f"✅ Connected to Anvil (Chain ID: {w3.eth.chain_id})")
    print(f"📍 Block number: {w3.eth.block_number}")
    
    # Deploy agents
    deployed = await deploy_agents()
    
    if deployed:
        # Test discovery
        await test_discovery()
        
        print_header("🎉 DEPLOYMENT COMPLETE!")
        print(f"\n✅ {len(deployed)} agents deployed successfully")
        print("✅ A2A ecosystem ready for testing!")
        print("\nNext steps:")
        print("  1. Run test_a2a.py to test agent discovery")
        print("  2. Test inter-agent communication")
        print("  3. Test task delegation")
    
    return 0 if deployed else 1


if __name__ == "__main__":
    result = asyncio.run(main())
    sys.exit(result)
