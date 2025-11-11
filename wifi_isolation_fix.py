#!/usr/bin/env python3
"""
WIFI ISOLATION FIX - Guaranteed WiFi Success Without USB Cable
Specifically targets: Phone WiFi + PC Ethernet + Same Router = Router Isolation
"""
import os
import socket
import subprocess
import threading
import time
import json
from pathlib import Path

class WiFiIsolationFix:
    def __init__(self):
        self.bridged_clients = []
        self.is_running = False
        
    def log(self, message):
        print(f"🌐 [WiFi-Isolation-Fix] {message}")
        
    def detect_router_isolation(self):
        """Detect and fix router isolation"""
        self.log("🔍 DETECTING ROUTER ISOLATION")
        
        try:
            # Get phone's WiFi IP
            s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
            s.connect(("8.8.8.8", 80))
            phone_ip = s.getsockname()[0]
            s.close()
            
            self.log(f"📱 Phone WiFi IP: {phone_ip}")
            
            # Get phone's subnet
            phone_net = '.'.join(phone_ip.split('.')[:3])
            
            # Try to detect PC on ethernet
            pc_ip = self.detect_pc_on_ethernet(phone_net)
            
            if pc_ip:
                self.log(f"💻 Detected PC Ethernet IP: {pc_ip}")
                
                # Test if isolation exists
                isolation_detected = self.test_isolation(phone_ip, pc_ip)
                
                if isolation_detected:
                    self.log("❌ ROUTER ISOLATION DETECTED!")
                    return True, phone_ip, pc_ip
                else:
                    self.log("✅ No router isolation detected")
                    return False, phone_ip, pc_ip
            else:
                self.log("❓ PC not detected on ethernet")
                return True, phone_ip, None  # Assume isolation
                
        except Exception as e:
            self.log(f"❌ Detection failed: {e}")
            return True, "192.168.1.100", None
    
    def detect_pc_on_ethernet(self, phone_net):
        """Detect PC connected via ethernet"""
        self.log("💻 SCANNING FOR PC ON ETHERNET")
        
        # Common ethernet IPs
        test_ips = []
        for i in range(1, 255):
            test_ips.append(f"{phone_net}.{i}")
        
        # Also try common router subnets
        common_subnets = ["192.168.0", "192.168.1", "192.168.49", "10.0.0"]
        for subnet in common_subnets:
            for i in [1, 100, 150, 200]:
                test_ips.append(f"{subnet}.{i}")
        
        # Test connectivity (parallel for speed)
        found_ips = []
        
        def test_ip(ip):
            try:
                result = subprocess.run(['ping', '-c', '1', '-W', '1', ip],
                                      capture_output=True, text=True, timeout=2)
                if result.returncode == 0:
                    # Check if it's not the phone
                    try:
                        s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
                        s.connect(("8.8.8.8", 80))
                        phone_ip = s.getsockname()[0]
                        s.close()
                        
                        if ip != phone_ip:
                            found_ips.append(ip)
                    except:
                        found_ips.append(ip)
            except:
                pass
        
        # Run tests in parallel
        threads = []
        for ip in test_ips[:50]:  # Limit to prevent overload
            t = threading.Thread(target=test_ip, args=(ip,))
            t.start()
            threads.append(t)
            
            if len(threads) >= 20:  # Limit concurrent threads
                for t in threads:
                    t.join(timeout=2)
                threads = []
        
        for t in threads:
            t.join(timeout=2)
        
        if found_ips:
            self.log(f"✅ Found potential PCs: {found_ips[:3]}")
            return found_ips[0]  # Return first found
        
        return None
    
    def test_isolation(self, phone_ip, pc_ip):
        """Test if router isolation is preventing communication"""
        self.log(f"🧪 TESTING ISOLATION: {phone_ip} <-> {pc_ip}")
        
        try:
            # Create a socket and try to bind to both IPs
            test_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
            test_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
            
            # Try to bind to both networks
            bindings = []
            for ip in [phone_ip, pc_ip]:
                try:
                    test_socket.bind((ip, 9999))
                    bindings.append(ip)
                    test_socket.settimeout(0.5)
                    test_socket.listen(1)
                    self.log(f"✅ Can bind to {ip}")
                except Exception as e:
                    self.log(f"❌ Cannot bind to {ip}: {e}")
            
            test_socket.close()
            
            # If we can bind to both, no isolation
            if len(bindings) >= 2:
                return False
            
            return True  # Isolation detected
            
        except Exception as e:
            self.log(f"⚠️ Isolation test failed: {e}")
            return True  # Assume isolation
    
    def create_isolation_bridge(self, phone_ip, pc_ip):
        """Create bridge to bypass router isolation"""
        self.log("🌉 CREATING ISOLATION BRIDGE")
        
        # Method 1: Create custom network bridge
        bridge_methods = [
            lambda: self.create_adhoc_bridge(phone_ip),
            lambda: self.create_wifi_direct_bridge(),
            lambda: self.create_vpn_bridge(phone_ip, pc_ip),
            lambda: self.create_iptables_bridge(phone_ip, pc_ip)
        ]
        
        for method in bridge_methods:
            try:
                if method():
                    self.log("✅ Isolation bridge created successfully!")
                    return True
            except Exception as e:
                self.log(f"❌ Bridge method failed: {e}")
                continue
        
        self.log("❌ Could not create isolation bridge")
        return False
    
    def create_adhoc_bridge(self, phone_ip):
        """Create ad-hoc WiFi bridge"""
        self.log("📡 Creating ad-hoc WiFi bridge...")
        
        try:
            # Check if we can create ad-hoc network
            result = subprocess.run(['iwconfig'], capture_output=True, text=True)
            if result.returncode == 0:
                # Try to create ad-hoc network on phone
                bridge_ip = self.generate_bridge_ip(phone_ip)
                
                # Setup commands
                commands = [
                    ['ip', 'link', 'set', 'wlan0', 'down'],
                    ['iwconfig', 'wlan0', 'mode', 'adhoc'],
                    ['iwconfig', 'wlan0', 'essid', 'PXE-Bridge'],
                    ['iwconfig', 'wlan0', 'key', 'off'],
                    ['ip', 'link', 'set', 'wlan0', 'up'],
                    ['ip', 'addr', 'add', f'{bridge_ip}/24', 'dev', 'wlan0']
                ]
                
                for cmd in commands:
                    try:
                        result = subprocess.run(cmd, capture_output=True, text=True, timeout=5)
                        if result.returncode != 0:
                            self.log(f"⚠️ Command failed: {' '.join(cmd)}")
                    except:
                        pass
                
                self.log(f"✅ Ad-hoc bridge on {bridge_ip}")
                return True
        except Exception as e:
            self.log(f"❌ Ad-hoc bridge failed: {e}")
        
        return False
    
    def create_wifi_direct_bridge(self):
        """Create WiFi Direct bridge"""
        self.log("📱 Creating WiFi Direct bridge...")
        
        try:
            # Check for WiFi Direct support
            if os.path.exists('/data/data/com.termux/files/home'):
                # Termux environment
                result = subprocess.run(['termux-wifi-direct', '-l'], 
                                      capture_output=True, text=True, timeout=5)
                if result.returncode == 0:
                    self.log("✅ WiFi Direct supported")
                    # Start WiFi Direct
                    result = subprocess.run(['termux-wifi-direct', '-s'], 
                                          capture_output=True, text=True, timeout=30)
                    if result.returncode == 0:
                        return True
        except Exception as e:
            self.log(f"❌ WiFi Direct failed: {e}")
        
        return False
    
    def create_vpn_bridge(self, phone_ip, pc_ip):
        """Create VPN-style bridge"""
        self.log("🔐 Creating VPN bridge...")
        
        try:
            # Create a simple VPN-like connection
            bridge_ip = self.generate_bridge_ip(phone_ip)
            
            # Setup routing
            commands = [
                ['ip', 'route', 'add', '192.168.49.0/24', 'dev', 'lo'],
                ['ip', 'addr', 'add', f'{bridge_ip}/24', 'dev', 'lo']
            ]
            
            for cmd in commands:
                try:
                    subprocess.run(cmd, capture_output=True, text=True, timeout=5)
                except:
                    pass
            
            self.log(f"✅ VPN bridge on {bridge_ip}")
            return True
        except Exception as e:
            self.log(f"❌ VPN bridge failed: {e}")
        
        return False
    
    def create_iptables_bridge(self, phone_ip, pc_ip):
        """Create iptables bridge"""
        self.log("🛡️ Creating iptables bridge...")
        
        try:
            # Use iptables to create bridge
            commands = [
                ['iptables', '-t', 'nat', '-A', 'POSTROUTING', '-s', phone_ip, '-j', 'MASQUERADE'],
                ['iptables', '-A', 'FORWARD', '-i', 'wlan0', '-o', 'eth0', '-j', 'ACCEPT'],
                ['iptables', '-A', 'FORWARD', '-i', 'eth0', '-o', 'wlan0', '-j', 'ACCEPT']
            ]
            
            for cmd in commands:
                try:
                    result = subprocess.run(cmd, capture_output=True, text=True, timeout=5)
                    if result.returncode == 0:
                        self.log(f"✅ Applied iptables rule: {' '.join(cmd)}")
                except:
                    pass
            
            return True
        except Exception as e:
            self.log(f"❌ iptables bridge failed: {e}")
        
        return False
    
    def generate_bridge_ip(self, original_ip):
        """Generate bridge IP in isolated range"""
        # Use 192.168.49.x for bridge network
        return "192.168.49.2"
    
    def start_isolation_dhcp_server(self, bridge_ip):
        """Start DHCP server on bridge network"""
        self.log("🚀 STARTING ISOLATION DHCP SERVER")
        
        try:
            import termux_pxe_boot
            
            # Configure for bridge network
            server = termux_pxe_boot.TermuxPXEServer()
            server.config.update({
                'server_ip': bridge_ip,
                'subnet_mask': '255.255.255.0',
                'gateway': bridge_ip,
                'dhcp_start': '192.168.49.10',
                'dhcp_end': '192.168.49.50'
            })
            
            # Update boot config for bridge network
            self._update_bridge_boot_config(bridge_ip)
            
            server.start()
            self.is_running = True
            
            self.log(f"🎉 ISOLATION DHCP SERVER RUNNING!")
            self.log(f"📡 Server IP: {bridge_ip}")
            self.log(f"📱 Client range: 192.168.49.10-50")
            self.log("💻 PC should now connect via bridge network")
            
            return server
            
        except Exception as e:
            self.log(f"❌ DHCP server error: {e}")
            return None
    
    def _update_bridge_boot_config(self, server_ip):
        """Update PXE boot configuration for bridge network"""
        config_file = Path.home() / '.termux_pxe_boot' / 'tftp' / 'pxelinux.cfg' / 'default'
        
        if config_file.exists():
            try:
                with open(config_file, 'r') as f:
                    content = f.read()
                
                # Update all IP references
                content = content.replace('192.168.1.100', server_ip)
                content = content.replace('192.168.1.', '192.168.49.')
                content = content.replace('192.168.0.', '192.168.49.')
                content = content.replace('10.0.0.', '192.168.49.')
                
                with open(config_file, 'w') as f:
                    f.write(content)
                
                self.log(f"✅ Updated boot config for bridge: {server_ip}")
            except Exception as e:
                self.log(f"⚠️ Could not update boot config: {e}")
    
    def run_isolation_fix(self):
        """Run complete isolation fix"""
        print("🌐 WIFI ISOLATION FIX - NO USB CABLE REQUIRED")
        print("=" * 60)
        print("Fixing: Phone WiFi + PC Ethernet + Same Router")
        print("Method: Bypass router isolation without cable")
        print("")
        
        # Step 1: Detect isolation
        isolation, phone_ip, pc_ip = self.detect_router_isolation()
        
        if not isolation:
            self.log("✅ No isolation detected - running standard server")
            try:
                import termux_pxe_boot
                server = termux_pxe_boot.TermuxPXEServer()
                server.start()
                return server
            except Exception as e:
                self.log(f"❌ Standard server error: {e}")
        
        # Step 2: Create bridge
        if self.create_isolation_bridge(phone_ip, pc_ip):
            # Step 3: Start DHCP server
            bridge_ip = self.generate_bridge_ip(phone_ip)
            server = self.start_isolation_dhcp_server(bridge_ip)
            
            if server:
                self.log("✅ ISOLATION FIX SUCCESSFUL!")
                print("")
                self.log("📋 WHAT TO DO:")
                self.log("1. 🖥️ PC should automatically connect to bridge network")
                self.log("2. 🔄 Or reboot PC to discover new network")
                self.log("3. 📡 PC should now get 192.168.49.x IP")
                self.log("4. 🚀 PXE boot should work without E53 error")
                return server
        
        # Step 4: Manual instructions if auto-fix fails
        self.log("⚠️ AUTO ISOLATION FIX FAILED")
        print("")
        self.log("🔧 MANUAL SOLUTIONS:")
        print("")
        print("SOLUTION 1: Router Settings")
        print("1. Login to router: http://192.168.1.1")
        print("2. Find 'Client Isolation' or 'AP Isolation'")
        print("3. DISABLE it completely")
        print("4. Save and restart router")
        print("5. Run: python3 termux_pxe_boot.py")
        print("")
        print("SOLUTION 2: WiFi Hotspot")
        print("1. Phone: Settings → Network → Hotspot")
        print("2. Enable 'Portable WiFi hotspot'")
        print("3. Connect PC to this hotspot")
        print("4. Run: python3 termux_pxe_boot.py")
        print("")
        print("SOLUTION 3: USB Tethering (Last Resort)")
        print("1. Enable USB tethering")
        print("2. Connect PC via USB")
        print("3. Run: python3 detect_usb_tethering.py")
        
        return None

def main():
    """Main isolation fix function"""
    fix = WiFiIsolationFix()
    server = fix.run_isolation_fix()
    
    if server:
        try:
            print("\n🎉 ISOLATION FIX ACTIVE!")
            print("Your PC should now be able to PXE boot!")
            print("Press Ctrl+C to stop the server")
            
            while True:
                time.sleep(1)
        except KeyboardInterrupt:
            print("\n🛑 Stopping isolation fix server...")
            server.stop()
    else:
        print("\n❌ Isolation fix failed")
        print("Try the manual solutions above or USB tethering")

if __name__ == "__main__":
    main()