#!/bin/bash
# Termux PXE Boot Launcher

# Set up environment
export PYTHONPATH="${PYTHONPATH}:$(pwd)"
cd "$(dirname "$0")"

# Check if Python is available
if ! command -v python &> /dev/null; then
    echo "❌ Python not found. Please install it:"
    echo "   pkg install python"
    exit 1
fi

# Check if tkinter is available (built into Python in Termux)
if ! python -c "import tkinter" 2>/dev/null; then
    echo "❌ tkinter not found!"
    echo "   Try: pkg install python"
    echo "   (tkinter is included in the python package)"
    exit 1
fi

# Start the working application
echo "⚡ Starting Termux PXE Boot..."
echo "🐧 Working Network Boot Server"
echo "================================"
python working_pxe_boot.py
