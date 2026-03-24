#!/bin/bash
# AgentX One-Liner Installation Script
# Install AgentX with a single command!
#
# Usage:
#   curl -fsSL https://raw.githubusercontent.com/ChimeraFoundationa/Agentx/main/scripts/install.sh | bash
#
# For Fuji testnet:
#   curl -fsSL https://raw.githubusercontent.com/ChimeraFoundationa/Agentx/main/scripts/install.sh | bash -s -- --network fuji

set -e

# Colors
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m'

# Configuration
AGENTX_DIR="${AGENTX_INSTALL_DIR:-$HOME/.agentx}"
REPO_URL="${AGENTX_REPO_URL:-https://github.com/ChimeraFoundationa/Agentx.git}"
BRANCH="${AGENTX_BRANCH:-main}"
PYTHON_VERSION="3.10"  # Use system Python version
NETWORK="fuji"  # Default network

# Parse arguments
while [[ $# -gt 0 ]]; do
    case $1 in
        --network)
            NETWORK="$2"
            shift 2
            ;;
        --dir)
            AGENTX_DIR="$2"
            shift 2
            ;;
        --branch)
            BRANCH="$2"
            shift 2
            ;;
        --help)
            echo "AgentX Installation Script"
            echo ""
            echo "Usage:"
            echo "  curl -fsSL https://raw.githubusercontent.com/ChimeraFoundationa/Agentx/main/scripts/install.sh | bash"
            echo ""
            echo "Options:"
            echo "  --network <network>  Target network (fuji, base-sepolia, base, ethereum)"
            echo "  --dir <directory>    Installation directory (default: ~/.agentx)"
            echo "  --branch <branch>    Git branch to install (default: main)"
            echo "  --help              Show this help message"
            exit 0
            ;;
        *)
            echo "Unknown option: $1"
            exit 1
            ;;
    esac
done

# Helper functions
log_info() { echo -e "${BLUE}[INFO]${NC} $1"; }
log_success() { echo -e "${GREEN}[SUCCESS]${NC} $1"; }
log_warning() { echo -e "${YELLOW}[WARNING]${NC} $1"; }
log_error() { echo -e "${RED}[ERROR]${NC} $1"; }

# Banner
echo ""
echo "╔═══════════════════════════════════════════════════════════╗"
echo "║                                                           ║"
echo "║   █████╗ ███████╗████████╗███████╗███╗   ███╗             ║"
echo "║  ██╔══██╗██╔════╝╚══██╔══╝██╔════╝████╗ ████║             ║"
echo "║  ███████║███████╗   ██║   █████╗  ██╔████╔██║             ║"
echo "║  ██╔══██║╚════██║   ██║   ██╔══╝  ██║╚██╔╝██║             ║"
echo "║  ██║  ██║███████║   ██║   ███████╗██║ ╚═╝ ██║             ║"
echo "║  ╚═╝  ╚═╝╚══════╝   ╚═╝   ╚══════╝╚═╝     ╚═╝             ║"
echo "║                                                           ║"
echo "║              The Web3 AI Agent Protocol                   ║"
echo "║                                                           ║"
echo "╚═══════════════════════════════════════════════════════════╝"
echo ""

# Install system dependencies (requires sudo)
log_info "Installing system dependencies..."
if command -v apt-get &> /dev/null; then
    sudo apt-get update -qq
    sudo apt-get install -y -qq python3-venv python3-pip git curl
    log_success "System dependencies installed"
elif command -v yum &> /dev/null; then
    sudo yum install -y -q python3-virtualenv python3-pip git curl
    log_success "System dependencies installed"
elif command -v brew &> /dev/null; then
    brew install python git curl --quiet
    log_success "System dependencies installed"
else
    log_warning "Cannot auto-install dependencies. Please install manually."
fi

# Check if running on Windows
if [[ "$OSTYPE" == "msys" || "$OSTYPE" == "win32" ]]; then
    log_error "Native Windows is not supported. Please install WSL2 and run this script there."
    echo "Install WSL2: https://learn.microsoft.com/en-us/windows/wsl/install"
    exit 1
fi

# Check for existing installation
if [ -d "$AGENTX_DIR" ]; then
    log_warning "Existing AgentX installation found at: $AGENTX_DIR"
    read -p "Do you want to continue? This will overwrite the existing installation (y/N): " confirm
    if [[ ! $confirm =~ ^[Yy]$ ]]; then
        log_info "Installation cancelled."
        exit 0
    fi
    rm -rf "$AGENTX_DIR"
fi

# Step 1: Check for Python
log_info "Checking Python installation..."
if command -v python3 &> /dev/null; then
    PYTHON_VERSION_INSTALLED=$(python3 --version | cut -d' ' -f2)
    log_success "Python found: $PYTHON_VERSION_INSTALLED"
else
    log_error "Python 3 not found. Please install Python 3.11 or higher."
    exit 1
fi

# Step 2: Check for git
log_info "Checking git installation..."
if command -v git &> /dev/null; then
    GIT_VERSION=$(git --version | cut -d' ' -f3)
    log_success "Git found: $GIT_VERSION"
else
    log_error "Git not found. Please install git."
    exit 1
fi

# Step 3: Install uv package manager (if not installed)
if ! command -v uv &> /dev/null; then
    log_info "Installing uv package manager..."
    curl -LsSf https://astral.sh/uv/install.sh | sh
    
    # Source the environment
    if [ -f "$HOME/.local/bin/env" ]; then
        source "$HOME/.local/bin/env"
    fi
    
    log_success "uv installed successfully"
else
    log_success "uv already installed"
fi

