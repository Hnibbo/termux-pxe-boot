#!/data/data/com.termux/files/usr/bin/bash
# Termux PXE Boot - Complete Installation Script
# For Android Termux - No Root Required

set -e

echo ""
echo "⚡ TERMUX PXE BOOT - COMPLETE INSTALLER ⚡"
echo "=========================================="
echo ""

# Colors
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
BLUE='\033[0;34m'
NC='\033[0m'

print_info() { echo -e "${BLUE}ℹ ${NC}$1"; }
print_success() { echo -e "${GREEN}✓${NC} $1"; }
print_warning() { echo -e "${YELLOW}⚠${NC} $1"; }
print_error() { echo -e "${RED}✗${NC} $1"; }

# Check if we're in Termux
if [ ! -d "/data/data/com.termux/files" ]; then
    print_warning "Not running in Termux - some features may not work"
fi

# Update packages
print_info "Updating package lists..."
if command -v pkg &> /dev/null; then
    pkg update -y 2>&1 | grep -v "Warning" || true
    print_success "Package lists updated"
else
    print_warning "pkg command not found - using apt"
    apt update -y 2>&1 | grep -v "Warning" || true
fi

# Install Python if needed
print_info "Checking Python installation..."
if ! command -v python &> /dev/null && ! command -v python3 &> /dev/null; then
    print_info "Installing Python..."
    if command -v pkg &> /dev/null; then
        pkg install -y python || pkg install -y python3
    else
        apt install -y python3
    fi
fi

# Find Python command
if command -v python3 &> /dev/null; then
    PYTHON_CMD=python3
elif command -v python &> /dev/null; then
    PYTHON_CMD=python
else
    print_error "Python installation failed"
    exit 1
fi

print_success "Python found: $($PYTHON_CMD --version)"

# Check Python version
PYTHON_VERSION=$($PYTHON_CMD -c "import sys; print(f'{sys.version_info.major}.{sys.version_info.minor}')")
print_info "Python version: $PYTHON_VERSION"

# Create directories
print_info "Creating directories..."
mkdir -p ~/.termux_pxe_boot/tftp/pxelinux.cfg
mkdir -p ~/.termux_pxe_boot/logs
mkdir -p ~/.termux_pxe_boot/config
print_success "Directories created"

# Set executable permissions
print_info "Setting permissions..."
chmod +x termux_pxe_boot.py 2>/dev/null || true
chmod +x run_termux.sh 2>/dev/null || true
chmod +x install_termux.sh 2>/dev/null || true
print_success "Permissions set"

# Create wrapper script
print_info "Creating launch script..."
cat > run_termux.sh << 'EOFSCRIPT'
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
EOFSCRIPT

chmod +x run_termux.sh
print_success "Launch script created"

# Test installation
print_info "Testing installation..."
if [ -f "termux_pxe_boot.py" ]; then
    if $PYTHON_CMD -c "import socket, threading, struct, json" 2>/dev/null; then
        print_success "All required Python modules available"
    else
        print_warning "Some Python modules may be missing"
    fi
else
    print_error "termux_pxe_boot.py not found!"
    exit 1
fi

echo ""
echo "════════════════════════════════════════"
print_success "INSTALLATION COMPLETE!"
echo "════════════════════════════════════════"
echo ""
echo "📱 Termux PXE Boot is ready to use!"
echo ""
echo "🚀 To start the server:"
echo "   ./run_termux.sh"
echo ""
echo "   or"
echo ""
echo "   python termux_pxe_boot.py"
echo ""
echo "📖 Features:"
echo "   • DHCP Server for PXE boot"
echo "   • TFTP Server for file transfer"
echo "   • No root access required"
echo "   • Automatic port fallback"
echo "   • Works on non-rooted Android"
echo ""
echo "⚠️  Important Notes:"
echo "   • Connect to WiFi before starting"
echo "   • Server may use alternate ports if standard ports are restricted"
echo "   • DHCP port 67 may require root (server will use port 6700 instead)"
echo "   • TFTP port 69 may require root (server will use port 6900 instead)"
echo ""
echo "🖥️  To boot a PC:"
echo "   1. Start this server on your Android device"
echo "   2. Connect PC to same network"
echo "   3. Enable PXE/Network boot in PC BIOS"
echo "   4. PC will boot from this server"
echo ""
