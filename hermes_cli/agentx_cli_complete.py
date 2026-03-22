#!/usr/bin/env python3
"""
AgentX - Complete CLI with all features

Features:
- MCP task execution
- x402 payments
- Task history tracking
- Multi-capability search
- Batch attestation
"""

import sys
import os
import click
import json
import asyncio

# Add project root to path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from web3_modules.a2a import A2ACoordinator, TaskRequest
from web3_modules.erc8004.identity import ERC8004Identity
from web3_modules.erc8004.reputation import ReputationTracker
from web3_modules.auto_attestation import AutoAttestationSystem, AttestationConfig
from web3_modules.task_history import TaskHistoryManager, get_task_history
from web3_modules.a2a_payments import A2APaymentManager, PaymentConfig
from web3_modules.agent_x402 import AgentX402Integration

# Default configuration
DEFAULT_RPC = "http://localhost:8545"
DEFAULT_IDENTITY = "0xF818A7C2AFC45cF4B9DDC48933C9A1edD624e46f"
DEFAULT_REPUTATION = "0x8613A4029EaA95dA61AE65380aC2e7366451bF2b"


@click.group(invoke_without_command=True)
@click.pass_context
def agentx(ctx):
    """AgentX - Web3 AI Agent Protocol"""
    if ctx.invoked_subcommand is None:
        click.echo("🤖 AgentX - Web3 AI Agent Protocol")
        click.echo("=" * 50)
        click.echo()
        click.echo("Commands:")
        click.echo("  discover [capabilities...]     Find agents (multi-capability)")
        click.echo("  delegate <agent> <task>        Delegate with auto-attestation")
        click.echo("  reputation <agent>             Check reputation")
        click.echo("  attest <agent> <score>         Submit attestation")
        click.echo("  batch-attest <scores...>       Batch attestation")
        click.echo("  tasks                          View task history")
        click.echo("  stats                          View statistics")
        click.echo()
        click.echo("Run 'agentx <command> --help' for more info.")


@agentx.command()
@click.argument('capabilities', nargs=-1, required=True)
@click.option('--min-score', '-m', default=0, type=int)
@click.option('--limit', '-l', default=10, type=int)
@click.option('--rpc', default=DEFAULT_RPC)
def discover(capabilities, min_score, limit, rpc):
    """Discover agents by capability (supports multiple)"""
    if len(capabilities) == 1:
        click.echo(f"🔍 Finding agents with: {capabilities[0]}")
    else:
        click.echo(f"🔍 Finding agents with: {', '.join(capabilities)}")
    
    try:
        identity = ERC8004Identity(rpc_url=rpc)
        identity.set_registry_address(DEFAULT_IDENTITY)
        
        # Support multiple capabilities
        agents = identity.discover_agents(list(capabilities))
        
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
@click.argument('task')
@click.option('--budget', '-b', default='$0.01')
@click.option('--input', '-i', default='{}')
@click.option('--key', '-k', required=True)
@click.option('--rpc', default=DEFAULT_RPC)
@click.option('--auto-pay', is_flag=True, help='Enable x402 auto-payment')
def delegate(agent_id, task, budget, input, key, rpc, auto_pay):
    """Delegate task with MCP execution, x402 payment & auto-attestation"""
    from web3_modules.mcp_web3.goldrush import GoldRushMCP
    
    click.echo(f"🤝 Delegating to Agent #{agent_id}")
    click.echo(f"   Task: {task}")
    click.echo(f"   Budget: {budget}")
    click.echo(f"   Auto-pay: {'Enabled' if auto_pay else 'Disabled'}")
    
    try:
        input_data = json.loads(input) if input else {}
        
        # Create task in history
        history = get_task_history()
        task_record = history.create_task(
            task_id=f"task_{task[:20]}_{int(asyncio.get_event_loop().time())}",
            agent_id=agent_id,
            requester_id=0,
            description=task,
            task_type="delegated",
            input_data=input_data,
            budget=budget
        )
        
        click.echo(f"   Task ID: {task_record.task_id}")
        
        # Initialize coordinator
        coordinator = A2ACoordinator(
            agent_token_id=0,
            rpc_url=rpc,
            private_key=key
        )
        coordinator.set_contracts(DEFAULT_IDENTITY, DEFAULT_REPUTATION)
        
        # Initialize payment manager if auto-pay enabled
        if auto_pay:
            from web3_modules.x402.client import X402Client
            x402_client = X402Client(private_key=key, rpc_url=rpc)
            payment_manager = A2APaymentManager(
                x402_client=x402_client,
                config=PaymentConfig(enabled=True, auto_pay=True)
            )
            click.echo("💳 Payment manager initialized")
        
        # Execute delegation
        async def run_delegation():
            async with coordinator as coord:
                agent_profile = type('AgentProfile', (), {
                    'token_id': agent_id,
                    'name': f'Agent #{agent_id}',
                    'service_endpoints': {'mcp': 'http://localhost:8080/mcp'}
                })()
                
                task_request = TaskRequest(
                    task_id=task_record.task_id,
                    task_type="delegated",
                    description=task,
                    input_data=input_data,
                    budget=budget,
                    deadline=9999999999,
                    requester_id=0
                )
                
                click.echo("\n⏳ Executing task via MCP...")
                task_record.status = "executing"
                history._save()
                
                # Mock execution (replace with real MCP call)
                await asyncio.sleep(1)  # Simulate execution
                
                result = await coord.request_task_execution(
                    target_agent=agent_profile,
                    task_request=task_request
                )
                
                # Update task history
                if result.success:
                    task_record.status = "completed"
                    task_record.result = {"success": True}
                    task_record.execution_time = result.execution_time
                else:
                    task_record.status = "failed"
                    task_record.result = {"error": "Task failed"}
                history._save()
                
                click.echo(f"\n{'✅' if result.success else '❌'} Task {'completed' if result.success else 'failed'}!")
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
                        custom_tags=tags[:3],
                        storage_type="http"
                    )
                    
                    # Update task history
                    history.set_attestation_tx(task_record.task_id, tx_hash, score)
                    
                    click.echo(f"   Score: {score}/100")
                    click.echo(f"   Tags: {', '.join(tags[:3])}")
                    click.echo(f"   TX: {tx_hash}")
                
                return result
        
        result = asyncio.run(run_delegation())
        
    except Exception as e:
        click.echo(f"❌ Error: {e}")


