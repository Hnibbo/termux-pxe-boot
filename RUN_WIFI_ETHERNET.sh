#!/data/data/com.termux/files/usr/bin/bash
# Ultimate WiFi + Ethernet PXE Boot
# PC on Ethernet + Phone on WiFi = WORKING!

cd "$(dirname "$0")"

# Colors
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
CYAN='\033[0;36m'
MAGENTA='\033[0;35m'
NC='\033[0m'

clear

echo -e "${CYAN}"
cat << "EOF"
╔══════════════════════════════════════════════════════════════════╗
║                                                                  ║
║        ⚡ ULTIMATE WIFI + ETHERNET PXE BOOT ⚡                   ║
║                                                                  ║
║        PC on Ethernet + Phone on WiFi = WORKING!                ║
║                                                                  ║
╚══════════════════════════════════════════════════════════════════╝
EOF
echo -e "${NC}"

echo -e "${MAGENTA}═══════════════════════════════════════════════════════════════════${NC}"
echo -e "${YELLOW}                    YOUR SETUP${NC}"
echo -e "${MAGENTA}═══════════════════════════════════════════════════════════════════${NC}"
echo ""
echo -e "${GREEN}✓${NC} Phone (this device): WiFi connected"
echo -e "${GREEN}✓${NC} PC (target): Ethernet cable connected"
echo -e "${GREEN}✓${NC} Both: Connected to same router"
echo ""
echo -e "${CYAN}This is the TRICKIEST setup, but we've got you covered!${NC}"
echo ""

# Step 1: Check Python
echo -e "${BLUE}[1/5]${NC} Checking Python..."
if command -v python3 &> /dev/null; then
    PYTHON_CMD=python3
    echo -e "${GREEN}✓${NC} Python3 found"
elif command -v python &> /dev/null; then
    PYTHON_CMD=python
    echo -e "${GREEN}✓${NC} Python found"
else
    echo -e "${RED}✗${NC} Python not found!"
    echo "Install with: pkg install python"
    exit 1
fi

# Step 2: Install netifaces (required for network detection)
echo -e "${BLUE}[2/5]${NC} Checking dependencies..."
if $PYTHON_CMD -c "import netifaces" 2>/dev/null; then
    echo -e "${GREEN}✓${NC} netifaces already installed"
else
    echo -e "${YELLOW}⚠${NC} Installing netifaces (required for network detection)..."
    if $PYTHON_CMD -m pip install netifaces 2>/dev/null || pip3 install netifaces 2>/dev/null || pip install netifaces 2>/dev/null; then
        echo -e "${GREEN}✓${NC} netifaces installed successfully"
    else
        echo -e "${RED}✗${NC} Failed to install netifaces"
        echo "Try manually: pip3 install netifaces"
        exit 1
    fi
fi

# Step 3: Detect network
echo -e "${BLUE}[3/5]${NC} Detecting network configuration..."
MY_IP=$(hostname -I 2>/dev/null | awk '{print $1}')
if [ -z "$MY_IP" ]; then
    MY_IP=$(ip addr show | grep 'inet ' | grep -v '127.0.0.1' | head -1 | awk '{print $2}' | cut -d/ -f1)
fi

if [ ! -z "$MY_IP" ]; then
    echo -e "${GREEN}✓${NC} Your phone IP: ${CYAN}${MY_IP}${NC}"
    
    # Extract network
    IFS='.' read -r -a ip_array <<< "$MY_IP"
    NETWORK="${ip_array[0]}.${ip_array[1]}.${ip_array[2]}"
    echo -e "${GREEN}✓${NC} Network: ${CYAN}${NETWORK}.0/24${NC}"
else
    echo -e "${YELLOW}⚠${NC} Could not detect IP address"
    MY_IP="Unknown"
    NETWORK="192.168.1"
fi

# Step 4: Check gateway
echo -e "${BLUE}[4/5]${NC} Checking router connection..."
GATEWAY=$(ip route show default | grep -oP 'via \K[\d.]+' | head -1)
if [ ! -z "$GATEWAY" ]; then
    echo -e "${GREEN}✓${NC} Router/Gateway: ${CYAN}${GATEWAY}${NC}"
    
    # Ping gateway
    if ping -c 1 -W 1 $GATEWAY >/dev/null 2>&1; then
        echo -e "${GREEN}✓${NC} Router is reachable"
    else
        echo -e "${YELLOW}⚠${NC} Router not responding to ping (may be normal)"
    fi
else
    echo -e "${YELLOW}⚠${NC} Gateway not detected"
    GATEWAY="Unknown"
fi

# Step 5: Set permissions
echo -e "${BLUE}[5/5]${NC} Preparing server..."
chmod +x ULTIMATE_WIFI_ETHERNET_FIX.py 2>/dev/null
echo -e "${GREEN}✓${NC} Ready to start"

