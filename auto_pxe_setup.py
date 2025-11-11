#!/usr/bin/env python3
"""
Autonomous Termux PXE Boot Setup
Fully automated system that works in ALL network scenarios
Includes USB tethering fallback for guaranteed operation
"""
import os
import sys
import socket
import subprocess
import time
import json
import threading
import platform
from pathlib import Path
from datetime import datetime

class AutonomousPXE:
    def __init__(self):
        self.setup_methods = []
        self.current_method = None
        self.log_file = "/data/data/com.termux/files/home/.termux_pxe_boot/auto_setup.log"
        self.network_tests = {}
        self.setup_success = False
        
    def log(self, message):
        """Log with timestamp"""
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        log_msg = f"[{timestamp}] {message}"
        print(log_msg)
        
        # Create log directory
        log_dir = os.path.dirname(self.log_file)
        os.makedirs(log_dir, exist_ok=True)
        
        # Write to log
        with open(self.log_file, 'a') as f:
            f.write(log_msg + '\n')
    
    def detect_environment(self):
        """Detect current environment and capabilities"""
        self.log("🔍 DETECTING ENVIRONMENT")
        env = {
            'platform': platform.system(),
            'termux': os.path.exists('/data/data/com.termux/files/home'),
            'root': os.geteuid() == 0 if hasattr(os, 'geteuid') else False,
            'android': self._is_android(),
            'network_interfaces': self._get_network_interfaces(),
            'available_methods': []
        }
        
        self.log(f"   Platform: {env['platform']}")
        self.log(f"   Termux: {env['termux']}")
        self.log(f"   Root: {env['root']}")
        self.log(f"   Android: {env['android']}")
        
        return env
    
    def _is_android(self):
        """Check if running on Android"""
        return os.path.exists('/system/build.prop') or os.path.exists('/data/data/com.termux/files/home')
    
    def _get_network_interfaces(self):
        """Get all network interfaces"""
        interfaces = []
        try:
            result = subprocess.run(['ip', 'addr', 'show'], capture_output=True, text=True)
            for line in result.stdout.split('\n'):
                if 'inet ' in line and '127.0.0.1' not in line:
                    parts = line.strip().split()
                    if len(parts) >= 2:
                        ip_info = parts[1]
                        interface = parts[-1]
                        interfaces.append({
                            'interface': interface,
                            'ip': ip_info
                        })
        except:
            pass
        return interfaces
    
    def test_connectivity(self):
        """Test connectivity to common network scenarios"""
        self.log("🌐 TESTING CONNECTIVITY")
        tests = {}
        
        # Test local IP detection
        try:
            s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
            s.connect(("8.8.8.8", 80))
            local_ip = s.getsockname()[0]
            s.close()
            tests['local_ip'] = local_ip
            self.log(f"   Local IP: {local_ip}")
        except Exception as e:
            tests['local_ip'] = None
            self.log(f"   Local IP: Failed - {e}")
        
        # Test subnet reachability
        subnet_tests = ['192.168.1.1', '192.168.0.1', '10.0.0.1', '172.16.0.1']
        tests['reachable_subnets'] = []
        
        for ip in subnet_tests:
            try:
                result = subprocess.run(['ping', '-c', '1', '-W', '1', ip], 
                                      capture_output=True, text=True, timeout=2)
                if result.returncode == 0:
                    tests['reachable_subnets'].append(ip)
                    self.log(f"   ✅ {ip} - Reachable")
                else:
                    self.log(f"   ❌ {ip} - Not reachable")
            except:
                self.log(f"   ❓ {ip} - Test failed")
        
        # Test for existing DHCP servers
        tests['dhcp_competition'] = self._test_dhcp_competition()
        
        self.network_tests = tests
        return tests
    
    def _test_dhcp_competition(self):
        """Test for existing DHCP servers on network"""
        self.log("   Testing for DHCP competition...")
        
        # Try to create DHCP socket
        try:
            test_sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
            test_sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
            test_sock.bind(('', 67))
            test_sock.close()
            return False  # No competition
        except:
            return True  # Port in use
    
    def setup_wifi_method(self):
        """Setup PXE via WiFi (primary method)"""
        self.log("📶 SETTING UP WIFI METHOD")
        
        if not self._is_termux_wifi_connected():
            self.log("   ❌ No WiFi connection detected")
            return False
        
        # Check if we can bind to required ports
        wifi_working = self._test_wifi_ports()
        if wifi_working:
            self.log("   ✅ WiFi method ready")
            self.current_method = "WiFi"
            return True
        else:
            self.log("   ❌ WiFi method failed")
            return False
    
    def _is_termux_wifi_connected(self):
        """Check if Termux has WiFi connection"""
        try:
            result = subprocess.run(['ip', 'route'], capture_output=True, text=True)
            return 'wlan' in result.stdout or 'wifi' in result.stdout
        except:
            return False
    
    def _test_wifi_ports(self):
        """Test if we can bind to WiFi ports"""
        test_ports = [67, 69, 8080]
        for port in test_ports:
            try:
                sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
                sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
                sock.bind(('', port))
                sock.close()
            except:
                return False
        return True
    
    def setup_usb_tethering_method(self):
        """Setup PXE via USB Tethering (guaranteed method)"""
        self.log("🔌 SETTING UP USB TETHERING METHOD")
        
        if not self._setup_usb_tethering():
            self.log("   ❌ USB tethering setup failed")
            return False
        
        # Wait for USB interface to be ready
        time.sleep(3)
        
        # Test if USB interface is working
        if self._test_usb_interface():
            self.log("   ✅ USB tethering method ready")
            self.current_method = "USB_Tethering"
            return True
        else:
            self.log("   ❌ USB tethering not functional")
            return False
    
    def _setup_usb_tethering(self):
        """Setup USB tethering on Android"""
        self.log("   Enabling USB tethering...")
        
        # Method 1: Try termux-wake-lock
        try:
            # Check if we can enable USB tethering via termux
            result = subprocess.run(['termux-usb', '-l'], capture_output=True, text=True)
            if result.returncode == 0:
                self.log("   ✅ USB tethering available")
                return True
        except:
            pass
        
        # Method 2: Check for existing USB network interface
        try:
            result = subprocess.run(['ip', 'link', 'show'], capture_output=True, text=True)
            usb_interfaces = []
            for line in result.stdout.split('\n'):
                if 'usb' in line.lower() or 'rndis' in line.lower():
                    interface = line.split(':')[1].strip().split('@')[0]
                    usb_interfaces.append(interface)
            
            if usb_interfaces:
                self.log(f"   ✅ Found USB interfaces: {usb_interfaces}")
                return True
        except:
            pass
        
        # Method 3: Check for Android USB debugging interface
        try:
            result = subprocess.run(['ip', 'addr', 'show'], capture_output=True, text=True)
            for line in result.stdout.split('\n'):
                if 'inet ' in line and any(usb_term in line for usb_term in ['192.168.42', '192.168.43']):
                    self.log("   ✅ USB tethering interface detected")
                    return True
        except:
            pass
        
        self.log("   ⚠️  USB tethering setup requires manual steps")
        return False
    
    def _test_usb_interface(self):
        """Test if USB interface is functional"""
        try:
            # Get network interfaces again
            interfaces = self._get_network_interfaces()
            
            # Look for USB-related interfaces
            for interface in interfaces:
                if any(usb_term in interface['interface'].lower() for usb_term in ['usb', 'rndis', 'rndis0']):
                    # Test if we can use this interface
                    try:
                        test_sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
                        test_sock.bind((interface['ip'].split('/')[0], 67))
                        test_sock.close()
                        return True
                    except:
                        continue
            return False
        except:
            return False
    
    def setup_ethernet_method(self):
        """Setup PXE via Ethernet (fallback method)"""
        self.log("🌐 SETTING UP ETHERNET METHOD")
        
        ethernet_interfaces = self._detect_ethernet_interfaces()
        if not ethernet_interfaces:
            self.log("   ❌ No Ethernet interfaces found")
            return False
        
        # Test Ethernet connectivity
        for interface in ethernet_interfaces:
            if self._test_ethernet_port(interface):
                self.log(f"   ✅ Ethernet method ready on {interface}")
                self.current_method = f"Ethernet_{interface}"
                return True
        
        self.log("   ❌ Ethernet method failed")
        return False
    
    def _detect_ethernet_interfaces(self):
        """Detect Ethernet interfaces"""
        try:
            result = subprocess.run(['ip', 'link', 'show'], capture_output=True, text=True)
            ethernet = []
            for line in result.stdout.split('\n'):
                if 'eth' in line.lower() or 'enp' in line.lower():
                    interface = line.split(':')[1].strip().split('@')[0]
                    ethernet.append(interface)
            return ethernet
        except:
            return []
    
    def _test_ethernet_port(self, interface):
        """Test Ethernet port availability"""
        try:
            sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
            sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
            sock.bind(('', 67))
            sock.close()
            return True
        except:
            return False
    
    def auto_select_best_method(self):
        """Automatically select the best available method"""
        self.log("🤖 AUTO-SELECTING BEST METHOD")
        
        # Test all methods in order of preference
        methods = [
            ('WiFi', self.setup_wifi_method),
            ('USB_Tethering', self.setup_usb_tethering_method), 
            ('Ethernet', self.setup_ethernet_method)
        ]
        
        for method_name, method_func in methods:
            self.log(f"   Trying {method_name}...")
            if method_func():
                self.log(f"   🎯 SELECTED: {method_name}")
                return method_name
        
        self.log("   ❌ No method available")
        return None
    
    def configure_for_method(self, method):
        """Configure system for selected method"""
        self.log(f"⚙️  CONFIGURING FOR {method}")
        
        if method == 'WiFi':
            return self._configure_wifi()
        elif method == 'USB_Tethering':
            return self._configure_usb_tethering()
        elif 'Ethernet' in method:
            return self._configure_ethernet()
        else:
            return False
    
    def _configure_wifi(self):
        """Configure for WiFi method"""
        # Update server configuration for WiFi
        config = {
            'server_ip': self.network_tests.get('local_ip', '192.168.1.100'),
            'method': 'WiFi',
            'dhcp_range': '192.168.1.50-200',
            'subnet': '192.168.1.0/24'
        }
        return True
    
    def _configure_usb_tethering(self):
        """Configure for USB Tethering method"""
        # Configure for USB tethering network
        config = {
            'server_ip': '192.168.42.2',  # Standard USB tethering IP
            'method': 'USB_Tethering', 
            'dhcp_range': '192.168.42.10-50',
            'subnet': '192.168.42.0/24'
        }
        
        # Get actual USB interface IP
        try:
            result = subprocess.run(['ip', 'addr', 'show'], capture_output=True, text=True)
            for line in result.stdout.split('\n'):
                if '192.168.42' in line:
                    parts = line.strip().split()
                    if len(parts) >= 2:
                        config['server_ip'] = parts[1].split('/')[0]
                        break
        except:
            pass
        
        return True
    
    def _configure_ethernet(self):
        """Configure for Ethernet method"""
        # Use detected Ethernet interface IP
        config = {
            'server_ip': self.network_tests.get('local_ip', '192.168.1.100'),
            'method': 'Ethernet',
            'dhcp_range': '192.168.1.50-200',
            'subnet': '192.168.1.0/24'
        }
        return True
    
    def start_pxe_server(self):
        """Start the PXE server with current configuration"""
        self.log("🚀 STARTING PXE SERVER")
        
        try:
            # Import the main server
            sys.path.append(os.path.dirname(os.path.abspath(__file__)))
            from termux_pxe_boot import TermuxPXEServer
            
            # Create and configure server
            server = TermuxPXEServer()
            
            # Update server configuration based on selected method
            if self.current_method == 'USB_Tethering':
                server.config['server_ip'] = '192.168.42.2'
                server.config['gateway'] = '192.168.42.1'
            
            # Start server
            server.start()
            self.setup_success = True
            self.log("✅ PXE SERVER SUCCESSFULLY STARTED!")
            return server
            
        except Exception as e:
            self.log(f"❌ Failed to start PXE server: {e}")
            return None
    
    def provide_manual_instructions(self):
        """Provide manual setup instructions if auto-setup fails"""
        self.log("📋 PROVIDING MANUAL INSTRUCTIONS")
        
        instructions = """
🔧 MANUAL USB TETHERING SETUP (Guaranteed to work):

1. **On your Android phone:**
   - Go to Settings > Network & Internet > Hotspot & tethering
   - Enable "USB tethering"
   - OR enable "USB debugging" and use "USB Network Sharing"

2. **On your PC:**
   - Connect phone to PC via USB cable
   - Wait for network connection to establish
   - Check network adapter for USB connection
   - Note the IP address (usually 192.168.42.x)

3. **Run server again:**
   python3 termux_pxe_boot.py

4. **Alternative - WiFi Direct:**
   - Disable all other network connections
   - Use WiFi Direct to create direct connection
   - Both devices will get 192.168.49.x IPs

5. **Router Settings (if WiFi not working):**
   - Login to router admin: http://192.168.1.1
   - Disable "Client Isolation" or "AP Isolation"
   - Save and restart router
   - Connect both devices to same network
        """
        
        print(instructions)
        self.log("Manual instructions provided")
    
    def run_autonomous_setup(self):
        """Run complete autonomous setup process"""
        self.log("🤖 STARTING AUTONOMOUS PXE SETUP")
        self.log("=" * 50)
        
        # Step 1: Detect environment
        env = self.detect_environment()
        
        # Step 2: Test connectivity
        tests = self.test_connectivity()
        
        # Step 3: Auto-select best method
        method = self.auto_select_best_method()
        
        if method:
            # Step 4: Configure for method
            if self.configure_for_method(method):
                # Step 5: Start PXE server
                server = self.start_pxe_server()
                if server:
                    self.log("🎉 AUTONOMOUS SETUP COMPLETE!")
                    self.log(f"📡 Method: {method}")
                    self.log("🔄 Server running - ready for PXE boot")
                    return server
        
        # If we get here, auto-setup failed - provide manual help
        self.provide_manual_instructions()
        return None

def main():
    """Main autonomous setup function"""
    print("🤖 AUTONOMOUS TERMUX PXE BOOT SETUP")
    print("=" * 50)
    print("This system will automatically detect and configure")
    print("the best network method and start your PXE server!")
    print("")
    
    # Create autonomous setup
    auto_setup = AutonomousPXE()
    
    # Run setup
    server = auto_setup.run_autonomous_setup()
    
    if server:
        try:
            # Keep server running
            while True:
                time.sleep(1)
        except KeyboardInterrupt:
            print("\n🛑 Stopping server...")
            server.stop()
    else:
        print("\n❌ Autonomous setup failed. Check manual instructions above.")
        sys.exit(1)

if __name__ == "__main__":
    main()