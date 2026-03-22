"""
AgentX A2A CLI Commands

Commands:
- agentx a2a discover     - Discover agents by capability
- agentx a2a delegate     - Delegate task to agent
- agentx a2a reputation   - Check agent reputation
- agentx a2a tasks        - List active tasks
- agentx a2a attestation  - Submit attestation
"""

import click
import json
import asyncio
from typing import List, Optional
from web3 import Web3

# Import AgentX modules
import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from web3_modules.a2a import A2ACoordinator, TaskRequest
from web3_modules.erc8004.identity import ERC8004Identity
from web3_modules.erc8004.reputation import ReputationTracker


# Default configuration
DEFAULT_RPC = "http://localhost:8545"
DEFAULT_IDENTITY = "0xF818A7C2AFC45cF4B9DDC48933C9A1edD624e46f"
DEFAULT_REPUTATION = "0x8613A4029EaA95dA61AE65380aC2e7366451bF2b"


@click.group()
def a2a():
    """Agent-to-Agent (A2A) commands"""
    pass


@a2a.command()
@click.option('--capability', '-c', multiple=True, required=True,
              help='Required capability (can be used multiple times)')
@click.option('--min-reputation', '-r', default=0, type=int,
              help='Minimum reputation score (0-100)')
@click.option('--max-results', '-m', default=10, type=int,
              help='Maximum number of results')
@click.option('--rpc', default=DEFAULT_RPC, help='RPC URL')
@click.option('--identity', default=DEFAULT_IDENTITY, help='Identity Registry address')
def discover(capability, min_reputation, max_results, rpc, identity):
    """Discover agents by capability"""
    click.echo(f"🔍 Discovering agents with capabilities: {', '.join(capability)}")
    click.echo(f"   Minimum reputation: {min_reputation}")
    click.echo(f"   Max results: {max_results}")
    click.echo()
    
    try:
        identity_module = ERC8004Identity(rpc_url=rpc)
        identity_module.set_registry_address(identity)
        
        agents = identity_module.discover_agents(list(capability))
        
        if agents:
            click.echo(f"✅ Found {len(agents)} agent(s):")
            click.echo()
            for i, agent_id in enumerate(agents[:max_results], 1):
                click.echo(f"  {i}. Agent #{agent_id}")
        else:
            click.echo("⚠️  No agents found with these capabilities")
    
    except Exception as e:
        click.echo(f"❌ Error: {e}")


@a2a.command()
@click.option('--agent', '-a', required=True, type=int,
              help='Agent token ID to delegate to')
@click.option('--task', '-t', required=True,
              help='Task description')
@click.option('--budget', '-b', default="$0.01",
              help='Budget for task')
@click.option('--input-data', '-i', default='{}',
              help='JSON input data for task')
@click.option('--rpc', default=DEFAULT_RPC, help='RPC URL')
@click.option('--identity', default=DEFAULT_IDENTITY, help='Identity Registry address')
@click.option('--private-key', '-k', required=True,
              help='Your private key')
def delegate(agent, task, budget, input_data, rpc, identity, private_key):
    """Delegate task to an agent"""
    click.echo(f"🤝 Delegating task to Agent #{agent}")
    click.echo(f"   Task: {task}")
    click.echo(f"   Budget: {budget}")
    click.echo()
    
    try:
        input_dict = json.loads(input_data)
        
        async def run_delegation():
            coordinator = A2ACoordinator(
                agent_token_id=0,  # Will be determined
                rpc_url=rpc,
                private_key=private_key
            )
            coordinator.set_contracts(identity, DEFAULT_REPUTATION)
            
            task_request = TaskRequest(
                task_id=f"task_{Web3.keccak(text=task).hex()[:16]}",
                task_type="custom",
                description=task,
                input_data=input_dict,
                budget=budget,
                deadline=9999999999,
                requester_id=0
            )
            
            # For now, just show what would happen
            click.echo("✅ Task delegation prepared!")
            click.echo(f"   Task ID: {task_request.task_id}")
            click.echo(f"   Input: {input_dict}")
            click.echo()
            click.echo("⚠️  Note: Full delegation requires agent MCP endpoint")
        
        asyncio.run(run_delegation())
    
    except Exception as e:
        click.echo(f"❌ Error: {e}")


@a2a.command()
@click.option('--agent', '-a', required=True, type=int,
              help='Agent token ID')
