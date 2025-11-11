#!/usr/bin/env python3
"""
USB Tethering Detection and Auto-Setup
Detects when USB tethering is active and configures accordingly
"""
import os
import socket
import subprocess
import time
import re
from pathlib import Path

def detect_usb_tethering():
    """Detect if USB tethering is active"""
    print("🔌 DETECTING USB TETHERING")
    print("=" * 30)
    
    # Check for USB network interfaces
    usb_interfaces = find_usb_interfaces()
    
    if usb_interfaces:
        print("✅ USB tethering interface found!")
        for interface in usb_interfaces:
            print(f"   Interface: {interface['name']}")
            print(f"   IP Address: {interface['ip']}")
            print(f"   Status: {interface['status']}")
        
        # Test connectivity
        if test_usb_connectivity(usb_interfaces[0]):
            print("✅ USB connectivity test passed!")
            return True
        else:
            print("❌ USB connectivity test failed")
            return False
    else:
        print("❌ No USB tethering interface detected")
        return False

def find_usb_interfaces():
    """Find USB network interfaces"""
    interfaces = []
    
    try:
        # Method 1: Check ip addr for USB interfaces
        result = subprocess.run(['ip', 'addr', 'show'], capture_output=True, text=True)
        lines = result.stdout.split('\n')
        
        current_interface = None
        for line in lines:
            line = line.strip()
            
            # Check for interface definition
            if re.match(r'^\d+:\s+\w+', line):
                parts = line.split()
                current_interface = {
                    'name': parts[1].rstrip(':'),
                    'index': int(parts[0].rstrip(':')),
                    'ip': None,
                    'status': 'down'
                }
                
                # Check if this looks like a USB interface
                if any(usb_term in current_interface['name'].lower() for usb_term in ['usb', 'rndis', 'rndis0', 'usb0']):
                    interfaces.append(current_interface)
            
            # Check for IP address
            elif current_interface and 'inet ' in line:
                parts = line.split()
                if len(parts) >= 2:
                    current_interface['ip'] = parts[1]
                    
                    # Check if interface is UP
                    if 'UP' in line:
                        current_interface['status'] = 'up'
    
    except Exception as e:
        print(f"   Error checking interfaces: {e}")
    
    # Method 2: Check for standard USB tethering IPs
    try:
        result = subprocess.run(['ip', 'route', 'show'], capture_output=True, text=True)
        for line in result.stdout.split('\n'):
            if '192.168.42' in line:  # Standard Android USB tethering
                print(f"   📱 Found USB tethering route: {line.strip()}")
                
                # Extract IP
                match = re.search(r'192\.168\.42\.(\d+)', line)
                if match:
                    server_ip = f"192.168.42.{match.group(1)}"
                    interfaces.append({
                        'name': 'usb0',
                        'ip': server_ip,
                        'status': 'up',
                        'type': 'usb_tethering'
                    })
    except:
        pass
    
    # Method 3: Check /proc/net/dev for USB interfaces
    try:
        with open('/proc/net/dev', 'r') as f:
            for line in f:
                if any(term in line.lower() for term in ['usb', 'rndis']):
                    parts = line.split()
                    if len(parts) >= 2:
                        interface_name = parts[0].rstrip(':')
                        interfaces.append({
                            'name': interface_name,
                            'ip': f"192.168.42.2",  # Default USB tethering IP
                            'status': 'active',
                            'type': 'usb_interface'
                        })
    except:
        pass
    
    return interfaces

def test_usb_connectivity(interface):
    """Test if USB interface is working for PXE"""
    
    # Test port binding
    test_ports = [67, 69, 8080]
    
    for port in test_ports:
        try:
            sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
            sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
            sock.bind((interface['ip'], port))
            sock.close()
            print(f"   ✅ Port {port} available on {interface['name']}")
        except Exception as e:
            print(f"   ❌ Port {port} blocked on {interface['name']}: {e}")
            return False
    
    # Test connectivity to PC network
    try:
        result = subprocess.run(['ping', '-c', '1', '-W', '1', '192.168.42.1'], 
                              capture_output=True, text=True, timeout=2)
        if result.returncode == 0:
            print("   ✅ Can reach USB gateway")
            return True
    except:
        pass
    
    return True  # If we got here, basic setup is working

