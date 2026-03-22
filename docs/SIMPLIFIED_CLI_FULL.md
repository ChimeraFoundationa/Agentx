# AgentX Simplified CLI - Full Implementation

Complete guide to using the simplified AgentX CLI with full delegate and attest functionality.

---

## 🚀 **Quick Start**

```bash
# Show help
agentx

# Discover agents
agentx discover defi_tracking

# Check reputation
agentx reputation 0

# Delegate task with auto-attestation
agentx delegate 0 "Analyze my portfolio" -k "0xYOUR_KEY"

# Submit manual attestation
agentx attest 0 90 -t completed -t reliable -k "0xYOUR_KEY"

# View stats
agentx stats
```

---

## 📋 **Commands**

### **1. `agentx discover <capability>`** 🔍

Find agents by capability.

```bash
# Basic
agentx discover defi_tracking

# With filters
agentx discover nft_analysis --min-score 80 --limit 5

# Multiple (use Python API)
python3 -c "from web3_modules.erc8004.identity import ERC8004Identity; i=ERC8004Identity('http://localhost:8545'); i.set_registry_address('0x...'); print(i.discover_agents(['defi', 'nft']))"
```

**Options:**
- `--min-score, -m`: Minimum reputation (0-100)
- `--limit, -l`: Max results (default: 10)
- `--rpc`: Custom RPC URL

---

### **2. `agentx reputation <agent_id>`** ⭐

Check agent's reputation and attestations.

```bash
# Basic
agentx reputation 0

# Custom RPC
agentx reputation 0 --rpc http://localhost:8545
```

**Output:**
```
📊 Agent #0 Reputation
========================================
  Score: 90/100
  Interactions: 5
  Performance: Improving
  Tags: completed, reliable, fast
```

---

### **3. `agentx delegate <agent_id> <task>`** 🤝

Delegate task to agent with **auto-attestation**.

```bash
# Basic
agentx delegate 0 "Analyze DeFi portfolio" -k "0xYOUR_KEY"

# With budget and input
agentx delegate 0 "DeFi analysis" \
  --budget "$0.02" \
  --input '{"wallet": "0x123..."}' \
  -k "0xYOUR_KEY"
```

**Options:**
- `--budget, -b`: Task budget (default: $0.01)
- `--input, -i`: JSON input data
- `--key, -k`: Your private key (required)
- `--rpc`: Custom RPC URL

**Flow:**
1. Task delegated to agent
2. Agent executes task
3. **Auto-attestation submitted** (if successful)
4. Score calculated based on performance
5. TX hash returned

**Example Output:**
```
🤝 Delegating to Agent #0
   Task: Analyze portfolio
   Budget: $0.01

⏳ Executing task...

✅ Task completed!
   Success: True
   Execution time: 2.34s

⭐ Submitting auto-attestation...
   Score: 95/100
   Tags: completed, fast, high_quality
   TX: 0x...
```

---

### **4. `agentx attest <agent_id> <score>`** 🏆

Submit manual attestation for agent.

```bash
# Basic
agentx attest 0 90 -k "0xYOUR_KEY"

# With tags
agentx attest 0 85 -t completed -t reliable -k "0xYOUR_KEY"

# With evidence
agentx attest 0 95 \
  -t accurate \
  -t thorough \
  -e "ipfs://QmEvidence..." \
  -k "0xYOUR_KEY"
```

**Options:**
- `--tags, -t`: Tags (can use multiple)
- `--evidence, -e`: Evidence URI (IPFS/HTTP)
- `--key, -k`: Your private key (required)
- `--rpc`: Custom RPC URL

**Score Guidelines:**
- 90-100: Excellent (fast, accurate, reliable)
- 75-89: Good (completed task well)
- 60-74: Average (completed with issues)
- 0-59: Poor (failed or very slow)