echo ""
echo -e "${MAGENTA}═══════════════════════════════════════════════════════════════════${NC}"
echo -e "${YELLOW}              ⚠️  CRITICAL ROUTER SETTINGS ⚠️${NC}"
echo -e "${MAGENTA}═══════════════════════════════════════════════════════════════════${NC}"
echo ""
echo -e "${RED}For this setup to work, you MUST configure your router:${NC}"
echo ""
echo -e "${CYAN}📱 Access Router Admin Panel:${NC}"
echo "   • Open browser on phone or PC"
echo "   • Go to: ${YELLOW}http://${GATEWAY}${NC} or ${YELLOW}http://192.168.1.1${NC}"
echo "   • Login (usually admin/admin or admin/password)"
echo ""
echo -e "${CYAN}🔧 Required Settings:${NC}"
echo ""
echo -e "${GREEN}1. DISABLE Client Isolation:${NC}"
echo "   • Look for: 'Client Isolation', 'AP Isolation', 'Network Isolation'"
echo "   • Common locations:"
echo "     - Wireless → Advanced → Client Isolation → ${RED}DISABLE${NC}"
echo "     - WiFi Settings → Advanced → AP Isolation → ${RED}OFF${NC}"
echo "     - Network → LAN → Client Isolation → ${RED}DISABLE${NC}"
echo ""
echo -e "${GREEN}2. VERIFY Same Subnet:${NC}"
echo "   • WiFi and Ethernet should be on same subnet"
echo "   • Check: Both should have IPs like ${NETWORK}.x"
echo "   • If different, enable 'Bridge Mode' or 'Router Mode'"
echo ""
echo -e "${YELLOW}3. OPTIONAL (Recommended):${NC}"
echo "   • Temporarily DISABLE router's DHCP server during PXE boot"
echo "   • This prevents conflicts with our PXE DHCP server"
echo "   • Location: DHCP Settings → DHCP Server → ${YELLOW}DISABLE${NC}"
echo "   • ${RED}IMPORTANT: Re-enable after PXE boot!${NC}"
echo ""

echo -e "${MAGENTA}═══════════════════════════════════════════════════════════════════${NC}"
echo -e "${YELLOW}                   PC BIOS SETUP${NC}"
echo -e "${MAGENTA}═══════════════════════════════════════════════════════════════════${NC}"
echo ""
echo -e "${CYAN}🖥️  On your PC:${NC}"
echo "   1. Restart PC and press ${YELLOW}F2${NC}, ${YELLOW}F12${NC}, ${YELLOW}Del${NC}, or ${YELLOW}Esc${NC}"
echo "   2. Find 'Boot' or 'Boot Options' menu"
echo "   3. Enable ${GREEN}'PXE Boot'${NC} or ${GREEN}'Network Boot'${NC}"
echo "   4. Set Network Boot as ${GREEN}FIRST${NC} boot priority"
echo "   5. Save (usually ${YELLOW}F10${NC}) and reboot"
echo ""

echo -e "${MAGENTA}═══════════════════════════════════════════════════════════════════${NC}"
echo -e "${YELLOW}                 TROUBLESHOOTING TIPS${NC}"
echo -e "${MAGENTA}═══════════════════════════════════════════════════════════════════${NC}"
echo ""
echo -e "${CYAN}If PXE boot doesn't work:${NC}"
echo "   ${RED}1.${NC} Check router client isolation is ${GREEN}DISABLED${NC}"
echo "   ${RED}2.${NC} Verify PC and phone have IPs in same subnet (${NETWORK}.x)"
echo "   ${RED}3.${NC} Try disabling router DHCP temporarily"
echo "   ${RED}4.${NC} Check firewall on router isn't blocking broadcasts"
echo "   ${RED}5.${NC} Try connecting PC to WiFi instead (same network as phone)"
echo ""

# Countdown
echo -e "${GREEN}═══════════════════════════════════════════════════════════════════${NC}"
echo -e "${GREEN}Starting ULTIMATE PXE Server in 10 seconds...${NC}"
echo -e "${GREEN}═══════════════════════════════════════════════════════════════════${NC}"
echo ""
echo -e "${YELLOW}Have you:${NC}"
echo "  • ${CYAN}Disabled Client Isolation on router?${NC}"
echo "  • ${CYAN}Configured PC BIOS for PXE boot?${NC}"
echo "  • ${CYAN}Ensured both are on same subnet?${NC}"
echo ""
echo -e "${RED}Press Ctrl+C to cancel if you need to configure router first${NC}"
echo ""

for i in 10 9 8 7 6 5 4 3 2 1; do
    echo -ne "${YELLOW}Starting in $i...${NC}\r"
    sleep 1
done
echo ""

# Run the ultimate server
echo -e "${GREEN}"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "          🚀 STARTING ULTIMATE WIFI + ETHERNET PXE SERVER"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo -e "${NC}"
echo ""

$PYTHON_CMD ULTIMATE_WIFI_ETHERNET_FIX.py

# Cleanup
echo ""
echo -e "${YELLOW}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
echo -e "${YELLOW}Server stopped${NC}"
echo -e "${YELLOW}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
echo ""
echo -e "${GREEN}Don't forget to re-enable router DHCP if you disabled it!${NC}"
echo ""