@click.option('--rpc', default=DEFAULT_RPC, help='RPC URL')
@click.option('--reputation', default=DEFAULT_REPUTATION, help='Reputation Registry address')
def reputation(agent, rpc, reputation):
    """Check agent reputation"""
    click.echo(f"📊 Checking reputation for Agent #{agent}")
    click.echo()
    
    try:
        rep_module = ReputationTracker(rpc_url=rpc)
        rep_module.set_registry_address(reputation)
        
        summary = rep_module.get_reputation_summary(agent)
        
        click.echo("Agent Reputation Summary:")
        click.echo(f"  Average Score: {summary['average_score']}/100")
        click.echo(f"  Total Interactions: {summary['total_interactions']}")
        click.echo(f"  Recent Performance: {summary['recent_performance']}")
        
        if summary['top_tags']:
            click.echo(f"  Top Tags: {', '.join([tag for tag, _ in summary['top_tags'][:5]])}")
        
        click.echo()
        
        # Show recent attestations
        history = rep_module.get_reputation_history(agent)
        if history:
            click.echo(f"Recent Attestations ({len(history)} total):")
            for att in history[-5:]:
                click.echo(f"  • Score: {att['score']}/100 | Tags: {', '.join(att['tags'])}")
        else:
            click.echo("No attestations yet")
    
    except Exception as e:
        click.echo(f"❌ Error: {e}")


@a2a.command()
@click.option('--status', '-s', default='active',
              type=click.Choice(['active', 'completed', 'failed', 'all']),
              help='Filter by status')
@click.option('--limit', '-l', default=10, type=int,
              help='Limit results')
def tasks(status, limit):
    """List active tasks"""
    click.echo(f"📋 Listing {status} tasks")
    click.echo()
    
    # Placeholder - would need task storage
    click.echo("ℹ️  Task tracking requires database storage")
    click.echo("   This feature is under development")


@a2a.command()
@click.option('--agent', '-a', required=True, type=int,
              help='Agent token ID to attest')
@click.option('--score', '-s', required=True, type=int,
              help='Score (0-100)')
@click.option('--tags', '-t', multiple=True,
              help='Tags (can be used multiple times)')
@click.option('--evidence', '-e', default='',
              help='Evidence URI (IPFS/HTTP)')
@click.option('--rpc', default=DEFAULT_RPC, help='RPC URL')
@click.option('--reputation', default=DEFAULT_REPUTATION, help='Reputation Registry address')
@click.option('--private-key', '-k', required=True,
              help='Your private key')
def attestation(agent, score, tags, evidence, rpc, reputation, private_key):
    """Submit attestation for an agent"""
    click.echo(f"⭐ Submitting attestation for Agent #{agent}")
    click.echo(f"   Score: {score}/100")
    click.echo(f"   Tags: {', '.join(tags) if tags else 'none'}")
    click.echo()
    
    if score < 0 or score > 100:
        click.echo("❌ Score must be between 0 and 100")
        return
    
    try:
        rep_module = ReputationTracker(rpc_url=rpc, private_key=private_key)
        rep_module.set_registry_address(reputation)
        
        # Simulate attestation (would need real interaction result)
        interaction_result = {
            "success": score >= 70,
            "score": score,
            "task": "custom_task"
        }
        
        tx_hash = rep_module.submit_attestation(
            agent_token_id=agent,
            interaction_result=interaction_result,
            custom_tags=list(tags),
            storage_type="http"
        )
        
        click.echo("✅ Attestation submitted!")
        click.echo(f"   Transaction: {tx_hash}")
    
    except Exception as e:
        click.echo(f"❌ Error: {e}")


@a2a.command()
@click.option('--rpc', default=DEFAULT_RPC, help='RPC URL')
@click.option('--identity', default=DEFAULT_IDENTITY, help='Identity Registry address')
def stats(rpc, identity):
    """View A2A ecosystem statistics"""
    click.echo("📊 AgentX A2A Ecosystem Statistics")
    click.echo()
    
    try:
        identity_module = ERC8004Identity(rpc_url=rpc)
        identity_module.set_registry_address(identity)
        
        total = identity_module.contract.functions.getTotalAgents().call()
        
        click.echo(f"Total Agents: {total}")
        click.echo(f"Identity Registry: {identity}")
        click.echo(f"Reputation Registry: {DEFAULT_REPUTATION}")
        click.echo()
        click.echo("ℹ️  More statistics coming soon!")
    
    except Exception as e:
        click.echo(f"❌ Error: {e}")


# Main entry point
def main():
    a2a()


if __name__ == '__main__':
    main()
