# AgentX x402 Payment Protocol

Complete implementation of x402 payment protocol for AgentX agents.

---

## 🚀 **Overview**

AgentX x402 enables **autonomous agent-to-agent payments** via HTTP 402 Payment Required protocol.

### **Features:**
- ✅ Automatic micropayments
- ✅ HTTP 402 handling
- ✅ EIP-712 typed data signing
- ✅ Facilitator integration
- ✅ Spending limits
- ✅ Payment history tracking
- ✅ Multi-chain support (Base, Ethereum, etc.)

---

## 🏗️ **Architecture**

```
┌─────────────┐                    ┌─────────────┐
│  Agent A    │                    │  Agent B    │
│  (Client)   │                    │  (Server)   │
└──────┬──────┘                    └──────┬──────┘
       │                                  │
       │  1. Request Service              │
       │─────────────────────────────────>│
       │                                  │
       │  2. 402 + PAYMENT-REQUIRED       │
       │     (price, network, asset)      │
       │<─────────────────────────────────│
       │                                  │
       │  3. Sign Payment (EIP-712)       │
       │                                  │
       │  4. Retry + PAYMENT-SIGNATURE    │
       │─────────────────────────────────>│
       │                                  │
       │  5. Verify & Settle (Facilitator)│
       │                                  │
       │  6. Service + PAYMENT-RESPONSE   │
       │<─────────────────────────────────│
       │                                  │
```

---

## 💻 **Usage**

### **Basic Payment**

```python
from web3_modules.agent_x402 import AgentX402Integration

# Configuration
agent_config = {
    "wallet_address": "0xYourAgentWallet",
    "private_key": "0xYourPrivateKey",
    "rpc_url": "http://localhost:8545",
    "chain_id": 8453,  # Base
    "spending_limit_usd": 10.0
}

# Initialize
integration = AgentX402Integration(agent_config)

# Pay for agent service
result = await integration.pay_for_agent_service(
    service_endpoint="http://agent-service.local/api/analyze",
    service_name="defi_analysis",
    input_data={"wallet": "0x123..."},
    expected_price="$0.01"
)

print(f"Service result: {result}")
```

### **Pay for MCP Tool**

```python
# Pay for MCP tool execution
tool_result = await integration.pay_for_mcp_tool(
    tool_url="http://mcp-server.local/tools/swap",
    tool_name="execute_swap",
    tool_args={
        "token_in": "USDC",
        "token_out": "ETH",
        "amount": "100"
    }
)

print(f"Tool result: {tool_result}")
```

### **CLI Usage**

```bash
# View payment history
agentx payments

# Set spending limit
agentx set-limit 50.0 -k "0xYourKey"

# View spending summary
agentx stats  # Includes payment stats
```

---

## 🔧 **Configuration**

### **Agent Config**

```yaml
# ~/.agentx/config.yaml

x402:
  enabled: true
  chain_id: 8453  # Base mainnet
  rpc_url: https://base-mainnet.g.alchemy.com/v2/YOUR_KEY
  facilitator_url: https://facilitator.payai.network
  
  spending_limits:
    daily_usd: 10.0
    per_transaction_usd: 1.0
  
  accepted_assets:
    - USDC
    - ETH
  
  accepted_networks:
    - eip155:8453    # Base
    - eip155:84532   # Base Sepolia
```

### **Environment Variables**

```bash
export AGENTX_X402_ENABLED=true
export AGENTX_X402_CHAIN_ID=8453
export AGENTX_X402_SPENDING_LIMIT=10.0
```

---

## 📊 **Payment Flow**

### **Step 1: Service Request**

```python
# Agent A requests service from Agent B
response = await http_client.post(
    "http://agent-b.local/api/analyze",
    json={"wallet": "0x123..."}
)
```

### **Step 2: 402 Response**

```http
HTTP/1.1 402 Payment Required
PAYMENT-REQUIRED: eyJwcmljZSI6IjAuMDAxIiwiY3VycmVuY3kiOiJVU0RDIiwi...
Content-Type: application/json
```

### **Step 3: Parse Requirements**

```python
from web3_modules.agent_x402 import AgentX402

x402 = AgentX402(...)

# Decode requirements
requirements_data = x402._decode_base64(payment_required_header)
requirements = PaymentRequirements(**requirements_data)

# requirements contains:
# - price: "$0.001"
# - currency: "USDC"
# - network: "eip155:8453"
# - recipient: "0x..."
# - idempotency_key: "unique-key"
```

### **Step 4: Sign Payment**

```python
# Create EIP-712 typed data
payment_data = x402.create_payment_payload(
    requirements=requirements,
    resource_url="http://agent-b.local/api/analyze"
)

# Sign with agent's wallet
signature = x402.sign_payment(payment_data)

# signature contains:
# - signature: "0x..."
# - payload: {EIP-712 data}
# - signer: "0xAgentWallet"
```

### **Step 5: Submit Payment**

```python
# Retry request with payment signature
response = await http_client.post(
    "http://agent-b.local/api/analyze",
    headers={"PAYMENT-SIGNATURE": signature.signature},
    json={"wallet": "0x123..."}
)
```

### **Step 6: Settlement**

```python
# Submit to facilitator for settlement
payment_response = await x402.submit_to_facilitator(signature)

print(f"Settlement ID: {payment_response.settlement_id}")
print(f"TX Hash: {payment_response.transaction_hash}")
```

---

