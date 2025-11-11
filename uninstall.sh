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
