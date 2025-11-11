#!/bin/bash
# Termux PXE Boot - Working Installation Script
# Handles actual Termux packages correctly

echo "⚡ Termux PXE Boot - Working Installer ⚡"
echo "=========================================="

# Colors
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
NC='\033[0m'

print_status() { echo -e "${GREEN}✅ $1${NC}"; }
print_warning() { echo -e "${YELLOW}⚠️  $1${NC}"; }
print_error() { echo -e "${RED}❌ $1${NC}"; }

# Check if in Termux
if [[ -d "/data/data/com.termux/files" ]]; then
    print_status "Termux environment detected"
fi

# Check Python
check_python() {
    if ! command -v python &> /dev/null; then
        print_error "Python not found!"
        if command -v pkg &> /dev/null; then
            print_info "Installing Python..."
            pkg install -y python python-pip
        else
            exit 1
        fi
    fi
    print_status "Python found: $(python --version)"
}

# Install packages (works in Termux)
install_packages() {
    print_info "Installing packages..."
    
    if command -v pkg &> /dev/null; then
        pkg update -y 2>/dev/null || true
        pkg install -y python python-pip openssh curl wget git 2>/dev/null || true
        
        # tkinter is included with python in Termux
        if ! python -c "import tkinter" 2>/dev/null; then
            print_warning "tkinter not found, reinstalling python..."
            pkg install -y python 2>/dev/null || true
        fi
    fi
    
    # Install Python packages
    python -m pip install --user requests psutil 2>/dev/null || true
    
    print_status "Package installation completed"
}

# Setup directories
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

# Create launcher
create_launcher() {
    print_info "Creating launcher script..."
    
    cat > run.sh << 'EOF'
#!/bin/bash
# Termux PXE Boot Launcher

cd "$(dirname "$0")"

# Check Python
if ! command -v python &> /dev/null; then
    echo "❌ Python not found. Install with: pkg install python"
    exit 1
fi

# Check tkinter (included with python in Termux)
if ! python -c "import tkinter" 2>/dev/null; then
    echo "❌ tkinter not found. Install with: pkg install python"
    exit 1
fi

# Start working application
echo "⚡ Starting Termux PXE Boot..."
echo "🐧 Network Boot Server"
echo "================================"
python working_pxe_boot.py
EOF
    
    chmod +x run.sh
    print_status "Launcher script created"
}

# Create uninstaller
create_uninstaller() {
    print_info "Creating uninstaller script..."
    
    cat > uninstall.sh << 'EOF'
#!/bin/bash
echo "🗑️  Termux PXE Boot Uninstaller"
read -p "Are you sure? (y/N): " -n 1 -r
echo
if [[ $REPLY =~ ^[Yy]$ ]]; then
    rm -rf ~/.termux_pxe_boot ~/pxe_assets ~/pxe_boot ~/pxe_tftp
    rm -f run.sh install.sh uninstall.sh working_pxe_boot.py
    echo "✅ Termux PXE Boot uninstalled"
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
        print_status "Application ready"
    else
        print_error "Application not ready"
        return 1
    fi
    
    return 0
}

# Main
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
        echo "Run with: ./run.sh"
        echo "or: ./run_simple.sh"
        echo ""
        echo "Features:"
        echo "• Real DHCP & TFTP servers"
        echo "• Network boot capabilities"
        echo "• No root required"
        echo "• Works in Termux"
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
    --help) echo "Usage: $0 [--force]"; exit 0;;
esac

main "$@"# Termux PXE Boot - Working Installation Script
# Handles actual Termux packages correctly

echo "⚡ Termux PXE Boot - Working Installer ⚡"
echo "=========================================="

# Colors
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
NC='\033[0m'

print_status() { echo -e "${GREEN}✅ $1${NC}"; }
print_warning() { echo -e "${YELLOW}⚠️  $1${NC}"; }
print_error() { echo -e "${RED}❌ $1${NC}"; }

# Check if in Termux
if [[ -d "/data/data/com.termux/files" ]]; then
    print_status "Termux environment detected"
fi

# Check Python
check_python() {
    if ! command -v python &> /dev/null; then
        print_error "Python not found!"
        if command -v pkg &> /dev/null; then
            print_info "Installing Python..."
            pkg install -y python python-pip
        else
            exit 1
        fi
    fi
    print_status "Python found: $(python --version)"
}

# Install packages (works in Termux)
install_packages() {
    print_info "Installing packages..."
    
    if command -v pkg &> /dev/null; then
        pkg update -y 2>/dev/null || true
        pkg install -y python python-pip openssh curl wget git 2>/dev/null || true
        
        # tkinter is included with python in Termux
        if ! python -c "import tkinter" 2>/dev/null; then
            print_warning "tkinter not found, reinstalling python..."
            pkg install -y python 2>/dev/null || true
        fi
    fi
    
    # Install Python packages
    python -m pip install --user requests psutil 2>/dev/null || true
    
    print_status "Package installation completed"
}

# Setup directories
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

# Create launcher
create_launcher() {
    print_info "Creating launcher script..."
    
    cat > run.sh << 'EOF'
#!/bin/bash
# Termux PXE Boot Launcher

cd "$(dirname "$0")"

# Check Python
if ! command -v python &> /dev/null; then
    echo "❌ Python not found. Install with: pkg install python"
    exit 1
fi

# Check tkinter (included with python in Termux)
if ! python -c "import tkinter" 2>/dev/null; then
    echo "❌ tkinter not found. Install with: pkg install python"
    exit 1
fi

# Start working application
echo "⚡ Starting Termux PXE Boot..."
echo "🐧 Network Boot Server"
echo "================================"
python working_pxe_boot.py
EOF
    
    chmod +x run.sh
    print_status "Launcher script created"
}

# Create uninstaller
create_uninstaller() {
    print_info "Creating uninstaller script..."
    
    cat > uninstall.sh << 'EOF'
#!/bin/bash
echo "🗑️  Termux PXE Boot Uninstaller"
read -p "Are you sure? (y/N): " -n 1 -r
echo
if [[ $REPLY =~ ^[Yy]$ ]]; then
    rm -rf ~/.termux_pxe_boot ~/pxe_assets ~/pxe_boot ~/pxe_tftp
    rm -f run.sh install.sh uninstall.sh working_pxe_boot.py
    echo "✅ Termux PXE Boot uninstalled"
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
        print_status "Application ready"
    else
        print_error "Application not ready"
        return 1
    fi
    
    return 0
}

# Main
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
        echo "Run with: ./run.sh"
        echo "or: ./run_simple.sh"
        echo ""
        echo "Features:"
        echo "• Real DHCP & TFTP servers"
        echo "• Network boot capabilities"
        echo "• No root required"
        echo "• Works in Termux"
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
    --help) echo "Usage: $0 [--force]"; exit 0;;
esac

main "$@"
