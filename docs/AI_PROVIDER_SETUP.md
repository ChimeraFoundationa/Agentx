# 🤖 AgentX AI Provider Setup Guide

Complete guide to configuring and using AI providers with AgentX.

---

## 🚀 **Quick Start (5 Minutes)**

### **Step 1: Choose Your Provider**

| Provider | Best For | Price | Get API Key |
|----------|----------|-------|-------------|
| **Anthropic** | Reasoning, Long context | $$ | [Get Key](https://console.anthropic.com/settings/keys) |
| **OpenAI** | Code, General tasks | $$ | [Get Key](https://platform.openai.com/api-keys) |
| **OpenRouter** | All models (200+) | $-$$$ | [Get Key](https://openrouter.ai/keys) |
| **Google Gemini** | Multimodal, Fast | $ | [Get Key](https://makersuite.google.com/app/apikey) |
| **Nous Hermes** | Agent tasks | $ | Free via OpenRouter |

**Recommended for beginners:** Start with **OpenRouter** (access to all models with one key!)

---

### **Step 2: Set API Key**

#### **Option A: Environment Variable (Recommended)**

```bash
# For Anthropic
export ANTHROPIC_API_KEY="sk-ant-..."

# For OpenAI
export OPENAI_API_KEY="sk-..."

# For OpenRouter (recommended)
export OPENROUTER_API_KEY="sk-or-..."

# For Google Gemini
export GOOGLE_API_KEY="..."

# Make permanent (add to ~/.bashrc or ~/.zshrc)
echo 'export OPENROUTER_API_KEY="sk-or-..."' >> ~/.bashrc
source ~/.bashrc
```

#### **Option B: Config File**

Edit `~/.agentx/config.yaml`:

```yaml
llm:
  provider: openrouter
  model: anthropic/claude-3.5-sonnet
  api_key: "sk-or-..."  # Not recommended (use env vars instead)
```

---

### **Step 3: Test Connection**

```bash
# Check current model
agentx model

# Test with simple query
agentx "Hello! Can you help me with DeFi analysis?"

# Should respond with AI answer
```

---

## 📋 **Provider-Specific Setup**

### **1. Anthropic (Claude)** ⭐ Recommended

**Best for:** Complex reasoning, long documents, analysis

```bash
# Get API key
# Visit: https://console.anthropic.com/settings/keys

# Set key
export ANTHROPIC_API_KEY="sk-ant-..."

# Configure AgentX
agentx model anthropic/claude-sonnet-4-20250514

# Test
agentx "Analyze the risks of providing private keys to AI agents"
```

**Available Models:**
- `claude-sonnet-4-20250514` - Best balance (recommended)
- `claude-3-opus-20240229` - Most powerful
- `claude-3-haiku-20240307` - Fast & cheap

**Pricing:**
- Sonnet: $3/million input tokens
- Opus: $15/million input tokens
- Haiku: $0.25/million input tokens

---

### **2. OpenAI (GPT)**

**Best for:** Code generation, general tasks

```bash
# Get API key
# Visit: https://platform.openai.com/api-keys

# Set key
export OPENAI_API_KEY="sk-..."

# Configure
agentx model openai/gpt-4-turbo

# Test
agentx "Write a Python script to check ERC-20 token balance"
```

**Available Models:**
- `gpt-4-turbo` - Latest GPT-4 (recommended)
- `gpt-4` - Standard GPT-4
- `gpt-3.5-turbo` - Fast & cheap

**Pricing:**
- GPT-4 Turbo: $10/million input tokens
- GPT-4: $30/million input tokens
- GPT-3.5: $0.5/million input tokens

---

### **3. OpenRouter** 🌟 Best Value

**Best for:** Access to ALL models with ONE key

```bash
# Get API key
# Visit: https://openrouter.ai/keys

# Set key
export OPENROUTER_API_KEY="sk-or-..."

# Use Claude via OpenRouter
agentx model openrouter/anthropic/claude-3.5-sonnet

# Use GPT-4 via OpenRouter
agentx model openrouter/openai/gpt-4-turbo

# Use Gemini via OpenRouter
agentx model openrouter/google/gemini-pro

# Use Llama via OpenRouter
agentx model openrouter/meta-llama/llama-3-70b

# Test
agentx "Compare Claude 3.5 vs GPT-4 for code analysis"
```

**Available Providers (200+ models):**
- Anthropic (Claude)
- OpenAI (GPT)
- Google (Gemini)
- Meta (Llama)
- Mistral
- Cohere
- And 195+ more!

**Pricing:**
- Same as direct providers
- Sometimes cheaper due to OpenRouter discounts
- One bill for all providers

---

### **4. Google Gemini**

**Best for:** Multimodal (images + text), fast responses

```bash
# Get API key
# Visit: https://makersuite.google.com/app/apikey

# Set key
export GOOGLE_API_KEY="..."

# Configure
agentx model gemini/gemini-pro

# Test (with image)
agentx "Analyze this chart" --image chart.png
```

**Available Models:**
- `gemini-pro` - Text (recommended)
- `gemini-pro-vision` - Images + text
- `gemini-ultra` - Most powerful (limited access)

**Pricing:**
- Free tier: 60 requests/minute
- Paid: $0.00025 per 1K characters

---

### **5. Nous Hermes** 🎯 Best for Agents

**Best for:** Agent tasks, tool use, A2A coordination

```bash
# Access via OpenRouter (free tier available)
export OPENROUTER_API_KEY="sk-or-..."

# Configure
agentx model openrouter/nousresearch/hermes-3-llama-3-70b

# Test
agentx "Coordinate a multi-agent DeFi analysis task"
```

**Why Hermes for Agents:**
- Trained specifically for agent tasks
- Better tool-calling accuracy
- Optimized for A2A communication
- Lower cost than Claude/GPT-4

**Pricing:**
- ~$0.40/million tokens (via OpenRouter)
- Much cheaper than Claude/GPT-4 for agent work

---

## 🎯 **Model Selection Guide**

### **By Task Type:**

| Task | Recommended Model | Cost | Speed |
|------|------------------|------|-------|
| **Complex Reasoning** | Claude 3.5 Sonnet | $$ | Fast |
| **Code Generation** | GPT-4 Turbo | $$ | Fast |
| **Agent Coordination** | Nous Hermes 3 | $ | Fast |
| **Long Documents** | Claude 3 Opus (200K) | $$$ | Medium |
| **Multimodal** | Gemini Pro Vision | $ | Very Fast |
| **Budget Tasks** | Llama 3 8B | ¢ | Very Fast |
| **Research** | Perplexity (via OpenRouter) | $$ | Fast |

### **By Budget:**

| Budget | Recommended Setup |
|--------|------------------|
| **Free** | Llama 3 (via Groq/OpenRouter free tier) |
| **<$10/month** | Nous Hermes 3 + Llama 3 |
| **$10-50/month** | Claude 3.5 Sonnet + Hermes |
| **$50+/month** | Claude 3.5 + GPT-4 + Hermes |

---

## 💻 **Advanced Configuration**

### **Multi-Provider Setup**

Use different providers for different tasks:

```yaml
# ~/.agentx/config.yaml

llm:
  default: openrouter/anthropic/claude-3.5-sonnet
  
  # Override for specific tasks
  coding: openai/gpt-4-turbo
  analysis: anthropic/claude-3-opus
  agent_tasks: openrouter/nousresearch/hermes-3
  budget: openrouter/meta-llama/llama-3-8b
```

### **Fallback Configuration**

Automatically fallback if primary fails:

```yaml
llm:
  primary: anthropic/claude-sonnet-4
  fallback:
    - openai/gpt-4-turbo
    - openrouter/anthropic/claude-3.5-sonnet
    - openrouter/meta-llama/llama-3-70b
```

### **Custom Endpoints**

Use self-hosted or custom LLM endpoints:

```yaml
llm:
  provider: custom
  endpoint: http://localhost:11434/v1  # Ollama
  model: llama3
  api_key: ""  # Not needed for local
```

---

## 🔧 **Troubleshooting**

### **Common Issues**

#### **1. "API key not set"**

```bash
# Check if key is set
echo $ANTHROPIC_API_KEY

# If empty, set it
export ANTHROPIC_API_KEY="sk-ant-..."

# Make permanent
echo 'export ANTHROPIC_API_KEY="sk-ant-..."' >> ~/.bashrc
source ~/.bashrc
```

#### **2. "Rate limit exceeded"**

```bash
# Switch to different provider
agentx model openrouter/anthropic/claude-3.5-sonnet

# Or use cheaper model for simple tasks
agentx model openrouter/meta-llama/llama-3-8b
```

#### **3. "Model not found"**

```bash
# List available models
agentx model --list

# Check provider status
# Anthropic: https://status.anthropic.com/
# OpenAI: https://status.openai.com/
# OpenRouter: https://status.openrouter.ai/
```

#### **4. "Response too slow"**

```bash
# Use faster model
agentx model openrouter/meta-llama/llama-3-70b

# Or reduce context
agentx --max-tokens 2000 "Your query..."
```

---

## 📊 **Cost Optimization Tips**

### **1. Use Right Model for Task**

```bash
# Complex analysis → Claude 3.5
agentx model anthropic/claude-sonnet-4
agentx "Analyze this smart contract for vulnerabilities..."

# Simple query → Llama 3
agentx model openrouter/meta-llama/llama-3-8b
agentx "What's the weather today?"
```

### **2. Cache Responses**

```yaml
# Enable caching
cache:
  enabled: true
  ttl: 3600  # Cache for 1 hour
```

### **3. Use OpenRouter**

One key for all providers, often cheaper:

```bash
export OPENROUTER_API_KEY="sk-or-..."

# Access Claude, GPT, Gemini with same key
agentx model openrouter/anthropic/claude-3.5-sonnet
agentx model openrouter/openai/gpt-4-turbo
agentx model openrouter/google/gemini-pro
```

### **4. Monitor Usage**

```bash
# Check usage (if supported)
agentx usage

# Set budget alerts
agentx config set budget.monthly 50
```

---

## 🎯 **Best Practices**

### **1. API Key Security**

```bash
# ✅ DO: Use environment variables
export ANTHROPIC_API_KEY="sk-ant-..."

# ❌ DON'T: Hardcode in config files
# llm:
#   api_key: "sk-ant-..."  # BAD!

# ✅ DO: Use .env file (add to .gitignore)
echo "ANTHROPIC_API_KEY=sk-ant-..." >> ~/.agentx/.env
```

### **2. Model Selection**

```bash
# For development/testing → Use cheap models
agentx model openrouter/meta-llama/llama-3-8b

# For production → Use best model
agentx model anthropic/claude-sonnet-4

# For agent tasks → Use Hermes
agentx model openrouter/nousresearch/hermes-3-llama-3-70b
```

### **3. Context Management**

```bash
# Long conversations → Use Claude (200K context)
agentx model anthropic/claude-3-opus

# Short tasks → Use GPT-4 or Hermes
agentx model openai/gpt-4-turbo
```

---

## 📚 **Resources**

### **API Key Links:**
- [Anthropic](https://console.anthropic.com/settings/keys)
- [OpenAI](https://platform.openai.com/api-keys)
- [OpenRouter](https://openrouter.ai/keys)
- [Google Gemini](https://makersuite.google.com/app/apikey)
- [Nous Research](https://nousresearch.com/)

### **Model Comparison:**
- [LMSys Leaderboard](https://chat.lmsys.org/)
- [OpenRouter Model List](https://openrouter.ai/models)
- [Anthropic Models](https://docs.anthropic.com/claude/docs/models-overview)

### **Documentation:**
- [Hermes Agent Docs](https://hermes-agent.nousresearch.com/docs/)
- [AgentX A2A Guide](./a2a-system.md)
- [AgentX CLI Guide](./A2A_CLI_GUIDE.md)

---

## 🚀 **Next Steps**

1. ✅ Choose your provider
2. ✅ Get API key
3. ✅ Set environment variable
4. ✅ Test with simple query
5. ✅ Configure for your use case
6. ✅ Start building with AgentX!

---

**Happy Agent Building!** 🎉

For support: [Discord](https://discord.gg/YOUR_DISCORD) | [GitHub](https://github.com/ChimeraFoundationa/Agentx)
