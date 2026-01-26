#!/bin/bash
set -e

echo "🚀 CAMARA FastMCP Server - Setup Script"
echo "========================================"

# Check Python version
if ! command -v python3 &> /dev/null; then
    echo "❌ Python 3 not found. Please install Python 3.13+"
    exit 1
fi

PYTHON_VERSION=$(python3 --version | cut -d' ' -f2)
echo "✅ Python $PYTHON_VERSION detected"

# Create virtual environment
if [ ! -d "venv" ]; then
    echo "📦 Creating virtual environment..."
    python3 -m venv venv
fi

# Activate venv
source venv/bin/activate

# Install dependencies
echo "📥 Installing dependencies..."
pip install --upgrade pip
pip install -r requirements_fastmcp.txt

# Create .env if not exists
if [ ! -f ".env" ]; then
    echo "📝 Creating .env from template..."
    cp .env.example .env
    echo "⚠️  Please edit .env with your CAMARA credentials!"
fi

echo ""
echo "✅ Setup complete!"
echo ""
echo "📋 Next steps:"
echo "   1. Edit .env with your CAMARA_BASE_URL and CAMARA_API_KEY"
echo "   2. For Claude Desktop: See CLAUDE_SETUP.md"
echo "   3. For server mode: python camara_final_complete.py --server"
echo "   4. For local mode: python camara_final_complete.py"
echo ""
