# AgentX One-Liner Installation

Install AgentX with a single command!

---

## 🚀 **Quick Install**

### **Default (Fuji Testnet)**
```bash
curl -fsSL https://raw.githubusercontent.com/ChimeraFoundationa/Agentx/main/scripts/install.sh | bash
```

### **Custom Network**
```bash
# Fuji Testnet
curl -fsSL https://raw.githubusercontent.com/ChimeraFoundationa/Agentx/main/scripts/install.sh | bash -s -- --network fuji

# Base Sepolia
curl -fsSL https://raw.githubusercontent.com/ChimeraFoundationa/Agentx/main/scripts/install.sh | bash -s -- --network base-sepolia

# Base Mainnet
curl -fsSL https://raw.githubusercontent.com/ChimeraFoundationa/Agentx/main/scripts/install.sh | bash -s -- --network base

# Ethereum Mainnet
curl -fsSL https://raw.githubusercontent.com/ChimeraFoundationa/Agentx/main/scripts/install.sh | bash -s -- --network ethereum
```

### **Custom Directory**
```bash
curl -fsSL https://raw.githubusercontent.com/ChimeraFoundationa/Agentx/main/scripts/install.sh | bash -s -- --dir /opt/agentx
```

### **Specific Branch**
```bash
curl -fsSL https://raw.githubusercontent.com/ChimeraFoundationa/Agentx/main/scripts/install.sh | bash -s -- --branch develop
```

---

## 📋 **What the Script Does**

1. ✅ Checks for Python 3.11+
2. ✅ Checks for git
3. ✅ Installs uv package manager
4. ✅ Clones AgentX repository
5. ✅ Creates virtual environment
6. ✅ Installs all dependencies
7. ✅ Installs Node.js (if needed)
8. ✅ Creates configuration directory
9. ✅ Adds AgentX to PATH
10. ✅ Verifies installation

---

## 🔧 **Post-Installation Setup**

### **1. Restart Shell**
```bash
source ~/.bashrc  # or source ~/.zshrc
```

### **2. Set API Keys**
```bash
# AI Provider (OpenRouter recommended)
export OPENROUTER_API_KEY="sk-or-..."

# Wallet (for transactions)
export AGENTX_PRIVATE_KEY="0x..."
```

### **3. Verify Installation**
```bash
agentx --help
```

### **4. Start Using**
```bash
# Show help
agentx

# Discover agents
agentx discover defi_tracking

# View stats
agentx stats

# Check reputation
agentx reputation 0
```

---

## 🎯 **Installation Options**

| Option | Description | Default |
|--------|-------------|---------|
| `--network` | Target network | `fuji` |
| `--dir` | Installation directory | `~/.agentx` |
| `--branch` | Git branch | `main` |
| `--help` | Show help message | - |

### **Available Networks:**
- `fuji` - Avalanche Fuji Testnet (default)
- `base-sepolia` - Base Sepolia Testnet
- `base` - Base Mainnet
- `ethereum` - Ethereum Mainnet

---

## 📊 **System Requirements**

| Requirement | Minimum | Recommended |
|-------------|---------|-------------|
| **OS** | Linux, macOS, WSL2 | Ubuntu 22.04+ |
| **Python** | 3.11 | 3.11+ |
| **RAM** | 2 GB | 4 GB+ |
| **Disk** | 1 GB | 2 GB+ |
| **Git** | Required | Required |

---

## 🐛 **Troubleshooting**

### **"Python not found"**
```bash
# Install Python 3.11
# Ubuntu/Debian
sudo apt update && sudo apt install python3.11 python3.11-venv

# macOS
brew install python@3.11
```

### **"Git not found"**
```bash
# Install git
# Ubuntu/Debian
sudo apt update && sudo apt install git

# macOS
brew install git
```

### **"Permission denied"**
```bash
# Run without sudo (script handles permissions)
curl -fsSL https://raw.githubusercontent.com/ChimeraFoundationa/Agentx/main/scripts/install.sh | bash
```

### **"Installation failed"**
```bash
# Check logs
cat /tmp/agentx-install.log

# Manual installation
git clone https://github.com/ChimeraFoundationa/Agentx.git ~/.agentx
cd ~/.agentx
uv venv venv --python 3.11
source venv/bin/activate
uv pip install -e ".[all,web3]"
```

---

## 🔄 **Update AgentX**

### **Auto Update**
```bash
agentx update
```

### **Manual Update**
```bash
cd ~/.agentx
git pull
source venv/bin/activate
uv pip install -e ".[all,web3]"
```

---

## 🗑️ **Uninstall AgentX**

```bash
# Remove installation
rm -rf ~/.agentx

# Remove from PATH (edit ~/.bashrc or ~/.zshrc)
nano ~/.bashrc  # Remove AgentX lines
source ~/.bashrc
```

---

## 📚 **Additional Resources**

- **Documentation:** `/root/agent/agentx/docs/`
- **GitHub:** https://github.com/ChimeraFoundationa/Agentx
- **Discord:** https://discord.gg/YOUR_DISCORD
- **Fuji Deployment:** `/root/agent/agentx/FUJI_DEPLOYMENT.md`

---

## 🎉 **Quick Start After Installation**

```bash
# 1. Install
curl -fsSL https://raw.githubusercontent.com/ChimeraFoundationa/Agentx/main/scripts/install.sh | bash

# 2. Restart shell
source ~/.bashrc

# 3. Set keys
export OPENROUTER_API_KEY="sk-or-..."
export AGENTX_PRIVATE_KEY="0x..."

# 4. Start using!
agentx discover defi_tracking
```

---

**That's it! One command to install AgentX!** 🚀
