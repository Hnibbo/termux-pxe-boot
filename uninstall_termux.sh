#!/data/data/com.termux/files/usr/bin/bash
# Termux PXE Boot - Uninstaller

echo ""
echo "🗑️  Termux PXE Boot Uninstaller"
echo "═══════════════════════════════════════"
echo ""
echo "This will remove:"
echo "  • All PXE boot files"
echo "  • Configuration files"
echo "  • Log files"
echo "  • TFTP directories"
echo ""
echo "⚠️  This action cannot be undone!"
echo ""

read -p "Are you sure you want to uninstall? (yes/no): " -r
echo ""

if [[ ! $REPLY =~ ^[Yy][Ee][Ss]$ ]]; then
    echo "❌ Uninstallation cancelled"
    exit 0
fi

echo "🗑️  Removing Termux PXE Boot..."
echo ""

# Remove directories
if [ -d ~/.termux_pxe_boot ]; then
    rm -rf ~/.termux_pxe_boot
    echo "✓ Removed ~/.termux_pxe_boot"
fi

# Remove scripts (optional)
read -p "Remove installation files? (yes/no): " -r
if [[ $REPLY =~ ^[Yy][Ee][Ss]$ ]]; then
    rm -f termux_pxe_boot.py
    rm -f install_termux.sh
    rm -f run_termux.sh
    rm -f uninstall_termux.sh
    rm -f test_server.sh
    echo "✓ Removed installation files"
fi

echo ""
echo "✅ Termux PXE Boot has been uninstalled"
echo ""
echo "To reinstall:"
echo "  Download the files again and run: ./install_termux.sh"
echo ""
