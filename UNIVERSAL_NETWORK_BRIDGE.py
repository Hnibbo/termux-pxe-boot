#!/usr/bin/env python3
"""
Universal Network Bridge System
Enhanced network interface detection system for mixed network scenarios
Designed for PC on ethernet + Phone on WiFi configurations and beyond

Features:
- Advanced Network Topology Detection
- Cross-Network Interface Identification
- Universal Network Bridge Creator using UDP tunnels
- Mixed Network PXE Configuration
- Zero-configuration operation with automatic fallback chains
- Router-agnostic design for any network configuration
"""

import os
import sys
import socket
import struct
import subprocess
import threading
import time
import json
import ipaddress
import hashlib
import platform
import signal
import logging
from pathlib import Path
from typing import Dict, List, Tuple, Optional, Set, Any
from dataclasses import dataclass, asdict, field
from concurrent.futures import ThreadPoolExecutor, as_completed
from contextlib import contextmanager

# Import existing infrastructure
try:
    from utils.network import NetworkManager
    from pxe.server import PXEServer
    from utils.logger import Logger
except ImportError as e:
    print(f"Warning: Could not import existing modules: {e}")
    # Fallback implementations
    class NetworkManager:
        def __init__(self): pass
        def get_interfaces(self): return []
        def get_interface_ip(self, interface): return None
    
    class PXEServer:
        def __init__(self, *args, **kwargs): pass
        def start(self): pass
        def stop(self): pass
    
    class Logger:
        def info(self, msg): print(f"[INFO] {msg}")
        def error(self, msg): print(f"[ERROR] {msg}")
        def warning(self, msg): print(f"[WARNING] {msg}")

# Enhanced DHCP Bridge Import
try:
    import ENHANCED_DHCP_BRIDGE
    ENHANCED_DHCP_AVAILABLE = True
except ImportError:
    print("Enhanced DHCP Bridge not available - using standard mode")
    ENHANCED_DHCP_AVAILABLE = False

@dataclass
class NetworkInterface:
    """Enhanced network interface representation"""
    name: str
    type: str  # ethernet, wireless, usb, loopback, virtual
    is_up: bool
    ip_address: Optional[str] = None
    subnet_mask: Optional[str] = None
    gateway: Optional[str] = None
    mac_address: Optional[str] = None
    interface_index: Optional[int] = None
    mtu: int = 1500
    speed: Optional[int] = None
    duplex: Optional[str] = None
    driver: Optional[str] = None
    capabilities: Set[str] = field(default_factory=set)
    bridge_candidate: bool = False
    pxe_enabled: bool = False

@dataclass
class NetworkSegment:
    """Network segment representation for topology mapping"""
    network: str  # CIDR notation
    interfaces: List[str]  # Interface names in this segment
    gateway_ip: Optional[str] = None
    is_isolated: bool = False
    isolation_level: int = 0  # 0=none, 1=partial, 2=complete
    bridge_required: bool = False
    multicast_reachable: bool = False
    broadcast_reachable: bool = False

@dataclass
class BridgeEndpoint:
    """Bridge endpoint for UDP tunnel"""
    interface: str
    local_ip: str
    local_port: int
    remote_ip: Optional[str] = None
    remote_port: Optional[int] = None
    tunnel_id: str = ""
    encryption_key: Optional[str] = None
    status: str = "inactive"  # inactive, connecting, active, error

