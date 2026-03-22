# Agent-to-Agent (A2A) System Guide

Complete guide to implementing agent-to-agent communication in AgentX.

---

## 📋 **What is A2A?**

**Agent-to-Agent (A2A)** system enables autonomous AI agents to:

- **Discover** other agents via ERC-8004 registry
- **Evaluate** agents by reputation scores
- **Delegate** tasks to specialized agents
- **Coordinate** complex multi-agent workflows
- **Pay** each other via x402 protocol
- **Build trust** through mutual attestations

---

## 🏗️ **A2A Architecture**

```
┌─────────────────────────────────────────────────────────┐
│                  A2A ECOSYSTEM                           │
├─────────────────────────────────────────────────────────┤
│                                                         │
│  ┌──────────┐      ┌──────────┐      ┌──────────┐     │
│  │  Agent A │◀────▶│  Agent B │◀────▶│  Agent C │     │
│  │(Coordinator)   │(Specialist)    │(Specialist)    │
│  └────┬─────┘      └────┬─────┘      └────┬─────┘     │
│       │                 │                 │            │
│       │ 1. Discover     │                 │            │
│       │◀──────────────────────────────────│            │
│       │                 │                 │            │
│       │ 2. Delegate Task│                 │            │
│       │────────────────>│                 │            │
│       │                 │                 │            │
│       │ 3. Sub-delegate │                 │            │
│       │                 │────────────────>│            │
│       │                 │                 │            │
│       │ 4. Payment (x402)                 │            │
│       │──────────────────────────────────>│            │
│       │                 │                 │            │
│       │ 5. Attestation (ERC-8004)         │            │
│       │◀──────────────────────────────────│            │
│       │                 │                 │            │
└─────────────────────────────────────────────────────────┘
```

---

## 🚀 **Quick Start**

### 1. Initialize A2A Coordinator

```python
from web3_modules.a2a import A2ACoordinator, AgentProfile, TaskRequest
from web3_modules.erc8004 import ERC8004Identity, ReputationTracker
from web3_modules.x402 import X402Client

# Initialize contracts
identity = ERC8004Identity(
    rpc_url="http://localhost:8545",
    private_key="0xYOUR_PRIVATE_KEY"
)
identity.set_registry_address("0x8464135c8F25Da09e49BC8782676a84730C318bC")

reputation = ReputationTracker(
    rpc_url="http://localhost:8545",
    private_key="0xYOUR_PRIVATE_KEY"
)
reputation.set_registry_address("0x71C95911E9a5D330f4D621842EC243EE1343292e")

# Initialize x402 client (optional, for payments)
x402_client = X402Client(
    private_key="0xYOUR_PRIVATE_KEY",
    rpc_url="http://localhost:8545"
)

# Create A2A coordinator
coordinator = A2ACoordinator(
    agent_token_id=YOUR_AGENT_ID,
    identity_contract=identity,
    reputation_contract=reputation,
    x402_client=x402_client
)
```

### 2. Discover Agents

```python
async with coordinator as coord:
    # Find DeFi specialists with good reputation
    agents = await coord.discover_agents(
        required_capabilities=["defi_tracking", "nft_analysis"],
        min_reputation=80,
        max_results=5
    )
    
    print(f"Found {len(agents)} qualified agents")
    
    for agent in agents:
        print(f"  - {agent.name} (Score: {agent.reputation_score})")
```

### 3. Delegate Task

```python
# Create task request
task = TaskRequest(
    task_id="task_001",
    task_type="defi_analysis",
    description="Analyze wallet DeFi positions",
    input_data={"wallet": "0x123..."},
    budget="$0.01",
    deadline=1234567890,
    requester_id=YOUR_AGENT_ID
)

# Execute via best agent
if agents:
    result = await coord.request_task_execution(
        target_agent=agents[0],
        task_request=task
    )
    
    if result.success:
        print(f"Task completed: {result.result}")
    else:
        print(f"Task failed: {result.result}")
```

### 4. Coordinated Multi-Agent Task

```python
# Complex task requiring multiple specialists
result = await coordinator.execute_coordinated_task(
    task_description="Full portfolio analysis: DeFi + NFT + Risk",
    required_capabilities=["defi_tracking", "nft_analysis", "security_audit"],
    budget="$0.05",
    timeout=300  # 5 minutes
)

if result['success']:
    print(f"Coordinated task completed by agent {result['agent_id']}")
    print(f"Result: {result['result']}")
```

---

## 🎯 **A2A Use Cases**

### 1. **Agent Marketplace**

Agents offer services and get discovered by others:

```python
# Agent A specializes in DeFi analysis
# Agent B needs DeFi analysis for its user

# Agent B discovers Agent A
agents = await coordinator.discover_agents(
    required_capabilities=["defi_tracking"],
    min_reputation=70
)

# Agent B delegates task to Agent A
result = await coordinator.execute_coordinated_task(
    task_description="Analyze DeFi positions for wallet 0x...",
    required_capabilities=["defi_tracking"],
    budget="$0.01"
)
```

### 2. **Parallel Task Execution**

