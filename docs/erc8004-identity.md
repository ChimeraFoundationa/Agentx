# ERC-8004 Identity Guide

Complete guide to ERC-8004 identity and reputation management in AgentX.

---

## 📋 What is ERC-8004?

**ERC-8004** is Ethereum's new standard for **AI agent identity and reputation**. It provides:

- **Identity Registry**: Mint your agent as an ERC-721 NFT
- **Reputation Registry**: Track attestations and feedback on-chain
- **Validation Registry**: Record task completion proofs

---

## 🎯 Why ERC-8004?

| Benefit | Description |
|---------|-------------|
| **Portable Identity** | Your agent's identity works across all platforms |
| **Verifiable Reputation** | On-chain attestations prove track record |
| **Trustless Discovery** | Find agents by capabilities and reputation |
| **Accountability** | All interactions recorded on-chain |

---

## 🚀 Getting Started

### 1. Configure ERC-8004

Edit `~/.agentx/config.yaml`:

```yaml
erc8004:
  enabled: true
  network: "base"  # or ethereum, base_sepolia, sepolia
  
  contracts:
    identity_registry: "0x..."  # Deploy after contract deployment
    reputation_registry: "0x..."
    validation_registry: "0x..."
  
  agent:
    name: "MyAgentX"
    auto_register: true
    capabilities:
      - defi_tracking
      - nft_analysis
```

### 2. Register Your Agent

```bash
agentx identity register \
  --name "MyAgentX" \
  --capabilities defi,nft,trading \
  --description "My personal Web3 AI agent"
```

This will:
1. Create an Agent Card (metadata)
2. Upload to IPFS
3. Mint ERC-721 NFT on-chain
4. Return your agent's Token ID

### 3. View Your Identity

```bash
# Show identity info
agentx identity reputation --show

# Get detailed info
agentx identity info --token-id <YOUR_TOKEN_ID>
```

---

## 📖 Key Concepts

### Agent Card

JSON metadata stored off-chain (IPFS/Arweave):

```json
{
  "name": "AgentX",
  "description": "Web3 AI Agent",
  "capabilities": ["defi_tracking", "nft_analysis"],
  "serviceEndpoints": {
    "mcp": "http://localhost:8080/mcp",
    "http": "http://localhost:8080/api"
  },
  "paymentAddress": "0xYourWallet",
  "x402Accepted": true,
  "version": "1.0.0"
}
```

### Attestations

Feedback submitted after interactions:

```python
# Submit attestation
agentx identity attest \
  --agent <TOKEN_ID> \
  --score 95 \
  --tags "fast,accurate,reliable"
```

### Validation Records

Proof of task completion:

```python
# Record validation
agentx identity validate \
  --agent <TOKEN_ID> \
  --task "wallet_analysis" \
  --success true
```

---

## 🔧 CLI Commands

### Identity Management

```bash
# Register new agent
agentx identity register --name "MyAgent" --capabilities defi,nft

# View identity info
agentx identity info --token-id <ID>

# Discover agents by capability
agentx identity discover --capability defi_tracking

# Transfer ownership
agentx identity transfer --token-id <ID> --to 0xAddress
```

### Reputation Management

```bash
# View reputation summary
agentx identity reputation --show

# Submit attestation
agentx identity attest --agent <ID> --score 90 --tags "good"

# Get average score
agentx identity score --token-id <ID>
```

### Validation Management

```bash
# Record task completion
agentx identity validate --agent <ID> --task "swap" --success true

# Get validation history
agentx identity validations --token-id <ID>
```

---

## 💻 Python API

### Register Agent

```python
from agentx.web3_modules import ERC8004Identity

# Initialize
identity = ERC8004Identity(
    rpc_url="https://base-mainnet.g.alchemy.com/v2/YOUR_KEY",
    private_key="0xYOUR_PRIVATE_KEY"
)

# Set registry address
identity.set_registry_address("0xREGISTRY_CONTRACT")

# Register agent
token_id = identity.register_agent(
    agent_name="MyAgentX",
    capabilities=["defi_tracking", "nft_analysis"],
    description="My Web3 AI agent"
)

print(f"Agent registered with Token ID: {token_id}")
```

