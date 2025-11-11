#!/usr/bin/env python3
"""
ULTRA-AGGRESSIVE PXE E53 FIX - MASTER DEPLOYMENT SCRIPT
=======================================================

This is the ultimate deployment script that integrates ALL ultra-aggressive PXE bypass 
methods. It coordinates ARP poisoning, raw socket injection, bridge hijacking, and 
multi-protocol injection to completely circumvent router filtering.

USAGE: sudo python3 ULTRA_PXE_DEPLOYMENT.py <target_mac> [interface] [boot_filename]
       sudo python3 ULTRA_PXE_DEPLOYMENT.py --auto                # Auto-detect and deploy
       sudo python3 ULTRA_PXE_DEPLOYMENT.py --bridge [wifi] [eth] # Bridge hijacking mode
"""

import sys
import os
import subprocess
import threading
import time
import logging
import signal
import json
from datetime import datetime

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

class UltraPXEDeployment:
    """Master deployment coordinator for ultra-aggressive PXE bypass."""
    
    def __init__(self):
        self.target_mac = None
        self.interface = "eth0"
        self.wifi_interface = "wlan0"
        self.eth_interface = "eth0"
        self.boot_filename = "pxelinux.0"
        self.attack_running = False
        self.components = {}
        self.attack_processes = []
        
        # Attack status tracking
        self.arp_injection_active = False
        self.raw_socket_active = False
        self.bridge_hijack_active = False
        self.multi_proto_active = False
        
        logger.info("🎯 ULTRA-AGGRESSIVE PXE E53 BYPASS DEPLOYMENT SYSTEM")
        logger.info("💪 NOW WITH LINUX ON STEROIDS BOOT!")
        logger.info("=" * 60)
        
    def check_requirements(self):
        """Check all system requirements."""
        logger.info("🔍 Checking system requirements...")
        
        # Check root access
        if os.geteuid() != 0:
            logger.error("❌ This script must be run as root (sudo)")
            return False
        
        # Check scapy installation
        try:
            import scapy.all
            logger.info("✅ Scapy installed")
        except ImportError:
            logger.error("❌ Scapy not found. Install with: pip install scapy")
            return False
        
        # Check network interfaces
        interfaces = self.get_network_interfaces()
        if not interfaces:
            logger.error("❌ No network interfaces found")
            return False
        
        logger.info(f"✅ Found {len(interfaces)} network interfaces")
        return True
    
    def get_network_interfaces(self):
        """Get all available network interfaces."""
        try:
            result = subprocess.check_output(['ip', 'link', 'show'])
            interfaces = []
            
            lines = result.decode().split('\n')
            for line in lines:
                if ': ' in line and 'state ' in line:
                    interface = line.split(':')[1].split('@')[0].strip()
                    if interface not in ['lo', 'sit0', 'tunl0']:
                        interfaces.append(interface)
            
            return interfaces
        except:
            return []
    
    def detect_target_pc(self):
        """Auto-detect target PC MAC address."""
        logger.info("🔍 Auto-detecting target PC...")
        
        try:
            # Get ARP table
            result = subprocess.check_output(['arp', '-a'])
            mac_addresses = []
            
            lines = result.decode().split('\n')
            for line in lines:
                if 'ether' in line and 'incomplete' not in line:
                    parts = line.split()
                    if len(parts) >= 3:
                        mac = parts[2]
                        if mac and len(mac) == 17:
                            mac_addresses.append(mac)
            
            if mac_addresses:
                target = mac_addresses[0]  # Use first found
                logger.info(f"🎯 Auto-detected target MAC: {target}")
                return target
            
        except Exception as e:
            logger.warning(f"⚠️  Auto-detection failed: {e}")
        
        return None
    
    def deploy_all_attacks(self):
        """Deploy all ultra-aggressive attack methods simultaneously."""
        logger.info("🚀 DEPLOYING ALL ULTRA-AGGRESSIVE ATTACK METHODS")
        logger.info("=" * 60)
        
        self.attack_running = True
        
        try:
            # Start ARP poisoning attack
            if self.target_mac:
                arp_thread = threading.Thread(target=self.deploy_arp_attack, daemon=True)
                arp_thread.start()
                time.sleep(2)
            
            # Start raw socket injection
            raw_thread = threading.Thread(target=self.deploy_raw_socket_attack, daemon=True)
            raw_thread.start()
            time.sleep(2)
            
            # Start multi-protocol injection
            multi_thread = threading.Thread(target=self.deploy_multi_proto_attack, daemon=True)
            multi_thread.start()
            time.sleep(2)
            
            # Monitor attack status
            self.monitor_attacks()
            
        except KeyboardInterrupt:
            logger.info("🛑 Attack deployment interrupted by user")
        finally:
            self.cleanup_attacks()
    
    def deploy_arp_attack(self):
        """Deploy ARP poisoning attack."""
        try:
            import importlib.util
            spec = importlib.util.spec_from_file_location("ULTRA_PXE_INJECTOR", "ULTRA_PXE_INJECTOR.py")
            ultra_injector = importlib.util.module_from_spec(spec)
            spec.loader.exec_module(ultra_injector)
            
            logger.info("🔥 Starting ARP Poisoning Attack")
            self.arp_injection_active = True
            
            injector = ultra_injector.ARPPoisoningDHCPInjector(self.target_mac, self.boot_filename, self.interface)
            injector.start_attack()
            
        except Exception as e:
            logger.error(f"❌ ARP attack failed: {e}")
        finally:
            self.arp_injection_active = False
    
    def deploy_raw_socket_attack(self):
        """Deploy raw socket attack."""
        try:
            import importlib.util
            spec = importlib.util.spec_from_file_location("RAW_DHCP_INJECTOR", "RAW_DHCP_INJECTOR.py")
            raw_injector = importlib.util.module_from_spec(spec)
            spec.loader.exec_module(raw_injector)
            
            logger.info("⚡ Starting Raw Socket Attack")
            self.raw_socket_active = True
            
            injector = raw_injector.RawSocketDHCPInjector(self.interface, self.boot_filename)
            injector.start_injection()
            
        except Exception as e:
            logger.error(f"❌ Raw socket attack failed: {e}")
        finally:
            self.raw_socket_active = False
    
    def deploy_bridge_attack(self):
        """Deploy bridge hijacking attack."""
        try:
            import importlib.util
            spec = importlib.util.spec_from_file_location("BRIDGE_HIJACK", "BRIDGE_HIJACK.py")
            bridge_hijack = importlib.util.module_from_spec(spec)
            spec.loader.exec_module(bridge_hijack)
            
            logger.info("🌉 Starting Bridge Hijacking Attack")
            self.bridge_hijack_active = True
            
            hijacker = bridge_hijack.BridgeHijacker(self.wifi_interface, self.eth_interface, self.boot_filename)
            hijacker.start_bridge_hijacking()
            
        except Exception as e:
            logger.error(f"❌ Bridge hijack attack failed: {e}")
        finally:
            self.bridge_hijack_active = False
    
    def deploy_multi_proto_attack(self):
        """Deploy multi-protocol attack."""
        try:
            import importlib.util
            spec = importlib.util.spec_from_file_location("MULTI_PROTO_DHCP", "MULTI_PROTO_DHCP.py")
            multi_proto = importlib.util.module_from_spec(spec)
            spec.loader.exec_module(multi_proto)
            
            logger.info("📡 Starting Multi-Protocol Attack")
            self.multi_proto_active = True
            
            injector = multi_proto.MultiProtocolDHCPInjector(self.interface, self.boot_filename)
            injector.continuous_multi_proto_injection()
            
        except Exception as e:
            logger.error(f"❌ Multi-protocol attack failed: {e}")
        finally:
            self.multi_proto_active = False
    
    def monitor_attacks(self):
        """Monitor all attack components and provide real-time status."""
        logger.info("📊 MONITORING ATTACK STATUS")
        logger.info("-" * 40)
        
        while self.attack_running:
            status = []
            
            if self.arp_injection_active:
                status.append("ARP Poisoning: 🔥 ACTIVE")
            else:
                status.append("ARP Poisoning: ❌ INACTIVE")
            
            if self.raw_socket_active:
                status.append("Raw Socket: 🔥 ACTIVE")
            else:
                status.append("Raw Socket: ❌ INACTIVE")
            
            if self.bridge_hijack_active:
                status.append("Bridge Hijack: 🔥 ACTIVE")
            else:
                status.append("Bridge Hijack: ❌ INACTIVE")
            
            if self.multi_proto_active:
                status.append("Multi-Protocol: 🔥 ACTIVE")
            else:
                status.append("Multi-Protocol: ❌ INACTIVE")
            
            # Print status
            os.system('clear')
            print("🎯 ULTRA-AGGRESSIVE PXE E53 BYPASS - LIVE STATUS")
            print("=" * 60)
            print(f"🎯 Target MAC: {self.target_mac}")
            print(f"🌐 Interface: {self.interface}")
            print(f"🔧 Boot File: {self.boot_filename}")
            print("-" * 60)
            
            for s in status:
                print(s)
            
            print("-" * 60)
            print("Press Ctrl+C to stop all attacks")
            print(f"⏰ Time: {datetime.now().strftime('%H:%M:%S')}")
            
            time.sleep(5)  # Update every 5 seconds
    
    def cleanup_attacks(self):
        """Clean up all attack components."""
        logger.info("🧹 Cleaning up all attacks...")
        
        self.attack_running = False
        
        # Wait for threads to finish
        time.sleep(2)
        
        logger.info("✅ All attacks cleaned up")
    
    def auto_deploy(self):
        """Auto-detect and deploy without manual configuration."""
        logger.info("🤖 AUTO-DEPLOYMENT MODE")
        logger.info("=" * 40)
        
        # Auto-detect target
        self.target_mac = self.detect_target_pc()
        if not self.target_mac:
            logger.error("❌ Could not auto-detect target. Please specify target MAC.")
            return False
        
        # Auto-detect interfaces
        interfaces = self.get_network_interfaces()
        if 'eth0' in interfaces:
            self.interface = 'eth0'
        elif interfaces:
            self.interface = interfaces[0]
        
        if 'wlan0' in interfaces:
            self.wifi_interface = 'wlan0'
        
        logger.info(f"🎯 Auto-detected target: {self.target_mac}")
        logger.info(f"🌐 Auto-detected interface: {self.interface}")
        logger.info(f"📶 Auto-detected WiFi: {self.wifi_interface}")
        
        # Deploy all attacks
        self.deploy_all_attacks()
        return True
    
    def bridge_deploy(self, wifi_interface=None, eth_interface=None):
        """Deploy bridge hijacking mode."""
        logger.info("🌉 BRIDGE HIJACKING MODE")
        logger.info("=" * 40)
        
        # Auto-detect interfaces if not specified
        interfaces = self.get_network_interfaces()
        
        if wifi_interface:
            self.wifi_interface = wifi_interface
        elif 'wlan0' in interfaces:
            self.wifi_interface = 'wlan0'
        else:
            self.wifi_interface = interfaces[0] if interfaces else "wlan0"
        
        if eth_interface:
            self.interface = eth_interface
            self.eth_interface = eth_interface
        elif 'eth0' in interfaces:
            self.interface = 'eth0'
            self.eth_interface = 'eth0'
        else:
            self.interface = interfaces[1] if len(interfaces) > 1 else "eth0"
            self.eth_interface = self.interface
        
        logger.info(f"📶 WiFi Interface: {self.wifi_interface}")
        logger.info(f"🔌 Ethernet Interface: {self.interface}")
        
        # Deploy bridge hijacking attack
        try:
            self.deploy_bridge_attack()
        except KeyboardInterrupt:
            logger.info("🛑 Bridge hijacking stopped by user")
        finally:
            self.cleanup_attacks()
    
    def deploy_steroids_pxe(self, interface=None):
        """Deploy Linux on Steroids PXE bypass."""
        logger.info("💪 LINUX ON STEROIDS PXE MODE")
        logger.info("=" * 40)
        
        # Auto-detect interface if not specified
        interfaces = self.get_network_interfaces()
        if interface:
            self.interface = interface
        elif 'eth0' in interfaces:
            self.interface = 'eth0'
        else:
            self.interface = interfaces[0] if interfaces else "eth0"
        
        # Auto-detect target
        self.target_mac = self.detect_target_pc()
        
        logger.info(f"🎯 Steroids Target: {self.target_mac or 'BROADCAST'}")
        logger.info(f"🌐 Interface: {self.interface}")
        logger.info(f"🚀 Boot: Arch Linux on Steroids (MAXIMUM PERFORMANCE)")
        
        # Deploy steroids PXE bypass
        try:
            import importlib.util
            spec = importlib.util.spec_from_file_location("STEROIDS_PXE_BYPASS", "STEROIDS_PXE_BYPASS.py")
            steroids_bypass = importlib.util.module_from_spec(spec)
            spec.loader.exec_module(steroids_bypass)
            
            logger.info("💪 Starting LINUX ON STEROIDS PXE bypass")
            steroids = steroids_bypass.SteroidsPXEBypass(self.target_mac, self.interface)
            steroids.start_steroids_attack()
            
        except KeyboardInterrupt:
            logger.info("🛑 Steroids PXE bypass stopped by user")
        except Exception as e:
            logger.error(f"❌ Steroids PXE bypass failed: {e}")

