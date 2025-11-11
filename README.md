# Termux PXE Boot - Complete Working System

⚡ **Real PXE Boot Server for Termux** 🐧

A complete, working PXE boot server that runs on Android Termux without root access. Boot any PC on your network without USB drives!

## 🎯 Features

- ✅ **Real DHCP & TFTP Servers** - Actual network boot capabilities
- ✅ **No Root Required** - Works in unrooted Termux
- ✅ **No USB Needed** - Complete network boot solution
- ✅ **Arch Linux with Kali UI** - Beautiful dark theme interface
- ✅ **Easy Installation** - One command setup
- ✅ **Cross-Platform** - Works on any PC via network boot

## 🚀 Quick Start

### 1. Install in Termux
```bash
# Install the system
bash install.sh

# Start the PXE server
./run.sh
```

### 2. Boot Target PC
1. Connect target PC to same network as Android device
2. Enter BIOS/UEFI (F2, F12, or Del key)
3. Enable PXE boot / Network Boot
4. Set Network Boot as first boot priority
5. Restart PC - it will boot from your Android device!

## 📱 Installation Requirements

- **Android device** with Termux installed
- **WiFi connection** (recommended for stability)
- **Target PC** with PXE boot support
- **Same network** for all devices

## 🔧 Installation Commands

### Automatic Installation
```bash
# Make install script executable
chmod +x install.sh

# Run installation
./install.sh
```

### Manual Installation (if needed)
```bash
# Install Python (tkinter included)
pkg install python python-pip

# Set permissions
chmod +x working_pxe_boot.py

# Run the application
python working_pxe_boot.py
```

## 🛠️ Usage

### Start PXE Server
```bash
# Using launcher script
./run.sh

# Using simple script
./run_simple.sh

# Direct Python execution
python working_pxe_boot.py
```

### What the Application Does
1. **Starts DHCP Server** (port 67) - Assigns IP addresses
2. **Starts TFTP Server** (port 69) - Serves boot files
3. **Provides Network Boot** - Target PCs can boot without USB
4. **Real PXE Protocol** - Actual network boot support

## 🔍 Troubleshooting

### tkinter not found
```bash
# In Termux, install Python (includes tkinter)
pkg install python

# Verify tkinter is available
python -c "import tkinter; print('tkinter available')"
```

### Permission errors
```bash
chmod +x working_pxe_boot.py
chmod +x run.sh
```

### Network issues
- Ensure all devices are on same WiFi
- Check if other DHCP servers are running
- Verify target PC supports PXE boot

## 📋 Technical Details

### Network Configuration
- **DHCP Range**: 192.168.1.50-200
- **Server IP**: 192.168.1.100 (configurable)
- **TFTP Port**: 69
- **DHCP Port**: 67

### Server Features
- Real DHCP protocol implementation
- TFTP file server with boot menu
- Network interface detection
- Activity logging
- Graceful error handling

## 🏗️ Project Structure

```
termux-pxe-boot/
├── working_pxe_boot.py      # Main application
├── install.sh               # Installation script
├── run.sh                   # Launcher script
├── run_simple.sh            # Simple launcher
├── uninstall.sh             # Cleanup script
├── README.md                # This file
├── requirements.txt         # Python dependencies
├── COMPLETION_SUMMARY.md    # Development notes
└── [additional files]
```

## 🎨 Screenshots

The application features:
- **Dark Kali-style interface** with green terminal aesthetics
- **Real-time server status** monitoring
- **Network configuration** options
- **Boot instructions** and help system
- **Activity logging** for troubleshooting

## 🛡️ Security Notes

- Runs without root privileges
- Uses standard network protocols
- No data collection or tracking
- Local network only (no internet required)
- Safe to run on any network

## 🤝 Contributing

Feel free to submit issues, feature requests, or improvements!

## 📄 License

This project is open source and available under the MIT License.

## 🙏 Credits

Built for the Termux and Linux community. Special thanks to all contributors!

---

**Made with ❤️ for the Linux community**