# Step 4: Clone repository
log_info "Cloning AgentX repository..."
git clone --branch "$BRANCH" "$REPO_URL" "$AGENTX_DIR"
log_success "Repository cloned to $AGENTX_DIR"

# Step 5: Create virtual environment
log_info "Creating virtual environment..."
cd "$AGENTX_DIR"
uv venv venv --python $PYTHON_VERSION
log_success "Virtual environment created"

# Step 6: Install dependencies
log_info "Installing dependencies (this may take a few minutes)..."
source venv/bin/activate
uv pip install -e ".[all,web3]"
log_success "Dependencies installed"

# Step 7: Install Node.js dependencies (for GoldRush MCP)
if command -v node &> /dev/null; then
    log_info "Node.js found, skipping installation..."
else
    log_warning "Node.js not found. Installing for GoldRush MCP..."
    # Install Node.js via nvm or package manager
    if command -v apt &> /dev/null; then
        curl -fsSL https://deb.nodesource.com/setup_20.x | sudo -E bash -
        sudo apt-get install -y nodejs
    elif command -v brew &> /dev/null; then
        brew install node
    fi
    log_success "Node.js installed"
fi

# Step 8: Create configuration directory
log_info "Setting up configuration..."
mkdir -p "$HOME/.agentx"

# Copy network-specific config
case $NETWORK in
    fuji)
        cp config/fuji-config.yaml "$HOME/.agentx/config.yaml"
        log_info "Fuji testnet configuration installed"
        ;;
    base-sepolia|base)
        cp config/base-config.yaml "$HOME/.agentx/config.yaml" 2>/dev/null || cp config/web3-config.yaml "$HOME/.agentx/config.yaml"
        log_info "Base configuration installed"
        ;;
    ethereum)
        cp config/ethereum-config.yaml "$HOME/.agentx/config.yaml" 2>/dev/null || cp config/web3-config.yaml "$HOME/.agentx/config.yaml"
        log_info "Ethereum configuration installed"
        ;;
    *)
        cp config/web3-config.yaml "$HOME/.agentx/config.yaml"
        log_info "Default configuration installed"
        ;;
esac

# Step 9: Add to PATH and configure
log_info "Configuring AgentX..."

# Detect shell
SHELL_NAME=$(basename "$SHELL")
if [[ "$SHELL_NAME" == "bash" ]]; then
    PROFILE="$HOME/.bashrc"
elif [[ "$SHELL_NAME" == "zsh" ]]; then
    PROFILE="$HOME/.zshrc"
elif [[ "$SHELL_NAME" == "fish" ]]; then
    PROFILE="$HOME/.config/fish/config.fish"
else
    PROFILE="$HOME/.profile"
fi

# Add exports to profile
cat >> "$PROFILE" << EOF

# AgentX Configuration
export AGENTX_DIR="$AGENTX_DIR"
export PYTHONPATH="\$AGENTX_DIR:\$PYTHONPATH"
export PATH="\$AGENTX_DIR/venv/bin:\$PATH"

# AgentX Alias
alias agentx="python3 -m hermes_cli.agentx_cli"
EOF

log_success "AgentX configured in $PROFILE"

# Source the profile for current session
if [[ "$SHELL_NAME" == "bash" || "$SHELL_NAME" == "zsh" ]]; then
    source "$PROFILE"
fi

# Step 10: Verify installation
log_info "Verifying installation..."

# Create test script
cat > "$AGENTX_DIR/agentx" << 'TESTSCRIPT'
#!/bin/bash
# AgentX Wrapper Script
AGENTX_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
source "$AGENTX_DIR/venv/bin/activate"
export PYTHONPATH="$AGENTX_DIR:$PYTHONPATH"
python3 -m hermes_cli.agentx_cli "$@"
TESTSCRIPT

chmod +x "$AGENTX_DIR/agentx"

# Test if agentx command works
if "$AGENTX_DIR/agentx" --help &> /dev/null; then
    log_success "AgentX installed successfully!"
else
    # Try alternative method
    if cd "$AGENTX_DIR" && source venv/bin/activate && PYTHONPATH="$AGENTX_DIR" python3 -m hermes_cli.agentx_cli --help &> /dev/null; then
        log_success "AgentX installed successfully!"
    else
        log_error "Installation verification failed. Please check the logs above."
        exit 1
    fi
fi

# Final summary
echo ""
echo "╔═══════════════════════════════════════════════════════════╗"
echo "║                                                           ║"
echo "║  🎉 AgentX installation complete!                         ║"
echo "║                                                           ║"
echo "╚═══════════════════════════════════════════════════════════╝"
echo ""
echo "Installation Details:"
echo "  Directory: $AGENTX_DIR"
echo "  Network: $NETWORK"
echo "  Config: $HOME/.agentx/config.yaml"
echo ""
echo "Next steps:"
echo ""
echo "  1. Restart your shell or run:"
echo "     source $PROFILE"
echo ""
echo "  2. Set your API keys:"
echo "     export OPENROUTER_API_KEY=\"sk-or-...\"  # For AI provider"
echo "     export AGENTX_PRIVATE_KEY=\"0x...\"       # For wallet"
echo ""
echo "  3. Start using AgentX:"
echo "     agentx                    # Show help"
echo "     agentx discover defi      # Find agents"
echo "     agentx stats              # View statistics"
echo ""
echo "  4. Read the documentation:"
echo "     https://github.com/ChimeraFoundationa/Agentx/docs"
echo ""
echo "Support:"
echo "  Discord: https://discord.gg/agentx"
echo "  GitHub:  https://github.com/ChimeraFoundationa/Agentx"
echo ""
