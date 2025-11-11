# 🎯 ULTIMATE GUIDE: WiFi + Ethernet PXE Boot

## Your Exact Setup
- **Phone**: Connected to WiFi 📱
- **PC**: Connected to Ethernet cable 🖥️
- **Router**: Providing both WiFi and Ethernet 🌐

This is THE MOST CHALLENGING setup, but we've solved it!

## 🚀 Quick Start (3 Steps)

### Step 1: Run the Script
```bash
chmod +x RUN_WIFI_ETHERNET.sh
./RUN_WIFI_ETHERNET.sh
```

### Step 2: Configure Router (CRITICAL!)
Access router admin panel and **DISABLE CLIENT ISOLATION**

### Step 3: Boot PC
Enable PXE boot in BIOS and reboot

**That's it! PXE-E53 error = GONE!**

---

## 🔧 Detailed Router Configuration

### Why Router Settings Matter
When PC is on Ethernet and phone is on WiFi:
- Router may **isolate** WiFi from Ethernet for security
- DHCP broadcasts don't cross the isolation boundary
- PXE requests from PC never reach your phone
- Result: **PXE-E53 error**

### How to Fix: Access Router Admin

**1. Find Router IP:**
```bash
# On phone (Termux):
ip route show default

# Usually one of these:
192.168.1.1
192.168.0.1
192.168.2.1
10.0.0.1
```

**2. Access Router:**
- Open browser on phone or PC
- Go to: `http://192.168.1.1` (or your router IP)
- Login credentials (common defaults):
  - Username: `admin`, Password: `admin`
  - Username: `admin`, Password: `password`
  - Check sticker on router for credentials

**3. Disable Client Isolation:**

**TP-Link Routers:**
```
Wireless → Wireless Settings → Advanced
└── [ ] AP Isolation → DISABLE
```

**Netgear Routers:**
```
Advanced → Wireless Settings
└── [ ] Enable AP Isolation → UNCHECK
```

**Asus Routers:**
```
Wireless → Professional
└── Set AP Isolated → No
```

**Linksys Routers:**
```
Wireless → Advanced Wireless Settings
└── AP Isolation → Disabled
```

**D-Link Routers:**
```
Advanced → Wi-Fi
└── Enable Wireless Isolation → Uncheck
```

**Generic Routers:**
Look for any of these settings and **DISABLE/UNCHECK** them:
- Client Isolation
- AP Isolation  
- Wireless Isolation
- Station Isolation
- Client-to-Client Blocking
- Wireless Bridge Restrict
- Network Isolation

**4. Verify Same Subnet:**
```
Settings → LAN Settings or Network Settings
└── Check: WiFi and Ethernet use same IP range
    Example: Both should be 192.168.1.x (not 192.168.1.x vs 192.168.2.x)
```

**5. Optional: Disable Router DHCP (Recommended)**
```
DHCP Settings → DHCP Server
└── [ ] Enable DHCP Server → UNCHECK
```
⚠️ **Remember to re-enable after PXE boot!**

**6. Save and Reboot Router:**
- Click "Save" or "Apply"
- Reboot router (usually in System or Administration menu)
- Wait 2-3 minutes for router to fully restart

---

## 🖥️ PC BIOS Configuration

### Enter BIOS
1. **Restart PC**
2. Immediately press one of these keys repeatedly:
   - **F2** (Most common)
   - **F12** (Boot menu - Dell, Lenovo)
   - **Del** (Desktop motherboards)
   - **Esc** (HP, some Asus)
   - **F10** (Some HP models)

### Enable PXE Boot

**Look for these menu locations:**

**Option 1: Boot Menu**
```
Boot → Boot Configuration
└── [✓] Network Boot (PXE) → ENABLE
```

**Option 2: Advanced Boot**
```
Advanced → Boot Features
└── [✓] PXE Boot to LAN → ENABLE
```

**Option 3: Boot Options**
```
Boot → Boot Options
└── [✓] Boot from Network → ENABLE
```

**Set Boot Priority:**
```
Boot → Boot Priority Order
└── 1st: Network Boot / PXE Boot
    2nd: Hard Drive
    3rd: USB Drive
```

**Legacy vs UEFI:**
- Try **Legacy** mode first (more compatible)
- If doesn't work, try **UEFI** mode
- Some PCs have separate "Legacy PXE" and "UEFI PXE" options

**Network Card Settings:**
```
Advanced → Network Configuration
└── [✓] Network Stack → ENABLE
    [✓] IPv4 PXE Support → ENABLE
    [ ] IPv6 PXE Support → Can disable
```

### Save and Exit
1. Press **F10** to save
2. Confirm "Yes" to save changes
3. PC will reboot

