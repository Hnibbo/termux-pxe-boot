#!/data/data/com.termux/files/usr/bin/bash
# Termux PXE Boot - Launch Script

cd "$(dirname "$0")"

# Find Python
if command -v python3 &> /dev/null; then
    PYTHON_CMD=python3
elif command -v python &> /dev/null; then
    PYTHON_CMD=python
else
    echo "❌ Python not found!"
    echo "Install with: pkg install python"
    exit 1
fi

# Check if main file exists
if [ ! -f "termux_pxe_boot.py" ]; then
    echo "❌ termux_pxe_boot.py not found!"
    exit 1
fi

# Run the server
echo ""
echo "🚀 Starting Termux PXE Boot Server..."
echo ""
$PYTHON_CMD termux_pxe_boot.py