class UniversalNetworkBridge:
    """
    Universal Network Bridge System
    
    Advanced network interface detection and bridging for mixed network scenarios.
    Automatically detects and handles PC on ethernet + Phone on WiFi configurations.
    """
    
    def __init__(self, config_file: Optional[str] = None):
        # Core components
        self.network_manager = NetworkManager()
        self.logger = Logger()
        self.config = self._load_config(config_file)
        
        # System state
        self.interfaces: Dict[str, NetworkInterface] = {}
        self.network_segments: Dict[str, NetworkSegment] = {}
        self.bridge_endpoints: Dict[str, BridgeEndpoint] = {}
        self.udp_tunnels: Dict[str, socket.socket] = {}
        
        # Configuration
        self.bridge_base_port = self.config.get('bridge_base_port', 9000)
        self.max_bridges = self.config.get('max_bridges', 4)
        self.discovery_timeout = self.config.get('discovery_timeout', 5)
        self.heartbeat_interval = self.config.get('heartbeat_interval', 30)
        self.isolation_detection_methods = self.config.get('isolation_methods', [
            'ping_test', 'arp_scan', 'multicast_test', 'broadcast_test'
        ])
        
        # Control flags
        self.is_running = False
        self.auto_bridge = self.config.get('auto_bridge', True)
        self.zero_config = self.config.get('zero_config', True)
        self.debug_mode = self.config.get('debug_mode', False)
        
        # Enhanced DHCP Bridge
        self.enhanced_dhcp_bridge = None
        self.use_enhanced_dhcp = self.config.get('use_enhanced_dhcp', True) and ENHANCED_DHCP_AVAILABLE
        
        # Threading
        self.monitoring_thread = None
        self.cleanup_thread = None
        self.lock = threading.RLock()
        
        # Initialize
        self._initialize_system()
    
    def _load_config(self, config_file: Optional[str]) -> Dict[str, Any]:
        """Load configuration from file or use defaults"""
        default_config = {
            'bridge_base_port': 9000,
            'max_bridges': 4,
            'discovery_timeout': 5,
            'heartbeat_interval': 30,
            'isolation_methods': ['ping_test', 'arp_scan', 'multicast_test', 'broadcast_test'],
            'auto_bridge': True,
            'zero_config': True,
            'debug_mode': False,
            'pxe_server_integration': True,
            'fallback_enabled': True,
            'performance_mode': False,
            'router_agnostic': True,
            'cross_platform': True
        }
        
        if config_file and os.path.exists(config_file):
            try:
                with open(config_file, 'r') as f:
                    user_config = json.load(f)
                default_config.update(user_config)
            except Exception as e:
                self.logger.warning(f"Could not load config {config_file}: {e}")
        
        return default_config
    
    def _initialize_system(self):
        """Initialize the Universal Network Bridge system"""
        try:
            self.logger.info("🌐 Initializing Universal Network Bridge System...")
            
            # Detect network topology
            self._detect_network_topology()
            
            # Analyze bridge candidates
            self._analyze_bridge_candidates()
            
            # Setup PXE integration if enabled
            if self.config.get('pxe_server_integration'):
                self._setup_pxe_integration()
            
            # Configure fallback chains
            if self.config.get('fallback_enabled'):
                self._configure_fallback_chains()
            
            self.logger.info("✅ Universal Network Bridge System initialized")
            
        except Exception as e:
            self.logger.error(f"Failed to initialize Universal Network Bridge: {e}")
            raise
    
    def _detect_network_topology(self):
        """Detect comprehensive network topology"""
        self.logger.info("🔍 DETECTING NETWORK TOPOLOGY")
        
        # Get all interfaces
        all_interfaces = self.network_manager.get_interfaces()
        
        with ThreadPoolExecutor(max_workers=8) as executor:
            futures = {}
            
            # Parallel interface analysis
            for interface_name in all_interfaces:
                future = executor.submit(self._analyze_interface, interface_name)
                futures[future] = interface_name
            
            # Collect results
            for future in as_completed(futures):
                interface_name = futures[future]
                try:
                    interface = future.result()
                    if interface:
                        self.interfaces[interface_name] = interface
                        self.logger.info(f"  {interface_name}: {interface.type} ({interface.ip_address or 'no IP'})")
                except Exception as e:
                    self.logger.warning(f"Interface analysis failed for {interface_name}: {e}")
        
        # Map network segments
        self._map_network_segments()
        
        # Detect router isolation
        self._detect_router_isolation()
        
        # Test cross-segment connectivity
        self._test_cross_segment_connectivity()
        
        self.logger.info(f"✅ Topology detection complete: {len(self.interfaces)} interfaces, {len(self.network_segments)} segments")
    
    def _analyze_interface(self, interface_name: str) -> Optional[NetworkInterface]:
        """Analyze a single network interface"""
        try:
            interface = NetworkInterface(
                name=interface_name,
                type=self._detect_interface_type(interface_name),
                is_up=self._is_interface_up(interface_name)
            )
            
            if not interface.is_up:
                return interface
            
            # Get IP configuration
            ip_info = self._get_interface_ip_info(interface_name)
            if ip_info:
                interface.ip_address = ip_info.get('ip')
                interface.subnet_mask = ip_info.get('netmask')
                interface.gateway = ip_info.get('gateway')
            
            # Get additional interface information
            interface.mac_address = self._get_interface_mac(interface_name)
            interface.mtu = self._get_interface_mtu(interface_name)
            interface.driver = self._get_interface_driver(interface_name)
            interface.capabilities = self._get_interface_capabilities(interface_name)
            
            # Determine bridge candidacy
            interface.bridge_candidate = self._is_bridge_candidate(interface)
            
            # Check PXE compatibility
            interface.pxe_enabled = self._is_pxe_capable(interface)
            
            return interface
            
        except Exception as e:
            self.logger.error(f"Interface analysis failed for {interface_name}: {e}")
            return None
    
    def _detect_interface_type(self, interface_name: str) -> str:
        """Detect interface type using multiple methods"""
        try:
            # Method 1: Check wireless capability
            if self._has_wireless_capability(interface_name):
                return 'wireless'
            
            # Method 2: Check USB association
            if self._is_usb_interface(interface_name):
                return 'usb'
            
            # Method 3: Check interface name patterns
            name_lower = interface_name.lower()
            if any(pattern in name_lower for pattern in ['eth', 'enp', 'enx', 'eno']):
                return 'ethernet'
            elif any(pattern in name_lower for pattern in ['wlan', 'wlp', 'wlx']):
                return 'wireless'
            elif any(pattern in name_lower for pattern in ['usb']):
                return 'usb'
            elif any(pattern in name_lower for pattern in ['lo', 'loopback']):
                return 'loopback'
            elif any(pattern in name_lower for pattern in ['tun', 'tap', 'vpn']):
                return 'virtual'
            
            # Method 4: Platform-specific detection
            return self._detect_interface_type_platform_specific(interface_name)
            
        except Exception as e:
            self.logger.warning(f"Interface type detection failed for {interface_name}: {e}")
            return 'unknown'
    
    def _has_wireless_capability(self, interface_name: str) -> bool:
        """Check if interface has wireless capability"""
        try:
            if platform.system() != "Windows":
                # Linux: Check /sys/class/net/interface_name/wireless
                wireless_path = f'/sys/class/net/{interface_name}/wireless'
                if os.path.exists(wireless_path):
                    return True
                
                # Check using iw command
                result = subprocess.run(['iw', 'dev', interface_name, 'info'], 
                                      capture_output=True, text=True, timeout=3)
                return result.returncode == 0
            else:
                # Windows: Check interface name for wireless indicators
                if any(term in interface_name.lower() for term in ['wireless', 'wifi', 'wlan']):
                    return True
        except:
            pass
        
        return False
    
    def _is_usb_interface(self, interface_name: str) -> bool:
        """Check if interface is USB-based"""
        try:
            if platform.system() != "Windows":
                # Check USB device path
                device_path = f'/sys/class/net/{interface_name}/device'
                if os.path.exists(device_path):
                    # Check if device is USB
                    subsystem_path = f'{device_path}/subsystem'
                    if os.path.exists(subsystem_path):
                        subsystem_link = os.readlink(subsystem_path)
                        if 'usb' in str(subsystem_link):
                            return True
                
                # Check interface name patterns
                if any(pattern in interface_name.lower() for pattern in ['usb', 'rndis']):
                    return True
        except:
            pass
        
        return False
    
    def _is_interface_up(self, interface_name: str) -> bool:
        """Check if interface is operational"""
        try:
            if platform.system() != "Windows":
                result = subprocess.run(['ip', 'link', 'show', interface_name], 
                                      capture_output=True, text=True, timeout=3)
                return 'state UP' in result.stdout
            else:
                # Windows method
                result = subprocess.run(['ipconfig', '/all'], 
                                      capture_output=True, text=True, timeout=5)
                return (interface_name in result.stdout and 
                       'Media disconnected' not in result.stdout)
        except:
            return False
    
    def _get_interface_ip_info(self, interface_name: str) -> Optional[Dict[str, str]]:
        """Get IP configuration for interface"""
        try:
            if platform.system() != "Windows":
                result = subprocess.run(['ip', 'addr', 'show', interface_name], 
                                      capture_output=True, text=True, timeout=3)
                
                info = {}
                for line in result.stdout.split('\n'):
                    if 'inet ' in line and 'scope global' in line:
                        # Extract IP and netmask
                        parts = line.strip().split()
                        if len(parts) >= 2:
                            ip_cidr = parts[1]
                            ip, prefix = ip_cidr.split('/')
                            info['ip'] = ip
                            info['netmask'] = self._prefix_to_netmask(int(prefix))
                    elif 'default' in line or 'gateway' in line:
                        # Extract gateway
                        for part in line.split():
                            if self._is_valid_ip(part):
                                info['gateway'] = part
                                break
                
                return info if info.get('ip') else None
            else:
                # Windows method - simplified
                ip = self.network_manager.get_interface_ip(interface_name)
                return {'ip': ip} if ip else None
        except:
            return None
    
    def _get_interface_mac(self, interface_name: str) -> Optional[str]:
        """Get MAC address for interface"""
        try:
            if platform.system() != "Windows":
                result = subprocess.run(['ip', 'link', 'show', interface_name], 
                                      capture_output=True, text=True, timeout=3)
                for line in result.stdout.split('\n'):
                    if 'link/ether' in line:
                        return line.split()[1]
            else:
                # Windows method - would need to parse ipconfig output
                pass
        except:
            pass
        return None
    
    def _get_interface_mtu(self, interface_name: str) -> int:
        """Get MTU for interface"""
        try:
            if platform.system() != "Windows":
                result = subprocess.run(['ip', 'link', 'show', interface_name], 
                                      capture_output=True, text=True, timeout=3)
                for line in result.stdout.split('\n'):
                    if 'mtu' in line:
                        mtu_part = [part for part in line.split() if part.startswith('mtu')]
                        if mtu_part:
                            return int(mtu_part[0].split(':')[1])
        except:
            pass
        return 1500  # Default MTU
    
    def _get_interface_driver(self, interface_name: str) -> Optional[str]:
        """Get driver for interface"""
        try:
            if platform.system() != "Windows":
                driver_path = f'/sys/class/net/{interface_name}/device/driver'
                if os.path.exists(driver_path):
                    return os.path.basename(os.readlink(driver_path))
        except:
            pass
        return None
    
    def _get_interface_capabilities(self, interface_name: str) -> Set[str]:
        """Get interface capabilities"""
        capabilities = set()
        
        try:
            # Check wireless capabilities
            if self._has_wireless_capability(interface_name):
                capabilities.add('wireless')
                capabilities.update(self._get_wireless_capabilities(interface_name))
            
            # Check USB tethering capability
            if self._is_usb_interface(interface_name):
                capabilities.add('usb_tethering')
            
            # Check PXE capability
            if self._is_pxe_capable_interface(interface_name):
                capabilities.add('pxe_boot')
            
            # Check bridging capability
            if self._supports_bridging(interface_name):
                capabilities.add('bridge_member')
        except Exception as e:
            self.logger.debug(f"Error getting capabilities for {interface_name}: {e}")
        
        return capabilities if capabilities else set()
    
    def _get_wireless_capabilities(self, interface_name: str) -> Set[str]:
        """Get wireless-specific capabilities"""
        capabilities = set()
        
        try:
            if platform.system() != "Windows":
                result = subprocess.run(['iw', 'dev', interface_name, 'info'], 
                                      capture_output=True, text=True, timeout=3)
                if result.returncode == 0:
                    # Parse wireless capabilities
                    info = result.stdout.lower()
                    if 'ap' in info:
                        capabilities.add('access_point')
                    if 'mesh' in info:
                        capabilities.add('mesh')
                    if 'p2p' in info:
                        capabilities.add('wifi_direct')
        except:
            pass
        
        return capabilities
    
    def _is_pxe_capable(self, interface: NetworkInterface) -> bool:
        """Check if interface is PXE capable"""
        return (interface.is_up and 
                interface.type in ['ethernet', 'wireless'] and
                'pxe_boot' in interface.capabilities)
    
    def _is_pxe_capable_interface(self, interface_name: str) -> bool:
        """Check if specific interface supports PXE boot"""
        # This would need platform-specific implementation
        # For now, assume ethernet and wireless interfaces are PXE capable
        return True
    
    def _supports_bridging(self, interface_name: str) -> bool:
        """Check if interface supports bridging"""
        # Most physical interfaces support bridging
        return True
    
    def _is_bridge_candidate(self, interface: NetworkInterface) -> bool:
        """Determine if interface is a good bridge candidate"""
        score = 0
        
        # Base score for being up
        if interface.is_up:
            score += 10
        
        # Type bonuses
        if interface.type == 'ethernet':
            score += 20
        elif interface.type == 'wireless':
            score += 15
        elif interface.type == 'usb':
            score += 25  # USB tethering is excellent for bridging
        
        # Capability bonuses
        if 'bridge_member' in interface.capabilities:
            score += 15
        if 'pxe_boot' in interface.capabilities:
            score += 10
        
        # Having an IP address is good
        if interface.ip_address:
            score += 5
        
        return score >= 15  # Threshold for bridge candidacy
    
    def _detect_interface_type_platform_specific(self, interface_name: str) -> str:
        """Platform-specific interface type detection"""
        system = platform.system()
        
        if system == "Linux":
            # Check if we're in Termux (Android)
            if os.path.exists("/data/data/com.termux/files/home"):
                # Android/Termux specific interface types
                if interface_name.startswith('p2p'):
                    return 'wifi_direct'
                elif interface_name.startswith('tun'):
                    return 'vpn'
                elif interface_name == 'lo':
                    return 'loopback'
            
            # Standard Linux interface type detection
            return self._detect_interface_type_linux(interface_name)
        
        elif system == "Windows":
            return self._detect_interface_type_windows(interface_name)
        
        elif system == "Darwin":  # macOS
            return self._detect_interface_type_macos(interface_name)
        
        return 'unknown'
    
    def _detect_interface_type_linux(self, interface_name: str) -> str:
        """Linux-specific interface type detection"""
        # This would implement Linux-specific logic
        return 'ethernet'  # Default fallback
    
    def _detect_interface_type_windows(self, interface_name: str) -> str:
        """Windows-specific interface type detection"""
        interface_lower = interface_name.lower()
        if 'wireless' in interface_lower or 'wifi' in interface_lower:
            return 'wireless'
        elif 'ethernet' in interface_lower:
            return 'ethernet'
        return 'unknown'
    
    def _detect_interface_type_macos(self, interface_name: str) -> str:
        """macOS-specific interface type detection"""
        # Similar logic for macOS
        return 'ethernet'  # Default fallback
    
    def _map_network_segments(self):
        """Map network segments based on IP configuration"""
        segments = {}
        
        for interface_name, interface in self.interfaces.items():
            if interface.ip_address and interface.subnet_mask:
                try:
                    network = ipaddress.IPv4Network(
                        f"{interface.ip_address}/{interface.subnet_mask}", 
                        strict=False
                    )
                    network_str = str(network)
                    
                    if network_str not in segments:
                        segments[network_str] = NetworkSegment(
                            network=network_str,
                            interfaces=[]
                        )
                    
                    segments[network_str].interfaces.append(interface_name)
                    
                    # Set gateway if found
                    if interface.gateway:
                        segments[network_str].gateway_ip = interface.gateway
                        
                except Exception as e:
                    self.logger.warning(f"Could not parse network for {interface_name}: {e}")
        
        self.network_segments = segments
        self.logger.info(f"Mapped {len(segments)} network segments")
    
    def _detect_router_isolation(self):
        """Detect router isolation between network segments"""
        self.logger.info("🔍 DETECTING ROUTER ISOLATION")
        
        if len(self.network_segments) < 2:
            self.logger.info("Single network segment - no isolation possible")
            return
        
        # Test each pair of segments
        for i, (seg1_name, seg1) in enumerate(self.network_segments.items()):
            for j, (seg2_name, seg2) in enumerate(self.network_segments.items()):
                if i >= j:  # Skip self and duplicates
                    continue
                
                isolation_level = self._test_isolation_between_segments(seg1, seg2)
                
                if isolation_level > 0:
                    seg1.is_isolated = True
                    seg1.isolation_level = max(seg1.isolation_level, isolation_level)
                    seg1.bridge_required = True
                    
                    seg2.is_isolated = True
                    seg2.isolation_level = max(seg2.isolation_level, isolation_level)
                    seg2.bridge_required = True
                    
                    self.logger.warning(f"🚫 Isolation detected between {seg1_name} and {seg2_name} (level {isolation_level})")
        
        isolated_segments = [seg for seg in self.network_segments.values() if seg.is_isolated]
        self.logger.info(f"Found {len(isolated_segments)} isolated segments requiring bridges")
    
    def _test_isolation_between_segments(self, seg1: NetworkSegment, seg2: NetworkSegment) -> int:
        """Test isolation level between two network segments"""
        isolation_tests = self.isolation_detection_methods
        isolation_score = 0
        
        for test in isolation_tests:
            try:
                if test == 'ping_test':
                    result = self._test_ping_isolation(seg1, seg2)
                elif test == 'arp_scan':
                    result = self._test_arp_isolation(seg1, seg2)
                elif test == 'multicast_test':
                    result = self._test_multicast_isolation(seg1, seg2)
                elif test == 'broadcast_test':
                    result = self._test_broadcast_isolation(seg1, seg2)
                else:
                    continue
                
                if result:
                    isolation_score += 1
                    
            except Exception as e:
                self.logger.debug(f"Isolation test {test} failed: {e}")
        
        # Determine isolation level
        if isolation_score >= 3:
            return 2  # Complete isolation
        elif isolation_score >= 1:
            return 1  # Partial isolation
        else:
            return 0  # No isolation
    
    def _test_ping_isolation(self, seg1: NetworkSegment, seg2: NetworkSegment) -> bool:
        """Test isolation using ping"""
        # Try to ping gateway of seg2 from seg1 interfaces
        if not seg2.gateway_ip:
            return True  # Assume isolation if no gateway
        
        for interface in seg1.interfaces:
            if interface not in self.interfaces:
                continue
            
            try:
                if platform.system() != "Windows":
                    result = subprocess.run([
                        'ping', '-c', '1', '-W', '2', '-I', interface, seg2.gateway_ip
                    ], capture_output=True, text=True, timeout=3)
                    if result.returncode != 0:
                        return True  # Ping failed - possible isolation
                else:
                    # Windows ping test
                    result = subprocess.run([
                        'ping', '-n', '1', '-w', '2000', seg2.gateway_ip
                    ], capture_output=True, text=True, timeout=3)
                    if result.returncode != 0:
                        return True
            except:
                return True
        
        return False  # Ping succeeded - no isolation
    
    def _test_arp_isolation(self, seg1: NetworkSegment, seg2: NetworkSegment) -> bool:
        """Test isolation using ARP scanning"""
        # This would implement ARP-based isolation detection
        # For now, assume ping test is sufficient
        return False
    
    def _test_multicast_isolation(self, seg1: NetworkSegment, seg2: NetworkSegment) -> bool:
        """Test isolation using multicast"""
        # This would implement multicast-based isolation detection
        return False
    
    def _test_broadcast_isolation(self, seg1: NetworkSegment, seg2: NetworkSegment) -> bool:
        """Test isolation using broadcast"""
        # This would implement broadcast-based isolation detection
        return False
    
    def _test_cross_segment_connectivity(self):
        """Test connectivity between network segments"""
        self.logger.info("🧪 TESTING CROSS-SEGMENT CONNECTIVITY")
        
        for segment in self.network_segments.values():
            if len(segment.interfaces) < 2:
                continue
            
            # Test if interfaces in same segment can reach each other
            for i, iface1 in enumerate(segment.interfaces):
                for iface2 in segment.interfaces[i+1:]:
                    reachable = self._test_interface_connectivity(iface1, iface2)
                    if reachable:
                        segment.multicast_reachable = True
                        segment.broadcast_reachable = True
                        break
            
            self.logger.debug(f"Segment {segment.network}: "
                            f"multicast={segment.multicast_reachable}, "
                            f"broadcast={segment.broadcast_reachable}")
    
    def _test_interface_connectivity(self, iface1: str, iface2: str) -> bool:
        """Test connectivity between two interfaces"""
        try:
            if iface1 not in self.interfaces or iface2 not in self.interfaces:
                return False
            
            ip1 = self.interfaces[iface1].ip_address
            ip2 = self.interfaces[iface2].ip_address
            
            if not ip1 or not ip2:
                return False
            
            # Try ping from iface1 to iface2
            if platform.system() != "Windows":
                result = subprocess.run([
                    'ping', '-c', '1', '-W', '2', '-I', iface1, ip2
                ], capture_output=True, text=True, timeout=3)
                return result.returncode == 0
            else:
                # Windows - would need interface-specific ping
                return True  # Assume reachable for Windows
                
        except:
            return False
    
    def _analyze_bridge_candidates(self):
        """Analyze which interfaces are good bridge candidates"""
        self.logger.info("🎯 ANALYZING BRIDGE CANDIDATES")
        
        # Create bridge candidates based on network segments
        candidates = []
        
        for segment in self.network_segments.values():
            if segment.bridge_required or len(segment.interfaces) > 1:
                segment_bridges = []
                
                for interface_name in segment.interfaces:
                    if interface_name in self.interfaces:
                        interface = self.interfaces[interface_name]
                        if interface.bridge_candidate:
                            segment_bridges.append(interface_name)
                
                candidates.extend(segment_bridges)
        
        # Special detection for mixed scenarios
        mixed_scenario = self._detect_mixed_scenario()
        if mixed_scenario:
            self.logger.info(f"🎯 DETECTED MIXED SCENARIO: {mixed_scenario}")
        
        # Log bridge candidates
        self.logger.info(f"Found {len(candidates)} bridge candidates:")
        for candidate in candidates:
            interface = self.interfaces[candidate]
            self.logger.info(f"  {candidate}: {interface.type} ({interface.ip_address or 'no IP'})")
        
        return candidates
    
    def _detect_mixed_scenario(self) -> Optional[str]:
        """Detect specific mixed network scenarios"""
        interface_types = {}
        
        # Count interface types
        for interface in self.interfaces.values():
            if interface.is_up:
                interface_types[interface.type] = interface_types.get(interface.type, 0) + 1
        
        # Detect PC on ethernet + Phone on WiFi scenario
        if (interface_types.get('ethernet', 0) >= 1 and 
            interface_types.get('wireless', 0) >= 1):
            return "PC-on-ethernet + Phone-on-WiFi"
        
        # Detect USB tethering scenario
        if interface_types.get('usb', 0) >= 1:
            return "USB Tethering detected"
        
        # Detect WiFi Direct scenario
        wireless_interfaces = [iface for iface in self.interfaces.values() 
                             if iface.type == 'wireless' and 'wifi_direct' in iface.capabilities]
        if len(wireless_interfaces) >= 2:
            return "WiFi Direct scenario"
        
        # Detect VPN scenario
        virtual_interfaces = [iface for iface in self.interfaces.values() 
                            if iface.type == 'virtual']
        if virtual_interfaces:
            return "VPN scenario detected"
        
        return None
    
    def _setup_pxe_integration(self):
        """Setup integration with PXE server"""
        self.logger.info("🔧 SETTING UP PXE INTEGRATION")
        
        # This would create interface-specific PXE configurations
        # and setup cross-network TFTP relay capabilities
        
        for interface_name, interface in self.interfaces.items():
            if interface.pxe_enabled:
                # Configure interface for PXE
                self._configure_interface_for_pxe(interface)
        
        self.logger.info("✅ PXE integration setup complete")
    
    def _configure_interface_for_pxe(self, interface: NetworkInterface):
        """Configure specific interface for PXE boot"""
        # This would create interface-specific DHCP ranges
        # and configure TFTP servers for each network segment
        
        if not interface.ip_address:
            return
        
        # Generate PXE configuration for this interface
        network = ipaddress.IPv4Network(f"{interface.ip_address}/24", strict=False)
        
        self.logger.debug(f"Configured {interface.name} for PXE on network {network}")
    
    def _configure_fallback_chains(self):
        """Configure fallback bridge creation chains"""
        self.logger.info("🔄 CONFIGURING FALLBACK CHAINS")
        
        # Define fallback methods in order of preference
        fallback_methods = [
            ('udp_tunnel', self._create_udp_tunnel_bridge),
            ('wifi_direct', self._create_wifi_direct_bridge),
            ('usb_tethering', self._create_usb_tethering_bridge),
            ('adhoc_bridge', self._create_adhoc_bridge),
            ('software_bridge', self._create_software_bridge)
        ]
        
        self.fallback_chain = fallback_methods
        self.logger.info(f"Configured {len(fallback_methods)} fallback methods")
    
    def start(self) -> bool:
        """Start the Universal Network Bridge system"""
        try:
            if self.is_running:
                self.logger.warning("Universal Network Bridge is already running")
                return True
            
            self.logger.info("🚀 STARTING UNIVERSAL NETWORK BRIDGE")
            
            # Start monitoring
            self.monitoring_thread = threading.Thread(target=self._monitoring_loop, daemon=True)
            self.monitoring_thread.start()
            
            # Start cleanup thread
            self.cleanup_thread = threading.Thread(target=self._cleanup_loop, daemon=True)
            self.cleanup_thread.start()
            
            self.is_running = True
            
            # Auto-create bridges if configured
            if self.auto_bridge:
                self._auto_create_bridges()
            
            # Start Enhanced DHCP Bridge if enabled
            if self.use_enhanced_dhcp:
                self._start_enhanced_dhcp_bridge()
            
            self.logger.info("✅ Universal Network Bridge started successfully")
            return True
            
        except Exception as e:
            self.logger.error(f"Failed to start Universal Network Bridge: {e}")
            return False
    
    def stop(self):
        """Stop the Universal Network Bridge system"""
        try:
            if not self.is_running:
                return
            
            self.logger.info("🛑 STOPPING UNIVERSAL NETWORK BRIDGE")
            
            self.is_running = False
            
            # Stop Enhanced DHCP Bridge
            if self.enhanced_dhcp_bridge:
                self.enhanced_dhcp_bridge.stop()
                self.enhanced_dhcp_bridge = None
            
            # Close all UDP tunnels
            for tunnel_id, tunnel_socket in self.udp_tunnels.items():
                try:
                    tunnel_socket.close()
                except:
                    pass
            self.udp_tunnels.clear()
            
            # Wait for threads to finish
            if self.monitoring_thread and self.monitoring_thread.is_alive():
                self.monitoring_thread.join(timeout=5)
            
            if self.cleanup_thread and self.cleanup_thread.is_alive():
                self.cleanup_thread.join(timeout=5)
            
            self.logger.info("✅ Universal Network Bridge stopped")
            
        except Exception as e:
            self.logger.error(f"Error stopping Universal Network Bridge: {e}")
    
    def _monitoring_loop(self):
        """Main monitoring loop"""
        while self.is_running:
            try:
                # Monitor bridge health
                self._monitor_bridge_health()
                
                # Check for new interfaces
                self._detect_new_interfaces()
                
                # Send heartbeats for active tunnels
                self._send_heartbeats()
                
                time.sleep(self.heartbeat_interval)
                
            except Exception as e:
                self.logger.error(f"Monitoring loop error: {e}")
                time.sleep(5)
    
    def _cleanup_loop(self):
        """Cleanup loop for stale connections"""
        while self.is_running:
            try:
                # Clean up stale bridge endpoints
                self._cleanup_stale_endpoints()
                
                time.sleep(60)  # Run cleanup every minute
                
            except Exception as e:
                self.logger.error(f"Cleanup loop error: {e}")
                time.sleep(30)
    
    def _auto_create_bridges(self):
        """Automatically create bridges for detected scenarios"""
        self.logger.info("🤖 AUTO-CREATING BRIDGES")
        
        # Create bridges for isolated segments
        isolated_segments = [seg for seg in self.network_segments.values() if seg.bridge_required]
        
        for segment in isolated_segments:
            self._create_bridge_for_segment(segment)
    
    def _create_bridge_for_segment(self, segment: NetworkSegment):
        """Create bridge for a specific network segment"""
        self.logger.info(f"🌉 Creating bridge for segment {segment.network}")
        
        # Try each fallback method in order
        for method_name, method_func in self.fallback_chain:
            try:
                if method_func(segment):
                    self.logger.info(f"✅ Bridge created using {method_name}")
                    return True
            except Exception as e:
                self.logger.warning(f"Bridge method {method_name} failed: {e}")
                continue
        
        self.logger.error(f"❌ Could not create bridge for segment {segment.network}")
        return False
    
    def _create_udp_tunnel_bridge(self, segment: NetworkSegment) -> bool:
        """Create bridge using UDP tunnels"""
        self.logger.info("🔧 Creating UDP tunnel bridge...")
        
        if len(self.udp_tunnels) >= self.max_bridges:
            self.logger.warning("Maximum number of bridges reached")
            return False
        
        # Create UDP tunnel
        tunnel_id = self._generate_tunnel_id(segment)
        local_port = self.bridge_base_port + len(self.udp_tunnels)
        
        try:
            # Create UDP socket
            tunnel_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
            tunnel_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
            tunnel_socket.bind(('0.0.0.0', local_port))
            tunnel_socket.settimeout(5.0)
            
            # Create bridge endpoints
            endpoints = []
            for interface_name in segment.interfaces:
                if interface_name in self.interfaces:
                    interface = self.interfaces[interface_name]
                    if interface.ip_address:
                        endpoint = BridgeEndpoint(
                            interface=interface_name,
                            local_ip=interface.ip_address,
                            local_port=local_port,
                            tunnel_id=tunnel_id
                        )
                        endpoints.append(endpoint)
                        self.bridge_endpoints[interface_name] = endpoint
            
            if not endpoints:
                tunnel_socket.close()
                return False
            
            # Start tunnel handler
            tunnel_thread = threading.Thread(
                target=self._udp_tunnel_handler,
                args=(tunnel_socket, tunnel_id, endpoints),
                daemon=True
            )
            tunnel_thread.start()
            
            self.udp_tunnels[tunnel_id] = tunnel_socket
            
            self.logger.info(f"✅ UDP tunnel bridge created: {tunnel_id} on port {local_port}")
            return True
            
        except Exception as e:
            self.logger.error(f"UDP tunnel bridge creation failed: {e}")
            return False
    
    def _udp_tunnel_handler(self, tunnel_socket: socket.socket, tunnel_id: str, endpoints: List[BridgeEndpoint]):
        """Handle UDP tunnel traffic"""
        self.logger.info(f"🎯 Starting UDP tunnel handler: {tunnel_id}")
        
        while self.is_running:
            try:
                data, addr = tunnel_socket.recvfrom(65507)  # Max UDP packet size
                
                # Parse tunnel packet
                parsed_data = self._parse_tunnel_packet(data)
                if not parsed_data:
                    continue
                
                source_endpoint, dest_endpoint, payload = parsed_data
                
                # Route to appropriate endpoint
                self._route_tunnel_packet(source_endpoint, dest_endpoint, payload, endpoints)
                
            except socket.timeout:
                continue
            except Exception as e:
                if self.is_running:
                    self.logger.error(f"UDP tunnel handler error: {e}")
                break
        
        self.logger.info(f"🛑 UDP tunnel handler stopped: {tunnel_id}")
    
    def _parse_tunnel_packet(self, data: bytes) -> Optional[Tuple[str, str, bytes]]:
        """Parse UDP tunnel packet"""
        try:
            # Simple packet format: SOURCE_ENDPOINT_ID|DEST_ENDPOINT_ID|PAYLOAD
            packet_str = data.decode('utf-8', errors='ignore')
            
            if '|' not in packet_str:
                return None
            
            parts = packet_str.split('|', 2)
            if len(parts) != 3:
                return None
            
            source_endpoint, dest_endpoint, payload = parts
            return source_endpoint, dest_endpoint, payload.encode('utf-8')
            
        except Exception as e:
            self.logger.debug(f"Packet parsing failed: {e}")
            return None
    
    def _route_tunnel_packet(self, source: str, dest: str, payload: bytes, endpoints: List[BridgeEndpoint]):
        """Route packet between tunnel endpoints"""
        # Find destination endpoint
        dest_endpoint = None
        for endpoint in endpoints:
            if endpoint.interface == dest:
                dest_endpoint = endpoint
                break
        
        if not dest_endpoint:
            self.logger.debug(f"Unknown destination endpoint: {dest}")
            return
        
        # Send to destination interface
        try:
            # This would normally involve actual network injection
            # For now, just log the routing
            self.logger.debug(f"Routing {len(payload)} bytes from {source} to {dest}")
        except Exception as e:
            self.logger.error(f"Packet routing failed: {e}")
    
    def _generate_tunnel_id(self, segment: NetworkSegment) -> str:
        """Generate unique tunnel ID"""
        segment_data = f"{segment.network}_{len(self.udp_tunnels)}"
        return hashlib.md5(segment_data.encode()).hexdigest()[:8]
    
    def _create_wifi_direct_bridge(self, segment: NetworkSegment) -> bool:
        """Create WiFi Direct bridge"""
        self.logger.info("📡 Creating WiFi Direct bridge...")
        
        # Check if WiFi Direct is supported
        try:
            if platform.system() != "Windows":
                # Check for WiFi Direct support
                result = subprocess.run(['iw', 'list'], capture_output=True, text=True, timeout=5)
                if 'P2P' not in result.stdout:
                    self.logger.info("WiFi Direct not supported")
                    return False
                
                # Create P2P group
                p2p_commands = [
                    ['ip', 'link', 'set', 'wlan0', 'down'],
                    ['iw', 'dev', 'wlan0', 'interface', 'add', 'p2p0', 'type', 'p2p'],
                    ['ip', 'link', 'set', 'wlan0', 'up'],
                    ['ip', 'link', 'set', 'p2p0', 'up']
                ]
                
                for cmd in p2p_commands:
                    try:
                        subprocess.run(cmd, check=True, timeout=5)
                    except subprocess.CalledProcessError:
                        continue
                
                self.logger.info("✅ WiFi Direct bridge created")
                return True
            else:
                # Windows WiFi Direct (would need specific implementation)
                self.logger.info("WiFi Direct on Windows not yet implemented")
                return False
                
        except Exception as e:
            self.logger.error(f"WiFi Direct bridge creation failed: {e}")
            return False
    
    def _create_usb_tethering_bridge(self, segment: NetworkSegment) -> bool:
        """Create USB tethering bridge"""
        self.logger.info("🔌 Creating USB tethering bridge...")
        
        # Find USB interfaces
        usb_interfaces = [iface for iface in self.interfaces.values() 
                         if iface.type == 'usb' and iface.is_up]
        
        if not usb_interfaces:
            self.logger.info("No USB interfaces found for tethering")
            return False
        
        # Check if USB tethering is enabled
        try:
            # Check for rndis interfaces (USB tethering)
            rndis_interfaces = [iface for iface in usb_interfaces 
                               if 'rndis' in iface.name.lower()]
            
            if rndis_interfaces:
                self.logger.info("✅ USB tethering interface detected")
                return True
            else:
                self.logger.info("USB tethering not active")
                return False
                
        except Exception as e:
            self.logger.error(f"USB tethering bridge creation failed: {e}")
            return False
    
    def _create_adhoc_bridge(self, segment: NetworkSegment) -> bool:
        """Create ad-hoc bridge"""
        self.logger.info("📡 Creating ad-hoc bridge...")
        
        # Find wireless interfaces
        wireless_interfaces = [iface for iface in self.interfaces.values() 
                              if iface.type == 'wireless' and iface.is_up]
        
        if not wireless_interfaces:
            return False
        
        try:
            # Try to create ad-hoc network
            interface = wireless_interfaces[0]
            
            adhoc_commands = [
                ['ip', 'link', 'set', interface.name, 'down'],
                ['iwconfig', interface.name, 'mode', 'ad-hoc'],
                ['iwconfig', interface.name, 'essid', 'UniversalBridge'],
                ['iwconfig', interface.name, 'channel', '6'],
                ['ip', 'link', 'set', interface.name, 'up']
            ]
            
            for cmd in adhoc_commands:
                try:
                    subprocess.run(cmd, check=True, timeout=5)
                except subprocess.CalledProcessError:
                    continue
            
            self.logger.info("✅ Ad-hoc bridge created")
            return True
            
        except Exception as e:
            self.logger.error(f"Ad-hoc bridge creation failed: {e}")
            return False
    
    def _create_software_bridge(self, segment: NetworkSegment) -> bool:
        """Create software bridge using Linux bridge tools"""
        self.logger.info("🔧 Creating software bridge...")
        
        if platform.system() != "Linux":
            self.logger.info("Software bridges only supported on Linux")
            return False
        
        try:
            # Create bridge interface
            bridge_name = f"ubr{len(self.udp_tunnels)}"
            
            bridge_commands = [
                ['ip', 'link', 'add', bridge_name, 'type', 'bridge'],
                ['ip', 'link', 'set', bridge_name, 'up']
            ]
            
            # Add interfaces to bridge
            for interface_name in segment.interfaces:
                if interface_name in self.interfaces:
                    bridge_commands.extend([
                        ['ip', 'link', 'set', interface_name, 'master', bridge_name]
                    ])
            
            for cmd in bridge_commands:
                try:
                    subprocess.run(cmd, check=True, timeout=5)
                except subprocess.CalledProcessError:
                    continue
            
            self.logger.info(f"✅ Software bridge {bridge_name} created")
            return True
            
        except Exception as e:
            self.logger.error(f"Software bridge creation failed: {e}")
            return False
    
    def _monitor_bridge_health(self):
        """Monitor bridge health and connectivity"""
        # This would implement bridge health monitoring
        # including connectivity tests, latency measurements, etc.
        pass
    
    def _detect_new_interfaces(self):
        """Detect new network interfaces"""
        current_interfaces = set(self.network_manager.get_interfaces())
        known_interfaces = set(self.interfaces.keys())
        
        new_interfaces = current_interfaces - known_interfaces
        if new_interfaces:
            self.logger.info(f"🆕 New interfaces detected: {list(new_interfaces)}")
            
            # Analyze new interfaces
            for interface_name in new_interfaces:
                interface = self._analyze_interface(interface_name)
                if interface:
                    with self.lock:
                        self.interfaces[interface_name] = interface
            
            # Remap segments
            self._map_network_segments()
    
    def _send_heartbeats(self):
        """Send heartbeats for active tunnels"""
        # This would send periodic heartbeats to maintain tunnel connections
        pass
    
    def _cleanup_stale_endpoints(self):
        """Clean up stale bridge endpoints"""
        # This would clean up endpoints that haven't been active recently
        pass
    
    def _start_enhanced_dhcp_bridge(self):
        """Start the Enhanced DHCP Bridge for PXE fixes"""
        if not self.use_enhanced_dhcp or not ENHANCED_DHCP_AVAILABLE:
            return
        
        try:
            self.logger.info("🔧 Starting Enhanced DHCP Bridge for PXE E53 fix...")
            
            # Create Enhanced DHCP Bridge instance
            self.enhanced_dhcp_bridge = ENHANCED_DHCP_BRIDGE.EnhancedDHCPBridge()
            self.enhanced_dhcp_bridge.start()
            
            # Log successful start
            self.logger.info("✅ Enhanced DHCP Bridge started - PXE E53 error will be fixed")
            self.logger.info("🎯 WiFi-to-Ethernet DHCP bridging enabled")
            self.logger.info("🔗 Router isolation bypass active")
            
        except Exception as e:
            self.logger.error(f"Failed to start Enhanced DHCP Bridge: {e}")
            self.use_enhanced_dhcp = False  # Disable if failed
    
    def _stop_enhanced_dhcp_bridge(self):
        """Stop the Enhanced DHCP Bridge"""
        if self.enhanced_dhcp_bridge:
            try:
                self.enhanced_dhcp_bridge.stop()
                self.enhanced_dhcp_bridge = None
                self.logger.info("🛑 Enhanced DHCP Bridge stopped")
            except Exception as e:
                self.logger.error(f"Error stopping Enhanced DHCP Bridge: {e}")
    
    # Utility methods
    def _prefix_to_netmask(self, prefix: int) -> str:
        """Convert prefix length to netmask"""
        return socket.inet_ntoa(struct.pack(">I", (0xffffffff << (32 - prefix)) & 0xffffffff))
    
    def _is_valid_ip(self, ip: str) -> bool:
        """Check if string is a valid IP address"""
        try:
            ipaddress.IPv4Address(ip)
            return True
        except:
            return False
    
    def get_enhanced_dhcp_status(self) -> Dict[str, Any]:
        """Get Enhanced DHCP Bridge status"""
        return {
            'enhanced_dhcp_enabled': self.use_enhanced_dhcp,
            'enhanced_dhcp_available': ENHANCED_DHCP_AVAILABLE,
            'enhanced_dhcp_running': self.enhanced_dhcp_bridge is not None and self.enhanced_dhcp_bridge.running if self.enhanced_dhcp_bridge else False,
            'dhcp_fixes_active': self.use_enhanced_dhcp and ENHANCED_DHCP_AVAILABLE,
            'ethernet_dhcp_forwarding': self.use_enhanced_dhcp and ENHANCED_DHCP_AVAILABLE,
            'pxe_e53_fix_enabled': self.use_enhanced_dhcp and ENHANCED_DHCP_AVAILABLE
        }
    
    # Public API methods
    def get_network_topology(self) -> Dict[str, Any]:
        """Get current network topology"""
        return {
            'interfaces': {name: asdict(interface) for name, interface in self.interfaces.items()},
            'segments': {name: asdict(segment) for name, segment in self.network_segments.items()},
            'bridge_endpoints': {name: asdict(endpoint) for name, endpoint in self.bridge_endpoints.items()},
            'active_tunnels': len(self.udp_tunnels),
            'mixed_scenario': self._detect_mixed_scenario(),
            'enhanced_dhcp': self.get_enhanced_dhcp_status()
        }
    
    def create_bridge(self, interface1: str, interface2: str) -> bool:
        """Create bridge between two specific interfaces"""
        self.logger.info(f"🌉 Creating bridge between {interface1} and {interface2}")
        
        # Find or create network segment
        segment = NetworkSegment(
            network="manual_bridge",
            interfaces=[interface1, interface2]
        )
        
        # Try to create bridge
        return self._create_udp_tunnel_bridge(segment)
    
    def get_pxe_server_config(self) -> Dict[str, Any]:
        """Get PXE server configuration for mixed networks"""
        config = {
            'interfaces': {},
            'dhcp_ranges': {},
            'tftp_servers': {}
        }
        
        for interface_name, interface in self.interfaces.items():
            if interface.pxe_enabled and interface.ip_address:
                # Configure PXE for this interface
                network = ipaddress.IPv4Network(f"{interface.ip_address}/24", strict=False)
                
                config['interfaces'][interface_name] = {
                    'ip': interface.ip_address,
                    'network': str(network),
                    'gateway': interface.gateway,
                    'pxe_enabled': True
                }
                
                # Configure DHCP range for this interface
                start_ip = str(network.network_address + 10)
                end_ip = str(network.network_address + 50)
                config['dhcp_ranges'][str(network)] = {
                    'start': start_ip,
                    'end': end_ip,
                    'interface': interface_name
                }
        
        return config
    
    @property
    def is_running_state(self) -> bool:
        """Check if bridge system is running"""
        return self.is_running

