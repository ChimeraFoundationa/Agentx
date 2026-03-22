"""
Agent-to-Agent (A2A) Communication Module for AgentX

Enables autonomous agents to:
- Discover and evaluate other agents
- Negotiate and coordinate tasks
- Execute inter-agent payments
- Build trust through reputation

Usage:
    from web3_modules.a2a import A2ACoordinator, SubAgentOrchestrator
    
    async with A2ACoordinator(...) as coordinator:
        agents = await coordinator.discover_agents(["defi_tracking"])
        result = await coordinator.execute_coordinated_task("Analyze portfolio")
"""

import json
import asyncio
import time
from typing import Dict, List, Any, Optional, Callable
from dataclasses import dataclass, asdict, field
from web3 import Web3
import aiohttp

# Lazy imports to avoid circular dependencies
_erc8004_identity = None
_erc8004_reputation = None
_x402_client = None

def _get_erc8004_identity():
    global _erc8004_identity
    if _erc8004_identity is None:
        from .erc8004.identity import ERC8004Identity
        _erc8004_identity = ERC8004Identity
    return _erc8004_identity

def _get_erc8004_reputation():
    global _erc8004_reputation
    if _erc8004_reputation is None:
        from .erc8004.reputation import ReputationTracker
        _erc8004_reputation = ReputationTracker
    return _erc8004_reputation

def _get_x402_client():
    global _x402_client
    if _x402_client is None:
        from .x402.client import X402Client
        _x402_client = X402Client
    return _x402_client


@dataclass
class AgentProfile:
    """Agent profile from ERC-8004"""
    token_id: int
    owner: str
    name: str
    capabilities: List[str]
    reputation_score: int
    total_interactions: int
    service_endpoints: Dict[str, str]
    x402_accepted: bool


@dataclass
class TaskRequest:
    """Task request from one agent to another"""
    task_id: str
    task_type: str
    description: str
    input_data: Dict[str, Any]
    budget: str  # e.g., "$0.01"
    deadline: int  # Unix timestamp
    requester_id: int  # ERC-8004 token ID
    payment_terms: Optional[Dict[str, Any]] = None


@dataclass
class TaskResponse:
    """Task response from service agent"""
    task_id: str
    success: bool
    result: Any
    execution_time: float
    agent_id: int
    error: Optional[str] = None


@dataclass
class ACPMessage:
    """
    Agent Communication Protocol Message
    
    Standard format for agent-to-agent communication
    """
    message_id: str
    sender_id: int
    recipient_id: int
    intent: str  # "request", "response", "proposal", "accept", "reject"
    payload: Dict[str, Any]
    timestamp: int = field(default_factory=lambda: int(time.time()))
    signature: Optional[str] = None


