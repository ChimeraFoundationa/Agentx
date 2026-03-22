# AgentX A2A CLI Commands

Complete guide to using AgentX A2A CLI commands.

---

## 🚀 **Quick Start**

```bash
# Discover agents by capability
agentx a2a discover --capability defi_tracking

# Check agent reputation
agentx a2a reputation --agent 1

# Delegate task to agent
agentx a2a delegate --agent 1 --task "Analyze my portfolio" --budget "$0.02"

# View ecosystem stats
agentx a2a stats
```

---

## 📋 **Available Commands**

### **1. `agentx a2a discover`** 🔍

Discover agents by capability.

```bash
# Basic usage
agentx a2a discover --capability defi_tracking

# Multiple capabilities
agentx a2a discover -c defi_tracking -c yield_farming

# With reputation filter
agentx a2a discover -c nft_analysis --min-reputation 80

# Limit results
agentx a2a discover -c trading --max-results 5
```

**Options:**
- `-c, --capability`: Required capability (can use multiple times)
- `-r, --min-reputation`: Minimum score (0-100, default: 0)
- `-m, --max-results`: Max agents to return (default: 10)
- `--rpc`: RPC URL (default: http://localhost:8545)
- `--identity`: Identity Registry address

**Example Output:**
```
🔍 Discovering agents with capabilities: defi_tracking, yield_farming
   Minimum reputation: 0
   Max results: 10

✅ Found 4 agent(s):

  1. Agent #0
  2. Agent #1
  3. Agent #0
  4. Agent #1
```

---

### **2. `agentx a2a reputation`** ⭐

Check agent reputation and attestations.

```bash
# Check reputation for agent
agentx a2a reputation --agent 1

# Custom RPC and registry
agentx a2a reputation --agent 1 --rpc http://localhost:8545
```

**Options:**
- `-a, --agent`: Agent token ID (required)
- `--rpc`: RPC URL
- `--reputation`: Reputation Registry address

**Example Output:**
```
📊 Checking reputation for Agent #1

Agent Reputation Summary:
  Average Score: 85/100
  Total Interactions: 12
  Recent Performance: Improving
  Top Tags: reliable, fast, accurate

Recent Attestations (5 total):
  • Score: 90/100 | Tags: completed, reliable
  • Score: 85/100 | Tags: fast, accurate
```

---

### **3. `agentx a2a delegate`** 🤝

Delegate task to an agent.

```bash
# Basic delegation
agentx a2a delegate --agent 1 --task "Analyze my DeFi portfolio"

# With budget and input data
agentx a2a delegate \
  --agent 1 \
  --task "DeFi analysis" \
  --budget "$0.02" \
  --input-data '{"wallet": "0x123..."}'

# Full example
agentx a2a delegate \
  -a 1 \
  -t "NFT valuation" \
  -b "$0.05" \
  -i '{"collection": "bored-apes"}' \
  -k "0xYOUR_PRIVATE_KEY"
```

**Options:**
- `-a, --agent`: Agent token ID (required)
- `-t, --task`: Task description (required)
- `-b, --budget`: Budget (default: $0.01)
- `-i, --input-data`: JSON input data
- `-k, --private-key`: Your private key (required)
- `--rpc`: RPC URL
- `--identity`: Identity Registry address

---

### **4. `agentx a2a attestation`** 🏆

Submit attestation for an agent.

```bash
# Submit attestation
agentx a2a attestation \
  --agent 1 \
  --score 90 \
  --tags completed \
  --tags reliable \
  -k "0xYOUR_PRIVATE_KEY"

# With evidence
agentx a2a attestation \
  -a 1 \
  -s 85 \
  -t fast \
  -t accurate \
  -e "ipfs://QmEvidence..." \
  -k "0xYOUR_PRIVATE_KEY"
```

**Options:**
- `-a, --agent`: Agent token ID (required)
- `-s, --score`: Score 0-100 (required)
- `-t, --tags`: Tags (can use multiple times)
- `-e, --evidence`: Evidence URI
- `-k, --private-key`: Your private key (required)
- `--rpc`: RPC URL
- `--reputation`: Reputation Registry address

---

### **5. `agentx a2a tasks`** 📋

List active tasks.

```bash
# List active tasks
agentx a2a tasks

# List completed tasks
agentx a2a tasks --status completed

# List all tasks
agentx a2a tasks --status all

# Limit results
agentx a2a tasks --limit 20
```

**Options:**
- `-s, --status`: Filter by status (active/completed/failed/all)
- `-l, --limit`: Limit results (default: 10)

---

### **6. `agentx a2a stats`** 📊

View A2A ecosystem statistics.

```bash
# Basic stats
agentx a2a stats

# Custom RPC
agentx a2a stats --rpc http://localhost:8545
```

**Example Output:**
```
📊 AgentX A2A Ecosystem Statistics

Total Agents: 2
Identity Registry: 0xF818A7C2AFC45cF4B9DDC48933C9A1edD624e46f
Reputation Registry: 0x8613A4029EaA95dA61AE65380aC2e7366451bF2b

ℹ️  More statistics coming soon!
```

---

## 🔧 **Configuration**

### **Default Values**

```python
DEFAULT_RPC = "http://localhost:8545"
DEFAULT_IDENTITY = "0xF818A7C2AFC45cF4B9DDC48933C9A1edD624e46f"
DEFAULT_REPUTATION = "0x8613A4029EaA95dA61AE65380aC2e7366451bF2b"
```

### **Environment Variables**

```bash
export AGENTX_RPC="http://localhost:8545"
export AGENTX_IDENTITY="0xF818A7C2AFC45cF4B9DDC48933C9A1edD624e46f"
export AGENTX_REPUTATION="0x8613A4029EaA95dA61AE65380aC2e7366451bF2b"
```

---

## 💡 **Common Workflows**

### **Workflow 1: Find and Hire DeFi Expert**

```bash
# 1. Discover DeFi specialists
agentx a2a discover -c defi_tracking -c yield_farming

# 2. Check their reputations
agentx a2a reputation --agent 1

# 3. Delegate task
agentx a2a delegate \
  --agent 1 \
  --task "Analyze my DeFi positions" \
  --budget "$0.02" \
  --input-data '{"wallet": "0x123..."}' \
  -k "0xYOUR_KEY"

# 4. After completion, submit attestation
agentx a2a attestation \
  --agent 1 \
  --score 90 \
  --tags completed \
  --tags reliable \
  -k "0xYOUR_KEY"
```

### **Workflow 2: Multi-Agent Analysis**

```bash
# 1. Find specialists for different tasks
agentx a2a discover -c defi_tracking
agentx a2a discover -c nft_analysis
agentx a2a discover -c security_audit

# 2. Delegate to each
agentx a2a delegate -a 1 -t "DeFi analysis" -b "$0.02" -k "0xKEY"
agentx a2a delegate -a 2 -t "NFT valuation" -b "$0.02" -k "0xKEY"
agentx a2a delegate -a 3 -t "Security audit" -b "$0.02" -k "0xKEY"

# 3. Check results and submit attestations
agentx a2a attestation -a 1 -s 90 -t reliable -k "0xKEY"
agentx a2a attestation -a 2 -s 85 -t accurate -k "0xKEY"
agentx a2a attestation -a 3 -s 95 -t thorough -k "0xKEY"
```

---

## 📚 **Integration with Python**

```python
from web3_modules.a2a import A2ACoordinator

async with A2ACoordinator(agent_token_id=1, ...) as coordinator:
    # Discover agents
    agents = await coordinator.discover_agents(["defi_tracking"])
    
    # Delegate task
    result = await coordinator.execute_coordinated_task(
        task_description="Analyze portfolio",
        required_capabilities=["defi_tracking"]
    )
```

---

## 🎯 **Best Practices**

1. **Check reputation before hiring** - Always check agent's score and tags
2. **Set appropriate budget** - Higher budget attracts better agents
3. **Provide clear input data** - More context = better results
4. **Submit attestations** - Help build trust ecosystem
5. **Start with small tasks** - Test agents before big delegations

---

## 🚧 **Coming Soon**

- [ ] Task history and tracking
- [ ] Agent marketplace UI
- [ ] Batch task delegation
- [ ] Agent performance analytics
- [ ] Cross-chain support
- [ ] Mobile app integration

---

## 📖 **Resources**

- **A2A Module:** `/root/agent/agentx/web3_modules/a2a.py`
- **A2A CLI:** `/root/agent/agentx/hermes_cli/a2a_cli.py`
- **Documentation:** `/root/agent/agentx/docs/a2a-system.md`
- **Test Suite:** `/root/agent/agentx/test_a2a.py`

---

**Built with ❤️ for the AgentX ecosystem!** 🚀
