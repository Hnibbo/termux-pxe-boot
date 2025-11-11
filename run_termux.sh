#!/data/data/com.termux/files/usr/bin/bash
# Termux PXE Boot - Launch Script

cd "$(dirname "$0")"

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

echo -e "${BLUE}⚡ TERMUX PXE BOOT - STEROID EDITION ⚡${NC}"
echo "=============================================="

# Find Python
if command -v python3 &> /dev/null; then
    PYTHON_CMD=python3
elif command -v python &> /dev/null; then
    PYTHON_CMD=python
else
    echo -e "${RED}❌ Python not found!${NC}"
    echo "Install with: pkg install python"
    exit 1
fi

# Check if main file exists
if [ ! -f "termux_pxe_boot.py" ]; then
    echo -e "${RED}❌ termux_pxe_boot.py not found!${NC}"
    exit 1
fi

# Check network connectivity first
echo -e "${YELLOW}🔍 Checking network configuration...${NC}"
if [ -f "network_diagnostic.py" ]; then
    echo "Running network diagnostic..."
    $PYTHON_CMD network_diagnostic.py
    echo ""
fi

# Network connectivity warning
echo -e "${YELLOW}⚠️  NETWORK SETUP VERIFICATION${NC}"
echo "================================"
echo "📱 Your phone IP: $(hostname -I 2>/dev/null || echo "Unknown")"
echo "🖧 For PXE to work, your PC MUST be on the SAME NETWORK as your phone"
echo ""
echo "🔧 QUICK FIXES:"
echo "1. Connect your PC to the SAME WiFi (2.4G or 5G) as your phone"
echo "2. Or connect phone to Ethernet and PC to WiFi (same router)"
echo "3. Check router admin panel: disable 'Client Isolation' or 'AP Isolation'"
echo ""

# Ask user to continue
read -p "Press Enter to start PXE server (after ensuring network connectivity)..."
echo ""

# Run the server
echo -e "${GREEN}🚀 Starting Termux PXE Boot Server...${NC}"
echo "======================================"
echo ""

# Try to start with enhanced logging
if $PYTHON_CMD termux_pxe_boot.py; then
    echo -e "${GREEN}✅ Server stopped normally${NC}"
else
    echo -e "${RED}❌ Server crashed or was interrupted${NC}"
    echo ""
    echo "💡 TROUBLESHOOTING:"
    echo "1. Run: chmod +x network_fix.sh && ./network_fix.sh"
    echo "2. Check network connectivity with: python3 network_diagnostic.py"
    echo "3. Ensure PC and phone are on same subnet"
fi