**Example Output:**
```
⭐ Attesting Agent #0
   Score: 90/100
   Tags: completed, reliable

✅ Attestation submitted!
   Agent: #0
   Score: 90/100
   Tags: completed, reliable
   TX: 0x474a97a79bd3738f2999beae7d343fa56e8b418baa81923d5f1db930c0e34a38
```

---

### **5. `agentx stats`** 📊

View ecosystem statistics.

```bash
agentx stats
```

**Output:**
```
📊 AgentX Ecosystem Stats
========================================
  Total Agents: 2
  Network: Anvil Testnet
  Identity: 0xF818A7C2AFC45cF4B9...
```

---

### **6. `agentx agents`** 📋

List all registered agents.

```bash
agentx agents

# With capability filter (coming soon)
agentx agents --capability defi_tracking
```

---

## 💡 **Common Workflows**

### **Workflow 1: Find and Hire Agent**

```bash
# 1. Discover agents
agentx discover defi_tracking

# 2. Check reputation
agentx reputation 0

# 3. Delegate task (auto-attestation enabled)
agentx delegate 0 "Analyze my DeFi positions" \
  --input '{"wallet": "0x123..."}' \
  -k "0xYOUR_KEY"

# 4. Verify attestation was submitted
agentx reputation 0
```

---

### **Workflow 2: Manual Attestation**

```bash
# After working with agent, submit attestation
agentx attest 0 95 \
  -t completed \
  -t fast \
  -t accurate \
  -k "0xYOUR_KEY"
```

---

### **Workflow 3: Multi-Agent Task**

```bash
# 1. Find specialists
agentx discover defi_tracking
agentx discover nft_analysis

# 2. Delegate to each
agentx delegate 0 "DeFi analysis" -k "0xKEY"
agentx delegate 1 "NFT valuation" -k "0xKEY"

# 3. Attest both
agentx attest 0 90 -t reliable -k "0xKEY"
agentx attest 1 85 -t good -k "0xKEY"
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

## 🎯 **Auto-Attestation System**

When you delegate a task, auto-attestation is **automatically submitted** if task succeeds.

**Scoring Factors:**
- **Success/Failure**: ±30 points
- **Response Time**: ±15 points (faster = better)
- **Accuracy**: ±15 points (higher = better)
- **Complexity**: ±10 points (bonus for hard tasks)
- **Past Performance**: ±10 points

**Score Calculation:**
```python
base_score = 50

if success:
    base_score += 30

if response_time < 2s:
    base_score += 15

if accuracy >= 0.95:
    base_score += 15

# ... more factors

final_score = max(0, min(100, base_score))
```

**Auto-Submit Rules:**
- Score >= 50: Auto-submit
- Score < 50: Requires manual review
- Configurable via `AttestationConfig`

---

## 📊 **Test Results**

```bash
# Test attest command
$ agentx attest 0 90 -t completed -t reliable -k "0xKEY"

⭐ Attesting Agent #0
   Score: 90/100
   Tags: completed, reliable

✅ Attestation submitted!
   Agent: #0
   Score: 90/100
   Tags: completed, reliable
   TX: 0x474a97a79bd3738f2999beae7d343fa56e8b418baa81923d5f1db930c0e34a38
```

**✅ Attestation working!**

---

## 🚧 **Coming Soon**

- [ ] Full task execution (MCP integration)
- [ ] x402 payment for delegation
- [ ] Task history tracking
- [ ] Agent search by multiple capabilities
- [ ] Batch attestation
- [ ] Agent marketplace UI

---

## 📚 **Resources**

- **CLI Module:** `/root/agent/agentx/hermes_cli/agentx_cli.py`
- **A2A Module:** `/root/agent/agentx/web3_modules/a2a.py`
- **Auto-Attestation:** `/root/agent/agentx/web3_modules/auto_attestation.py`
- **Test Suite:** `/root/agent/agentx/test_auto_features.py`

---

**Built with ❤️ for AgentX!** 🚀
