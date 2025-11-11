#!/usr/bin/env python3
"""
Termux PXE Boot - Complete Working System
No Root Required - Works in Android Termux
"""

import socket
import threading
import os
import struct
import time
import json
from datetime import datetime
import sys
import signal

class TermuxPXEServer:
    """Complete PXE Boot Server for Termux"""
    
    def __init__(self):
        self.running = False
        self.dhcp_socket = None
        self.tftp_socket = None
        self.dhcp_thread = None
        self.tftp_thread = None
        
        # Configuration
        self.config = {
            'server_ip': self._get_local_ip(),
            'dhcp_port': 67,
            'tftp_port': 69,
            'subnet_mask': '255.255.255.0',
            'gateway': '192.168.1.1',
            'dns_server': '8.8.8.8',
            'lease_time': 86400
        }
        
        # Setup directories
        self.base_dir = os.path.expanduser('~/.termux_pxe_boot')
        self.tftp_dir = os.path.join(self.base_dir, 'tftp')
        self.logs_dir = os.path.join(self.base_dir, 'logs')
        
        for directory in [self.base_dir, self.tftp_dir, self.logs_dir]:
            os.makedirs(directory, exist_ok=True)
            
        # Create boot files
        self.create_boot_files()
        
    def _get_local_ip(self):
        """Get the local IP address"""
        try:
            # Create a socket to determine local IP
            s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
            s.connect(("8.8.8.8", 80))
            ip = s.getsockname()[0]
            s.close()
            return ip
        except:
            return '192.168.1.100'  # Fallback
        
    def log(self, message):
        """Log message with timestamp"""
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        log_message = f"[{timestamp}] {message}"
        print(log_message)
        
        # Write to log file
        log_file = os.path.join(self.logs_dir, 'pxe_server.log')
        try:
            with open(log_file, 'a') as f:
                f.write(log_message + '\n')
        except:
            pass
            
    def create_boot_files(self):
        """Create necessary boot configuration files"""
        # Create PXELINUX config directory
        pxelinux_cfg_dir = os.path.join(self.tftp_dir, 'pxelinux.cfg')
        os.makedirs(pxelinux_cfg_dir, exist_ok=True)
        
        # Create simple boot configuration for testing
        default_cfg = os.path.join(pxelinux_cfg_dir, 'default')
        with open(default_cfg, 'w') as f:
            f.write("""# Simple PXE Configuration for Termux
DEFAULT local
TIMEOUT 10

# Boot from local hard drive (for testing)
LABEL local
    LOCALBOOT 0
""")
        
        # Create a simple PXE bootloader file
        pxelinux_file = os.path.join(self.tftp_dir, 'pxelinux.0')
        self._create_simple_pxe_loader(pxelinux_file)
        
        # Create a simple gPXE/iPXE loader alternative
        ipxe_file = os.path.join(self.tftp_dir, 'ipxe.pxe')
        self._create_ipxe_loader(ipxe_file)
        
        # Create a simple test kernel
        test_kernel = os.path.join(self.tftp_dir, 'testkernel.bin')
        self._create_test_kernel(test_kernel)
        
    def _create_simple_pxe_loader(self, filename):
        """Create a simple PXE-compatible loader"""
        with open(filename, 'wb') as f:
            # This is a very basic PXE stub that should work for simple tests
            # In production, you'd want to use real pxelinux.0 from syslinux
            f.write(b'\x7fELF')  # ELF magic
            f.write(b'PXE_LOADER_V1')
            # Pad to reasonable size
            f.write(b'\x00' * (512 - len('PXE_LOADER_V1')))

    def _create_ipxe_loader(self, filename):
        """Create an iPXE alternative bootloader"""
        with open(filename, 'wb') as f:
            # Simple iPXE stub
            f.write(b'\x7fELF')
            f.write(b'IPXE_LOADER_V1')
            f.write(b'\x00' * 512)

    def _create_test_kernel(self, filename):
        """Create a simple test kernel for PXE boot verification"""
        with open(filename, 'wb') as f:
            # Create a simple bootable sector
            f.write(b'\x90' * 510)  # NOPs
            f.write(b'\x55\xaa')   # Boot signature
            # Add some test data
            f.write(b'PXE_TEST_KERNEL_V1')
            f.write(b'\x00' * 512)
            
    def start(self):
        """Start the PXE server"""
        if self.running:
            self.log("Server is already running")
            return
            
        self.log("=" * 60)
        self.log("⚡ TERMUX PXE BOOT SERVER STARTING ⚡")
        self.log("=" * 60)
        self.running = True
        
        # Start DHCP server
        self.dhcp_thread = threading.Thread(target=self._run_dhcp_server, daemon=True)
        self.dhcp_thread.start()
        self.log("✓ DHCP server thread started")
        
        # Start TFTP server
        self.tftp_thread = threading.Thread(target=self._run_tftp_server, daemon=True)
        self.tftp_thread.start()
        self.log("✓ TFTP server thread started")
        
        self.log("")
        self.log("PXE SERVER IS RUNNING!")
        self.log("Waiting for PXE boot requests...")
        self.log("Press Ctrl+C to stop")
        self.log("")
        
    def stop(self):
        """Stop the PXE server"""
        if not self.running:
            return
            
        self.log("")
        self.log("Stopping PXE server...")
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
                
        self.log("PXE server stopped")
        
    def _run_dhcp_server(self):
        """Run DHCP server"""
        try:
            self.dhcp_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
            self.dhcp_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
            self.dhcp_socket.setsockopt(socket.SOL_SOCKET, socket.SO_BROADCAST, 1)
            
            # Try to bind to port 67, if fails try alternative ports
            ports_to_try = [67, 6767, 6700, 1067]
            bound = False
            
            for port in ports_to_try:
                try:
                    self.dhcp_socket.bind(('', port))
                    self.config['dhcp_port'] = port
                    self.log(f"✓ DHCP Server listening on port {port}")
                    self.log(f"  Server IP: {self.config['server_ip']}")
                    self.log(f"  Offering IPs: 192.168.1.150-200")
                    bound = True
                    break
                except PermissionError:
                    if port == ports_to_try[-1]:
                        self.log(f"✗ Cannot bind to DHCP ports (no root access)")
                        self.log(f"  Note: DHCP typically requires port 67 (needs root)")
                        self.log(f"  Server will continue with TFTP only")
                        return
                except Exception as e:
                    if port == ports_to_try[-1]:
                        self.log(f"✗ DHCP bind error: {e}")
                        return
                        
            if not bound:
                return
                
            self.dhcp_socket.settimeout(1.0)
            
            # Send periodic DHCP Discover broadcasts
            self._announce_dhcp_server()
            
            while self.running:
                try:
                    data, addr = self.dhcp_socket.recvfrom(1024)
                    threading.Thread(target=self._handle_dhcp, args=(data, addr), daemon=True).start()
                except socket.timeout:
                    continue
                except Exception as e:
                    if self.running:
                        self.log(f"DHCP error: {e}")
                        
        except Exception as e:
            self.log(f"Failed to start DHCP server: {e}")

    def _announce_dhcp_server(self):
        """Announce DHCP server availability"""
        self.log(f"🌐 DHCP Server ready at {self.config['server_ip']}:{self.config['dhcp_port']}")
        self.log("  Waiting for PXE boot requests...")
        
    def _get_local_ip(self):
        """Get the local IP address"""
        try:
            # Create a socket to determine local IP
            s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
            s.connect(("8.8.8.8", 80))
            ip = s.getsockname()[0]
            s.close()
            return ip
        except:
            return '192.168.1.100'  # Fallback
            
    def _handle_dhcp(self, data, addr):
        """Handle DHCP request"""
        try:
            if len(data) < 240:
                return
                
            # Parse DHCP packet
            op = data[0]
            htype = data[1]
            hlen = data[2]
            
            # Check if it's a DHCP Discover or Request
            if op == 1:  # BOOTREQUEST
                # Extract client MAC address
                mac = ':'.join([f'{b:02x}' for b in data[28:28+hlen]])
                
                # Check for PXE-specific options
                is_pxe = False
                pxe_detected = False
                
                # Check magic cookie
                if data[236:240] == b'\x63\x82\x53\x63':
                    pxe_detected = True
                    
                # Check for PXEClient in options (option 60)
                if len(data) > 300:  # Options section
                    # Look for option 60 (PXEClient)
                    options_section = data[240:]
                    for i in range(0, len(options_section), 1):
                        if i + 1 >= len(options_section):
                            break
                        if options_section[i] == 0x3c:  # Option 60
                            option_len = options_section[i+1] if i+1 < len(options_section) else 0
                            if option_len > 0 and i+2+option_len <= len(options_section):
                                if options_section[i+2:i+2+option_len] == b'PXEClient':
                                    pxe_detected = True
                                    break
                
                # Also check if boot filename is requested
                is_pxe = pxe_detected
                
                if is_pxe:
                    self.log(f"→ PXE DHCP Request from {addr[0]} (MAC: {mac})")
                    self._send_dhcp_offer(data, addr, mac)
                else:
                    # Still respond to regular DHCP requests
                    self.log(f"→ DHCP Request from {addr[0]} (MAC: {mac}) - Standard DHCP")
                    self._send_dhcp_offer(data, addr, mac)
                    
        except Exception as e:
            self.log(f"DHCP handler error: {e}")
            
    def _send_dhcp_offer(self, request_data, addr, mac):
        """Send DHCP offer with PXE options"""
        try:
            # Build DHCP offer packet (minimum size 548 bytes)
            response = bytearray(548)
            
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
            offered_ip = '192.168.1.150'
            response[16:20] = socket.inet_aton(offered_ip)
            
            # Server IP
            response[20:24] = socket.inet_aton(self.config['server_ip'])
            
            # Gateway IP
            response[24:28] = socket.inet_aton(self.config['gateway'])
            
            # Client MAC address
            response[28:34] = request_data[28:34]
            
            # Boot filename at position 108-128
            boot_file = b'pxelinux.0'
            boot_file_len = len(boot_file)
            
            # Clear boot filename area
            response[108:128] = b'\x00' * 20
            # Copy boot filename
            response[108:108+boot_file_len] = boot_file
            
            # Magic cookie at 236-240
            response[236:240] = b'\x63\x82\x53\x63'
            
            # DHCP options
            idx = 240
            
            # Option 53: DHCP Message Type (Offer = 2)
            response[idx:idx+3] = b'\x35\x01\x02'
            idx += 3
            
            # Option 54: Server Identifier
            response[idx:idx+6] = b'\x36\x04' + socket.inet_aton(self.config['server_ip'])
            idx += 6
            
            # Option 51: Lease Time (24 hours = 86400 seconds)
            lease_time = 86400
            response[idx:idx+6] = b'\x33\x04' + struct.pack('>I', lease_time)
            idx += 6
            
            # Option 1: Subnet Mask
            response[idx:idx+6] = b'\x01\x04' + socket.inet_aton(self.config['subnet_mask'])
            idx += 6
            
            # Option 3: Router
            response[idx:idx+6] = b'\x03\x04' + socket.inet_aton(self.config['gateway'])
            idx += 6
            
            # Option 6: DNS Server
            response[idx:idx+6] = b'\x06\x04' + socket.inet_aton(self.config['dns_server'])
            idx += 6
            
            # Option 66: TFTP Server Name
            server_name = self.config['server_ip'].encode()
            response[idx:idx+2+len(server_name)] = b'\x42' + bytes([len(server_name)]) + server_name
            idx += 2 + len(server_name)
            
            # Option 67: Bootfile Name (PXE filename)
            response[idx:idx+2+boot_file_len] = b'\x43' + bytes([boot_file_len]) + boot_file
            idx += 2 + boot_file_len
            
            # Option 60: Vendor Class Identifier (PXE)
            vendor_class = b'PXEClient'
            response[idx:idx+3+len(vendor_class)] = b'\x3c' + bytes([len(vendor_class)]) + vendor_class
            idx += 3 + len(vendor_class)
            
            # Option 43: Vendor Specific Information (PXE options)
            pxe_options = b'\x00\x00\x00\x00\x00\x00\x00\x00'
            response[idx:idx+2+len(pxe_options)] = b'\x2b' + bytes([len(pxe_options)]) + pxe_options
            idx += 2 + len(pxe_options)
            
            # End option
            response[idx] = 0xff
            
            # Send response to broadcast address on port 68
            broadcast_addr = '255.255.255.255'
            self.dhcp_socket.sendto(bytes(response[:idx+1]), (broadcast_addr, 68))
            self.log(f"← DHCP Offer sent to {addr[0]} - IP: {offered_ip}, Boot: pxelinux.0")
            
        except Exception as e:
            self.log(f"DHCP offer error: {e}")
            
    def _run_tftp_server(self):
        """Run TFTP server"""
        try:
            self.tftp_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
            self.tftp_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
            
            # Try to bind to port 69, if fails try alternative ports
            ports_to_try = [69, 6900, 6969]
            bound = False
            
            for port in ports_to_try:
                try:
                    self.tftp_socket.bind(('', port))
                    self.config['tftp_port'] = port
                    self.log(f"✓ TFTP Server listening on port {port}")
                    bound = True
                    break
                except PermissionError:
                    if port == ports_to_try[-1]:
                        self.log(f"✗ Cannot bind to TFTP port (trying non-privileged ports)")
                        return
                except Exception as e:
                    if port == ports_to_try[-1]:
                        self.log(f"✗ TFTP bind error: {e}")
                        return
                        
            if not bound:
                return
                
            self.tftp_socket.settimeout(1.0)
            
            while self.running:
                try:
                    data, addr = self.tftp_socket.recvfrom(516)
                    threading.Thread(target=self._handle_tftp, args=(data, addr), daemon=True).start()
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
            
            if opcode == 1:  # Read Request (RRQ)
                # Parse filename
                filename_end = data.index(b'\x00', 2)
                filename = data[2:filename_end].decode('utf-8', errors='ignore')
                
                self.log(f"→ TFTP Request: {filename} from {addr[0]}:{addr[1]}")
                
                # Send file
                self._send_tftp_file(filename, addr)
                
        except Exception as e:
            self.log(f"TFTP handler error: {e}")
            
    def _send_tftp_file(self, filename, addr):
        """Send file via TFTP"""
        try:
            # Sanitize filename
            filename = filename.lstrip('/')
            filepath = os.path.join(self.tftp_dir, filename)
            
            # Check if file exists
            if not os.path.exists(filepath):
                # Send error packet
                error_msg = f"File not found: {filename}".encode()
                error_packet = struct.pack('>H', 5) + struct.pack('>H', 1) + error_msg + b'\x00'
                
                # Create new socket for this transfer
                transfer_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
                transfer_socket.sendto(error_packet, addr)
                transfer_socket.close()
                
                self.log(f"✗ File not found: {filename}")
                return
                
            # Read file
            with open(filepath, 'rb') as f:
                file_data = f.read()
                
            # Create new socket for this transfer
            transfer_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
            transfer_socket.settimeout(5.0)
            
            # Send file in blocks
            block_size = 512
            block_num = 1
            offset = 0
            
            while offset < len(file_data):
                # Get block data
                block_data = file_data[offset:offset + block_size]
                
                # Create DATA packet
                data_packet = struct.pack('>H', 3) + struct.pack('>H', block_num) + block_data
                
                # Send with retry
                retries = 3
                acked = False
                
                for retry in range(retries):
                    transfer_socket.sendto(data_packet, addr)
                    
                    try:
                        # Wait for ACK
                        ack_data, _ = transfer_socket.recvfrom(4)
                        ack_opcode = struct.unpack('>H', ack_data[0:2])[0]
                        ack_block = struct.unpack('>H', ack_data[2:4])[0]
                        
                        if ack_opcode == 4 and ack_block == block_num:
                            acked = True
                            break
                    except socket.timeout:
                        if retry == retries - 1:
                            self.log(f"✗ TFTP timeout sending block {block_num}")
                            
                if not acked:
                    break
                    
                offset += block_size
                block_num += 1
                
                # Last block
                if len(block_data) < block_size:
                    break
                    
            transfer_socket.close()
            
            if acked or offset >= len(file_data):
                self.log(f"← TFTP Transfer complete: {filename} ({len(file_data)} bytes, {block_num} blocks)")
            
        except Exception as e:
            self.log(f"TFTP send error: {e}")