### Get Reputation

```python
from agentx.web3_modules import ReputationTracker

reputation = ReputationTracker(
    rpc_url="https://base-mainnet.g.alchemy.com/v2/YOUR_KEY",
    private_key="0xYOUR_PRIVATE_KEY"
)

reputation.set_registry_address("0xREPUTATION_CONTRACT")

# Get summary
summary = reputation.get_reputation_summary(token_id)
print(f"Average score: {summary['average_score']}")
print(f"Total interactions: {summary['total_interactions']}")
```

### Submit Attestation

```python
# After agent completes a task
tx_hash = reputation.submit_attestation(
    agent_token_id=token_id,
    interaction_result={
        "success": True,
        "response_time": 2.5,
        "accuracy": 0.98,
        "task": "wallet_analysis"
    },
    custom_tags=["fast", "accurate"]
)

print(f"Attestation submitted: {tx_hash}")
```

---

## 🏗️ Architecture

```
┌─────────────────────────────────────────────────────────┐
│                  ERC-8004 REGISTRIES                     │
├─────────────────────────────────────────────────────────┤
│                                                         │
│  ┌─────────────────┐   ┌─────────────────┐             │
│  │ Identity        │   │ Reputation      │             │
│  │ Registry        │   │ Registry        │             │
│  │ (ERC-721 NFT)   │◀──┤ (Attestations)  │             │
│  └────────┬────────┘   └────────┬────────┘             │
│           │                     │                      │
│           │      ┌──────────────┘                      │
│           │      │                                     │
│           ▼      ▼                                     │
│  ┌─────────────────┐                                   │
│  │ Validation      │                                   │
│  │ Registry        │                                   │
│  │ (Task Proofs)   │                                   │
│  └─────────────────┘                                   │
│                                                         │
└─────────────────────────────────────────────────────────┘
```

---

## 📊 Use Cases

### 1. Agent Marketplace

```
1. User discovers agent via ERC-8004 registry
2. Checks reputation score (85/100) ✓
3. Validates task completion history ✓
4. Hires agent for DeFi analysis
5. Submits attestation after completion
```

### 2. Inter-Agent Coordination

```
1. Agent A needs help with NFT valuation
2. Queries ERC-8004 for NFT specialists
3. Finds Agent B (reputation: 92/100)
4. Delegates task via MCP
5. Both agents record validation
```

### 3. Reputation Building

```
1. New agent registers on ERC-8004
2. Completes tasks for early users
3. Collects positive attestations
4. Reputation score increases
5. Can charge higher fees
```

---

## 🔒 Security Considerations

| Risk | Mitigation |
|------|------------|
| **Fake Attestations** | Require signature from verified addresses |
| **Sybil Attacks** | Weight attestations by attester reputation |
| **Reputation Manipulation** | Time-decay weights, recent performance focus |
| **Privacy** | Store sensitive data off-chain (IPFS/Arweave) |

---

## 🚧 Current Status

| Component | Status |
|-----------|--------|
| **Identity Registry** | ✅ Implemented (placeholder contracts) |
| **Reputation Registry** | ✅ Implemented (placeholder contracts) |
| **Validation Registry** | ✅ Implemented (placeholder contracts) |
| **CLI Commands** | 🚧 In Progress |
| **Auto-Registration** | 🚧 In Progress |
| **Auto-Attestation** | 🚧 In Progress |

---

## 📚 Resources

- [ERC-8004 Specification](https://eips.ethereum.org/EIPS/eip-8004)
- [AgentX Documentation](https://docs.agentx.dev)
- [Nous Research Hermes Agent](https://github.com/NousResearch/hermes-agent)

---

**Next:** [x402 Payments Guide](./x402-payments.md)
