# AgentX - Getting Started

Welcome to **AgentX** - The Web3 AI Agent Protocol with ERC-8004 Identity and x402 Payments.

This guide will get you up and running in 5 minutes.

---

## 🚀 Quick Start

### 1. Install AgentX

**One-Line Installation:**

```bash
curl -fsSL https://raw.githubusercontent.com/ChimeraFoundationa/Agentx/main/scripts/install.sh | bash
```

**Manual Installation:**

```bash
# Clone repository
git clone https://github.com/ChimeraFoundationa/Agentx.git
cd agentx

# Install uv package manager
curl -LsSf https://astral.sh/uv/install.sh | sh

# Create virtual environment
uv venv venv --python 3.11
source venv/bin/activate

# Install with Web3 dependencies
uv pip install -e ".[all,web3]"

# Verify installation
agentx --help
```

---

## ⚙️ Initial Setup

### 1. Run Setup Wizard

```bash
agentx setup
```

This will guide you through:
- LLM provider configuration
- Wallet setup
- Network selection
- Initial configuration

### 2. Configure Your Wallet

```bash
# Set your wallet address
agentx config set wallet.address 0xYourWalletAddress

# Or edit config file directly
nano ~/.agentx/config.yaml
```

### 3. Register ERC-8004 Identity

Give your agent an on-chain identity:

```bash
agentx identity register \
  --name "MyAgentX" \
  --capabilities defi,nft,trading \
  --description "My personal Web3 AI agent"
```

This will:
- Mint an ERC-721 NFT representing your agent
- Store agent metadata (capabilities, endpoints)
- Enable reputation tracking

---

## 💰 Setting Up x402 Payments

### 1. Configure Payment Settings

Edit `~/.agentx/config.yaml`:

```yaml
x402:
  enabled: true
  facilitator: "https://facilitator.payai.network"
  accepted_networks:
    - "eip155:8453"    # Base mainnet
    - "eip155:84532"   # Base Sepolia
  accepted_assets:
    - "USDC"
    - "ETH"
  pricing:
    api_call: "$0.001"
    tool_execution: "$0.005"
```

### 2. Get Test USDC (for testing)

```bash
# Base Sepolia faucet
# Visit: https://faucet.circle.com/
# Request test USDC on Base Sepolia
```

### 3. Set Spending Limits

```bash
# Limit auto-payments to $10/day
agentx payment limit --set "$10/day"
```

---

## 🛠️ Basic Usage

### Start Interactive CLI

```bash
agentx
```

You'll see the AgentX terminal interface. Try these commands:

### Common Commands

```bash
# Start fresh conversation
/new

# Check available skills
/skills

# Use a Web3 skill
/defi_tracker --wallet 0x...

# Check your agent identity
agentx identity reputation --show

# Check payment balance
agentx payment balance
```

### Example: Track DeFi Portfolio

```bash
# In the AgentX CLI
/defi_tracker --address 0xYourWallet --protocols uniswap,aave,compound
```

### Example: Analyze NFT Portfolio

```bash
/nft_monitor --address 0xYourWallet --collections bored-apes,azuki
```

---

## 🔧 Web3 Commands Reference

### Identity Commands

```bash
# Register new agent identity
agentx identity register --name "MyAgent" --capabilities defi,nft

# View reputation
agentx identity reputation --show

# Discover agents by capability
agentx identity discover --capability defi_tracking

# Submit attestation for another agent
agentx identity attest --agent <token_id> --score 95 --tags "fast,accurate"
```

### Payment Commands

```bash
# Setup x402 payments
agentx payment setup --network base --asset USDC

# Check balance
agentx payment balance --check

# Set spending limit
agentx payment limit --set "$10/day"

# View payment history
agentx payment history --show
```

### Web3 Utilities

```bash
# Connect wallet
agentx web3 wallet --connect

# Switch network
agentx web3 network --switch base

# Configure RPC
agentx web3 rpc --configure
```

---

## 📚 Available Web3 Skills

AgentX comes with pre-built Web3 skills:

| Skill | Description | Command |
|-------|-------------|---------|
| **DeFi Tracker** | Track DeFi positions across protocols | `/defi_tracker` |
| **NFT Monitor** | NFT portfolio tracking & valuation | `/nft_monitor` |
| **Whale Alert** | Monitor large transactions | `/whale_alert` |
| **Airdrop Hunter** | Check airdrop eligibility | `/airdrop_hunter` |
| **Security Auditor** | Token approval security checks | `/security_auditor` |

---

## 🔗 GoldRush MCP Integration

AgentX includes GoldRush MCP for 100+ blockchain data tools:

### Enable GoldRush

```bash
# Set your GoldRush API key
export GOLDRUSH_API_KEY="your_api_key_here"

# Or add to ~/.agentx/config.yaml
goldrush_mcp:
  api_key: "your_api_key_here"
```

### Available GoldRush Tools

- `multichain_balances` - Get balances across chains
- `multichain_transactions` - Transaction history
- `token_balances` - ERC-20 token balances
- `nft_for_address` - NFT holdings
- `historical_token_prices` - Price history
- `gas_prices` - Current gas prices
- `token_approvals` - Check token approvals (security)

---

## 📖 Next Steps

### Learn More

- [ERC-8004 Identity Guide](./erc8004-identity.md)
- [x402 Payments Guide](./x402-payments.md)
- [Web3 Skills Documentation](./web3-skills.md)
- [MCP Integration](./mcp-integration.md)

### Join the Community

- **Discord**: https://discord.gg/YOUR_DISCORD
- **Twitter**: https://twitter.com/agentx_dev
- **Telegram**: https://t.me/agentx_dev

### Contribute

AgentX is open source! Contribute on GitHub:
https://github.com/ChimeraFoundationa/Agentx

---

## ❓ Troubleshooting

### "Command not found: agentx"

Make sure you've sourced your shell profile:

```bash
source ~/.bashrc  # or source ~/.zshrc
```

### "No module named 'web3'"

Reinstall with Web3 dependencies:

```bash
source ~/.agentx/venv/bin/activate
uv pip install -e ".[web3]"
```

### "RPC connection failed"

Check your RPC provider configuration in `~/.agentx/config.yaml`

### "Payment failed: Insufficient balance"

Make sure your wallet has enough USDC/ETH for payments.

---

**Need help?** Join our Discord or open an issue on GitHub.