## 🎯 **EIP-712 Typed Data**

x402 uses EIP-712 for secure payment signing:

```javascript
{
  "types": {
    "EIP712Domain": [
      {"name": "name", "type": "string"},
      {"name": "version", "type": "string"},
      {"name": "chainId", "type": "uint256"},
      {"name": "verifyingContract", "type": "address"}
    ],
    "Payment": [
      {"name": "price", "type": "uint256"},
      {"name": "asset", "type": "address"},
      {"name": "recipient", "type": "address"},
      {"name": "idempotencyKey", "type": "bytes32"},
      {"name": "resource", "type": "string"},
      {"name": "expiration", "type": "uint256"}
    ]
  },
  "primaryType": "Payment",
  "domain": {
    "name": "x402 Payment",
    "version": "1",
    "chainId": 8453,
    "verifyingContract": "0xRecipient"
  },
  "message": {
    "price": 1000,  // 0.001 USDC (6 decimals)
    "asset": "0x833589fCD6eDb6E08f4c7C32D4f71b54bdA02913",
    "recipient": "0xRecipient",
    "idempotencyKey": "0x...",
    "resource": "http://...",
    "expiration": 1234567890
  }
}
```

---

## 💰 **Supported Networks & Assets**

### **Networks:**
- ✅ Base Mainnet (eip155:8453)
- ✅ Base Sepolia (eip155:84532)
- ✅ Ethereum Mainnet (eip155:1)
- ✅ Ethereum Sepolia (eip155:11155111)

### **Assets:**
- ✅ USDC (native on all networks)
- ✅ ETH (for gas)
- ✅ Custom ERC-20 tokens (via address)

---

## 🔒 **Security Features**

### **1. Spending Limits**

```python
# Set daily limit
x402.set_spending_limit(10.0)  # $10/day

# Check before payment
if not x402._check_spending_limit("$0.001"):
    raise ValueError("Payment exceeds limit")
```

### **2. Idempotency Keys**

Prevents double-spending:

```python
import uuid

# Generate unique key for each payment
idempotency_key = str(uuid.uuid4())

# Included in payment signature
# Facilitator rejects duplicate keys
```

### **3. Expiration**

Payments expire after 1 hour by default:

```python
requirements.expires_at = int(time.time()) + 3600  # 1 hour
```

### **4. Signature Verification**

Facilitator verifies:
- ✅ Signature is valid
- ✅ Signer has sufficient balance
- ✅ Idempotency key not used
- ✅ Payment not expired

---

## 📊 **Payment History**

```python
# Get payment history
history = x402.payment_history

for payment in history:
    print(f"Settlement: {payment.settlement_id}")
    print(f"Status: {payment.status}")
    print(f"TX: {payment.transaction_hash}")
    print(f"Timestamp: {payment.timestamp}")
```

### **Spending Summary**

```python
summary = x402.get_spending_summary()

print(f"Spent Today: ${summary['spent_today_usd']}")
print(f"Daily Limit: ${summary['daily_limit_usd']}")
print(f"Remaining: ${summary['remaining_usd']}")
print(f"Total Payments: {summary['total_payments']}")
print(f"Completed: {summary['completed_payments']}")
print(f"Failed: {summary['failed_payments']}")
```

---

## 🎯 **Use Cases**

### **1. Agent Service Payment**

```python
# Pay for DeFi analysis
result = await integration.pay_for_agent_service(
    service_endpoint="http://defi-agent.local/api/analyze",
    service_name="portfolio_analysis",
    input_data={"wallet": "0x123..."},
    expected_price="$0.02"
)
```

### **2. MCP Tool Payment**

```python
# Pay for token swap
result = await integration.pay_for_mcp_tool(
    tool_url="http://mcp.local/tools/swap",
    tool_name="execute_swap",
    tool_args={"token_in": "USDC", "amount": "100"}
)
```

### **3. API Access Payment**

```python
# Pay for data API
data = await x402.pay_for_resource(
    url="https://api.goldrush.dev/v1/balances",
    method="GET",
    headers={"Authorization": "Bearer token"}
)
```

### **4. Content Monetization**

```python
# Pay for premium content
content = await x402.pay_for_resource(
    url="https://content.site.com/premium/article-123",
    method="GET"
)
```

---

## 🚧 **Production Checklist**

- [ ] Deploy facilitator service
- [ ] Configure multi-chain support
- [ ] Add payment webhooks
- [ ] Implement refund logic
- [ ] Add payment analytics
- [ ] Create payment dashboard
- [ ] Add dispute resolution
- [ ] Implement rate limiting
- [ ] Add fraud detection
- [ ] Create payment subscriptions

---

## 📚 **Resources**

- **x402 Spec:** https://x402.org
- **PayAI Facilitator:** https://payai.network
- **Base Network:** https://base.org
- **EIP-712:** https://eips.ethereum.org/EIPS/eip-712

---

## 🎉 **Implementation Complete!**

**Files Created:**
- `web3_modules/agent_x402.py` - Full x402 implementation
- `hermes_cli/agentx_cli_complete.py` - CLI integration
- `docs/AGENT_X402.md` - This documentation

**Features:**
- ✅ Autonomous agent payments
- ✅ HTTP 402 handling
- ✅ EIP-712 signing
- ✅ Facilitator integration
- ✅ Spending limits
- ✅ Payment history
- ✅ Multi-chain support

**AgentX agents can now pay each other autonomously!** 🚀