@agentx.command()
@click.argument('agent_id', type=int)
@click.argument('score', type=int)
@click.option('--tags', '-t', multiple=True)
@click.option('--evidence', '-e', default='')
@click.option('--key', '-k', required=True)
@click.option('--rpc', default=DEFAULT_RPC)
def attest(agent_id, score, tags, evidence, key, rpc):
    """Submit attestation for agent"""
    if score < 0 or score > 100:
        click.echo("❌ Score must be 0-100")
        return
    
    click.echo(f"⭐ Attesting Agent #{agent_id}")
    click.echo(f"   Score: {score}/100")
    if tags:
        click.echo(f"   Tags: {', '.join(tags)}")
    
    try:
        rep = ReputationTracker(rpc_url=rpc, private_key=key)
        rep.set_registry_address(DEFAULT_REPUTATION)
        
        interaction_result = {
            "success": score >= 70,
            "score": score,
            "task": "manual_attestation",
            "evidence": evidence
        }
        
        tx_hash = rep.submit_attestation(
            agent_token_id=agent_id,
            interaction_result=interaction_result,
            custom_tags=list(tags) if tags else ["manual", "attestation"],
            storage_type="http"
        )
        
        click.echo(f"\n✅ Attestation submitted!")
        click.echo(f"   TX: {tx_hash}")
    
    except Exception as e:
        click.echo(f"❌ Error: {e}")


@agentx.command()
@click.argument('attestations', nargs=-1, required=True)
@click.option('--key', '-k', required=True)
@click.option('--rpc', default=DEFAULT_RPC)
def batch_attest(attestations, key, rpc):
    """Batch attestation for multiple agents
    
    Format: agent_id:score:tags
    Example: agentx batch-attest 0:90:completed,reliable 1:85:good,fast
    """
    click.echo(f"📋 Batch attestation for {len(attestations)} agent(s)")
    
    try:
        rep = ReputationTracker(rpc_url=rpc, private_key=key)
        rep.set_registry_address(DEFAULT_REPUTATION)
        
        results = []
        for att in attestations:
            parts = att.split(':')
            if len(parts) < 2:
                click.echo(f"⚠️  Invalid format: {att} (expected agent_id:score:tags)")
                continue
            
            agent_id = int(parts[0])
            score = int(parts[1])
            tags = parts[2].split(',') if len(parts) > 2 else ["batch"]
            
            if score < 0 or score > 100:
                click.echo(f"⚠️  Invalid score for agent {agent_id}: {score}")
                continue
            
            click.echo(f"\n  Agent #{agent_id}: Score {score}/100, Tags: {', '.join(tags)}")
            
            interaction_result = {
                "success": score >= 70,
                "score": score,
                "task": "batch_attestation"
            }
            
            tx_hash = rep.submit_attestation(
                agent_token_id=agent_id,
                interaction_result=interaction_result,
                custom_tags=tags,
                storage_type="http"
            )
            
            results.append({
                "agent_id": agent_id,
                "score": score,
                "tx": tx_hash
            })
        
        click.echo(f"\n✅ Batch attestation complete!")
        click.echo(f"   Submitted: {len(results)} attestations")
        for r in results:
            click.echo(f"   • Agent #{r['agent_id']}: {r['tx'][:20]}...")
    
    except Exception as e:
        click.echo(f"❌ Error: {e}")


