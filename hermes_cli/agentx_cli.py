#!/usr/bin/env python3
"""
AgentX - Simplified CLI

Usage:
    agentx                      # Interactive mode (default)
    agentx discover defi        # Discover agents
    agentx reputation 1         # Check reputation
    agentx delegate 1 "task"    # Delegate task
    agentx stats                # View stats
    agentx attest 1 90          # Submit attestation
"""

import sys
import os
import click

# Add project root to path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from web3_modules.a2a import A2ACoordinator
from web3_modules.erc8004.identity import ERC8004Identity
from web3_modules.erc8004.reputation import ReputationTracker
from web3_modules.auto_attestation import AutoAttestationSystem, AttestationConfig

# Default configuration
DEFAULT_RPC = "http://localhost:8545"
DEFAULT_IDENTITY = "0xF818A7C2AFC45cF4B9DDC48933C9A1edD624e46f"
DEFAULT_REPUTATION = "0x8613A4029EaA95dA61AE65380aC2e7366451bF2b"


@click.group(invoke_without_command=True)
@click.pass_context
def agentx(ctx):
    """AgentX - Web3 AI Agent Protocol"""
    if ctx.invoked_subcommand is None:
        # Default: show help or interactive mode
        click.echo("🤖 AgentX - Web3 AI Agent Protocol")
        click.echo("=" * 50)
        click.echo()
        click.echo("Usage:")
        click.echo("  agentx discover <capability>     Find agents")
        click.echo("  agentx reputation <agent_id>     Check reputation")
        click.echo("  agentx delegate <agent> <task>   Delegate task")
        click.echo("  agentx stats                     View statistics")
        click.echo("  agentx attest <agent> <score>    Submit attestation")
        click.echo()
        click.echo("Run 'agentx <command> --help' for more info.")


@agentx.command()
@click.argument('capability')
@click.option('--min-score', '-m', default=0, type=int, help='Minimum reputation')
@click.option('--limit', '-l', default=10, type=int, help='Max results')
@click.option('--rpc', default=DEFAULT_RPC, help='RPC URL')
def discover(capability, min_score, limit, rpc):
    """Discover agents by capability"""
    click.echo(f"🔍 Finding agents with: {capability}")
    
    try:
        identity = ERC8004Identity(rpc_url=rpc)
        identity.set_registry_address(DEFAULT_IDENTITY)
        
        agents = identity.discover_agents([capability])
        
        if agents:
            click.echo(f"\n✅ Found {len(agents)} agent(s):")
            for i, agent_id in enumerate(agents[:limit], 1):
                click.echo(f"  {i}. Agent #{agent_id}")
        else:
            click.echo("⚠️  No agents found")
    
    except Exception as e:
        click.echo(f"❌ Error: {e}")


@agentx.command()
@click.argument('agent_id', type=int)
@click.option('--rpc', default=DEFAULT_RPC, help='RPC URL')
def reputation(agent_id, rpc):
    """Check agent reputation"""
    click.echo(f"📊 Agent #{agent_id} Reputation")
    click.echo("=" * 40)
    
    try:
        rep = ReputationTracker(rpc_url=rpc)
        rep.set_registry_address(DEFAULT_REPUTATION)
        
        summary = rep.get_reputation_summary(agent_id)
        
        click.echo(f"  Score: {summary['average_score']}/100")
        click.echo(f"  Interactions: {summary['total_interactions']}")
        click.echo(f"  Performance: {summary['recent_performance']}")
        
        if summary['top_tags']:
            tags = [tag for tag, _ in summary['top_tags'][:5]]
            click.echo(f"  Tags: {', '.join(tags)}")
    
    except Exception as e:
        click.echo(f"❌ Error: {e}")