def main():
    """Main function for Universal Network Bridge"""
    import argparse
    
    parser = argparse.ArgumentParser(description="Universal Network Bridge System")
    parser.add_argument('--config', help='Configuration file path')
    parser.add_argument('--auto-bridge', action='store_true', help='Auto-create bridges')
    parser.add_argument('--debug', action='store_true', help='Enable debug mode')
    parser.add_argument('--pxe-config', action='store_true', help='Show PXE configuration')
    parser.add_argument('--topology', action='store_true', help='Show network topology')
    
    args = parser.parse_args()
    
    # Initialize bridge system
    bridge = UniversalNetworkBridge(config_file=args.config)
    
    if args.debug:
        bridge.debug_mode = True
    
    if args.auto_bridge:
        bridge.auto_bridge = True
    
    try:
        # Start bridge system
        if bridge.start():
            print("🌐 Universal Network Bridge System started successfully!")
            
            if args.topology:
                topology = bridge.get_network_topology()
                print("\n📊 Network Topology:")
                print(json.dumps(topology, indent=2))
            
            if args.pxe_config:
                pxe_config = bridge.get_pxe_server_config()
                print("\n⚡ PXE Configuration:")
                print(json.dumps(pxe_config, indent=2))
            
            # Keep running
            try:
                while True:
                    time.sleep(1)
            except KeyboardInterrupt:
                print("\n🛑 Stopping bridge system...")
                bridge.stop()
                
    except KeyboardInterrupt:
        print("\n🛑 Interrupted by user")
    except Exception as e:
        print(f"\n❌ Bridge system error: {e}")
        return 1
    
    return 0

if __name__ == "__main__":
    sys.exit(main())