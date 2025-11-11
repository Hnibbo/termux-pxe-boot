# 🚀 Quick Start Guide - Termux PXE Boot

## 3-Step Setup

### 1️⃣ Install (One Time)

```bash
chmod +x install_termux.sh
./install_termux.sh
```

### 2️⃣ Run Server

```bash
./run_termux.sh
```

### 3️⃣ Boot Your PC

1. Connect PC to same WiFi as Android
2. Enter BIOS (press F2, F12, or Del during boot)
3. Enable "PXE Boot" or "Network Boot"
4. Set as first boot priority
5. Save and restart
6. PC boots from your Android! 🎉

---

## Alternative: Direct Run

```bash
python termux_pxe_boot.py
```

---

## What You'll See

```
⚡ TERMUX PXE BOOT SERVER - COMPLETE EDITION ⚡
Network Boot for Android Termux

✓ DHCP Server listening on port 67
✓ TFTP Server listening on port 69

PXE SERVER IS RUNNING!
Waiting for PXE boot requests...
```

---

## Troubleshooting

### "Permission denied on port 67/69"

✅ **Normal!** Server automatically uses ports 6700/6900 instead.

### "PC can't find server"

1. Check WiFi: Android and PC on same network
2. Check IP: `ip addr show wlan0`
3. Disable router DHCP temporarily

### "Module not found"

```bash
pkg install python
```

---

## Port Information

| Service | Standard Port | Fallback Port |
|---------|--------------|---------------|
| DHCP    | 67           | 6700          |
| TFTP    | 69           | 6900          |

**Note**: Standard ports require root. Fallback ports work without root.

---

## Testing

Run tests:

```bash
chmod +x test_server.sh
./test_server.sh
```

---

## Commands Reference

```bash
# Install
./install_termux.sh

# Run
./run_termux.sh

# Test
./test_server.sh

# View logs
tail -f ~/.termux_pxe_boot/logs/pxe_server.log

# Uninstall
./uninstall_termux.sh
```

---

## Features

✅ DHCP Server (assigns IPs)  
✅ TFTP Server (serves files)  
✅ No root required  
✅ Auto port fallback  
✅ Complete logging  
✅ Multiple PC support  

---

## That's It!

You now have a working PXE boot server on your Android device! 🎊

**Questions?** Check `README_TERMUX.md` for detailed documentation.