@agentx.command()
@click.argument('agent_id', type=int)
@click.argument('task')
@click.option('--budget', '-b', default='$0.01', help='Task budget')
@click.option('--input', '-i', default='{}', help='JSON input data')
@click.option('--key', '-k', required=True, help='Your private key')
@click.option('--rpc', default=DEFAULT_RPC, help='RPC URL')
def delegate(agent_id, task, budget, input, key, rpc):
    """Delegate task to agent"""
    import json
    import asyncio
    from web3_modules.a2a import A2ACoordinator, TaskRequest
    from web3_modules.auto_attestation import AutoAttestationSystem, AttestationConfig
    
    click.echo(f"🤝 Delegating to Agent #{agent_id}")
    click.echo(f"   Task: {task}")
    click.echo(f"   Budget: {budget}")
    
    try:
        # Parse input data
        input_data = json.loads(input) if input else {}
        
        # Initialize coordinator
        coordinator = A2ACoordinator(
            agent_token_id=0,
            rpc_url=rpc,
            private_key=key
        )
        coordinator.set_contracts(DEFAULT_IDENTITY, DEFAULT_REPUTATION)
        
        # Create task request
        task_request = TaskRequest(
            task_id=f"task_{task[:20]}",
            task_type="custom",
            description=task,
            input_data=input_data,
            budget=budget,
            deadline=9999999999,
            requester_id=0
        )
        
        # Execute delegation
        async def run_delegation():
            async with coordinator as coord:
                # Get agent info (mock for now)
                agent_profile = type('AgentProfile', (), {
                    'token_id': agent_id,
                    'name': f'Agent #{agent_id}',
                    'service_endpoints': {'mcp': 'http://localhost:8080/mcp'}
                })()
                
                # Execute task
                click.echo("\n⏳ Executing task...")
                result = await coord.request_task_execution(
                    target_agent=agent_profile,
                    task_request=task_request
                )
                
                click.echo(f"\n✅ Task completed!")
                click.echo(f"   Success: {result.success}")
                click.echo(f"   Execution time: {result.execution_time:.2f}s")
                
                # Auto-attestation
                if result.success:
                    click.echo("\n⭐ Submitting auto-attestation...")
                    
                    rep = ReputationTracker(rpc_url=rpc, private_key=key)
                    rep.set_registry_address(DEFAULT_REPUTATION)
                    
                    auto_attest = AutoAttestationSystem(
                        reputation_contract=rep,
                        config=AttestationConfig(enabled=True, auto_submit=True),
                        private_key=key
                    )
                    
                    # Calculate score based on result
                    task_result = {
                        "success": result.success,
                        "response_time": result.execution_time,
                        "accuracy": 0.95,
                        "task_type": "delegated_task"
                    }
                    
                    score = auto_attest.calculate_score(task_result)
                    tags = auto_attest.generate_tags(task_result, score)
                    
                    tx_hash = rep.submit_attestation(
                        agent_token_id=agent_id,
                        interaction_result=task_result,
                        custom_tags=tags[:3],  # Top 3 tags
                        storage_type="http"
                    )
                    
                    click.echo(f"   Score: {score}/100")
                    click.echo(f"   Tags: {', '.join(tags[:3])}")
                    click.echo(f"   TX: {tx_hash}")
                
                return result
        
        # Run async
        result = asyncio.run(run_delegation())
        
    except Exception as e:
        click.echo(f"❌ Error: {e}")


@agentx.command()
@click.argument('agent_id', type=int)
@click.argument('score', type=int)
@click.option('--tags', '-t', multiple=True, help='Tags')
@click.option('--evidence', '-e', default='', help='Evidence URI')
@click.option('--key', '-k', required=True, help='Your private key')
@click.option('--rpc', default=DEFAULT_RPC, help='RPC URL')
def attest(agent_id, score, tags, evidence, key, rpc):
    """Submit attestation for agent"""
    from web3_modules.erc8004.reputation import ReputationTracker
    
    if score < 0 or score > 100:
        click.echo("❌ Score must be 0-100")
        return
    
    click.echo(f"⭐ Attesting Agent #{agent_id}")
    click.echo(f"   Score: {score}/100")
    if tags:
        click.echo(f"   Tags: {', '.join(tags)}")
    
    try:
        # Initialize reputation tracker
        rep = ReputationTracker(rpc_url=rpc, private_key=key)
        rep.set_registry_address(DEFAULT_REPUTATION)
        
        # Create interaction result
        interaction_result = {
            "success": score >= 70,
            "score": score,
            "task": "manual_attestation",
            "evidence": evidence
        }
        
        # Submit attestation
        tx_hash = rep.submit_attestation(
            agent_token_id=agent_id,
            interaction_result=interaction_result,
            custom_tags=list(tags) if tags else ["manual", "attestation"],
            storage_type="http"
        )
        
        click.echo(f"\n✅ Attestation submitted!")
        click.echo(f"   Agent: #{agent_id}")
        click.echo(f"   Score: {score}/100")
        if tags:
            click.echo(f"   Tags: {', '.join(tags)}")
        click.echo(f"   TX: {tx_hash}")
    
    except Exception as e:
        click.echo(f"❌ Error: {e}")


@agentx.command()
@click.option('--rpc', default=DEFAULT_RPC, help='RPC URL')
def stats(rpc):
    """View ecosystem statistics"""
    click.echo("📊 AgentX Ecosystem Stats")
    click.echo("=" * 40)
    
    try:
        identity = ERC8004Identity(rpc_url=rpc)
        identity.set_registry_address(DEFAULT_IDENTITY)
        
        total = identity.contract.functions.getTotalAgents().call()
        
        click.echo(f"  Total Agents: {total}")
        click.echo(f"  Network: Anvil Testnet")
        click.echo(f"  Identity: {DEFAULT_IDENTITY[:20]}...")
    
    except Exception as e:
        click.echo(f"❌ Error: {e}")


@agentx.command()
@click.option('--capability', '-c', help='Filter by capability')
@click.option('--limit', '-l', default=10, type=int)
def agents(capability, limit):
    """List all agents"""
    click.echo("📋 Agent List")
    click.echo("=" * 40)
    
    try:
        identity = ERC8004Identity(rpc_url=DEFAULT_RPC)
        identity.set_registry_address(DEFAULT_IDENTITY)
        
        total = identity.contract.functions.getTotalAgents().call()
        click.echo(f"Total: {total} agents")
        
        # TODO: List individual agents
        
    except Exception as e:
        click.echo(f"❌ Error: {e}")


def main():
    """Main entry point"""
    agentx()


if __name__ == '__main__':
    main()