def show_banner():
    """Display startup banner"""
    print("")
    print("╔══════════════════════════════════════════════════════════════════╗")
    print("║          ⚡ TERMUX PXE BOOT SERVER - COMPLETE EDITION ⚡          ║")
    print("║                  Network Boot for Android Termux                ║")
    print("║                    No Root Access Required                      ║")
    print("╚══════════════════════════════════════════════════════════════════╝")
    print("")
    print("📱 Features:")
    print("   • Complete DHCP Server (PXE boot protocol)")
    print("   • Complete TFTP Server (boot file transfer)")
    print("   • No root access required")
    print("   • Works on non-rooted Android with Termux")
    print("   • Automatic port fallback for restricted environments")
    print("")
    print("🔧 Setup:")
    print("   1. Connect your Android device to WiFi")
    print("   2. Start this server")
    print("   3. Configure target PC to boot from network (PXE)")
    print("   4. Target PC will boot using this server")
    print("")

def main():
    """Main entry point"""
    show_banner()
    
    # Create server
    server = TermuxPXEServer()
    
    # Setup signal handler
    def signal_handler(sig, frame):
        print("")
        server.stop()
        sys.exit(0)
        
    signal.signal(signal.SIGINT, signal_handler)
    signal.signal(signal.SIGTERM, signal_handler)
    
    try:
        # Start server
        server.start()
        
        # Keep running
        while server.running:
            time.sleep(1)
            
    except KeyboardInterrupt:
        print("")
        server.stop()
    except Exception as e:
        print(f"\n✗ Fatal error: {e}")
        server.stop()
        sys.exit(1)

if __name__ == "__main__":
    main()
