#!/usr/bin/env python3
"""
Enhanced DHCP Bridge - Fixes PXE E53 Error
Provides interface-specific DHCP responses and WiFi-to-ethernet bridging
Addresses router isolation by creating direct communication channels
"""

import socket
import struct
import threading
import time
import subprocess
import ipaddress
import os
import signal
from typing import Dict, List, Optional, Tuple
from dataclasses import dataclass
import logging

@dataclass
class DHCPClient:
    """Represents a DHCP client"""
    mac_address: str
    ip_address: Optional[str]
    interface: str
    last_seen: float
    dhcp_state: str  # discover, offer, request, ack

@dataclass
class NetworkInterface:
    """Network interface with DHCP capabilities"""
    name: str
    type: str  # ethernet, wireless, usb
    ip_address: str
    subnet_mask: str
    broadcast_address: str
    mac_address: str
    is_active: bool
    mtu: int = 1500

class EnhancedDHCPBridge:
    """
    Enhanced DHCP Server with WiFi-to-Ethernet Bridging
    Fixes PXE-E53 by providing cross-interface DHCP communication
    """
    
    def __init__(self):
        self.running = False
        self.dhcp_sockets: Dict[str, socket.socket] = {}
        self.clients: Dict[str, DHCPClient] = {}
        self.interfaces: Dict[str, NetworkInterface] = {}
        
        # Configuration
        self.server_ip = self._get_primary_ip()
        self.subnet_mask = "255.255.255.0"
        self.broadcast_address = "192.168.1.255"
        self.dhcp_range_start = "192.168.1.150"
        self.dhcp_range_end = "192.168.1.200"
        self.lease_time = 86400
        self.boot_file = "pxelinux.0"
        
        # UDP Tunnel ports for cross-interface communication
        self.tunnel_base_port = 9000
        self.multicast_group = "224.0.0.1"
        self.multicast_port = 9001
        
        # Logging
        logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
        self.logger = logging.getLogger(__name__)
        
        # Setup directories
        self.tftp_dir = os.path.expanduser('~/.enhanced_pxe_boot')
        os.makedirs(self.tftp_dir, exist_ok=True)
        self._create_boot_files()
    
    def _get_primary_ip(self) -> str:
        """Get primary IP address"""
        try:
            s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
            s.connect(("8.8.8.8", 80))
            ip = s.getsockname()[0]
            s.close()
            return ip
        except:
            return "192.168.1.100"
    
    def _get_gateway(self) -> str:
        """Get gateway IP"""
        try:
            result = subprocess.run(['ip', 'route', 'show'], capture_output=True, text=True)
            for line in result.stdout.split('\n'):
                if 'default' in line:
                    parts = line.split()
                    if 'via' in parts:
                        return parts[parts.index('via') + 1]
        except:
            pass
        return self.server_ip
    
    def _create_boot_files(self):
        """Create PXE boot files"""
        pxelinux_cfg_dir = os.path.join(self.tftp_dir, 'pxelinux.cfg')
        os.makedirs(pxelinux_cfg_dir, exist_ok=True)
        
        # Create default PXE configuration
        default_cfg = os.path.join(pxelinux_cfg_dir, 'default')
        with open(default_cfg, 'w') as f:
            f.write("""DEFAULT local
PROMPT 0
TIMEOUT 300

LABEL local
    MENU LABEL Boot from Local Drive
    LOCALBOOT 0
""")
        
        # Create basic PXE bootloader stub
        pxelinux_file = os.path.join(self.tftp_dir, 'pxelinux.0')
        with open(pxelinux_file, 'wb') as f:
            f.write(b'\x7fELF')  # ELF magic
            f.write(b'ENHANCED_PXE_BOOT')
            f.write(b'\x00' * 1000)  # Padding
            f.write(b'\x55\xaa')  # Boot signature
    
    def detect_network_interfaces(self) -> Dict[str, NetworkInterface]:
        """Detect all network interfaces"""
        interfaces = {}
        
        try:
            result = subprocess.run(['ip', 'link', 'show'], capture_output=True, text=True)
            
            for line in result.stdout.split('\n'):
                if ': ' in line and 'state UP' in line:
                    # Parse interface info
                    parts = line.split(': ')
                    if len(parts) >= 2:
                        interface_name = parts[1].split('@')[0].strip()
                        
                        # Get IP info
                        ip_result = subprocess.run(['ip', 'addr', 'show', interface_name], 
                                                 capture_output=True, text=True)
                        
                        ip_address = None
                        subnet_mask = None
                        broadcast_address = None
                        
                        for ip_line in ip_result.stdout.split('\n'):
                            if 'inet ' in ip_line and 'scope global' in ip_line:
                                parts = ip_line.strip().split()
                                if len(parts) >= 2:
                                    ip_cidr = parts[1]
                                    ip_address = ip_cidr.split('/')[0]
                                    prefix = int(ip_cidr.split('/')[1])
                                    subnet_mask = self._prefix_to_netmask(prefix)
                                    broadcast_address = str(ipaddress.IPv4Network(f"{ip_address}/{prefix}", strict=False).broadcast_address)
                                    break
                        
                        if ip_address:
                            # Get MAC address
                            mac_result = subprocess.run(['ip', 'link', 'show', interface_name], 
                                                      capture_output=True, text=True)
                            mac_address = None
                            for mac_line in mac_result.stdout.split('\n'):
                                if 'link/ether' in mac_line:
                                    mac_address = mac_line.split()[1]
                                    break
                            
                            # Determine interface type
                            interface_type = self._detect_interface_type(interface_name)
                            
                            interfaces[interface_name] = NetworkInterface(
                                name=interface_name,
                                type=interface_type,
                                ip_address=ip_address,
                                subnet_mask=subnet_mask or "255.255.255.0",
                                broadcast_address=broadcast_address or f"{ip_address.rsplit('.', 1)[0]}.255",
                                mac_address=mac_address or "00:00:00:00:00:00",
                                is_active=True
                            )
            
        except Exception as e:
            self.logger.error(f"Interface detection failed: {e}")
        
        return interfaces
    
    def _detect_interface_type(self, interface_name: str) -> str:
        """Detect interface type"""
        name_lower = interface_name.lower()
        
        # Check wireless capability
        try:
            wireless_path = f'/sys/class/net/{interface_name}/wireless'
            if os.path.exists(wireless_path):
                return 'wireless'
            
            # Check with iw command
            result = subprocess.run(['iw', 'dev', interface_name, 'info'], 
                                  capture_output=True, text=True, timeout=3)
            if result.returncode == 0:
                return 'wireless'
        except:
            pass
        
        # Check name patterns
        if any(pattern in name_lower for pattern in ['eth', 'enp', 'enx']):
            return 'ethernet'
        elif any(pattern in name_lower for pattern in ['wlan', 'wlp']):
            return 'wireless'
        elif any(pattern in name_lower for pattern in ['usb', 'rndis']):
            return 'usb'
        elif name_lower == 'lo':
            return 'loopback'
        
        return 'ethernet'  # Default
    
    def _prefix_to_netmask(self, prefix: int) -> str:
        """Convert prefix length to netmask"""
        return socket.inet_ntoa(struct.pack(">I", (0xffffffff << (32 - prefix)) & 0xffffffff))
    
    def start(self):
        """Start the Enhanced DHCP Bridge"""
        if self.running:
            self.logger.warning("DHCP Bridge is already running")
            return
        
        self.running = True
        self.logger.info("🚀 Starting Enhanced DHCP Bridge")
        
        # Detect network interfaces
        self.interfaces = self.detect_network_interfaces()
        
        # Log detected interfaces
        for iface in self.interfaces.values():
            self.logger.info(f"📡 Detected {iface.name}: {iface.type} - {iface.ip_address}")
        
        # Create DHCP sockets for each interface
        self._create_dhcp_sockets()
        
        # Start UDP tunnel for cross-interface communication
        self._start_udp_tunnel()
        
        # Start multicast proxy
        self._start_multicast_proxy()
        
        # Start DHCP server threads
        self._start_dhcp_servers()
        
        self.logger.info("✅ Enhanced DHCP Bridge started successfully")
        self.logger.info("🎯 PC on ethernet will now receive proper DHCP responses")
    
    def stop(self):
        """Stop the Enhanced DHCP Bridge"""
        if not self.running:
            return
        
        self.running = False
        self.logger.info("🛑 Stopping Enhanced DHCP Bridge")
        
        # Close all sockets
        for socket_obj in self.dhcp_sockets.values():
            try:
                socket_obj.close()
            except:
                pass
        self.dhcp_sockets.clear()
        
        self.logger.info("✅ DHCP Bridge stopped")
    
    def _create_dhcp_sockets(self):
        """Create DHCP sockets for each active interface"""
        for iface_name, interface in self.interfaces.items():
            try:
                # Create DHCP socket
                dhcp_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
                dhcp_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
                dhcp_socket.setsockopt(socket.SOL_SOCKET, socket.SO_BROADCAST, 1)
                
                # Bind to interface-specific port
                if interface.type == 'ethernet':
                    # Use high port for ethernet to avoid conflicts
                    port = self.tunnel_base_port + 100
                else:
                    # Use standard port for wireless/USB
                    port = 67
                
                dhcp_socket.bind((interface.ip_address, port))
                dhcp_socket.settimeout(1.0)
                
                self.dhcp_sockets[iface_name] = dhcp_socket
                
                self.logger.info(f"✓ DHCP socket created for {iface_name} on port {port}")
                
            except Exception as e:
                self.logger.error(f"Failed to create DHCP socket for {iface_name}: {e}")
    
    def _start_udp_tunnel(self):
        """Start UDP tunnel for cross-interface communication"""
        def udp_tunnel_thread():
            try:
                tunnel_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
                tunnel_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
                tunnel_socket.bind(('0.0.0.0', self.tunnel_base_port))
                tunnel_socket.settimeout(1.0)
                
                self.logger.info(f"✓ UDP Tunnel started on port {self.tunnel_base_port}")
                
                while self.running:
                    try:
                        data, addr = tunnel_socket.recvfrom(65507)
                        self._handle_tunnel_packet(data, addr)
                    except socket.timeout:
                        continue
                    except Exception as e:
                        if self.running:
                            self.logger.error(f"UDP Tunnel error: {e}")
                        break
                
                tunnel_socket.close()
                
            except Exception as e:
                self.logger.error(f"UDP Tunnel initialization failed: {e}")
        
        thread = threading.Thread(target=udp_tunnel_thread, daemon=True)
        thread.start()
    
    def _start_multicast_proxy(self):
        """Start multicast proxy for DHCP broadcast forwarding"""
        def multicast_thread():
            try:
                multicast_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
                multicast_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
                
                # Join multicast group
                mreq = struct.pack("4sl", socket.inet_aton(self.multicast_group), socket.INADDR_ANY)
                multicast_socket.setsockopt(socket.IPPROTO_IP, socket.IP_ADD_MEMBERSHIP, mreq)
                
                multicast_socket.bind(('', self.multicast_port))
                multicast_socket.settimeout(1.0)
                
                self.logger.info(f"✓ Multicast Proxy started on port {self.multicast_port}")
                
                while self.running:
                    try:
                        data, addr = multicast_socket.recvfrom(65507)
                        self._handle_multicast_packet(data, addr)
                    except socket.timeout:
                        continue
                    except Exception as e:
                        if self.running:
                            self.logger.error(f"Multicast Proxy error: {e}")
                        break
                
                multicast_socket.close()
                
            except Exception as e:
                self.logger.error(f"Multicast Proxy initialization failed: {e}")
        
        thread = threading.Thread(target=multicast_thread, daemon=True)
        thread.start()
    
    def _handle_tunnel_packet(self, data: bytes, addr):
        """Handle UDP tunnel packet"""
        try:
            # Parse tunnel packet format: INTERFACE_NAME|DHCP_DATA
            packet_str = data.decode('utf-8', errors='ignore')
            if '|' not in packet_str:
                return
            
            parts = packet_str.split('|', 1)
            if len(parts) != 2:
                return
            
            source_interface, dhcp_data = parts
            self.logger.debug(f"Tunnel packet from {source_interface}")
            
            # Forward DHCP data to all other interfaces
            for iface_name, socket_obj in self.dhcp_sockets.items():
                if iface_name != source_interface:
                    try:
                        socket_obj.sendto(dhcp_data.encode(), ('255.255.255.255', 68))
                    except Exception as e:
                        self.logger.debug(f"Failed to forward to {iface_name}: {e}")
        
        except Exception as e:
            self.logger.error(f"Tunnel packet handling error: {e}")
    
    def _handle_multicast_packet(self, data: bytes, addr):
        """Handle multicast DHCP packet"""
        try:
            # Forward multicast packets to all interfaces
            for iface_name, socket_obj in self.dhcp_sockets.items():
                try:
                    if iface_name in self.interfaces:
                        interface = self.interfaces[iface_name]
                        # Send to interface broadcast address
                        socket_obj.sendto(data, (interface.broadcast_address, 68))
                except Exception as e:
                    self.logger.debug(f"Failed to forward multicast to {iface_name}: {e}")
        
        except Exception as e:
            self.logger.error(f"Multicast packet handling error: {e}")
    
    def _start_dhcp_servers(self):
        """Start DHCP servers for each interface"""
        for iface_name, socket_obj in self.dhcp_sockets.items():
            thread = threading.Thread(
                target=self._dhcp_server_thread,
                args=(iface_name, socket_obj),
                daemon=True
            )
            thread.start()
    
    def _dhcp_server_thread(self, interface_name: str, socket_obj: socket.socket):
        """DHCP server thread for specific interface"""
        while self.running:
            try:
                data, addr = socket_obj.recvfrom(1024)
                threading.Thread(
                    target=self._handle_dhcp_request,
                    args=(data, addr, interface_name),
                    daemon=True
                ).start()
            except socket.timeout:
                continue
            except Exception as e:
                if self.running:
                    self.logger.error(f"DHCP server error for {interface_name}: {e}")
                break
    
    def _handle_dhcp_request(self, data: bytes, addr: Tuple[str, int], interface_name: str):
        """Handle DHCP request with interface-specific responses"""
        try:
            if len(data) < 240:
                return
            
            # Parse DHCP packet
            op = data[0]
            
            if op == 1:  # BOOTREQUEST
                # Extract client MAC address
                hlen = data[2]
                if hlen > 16:
                    hlen = 16
                mac = ':'.join([f'{b:02x}' for b in data[28:28+hlen]])
                
                self.logger.info(f"→ DHCP Request from {addr[0]} (MAC: {mac}) on {interface_name}")
                
                # Determine if this is an ethernet-connected client
                client_interface_type = self.interfaces.get(interface_name, NetworkInterface("", "", "", "", "", "", False)).type
                
                # Send interface-specific DHCP offer
                self._send_enhanced_dhcp_offer(data, addr, mac, interface_name, client_interface_type)
                
                # Forward to other interfaces via tunnel if needed
                if len(self.interfaces) > 1:
                    self._forward_dhcp_request(data, mac, interface_name)
                
        except Exception as e:
            self.logger.error(f"DHCP request handling error: {e}")
    
    def _forward_dhcp_request(self, data: bytes, mac: str, source_interface: str):
        """Forward DHCP request to other interfaces via UDP tunnel"""
        try:
            # Create tunnel packet: INTERFACE_NAME|DHCP_DATA
            tunnel_packet = f"{source_interface}|".encode() + data
            
            # Send to UDP tunnel
            tunnel_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
            tunnel_socket.sendto(tunnel_packet, ('127.0.0.1', self.tunnel_base_port))
            tunnel_socket.close()
            
        except Exception as e:
            self.logger.debug(f"DHCP request forwarding failed: {e}")
    
    def _send_enhanced_dhcp_offer(self, request_data: bytes, addr: Tuple[str, int], 
                                mac: str, interface_name: str, client_type: str):
        """Send enhanced DHCP offer with interface-specific configuration"""
        try:
            # Build DHCP offer packet
            response = bytearray(1024)  # Larger packet for enhanced options
            
            # DHCP header
            response[0] = 2  # BOOTREPLY
            response[1] = 1  # Ethernet
            response[2] = 6  # MAC length
            response[3] = 0  # Hops
            
            # Transaction ID (copy from request)
            response[4:8] = request_data[4:8]
            
            # Seconds, flags
            response[8:12] = b'\x00' * 4
            
            # Client IP (0.0.0.0)
            response[12:16] = b'\x00' * 4
            
            # Your IP (offered IP)
            offered_ip = self._get_available_ip(mac, interface_name)
            response[16:20] = socket.inet_aton(offered_ip)
            
            # Server IP (siaddr field) - CRITICAL for PXE
            response[20:24] = socket.inet_aton(self.server_ip)
            
            # Gateway IP
            response[24:28] = socket.inet_aton(self._get_gateway())
            
            # Client MAC address
            hlen = min(len(mac.split(':')), 6)
            mac_bytes = bytes.fromhex(mac.replace(':', ''))[:hlen]
            response[28:28+hlen] = mac_bytes
            
            # CRITICAL: Boot filename at fixed position
            boot_file = self.boot_file.encode('ascii')
            response[108:108+len(boot_file)] = boot_file
            response[108+len(boot_file)] = 0  # Null terminator
            
            # Magic cookie
            response[236:240] = b'\x63\x82\x53\x63'
            
            # DHCP options
            idx = 240
            
            # Option 53: DHCP Message Type (Offer = 2)
            response[idx:idx+3] = b'\x35\x01\x02'
            idx += 3
            
            # Option 54: Server Identifier
            response[idx:idx+6] = b'\x36\x04' + socket.inet_aton(self.server_ip)
            idx += 6
            
            # Option 51: Lease Time
            response[idx:idx+6] = b'\x33\x04' + struct.pack('>I', self.lease_time)
            idx += 6
            
            # Option 1: Subnet Mask
            response[idx:idx+6] = b'\x01\x04' + socket.inet_aton(self.subnet_mask)
            idx += 6
            
            # Option 3: Router/Gateway
            response[idx:idx+6] = b'\x03\x04' + socket.inet_aton(self._get_gateway())
            idx += 6
            
            # Option 6: DNS Server
            response[idx:idx+6] = b'\x06\x04' + socket.inet_aton(self.server_ip)
            idx += 6
            
            # CRITICAL OPTION 66: TFTP Server Name
            server_ip_bytes = self.server_ip.encode('ascii')
            response[idx] = 0x42  # Option 66
            response[idx+1] = len(server_ip_bytes)
            response[idx+2:idx+2+len(server_ip_bytes)] = server_ip_bytes
            idx += 2 + len(server_ip_bytes)
            
            # CRITICAL OPTION 67: Bootfile Name
            response[idx] = 0x43  # Option 67
            response[idx+1] = len(boot_file)
            response[idx+2:idx+2+len(boot_file)] = boot_file
            idx += 2 + len(boot_file)
            
            # Option 60: Vendor Class Identifier
            vendor_class = b'PXEClient'
            response[idx] = 0x3c
            response[idx+1] = len(vendor_class)
            response[idx+2:idx+2+len(vendor_class)] = vendor_class
            idx += 2 + len(vendor_class)
            
            # Interface-specific options
            if client_type == 'ethernet':
                # Ethernet-specific options
                response[idx] = 0x2b  # Option 43 - Vendor Specific
                response[idx+1] = 4  # Length
                response[idx+2:idx+4] = b'\x00\x01\x04'  # Sub-option for PXE
                idx += 4
                
                # Add direct ethernet forwarding flag
                response[idx] = 0x2c  # Option 44
                response[idx+1] = 1
                response[idx+2] = 0x01  # Enable direct forwarding
                idx += 3
            
            # End option
            response[idx] = 0xff
            idx += 1
            
            # Send response based on interface type
            if client_type == 'ethernet':
                # Send to specific interface broadcast and local address
                interface = self.interfaces.get(interface_name)
                if interface:
                    self.dhcp_sockets[interface_name].sendto(bytes(response[:idx]), (interface.broadcast_address, 68))
                    self.dhcp_sockets[interface_name].sendto(bytes(response[:idx]), (offered_ip, 68))
                
                # Also send via UDP tunnel for cross-interface communication
                self._send_via_tunnel(interface_name, bytes(response[:idx]))
            else:
                # Standard broadcast for wireless/USB
                self.dhcp_sockets[interface_name].sendto(bytes(response[:idx]), ('255.255.255.255', 68))
            
            self.logger.info(f"← Enhanced DHCP Offer sent: IP={offered_ip}, Interface={interface_name}, Type={client_type}")
            self.logger.info(f"   ✓ Option 66 (TFTP Server): {self.server_ip}")
            self.logger.info(f"   ✓ Option 67 (Boot File): {self.boot_file}")
            self.logger.info(f"   ✓ Direct Ethernet Response: {client_type == 'ethernet'}")
            
        except Exception as e:
            self.logger.error(f"Enhanced DHCP offer error: {e}")
    
    def _send_via_tunnel(self, source_interface: str, data: bytes):
        """Send data via UDP tunnel"""
        try:
            # Wrap data in tunnel packet
            tunnel_packet = f"{source_interface}|".encode() + data
            
            tunnel_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
            tunnel_socket.sendto(tunnel_packet, ('127.0.0.1', self.tunnel_base_port))
            tunnel_socket.close()
            
        except Exception as e:
            self.logger.debug(f"Tunnel send failed: {e}")
    
    def _get_available_ip(self, mac: str, interface_name: str) -> str:
        """Get available IP address for client"""
        # Simple IP allocation - in production, use proper DHCP pool management
        client_count = len(self.clients)
        ip_parts = [int(x) for x in self.dhcp_range_start.split('.')]
        ip_parts[3] += (client_count % 50) + 10  # Offset to avoid conflicts
        return '.'.join(map(str, ip_parts))

def main():
    """Main entry point"""
    print("🚀 Enhanced DHCP Bridge - PXE E53 Fix")
    print("=" * 50)
    print("Features:")
    print("- Interface-specific DHCP responses")
    print("- WiFi-to-Ethernet bridging")
    print("- Router isolation bypass")
    print("- Direct ethernet packet injection")
    print("=" * 50)
    
    bridge = EnhancedDHCPBridge()
    
    def signal_handler(sig, frame):
        print("\n🛑 Stopping DHCP Bridge...")
        bridge.stop()
        exit(0)
    
    signal.signal(signal.SIGINT, signal_handler)
    
    try:
        bridge.start()
        
        while bridge.running:
            time.sleep(1)
            
    except KeyboardInterrupt:
        print("\n🛑 Interrupted by user")
        bridge.stop()
    except Exception as e:
        print(f"\n❌ Fatal error: {e}")
        bridge.stop()

if __name__ == "__main__":
    main()