```python
from web3_modules.a2a import SubAgentOrchestrator

orchestrator = SubAgentOrchestrator(coordinator)

# Execute multiple tasks in parallel
tasks = [
    {
        "capabilities": ["defi_tracking"],
        "description": "Analyze DeFi positions",
        "timeout": 60
    },
    {
        "capabilities": ["nft_analysis"],
        "description": "Analyze NFT portfolio",
        "timeout": 60
    },
    {
        "capabilities": ["security_audit"],
        "description": "Check token approvals",
        "timeout": 30
    }
]

results = await orchestrator.parallel_execution(tasks)

for i, result in enumerate(results):
    print(f"Task {i+1}: {'Success' if result['success'] else 'Failed'}")
```

### 3. **Agent Collaboration**

Multiple agents work together on complex tasks:

```
User Request: "Full crypto portfolio analysis"
     │
     ▼
┌─────────────────┐
│  Agent A        │  ← Coordinator
│  (Orchestrator) │
└────────┬────────┘
         │
    ┌────┴────┬────────────┐
    ▼         ▼            ▼
┌───────┐ ┌───────┐ ┌──────────┐
│Agent B│ │Agent C│ │ Agent D  │
│(DeFi) │ │(NFT)  │ │(Security)│
└───────┘ └───────┘ └──────────┘
```

---

## 💰 **Inter-Agent Payments (x402)**

Agents can pay each other automatically:

```python
from web3_modules.x402 import X402Client

# Agent A pays Agent B for service
x402_client = X402Client(
    private_key=AGENT_A_PRIVATE_KEY,
    rpc_url="http://localhost:8545"
)

# Pay for MCP tool execution
result = await x402_client.pay_for_mcp_tool(
    tool_url="http://agent-b.local:8080/mcp/tools/defi_analysis",
    tool_name="defi_analysis",
    tool_args={"wallet": "0x123..."},
    expected_price="$0.01"
)
```

---

## 🏆 **Reputation & Trust**

After successful collaboration, agents attest each other:

```python
# Agent A submits attestation for Agent B
reputation.submit_attestation(
    agent_token_id=AGENT_B_ID,
    interaction_result={
        "success": True,
        "response_time": 2.5,
        "accuracy": 0.98,
        "task": "defi_analysis"
    },
    custom_tags=["reliable", "fast", "accurate"]
)

# Agent B can also attest Agent A
reputation.submit_attestation(
    agent_token_id=AGENT_A_ID,
    interaction_result={
        "success": True,
        "payment": "prompt",
        "communication": "clear"
    },
    custom_tags=["good_client", "prompt_payment"]
)
```

---

## 📊 **A2A Message Flow**

```
┌─────────┐                    ┌─────────┐
│ Agent A │                    │ Agent B │
│(Client) │                    │(Server) │
└────┬────┘                    └────┬────┘
     │                              │
     │ 1. Discover (ERC-8004)       │
     │◀─────────────────────────────│
     │                              │
     │ 2. Request Quote             │
     │─────────────────────────────>│
     │                              │
     │ 3. Quote Response            │
     │◀─────────────────────────────│
     │                              │
     │ 4. Create Agreement          │
     │─────────────────────────────>│
     │                              │
     │ 5. Payment (x402)            │
     │─────────────────────────────>│
     │                              │
     │ 6. Execute Task              │
     │◀─────────────────────────────│
     │                              │
     │ 7. Submit Result             │
     │─────────────────────────────>│
     │                              │
     │ 8. Mutual Attestation        │
     │◀────────────────────────────>│
     │                              │
```

---

## 🔧 **Configuration**

### A2A Settings

```yaml
# ~/.agentx/a2a-config.yaml

a2a:
  enabled: true
  
  # Discovery settings
  discovery:
    min_reputation: 70
    max_results: 10
    timeout: 30
  
  # Task delegation
  delegation:
    default_budget: "$0.05"
    default_timeout: 300
    max_retries: 3
  
  # Payment settings
  payment:
    enabled: true
    facilitator: "https://facilitator.payai.network"
    auto_pay: true
    spending_limit: "$10/day"
  
  # Reputation
  reputation:
    auto_attest: true
    min_score_to_attest: 80
```

---

## 🚧 **Current Status**

| Feature | Status | Notes |
|---------|--------|-------|
| **Agent Discovery** | ✅ Implemented | Via ERC-8004 |
| **Reputation Check** | ✅ Implemented | Via ERC-8004 |
| **Task Delegation** | 🚧 In Progress | Basic implementation |
| **x402 Payments** | ✅ Infrastructure | Needs integration |
| **Subagent Orchestration** | 🚧 In Progress | Basic parallel execution |
| **ACP Protocol** | 🚧 Planned | Standard message format |
| **Agent Marketplace** | 🚧 Planned | Service discovery UI |

---

## 📚 **Resources**

- **A2A Module:** `/root/agent/agentx/web3_modules/a2a.py`
- **ERC-8004 Guide:** `/root/agent/agentx/docs/erc8004-identity.md`
- **x402 Guide:** `/root/agent/agentx/docs/x402-payments.md`

---

**Next:** Implement full A2A workflow with real agent-to-agent communication! 🚀
