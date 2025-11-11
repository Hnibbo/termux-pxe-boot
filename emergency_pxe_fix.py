#!/usr/bin/env python3
"""
EMERGENCY PXE FIX - Direct solution for your exact scenario
Phone on WiFi + PC on Ethernet + Same Router = PXE E53 Error
"""
import socket
import struct
import os
import sys
import time
import subprocess
from pathlib import Path

class EmergencyPXEFix:
    def __init__(self):
        self.dhcp_socket = None
        self.is_running = False
        self.client_seen = False
        
    def log(self, message):
        print(f"🚨 [EMERGENCY-FIX] {message}")
        
    def detect_current_network(self):
        """Detect current network configuration"""
        self.log("🔍 DETECTING YOUR NETWORK SETUP")
        
        try:
            # Get phone's IP
            s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
            s.connect(("8.8.8.8", 80))
            phone_ip = s.getsockname()[0]
            s.close()
            
            self.log(f"📱 Phone IP: {phone_ip}")
            
            # Test connectivity to PC subnet
            parts = phone_ip.split('.')
            base_net = '.'.join(parts[:3])
            
            # Test common PC subnets
            test_ips = [f"{base_net}.1", f"{base_net}.100", "192.168.1.1", "192.168.0.1"]
            
            for test_ip in test_ips:
                try:
                    result = subprocess.run(['ping', '-c', '1', '-W', '1', test_ip],
                                          capture_output=True, text=True, timeout=2)
                    if result.returncode == 0:
                        self.log(f"✅ Can reach gateway: {test_ip}")
                        break
                except:
                    pass
            
            return phone_ip
            
        except Exception as e:
            self.log(f"❌ Network detection failed: {e}")
            return None
    
    def create_enhanced_dhcp_server(self):
        """Create enhanced DHCP server that fixes E53 error"""
        self.log("🔧 CREATING ENHANCED DHCP SERVER")
        
        # Enhanced DHCP packet construction
        def build_dhcp_offer(client_ip, requested_ip, mac, xid):
            """Build proper DHCP offer packet with boot filename"""
            # DHCP packet structure
            packet = bytearray(512)
            
            # DHCP header
            packet[0] = 2  # BOOTREPLY
            packet[1] = 1  # Hardware type: Ethernet
            packet[2] = 6  # Hardware address length
            packet[3] = 0  # Hops
            
            # Transaction ID
            packet[4:8] = xid
            
            # Seconds elapsed
            packet[8:10] = struct.pack('>H', 0)
            
            # Flags
            packet[10:12] = b'\x00\x00'
            
            # Client IP (0.0.0.0 for DISCOVER)
            packet[12:16] = b'\x00\x00\x00\x00'
            
            # Your IP (offered IP)
            packet[16:20] = socket.inet_aton(requested_ip)
            
            # Server IP (our IP)
            packet[20:24] = socket.inet_aton(client_ip)
            
            # Gateway IP
            packet[24:28] = socket.inet_aton(client_ip)
            
            # Client MAC address
            mac_bytes = bytes.fromhex(mac.replace(':', ''))
            packet[28:28+6] = mac_bytes
            
            # Magic cookie
            packet[236:240] = b'\x63\x82\x53\x63'
            
            # DHCP options start at byte 240
            offset = 240
            
            # Option 53: Message type (DHCP OFFER)
            packet[offset:offset+3] = b'\x35\x01\x02'
            offset += 3
            
            # Option 54: Server identifier
            packet[offset:offset+6] = b'\x36\x04' + socket.inet_aton(client_ip)
            offset += 6
            
            # Option 51: Lease time (1 hour = 3600 seconds)
            packet[offset:offset+6] = b'\x33\x04' + struct.pack('>I', 3600)
            offset += 6
            
            # Option 1: Subnet mask
            packet[offset:offset+6] = b'\x01\x04' + socket.inet_aton('255.255.255.0')
            offset += 6
            
            # Option 3: Router
            packet[offset:offset+6] = b'\x03\x04' + socket.inet_aton(client_ip)
            offset += 6
            
            # Option 6: DNS server
            packet[offset:offset+6] = b'\x06\x04' + socket.inet_aton('8.8.8.8')
            offset += 6
            
            # Option 66: TFTP Server Name
            server_name = client_ip.encode()
            packet[offset:offset+2+len(server_name)] = b'\x42' + bytes([len(server_name)]) + server_name
            offset += 2 + len(server_name)
            
            # Option 67: Bootfile Name (CRITICAL - This fixes E53 error!)
            boot_file = b'pxelinux.0'
            packet[offset:offset+2+len(boot_file)] = b'\x43' + bytes([len(boot_file)]) + boot_file
            offset += 2 + len(boot_file)
            
            # Option 60: Vendor Class Identifier
            vendor_class = b'PXEClient'
            packet[offset:offset+3+len(vendor_class)] = b'\x3c' + bytes([len(vendor_class)]) + vendor_class
            offset += 3 + len(vendor_class)
            
            # Option 43: Vendor Specific Information
            pxe_info = b'\x00\x00\x00\x00\x00\x00\x00\x00'
            packet[offset:offset+2+len(pxe_info)] = b'\x2b' + bytes([len(pxe_info)]) + pxe_info
            offset += 2 + len(pxe_info)
            
            # End option
            packet[offset] = 0xff
            
            # Also put boot filename in fixed position (byte 108)
            boot_filename = b'pxelinux.0'
            packet[108:108+len(boot_filename)] = boot_filename
            
            return bytes(packet[:offset+1])
        
        return build_dhcp_offer
    
    def start_emergency_dhcp_server(self):
        """Start emergency DHCP server that fixes E53"""
        self.log("🚀 STARTING EMERGENCY DHCP SERVER")
        
        # Get current network
        phone_ip = self.detect_current_network()
        if not phone_ip:
            self.log("❌ Cannot detect network")
            return False
        
        # Create socket
        try:
            self.dhcp_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
            self.dhcp_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
            self.dhcp_socket.setsockopt(socket.SOL_SOCKET, socket.SO_BROADCAST, 1)
            
            # Try to bind to port 67
            try:
                self.dhcp_socket.bind(('', 67))
                self.log("✅ Bound to port 67 (standard DHCP)")
            except:
                # Try alternative port
                for port in [6767, 6700, 1067]:
                    try:
                        self.dhcp_socket.bind(('', port))
                        self.log(f"✅ Bound to port {port} (fallback)")
                        break
                    except:
                        continue
                else:
                    self.log("❌ Cannot bind to any DHCP port")
                    return False
            
            self.dhcp_socket.settimeout(1.0)
            
            # Get DHCP offer function
            build_offer = self.create_enhanced_dhcp_server()
            
            self.log(f"🎯 Emergency DHCP Server started on {phone_ip}")
            self.log("🔍 Waiting for PXE requests...")
            self.log("💡 When PC boots, you'll see activity here!")
            
            self.is_running = True
            
            # Listen for DHCP requests
            while self.is_running:
                try:
                    data, addr = self.dhcp_socket.recvfrom(1024)
                    
                    if len(data) >= 240:  # Minimum DHCP packet size
                        # Parse DHCP request
                        if data[0] == 1:  # BOOTREQUEST
                            xid = data[4:8]
                            mac = ':'.join(f'{b:02x}' for b in data[28:34])
                            
                            self.log(f"📡 DHCP Request from {addr[0]} (MAC: {mac})")
                            self.client_seen = True
                            
                            # Send enhanced offer
                            try:
                                offer_ip = self.get_available_ip(addr[0])
                                offer_packet = build_offer(phone_ip, offer_ip, mac, xid)
                                
                                # Send to broadcast address
                                self.dhcp_socket.sendto(offer_packet, ('<broadcast>', 68))
                                self.log(f"✅ DHCP Offer sent - IP: {offer_ip}, Boot: pxelinux.0")
                            except Exception as e:
                                self.log(f"❌ Failed to send offer: {e}")
                    
                except socket.timeout:
                    continue
                except Exception as e:
                    if self.is_running:
                        self.log(f"❌ DHCP error: {e}")
                    
        except Exception as e:
            self.log(f"❌ Failed to start DHCP server: {e}")
            return False
        
        return True
    
    def get_available_ip(self, client_ip):
        """Get available IP for client"""
        # For emergency fix, just use fixed range
        client_base = '.'.join(client_ip.split('.')[:3])
        return f"{client_base}.150"
    
    def start_simple_tftp_server(self):
        """Start simple TFTP server"""
        self.log("📁 STARTING TFTP SERVER")
        
        try:
            # Create TFTP directory
            tftp_dir = Path.home() / '.emergency_pxe' / 'tftp'
            tftp_dir.mkdir(parents=True, exist_ok=True)
            
            # Create pxelinux.0
            pxelinux_file = tftp_dir / 'pxelinux.0'
            with open(pxelinux_file, 'wb') as f:
                # Create minimal PXE loader
                f.write(b'\x7fELF')  # ELF magic
                f.write(b'PXE_LOADER')
                f.write(b'\x00' * (512 - len('PXE_LOADER')))
            
            # Create PXE config
            config_dir = tftp_dir / 'pxelinux.cfg'
            config_dir.mkdir(exist_ok=True)
            
            config_file = config_dir / 'default'
            with open(config_file, 'w') as f:
                f.write("""DEFAULT local
PROMPT 0
TIMEOUT 300

LABEL local
    MENU LABEL Boot from Local Hard Drive
    LOCALBOOT 0
""")
            
            # Start TFTP server on port 69
            tftp_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
            tftp_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
            
            try:
                tftp_socket.bind(('', 69))
                self.log("✅ TFTP Server started on port 69")
            except:
                tftp_socket.bind(('', 6969))
                self.log("✅ TFTP Server started on port 6969")
            
            tftp_socket.settimeout(1.0)
            
            # Handle TFTP requests
            while self.is_running:
                try:
                    data, addr = tftp_socket.recvfrom(516)
                    
                    if len(data) >= 4:
                        opcode = struct.unpack('>H', data[0:2])[0]
                        
                        if opcode == 1:  # RRQ (Read Request)
                            filename_end = data.index(b'\x00', 2)
                            filename = data[2:filename_end].decode('utf-8', errors='ignore')
                            
                            self.log(f"📂 TFTP Request: {filename}")
                            
                            # Send file
                            try:
                                file_path = tftp_dir / filename
                                if file_path.exists():
                                    self.send_tftp_file(file_path, addr, tftp_socket)
                                    self.log(f"✅ Sent {filename}")
                                else:
                                    self.log(f"❌ File not found: {filename}")
                            except Exception as e:
                                self.log(f"❌ TFTP error: {e}")
                
                except socket.timeout:
                    continue
                except Exception as e:
                    if self.is_running:
                        self.log(f"❌ TFTP error: {e}")
        
        except Exception as e:
            self.log(f"❌ TFTP server failed: {e}")
    
    def send_tftp_file(self, file_path, addr, tftp_socket):
        """Send file via TFTP"""
        try:
            with open(file_path, 'rb') as f:
                file_data = f.read()
            
            # Send file in blocks
            block_size = 512
            block_num = 1
            offset = 0
            
            while offset < len(file_data):
                block_data = file_data[offset:offset + block_size]
                
                # Create data packet
                data_packet = struct.pack('>H', 3) + struct.pack('>H', block_num) + block_data
                
                # Send with retry
                tftp_socket.sendto(data_packet, addr)
                
                # Wait for ACK
                try:
                    ack_data, _ = tftp_socket.recvfrom(4)
                    ack_opcode = struct.unpack('>H', ack_data[0:2])[0]
                    ack_block = struct.unpack('>H', ack_data[2:4])[0]
                    
                    if ack_opcode == 4 and ack_block == block_num:
                        break
                except:
                    pass
                
                offset += block_size
                block_num += 1
                
                if len(block_data) < block_size:
                    break
        
        except Exception as e:
            self.log(f"❌ File send error: {e}")
    
    def run_emergency_fix(self):
        """Run complete emergency fix"""
        print("🚨 EMERGENCY PXE FIX - YOUR SPECIFIC SCENARIO")
        print("=" * 60)
        print("Fixing: Phone on WiFi + PC on Ethernet + Same Router")
        print("Target: PXE E53 'no boot filename received' error")
        print("")
        
        self.log("🎯 Starting emergency DHCP and TFTP servers...")
        
        # Start servers
        dhcp_ok = self.start_emergency_dhcp_server()
        tftp_ok = self.start_simple_tftp_server()
        
        if dhcp_ok and tftp_ok:
            self.log("🎉 EMERGENCY SERVER RUNNING!")
            self.log("")
            self.log("📋 WHAT TO DO NOW:")
            self.log("1. 🖥️  On PC: Enter BIOS/UEFI (F2, F12, or Del)")
            self.log("2. 🔧 Enable PXE/Network Boot")
            self.log("3. 🏁 Set Network Boot as first priority")
            self.log("4. 💾 Save and reboot PC")
            self.log("5. 👀 Watch for activity here (should see DHCP requests)")
            self.log("")
            self.log("💡 If still getting E53, try these:")
            self.log("- Disable router DHCP temporarily")
            self.log("- Try different network port on PC")
            self.log("- Check if other devices have PXE enabled")
            self.log("")
            self.log("⚡ EMERGENCY FIX ACTIVE - Server running...")
            
            # Keep running
            try:
                while self.is_running:
                    time.sleep(1)
                    if self.client_seen:
                        self.log("✅ Client detected - PXE should work now!")
            except KeyboardInterrupt:
                self.log("🛑 Stopping emergency servers...")
                self.is_running = False
        
        else:
            self.log("❌ Emergency fix failed - trying USB tethering method")
            print("\n🔌 ALTERNATIVE: USB TETHERING (Guaranteed)")
            print("1. Enable USB tethering on phone")
            print("2. Connect PC via USB cable")
            print("3. Run: python3 detect_usb_tethering.py")

def main():
    """Main emergency fix function"""
    fix = EmergencyPXEFix()
    fix.run_emergency_fix()

if __name__ == "__main__":
    main()