class A2ACoordinator:
    """
    Coordinate agent-to-agent interactions
    
    Features:
    - Agent discovery and evaluation
    - Task delegation
    - Payment coordination
    - Reputation tracking
    """
    
    def __init__(
        self,
        agent_token_id: int,
        identity_contract = None,
        reputation_contract = None,
        x402_client = None,
        rpc_url: str = "http://localhost:8545",
        private_key: Optional[str] = None
    ):
        """
        Initialize A2A Coordinator
        
        Args:
            agent_token_id: This agent's ERC-8004 token ID
            identity_contract: ERC8004Identity instance (optional, will create if not provided)
            reputation_contract: ERC8004Reputation instance (optional)
            x402_client: X402Client for payments (optional)
            rpc_url: RPC endpoint
            private_key: Private key for signing (optional, needed for transactions)
        """
        self.agent_token_id = agent_token_id
        self.rpc_url = rpc_url
        self.private_key = private_key
        self.w3 = Web3(Web3.HTTPProvider(rpc_url))
        self.http_session = None
        
        # Lazy import classes
        ERC8004Identity = _get_erc8004_identity()
        ReputationTracker = _get_erc8004_reputation()
        X402Client = _get_x402_client()
        
        # Initialize contracts if not provided
        if identity_contract:
            self.identity = identity_contract
        else:
            self.identity = ERC8004Identity(rpc_url=rpc_url, private_key=private_key)
        
        if reputation_contract:
            self.reputation = reputation_contract
        else:
            self.reputation = ReputationTracker(rpc_url=rpc_url, private_key=private_key)
        
        self.x402 = x402_client
    
    async def __aenter__(self):
        self.http_session = aiohttp.ClientSession()
        return self
    
    async def __aexit__(self, exc_type, exc_val, exc_tb):
        if self.http_session:
            await self.http_session.close()
    
    def set_contracts(self, identity_address: str, reputation_address: str):
        """Set contract addresses for identity and reputation"""
        self.identity.set_registry_address(identity_address)
        self.reputation.set_registry_address(reputation_address)
    
    async def discover_agents(
        self,
        required_capabilities: List[str],
        min_reputation: int = 70,
        max_results: int = 10
    ) -> List[AgentProfile]:
        """
        Discover agents matching criteria

        Args:
            required_capabilities: List of required capabilities
            min_reputation: Minimum reputation score (0-100)
            max_results: Maximum number of results

        Returns:
            List of qualified agent profiles
        """
        # Query identity registry
        # Pass capability names as strings (not hashes) - identity.discover_agents will hash them
        try:
            agent_ids = self.identity.discover_agents(required_capabilities)
        except Exception as e:
            # Handle any HexBytes or other errors
            import traceback
            print(f"Warning: discover_agents failed: {e}")
            print(f"Traceback: {traceback.format_exc()}")
            agent_ids = []

        # Filter and build profiles
        qualified_agents = []

        for agent_id in agent_ids[:max_results]:
            try:
                # Get reputation
                rep_summary = self.reputation.get_reputation_summary(agent_id)
                
                if rep_summary['average_score'] >= min_reputation:
                    # Get agent info
                    agent_info = self.identity.get_identity_info(agent_id)
                    
                    profile = AgentProfile(
                        token_id=agent_id,
                        owner=agent_info['owner'],
                        name=agent_info['name'],
                        capabilities=agent_info['capabilities'],
                        reputation_score=rep_summary['average_score'],
                        total_interactions=rep_summary['total_interactions'],
                        service_endpoints=agent_info.get('service_endpoints', {}),
                        x402_accepted=agent_info.get('x402_accepted', True)
                    )
                    
                    qualified_agents.append(profile)
            
            except Exception as e:
                print(f"Error evaluating agent {agent_id}: {e}")
                continue
        
        # Sort by reputation
        qualified_agents.sort(key=lambda x: x.reputation_score, reverse=True)
        
        return qualified_agents
    
    async def request_task_execution(
        self,
        target_agent: AgentProfile,
        task_request: TaskRequest
    ) -> TaskResponse:
        """
        Request another agent to execute a task
        
        Args:
            target_agent: Agent to delegate task to
            task_request: Task details
        
        Returns:
            Task response
        """
        # Get agent's MCP endpoint
        mcp_endpoint = target_agent.service_endpoints.get('mcp')
        
        if not mcp_endpoint:
            raise ValueError(f"Agent {target_agent.token_id} has no MCP endpoint")
        
        # Prepare request
        url = f"{mcp_endpoint}/mcp/tools/execute"
        
        payload = {
            "task_id": task_request.task_id,
            "task_type": task_request.task_type,
            "description": task_request.description,
            "input_data": task_request.input_data,
            "requester_id": self.agent_token_id,
            "budget": task_request.budget,
            "deadline": task_request.deadline
        }
        
        headers = {
            "Content-Type": "application/json",
            "X-Agent-ID": str(self.agent_token_id),
        }
        
        # Add x402 payment if required
        if target_agent.x402_accepted and self.x402:
            # TODO: Implement x402 payment for task
            pass
        
        # Send request
        async with self.http_session.post(url, json=payload, headers=headers) as response:
            if response.status == 200:
                result = await response.json()
                return TaskResponse(
                    task_id=task_request.task_id,
                    success=True,
                    result=result,
                    execution_time=result.get('execution_time', 0),
                    agent_id=target_agent.token_id
                )
            else:
                return TaskResponse(
                    task_id=task_request.task_id,
                    success=False,
                    result={"error": await response.text()},
                    execution_time=0,
                    agent_id=target_agent.token_id
                )
    
    async def execute_coordinated_task(
        self,
        task_description: str,
        required_capabilities: List[str],
        budget: str = "$0.05",
        timeout: int = 300
    ) -> Dict[str, Any]:
        """
        Execute a complex task by coordinating multiple agents
        
        Args:
            task_description: High-level task description
            required_capabilities: Capabilities needed
            budget: Total budget for task
            timeout: Timeout in seconds
        
        Returns:
            Task result
        """
        # 1. Discover suitable agents
        agents = await self.discover_agents(
            required_capabilities=required_capabilities,
            min_reputation=70
        )
        
        if not agents:
            return {
                "success": False,
                "error": "No qualified agents found"
            }
        
        # 2. Create task request
        task_request = TaskRequest(
            task_id=f"task_{Web3.keccak(text=task_description).hex()[:16]}",
            task_type="coordinated_task",
            description=task_description,
            input_data={"description": task_description},
            budget=budget,
            deadline=int(asyncio.get_event_loop().time()) + timeout,
            requester_id=self.agent_token_id
        )
        
        # 3. Delegate to best agent
        best_agent = agents[0]  # Highest reputation
        
        try:
            response = await self.request_task_execution(best_agent, task_request)
            
            if response.success:
                # 4. Submit attestation for successful task
                await self._submit_success_attestation(
                    agent_id=best_agent.token_id,
                    task_response=response
                )
                
                return {
                    "success": True,
                    "agent_id": best_agent.token_id,
                    "result": response.result,
                    "execution_time": response.execution_time
                }
            else:
                return {
                    "success": False,
                    "error": "Task execution failed",
                    "details": response.result
                }
        
        except Exception as e:
            return {
                "success": False,
                "error": str(e)
            }
    
    async def _submit_success_attestation(
        self,
        agent_id: int,
        task_response: TaskResponse
    ):
        """Submit positive attestation after successful task"""
        try:
            score = min(100, 80 + int(task_response.execution_time < 5))
            
            self.reputation.submit_attestation(
                agent_token_id=agent_id,
                interaction_result={
                    "success": True,
                    "task": task_response.task_id,
                    "response_time": task_response.execution_time,
                    "accuracy": 1.0
                },
                custom_tags=["reliable", "completed"]
            )
        except Exception as e:
            print(f"Failed to submit attestation: {e}")