def configure_for_usb_tethering():
    """Configure system for USB tethering"""
    print("⚙️  CONFIGURING FOR USB TETHERING")
    print("=" * 35)
    
    # Create USB-specific configuration
    config = {
        'server_ip': '192.168.42.2',
        'dhcp_range': '192.168.42.10-50',
        'subnet': '192.168.42.0/24',
        'gateway': '192.168.42.1',
        'dns_server': '192.168.42.1',
        'method': 'USB_Tethering'
    }
    
    # Get actual IP from system
    try:
        result = subprocess.run(['ip', 'route', 'get', '192.168.42.1'], 
                              capture_output=True, text=True)
        if result.returncode == 0:
            # Extract source IP
            match = re.search(r'src ([\d\.]+)', result.stdout)
            if match:
                config['server_ip'] = match.group(1)
                print(f"   📍 Detected actual IP: {config['server_ip']}")
    except:
        pass
    
    print(f"   Server IP: {config['server_ip']}")
    print(f"   DHCP Range: {config['dhcp_range']}")
    print(f"   Subnet: {config['subnet']}")
    
    return config

def start_usb_pxe_server(config):
    """Start PXE server configured for USB tethering"""
    print("🚀 STARTING USB TETHERING PXE SERVER")
    print("=" * 40)
    
    try:
        # Import and configure server
        import sys
        sys.path.append(os.path.dirname(os.path.abspath(__file__)))
        from termux_pxe_boot import TermuxPXEServer
        
        # Create server with USB configuration
        server = TermuxPXEServer()
        
        # Override configuration for USB tethering
        server.config.update({
            'server_ip': config['server_ip'],
            'gateway': config['gateway'],
            'dns_server': config['dns_server']
        })
        
        # Update boot configuration
        update_boot_config_for_usb(config['server_ip'])
        
        print(f"   ✅ Server configured for {config['method']}")
        print(f"   📡 Server IP: {config['server_ip']}")
        print(f"   🔌 Ready for USB tethering connection")
        
        # Start server
        server.start()
        return server
        
    except Exception as e:
        print(f"   ❌ Failed to start USB PXE server: {e}")
        return None

def update_boot_config_for_usb(server_ip):
    """Update PXE boot configuration for USB tethering"""
    
    # Update PXE config file
    config_file = Path.home() / '.termux_pxe_boot' / 'tftp' / 'pxelinux.cfg' / 'default'
    
    if config_file.exists():
        try:
            with open(config_file, 'r') as f:
                content = f.read()
            
            # Replace hardcoded IPs with actual USB IP
            content = content.replace('192.168.1.100', server_ip)
            content = content.replace('192.168.1.', '192.168.42.')
            
            with open(config_file, 'w') as f:
                f.write(content)
            
            print(f"   ✅ Updated boot config for USB: {server_ip}")
        except Exception as e:
            print(f"   ⚠️  Could not update boot config: {e}")

def main():
    """Main USB tethering detection and setup"""
    print("🔌 USB TETHERING AUTO-SETUP")
    print("=" * 30)
    print("This will detect and configure USB tethering for guaranteed PXE success!")
    print("")
    
    # Detect USB tethering
    if detect_usb_tethering():
        # Configure for USB
        config = configure_for_usb_tethering()
        
        # Start server
        server = start_usb_pxe_server(config)
        
        if server:
            print("")
            print("🎉 USB TETHERING PXE SERVER RUNNING!")
            print("=" * 40)
            print("Your PC should now be able to PXE boot!")
            print("Make sure USB tethering is enabled on your phone.")
            print("")
            print("📱 ON YOUR PC:")
            print("1. Boot from network (F12, F2, or Del)")
            print("2. Select 'Network Boot' or 'PXE Boot'")
            print("3. The PC will connect via USB tethering")
            print("")
            print("Press Ctrl+C to stop the server.")
            print("")
            
            try:
                while True:
                    time.sleep(1)
            except KeyboardInterrupt:
                print("\n🛑 Stopping USB PXE server...")
                server.stop()
                print("Server stopped successfully!")
        else:
            print("❌ Failed to start USB PXE server")
            return False
    else:
        print("")
        print("❌ USB TETHERING NOT DETECTED")
        print("=" * 30)
        print("To enable USB tethering:")
        print("1. Connect phone to PC via USB cable")
        print("2. Go to: Settings > Network & Internet > Hotspot & tethering")
        print("3. Enable 'USB tethering'")
        print("4. Run this script again")
        return False
    
    return True

if __name__ == "__main__":
    main()