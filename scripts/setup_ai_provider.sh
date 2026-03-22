#!/bin/bash
# AgentX AI Provider Quick Setup
# Run this script to quickly configure your AI provider

set -e

echo "╔═══════════════════════════════════════════════════════════╗"
echo "║                                                           ║"
echo "║   █████╗ ██╗      █████╗  ██████╗████████╗██╗ ██████╗    ║"
echo "║  ██╔══██╗██║     ██╔══██╗██╔════╝╚══██╔══╝██║██╔═══██╗    ║"
echo "║  ███████║██║     ███████║██║        ██║   ██║██║   ██║    ║"
echo "║  ██╔══██║██║     ██╔══██║██║        ██║   ██║██║   ██║    ║"
echo "║  ██║  ██║███████╗██║  ██║╚██████╗   ██║   ██║╚██████╔╝    ║"
echo "║  ╚═╝  ╚═╝╚══════╝╚═╝  ╚═╝ ╚═════╝   ╚═╝   ╚═╝ ╚═════╝     ║"
echo "║                                                           ║"
echo "║              AI Provider Quick Setup                      ║"
echo "║                                                           ║"
echo "╚═══════════════════════════════════════════════════════════╝"
echo ""

# Create config directory
mkdir -p ~/.agentx

# Menu
echo "Choose your AI provider:"
echo ""
echo "  1) Anthropic (Claude) - Best for reasoning"
echo "  2) OpenAI (GPT-4) - Best for code"
echo "  3) OpenRouter (200+ models) - Best value ⭐"
echo "  4) Google Gemini - Best for multimodal"
echo "  5) Nous Hermes - Best for agents"
echo "  6) Skip (configure manually later)"
echo ""
read -p "Enter choice (1-6): " choice

case $choice in
    1)
        echo ""
        echo "🔑 Anthropic Setup"
        echo "─────────────────────────────────────"
        echo ""
        echo "Get your API key from: https://console.anthropic.com/settings/keys"
        echo ""
        read -p "Enter your Anthropic API key: " api_key
        
        if [ -z "$api_key" ]; then
            echo "❌ API key cannot be empty"
            exit 1
        fi
        
        # Add to .bashrc/.zshrc
        echo "" >> ~/.bashrc
        echo "# AgentX - Anthropic" >> ~/.bashrc
        echo "export ANTHROPIC_API_KEY=\"$api_key\"" >> ~/.bashrc
        
        # Also add to .zshrc if exists
        if [ -f ~/.zshrc ]; then
            echo "" >> ~/.zshrc
            echo "# AgentX - Anthropic" >> ~/.zshrc
            echo "export ANTHROPIC_API_KEY=\"$api_key\"" >> ~/.zshrc
        fi
        
        # Create config
        cat > ~/.agentx/config.yaml << EOF
# AgentX Configuration
llm:
  provider: anthropic
  model: anthropic/claude-sonnet-4-20250514
EOF
        
        echo ""
        echo "✅ Anthropic configured successfully!"
        echo ""
        echo "To activate, run: source ~/.bashrc"
        echo "Then test with: agentx \"Hello!\""
        ;;
        
    2)
        echo ""
        echo "🔑 OpenAI Setup"
        echo "─────────────────────────────────────"
        echo ""
        echo "Get your API key from: https://platform.openai.com/api-keys"
        echo ""
        read -p "Enter your OpenAI API key: " api_key
        
        if [ -z "$api_key" ]; then
            echo "❌ API key cannot be empty"
            exit 1
        fi
        
        # Add to shell config
        echo "" >> ~/.bashrc
        echo "# AgentX - OpenAI" >> ~/.bashrc
        echo "export OPENAI_API_KEY=\"$api_key\"" >> ~/.bashrc
        
        if [ -f ~/.zshrc ]; then
            echo "" >> ~/.zshrc
            echo "# AgentX - OpenAI" >> ~/.zshrc
            echo "export OPENAI_API_KEY=\"$api_key\"" >> ~/.zshrc
        fi
        
        # Create config
        cat > ~/.agentx/config.yaml << EOF
# AgentX Configuration
llm:
  provider: openai
  model: openai/gpt-4-turbo
EOF
        
        echo ""
        echo "✅ OpenAI configured successfully!"
        echo ""
        echo "To activate, run: source ~/.bashrc"
        echo "Then test with: agentx \"Hello!\""
        ;;
        
    3)
        echo ""
        echo "🔑 OpenRouter Setup (Recommended)"
        echo "─────────────────────────────────────"
        echo ""
        echo "Get your API key from: https://openrouter.ai/keys"
        echo "Benefits: Access to 200+ models with ONE key!"
        echo ""
        read -p "Enter your OpenRouter API key: " api_key
        
        if [ -z "$api_key" ]; then
            echo "❌ API key cannot be empty"
            exit 1
        fi
        
        # Add to shell config
        echo "" >> ~/.bashrc
        echo "# AgentX - OpenRouter" >> ~/.bashrc
        echo "export OPENROUTER_API_KEY=\"$api_key\"" >> ~/.bashrc
        
        if [ -f ~/.zshrc ]; then
            echo "" >> ~/.zshrc
            echo "# AgentX - OpenRouter" >> ~/.zshrc
            echo "export OPENROUTER_API_KEY=\"$api_key\"" >> ~/.zshrc
        fi
        
        # Create config
        cat > ~/.agentx/config.yaml << EOF