class SubAgentOrchestrator:
    """
    Orchestrator for spawning and managing subagents
    
    Enables parallel task execution with isolated contexts
    """
    
    def __init__(self, coordinator: A2ACoordinator):
        self.coordinator = coordinator
        self.active_subagents = {}
    
    async def spawn_subagent(
        self,
        capabilities: List[str],
        task: str,
        timeout: int = 60
    ) -> Dict[str, Any]:
        """
        Spawn a subagent for isolated task execution
        
        Args:
            capabilities: Required capabilities
            task: Task description
            timeout: Execution timeout
        
        Returns:
            Task result
        """
        # Find suitable agent
        agents = await self.coordinator.discover_agents(capabilities)
        
        if not agents:
            return {"success": False, "error": "No agents found"}
        
        # Execute via subagent
        result = await self.coordinator.execute_coordinated_task(
            task_description=task,
            required_capabilities=capabilities,
            timeout=timeout
        )
        
        return result
    
    async def parallel_execution(
        self,
        tasks: List[Dict[str, Any]]
    ) -> List[Dict[str, Any]]:
        """
        Execute multiple tasks in parallel via subagents
        
        Args:
            tasks: List of task definitions
        
        Returns:
            List of results
        """
        coroutines = [
            self.spawn_subagent(
                capabilities=task['capabilities'],
                task=task['description'],
                timeout=task.get('timeout', 60)
            )
            for task in tasks
        ]
        
        results = await asyncio.gather(*coroutines, return_exceptions=True)
        
        return [
            result if isinstance(result, dict) else {"error": str(result)}
            for result in results
        ]
