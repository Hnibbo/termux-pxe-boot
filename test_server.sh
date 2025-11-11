#!/data/data/com.termux/files/usr/bin/bash
# Test Termux PXE Boot Server

echo "🧪 Testing Termux PXE Boot Server..."
echo ""

# Colors
GREEN='\033[0;32m'
RED='\033[0;31m'
YELLOW='\033[1;33m'
NC='\033[0m'

test_passed=0
test_failed=0

print_test() {
    if [ $2 -eq 0 ]; then
        echo -e "${GREEN}✓${NC} $1"
        ((test_passed++))
    else
        echo -e "${RED}✗${NC} $1"
        ((test_failed++))
    fi
}

# Test 1: Python installation
echo "Test 1: Python installation"
if command -v python &> /dev/null || command -v python3 &> /dev/null; then
    print_test "Python is installed" 0
else
    print_test "Python is installed" 1
fi

# Test 2: Main script exists
echo "Test 2: Main script"
if [ -f "termux_pxe_boot.py" ]; then
    print_test "termux_pxe_boot.py exists" 0
else
    print_test "termux_pxe_boot.py exists" 1
fi

# Test 3: Script is executable
echo "Test 3: Script permissions"
if [ -x "termux_pxe_boot.py" ]; then
    print_test "Script is executable" 0
else
    print_test "Script is executable" 1
fi

# Test 4: Python modules
echo "Test 4: Required Python modules"
if python -c "import socket, threading, struct, json, os, sys, signal, time" 2>/dev/null; then
    print_test "All required modules available" 0
else
    print_test "All required modules available" 1
fi

# Test 5: Directories
echo "Test 5: Directory structure"
if [ -d "$HOME/.termux_pxe_boot" ]; then
    print_test "Base directory exists" 0
else
    print_test "Base directory exists" 1
fi

# Test 6: Boot files
echo "Test 6: Boot files"
if [ -f ~/.termux_pxe_boot/tftp/pxelinux.0 ]; then
    print_test "Boot files created" 0
else
    print_test "Boot files created" 1
fi

# Test 7: Configuration files
echo "Test 7: Configuration"
if [ -f ~/.termux_pxe_boot/tftp/pxelinux.cfg/default ]; then
    print_test "Boot configuration exists" 0
else
    print_test "Boot configuration exists" 1
fi

# Test 8: Launch script
echo "Test 8: Launch script"
if [ -f "run_termux.sh" ] && [ -x "run_termux.sh" ]; then
    print_test "Launch script ready" 0
else
    print_test "Launch script ready" 1
fi

# Test 9: Python syntax check
echo "Test 9: Python syntax"
if python -m py_compile termux_pxe_boot.py 2>/dev/null; then
    print_test "Python syntax valid" 0
else
    print_test "Python syntax valid" 1
fi

# Test 10: Quick start test
echo "Test 10: Server start test"
if timeout 2 python termux_pxe_boot.py 2>&1 | grep -q "PXE SERVER IS RUNNING"; then
    print_test "Server can start" 0
else
    print_test "Server can start" 1
fi

echo ""
echo "═══════════════════════════════════════"
echo "Test Results:"
echo -e "${GREEN}Passed: $test_passed${NC}"
echo -e "${RED}Failed: $test_failed${NC}"
echo "═══════════════════════════════════════"

if [ $test_failed -eq 0 ]; then
    echo ""
    echo -e "${GREEN}🎉 All tests passed!${NC}"
    echo -e "${GREEN}✓ Termux PXE Boot is ready to use${NC}"
    echo ""
    echo "Start with: ./run_termux.sh"
    exit 0
else
    echo ""
    echo -e "${RED}⚠ Some tests failed${NC}"
    echo "Run: ./install_termux.sh to fix issues"
    exit 1
fi