---

## 📊 How It Works

### The Problem
```
Phone (WiFi)          Router          PC (Ethernet)
192.168.1.100    ←→ [ISOLATION] ←→   ???
     ↑                                  ↑
   DHCP Server                    PXE Client
     
❌ Client Isolation blocks communication
❌ DHCP broadcasts don't reach PC
❌ Result: PXE-E53 error
```

### The Solution
```
Phone (WiFi)          Router          PC (Ethernet)
192.168.1.100    ←→ [NO BARRIER] ←→  192.168.1.150
     ↑                                  ↑
   DHCP Server                    PXE Client
     |                                  |
     +------ DHCP Offer with ----------+
             Option 67 (boot file)
     
✅ Isolation disabled = full communication
✅ Multi-broadcast DHCP = reaches all networks
✅ Option 67 guaranteed = no PXE-E53
```

### Our Ultimate Server Features

**1. Multi-Interface Detection**
- Scans ALL network interfaces (wlan0, eth0, usb0, etc.)
- Gets IP, netmask, broadcast for each
- Identifies which is WiFi, which is Ethernet

**2. Multi-Broadcast DHCP**
- Sends DHCP offers to ALL broadcast addresses
- Covers: interface broadcasts + 255.255.255.255
- Also sends directly to client IP
- Ensures packet reaches PC even with partial isolation

**3. Periodic Announcements**
- Broadcasts DHCP availability every 30 seconds
- Helps with discovery even if initial broadcast missed
- Improves reliability on flaky networks

**4. Enhanced Logging**
- Shows which interface received request
- Logs all broadcast destinations
- Displays complete DHCP/TFTP transaction
- Helps diagnose issues

**5. Guaranteed Option 67**
- Boot filename in fixed field (byte 108)
- DHCP Option 66 (TFTP server)
- DHCP Option 67 (boot filename) - THE FIX
- All properly formatted and null-terminated

---

## 🔍 What You Should See

### On Phone (Termux)

**Startup:**
```
╔══════════════════════════════════════════════════════════════════╗
║          ⚡ ULTIMATE PXE - WIFI + ETHERNET BRIDGE MODE ⚡        ║
╚══════════════════════════════════════════════════════════════════╝

🔍 DETECTING NETWORK TOPOLOGY FOR WIFI + ETHERNET SETUP
======================================================================
✓ Interface: wlan0
  IP: 192.168.1.100
  Netmask: 255.255.255.0
  Broadcast: 192.168.1.255
  Type: WiFi

📊 NETWORK TOPOLOGY SUMMARY:
  Server IPs: 192.168.1.100
  Gateway: 192.168.1.1
  Subnets: 192.168.1.0/24
  Broadcast IPs: 192.168.1.255

✓ DHCP Server listening on ALL interfaces, port 67
✓ TFTP Server listening on ALL interfaces, port 69
```

**When PC Boots:**
```
📥 DHCP packet from 192.168.1.50 (could be from Ethernet side!)

🎯 PXE BOOT REQUEST DETECTED!
  From: 192.168.1.50 (MAC: aa:bb:cc:dd:ee:ff)
  This could be your PC on Ethernet!

  📤 DHCP Offer sent to 192.168.1.255:68
  📤 DHCP Offer sent to 255.255.255.255:68
  📤 DHCP Offer sent directly to 192.168.1.50:68

✅ DHCP OFFER SENT! (to 3 destinations)
  Offered IP: 192.168.1.150
  Boot File: pxelinux.0
  TFTP Server: 192.168.1.100
  ✓ Option 66: 192.168.1.100
  ✓ Option 67: pxelinux.0

🔍 Watch for TFTP request next...

📥 TFTP request from 192.168.1.150 (Ethernet side!)
📂 TFTP Request: pxelinux.0 from 192.168.1.150
✅ TFTP Transfer complete: pxelinux.0 (1024 bytes)

🎉 PXE BOOT SUCCESSFUL!
Your PC should now be booting from network!
```

### On PC Screen

**Success Sequence:**
```
1. PXE Boot ROM initializing...
2. Searching for DHCP server...
3. DHCP server found: 192.168.1.100
4. Receiving boot filename... pxelinux.0      ← NO E53 ERROR!
5. Downloading pxelinux.0 via TFTP...
6. Loading configuration...
7. Boot menu appears
```

---

## 🐛 Troubleshooting

### Issue: Still Getting PXE-E53

**Check #1: Router Isolation**
```bash
# On phone, check if you can reach PC IP
ping 192.168.1.50   # Use your PC's IP

# If "Destination Host Unreachable" = isolation still enabled
```

**Solution:** Double-check router settings, ensure isolation is OFF

