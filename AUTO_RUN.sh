#!/data/data/com.termux/files/usr/bin/bash
# Autonomous PXE Boot - Just run and it works
# Fixes PXE-E53 error automatically

cd "$(dirname "$0")"

# Colors
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
CYAN='\033[0;36m'
NC='\033[0m' # No Color

clear

echo -e "${CYAN}"
echo "╔══════════════════════════════════════════════════════════════════╗"
echo "║       ⚡ AUTONOMOUS PXE BOOT - E53 ERROR FIX ⚡                   ║"
echo "║                  Just run and boot your PC                       ║"
echo "╚══════════════════════════════════════════════════════════════════╝"
echo -e "${NC}"

# Step 1: Find Python
echo -e "${BLUE}[1/5]${NC} Finding Python..."
if command -v python3 &> /dev/null; then
    PYTHON_CMD=python3
    echo -e "${GREEN}✓${NC} Python3 found"
elif command -v python &> /dev/null; then
    PYTHON_CMD=python
    echo -e "${GREEN}✓${NC} Python found"
else
    echo -e "${RED}✗${NC} Python not found! Install with: pkg install python"
    exit 1
fi

# Step 2: Check network
echo -e "${BLUE}[2/5]${NC} Checking network configuration..."
MY_IP=$(hostname -I 2>/dev/null | awk '{print $1}')
if [ -z "$MY_IP" ]; then
    MY_IP="Unknown"
    echo -e "${YELLOW}⚠${NC} Could not detect IP address"
else
    echo -e "${GREEN}✓${NC} Your IP: ${MY_IP}"
fi

# Step 3: Check for USB tethering
echo -e "${BLUE}[3/5]${NC} Checking connection type..."
ROUTE_INFO=$(ip route show 2>/dev/null)
if echo "$ROUTE_INFO" | grep -q "192.168.42"; then
    echo -e "${GREEN}✓${NC} USB Tethering detected (192.168.42.x network)"
    USB_TETHER=true
elif echo "$ROUTE_INFO" | grep -q "wlan"; then
    echo -e "${GREEN}✓${NC} WiFi detected"
    USB_TETHER=false
else
    echo -e "${YELLOW}⚠${NC} Unknown connection type"
    USB_TETHER=false
fi

# Step 4: Set permissions
echo -e "${BLUE}[4/5]${NC} Setting up permissions..."
chmod +x FIXED_PXE_BOOT.py 2>/dev/null
chmod +x termux_pxe_boot.py 2>/dev/null
echo -e "${GREEN}✓${NC} Permissions set"

# Step 5: Display instructions
echo ""
echo -e "${CYAN}╔══════════════════════════════════════════════════════════════════╗${NC}"
echo -e "${CYAN}║                     📋 IMPORTANT SETUP                           ║${NC}"
echo -e "${CYAN}╚══════════════════════════════════════════════════════════════════╝${NC}"
echo ""

if [ "$USB_TETHER" = true ]; then
    echo -e "${GREEN}🔌 USB TETHERING MODE${NC}"
    echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
    echo -e "${YELLOW}This is the BEST mode for PXE boot!${NC}"
    echo ""
    echo "✓ Phone connected via USB to PC"
    echo "✓ USB tethering enabled"
    echo "✓ Direct connection = No network isolation"
    echo ""
else
    echo -e "${YELLOW}⚠️  NETWORK MODE${NC}"
    echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
    echo -e "${YELLOW}For best results, consider USB tethering instead${NC}"
    echo ""
    echo "Current setup:"
    echo "• Phone IP: ${MY_IP}"
    echo "• Connection: WiFi/Ethernet"
    echo ""
    echo -e "${CYAN}⚠️ CRITICAL: Your PC MUST be on the SAME NETWORK!${NC}"
    echo ""
    echo "Quick fixes if not working:"
    echo "1. Connect PC to SAME WiFi as phone"
    echo "2. Disable 'Client Isolation' in router settings"
    echo "3. Or use USB tethering (recommended)"
    echo ""
fi

echo -e "${CYAN}📱 ON YOUR PC:${NC}"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "1. Enter BIOS/UEFI (press F2, F12, or Del during boot)"
echo "2. Find 'Boot Options' or 'Boot Menu'"
echo "3. Enable 'PXE Boot' or 'Network Boot'"
echo "4. Set 'Network Boot' as FIRST boot priority"
echo "5. Save settings (usually F10)"
echo "6. Reboot your PC"
echo ""
echo -e "${GREEN}The PXE-E53 error is now FIXED!${NC}"
echo ""

# Countdown
echo -e "${YELLOW}Starting PXE server in 5 seconds...${NC}"
echo "(Press Ctrl+C to cancel)"
for i in 5 4 3 2 1; do
    echo -n "$i... "
    sleep 1
done
echo ""
echo ""

# Run the fixed server
echo -e "${GREEN}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
echo -e "${GREEN}🚀 STARTING FIXED PXE SERVER${NC}"
echo -e "${GREEN}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
echo ""

# Decide which server to run
if [ -f "FIXED_PXE_BOOT.py" ]; then
    echo -e "${CYAN}Running enhanced fixed server...${NC}"
    $PYTHON_CMD FIXED_PXE_BOOT.py
else
    echo -e "${CYAN}Running standard server...${NC}"
    $PYTHON_CMD termux_pxe_boot.py
fi

# Cleanup
echo ""
echo -e "${YELLOW}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
echo -e "${YELLOW}Server stopped${NC}"
echo -e "${YELLOW}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
