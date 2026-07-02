#!/bin/bash

# AI News Aggregator Setup Script

echo "🤖 AI News Aggregator - Setup"
echo "================================"
echo ""

# Check Python version
python_version=$(python3 --version 2>&1 | awk '{print $2}')
echo "✓ Python version: $python_version"

# Check if pip is installed
if ! command -v pip3 &> /dev/null; then
    echo "❌ pip3 is not installed. Please install pip first."
    exit 1
fi

echo "✓ pip3 is available"
echo ""

# Install dependencies
echo "📦 Installing dependencies..."
pip3 install -r requirements.txt --break-system-packages

if [ $? -ne 0 ]; then
    echo "❌ Failed to install dependencies"
    exit 1
fi

echo "✓ Dependencies installed"
echo ""

# Create config file if it doesn't exist
if [ ! -f "config/config.yaml" ]; then
    echo "📝 Creating configuration file..."
    cp config/config.example.yaml config/config.yaml
    echo "✓ Created config/config.yaml"
    echo ""
    echo "⚠️  IMPORTANT: Please edit config/config.yaml and set:"
    echo "   1. Your Obsidian vault path"
    echo "   2. Adjust news sources if desired"
    echo "   3. Configure scoring criteria"
    echo ""
else
    echo "✓ Configuration file already exists"
    echo ""
fi

# Create necessary directories
mkdir -p state/archive
mkdir -p output

echo "✓ Created directory structure"
echo ""

# Check for ANTHROPIC_API_KEY
if [ -z "$ANTHROPIC_API_KEY" ]; then
    echo "⚠️  WARNING: ANTHROPIC_API_KEY environment variable is not set"
    echo "   You'll need to set this before running the aggregator:"
    echo "   export ANTHROPIC_API_KEY='your-api-key-here'"
    echo ""
else
    echo "✓ ANTHROPIC_API_KEY is set"
    echo ""
fi

# Make main.py executable
chmod +x main.py

echo "✅ Setup complete!"
echo ""
echo "Next steps:"
echo "1. Edit config/config.yaml with your settings"
echo "2. Set your Anthropic API key: export ANTHROPIC_API_KEY='your-key'"
echo "3. Run the aggregator: python3 main.py"
echo ""
echo "For help: python3 main.py --help"