def main():
    deployment = UltraPXEDeployment()
    
    # Check requirements first
    if not deployment.check_requirements():
        sys.exit(1)
    
    # Handle command line arguments
    if len(sys.argv) == 1 or sys.argv[1] == "--help" or sys.argv[1] == "-h":
        print("ULTRA-AGGRESSIVE PXE E53 FIX - DEPLOYMENT SCRIPT")
        print("=" * 50)
        print("Usage:")
        print("  sudo python3 ULTRA_PXE_DEPLOYMENT.py <target_mac> [interface] [boot_filename]")
        print("  sudo python3 ULTRA_PXE_DEPLOYMENT.py --auto")
        print("  sudo python3 ULTRA_PXE_DEPLOYMENT.py --bridge [wifi_interface] [eth_interface]")
        print("  sudo python3 ULTRA_PXE_DEPLOYMENT.py --steroids [interface]")
        print()
        print("Examples:")
        print("  sudo python3 ULTRA_PXE_DEPLOYMENT.py aa:bb:cc:dd:ee:ff eth0 pxelinux.0")
        print("  sudo python3 ULTRA_PXE_DEPLOYMENT.py --auto")
        print("  sudo python3 ULTRA_PXE_DEPLOYMENT.py --bridge wlan0 eth0")
        print("  sudo python3 ULTRA_PXE_DEPLOYMENT.py --steroids")
        print()
        print("💪 NEW: LINUX ON STEROIDS BOOT - Maximum Performance!")
        sys.exit(0)
    
    elif sys.argv[1] == "--auto":
        deployment.auto_deploy()
    
    elif sys.argv[1] == "--steroids":
        interface = sys.argv[2] if len(sys.argv) > 2 else None
        deployment.deploy_steroids_pxe(interface)
    
    elif sys.argv[1] == "--bridge":
        wifi_if = sys.argv[2] if len(sys.argv) > 2 else None
        eth_if = sys.argv[3] if len(sys.argv) > 3 else None
        deployment.bridge_deploy(wifi_if, eth_if)
    
    else:
        # Manual deployment
        if len(sys.argv) < 2:
            print("❌ Target MAC address required")
            print("Use --help for usage information")
            sys.exit(1)
        
        deployment.target_mac = sys.argv[1]
        deployment.interface = sys.argv[2] if len(sys.argv) > 2 else "eth0"
        deployment.boot_filename = sys.argv[3] if len(sys.argv) > 3 else "pxelinux.0"
        
        deployment.deploy_all_attacks()

if __name__ == "__main__":
    main()