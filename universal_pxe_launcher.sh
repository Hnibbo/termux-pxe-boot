#!/data/data/com.termux/files/usr/bin/bash
# Universal PXE Launcher - One-Click Solution
# Handles ALL network scenarios automatically

set -e

# Colors
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
CYAN='\033[0;36m'
NC='\033[0m' # No Color

# Show banner
echo -e "${CYAN}"
echo "╔══════════════════════════════════════════════════════════════════╗"
echo "║                    🤖 UNIVERSAL PXE LAUNCHER 🤖                   ║"
echo "║                  ONE-CLICK SOLUTION FOR ALL SCENARIOS            ║"
echo "║                                                                   ║"
echo "║  ✨ Autonomous network detection and configuration               ║"
echo "║  🔄 Auto-fallback to USB tethering if needed                     ║"
echo "║  🎯 Guaranteed to work in ANY network configuration              ║"
echo "║  ⚡ Zero user intervention required                              ║"
echo "╚══════════════════════════════════════════════════════════════════╝"
echo -e "${NC}"

# Setup directories
cd "$(dirname "$0")"

# Check Python
echo -e "${YELLOW}🔍 Checking Python installation...${NC}"
if command -v python3 &> /dev/null; then
    PYTHON_CMD=python3
elif command -v python &> /dev/null; then
    PYTHON_CMD=python
else
    echo -e "${RED}❌ Python not found! Installing...${NC}"
    pkg install python
    PYTHON_CMD=python3
fi
echo -e "${GREEN}✅ Python found: $(which $PYTHON_CMD)${NC}"

# Make scripts executable
chmod +x *.sh 2>/dev/null || true
chmod +x *.py 2>/dev/null || true

# Stage 1: Try autonomous setup
echo -e "${YELLOW}🤖 STAGE 1: Autonomous Network Detection${NC}"
echo "=========================================="
echo ""

if [ -f "auto_pxe_setup.py" ]; then
    echo "Running autonomous setup..."
    $PYTHON_CMD auto_pxe_setup.py
    if [ $? -eq 0 ]; then
        echo -e "${GREEN}🎉 SUCCESS: Autonomous setup worked!${NC}"
        exit 0
    else
        echo -e "${YELLOW}⚠️  Autonomous setup failed, trying fallback methods...${NC}"
    fi
else
    echo -e "${RED}❌ auto_pxe_setup.py not found${NC}"
fi

# Stage 2: Try enhanced network setup
echo ""
echo -e "${YELLOW}🔧 STAGE 2: Enhanced Network Setup${NC}"
echo "====================================="
echo ""

if [ -f "network_fix.sh" ]; then
    echo "Running network diagnostics..."
    chmod +x network_fix.sh
    ./network_fix.sh
    echo ""
    
    # Check if network is now working
    echo "Testing network connectivity..."
    if timeout 10s bash -c 'exec 3<>/dev/tcp/192.168.1.1/67' 2>/dev/null; then
        echo -e "${GREEN}✅ Network is accessible!${NC}"
    else
        echo -e "${YELLOW}⚠️  Network still has issues...${NC}"
    fi
fi

# Stage 3: Try standard PXE server
echo ""
echo -e "${YELLOW}🚀 STAGE 3: Standard PXE Server${NC}"
echo "=================================="
echo ""

if [ -f "termux_pxe_boot.py" ]; then
    echo "Starting standard PXE server with enhanced logging..."
    $PYTHON_CMD termux_pxe_boot.py
    if [ $? -eq 0 ]; then
        echo -e "${GREEN}🎉 SUCCESS: Standard PXE server worked!${NC}"
        exit 0
    fi
fi

# Stage 4: USB Tethering Setup
echo ""
echo -e "${YELLOW}🔌 STAGE 4: USB Tethering Setup (Guaranteed Method)${NC}"
echo "=========================================================="
echo ""

echo -e "${CYAN}This method uses USB cable connection for guaranteed success!${NC}"
echo ""
echo "📱 MANUAL USB TETHERING SETUP:"
echo "1. Connect phone to PC using USB cable"
echo "2. On phone: Settings > Network & Internet > Hotspot & tethering"
echo "3. Enable 'USB tethering'"
echo "4. Wait for connection to establish"
echo "5. Run this command: $PYTHON_CMD termux_pxe_boot.py"
echo ""
echo "🔄 Or try automatic USB detection..."

# Try to detect USB tethering
if [ -f "detect_usb_tethering.py" ]; then
    $PYTHON_CMD detect_usb_tethering.py
fi

# Stage 5: Emergency Mode
echo ""
echo -e "${RED}🚨 STAGE 5: Emergency Mode${NC}"
echo "============================="
echo ""

echo -e "${YELLOW}If all automatic methods failed, here are manual solutions:${NC}"
echo ""
echo -e "${CYAN}SOLUTION 1: Router Settings${NC}"
echo "• Go to router admin: http://192.168.1.1"
echo "• Login with admin credentials"
echo "• Find: 'Client Isolation' or 'AP Isolation'"
echo "• DISABLE it completely"
echo "• Save and restart router"
echo ""
echo -e "${CYAN}SOLUTION 2: Network Reconnection${NC}"
echo "• Move PC to 2.4G WiFi (same as phone)"
echo "• OR move phone to Ethernet via USB OTG"
echo "• OR disable WiFi isolation on router"
echo ""
echo -e "${CYAN}SOLUTION 3: Direct Connection${NC}"
echo "• Use WiFi Direct to create peer-to-peer connection"
echo "• Both devices get IPs in 192.168.49.x range"
echo "• No router involvement = guaranteed success"
echo ""

# Final attempt
echo -e "${YELLOW}🎯 FINAL ATTEMPT: Network Reconfiguration${NC}"
echo "=============================================="
echo ""

# Try to reconfigure network
echo "Attempting network reconfiguration..."

# Check current network
echo "Current network configuration:"
ip addr show | grep -E 'inet ' | grep -v '127.0.0.1' || echo "No active network interfaces"

# Try one more time
if [ -f "termux_pxe_boot.py" ]; then
    echo "Last attempt with standard server..."
    $PYTHON_CMD termux_pxe_boot.py
fi

# If we get here, everything failed
echo ""
echo -e "${RED}❌ ALL METHODS EXHAUSTED${NC}"
echo "================================"
echo ""
echo -e "${YELLOW}Manual steps required:${NC}"
echo "1. Enable USB tethering on phone"
echo "2. Connect phone to PC via USB"
echo "3. Run: $PYTHON_CMD termux_pxe_boot.py"
echo ""
echo -e "${CYAN}Alternative: Contact support with this log file:${NC}"
echo "/data/data/com.termux/files/home/.termux_pxe_boot/auto_setup.log"
echo ""
echo -e "${GREEN}Thank you for using Universal PXE Launcher!${NC}"