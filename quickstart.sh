#!/bin/bash
# Quick start script for yasched

set -e

echo "🎯 yasched Quick Start"
echo "======================"
echo ""

# Check if Python is installed
if ! command -v python3 &> /dev/null; then
    echo "❌ Error: Python 3 is not installed"
    echo "   Please install Python 3.9 or higher"
    exit 1
fi

PYTHON_VERSION=$(python3 -c 'import sys; print(".".join(map(str, sys.version_info[:2])))')
echo "✓ Python $PYTHON_VERSION detected"

# Check if pip is installed
if ! command -v pip3 &> /dev/null && ! command -v pip &> /dev/null; then
    echo "❌ Error: pip is not installed"
    echo "   Please install pip"
    exit 1
fi

echo "✓ pip detected"
echo ""

# Ask user what they want to do
echo "What would you like to do?"
echo "1. Install yasched and dependencies"
echo "2. Run tests"
echo "3. Start web interface"
echo "4. Start daemon"
echo "5. Run example"
echo "6. View documentation"
echo ""

read -p "Enter your choice (1-6): " choice

case $choice in
    1)
        echo ""
        echo "📦 Installing yasched..."
        pip install -e ".[dev,docs]"
        echo ""
        echo "✅ Installation complete!"
        echo "   Run './quickstart.sh' again to use yasched"
        ;;
    
    2)
        echo ""
        echo "🧪 Running tests..."
        export PYTHONPATH=$(pwd):$PYTHONPATH
        pytest -v
        echo ""
        echo "✅ Tests complete!"
        ;;
    
    3)
        echo ""
        echo "🖥️  Starting web interface..."
        echo "   The interface will open at http://localhost:8501"
        echo "   Press Ctrl+C to stop"
        echo ""
        streamlit run app/main.py
        ;;
    
    4)
        echo ""
        echo "🚀 Starting daemon..."
        ./scripts/start_daemon.sh
        ;;
    
    5)
        echo ""
        echo "📝 Running simple example..."
        echo "   Press Ctrl+C to stop after a few executions"
        echo ""
        export PYTHONPATH=$(pwd):$PYTHONPATH
        python3 examples/simple_example.py
        ;;
    
    6)
        echo ""
        echo "📚 Building documentation..."
        mkdocs serve
        ;;
    
    *)
        echo "Invalid choice. Please run the script again."
        exit 1
        ;;
esac
