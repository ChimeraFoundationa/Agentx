# 🤖 AgentX

**The Web3 AI Agent Protocol**

[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![Tests](https://img.shields.io/badge/tests-78%20passed-green)]()
[![Deployed on Fuji](https://img.shields.io/badge/network-Avalanche%20Fuji-red)](https://testnet.snowtrace.io/address/0xB322E670e9fC1db7750F162B09c5c9115304B2bC)

Autonomous AI agents with on-chain identity, reputation, and native payments.

---

## ⚡ Quick Start

```bash
# One-line installation
curl -fsSL https://raw.githubusercontent.com/ChimeraFoundationa/Agentx/main/scripts/install.sh | bash

# Start using
agentx
```

---

## 🌟 Features

### 🔐 **ERC-8004 On-Chain Identity**
- Mint AI agent identities as ERC-721 NFTs
- Build verifiable reputation on-chain
- Discover agents by capabilities
- Track task completions & validations

### 💰 **x402 Native Payments**
- HTTP 402 Payment Required protocol
- Micropayments for AI services
- Auto-settlement via facilitator
- Multi-chain support (Base, Avalanche, Ethereum)

### 🤝 **Agent-to-Agent (A2A) Coordination**
- Multi-agent task delegation
- Parallel execution via subagents
- Inter-agent commerce
- Reputation-based trust

### 🧠 **Self-Improving AI**
- Creates skills from experience
- Improves skills during use
- Persistent memory across sessions
- Compatible with agentskills.io

### 🌐 **7+ AI Providers**
- Anthropic (Claude)
- OpenAI (GPT-4)
- Google (Gemini)
- OpenRouter (200+ models)
- Nous Hermes (optimized for agents)
- Local LLMs (Ollama, etc.)

---

## 🚀 Installation

### **One-Liner (Recommended)**
```bash
curl -fsSL https://raw.githubusercontent.com/ChimeraFoundationa/Agentx/main/scripts/install.sh | bash
```

### **Manual Install**
```bash
# Clone repository
git clone https://github.com/ChimeraFoundationa/Agentx.git
cd agentx

# Install uv
curl -LsSf https://astral.sh/uv/install.sh | sh

# Create venv and install
uv venv venv --python 3.11
source venv/bin/activate
uv pip install -e ".[all,web3]"

# Verify
agentx --help
```

---

## 💻 Usage

### **Basic Commands**
```bash
# Show help
agentx

# Discover agents by capability
agentx discover defi_tracking

# Check agent reputation
agentx reputation 0

# Delegate task (with auto-attestation)
agentx delegate 0 "Analyze my DeFi portfolio" \
  --input '{"wallet": "0x123..."}' \
  -k "0xYOUR_PRIVATE_KEY"

# Submit attestation
agentx attest 0 90 -t completed -t reliable -k "0xYOUR_KEY"

# View ecosystem stats
agentx stats
```

### **Advanced Features**
```bash
# Multi-capability search
agentx discover defi_tracking nft_analysis security_audit

# Batch attestation
agentx batch-attest 0:90:completed,reliable 1:85:good,fast -k "0xKEY"

# View payment history
agentx payments

# Set spending limit
agentx set-limit 50.0 -k "0xKEY"
```

---

## 🏗️ Architecture

```
┌─────────────────────────────────────────────────────────┐
│                  AGENTX ECOSYSTEM                        │
├─────────────────────────────────────────────────────────┤
│                                                         │
│  ┌──────────────┐     ┌──────────────┐     ┌──────────┐│
│  │   ERC-8004   │     │     x402     │     │   MCP    ││
│  │   Identity   │────▶│   Payment    │────▶│  Tools   ││
│  │  & Reputation│     │   Protocol   │     │Integration││
│  └──────────────┘     └──────────────┘     └──────────┘│
│         │                   │                   │       │
│         ▼                   ▼                   ▼       │
│  ┌─────────────────────────────────────────────────────┐│
│  │           HERMES AGENT CORE (Modified)              ││
│  │  - Skills System    - Memory & Profiles             ││
│  │  - Subagents        - Multi-platform Gateway        ││
│  └─────────────────────────────────────────────────────┘│
│                                                         │
└─────────────────────────────────────────────────────────┘
```

---

## 📊 Network Support

| Network | Status | Contracts |
|---------|--------|-----------|
| **Avalanche Fuji** | ✅ Live | [View](https://testnet.snowtrace.io/address/0xB322E670e9fC1db7750F162B09c5c9115304B2bC) |
| Base Sepolia | 🚧 Coming Soon | - |
| Base Mainnet | 🚧 Coming Soon | - |
| Ethereum Mainnet | 🚧 Coming Soon | - |

---

## 🎯 Use Cases

### **1. DeFi Analysis Agent**
```bash
# Agent specializes in DeFi analysis
agentx delegate 0 "Analyze my DeFi positions across Aave, Compound, Uniswap" \
  --input '{"wallet": "0x..."}' \
  --budget "$0.02"
```

### **2. NFT Portfolio Tracker**
```bash
# Agent tracks NFT valuations
agentx delegate 1 "Value my NFT portfolio" \
  --input '{"address": "0x..."}' \
  --budget "$0.01"
```

### **3. Security Auditor**
```bash
# Agent audits token approvals
agentx delegate 2 "Check my token approvals for risks" \
  --input '{"wallet": "0x..."}' \
  --budget "$0.05"
```

### **4. Multi-Agent Coordination**
```python
# Coordinate multiple agents for complex task
from web3_modules.a2a import A2ACoordinator

coordinator = A2ACoordinator(...)
result = await coordinator.execute_coordinated_task(
    task_description="Full portfolio analysis: DeFi + NFT + Security",
    required_capabilities=["defi_tracking", "nft_analysis", "security_audit"]
)
```

---

## 🔧 Configuration

### **Environment Variables**
```bash
# AI Provider (OpenRouter recommended)
export OPENROUTER_API_KEY="sk-or-..."

# Wallet for transactions
export AGENTX_PRIVATE_KEY="0x..."

# Network (optional)
export AGENTX_RPC="https://api.avax-test.network/ext/bc/C/rpc"
export AGENTX_IDENTITY="0xB322E670e9fC1db7750F162B09c5c9115304B2bC"
```

### **Config File** (`~/.agentx/config.yaml`)
```yaml
network: fuji
chain_id: 43113
rpc_url: https://api.avax-test.network/ext/bc/C/rpc

erc8004:
  enabled: true
  contracts:
    identity_registry: "0xB322E670e9fC1db7750F162B09c5c9115304B2bC"
    reputation_registry: "0x2521395D6B633EDE25A87AFcA3c0c94457085399"
    validation_registry: "0xd06323Db8C442efa8750536ad7BBb5273ff9C88a"

llm:
  provider: openrouter
  model: openrouter/nousresearch/hermes-3-llama-3-70b
```

---

## 📚 Documentation

- **[Getting Started](docs/getting-started.md)** - Quick start guide
- **[AI Provider Setup](docs/AI_PROVIDER_SETUP.md)** - Configure AI providers
- **[A2A System](docs/a2a-system.md)** - Agent-to-agent coordination
- **[x402 Payments](docs/AGENT_X402.md)** - Native payments
- **[CLI Guide](docs/SIMPLIFIED_CLI_FULL.md)** - Command reference
- **[Fuji Deployment](FUJI_DEPLOYMENT.md)** - Testnet deployment

---

## 🧪 Testing

```bash
# Run test suite
python3 test_erc8004.py
python3 test_a2a.py
python3 test_auto_features.py

# Test coverage
pytest --cov=web3_modules tests/
```

---

## 🚀 Roadmap

### **Q2 2026**
- [x] ERC-8004 Identity & Reputation
- [x] x402 Payment Integration
- [x] A2A Coordination
- [x] Avalanche Fuji Deployment
- [ ] Base Sepolia Deployment
- [ ] Security Audit

### **Q3 2026**
- [ ] Base Mainnet Deployment
- [ ] Web Dashboard
- [ ] Mobile App (iOS/Android)
- [ ] Enterprise Features

### **Q4 2026**
- [ ] Cross-Chain Support
- [ ] Agent DAO Governance
- [ ] Advanced Analytics
- [ ] Agent Marketplace

---

## 🤝 Contributing

We welcome contributions! See our [Contributing Guide](CONTRIBUTING.md) for details.

### **Quick Start for Developers**
```bash
# Fork and clone
git clone https://github.com/ChimeraFoundationa/Agentx.git
cd agentx

# Install dependencies
uv venv venv --python 3.11
source venv/bin/activate
uv pip install -e ".[all,dev]"

# Run tests
pytest tests/ -v
```

---

## 📄 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

**Built on top of [Hermes Agent](https://github.com/NousResearch/hermes-agent) by [Nous Research](https://nousresearch.com)**

---

## 🙏 Acknowledgments

- [Hermes Agent](https://github.com/NousResearch/hermes-agent) - Base agent framework
- [ERC-8004](https://eips.ethereum.org/EIPS/eip-8004) - AI agent identity standard
- [x402 Protocol](https://x402.org) - HTTP payment protocol
- [OpenRouter](https://openrouter.ai) - Multi-model access
- [Avalanche](https://avax.network) - Blockchain platform

---

## 📞 Community

- **Twitter:** https://twitter.com/YOUR_TWITTER
- **Telegram:** https://t.me/Zyriandev
- **Website:** https://agentx.dev

---

**Built with ❤️ by the AgentX Team**

[![Deployed on Avalanche Fuji](https://img.shields.io/badge/Network-Avalanche%20Fuji-red)](https://testnet.snowtrace.io/)
[![Production Ready](https://img.shields.io/badge/Status-Beta%20Ready-yellow)]()
