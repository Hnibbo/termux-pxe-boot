# Termux PXE Boot - Troubleshooting Guide

## 🚨 Common Issue: Network Isolation (Most Likely Your Problem!)

**SYMPTOMS:**
- "PXE E53: no boot filename received" error
- PC shows "No DHCP servers found" or "No boot file received"
- No logs appear in Termux when PC tries to boot
- PC on Ethernet, Phone on WiFi, but they can't see each other

**ROOT CAUSE:** 
Your router is likely **isolating** the 2.4G WiFi network from the Ethernet network, or they are on different subnets.

## ✅ SOLUTION 1: Connect Both Devices to Same Network

**EASIEST FIX:**
1. **Move your PC to 2.4G WiFi** (same network as your phone)
2. OR **Move your phone to Ethernet** (if possible with USB OTG adapter)
3. OR **Connect both to 5G WiFi** (if your router allows it)

## ✅ SOLUTION 2: Disable Router Isolation

1. **Access router admin panel:**
   - Go to browser: `http://192.168.1.1` or `http://192.168.0.1`
   - Login with admin credentials

2. **Look for these settings and DISABLE them:**
   - "Client Isolation" 
   - "AP Isolation"
   - "Network Isolation" 
   - "Guest Network Isolation"
   - "Client-to-Client Blocking"

3. **Save settings and restart router**

## ✅ SOLUTION 3: Test Network Connectivity

Run the network diagnostic tools:

```bash
# 1. Check network configuration
chmod +x network_fix.sh && ./network_fix.sh

# 2. Detailed network analysis
python3 network_diagnostic.py

# 3. Test the server
chmod +x test_pxe_server.py && python3 test_pxe_server.py
```

## 🔧 Network Diagnostic Steps

### Step 1: Check Your Phone's IP
```bash
hostname -I
# Should show something like: 192.168.1.100
```

### Step 2: Test PC ↔ Phone Connectivity
**On PC terminal:**
```bash
ping [phone-ip-from-step-1]
```

**On Phone Termux:**
```bash
ping [pc-ip]
```

### Step 3: Check ARP Table
**On Phone Termux:**
```bash
ip neigh
```

You should see your PC's MAC address if they're on the same network.

## 🚀 Quick Fix Commands

Run these commands in Termux:

```bash
# 1. Check current network
ip addr show

# 2. Test connectivity
ping -c 1 192.168.1.1
ping -c 1 192.168.0.1

# 3. Start with diagnostics
chmod +x run_termux.sh
./run_termux.sh
```

## 📱 Phone Network Configuration

### Termux Network Setup
1. **Ensure WiFi is enabled and connected**
2. **Check if hotspot is OFF** (can cause conflicts)
3. **Disable VPN** (can block PXE traffic)
4. **Check firewall settings** (Android firewall apps can block traffic)

### Network Permissions (if needed)
```bash
# Grant network permissions (Termux)
termux-setup-storage
pkg install network-tool
```

## 🖥️ PC Configuration

### BIOS/UEFI Settings
1. **Enable PXE Boot:**
   - Look for "Network Boot", "PXE Boot", or "Boot from LAN"
   - Set to "Enabled"

2. **Boot Order:**
   - Set "Network Boot" as **first** boot priority
   - Below "USB" and "Hard Drive"

3. **Legacy vs UEFI:**
   - Try both Legacy and UEFI modes
   - Some PCs only support one mode

### Network Card Settings
```bash
# In PC BIOS, check:
# - "Wake on LAN" enabled
# - "PXE Boot" enabled
# - Network boot protocol: "PXE" or "IP4"
```

## 🐛 Error Code Solutions

### "PXE E53: No boot filename received"
**FIX:** ✅ **Network isolation issue** - Connect both devices to same network

### "DHCP server not found"
**FIX:** 
1. Check if router DHCP is disabled
2. Our server should provide DHCP automatically
3. Verify network connectivity

### "TFTP timeout" 
**FIX:**
1. Check firewall settings
2. Verify TFTP port 69 is open
3. Test with: `telnet [phone-ip] 69`

### "No network bootable device"
**FIX:**
1. Check PC BIOS settings
2. Verify PXE is enabled
3. Try different network port on PC

## 🔍 Advanced Troubleshooting

### Check Server Logs
```bash
# View real-time logs
tail -f ~/.termux_pxe_boot/logs/pxe_server.log

# Check if servers started
ss -uln | grep -E ":(67|69|8080)"
```

### Manual Network Test
```bash
# Test if DHCP is working
sudo tcpdump -i any port 67 -n

# Test if TFTP is working  
sudo tcpdump -i any port 69 -n
```

### Router Configuration Check
```bash
# Check what IP range router uses
ip route | grep default
```

## 🌐 Alternative Setup Methods

### Method 1: WiFi Direct (Advanced)
- Use WiFi Direct to connect directly
- No router needed
- More complex setup

### Method 2: USB Tethering
- Connect phone to PC via USB
- Enable USB tethering
- PC should get IP from phone

### Method 3: Ethernet Bridge
- Use USB-to-Ethernet adapter on phone
- Connect both to same switch
- No WiFi isolation issues

## 💡 Pro Tips

1. **Use the same WiFi channel** (2.4G or 5G) for both devices
2. **Disable VPN** on both devices
3. **Restart router** after changing settings
4. **Test with laptop** first (easier than desktop)
5. **Check router logs** for client connections

## 📞 Still Not Working?

If you've tried all solutions:

1. **Run diagnostic tools:**
   ```bash
   python3 network_diagnostic.py > diagnosis.txt
   ```

2. **Share diagnostic results** with the community

3. **Try different router** (some routers are notorious for isolation)

4. **Use Ethernet-only setup** (no WiFi involved)

## 🎯 Success Indicators

You'll know it's working when you see:
- `→ PXE DHCP Request from [PC-IP]` in Termux logs
- PC gets IP address in the 192.168.1.x range
- TFTP transfer messages appear
- Boot menu appears on PC screen

**Remember: The #1 cause is network isolation by the router!**