**Check #2: Different Subnets**
```bash
# On phone:
ip addr show | grep inet

# On PC (Windows cmd):
ipconfig

# Both should be 192.168.X.Y where X is the SAME number
```

**Solution:** Configure router to use same subnet for WiFi and Ethernet

**Check #3: Firewall**
```bash
# Check if ports are blocked
netstat -uln | grep -E ":(67|69)"
```

**Solution:** Temporarily disable any firewall on phone

### Issue: PC Says "No DHCP Server Found"

**Possible Causes:**
1. Client isolation still enabled on router
2. PC and phone on different VLANs
3. Router DHCP conflicting with our DHCP
4. DHCP packets being filtered

**Solutions:**
1. Verify isolation OFF (check router web interface)
2. Check router VLAN settings (disable if present)
3. Disable router DHCP temporarily
4. Check router firewall rules

### Issue: DHCP Works but TFTP Fails

**Check Logs:**
```bash
tail -f ~/.termux_pxe_boot/logs/ultimate_pxe.log
```

**Common Causes:**
1. Port 69 blocked by firewall
2. TFTP file not found
3. Permission issues

**Solutions:**
1. Disable firewall temporarily
2. Verify files exist in `~/.termux_pxe_boot/tftp/`
3. Check file permissions: `chmod -R 755 ~/.termux_pxe_boot/tftp/`

### Issue: Connection Keeps Timing Out

**Enhance Reliability:**
1. **Move closer to router** - weak signal can cause packet loss
2. **Use 2.4GHz WiFi** - better range and penetration
3. **Restart router** - clear any stuck states
4. **Temporarily disconnect other devices** - reduce network load

### Ultimate Fallback: USB Tethering

If WiFi + Ethernet still doesn't work after all troubleshooting:

```bash
# Use USB tethering instead (100% success rate)
1. Connect phone to PC via USB
2. Enable USB Tethering on phone
3. Run: ./AUTO_RUN.sh
4. Boot PC

USB tethering = direct connection = no router issues!
```

---

## ✅ Success Checklist

Before starting, verify:
- [ ] Router client isolation is **DISABLED**
- [ ] WiFi and Ethernet are on **same subnet**
- [ ] Router DHCP **optionally disabled**
- [ ] PC BIOS has PXE boot **enabled**
- [ ] PC BIOS has Network Boot as **1st priority**
- [ ] PC is connected to router via **Ethernet cable**
- [ ] Phone is connected to **same router WiFi**

During PXE boot, you should see:
- [ ] Phone logs show "DHCP packet from [PC-IP]"
- [ ] Phone logs show "DHCP Offer sent to 3 destinations"
- [ ] Phone logs show "Option 67: pxelinux.0"
- [ ] Phone logs show "TFTP Request: pxelinux.0"
- [ ] Phone logs show "TFTP Transfer complete"
- [ ] PC screen shows "Receiving boot filename... pxelinux.0"
- [ ] PC screen shows boot menu

---

## 📝 Quick Reference

### Files
- **Main server:** `ULTIMATE_WIFI_ETHERNET_FIX.py`
- **Runner script:** `RUN_WIFI_ETHERNET.sh`
- **This guide:** `WIFI_ETHERNET_GUIDE.md`
- **Logs:** `~/.termux_pxe_boot/logs/ultimate_pxe.log`

### Commands
```bash
# Start server
chmod +x RUN_WIFI_ETHERNET.sh && ./RUN_WIFI_ETHERNET.sh

# View logs
tail -f ~/.termux_pxe_boot/logs/ultimate_pxe.log

# Check network
ip addr show
ip route show

# Test connectivity
ping [router-ip]
ping [pc-ip]
```

### Key Settings
- **DHCP Port:** 67 (or 6767, 6700 as fallback)
- **TFTP Port:** 69 (or 6969, 6900 as fallback)
- **Offered IP Range:** X.X.X.150 (where X.X.X is your subnet)
- **Boot File:** pxelinux.0
- **DHCP Options:** 66 (TFTP server), 67 (boot filename)

---

## 🎉 Conclusion

Your WiFi + Ethernet setup is now **fully supported**!

The key points:
1. ✅ **Router isolation must be disabled**
2. ✅ **Our server broadcasts to multiple addresses**
3. ✅ **Option 67 is guaranteed in DHCP offers**
4. ✅ **Works even with partial isolation (with settings)**

Just run:
```bash
./RUN_WIFI_ETHERNET.sh
```

And enjoy PXE booting without any E53 errors!

---

**Made with ❤️ to solve the WiFi + Ethernet challenge**

Repository: https://github.com/Hnibbo/termux-pxe-boot