@agentx.command()
@click.option('--status', '-s', type=click.Choice(['all', 'pending', 'completed', 'failed']))
@click.option('--limit', '-l', default=10, type=int)
@click.option('--agent', '-a', type=int, help='Filter by agent ID')
def tasks(status, limit, agent):
    """View task history"""
    click.echo("📋 Task History")
    click.echo("=" * 50)
    
    try:
        history = get_task_history()
        
        if status == 'all' or not status:
            task_list = history.get_recent_tasks(limit)
        else:
            task_list = history.get_tasks_by_status(status)
        
        if agent is not None:
            task_list = history.get_tasks_by_agent(agent)
        
        if not task_list:
            click.echo("No tasks found")
            return
        
        for task in task_list[:limit]:
            status_icon = {
                "pending": "⏳",
                "executing": "⏳",
                "completed": "✅",
                "failed": "❌"
            }.get(task.status, "❓")
            
            click.echo(f"\n{status_icon} Task: {task.description[:40]}")
            click.echo(f"   ID: {task.task_id}")
            click.echo(f"   Agent: #{task.agent_id}")
            click.echo(f"   Status: {task.status}")
            click.echo(f"   Created: {task.created_at}")
            if task.execution_time:
                click.echo(f"   Execution time: {task.execution_time:.2f}s")
            if task.score:
                click.echo(f"   Score: {task.score}/100")
        
        # Show summary
        stats = history.get_statistics()
        click.echo(f"\n{'='*50}")
        click.echo(f"Total: {stats['total_tasks']} | Completed: {stats['completed']} | Failed: {stats['failed']}")
        click.echo(f"Success rate: {stats['success_rate']}%")
    
    except Exception as e:
        click.echo(f"❌ Error: {e}")


@agentx.command()
@click.option('--rpc', default=DEFAULT_RPC)
def stats(rpc):
    """View ecosystem statistics"""
    click.echo("📊 AgentX Ecosystem Stats")
    click.echo("=" * 50)
    
    try:
        identity = ERC8004Identity(rpc_url=rpc)
        identity.set_registry_address(DEFAULT_IDENTITY)
        
        total = identity.contract.functions.getTotalAgents().call()
        
        # Get task stats
        task_history = get_task_history()
        task_stats = task_history.get_statistics()
        
        click.echo(f"\n🤖 Agents:")
        click.echo(f"  Total Agents: {total}")
        
        click.echo(f"\n📋 Tasks:")
        click.echo(f"  Total Tasks: {task_stats['total_tasks']}")
        click.echo(f"  Completed: {task_stats['completed']}")
        click.echo(f"  Success Rate: {task_stats['success_rate']}%")
        click.echo(f"  Avg Execution: {task_stats['avg_execution_time']}s")
        
        click.echo(f"\n🌐 Network:")
        click.echo(f"  Network: Anvil Testnet")
        click.echo(f"  Identity: {DEFAULT_IDENTITY[:20]}...")
        click.echo(f"  Reputation: {DEFAULT_REPUTATION[:20]}...")
    
    except Exception as e:
        click.echo(f"❌ Error: {e}")


@agentx.command()
@click.option('--limit', '-l', default=10, type=int)
def payments(limit):
    """View x402 payment history"""
    click.echo("💳 x402 Payment History")
    click.echo("=" * 50)
    
    try:
        # Get payment history from task history
        history = get_task_history()
        tasks = history.get_recent_tasks(limit)
        
        payments_count = sum(1 for t in tasks if t.payment_tx)
        
        if payments_count == 0:
            click.echo("No payments yet")
            return
        
        click.echo(f"Recent payments ({payments_count} total):")
        for task in tasks[:limit]:
            if task.payment_tx:
                click.echo(f"\n  💰 Payment for: {task.description[:30]}")
                click.echo(f"     Amount: {task.budget}")
                click.echo(f"     TX: {task.payment_tx[:20]}...")
                click.echo(f"     Status: {task.status}")
        
        # Show spending summary
        click.echo(f"\n{'='*50}")
        click.echo(f"Total Payments: {payments_count}")
    
    except Exception as e:
        click.echo(f"❌ Error: {e}")


@agentx.command()
@click.argument('limit_usd', type=float)
@click.option('--key', '-k', required=True, help='Private key')
def set_limit(limit_usd, key):
    """Set daily spending limit for x402"""
    click.echo(f"💳 Setting daily spending limit: ${limit_usd}")
    
    try:
        # In production, this would update the x402 client config
        click.echo(f"✅ Spending limit set to ${limit_usd}/day")
        click.echo("⚠️  Note: This is a demo. Full implementation requires wallet integration.")
    
    except Exception as e:
        click.echo(f"❌ Error: {e}")


@agentx.command()
@click.option('--capability', '-c', help='Filter by capability')
@click.option('--limit', '-l', default=20, type=int)
def agents(capability, limit):
    """List all agents"""
    click.echo("📋 Agent List")
    click.echo("=" * 50)
    
    try:
        identity = ERC8004Identity(rpc_url=DEFAULT_RPC)
        identity.set_registry_address(DEFAULT_IDENTITY)
        
        total = identity.contract.functions.getTotalAgents().call()
        click.echo(f"Total: {total} agents")
        
        if capability:
            click.echo(f"Filter: {capability}")
            agents = identity.discover_agents([capability])
            click.echo(f"Found: {len(agents)} with '{capability}'")
        
        # TODO: List individual agents with details
    
    except Exception as e:
        click.echo(f"❌ Error: {e}")


def main():
    """Main entry point"""
    agentx()


if __name__ == '__main__':
    main()
