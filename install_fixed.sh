#!/bin/bash
# Termux PXE Boot - Working Installation Script
# Handles actual Termux packages properly

echo "⚡ Termux PXE Boot - Working Edition ⚡"
echo "========================================="

# Colors
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
NC='\033[0m'

print_status() { echo -e "${GREEN}✅ $1${NC}"; }
print_warning() { echo -e "${YELLOW}⚠️  $1${NC}"; }
print_error() { echo -e "${RED}❌ $1${NC}"; }

# Check Python
check_python() {
    if ! command -v python &> /dev/null; then
        print_error "Python not found!"
        if command -v pkg &> /dev/null; then
            echo "Installing Python..."
            pkg install -y python
        else
            exit 1
        fi
    fi
    print_status "Python found: $(python --version)"
}

# Install packages (handle gracefully)
install_packages() {
    echo "Installing packages..."
    
    if command -v pkg &> /dev/null; then
        pkg update -y 2>/dev/null || true
        pkg install -y python python-pip 2>/dev/null || true
        
        # Try different tkinter approaches
        if ! python -c "import tkinter" 2>/dev/null; then
            print_warning "tkinter not found, trying alternatives..."
            pkg install -y python-tkinter 2>/dev/null || true
            pkg install -y tkinter 2>/dev/null || true
        fi
        
        # Install useful tools
        pkg install -y openssh curl wget git 2>/dev/null || true
    fi
    
    # Install Python packages
    python -m pip install --user requests psutil 2>/dev/null || true
    
    print_status "Package installation completed"
}

# Create directories
setup_directories() {
    echo "Setting up directories..."
    mkdir -p ~/.termux_pxe_boot/{configs,logs,boot,tftp}
    print_status "Directories created"
}

# Set permissions
set_permissions() {
    echo "Setting permissions..."
    chmod +x working_pxe_boot.py
    chmod +x run.sh
    chmod +x run_simple.sh
    chmod +x install.sh
    print_status "Permissions set"
}

# Test installation
test_installation() {
    echo "Testing installation..."
    
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
    echo "Starting installation..."
    echo ""
    
    check_python
    install_packages
    setup_directories
    set_permissions
    
    if test_installation; then
        echo ""
        echo "🎉 Installation successful!"
        echo ""
        print_status "Ready to use"
        echo ""
        echo "Run with: ./run.sh"
        echo "or: ./run_simple.sh"
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
# Handles actual Termux packages properly

echo "⚡ Termux PXE Boot - Working Edition ⚡"
echo "========================================="

# Colors
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
NC='\033[0m'

print_status() { echo -e "${GREEN}✅ $1${NC}"; }
print_warning() { echo -e "${YELLOW}⚠️  $1${NC}"; }
print_error() { echo -e "${RED}❌ $1${NC}"; }

# Check Python
check_python() {
    if ! command -v python &> /dev/null; then
        print_error "Python not found!"
        if command -v pkg &> /dev/null; then
            echo "Installing Python..."
            pkg install -y python
        else
            exit 1
        fi
    fi
    print_status "Python found: $(python --version)"
}

# Install packages (handle gracefully)
install_packages() {
    echo "Installing packages..."
    
    if command -v pkg &> /dev/null; then
        pkg update -y 2>/dev/null || true
        pkg install -y python python-pip 2>/dev/null || true
        
        # Try different tkinter approaches
        if ! python -c "import tkinter" 2>/dev/null; then
            print_warning "tkinter not found, trying alternatives..."
            pkg install -y python-tkinter 2>/dev/null || true
            pkg install -y tkinter 2>/dev/null || true
        fi
        
        # Install useful tools
        pkg install -y openssh curl wget git 2>/dev/null || true
    fi
    
    # Install Python packages
    python -m pip install --user requests psutil 2>/dev/null || true
    
    print_status "Package installation completed"
}

# Create directories
setup_directories() {
    echo "Setting up directories..."
    mkdir -p ~/.termux_pxe_boot/{configs,logs,boot,tftp}
    print_status "Directories created"
}

# Set permissions
set_permissions() {
    echo "Setting permissions..."
    chmod +x working_pxe_boot.py
    chmod +x run.sh
    chmod +x run_simple.sh
    chmod +x install.sh
    print_status "Permissions set"
}

# Test installation
test_installation() {
    echo "Testing installation..."
    
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
    echo "Starting installation..."
    echo ""
    
    check_python
    install_packages
    setup_directories
    set_permissions
    
    if test_installation; then
        echo ""
        echo "🎉 Installation successful!"
        echo ""
        print_status "Ready to use"
        echo ""
        echo "Run with: ./run.sh"
        echo "or: ./run_simple.sh"
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
