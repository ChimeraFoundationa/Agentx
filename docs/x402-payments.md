# x402 Payments Guide

Complete guide to x402 payment protocol integration in AgentX.

---

## 📋 What is x402?

**x402** is an open payment protocol that brings **on-chain payments to HTTP**. It uses the HTTP `402 Payment Required` status code to enable:

- **Micropayments**: Pay per API call, per tool execution
- **No Accounts**: Payment is the gate, no API keys needed
- **Instant Settlement**: ~200ms on Base
- **Stablecoin Native**: USDC, USDT, DAI support

---

## 🎯 Why x402 for AI Agents?

| Use Case | Description |
|----------|-------------|
| **Agent-to-Agent Commerce** | Agents pay each other for services autonomously |
| **Paid API Access** | Monetize your agent's capabilities |
| **Pay-Per-Use Tools** | Charge per tool execution via MCP |
| **Content Monetization** | Sell reports, analysis, insights |

---

## 🚀 Getting Started

### 1. Configure x402

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
    wallet_analysis: "$0.01"
  
  wallet:
    address: "0xYourWalletAddress"
    spending_limit: "$10/day"
```

### 2. Get Test USDC

For testing on Base Sepolia:

1. Visit [Circle Faucet](https://faucet.circle.com/)
2. Request test USDC on Base Sepolia
3. Import wallet to MetaMask

### 3. Setup Wallet

```bash
# Configure wallet
agentx config set wallet.address 0xYourWalletAddress

# Set spending limit
agentx payment limit --set "$10/day"
```

---

## 💰 Payment Flow

```
┌─────────────┐                    ┌─────────────┐
│   CLIENT    │                    │   SERVER    │
└──────┬──────┘                    └──────┬──────┘
       │                                  │
       │  1. HTTP Request (unpaid)        │
       │─────────────────────────────────>│
       │                                  │
       │  2. 402 + PAYMENT-REQUIRED       │
       │     (price, network, asset)      │
       │<─────────────────────────────────│
       │                                  │
       │  3. Parse requirements           │
       │     Sign payment payload         │
       │                                  │
       │  4. Retry + PAYMENT-SIGNATURE    │
       │─────────────────────────────────>│
       │                                  │
       │  5. Verify & Settle payment      │
       │     (via facilitator)            │
       │                                  │
       │  6. 200 + PAYMENT-RESPONSE       │
       │     + Protected Resource         │
       │<─────────────────────────────────│
       │                                  │
```

---

## 🔧 CLI Commands

### Payment Management

```bash
# Setup x402 payments
agentx payment setup --network base --asset USDC

# Check balance
agentx payment balance --check

# Set spending limit
agentx payment limit --set "$10/day"

# View payment history
agentx payment history --show

# Reset spending tracking
agentx payment reset
```

---

## 💻 Python API

### X402 Client (Paying for Services)

```python
from agentx.web3_modules import X402Client

# Initialize client
client = X402Client(
    private_key="0xYOUR_PRIVATE_KEY",
    rpc_url="https://base-mainnet.g.alchemy.com/v2/YOUR_KEY",
    chain_id=8453  # Base mainnet
)

# Fetch paid resource
async def fetch_paid_analysis():
    result = await client.fetch_paid_resource(
        url="http://localhost:8080/api/analyze-wallet",
        method="GET",
        json_data={"address": "0xTargetWallet"}
    )
    return result

# Pay for MCP tool execution
async def pay_for_tool():
    result = await client.pay_for_mcp_tool(
        tool_url="http://localhost:8080/mcp/tools/defi_report",
        tool_name="defi_report",
        tool_args={"wallet": "0xTargetWallet"},
        expected_price="$0.02"
    )
    return result
```

### X402 Server (Accepting Payments)

```python
from agentx.web3_modules import X402Server
from fastapi import FastAPI, Header, HTTPException

# Initialize server
server = X402Server(
    wallet_address="0xYourWalletAddress",
    rpc_url="https://base-mainnet.g.alchemy.com/v2/YOUR_KEY"
)

# Register endpoint with payment
server.register_endpoint(
    method="GET",
    path="/api/analyze-wallet",
    price="$0.01",
    description="Analyze wallet holdings and transactions",
    network="eip155:8453",
    asset="USDC"
)

app = FastAPI()

@app.get("/api/analyze-wallet")
async def analyze_wallet(
    address: str,
    payment_signature: str | None = Header(default=None)
):
    endpoint_key = "GET /api/analyze-wallet"
    
    # Check for payment
    if not payment_signature:
        # Return 402 response
        response = server.create_402_response(endpoint_key)
        raise HTTPException(
            status_code=402,
            detail=response["body"],
            headers={"PAYMENT-REQUIRED": response["headers"]["PAYMENT-REQUIRED"]}
        )
    
    # Verify and settle payment
    payment_result = await server.verify_and_settle(
        signature=payment_signature,
        endpoint_key=endpoint_key,
        resource_url="/api/analyze-wallet"
    )
    
    if not payment_result.get("valid"):
        raise HTTPException(status_code=403, detail="Payment failed")
    
    # Execute actual endpoint logic
    result = {"analysis": f"Wallet analysis for {address}..."}
    
    return result