# AgentX Configuration
llm:
  provider: openrouter
  model: openrouter/anthropic/claude-3.5-sonnet
EOF
        
        echo ""
        echo "✅ OpenRouter configured successfully!"
        echo ""
        echo "You can now use 200+ models:"
        echo "  - Claude: agentx model openrouter/anthropic/claude-3.5-sonnet"
        echo "  - GPT-4:  agentx model openrouter/openai/gpt-4-turbo"
        echo "  - Gemini: agentx model openrouter/google/gemini-pro"
        echo "  - Llama:  agentx model openrouter/meta-llama/llama-3-70b"
        echo ""
        echo "To activate, run: source ~/.bashrc"
        echo "Then test with: agentx \"Hello!\""
        ;;
        
    4)
        echo ""
        echo "🔑 Google Gemini Setup"
        echo "─────────────────────────────────────"
        echo ""
        echo "Get your API key from: https://makersuite.google.com/app/apikey"
        echo ""
        read -p "Enter your Google API key: " api_key
        
        if [ -z "$api_key" ]; then
            echo "❌ API key cannot be empty"
            exit 1
        fi
        
        # Add to shell config
        echo "" >> ~/.bashrc
        echo "# AgentX - Google Gemini" >> ~/.bashrc
        echo "export GOOGLE_API_KEY=\"$api_key\"" >> ~/.bashrc
        
        if [ -f ~/.zshrc ]; then
            echo "" >> ~/.zshrc
            echo "# AgentX - Google Gemini" >> ~/.zshrc
            echo "export GOOGLE_API_KEY=\"$api_key\"" >> ~/.zshrc
        fi
        
        # Create config
        cat > ~/.agentx/config.yaml << EOF
# AgentX Configuration
llm:
  provider: gemini
  model: gemini/gemini-pro
EOF
        
        echo ""
        echo "✅ Google Gemini configured successfully!"
        echo ""
        echo "To activate, run: source ~/.bashrc"
        echo "Then test with: agentx \"Hello!\""
        ;;
        
    5)
        echo ""
        echo "🔑 Nous Hermes Setup"
        echo "─────────────────────────────────────"
        echo ""
        echo "Nous Hermes is optimized for agent tasks!"
        echo "Access via OpenRouter (get key from: https://openrouter.ai/keys)"
        echo ""
        read -p "Enter your OpenRouter API key: " api_key
        
        if [ -z "$api_key" ]; then
            echo "❌ API key cannot be empty"
            exit 1
        fi
        
        # Add to shell config
        echo "" >> ~/.bashrc
        echo "# AgentX - OpenRouter (for Nous Hermes)" >> ~/.bashrc
        echo "export OPENROUTER_API_KEY=\"$api_key\"" >> ~/.bashrc
        
        if [ -f ~/.zshrc ]; then
            echo "" >> ~/.zshrc
            echo "# AgentX - OpenRouter (for Nous Hermes)" >> ~/.zshrc
            echo "export OPENROUTER_API_KEY=\"$api_key\"" >> ~/.zshrc
        fi
        
        # Create config
        cat > ~/.agentx/config.yaml << EOF
# AgentX Configuration
llm:
  provider: openrouter
  model: openrouter/nousresearch/hermes-3-llama-3-70b
EOF
        
        echo ""
        echo "✅ Nous Hermes configured successfully!"
        echo ""
        echo "Best for agent tasks, A2A coordination, and tool use!"
        echo ""
        echo "To activate, run: source ~/.bashrc"
        echo "Then test with: agentx \"Help me coordinate a multi-agent task\""
        ;;
        
    6)
        echo ""
        echo "⚠️  Setup skipped"
        echo ""
        echo "You can configure manually later by:"
        echo "  1. Setting API key: export PROVIDER_API_KEY=\"...\""
        echo "  2. Running: agentx model <provider/model>"
        echo ""
        echo "See docs/AI_PROVIDER_SETUP.md for detailed guide"
        ;;
        
    *)
        echo ""
        echo "❌ Invalid choice"
        exit 1
        ;;
esac

echo ""
echo "╔═══════════════════════════════════════════════════════════╗"
echo "║                                                           ║"
echo "║  📚 Next Steps:                                           ║"
echo "║                                                           ║"
echo "║  1. Run: source ~/.bashrc                                 ║"
echo "║  2. Test: agentx \"Hello!\"                                 ║"
echo "║  3. Read: docs/AI_PROVIDER_SETUP.md                       ║"
echo "║                                                           ║"
echo "╚═══════════════════════════════════════════════════════════╝"
echo ""
