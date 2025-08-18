#!/bin/bash

# GoldenGate PII Scanner Setup Script
echo "🔍 Setting up GoldenGate PII Scanner..."
echo "=" * 50

# Check if virtual environment exists
if [ ! -d "venv" ]; then
    echo "📦 Creating virtual environment..."
    python3 -m venv venv
    if [ $? -ne 0 ]; then
        echo "❌ Failed to create virtual environment"
        echo "Please ensure python3-venv is installed: sudo apt install python3-venv"
        exit 1
    fi
fi

# Activate virtual environment and install dependencies
echo "⚙️  Installing dependencies..."
source venv/bin/activate
pip install -r requirements.txt

if [ $? -ne 0 ]; then
    echo "❌ Failed to install dependencies"
    exit 1
fi

echo ""
echo "✅ Setup complete!"
echo ""
echo "🚀 Starting scanner..."
echo ""

# Auto-activate and run
source venv/bin/activate
python easy_launcher.py