```

---

## 🛠️ Integrating with MCP

### Paid MCP Tools

```python
# Server-side: Register MCP tool with x402
server.register_endpoint(
    method="POST",
    path="/mcp/tools/defi_tracker",
    price="$0.005",
    description="Track DeFi positions",
    network="eip155:8453",
    asset="USDC"
)

# Client-side: Call paid MCP tool
from agentx.web3_modules import X402Client

client = X402Client(...)

result = await client.pay_for_mcp_tool(
    tool_url="http://localhost:8080/mcp/tools/defi_tracker",
    tool_name="defi_tracker",
    tool_args={"wallet": "0xTargetWallet"}
)
```

---

## 📊 Pricing Examples

| Service | Price | Description |
|---------|-------|-------------|
| **Wallet Analysis** | $0.01 | Basic wallet holdings |
| **DeFi Report** | $0.02 | Full DeFi portfolio |
| **NFT Valuation** | $0.015 | NFT portfolio value |
| **Swap Execution** | $0.10 | Execute DEX swap |
| **Security Audit** | $0.05 | Token approval check |
| **Whale Alert** | $0.005 | Single whale tx alert |

---

## 🔒 Security Considerations

| Risk | Mitigation |
|------|------------|
| **Replay Attacks** | Idempotency keys prevent double-spending |
| **Front-Running** | Use private RPCs for settlement |
| **Key Management** | Spending limits, allowlists |
| **Invalid Payments** | Verify via trusted facilitator |

### Best Practices

```python
# 1. Set spending limits
client.spending_limit_usd = 10.0  # $10/day

# 2. Use allowlists
client.allowlist = [
    "0xTrustedService1",
    "0xTrustedService2"
]

# 3. Log all payments
client.log_payments = True

# 4. Monitor balance
balance = client.get_balance()
if balance < 10.0:  # USDC
    print("Warning: Low balance!")
```

---

## 🏗️ Architecture

```
┌─────────────────────────────────────────────────────────┐
│                    X402 PAYMENT FLOW                     │
├─────────────────────────────────────────────────────────┤
│                                                         │
│  ┌──────────┐      ┌──────────┐      ┌──────────┐      │
│  │  Client  │      │  Server  │      │Facilitator│      │
│  │  (Agent) │      │  (Agent) │      │ (Service) │      │
│  └────┬─────┘      └────┬─────┘      └────┬─────┘      │
│       │                 │                 │             │
│       │  1. Request     │                 │             │
│       │────────────────>│                 │             │
│       │                 │                 │             │
│       │  2. 402 + Terms │                 │             │
│       │<────────────────│                 │             │
│       │                 │                 │             │
│       │  3. Sign Payment│                 │             │
│       │                 │                 │             │
│       │  4. Payment Sig │                 │             │
│       │────────────────>│                 │             │
│       │                 │                 │             │
│       │                 │  5. Verify      │             │
│       │                 │────────────────>│             │
│       │                 │                 │             │
│       │                 │  6. Settle      │             │
│       │                 │────────────────>│             │
│       │                 │                 │             │
│       │                 │  7. Confirm     │             │
│       │                 │<────────────────│             │
│       │                 │                 │             │
│       │  8. Resource    │                 │             │
│       │<────────────────│                 │             │
│       │                 │                 │             │
└─────────────────────────────────────────────────────────┘
```

---

## 📚 Supported Networks

| Network | Chain ID | USDC Address | Status |
|---------|----------|--------------|--------|
| **Base Mainnet** | 8453 | 0x833589f... | ✅ Ready |
| **Base Sepolia** | 84532 | 0x036CbD5... | ✅ Ready |
| **Ethereum** | 1 | 0xA0b86991... | 🚧 Coming |
| **Arbitrum** | 42161 | 0xFF970A61... | 🚧 Coming |

---

## 🚧 Current Status

| Component | Status |
|-----------|--------|
| **X402 Client** | ✅ Implemented |
| **X402 Server** | ✅ Implemented |
| **Facilitator Integration** | ✅ PayAI supported |
| **CLI Commands** | 🚧 In Progress |
| **Auto-Payments** | 🚧 In Progress |
| **Spending Limits** | ✅ Implemented |
| **Allowlists** | ✅ Implemented |

---

## 💡 Use Cases

### 1. Agent Marketplace

```
1. Agent A offers wallet analysis service
2. Sets price: $0.01 per analysis
3. Agent B needs analysis for client
4. Pays via x402 automatically
5. Agent A delivers report
6. Both submit ERC-8004 attestations
```

### 2. Paid API Gateway

```
1. Deploy AgentX with public API
2. Protect endpoints with x402
3. Users pay per request
4. No API key management needed
5. Instant settlement to your wallet
```

### 3. Autonomous Trading

```
1. Agent monitors DEX prices
2. Finds arbitrage opportunity
3. Pays for swap execution via x402
4. Executes trade
5. Profits exceed payment cost
```

---

## 📚 Resources

- [x402 Protocol Spec](https://x402.org)
- [PayAI Facilitator](https://payai.network)
- [Base Network Docs](https://docs.base.org)
- [AgentX Documentation](https://docs.agentx.dev)

---

**Previous:** [ERC-8004 Identity](./erc8004-identity.md)  
**Next:** [Web3 Skills Guide](./web3-skills.md)
