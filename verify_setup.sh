#!/bin/bash
# Verification script for Suno Prompter implementation
# This script is run by AI assistants before marking implementations complete

set -e

echo "🔍 Suno Prompter Setup Verification"
echo "===================================="
echo ""

# Check Python version
echo "1. Checking Python version..."
PYTHON_VERSION=$(python3 --version | cut -d' ' -f2)
echo "   ✓ Python $PYTHON_VERSION found"
echo ""

# Create virtual environment
echo "2. Creating virtual environment..."
if [ -d "venv" ]; then
    echo "   ℹ venv already exists, skipping creation"
else
    python3 -m venv venv
    echo "   ✓ Virtual environment created"
fi
echo ""

# Activate virtual environment
echo "3. Activating virtual environment..."
source venv/bin/activate
echo "   ✓ Virtual environment activated"
echo ""

# Install dependencies
echo "4. Installing dependencies from requirements.txt..."
pip install --quiet -r requirements.txt
echo "   ✓ Dependencies installed"
echo ""

# Syntax check all Python files
echo "5. Syntax checking Python files..."
python3 -m py_compile app.py config.py agents/chat_agent.py utils/logging.py
echo "   ✓ All Python files compile successfully"
echo ""

# Check imports without running app
echo "6. Checking imports (without running app)..."
python3 << 'PYEOF'
import sys
sys.path.insert(0, '.')

try:
    # Test basic imports
    import streamlit
    print("   ✓ Streamlit imports successfully")

    import agent_framework
    print("   ✓ agent-framework imports successfully")

    import dotenv
    print("   ✓ python-dotenv imports successfully")

    import azure.identity
    print("   ✓ azure-identity imports successfully")

    import nest_asyncio
    print("   ✓ nest-asyncio imports successfully")

except ImportError as e:
    print(f"   ✗ Import error: {e}")
    sys.exit(1)
PYEOF
echo ""

# Test config loading
echo "7. Testing config module..."
python3 << 'PYEOF'
import sys
sys.path.insert(0, '.')
from config import config
print(f"   ✓ Config loaded successfully")
print(f"   - DEBUG: {config.DEBUG}")
print(f"   - LOG_LEVEL: {config.LOG_LEVEL}")
PYEOF
echo ""

# Test agent imports
echo "8. Testing agent module imports..."
python3 << 'PYEOF'
import sys
sys.path.insert(0, '.')
from agents import ChatAgent
print("   ✓ ChatAgent imports successfully")
PYEOF
echo ""

echo "✅ All verification checks passed!"
echo ""
echo "To run the application, ensure .env is configured and run:"
echo "   streamlit run app.py"
echo ""
