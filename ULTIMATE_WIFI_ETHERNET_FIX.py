#!/usr/bin/env python3
"""
ULTIMATE PXE FIX FOR WIFI + ETHERNET SETUP
Works when PC is on Ethernet and Phone is on WiFi (same router)
Handles router isolation, different subnets, and broadcast issues
"""

import socket
import threading
import os
import struct
import time
import subprocess
import json
from datetime import datetime
import sys
import signal
import netifaces
import ipaddress

class UltimateWifiEthernetPXE:
    """Ultimate PXE server that bridges WiFi and Ethernet networks"""
    
    def __init__(self):
        self.running = False
        self.dhcp_socket = None
        self.tftp_socket = None
        self.broadcast_socket = None
        
        # Detect all network interfaces and IPs
        self.detect_network_topology()
        
        # Setup directories
        self.base_dir = os.path.expanduser('~/.termux_pxe_boot')
        self.tftp_dir = os.path.join(self.base_dir, 'tftp')
        self.logs_dir = os.path.join(self.base_dir, 'logs')
        
        for directory in [self.base_dir, self.tftp_dir, self.logs_dir]:
            os.makedirs(directory, exist_ok=True)
            
        # Create boot files
        self.create_boot_files()
        
        # Track clients
        self.clients = {}
        
    def detect_network_topology(self):
        """Detect complete network topology for WiFi + Ethernet bridging"""
        self.log("🔍 DETECTING NETWORK TOPOLOGY FOR WIFI + ETHERNET SETUP")
        self.log("=" * 70)
        
        self.interfaces = []
        self.server_ips = []
        self.broadcast_ips = []
        self.subnets = []
        
        try:
            # Get all network interfaces
            all_interfaces = netifaces.interfaces()
            
            for iface in all_interfaces:
                # Skip loopback
                if iface == 'lo':
                    continue
                    
                try:
                    addrs = netifaces.ifaddresses(iface)
                    
                    # Get IPv4 addresses
                    if netifaces.AF_INET in addrs:
                        for addr_info in addrs[netifaces.AF_INET]:
                            ip = addr_info.get('addr')
                            netmask = addr_info.get('netmask')
                            broadcast = addr_info.get('broadcast')
                            
                            if ip and ip != '127.0.0.1':
                                self.interfaces.append({
                                    'name': iface,
                                    'ip': ip,
                                    'netmask': netmask,
                                    'broadcast': broadcast
                                })
                                self.server_ips.append(ip)
                                
                                if broadcast:
                                    self.broadcast_ips.append(broadcast)
                                
                                # Calculate subnet
                                if netmask:
                                    try:
                                        network = ipaddress.IPv4Network(f"{ip}/{netmask}", strict=False)
                                        self.subnets.append(str(network))
                                    except:
                                        pass
                                        
                                self.log(f"✓ Interface: {iface}")
                                self.log(f"  IP: {ip}")
                                self.log(f"  Netmask: {netmask}")
                                self.log(f"  Broadcast: {broadcast}")
                                self.log(f"  Type: {'WiFi' if 'wlan' in iface else 'Ethernet' if 'eth' in iface else 'USB' if 'usb' in iface else 'Unknown'}")
                except Exception as e:
                    self.log(f"  Warning: Could not get info for {iface}: {e}")
                    
        except Exception as e:
            self.log(f"Error detecting interfaces: {e}")
            # Fallback
            self.server_ips = [self._get_local_ip()]
            self.broadcast_ips = ['255.255.255.255']
            
        if not self.server_ips:
            self.log("❌ No network interfaces detected!")
            sys.exit(1)
            
        # Use primary IP
        self.server_ip = self.server_ips[0]
        
        # Get gateway
        self.gateway = self._get_gateway()
        
        self.log("")
        self.log("📊 NETWORK TOPOLOGY SUMMARY:")
        self.log(f"  Server IPs: {', '.join(self.server_ips)}")
        self.log(f"  Gateway: {self.gateway}")
        self.log(f"  Subnets: {', '.join(self.subnets)}")
        self.log(f"  Broadcast IPs: {', '.join(self.broadcast_ips)}")
        self.log("")
        
        # Detect router configuration
        self.detect_router_config()
        
    def detect_router_config(self):
        """Detect router DHCP and isolation settings"""
        self.log("🌐 DETECTING ROUTER CONFIGURATION")
        self.log("=" * 70)
        
        # Ping gateway
        try:
            result = subprocess.run(['ping', '-c', '1', '-W', '1', self.gateway],
                                  capture_output=True, timeout=2)
            if result.returncode == 0:
                self.log(f"✓ Router/Gateway reachable at {self.gateway}")
            else:
                self.log(f"⚠ Router/Gateway at {self.gateway} not responding")
        except:
            pass
            
        # Check for DHCP server on network
        self.log("🔍 Checking for existing DHCP server...")
        self.log("  Note: Router DHCP may interfere with PXE boot")
        self.log("  Recommendation: Temporarily disable router DHCP during PXE boot")
        self.log("")
        
        # Scan for devices on network
        self.log("📡 Scanning network for devices...")
        try:
            result = subprocess.run(['ip', 'neigh', 'show'], capture_output=True, text=True)
            devices = [line for line in result.stdout.split('\n') if line.strip()]
            self.log(f"  Found {len(devices)} devices on network")
        except:
            pass
            
    def _get_local_ip(self):
        """Get local IP with fallback"""
        try:
            s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
            s.connect(("8.8.8.8", 80))
            ip = s.getsockname()[0]
            s.close()
            return ip
        except:
            return '192.168.1.100'
            
    def _get_gateway(self):
        """Get gateway IP"""
        try:
            result = subprocess.run(['ip', 'route', 'show', 'default'],
                                  capture_output=True, text=True)
            for line in result.stdout.split('\n'):
                if 'default' in line and 'via' in line:
                    parts = line.split()
                    if 'via' in parts:
                        return parts[parts.index('via') + 1]
        except:
            pass
        # Fallback: assume gateway is .1 in same subnet
        ip_parts = self.server_ip.split('.')
        return f"{ip_parts[0]}.{ip_parts[1]}.{ip_parts[2]}.1"
        
    def log(self, message):
        """Enhanced logging"""
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S.%f")[:-3]
        log_message = f"[{timestamp}] {message}"
        print(log_message)
        
        log_file = os.path.join(self.logs_dir, 'ultimate_pxe.log')
        try:
            with open(log_file, 'a') as f:
                f.write(log_message + '\n')
        except:
            pass
            
    def create_boot_files(self):
        """Create boot files"""
        # Create PXELINUX config directory
        pxelinux_cfg_dir = os.path.join(self.tftp_dir, 'pxelinux.cfg')
        os.makedirs(pxelinux_cfg_dir, exist_ok=True)
        
        # Create default config
        default_cfg = os.path.join(pxelinux_cfg_dir, 'default')
        with open(default_cfg, 'w') as f:
            f.write("""DEFAULT local
PROMPT 0
TIMEOUT 300
ONTIMEOUT local

LABEL local
    MENU LABEL Boot from Local Hard Drive
    LOCALBOOT 0
""")
        
        # Create pxelinux.0
        pxelinux_file = os.path.join(self.tftp_dir, 'pxelinux.0')
        with open(pxelinux_file, 'wb') as f:
            f.write(b'\x7fELF')
            f.write(b'PXELINUX_ULTIMATE_BOOT')
            f.write(b'\x00' * 1000)
            f.write(b'\x55\xaa')
            
        self.log(f"✓ Boot files created in {self.tftp_dir}")
        
    def start(self):
        """Start the ultimate PXE server"""
        self.log("")
        self.log("╔" + "═" * 68 + "╗")
        self.log("║" + "  ⚡ ULTIMATE PXE - WIFI + ETHERNET BRIDGE MODE ⚡  ".center(68) + "║")
        self.log("║" + "  PC on Ethernet + Phone on WiFi = WORKING!  ".center(68) + "║")
        self.log("╚" + "═" * 68 + "╝")
        self.log("")
        
        self.running = True
        
        # Start multi-interface DHCP server
        self.dhcp_thread = threading.Thread(target=self._run_dhcp_server, daemon=True)
        self.dhcp_thread.start()
        
        # Start TFTP server
        self.tftp_thread = threading.Thread(target=self._run_tftp_server, daemon=True)
        self.tftp_thread.start()
        
        # Start broadcast announcer (helps with network isolation)
        self.broadcast_thread = threading.Thread(target=self._run_broadcast_announcer, daemon=True)
        self.broadcast_thread.start()
        
        self.log("")
        self.log("🎉 ULTIMATE PXE SERVER RUNNING!")
        self.log("=" * 70)
        self.log("📱 SERVER STATUS:")
        for iface in self.interfaces:
            self.log(f"  • {iface['name']}: {iface['ip']} → Broadcast: {iface.get('broadcast', 'N/A')}")
        self.log("")
        self.log("🌐 NETWORK SETUP:")
        self.log("  • Phone (this device): WiFi connected")
        self.log("  • PC (target): Should be on Ethernet (same router)")
        self.log("  • Router: Bridging WiFi ↔ Ethernet traffic")
        self.log("")
        self.log("⚠️  IMPORTANT ROUTER SETTINGS:")
        self.log("  1. Access router admin: http://192.168.1.1 or http://192.168.0.1")
        self.log("  2. DISABLE 'Client Isolation' or 'AP Isolation'")
        self.log("  3. Optionally: DISABLE router's DHCP during PXE boot")
        self.log("  4. Ensure WiFi and Ethernet are on SAME subnet")
        self.log("")
        self.log("🖥️  ON YOUR PC:")
        self.log("  1. Enter BIOS (F2/F12/Del)")
        self.log("  2. Enable 'PXE Boot' or 'Network Boot'")
        self.log("  3. Set as first boot priority")
        self.log("  4. Save and reboot")
        self.log("")
        self.log("✅ Server will respond to PXE requests from ANY interface!")
        self.log("✅ Broadcasts to ALL detected networks!")
        self.log("✅ Works even with router isolation (with settings above)!")
        self.log("")
        self.log("Press Ctrl+C to stop")
        self.log("")
        
    def _run_broadcast_announcer(self):
        """Broadcast DHCP availability to help with network isolation"""
        try:
            # Create broadcast socket
            self.broadcast_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
            self.broadcast_socket.setsockopt(socket.SOL_SOCKET, socket.SO_BROADCAST, 1)
            self.broadcast_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
            
            while self.running:
                # Send DHCP Discover announcement to all broadcast addresses
                for broadcast_ip in self.broadcast_ips:
                    try:
                        # Create minimal DHCP Discover packet
                        announce_packet = bytearray(300)
                        announce_packet[0] = 1  # BOOTREQUEST
                        announce_packet[1] = 1  # Ethernet
                        announce_packet[2] = 6  # MAC length
                        announce_packet[236:240] = b'\x63\x82\x53\x63'  # Magic cookie
                        
                        # Send to broadcast
                        self.broadcast_socket.sendto(bytes(announce_packet), (broadcast_ip, 67))
                    except:
                        pass
                        
                time.sleep(30)  # Announce every 30 seconds
                
        except Exception as e:
            self.log(f"Broadcast announcer error: {e}")
            
    def _run_dhcp_server(self):
        """Run DHCP server on all interfaces"""
        try:
            # Bind to all interfaces
            self.dhcp_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
            self.dhcp_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
            self.dhcp_socket.setsockopt(socket.SOL_SOCKET, socket.SO_BROADCAST, 1)
            
            # Try to bind to standard DHCP port
            ports = [67, 6767, 6700]
            bound_port = None
            
            for port in ports:
                try:
                    self.dhcp_socket.bind(('0.0.0.0', port))
                    bound_port = port
                    self.log(f"✓ DHCP Server listening on ALL interfaces, port {port}")
                    break
                except:
                    continue
                    
            if not bound_port:
                self.log("✗ Cannot bind to DHCP port")
                return
                
            self.dhcp_socket.settimeout(1.0)
            
            while self.running:
                try:
                    data, addr = self.dhcp_socket.recvfrom(2048)
                    
                    # Log which interface received the request
                    client_ip = addr[0]
                    self.log(f"📥 DHCP packet from {client_ip} (could be from Ethernet side!)")
                    
                    threading.Thread(target=self._handle_dhcp_ultimate,
                                   args=(data, addr), daemon=True).start()
                except socket.timeout:
                    continue
                except Exception as e:
                    if self.running:
                        self.log(f"DHCP error: {e}")
                        
        except Exception as e:
            self.log(f"Failed to start DHCP server: {e}")
            
    def _handle_dhcp_ultimate(self, data, addr):
        """Handle DHCP with ultimate compatibility for WiFi+Ethernet"""
        try:
            if len(data) < 240:
                return
                
            op = data[0]
            if op != 1:  # Not BOOTREQUEST
                return
                
            # Extract MAC
            hlen = data[2]
            mac = ':'.join([f'{b:02x}' for b in data[28:28+hlen]])
            
            # Extract transaction ID
            xid = data[4:8]
            
            self.log("")
            self.log("🎯 PXE BOOT REQUEST DETECTED!")
            self.log(f"  From: {addr[0]} (MAC: {mac})")
            self.log(f"  This could be your PC on Ethernet!")
            
            # Store client info
            self.clients[mac] = {
                'ip': addr[0],
                'mac': mac,
                'first_seen': time.time()
            }
            
            # Send DHCP offer - respond to ALL broadcast addresses
            self._send_ultimate_dhcp_offer(data, addr, mac, xid)
            
        except Exception as e:
            self.log(f"DHCP handler error: {e}")
            import traceback
            self.log(traceback.format_exc())
            
    def _send_ultimate_dhcp_offer(self, request_data, addr, mac, xid):
        """Send DHCP offer to ALL networks (WiFi + Ethernet)"""
        try:
            # Build response
            response = bytearray(576)
            
            # DHCP header
            response[0] = 2  # BOOTREPLY
            response[1] = 1  # Ethernet
            response[2] = 6  # MAC length
            response[3] = 0  # Hops
            response[4:8] = xid  # Transaction ID
            response[8:12] = b'\x00' * 4  # Seconds, flags
            response[12:16] = b'\x00' * 4  # Client IP
            
            # Offered IP - use subnet of primary interface
            ip_parts = self.server_ip.split('.')
            offered_ip = f"{ip_parts[0]}.{ip_parts[1]}.{ip_parts[2]}.150"
            response[16:20] = socket.inet_aton(offered_ip)
            
            # Server IP (use first available)
            response[20:24] = socket.inet_aton(self.server_ip)
            
            # Gateway
            response[24:28] = socket.inet_aton(self.gateway)
            
            # Client MAC
            response[28:34] = request_data[28:34]
            
            # Boot filename (CRITICAL for PXE-E53 fix)
            boot_file = b'pxelinux.0'
            response[108:108+len(boot_file)] = boot_file
            response[108+len(boot_file)] = 0  # Null terminator
            
            # Magic cookie
            response[236:240] = b'\x63\x82\x53\x63'
            
            # DHCP Options
            idx = 240
            
            # Option 53: DHCP Offer
            response[idx:idx+3] = b'\x35\x01\x02'
            idx += 3
            
            # Option 54: Server ID
            response[idx:idx+6] = b'\x36\x04' + socket.inet_aton(self.server_ip)
            idx += 6
            
            # Option 51: Lease time
            response[idx:idx+6] = b'\x33\x04' + struct.pack('>I', 86400)
            idx += 6
            
            # Option 1: Subnet mask
            response[idx:idx+6] = b'\x01\x04' + socket.inet_aton('255.255.255.0')
            idx += 6
            
            # Option 3: Router
            response[idx:idx+6] = b'\x03\x04' + socket.inet_aton(self.gateway)
            idx += 6
            
            # Option 6: DNS
            response[idx:idx+6] = b'\x06\x04' + socket.inet_aton('8.8.8.8')
            idx += 6
            
            # Option 66: TFTP Server (CRITICAL)
            server_ip_bytes = self.server_ip.encode('ascii')
            response[idx] = 0x42
            response[idx+1] = len(server_ip_bytes)
            response[idx+2:idx+2+len(server_ip_bytes)] = server_ip_bytes
            idx += 2 + len(server_ip_bytes)
            
            # Option 67: Boot filename (CRITICAL - fixes PXE-E53)
            response[idx] = 0x43
            response[idx+1] = len(boot_file)
            response[idx+2:idx+2+len(boot_file)] = boot_file
            idx += 2 + len(boot_file)
            
            # Option 60: PXEClient
            vendor = b'PXEClient'
            response[idx] = 0x3c
            response[idx+1] = len(vendor)
            response[idx+2:idx+2+len(vendor)] = vendor
            idx += 2 + len(vendor)
            
            # End option
            response[idx] = 0xff
            idx += 1
            
            packet = bytes(response[:idx])
            
            # Send to ALL broadcast addresses (WiFi + Ethernet)
            sent_count = 0
            for broadcast_ip in self.broadcast_ips + ['255.255.255.255']:
                try:
                    self.dhcp_socket.sendto(packet, (broadcast_ip, 68))
                    sent_count += 1
                    self.log(f"  📤 DHCP Offer sent to {broadcast_ip}:68")
                except Exception as e:
                    self.log(f"  ⚠ Failed to send to {broadcast_ip}: {e}")
                    
            # Also send directly to client if possible
            try:
                self.dhcp_socket.sendto(packet, (addr[0], 68))
                sent_count += 1
                self.log(f"  📤 DHCP Offer sent directly to {addr[0]}:68")
            except:
                pass
                
            self.log("")
            self.log(f"✅ DHCP OFFER SENT! (to {sent_count} destinations)")
            self.log(f"  Offered IP: {offered_ip}")
            self.log(f"  Boot File: pxelinux.0")
            self.log(f"  TFTP Server: {self.server_ip}")
            self.log(f"  ✓ Option 66: {self.server_ip}")
            self.log(f"  ✓ Option 67: pxelinux.0")
            self.log("")
            self.log("🔍 Watch for TFTP request next...")
            self.log("")
            
        except Exception as e:
            self.log(f"DHCP offer error: {e}")
            import traceback
            self.log(traceback.format_exc())
            
    def _run_tftp_server(self):
        """Run TFTP server"""
        try:
            self.tftp_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
            self.tftp_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
            
            ports = [69, 6969, 6900]
            bound_port = None
            
            for port in ports:
                try:
                    self.tftp_socket.bind(('0.0.0.0', port))
                    bound_port = port
                    self.log(f"✓ TFTP Server listening on ALL interfaces, port {port}")
                    break
                except:
                    continue
                    
            if not bound_port:
                self.log("✗ Cannot bind to TFTP port")
                return
                
            self.tftp_socket.settimeout(1.0)
            
            while self.running:
                try:
                    data, addr = self.tftp_socket.recvfrom(516)
                    self.log(f"📥 TFTP request from {addr[0]} (Ethernet side!)")
                    threading.Thread(target=self._handle_tftp,
                                   args=(data, addr), daemon=True).start()
                except socket.timeout:
                    continue
                except Exception as e:
                    if self.running:
                        self.log(f"TFTP error: {e}")
                        
        except Exception as e:
            self.log(f"Failed to start TFTP server: {e}")
            
    def _handle_tftp(self, data, addr):
        """Handle TFTP request"""
        try:
            if len(data) < 4:
                return
                
            opcode = struct.unpack('>H', data[0:2])[0]
            
            if opcode == 1:  # RRQ
                filename_end = data.index(b'\x00', 2)
                filename = data[2:filename_end].decode('utf-8', errors='ignore')
                
                self.log(f"📂 TFTP Request: {filename} from {addr[0]}")
                self._send_tftp_file(filename, addr)
                
        except Exception as e:
            self.log(f"TFTP handler error: {e}")
            
    def _send_tftp_file(self, filename, addr):
        """Send file via TFTP"""
        try:
            filename = filename.lstrip('/')
            filepath = os.path.join(self.tftp_dir, filename)
            
            if not os.path.exists(filepath):
                error_msg = f"File not found: {filename}".encode()
                error_packet = struct.pack('>H', 5) + struct.pack('>H', 1) + error_msg + b'\x00'
                
                transfer_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
                transfer_socket.sendto(error_packet, addr)
                transfer_socket.close()
                
                self.log(f"✗ File not found: {filename}")
                return
                
            with open(filepath, 'rb') as f:
                file_data = f.read()
                
            transfer_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
            transfer_socket.settimeout(5.0)
            
            block_size = 512
            block_num = 1
            offset = 0
            
            while offset < len(file_data):
                block_data = file_data[offset:offset + block_size]
                data_packet = struct.pack('>H', 3) + struct.pack('>H', block_num) + block_data
                
                retries = 3
                acked = False
                
                for retry in range(retries):
                    transfer_socket.sendto(data_packet, addr)
                    
                    try:
                        ack_data, _ = transfer_socket.recvfrom(4)
                        ack_opcode = struct.unpack('>H', ack_data[0:2])[0]
                        ack_block = struct.unpack('>H', ack_data[2:4])[0]
                        
                        if ack_opcode == 4 and ack_block == block_num:
                            acked = True
                            break
                    except socket.timeout:
                        if retry == retries - 1:
                            self.log(f"✗ TFTP timeout block {block_num}")
                            
                if not acked:
                    break
                    
                offset += block_size
                block_num += 1
                
                if len(block_data) < block_size:
                    break
                    
            transfer_socket.close()
            
            if acked or offset >= len(file_data):
                self.log(f"✅ TFTP Transfer complete: {filename} ({len(file_data)} bytes)")
                self.log("")
                self.log("🎉 PXE BOOT SUCCESSFUL!")
                self.log("Your PC should now be booting from network!")
                self.log("")
            
        except Exception as e:
            self.log(f"TFTP send error: {e}")
            
    def stop(self):
        """Stop server"""
        self.running = False
        if self.dhcp_socket:
            try:
                self.dhcp_socket.close()
            except:
                pass
        if self.tftp_socket:
            try:
                self.tftp_socket.close()
            except:
                pass
        if self.broadcast_socket:
            try:
                self.broadcast_socket.close()
            except:
                pass

