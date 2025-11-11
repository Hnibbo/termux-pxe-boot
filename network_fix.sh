#!/bin/bash
# Network Setup and Fix for Termux PXE Boot
# Helps configure network for proper PXE communication

set -e

echo "🔧 TERMUX PXE BOOT - NETWORK SETUP"
echo "=================================="

# Check if running in Termux
if [ ! -d "/data/data/com.termux/files/home" ]; then
    echo "❌ This script is designed for Termux on Android"
    echo "   Install Termux from F-Droid or Play Store"
    exit 1
fi

# Get current network info
echo "📡 Checking current network configuration..."

# Check active network interface
echo "🌐 Network Interfaces:"
ip addr show | grep -E '^[0-9]+: ' | while read line; do
    interface=$(echo $line | cut -d: -f2 | tr -d ' ')
    state=$(echo $line | cut -d: -f3)
    echo "   $interface ($state)"
    ip addr show $interface | grep -E 'inet ' | sed 's/^/     /'
done

# Get IP addresses
echo ""
echo "📍 IP Address Information:"
hostname -I 2>/dev/null || echo "   Could not get IP"
echo "   Default gateway:"
ip route | grep default | head -1 | sed 's/^/   /'

# Network connectivity test
echo ""
echo "🔍 Testing network connectivity..."

# Test local subnet
SUBNET=$(ip addr show | grep 'inet ' | grep -v 127.0.0.1 | head -1 | awk '{print $2}' | cut -d/ -f1 | cut -d. -f1-3)
if [ ! -z "$SUBNET" ]; then
    echo "   Testing subnet $SUBNET.x..."
    
    # Test common gateway IPs
    for i in {1..5}; do
        TEST_IP="$SUBNET.$i"
        echo -n "   Testing $TEST_IP..."
        if ping -c 1 -W 1 $TEST_IP >/dev/null 2>&1; then
            echo " ✅ REACHABLE"
        else
            echo " ❌ Not reachable"
        fi
    done
fi

# Network isolation check
echo ""
echo "🔐 Checking for network isolation..."

# Check if we can reach the router admin panel
echo "   Router admin panel tests:"
for router_ip in 192.168.1.1 192.168.0.1 10.0.0.1 192.168.1.254; do
    if ping -c 1 -W 1 $router_ip >/dev/null 2>&1; then
        echo "   ✅ Router reachable at $router_ip"
        ROUTER_IP=$router_ip
        break
    else
        echo "   ❌ Router not reachable at $router_ip"
    fi
done

if [ -z "$ROUTER_IP" ]; then
    echo "   ⚠️  No router found - this might be the issue!"
fi

# Check for other devices on network
echo ""
echo "🖧 Checking for other devices..."
echo "   ARP table:"
ip neigh | grep REACHABLE | while read line; do
    echo "   $line"
done

# Port binding test
echo ""
echo "🔌 Testing PXE server port availability..."

for port in 67 69 8080; do
    if ss -uln | grep ":$port " >/dev/null 2>&1; then
        echo "   Port $port: ⚠️  Already in use"
    else
        echo "   Port $port: ✅ Available"
    fi
done

# Generate solutions
echo ""
echo "💡 RECOMMENDED SOLUTIONS:"
echo "========================"

if [ ! -z "$SUBNET" ]; then
    echo "1. 🏠 ENSURE DEVICES ARE ON SAME SUBNET"
    echo "   Your current subnet: $SUBNET.0/24"
    echo "   Your PC should also be on: $SUBNET.0/24"
    echo ""
fi

echo "2. 📱 ROUTER CONFIGURATION (in browser):"
echo "   • Go to router admin panel (usually $ROUTER_IP)"
echo "   • Look for: 'Client Isolation', 'AP Isolation', or 'Network Isolation'"
echo "   • DISABLE client isolation if found"
echo "   • Make sure 2.4G and 5G networks are not isolated"
echo ""

echo "3. 🔄 ALTERNATIVE SETUP OPTIONS:"
echo "   OPTION A: Move PC to 2.4G WiFi (same as phone)"
echo "   OPTION B: Use WiFi to Ethernet bridge (phone connects to PC)"
echo "   OPTION C: Connect phone to Ethernet using USB OTG + adapter"
echo "   OPTION D: Use router repeater to extend network"
echo ""

echo "4. 🔧 QUICK TEST:"
echo "   Run this on phone: python3 network_diagnostic.py"
echo "   This will show detailed network analysis"
echo ""

echo "5. 🌐 FORCED NETWORK MODE (if supported):"
echo "   In Termux, try: wifi-direct-connection"
echo "   Or use USB tethering with adb reverse"
echo ""

# Create a simple test file
echo "Creating network test file..."
cat > network_test.txt << EOF
NETWORK SETUP TEST RESULTS
==========================
Date: $(date)
Subnet: ${SUBNET:-Unknown}
Router IP: ${ROUTER_IP:-Not found}
Phone IP: $(hostname -I 2>/dev/null || echo "Unknown")

NEXT STEPS:
1. Check if PC IP is in same subnet ($SUBNET.0/24)
2. Test ping from PC to this phone
3. Test ping from phone to PC
4. Check router admin panel for client isolation

To test connectivity:
From PC terminal: ping [phone-ip]
From phone Termux: ping [pc-ip]
EOF

echo ""
echo "📄 Test results saved to: network_test.txt"
echo ""
echo "✅ NETWORK DIAGNOSIS COMPLETE"
echo ""
echo "🚀 Ready to run: ./run_termux.sh"
echo "   But first fix the network isolation issue!"