#!/bin/bash
# AUTONOMOUS SETUP SCRIPT - Complete PXE E53 Bypass System
echo "🚀 AUTONOMOUS PXE E53 BYPASS SETUP"
echo "=================================="

# Create project directory
PROJECT_DIR="/opt/ultra-pxe-bypass"
if [ ! -d "$PROJECT_DIR" ]; then
    sudo mkdir -p "$PROJECT_DIR"
fi

cd "$PROJECT_DIR"

# Clone repository
if [ ! -d ".git" ]; then
    echo "📦 Cloning repository..."
    git clone https://github.com/Hnibbo/termux-pxe-boot.git .
fi

# Install dependencies
echo "🔧 Installing dependencies..."

if [ "$EUID" -eq 0 ]; then
    # Root installation
    sudo apt-get update -qq
    sudo apt-get install -y python3 python3-pip iptables bridge-utils git
    pip3 install scapy colorama psutil tqdm requests
else
    # Termux installation
    pkg update -y 2>/dev/null
    pkg install -y python3 git curl 2>/dev/null
    pip3 install psutil colorama 2>/dev/null
fi

# Make scripts executable
chmod +x *.py *.sh

# Create launch scripts
echo "🚀 Creating launch scripts..."

cat > LAUNCH_PXE_BYPASS.sh << 'EOF'
#!/bin/bash
echo "🎯 LAUNCHING PXE E53 BYPASS SYSTEM"
if [ "$EUID" -eq 0 ]; then
    python3 ULTRA_PXE_DEPLOYMENT.py --auto
else
    python3 TERMUX_PXE_BYPASS.py
fi
EOF

cat > LAUNCH_STEROIDS.sh << 'EOF'
#!/bin/bash
echo "💪 LAUNCHING LINUX ON STEROIDS BOOT"
if [ "$EUID" -eq 0 ]; then
    python3 STEROIDS_PXE_BYPASS.py --auto
else
    python3 TERMUX_PXE_BYPASS.py
fi
EOF

chmod +x LAUNCH_*.sh

echo "🎉 SETUP COMPLETE!"
echo "=================="
echo ""
echo "🚀 QUICK LAUNCH COMMANDS:"
echo "  bash LAUNCH_PXE_BYPASS.sh     # Main system"
echo "  bash LAUNCH_STEROIDS.sh       # Linux on Steroids"
echo ""
echo "💪 FEATURES:"
echo "✅ Bypasses router DHCP filtering"
echo "✅ Boots Linux on Steroids with maximum performance"
echo "✅ Works for both Termux and root users"
echo "✅ Complete autonomous deployment"
echo ""
echo "📦 Repository: https://github.com/Hnibbo/termux-pxe-boot"