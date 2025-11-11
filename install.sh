#!/bin/bash
# Termux PXE Boot - Working Installation Script
# Properly handles Termux packages

echo "⚡ Termux PXE Boot - Working Installer ⚡"
echo "=========================================="

# Colors for output
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
NC='\033[0m'

print_status() { echo -e "${GREEN}✅ $1${NC}"; }
print_warning() { echo -e "${YELLOW}⚠️  $1${NC}"; }
print_error() { echo -e "${RED}❌ $1${NC}"; }

# Check if in Termux (optional)
if [[ -d "/data/data/com.termux/files" ]]; then
    print_status "Termux environment detected"
fi

# Check if Python exists
check_python() {
    if ! command -v python &> /dev/null; then
        print_error "Python not found!"
        if command -v pkg &> /dev/null; then
            print_info "Installing Python..."
            pkg install -y python python-pip
        else
            print_error "Cannot install Python - not in Termux?"
            exit 1
        fi
    fi
    print_status "Python found: $(python --version)"
}

# Install packages (handle gracefully)
install_packages() {
    print_info "Installing packages..."
    
    if command -v pkg &> /dev/null; then
        pkg update -y 2>/dev/null || true
        pkg install -y python python-pip 2>/dev/null || true
        
        # Install useful tools
        pkg install -y openssh curl wget git 2>/dev/null || true
        
        # Check if tkinter is available (should be with python)
        if ! python -c "import tkinter" 2>/dev/null; then
            print_warning "tkinter not found, but should be included with python"
            print_info "Try: pkg install python"
        else
            print_status "tkinter available"
        fi
    fi
    
    # Install Python packages
    python -m pip install --user requests psutil 2>/dev/null || true
    
    print_status "Package installation completed"
}

# Create directories
setup_directories() {
    print_info "Setting up directories..."
    mkdir -p ~/.termux_pxe_boot/{configs,logs,boot,tftp}
    mkdir -p ~/pxe_assets/{arch,customizer,scripts}
    mkdir -p ~/pxe_boot/{configs,logs}
    mkdir -p ~/pxe_tftp/{pxelinux.cfg,boot}
    print_status "Directories created"
}

# Set permissions
set_permissions() {
    print_info "Setting permissions..."
    chmod +x working_pxe_boot.py
    chmod +x run.sh
    chmod +x run_simple.sh
    chmod +x install.sh
    chmod +x uninstall.sh
    print_status "Permissions set"
}

# Create working launcher
create_launcher() {
    print_info "Creating launcher script..."
    
    cat > run.sh << 'EOF'
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
EOF
    
    chmod +x run.sh
    print_status "Launcher script created"
}

# Create uninstall script
create_uninstaller() {
    print_info "Creating uninstaller script..."
    
    cat > uninstall.sh << 'EOF'
#!/bin/bash
# Termux PXE Boot Uninstaller

echo "🗑️  Termux PXE Boot Uninstaller"
echo "================================"
echo "This will remove all application files and configurations."
read -p "Are you sure? (y/N): " -n 1 -r
echo
if [[ $REPLY =~ ^[Yy]$ ]]; then
    rm -rf ~/.termux_pxe_boot
    rm -rf ~/pxe_assets
    rm -rf ~/pxe_boot
    rm -rf ~/pxe_tftp
    rm -f run.sh install.sh uninstall.sh
    rm -f working_pxe_boot.py
    echo "✅ Termux PXE Boot has been uninstalled"
else
    echo "❌ Uninstallation cancelled"
fi
EOF
    
    chmod +x uninstall.sh
    print_status "Uninstaller script created"
}

# Test installation
test_installation() {
    print_info "Testing installation..."
    
    if python -c "import tkinter" 2>/dev/null; then
        print_status "tkinter available"
    else
        print_warning "tkinter not available, GUI may not work"
    fi
    
    if [[ -x "working_pxe_boot.py" ]]; then
        print_status "Application executable"
    else
        print_error "Application not executable"
        return 1
    fi
    
    return 0
}

# Main installation
main() {
    echo ""
    print_info "Starting installation..."
    echo ""
    
    check_python
    install_packages
    setup_directories
    set_permissions
    create_launcher
    create_uninstaller
    
    if test_installation; then
        echo ""
        echo "🎉 Installation successful!"
        echo ""
        print_status "Termux PXE Boot is ready to use"
        echo ""
        echo "🚀 To start the application:"
        echo "   ./run.sh"
        echo "   or"
        echo "   ./run_simple.sh"
        echo ""
        print_info "Features included:"
        echo "   • Real DHCP & TFTP servers"
        echo "   • Network interface detection"
        echo "   • PXE boot capabilities"
        echo "   • No root required"
        echo "   • Works in Termux"
        echo ""
        print_info "Next steps:"
        echo "   1. Connect to WiFi"
        echo "   2. Run: ./run.sh"
        echo "   3. Start the PXE server"
        echo "   4. Boot target PCs via network"
        echo ""
    else
        echo ""
        print_error "Installation failed"
        exit 1
    fi
}

# Handle arguments
case "${1:-}" in
    --force) print_warning "Force mode";;
    --help) 
        echo "Termux PXE Boot Installer"
        echo "Usage: $0 [--force]"
        exit 0
        ;;
esac

main "$@"