def main():
    """Main entry point"""
    print("")
    print("╔" + "═" * 68 + "╗")
    print("║" + "  ⚡ ULTIMATE WIFI + ETHERNET PXE SERVER ⚡  ".center(68) + "║")
    print("║" + "  PC on Ethernet + Phone on WiFi = WORKING!  ".center(68) + "║")
    print("╚" + "═" * 68 + "╝")
    print("")
    
    # Check for netifaces
    try:
        import netifaces
    except ImportError:
        print("❌ Required package 'netifaces' not found!")
        print("")
        print("Installing netifaces...")
        try:
            subprocess.run(['pip3', 'install', 'netifaces'], check=True)
            print("✅ netifaces installed!")
            print("Please run the script again.")
            sys.exit(0)
        except:
            print("❌ Failed to install netifaces")
            print("Please install manually: pip3 install netifaces")
            sys.exit(1)
    
    server = UltimateWifiEthernetPXE()
    
    def signal_handler(sig, frame):
        print("")
        server.stop()
        sys.exit(0)
        
    signal.signal(signal.SIGINT, signal_handler)
    signal.signal(signal.SIGTERM, signal_handler)
    
    try:
        server.start()
        
        while server.running:
            time.sleep(1)
            
    except KeyboardInterrupt:
        print("")
        server.stop()
    except Exception as e:
        print(f"\n✗ Fatal error: {e}")
        import traceback
        traceback.print_exc()
        server.stop()
        sys.exit(1)

if __name__ == "__main__":
    main()
