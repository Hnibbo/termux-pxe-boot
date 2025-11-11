"""
Network utilities for Termux PXE Boot
High-performance network interface detection and management
Cross-platform compatible with steroid-level optimizations
"""
import subprocess
import socket
import os
import re
import threading
import time
import platform
from concurrent.futures import ThreadPoolExecutor

class NetworkManager:
    def __init__(self):
        self.interfaces = []
        self.interface_cache = {}
        self.performance_mode = True
        self._lock = threading.Lock()
        self._last_refresh = 0
        self._cache_ttl = 5  # 5 seconds cache
        
        # Performance optimization flags
        self.use_psutil = True
        self.prefer_ip_command = True
        self.async_refresh = True
        
        self.refresh_interfaces()
        
    def refresh_interfaces(self, force=False):
        """Refresh the list of available network interfaces with performance optimizations"""
        current_time = time.time()
        
        # Use cached results if not forced and cache is still valid
        if not force and (current_time - self._last_refresh) < self._cache_ttl and self.interfaces:
            return self.interfaces
            
        with self._lock:
            self.interfaces = []
            self.interface_cache = {}
            
            # High-performance interface detection methods
            if self.use_psutil:
                self._get_interfaces_psutil()
            else:
                self._get_interfaces_system()
                
            # Fallback interface methods for compatibility
            if not self.interfaces:
                self._get_interfaces_fallback()
                
            self._last_refresh = current_time
            return self.interfaces
            
    def _get_interfaces_psutil(self):
        """Get network interfaces using psutil (fastest method)"""
        try:
            import psutil
            if hasattr(psutil, 'net_if_addrs'):
                for interface, addrs in psutil.net_if_addrs().items():
                    if interface != 'lo':  # Skip loopback
                        # Get interface type and status
                        is_up = self._is_interface_up(interface)
                        if is_up or not self.performance_mode:  # Include all interfaces unless in strict performance mode
                            self.interfaces.append(interface)
                            # Cache interface information
                            self.interface_cache[interface] = {
                                'type': self._get_interface_type(interface),
                                'up': is_up,
                                'addresses': [addr.address for addr in addrs if addr.family == socket.AF_INET]
                            }
        except Exception as e:
            print(f"psutil interface detection failed: {e}")
            
    def _get_interfaces_system(self):
        """Get network interfaces using system commands (high performance)"""
        # Try multiple system methods in order of preference
        methods = [
            self._get_interfaces_ip_cmd,
            self._get_interfaces_sys_class,
            self._get_interfaces_proc_net
        ]
        
        for method in methods:
            try:
                result = method()
                if result:  # If method succeeded and found interfaces
                    self.interfaces = result
                    break
            except Exception as e:
                print(f"Interface detection method {method.__name__} failed: {e}")
                continue
                
    def _get_interfaces_ip_cmd(self):
        """Get interfaces using ip command (fastest system method)"""
        try:
            if platform.system() == "Windows":
                # Windows-specific command
                result = subprocess.run(['ipconfig', '/all'], 
                                      capture_output=True, text=True, timeout=3)
                interfaces = []
                
                for line in result.stdout.split('\n'):
                    line = line.strip()
                    if 'adapter' in line.lower() and ':' in line:
                        interface = line.split(':')[0].strip()
                        if '127.0.0.1' not in line:  # Skip localhost adapters
                            interfaces.append(interface)
                return interfaces
            else:
                # Unix/Linux/macOS method
                result = subprocess.run(['ip', 'link', 'show'], 
                                      capture_output=True, text=True, timeout=3)
                interfaces = []
                
                for line in result.stdout.split('\n'):
                    if ': ' in line and 'state ' in line:
                        interface = line.split(': ')[1].split('@')[0]
                        if interface != 'lo':
                            interfaces.append(interface)
                            
                return interfaces
        except (subprocess.TimeoutExpired, subprocess.SubprocessError) as e:
            print(f"ip command failed: {e}")
            return None
            
    def _get_interfaces_sys_class(self):
        """Get interfaces from /sys/class/net (Linux specific, very fast)"""
        if not os.path.exists('/sys/class/net'):
            return None
            
        try:
            interfaces = [iface for iface in os.listdir('/sys/class/net') 
                         if iface != 'lo' and os.path.isdir(f'/sys/class/net/{iface}')]
            return interfaces
        except Exception as e:
            print(f"/sys/class/net detection failed: {e}")
            return None
            
    def _get_interfaces_proc_net(self):
        """Get interfaces from /proc/net/dev (Linux specific)"""
        if not os.path.exists('/proc/net/dev'):
            return None
            
        try:
            with open('/proc/net/dev', 'r') as f:
                lines = f.readlines()
                
            interfaces = []
            for line in lines[2:]:  # Skip header lines
                if ':' in line:
                    interface = line.split(':')[0].strip()
                    if interface != 'lo':
                        interfaces.append(interface)
            return interfaces
        except Exception as e:
            print(f"/proc/net/dev detection failed: {e}")
            return None
            
    def _get_interfaces_fallback(self):
        """Fallback method for interface detection"""
        # Add common interface names for different platforms
        system = platform.system()
        if system == "Linux":
            if os.path.exists("/data/data/com.termux/files/home"):
                # Termux on Android
                self.interfaces = ['wlan0', 'eth0', 'tun0', 'usb0', 'p2p0']
            else:
                # Regular Linux
                self.interfaces = ['eth0', 'enp0s3', 'wlan0', 'wlp2s0', 'tun0']
        elif system == "Darwin":  # macOS
            self.interfaces = ['en0', 'en1', 'lo0', 'utun0']
        elif system == "Windows":
            self.interfaces = ['Ethernet', 'Wi-Fi', 'Loopback', 'Ethernet0', 'WiFi']
        else:
            # Generic fallback
            self.interfaces = ['eth0', 'wlan0']
            
    def _is_interface_up(self, interface):
        """Check if interface is up (using multiple methods)"""
        try:
            if platform.system() != "Windows":
                # Use ip command for Unix-like systems
                result = subprocess.run(['ip', 'link', 'show', interface], 
                                      capture_output=True, text=True, timeout=2)
                return 'state UP' in result.stdout or 'state UP' in result.stderr
            else:
                # Windows method
                result = subprocess.run(['ipconfig', '/all'], 
                                      capture_output=True, text=True, timeout=3)
                return interface in result.stdout and 'Media disconnected' not in result.stdout
        except Exception:
            return True  # Assume up if we can't check
            
    def _get_interface_type(self, interface):
        """Determine interface type (ethernet, wireless, etc.)"""
        try:
            if platform.system() != "Windows":
                # Check interface type via sysfs or ethtool
                if os.path.exists(f'/sys/class/net/{interface}/wireless'):
                    return 'wireless'
                else:
                    return 'ethernet'
            else:
                # Windows interface type detection
                if 'Wi-Fi' in interface or 'Wireless' in interface:
                    return 'wireless'
                elif 'Ethernet' in interface:
                    return 'ethernet'
                else:
                    return 'unknown'
        except Exception:
            return 'unknown'
            
    def get_interfaces(self):
        """Get list of available network interfaces (cached)"""
        return self.refresh_interfaces()
        
    def get_interface_ip(self, interface):
        """Get IP address for a specific interface with performance optimization"""
        # Check cache first
        if interface in self.interface_cache and self.interface_cache[interface].get('addresses'):
            return self.interface_cache[interface]['addresses'][0]
            
        # Fallback to direct detection
        try:
            if platform.system() == "Windows":
                # Windows method
                result = subprocess.run(['ipconfig', '/all'], 
                                      capture_output=True, text=True, timeout=3)
                lines = result.stdout.split('\n')
                
                for line in lines:
                    if interface in line:
                        # Look for IPv4 address in the next few lines
                        for i, next_line in enumerate(lines[lines.index(line):lines.index(line)+10]):
                            if 'IPv4 Address' in next_line or 'IP Address' in next_line:
                                ip = re.search(r'(\d+\.\d+\.\d+\.\d+)', next_line)
                                if ip:
                                    return ip.group(1)
            else:
                # Unix-like systems
                result = subprocess.run(['ip', 'addr', 'show', interface], 
                                      capture_output=True, text=True, timeout=3)
                for line in result.stdout.split('\n'):
                    if 'inet ' in line and 'scope global' in line and not '127.0.0.1' in line:
                        ip = line.strip().split()[1].split('/')[0]
                        return ip
        except Exception as e:
            print(f"Error getting IP for {interface}: {e}")
            
        return None
        
    def check_network_connectivity(self):
        """Check network connectivity with timeout and retry"""
        test_hosts = [
            ("8.8.8.8", 53),
            ("1.1.1.1", 53),
            ("google.com", 80)
        ]
        
        for host, port in test_hosts:
            try:
                socket.create_connection((host, port), timeout=2)
                return True
            except (OSError, socket.timeout):
                continue
                
        return False
        
    def get_best_interface(self):
        """Get the best interface for PXE server with performance analysis"""
        with ThreadPoolExecutor(max_workers=4) as executor:
            # Test all interfaces in parallel
            future_to_interface = {
                executor.submit(self._analyze_interface, interface): interface
                for interface in self.interfaces
            }
            
            interface_scores = []
            for future in future_to_interface:
                interface = future_to_interface[future]
                try:
                    score = future.result(timeout=1.0)
                    interface_scores.append((interface, score))
                except Exception:
                    # If analysis fails, give it a low score
                    interface_scores.append((interface, 0))
                    
        # Sort by score (higher is better)
        interface_scores.sort(key=lambda x: x[1], reverse=True)
        
        for interface, score in interface_scores:
            if score > 0:  # Only return interfaces that scored
                ip = self.get_interface_ip(interface)
                if ip:
                    return interface, ip
                    
        # Fallback to first available interface
        if self.interfaces:
            return self.interfaces[0], "192.168.1.100"
            
        return None, None
        
    def _analyze_interface(self, interface):
        """Analyze interface and return a performance score"""
        score = 0
        
        # Base score for being available
        score += 10
        
        # Get interface info from cache
        info = self.interface_cache.get(interface, {})
        
        # Bonus for being up
        if info.get('up', False):
            score += 20
            
        # Type bonuses
        interface_type = info.get('type', 'unknown')
        if interface_type == 'wireless':
            score += 15  # Wireless is common in modern setups
        elif interface_type == 'ethernet':
            score += 10
            
        # Check if interface has a valid IP
        if info.get('addresses'):
            score += 25
            
        return score
        
    def suggest_pxe_ip(self, interface):
        """Suggest a PXE server IP based on interface's network with optimization"""
        try:
            ip = self.get_interface_ip(interface)
            if ip:
                # Extract network portion and suggest .100
                parts = ip.split('.')
                if len(parts) == 4:
                    network = '.'.join(parts[:3])
                    return f"{network}.100"
        except Exception as e:
            print(f"Error suggesting PXE IP: {e}")
            
        return "192.168.1.100"
        
    def get_network_stats(self):
        """Get network statistics for performance monitoring"""
        stats = {
            'interfaces': len(self.interfaces),
            'active_interfaces': 0,
            'total_connections': 0,
            'bandwidth_usage': 0
        }
        
        if self.use_psutil:
            try:
                import psutil
                if hasattr(psutil, 'net_io_counters'):
                    net_io = psutil.net_io_counters()
                    stats['total_connections'] = len(psutil.net_connections())
                    stats['bandwidth_usage'] = (net_io.bytes_sent + net_io.bytes_recv) / (1024 * 1024)  # MB
            except Exception:
                pass
                
        # Count active interfaces
        for interface in self.interfaces:
            if self._is_interface_up(interface):
                stats['active_interfaces'] += 1
                
        return stats
        
    def optimize_for_performance(self):
        """Enable high-performance mode"""
        self.performance_mode = True
        self.use_psutil = True
        self.async_refresh = True
        
        # Reduce cache TTL for better responsiveness
        self._cache_ttl = 3
        
    def optimize_for_compatibility(self):
        """Enable compatibility mode"""
        self.performance_mode = False
        self.use_psutil = False
        self.async_refresh = False
        
        # Increase cache TTL for stability
        self._cache_ttl = 10
                # Windows-specific command
                result = subprocess.run(['ipconfig', '/all'], 
                                      capture_output=True, text=True, timeout=3)
                interfaces = []
                
                for line in result.stdout.split('\n'):
                    line = line.strip()
                    if 'adapter' in line.lower() and ':' in line:
                        interface = line.split(':')[0].strip()
                        if '127.0.0.1' not in line:  # Skip localhost adapters
                            interfaces.append(interface)
                return interfaces
            else:
                # Unix/Linux/macOS method
                result = subprocess.run(['ip', 'link', 'show'], 
                                      capture_output=True, text=True, timeout=3)
                interfaces = []
                
                for line in result.stdout.split('\n'):
                    if ': ' in line and 'state ' in line:
                        interface = line.split(': ')[1].split('@')[0]
                        if interface != 'lo':
                            interfaces.append(interface)
                            
                return interfaces
        except (subprocess.TimeoutExpired, subprocess.SubprocessError) as e:
            print(f"ip command failed: {e}")
            return None
            
    def _get_interfaces_sys_class(self):
        """Get interfaces from /sys/class/net (Linux specific, very fast)"""
        if not os.path.exists('/sys/class/net'):
            return None
            
        try:
            interfaces = [iface for iface in os.listdir('/sys/class/net') 
                         if iface != 'lo' and os.path.isdir(f'/sys/class/net/{iface}')]
            return interfaces
        except Exception as e:
            print(f"/sys/class/net detection failed: {e}")
            return None
            
    def _get_interfaces_proc_net(self):
        """Get interfaces from /proc/net/dev (Linux specific)"""
        if not os.path.exists('/proc/net/dev'):
            return None
            
        try:
            with open('/proc/net/dev', 'r') as f:
                lines = f.readlines()
                
            interfaces = []
            for line in lines[2:]:  # Skip header lines
                if ':' in line:
                    interface = line.split(':')[0].strip()
                    if interface != 'lo':
                        interfaces.append(interface)
            return interfaces
        except Exception as e:
            print(f"/proc/net/dev detection failed: {e}")
            return None
            
    def _get_interfaces_fallback(self):
        """Fallback method for interface detection"""
        # Add common interface names for different platforms
        system = platform.system()
        if system == "Linux":
            if os.path.exists("/data/data/com.termux/files/home"):
                # Termux on Android
                self.interfaces = ['wlan0', 'eth0', 'tun0', 'usb0', 'p2p0']
            else:
                # Regular Linux
                self.interfaces = ['eth0', 'enp0s3', 'wlan0', 'wlp2s0', 'tun0']
        elif system == "Darwin":  # macOS
            self.interfaces = ['en0', 'en1', 'lo0', 'utun0']
        elif system == "Windows":
            self.interfaces = ['Ethernet', 'Wi-Fi', 'Loopback', 'Ethernet0', 'WiFi']
        else:
            # Generic fallback
            self.interfaces = ['eth0', 'wlan0']
            
    def _is_interface_up(self, interface):
        """Check if interface is up (using multiple methods)"""
        try:
            if platform.system() != "Windows":
                # Use ip command for Unix-like systems
                result = subprocess.run(['ip', 'link', 'show', interface], 
                                      capture_output=True, text=True, timeout=2)
                return 'state UP' in result.stdout or 'state UP' in result.stderr
            else:
                # Windows method
                result = subprocess.run(['ipconfig', '/all'], 
                                      capture_output=True, text=True, timeout=3)
                return interface in result.stdout and 'Media disconnected' not in result.stdout
        except Exception:
            return True  # Assume up if we can't check
            
    def _get_interface_type(self, interface):
        """Determine interface type (ethernet, wireless, etc.)"""
        try:
            if platform.system() != "Windows":
                # Check interface type via sysfs or ethtool
                if os.path.exists(f'/sys/class/net/{interface}/wireless'):
                    return 'wireless'
                else:
                    return 'ethernet'
            else:
                # Windows interface type detection
                if 'Wi-Fi' in interface or 'Wireless' in interface:
                    return 'wireless'
                elif 'Ethernet' in interface:
                    return 'ethernet'
                else:
                    return 'unknown'
        except Exception:
            return 'unknown'
            
    def get_interfaces(self):
        """Get list of available network interfaces (cached)"""
        return self.refresh_interfaces()
        
    def get_interface_ip(self, interface):
        """Get IP address for a specific interface with performance optimization"""
        # Check cache first
        if interface in self.interface_cache and self.interface_cache[interface].get('addresses'):
            return self.interface_cache[interface]['addresses'][0]
            
        # Fallback to direct detection
        try:
            if platform.system() == "Windows":
                # Windows method
                result = subprocess.run(['ipconfig', '/all'], 
                                      capture_output=True, text=True, timeout=3)
                lines = result.stdout.split('\n')
                
                for line in lines:
                    if interface in line:
                        # Look for IPv4 address in the next few lines
                        for i, next_line in enumerate(lines[lines.index(line):lines.index(line)+10]):
                            if 'IPv4 Address' in next_line or 'IP Address' in next_line:
                                ip = re.search(r'(\d+\.\d+\.\d+\.\d+)', next_line)
                                if ip:
                                    return ip.group(1)
            else:
                # Unix-like systems
                result = subprocess.run(['ip', 'addr', 'show', interface], 
                                      capture_output=True, text=True, timeout=3)
                for line in result.stdout.split('\n'):
                    if 'inet ' in line and 'scope global' in line and not '127.0.0.1' in line:
                        ip = line.strip().split()[1].split('/')[0]
                        return ip
        except Exception as e:
            print(f"Error getting IP for {interface}: {e}")
            
        return None
        
    def check_network_connectivity(self):
        """Check network connectivity with timeout and retry"""
        test_hosts = [
            ("8.8.8.8", 53),
            ("1.1.1.1", 53),
            ("google.com", 80)
        ]
        
        for host, port in test_hosts:
            try:
                socket.create_connection((host, port), timeout=2)
                return True
            except (OSError, socket.timeout):
                continue
                
        return False
        
    def get_best_interface(self):
        """Get the best interface for PXE server with performance analysis"""
        with ThreadPoolExecutor(max_workers=4) as executor:
            # Test all interfaces in parallel
            future_to_interface = {
                executor.submit(self._analyze_interface, interface): interface
                for interface in self.interfaces
            }
            
            interface_scores = []
            for future in future_to_interface:
                interface = future_to_interface[future]
                try:
                    score = future.result(timeout=1.0)
                    interface_scores.append((interface, score))
                except Exception:
                    # If analysis fails, give it a low score
                    interface_scores.append((interface, 0))
                    
        # Sort by score (higher is better)
        interface_scores.sort(key=lambda x: x[1], reverse=True)
        
        for interface, score in interface_scores:
            if score > 0:  # Only return interfaces that scored
                ip = self.get_interface_ip(interface)
                if ip:
                    return interface, ip
                    
        # Fallback to first available interface
        if self.interfaces:
            return self.interfaces[0], "192.168.1.100"
            
        return None, None
        
    def _analyze_interface(self, interface):
        """Analyze interface and return a performance score"""
        score = 0
        
        # Base score for being available
        score += 10
        
        # Get interface info from cache
        info = self.interface_cache.get(interface, {})
        
        # Bonus for being up
        if info.get('up', False):
            score += 20
            
        # Type bonuses
        interface_type = info.get('type', 'unknown')
        if interface_type == 'wireless':
            score += 15  # Wireless is common in modern setups
        elif interface_type == 'ethernet':
            score += 10
            
        # Check if interface has a valid IP
        if info.get('addresses'):
            score += 25
            
        return score
        
    def suggest_pxe_ip(self, interface):
        """Suggest a PXE server IP based on interface's network with optimization"""
        try:
            ip = self.get_interface_ip(interface)
            if ip:
                # Extract network portion and suggest .100
                parts = ip.split('.')
                if len(parts) == 4:
                    network = '.'.join(parts[:3])
                    return f"{network}.100"
        except Exception as e:
            print(f"Error suggesting PXE IP: {e}")
            
        return "192.168.1.100"
        
    def get_network_stats(self):
        """Get network statistics for performance monitoring"""
        stats = {
            'interfaces': len(self.interfaces),
            'active_interfaces': 0,
            'total_connections': 0,
            'bandwidth_usage': 0
        }
        
        if self.use_psutil:
            try:
                import psutil
                if hasattr(psutil, 'net_io_counters'):
                    net_io = psutil.net_io_counters()
                    stats['total_connections'] = len(psutil.net_connections())
                    stats['bandwidth_usage'] = (net_io.bytes_sent + net_io.bytes_recv) / (1024 * 1024)  # MB
            except Exception:
                pass
                
        # Count active interfaces
        for interface in self.interfaces:
            if self._is_interface_up(interface):
                stats['active_interfaces'] += 1
                
        return stats
        
    def optimize_for_performance(self):
        """Enable high-performance mode"""
        self.performance_mode = True
        self.use_psutil = True
        self.async_refresh = True
        
        # Reduce cache TTL for better responsiveness
        self._cache_ttl = 3
        
    def optimize_for_compatibility(self):
        """Enable compatibility mode"""
        self.performance_mode = False
        self.use_psutil = False
        self.async_refresh = False
        
        # Increase cache TTL for stability
        self._cache_ttl = 10
                # Windows-specific command
                result = subprocess.run(['ipconfig', '/all'], 
                                      capture_output=True, text=True, timeout=3)
                interfaces = []
                
                for line in result.stdout.split('\n'):
                    line = line.strip()
                    if 'adapter' in line.lower() and ':' in line:
                        interface = line.split(':')[0].strip()
                        if '127.0.0.1' not in line:  # Skip localhost adapters
                            interfaces.append(interface)
                return interfaces
            else:
                # Unix/Linux/macOS method
                result = subprocess.run(['ip', 'link', 'show'], 
                                      capture_output=True, text=True, timeout=3)
                interfaces = []
                
                for line in result.stdout.split('\n'):
                    if ': ' in line and 'state ' in line:
                        interface = line.split(': ')[1].split('@')[0]
                        if interface != 'lo':
                            interfaces.append(interface)
                            
                return interfaces
        except (subprocess.TimeoutExpired, subprocess.SubprocessError) as e:
            print(f"ip command failed: {e}")
            return None
            
    def _get_interfaces_sys_class(self):
        """Get interfaces from /sys/class/net (Linux specific, very fast)"""
        if not os.path.exists('/sys/class/net'):
            return None
            
        try:
            interfaces = [iface for iface in os.listdir('/sys/class/net') 
                         if iface != 'lo' and os.path.isdir(f'/sys/class/net/{iface}')]
            return interfaces
        except Exception as e:
            print(f"/sys/class/net detection failed: {e}")
            return None
            
    def _get_interfaces_proc_net(self):
        """Get interfaces from /proc/net/dev (Linux specific)"""
        if not os.path.exists('/proc/net/dev'):
            return None
            
        try:
            with open('/proc/net/dev', 'r') as f:
                lines = f.readlines()
                
            interfaces = []
            for line in lines[2:]:  # Skip header lines
                if ':' in line:
                    interface = line.split(':')[0].strip()
                    if interface != 'lo':
                        interfaces.append(interface)
            return interfaces
        except Exception as e:
            print(f"/proc/net/dev detection failed: {e}")
            return None
            
    def _get_interfaces_fallback(self):
        """Fallback method for interface detection"""
        # Add common interface names for different platforms
        system = platform.system()
        if system == "Linux":
            if os.path.exists("/data/data/com.termux/files/home"):
                # Termux on Android
                self.interfaces = ['wlan0', 'eth0', 'tun0', 'usb0', 'p2p0']
            else:
                # Regular Linux
                self.interfaces = ['eth0', 'enp0s3', 'wlan0', 'wlp2s0', 'tun0']
        elif system == "Darwin":  # macOS
            self.interfaces = ['en0', 'en1', 'lo0', 'utun0']
        elif system == "Windows":
            self.interfaces = ['Ethernet', 'Wi-Fi', 'Loopback', 'Ethernet0', 'WiFi']
        else:
            # Generic fallback
            self.interfaces = ['eth0', 'wlan0']
            
    def _is_interface_up(self, interface):
        """Check if interface is up (using multiple methods)"""
        try:
            if platform.system() != "Windows":
                # Use ip command for Unix-like systems
                result = subprocess.run(['ip', 'link', 'show', interface], 
                                      capture_output=True, text=True, timeout=2)
                return 'state UP' in result.stdout or 'state UP' in result.stderr
            else:
                # Windows method
                result = subprocess.run(['ipconfig', '/all'], 
                                      capture_output=True, text=True, timeout=3)
                return interface in result.stdout and 'Media disconnected' not in result.stdout
        except Exception:
            return True  # Assume up if we can't check
            
    def _get_interface_type(self, interface):
        """Determine interface type (ethernet, wireless, etc.)"""
        try:
            if platform.system() != "Windows":
                # Check interface type via sysfs or ethtool
                if os.path.exists(f'/sys/class/net/{interface}/wireless'):
                    return 'wireless'
                else:
                    return 'ethernet'
            else:
                # Windows interface type detection
                if 'Wi-Fi' in interface or 'Wireless' in interface:
                    return 'wireless'
                elif 'Ethernet' in interface:
                    return 'ethernet'
                else:
                    return 'unknown'
        except Exception:
            return 'unknown'
            
    def get_interfaces(self):
        """Get list of available network interfaces (cached)"""
        return self.refresh_interfaces()
        
    def get_interface_ip(self, interface):
        """Get IP address for a specific interface with performance optimization"""
        # Check cache first
        if interface in self.interface_cache and self.interface_cache[interface].get('addresses'):
            return self.interface_cache[interface]['addresses'][0]
            
        # Fallback to direct detection
        try:
            if platform.system() == "Windows":
                # Windows method
                result = subprocess.run(['ipconfig', '/all'], 
                                      capture_output=True, text=True, timeout=3)
                lines = result.stdout.split('\n')
                
                for line in lines:
                    if interface in line:
                        # Look for IPv4 address in the next few lines
                        for i, next_line in enumerate(lines[lines.index(line):lines.index(line)+10]):
                            if 'IPv4 Address' in next_line or 'IP Address' in next_line:
                                ip = re.search(r'(\d+\.\d+\.\d+\.\d+)', next_line)
                                if ip:
                                    return ip.group(1)
            else:
                # Unix-like systems
                result = subprocess.run(['ip', 'addr', 'show', interface], 
                                      capture_output=True, text=True, timeout=3)
                for line in result.stdout.split('\n'):
                    if 'inet ' in line and 'scope global' in line and not '127.0.0.1' in line:
                        ip = line.strip().split()[1].split('/')[0]
                        return ip
        except Exception as e:
            print(f"Error getting IP for {interface}: {e}")
            
        return None
        
    def check_network_connectivity(self):
        """Check network connectivity with timeout and retry"""
        test_hosts = [
            ("8.8.8.8", 53),
            ("1.1.1.1", 53),
            ("google.com", 80)
        ]
        
        for host, port in test_hosts:
            try:
                socket.create_connection((host, port), timeout=2)
                return True
            except (OSError, socket.timeout):
                continue
                
        return False
        
    def get_best_interface(self):
        """Get the best interface for PXE server with performance analysis"""
        with ThreadPoolExecutor(max_workers=4) as executor:
            # Test all interfaces in parallel
            future_to_interface = {
                executor.submit(self._analyze_interface, interface): interface
                for interface in self.interfaces
            }
            
            interface_scores = []
            for future in future_to_interface:
                interface = future_to_interface[future]
                try:
                    score = future.result(timeout=1.0)
                    interface_scores.append((interface, score))
                except Exception:
                    # If analysis fails, give it a low score
                    interface_scores.append((interface, 0))
                    
        # Sort by score (higher is better)
        interface_scores.sort(key=lambda x: x[1], reverse=True)
        
        for interface, score in interface_scores:
            if score > 0:  # Only return interfaces that scored
                ip = self.get_interface_ip(interface)
                if ip:
                    return interface, ip
                    
        # Fallback to first available interface
        if self.interfaces:
            return self.interfaces[0], "192.168.1.100"
            
        return None, None
        
    def _analyze_interface(self, interface):
        """Analyze interface and return a performance score"""
        score = 0
        
        # Base score for being available
        score += 10
        
        # Get interface info from cache
        info = self.interface_cache.get(interface, {})
        
        # Bonus for being up
        if info.get('up', False):
            score += 20
            
        # Type bonuses
        interface_type = info.get('type', 'unknown')
        if interface_type == 'wireless':
            score += 15  # Wireless is common in modern setups
        elif interface_type == 'ethernet':
            score += 10
            
        # Check if interface has a valid IP
        if info.get('addresses'):
            score += 25
            
        return score
        
    def suggest_pxe_ip(self, interface):
        """Suggest a PXE server IP based on interface's network with optimization"""
        try:
            ip = self.get_interface_ip(interface)
            if ip:
                # Extract network portion and suggest .100
                parts = ip.split('.')
                if len(parts) == 4:
                    network = '.'.join(parts[:3])
                    return f"{network}.100"
        except Exception as e:
            print(f"Error suggesting PXE IP: {e}")
            
        return "192.168.1.100"
        
    def get_network_stats(self):
        """Get network statistics for performance monitoring"""
        stats = {
            'interfaces': len(self.interfaces),
            'active_interfaces': 0,
            'total_connections': 0,
            'bandwidth_usage': 0
        }
        
        if self.use_psutil:
            try:
                import psutil
                if hasattr(psutil, 'net_io_counters'):
                    net_io = psutil.net_io_counters()
                    stats['total_connections'] = len(psutil.net_connections())
                    stats['bandwidth_usage'] = (net_io.bytes_sent + net_io.bytes_recv) / (1024 * 1024)  # MB
            except Exception:
                pass
                
        # Count active interfaces
        for interface in self.interfaces:
            if self._is_interface_up(interface):
                stats['active_interfaces'] += 1
                
        return stats
        
    def optimize_for_performance(self):
        """Enable high-performance mode"""
        self.performance_mode = True
        self.use_psutil = True
        self.async_refresh = True
        
        # Reduce cache TTL for better responsiveness
        self._cache_ttl = 3
        
    def optimize_for_compatibility(self):
        """Enable compatibility mode"""
        self.performance_mode = False
        self.use_psutil = False
        self.async_refresh = False
        
        # Increase cache TTL for stability
        self._cache_ttl = 10
                result = subprocess.run(['ipconfig', '/all'], 
                                      capture_output=True, text=True, timeout=3)
                interfaces = []
                current_adapter = None
                
                for line in result.stdout.split('\n'):
                    line = line.strip()
                    if 'adapter' in line.lower() and ':' in line:
                        current_adapter = line.split(':')[0].strip()
                        if '127.0.0.1' not in line:  # Skip localhost adapters
                            interfaces.append(current_adapter)
            else:
                # Unix/Linux/macOS method
                result = subprocess.run(['ip', 'link', 'show'], 
                                      capture_output=True, text=True, timeout=3)
                interfaces = []
                
                for line in result.stdout.split('\n'):
                    if ': ' in line and 'state ' in line:
                        interface = line.split(': ')[1].split('@')[0]
                        if interface != 'lo':
                            interfaces.append(interface)
                            
            return interfaces
        except (subprocess.TimeoutExpired, subprocess.SubprocessError) as e:
            print(f"ip command failed: {e}")
            return None
            
    def _get_interfaces_sys_class(self):
        """Get interfaces from /sys/class/net (Linux specific, very fast)"""
        if not os.path.exists('/sys/class/net'):
            return None
            
        try:
            interfaces = [iface for iface in os.listdir('/sys/class/net') 
                         if iface != 'lo' and os.path.isdir(f'/sys/class/net/{iface}')]
            return interfaces
        except Exception as e:
            print(f"/sys/class/net detection failed: {e}")
            return None
            
    def _get_interfaces_proc_net(self):
        """Get interfaces from /proc/net/dev (Linux specific)"""
        if not os.path.exists('/proc/net/dev'):
            return None
            
        try:
            with open('/proc/net/dev', 'r') as f:
                lines = f.readlines()
                
            interfaces = []
            for line in lines[2:]:  # Skip header lines
                if ':' in line:
                    interface = line.split(':')[0].strip()
                    if interface != 'lo':
                        interfaces.append(interface)
            return interfaces
        except Exception as e:
            print(f"/proc/net/dev detection failed: {e}")
            return None
            
    def _get_interfaces_fallback(self):
        """Fallback method for interface detection"""
        # Add common interface names for different platforms
        system = platform.system()
        if system == "Linux":
            if os.path.exists("/data/data/com.termux/files/home"):
                # Termux on Android
                self.interfaces = ['wlan0', 'eth0', 'tun0', 'usb0', 'p2p0']
            else:
                # Regular Linux
                self.interfaces = ['eth0', 'enp0s3', 'wlan0', 'wlp2s0', 'tun0', 'lo']
        elif system == "Darwin":  # macOS
            self.interfaces = ['en0', 'en1', 'lo0', 'utun0']
        elif system == "Windows":
            self.interfaces = ['Ethernet', 'Wi-Fi', 'Loopback', 'Ethernet0', 'WiFi']
        else:
            # Generic fallback
            self.interfaces = ['eth0', 'wlan0', 'lo']
            
    def _is_interface_up(self, interface):
        """Check if interface is up (using multiple methods)"""
        try:
            if platform.system() != "Windows":
                # Use ip command for Unix-like systems
                result = subprocess.run(['ip', 'link', 'show', interface], 
                                      capture_output=True, text=True, timeout=2)
                return 'state UP' in result.stdout or 'state UP' in result.stderr
            else:
                # Windows method
                result = subprocess.run(['ipconfig', '/all'], 
                                      capture_output=True, text=True, timeout=3)
                return interface in result.stdout and 'Media disconnected' not in result.stdout
        except Exception:
            return True  # Assume up if we can't check
            
    def _get_interface_type(self, interface):
        """Determine interface type (ethernet, wireless, etc.)"""
        try:
            if platform.system() != "Windows":
                # Check interface type via sysfs or ethtool
                if os.path.exists(f'/sys/class/net/{interface}/wireless'):
                    return 'wireless'
                else:
                    return 'ethernet'
            else:
                # Windows interface type detection
                if 'Wi-Fi' in interface or 'Wireless' in interface:
                    return 'wireless'
                elif 'Ethernet' in interface:
                    return 'ethernet'
                else:
                    return 'unknown'
        except Exception:
            return 'unknown'
            
    def get_interfaces(self):
        """Get list of available network interfaces (cached)"""
        return self.refresh_interfaces()
        
    def get_interface_ip(self, interface):
        """Get IP address for a specific interface with performance optimization"""
        # Check cache first
        if interface in self.interface_cache and self.interface_cache[interface].get('addresses'):
            return self.interface_cache[interface]['addresses'][0]
            
        # Fallback to direct detection
        try:
            if platform.system() == "Windows":
                # Windows method
                result = subprocess.run(['ipconfig', '/all'], 
                                      capture_output=True, text=True, timeout=3)
                lines = result.stdout.split('\n')
                in_adapter = False
                
                for line in lines:
                    if interface in line:
                        in_adapter = True
                        continue
                    if in_adapter and 'IPv4 Address' in line:
                        ip = re.search(r'(\d+\.\d+\.\d+\.\d+)', line)
                        if ip:
                            return ip.group(1)
            else:
                # Unix-like systems
                result = subprocess.run(['ip', 'addr', 'show', interface], 
                                      capture_output=True, text=True, timeout=3)
                for line in result.stdout.split('\n'):
                    if 'inet ' in line and 'scope global' in line and not '127.0.0.1' in line:
                        ip = line.strip().split()[1].split('/')[0]
                        return ip
        except Exception as e:
            print(f"Error getting IP for {interface}: {e}")
            
        return None
        
    def check_network_connectivity(self):
        """Check network connectivity with timeout and retry"""
        test_hosts = [
            ("8.8.8.8", 53),
            ("1.1.1.1", 53),
            ("google.com", 80)
        ]
        
        for host, port in test_hosts:
            try:
                socket.create_connection((host, port), timeout=2)
                return True
            except (OSError, socket.timeout):
                continue
                
        return False
        
    def get_best_interface(self):
        """Get the best interface for PXE server with performance analysis"""
        with ThreadPoolExecutor(max_workers=4) as executor:
            # Test all interfaces in parallel
            future_to_interface = {
                executor.submit(self._analyze_interface, interface): interface
                for interface in self.interfaces
            }
            
            interface_scores = []
            for future in future_to_interface:
                interface = future_to_interface[future]
                try:
                    score = future.result(timeout=1.0)
                    interface_scores.append((interface, score))
                except Exception:
                    # If analysis fails, give it a low score
                    interface_scores.append((interface, 0))
                    
        # Sort by score (higher is better)
        interface_scores.sort(key=lambda x: x[1], reverse=True)
        
        for interface, score in interface_scores:
            if score > 0:  # Only return interfaces that scored
                ip = self.get_interface_ip(interface)
                if ip:
                    return interface, ip
                    
        # Fallback to first available interface
        if self.interfaces:
            return self.interfaces[0], "192.168.1.100"
            
        return None, None
        
    def _analyze_interface(self, interface):
        """Analyze interface and return a performance score"""
        score = 0
        
        # Base score for being available
        score += 10
        
        # Get interface info from cache
        info = self.interface_cache.get(interface, {})
        
        # Bonus for being up
        if info.get('up', False):
            score += 20
            
        # Type bonuses
        interface_type = info.get('type', 'unknown')
        if interface_type == 'wireless':
            score += 15  # Wireless is common in modern setups
        elif interface_type == 'ethernet':
            score += 10
            
        # Check if interface has a valid IP
        if info.get('addresses'):
            score += 25
            
        return score
        
    def suggest_pxe_ip(self, interface):
        """Suggest a PXE server IP based on interface's network with optimization"""
        try:
            ip = self.get_interface_ip(interface)
            if ip:
                # Extract network portion and suggest .100
                parts = ip.split('.')
                if len(parts) == 4:
                    network = '.'.join(parts[:3])
                    return f"{network}.100"
        except Exception as e:
            print(f"Error suggesting PXE IP: {e}")
            
        return "192.168.1.100"
        
    def get_network_stats(self):
        """Get network statistics for performance monitoring"""
        stats = {
            'interfaces': len(self.interfaces),
            'active_interfaces': 0,
            'total_connections': 0,
            'bandwidth_usage': 0
        }
        
        if self.use_psutil and hasattr(psutil, 'net_io_counters'):
            try:
                net_io = psutil.net_io_counters()
                stats['total_connections'] = len(psutil.net_connections())
                stats['bandwidth_usage'] = (net_io.bytes_sent + net_io.bytes_recv) / (1024 * 1024)  # MB
            except Exception:
                pass
                
        # Count active interfaces
        for interface in self.interfaces:
            if self._is_interface_up(interface):
                stats['active_interfaces'] += 1
                
        return stats
        
    def optimize_for_performance(self):
        """Enable high-performance mode"""
        self.performance_mode = True
        self.use_psutil = True
        self.async_refresh = True
        
        # Reduce cache TTL for better responsiveness
        self._cache_ttl = 3
        
    def optimize_for_compatibility(self):
        """Enable compatibility mode"""
        self.performance_mode = False
        self.use_psutil = False
        self.async_refresh = False
        
        # Increase cache TTL for stability
        self._cache_ttl = 10
