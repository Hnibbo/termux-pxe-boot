#!/usr/bin/env python3
"""
Network Diagnostic Tool for Termux PXE Boot
Helps identify and fix network connectivity issues
"""
import socket
import subprocess
import os
import sys
import json
from pathlib import Path

def get_network_info():
    """Get detailed network information"""
    network_info = {
        'interfaces': [],
        'routing_table': [],
        'dns_servers': [],
        'external_ip': None,
        'local_subnets': []
    }
    
    try:
        # Get network interfaces
        result = subprocess.run(['ip', 'addr', 'show'], capture_output=True, text=True)
        if result.returncode == 0:
            lines = result.stdout.split('\n')
            for line in lines:
                if 'inet ' in line and '127.0.0.1' not in line:
                    parts = line.strip().split()
                    if len(parts) >= 2:
                        ip_info = parts[1]
                        interface = parts[-1]
                        if ip_info not in network_info['local_subnets']:
                            network_info['local_subnets'].append(ip_info)
                            network_info['interfaces'].append({
                                'interface': interface,
                                'ip': ip_info
                            })
    except:
        pass
    
    try:
        # Get routing table
        result = subprocess.run(['ip', 'route', 'show'], capture_output=True, text=True)
        if result.returncode == 0:
            network_info['routing_table'] = result.stdout.strip().split('\n')
    except:
        pass
    
    try:
        # Get external IP
        s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        s.connect(("8.8.8.8", 80))
        network_info['external_ip'] = s.getsockname()[0]
        s.close()
    except:
        pass
    
    return network_info

def check_connectivity_to_subnets(network_info):
    """Test connectivity to common subnets"""
    test_ips = ['192.168.1.1', '192.168.0.1', '10.0.0.1', '192.168.1.100']
    reachable = []
    
    for ip in test_ips:
        try:
            result = subprocess.run(['ping', '-c', '1', '-W', '1', ip], 
                                  capture_output=True, text=True, timeout=2)
            if result.returncode == 0:
                reachable.append(ip)
        except:
            pass
    
    return reachable

def test_pxe_ports():
    """Test if PXE server ports are accessible"""
    test_results = {}
    ports_to_test = [67, 69, 8080]
    
    for port in ports_to_test:
        try:
            sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
            sock.settimeout(1)
            sock.bind(('', port))
            sock.close()
            test_results[port] = "Available"
        except:
            test_results[port] = "In Use or Blocked"
    
    return test_results

def check_router_arp():
    """Check ARP table for router discovery"""
    try:
        result = subprocess.run(['ip', 'neigh'], capture_output=True, text=True)
        if result.returncode == 0:
            neighbors = []
            for line in result.stdout.split('\n'):
                if 'REACHABLE' in line or 'STALE' in line:
                    parts = line.split()
                    if len(parts) >= 5:
                        ip = parts[0]
                        mac = parts[4]
                        neighbors.append({'ip': ip, 'mac': mac})
            return neighbors
    except:
        pass
    return []

def suggest_solutions(network_info, reachable_ips, port_status, arp_neighbors):
    """Generate solution suggestions"""
    solutions = []
    
    # Check if on same subnet
    local_ips = [info['ip'].split('/')[0] for info in network_info['interfaces']]
    
    if len(local_ips) > 1:
        solutions.append("⚠️ MULTIPLE NETWORK INTERFACES DETECTED")
        for ip in local_ips:
            solutions.append(f"   Interface: {ip}")
        solutions.append("   This can cause connectivity issues")
    
    # Check subnet reachability
    if not reachable_ips:
        solutions.append("❌ NO ROUTER CONNECTIVITY")
        solutions.append("   Your devices may be on isolated network segments")
        solutions.append("   Try: Switch PC to 2.4G WiFi OR use WiFi bridge")
    else:
        solutions.append("✅ ROUTER CONNECTIVITY OK")
        for ip in reachable_ips:
            solutions.append(f"   Reachable: {ip}")
    
    # Port availability
    solutions.append("🔌 PXE SERVER PORTS:")
    for port, status in port_status.items():
        solutions.append(f"   Port {port}: {status}")
    
    # ARP table
    if arp_neighbors:
        solutions.append("🖧 ARP NEIGHBORS:")
        for neighbor in arp_neighbors[:5]:  # Show first 5
            solutions.append(f"   {neighbor['ip']} -> {neighbor['mac']}")
    
    return solutions

def main():
    """Main diagnostic function"""
    print("🔍 TERMUX PXE BOOT - NETWORK DIAGNOSTIC")
    print("=" * 50)
    
    # Get network information
    print("📡 Analyzing network configuration...")
    network_info = get_network_info()
    
    # Test connectivity
    print("🌐 Testing router connectivity...")
    reachable_ips = check_connectivity_to_subnets(network_info)
    
    # Test ports
    print("🔌 Testing PXE server ports...")
    port_status = test_pxe_ports()
    
    # Check ARP table
    print("🖧 Scanning ARP table...")
    arp_neighbors = check_router_arp()
    
    # Generate report
    print("\n" + "=" * 50)
    print("📋 DIAGNOSTIC REPORT")
    print("=" * 50)
    
    print("🖧 INTERFACES:")
    for interface in network_info['interfaces']:
        print(f"   {interface['interface']}: {interface['ip']}")
    
    if network_info['external_ip']:
        print(f"   External IP: {network_info['external_ip']}")
    
    print("\n🔧 SOLUTIONS:")
    solutions = suggest_solutions(network_info, reachable_ips, port_status, arp_neighbors)
    for solution in solutions:
        print(solution)
    
    print("\n🚀 QUICK FIXES:")
    print("1. 📱 Connect both PC AND phone to SAME WiFi network (2.4G or 5G)")
    print("2. 🖧 Use ethernet cable to connect phone to router (if available)")
    print("3. 🔄 Restart router after changing network settings")
    print("4. 📡 Check router admin panel for client isolation settings")
    print("5. ⚙️ Disable AP isolation / Client isolation on router")
    
    # Save detailed report
    report_file = "network_diagnostic_report.json"
    with open(report_file, 'w') as f:
        json.dump({
            'network_info': network_info,
            'reachable_ips': reachable_ips,
            'port_status': port_status,
            'arp_neighbors': arp_neighbors
        }, f, indent=2)
    
    print(f"\n💾 Detailed report saved to: {report_file}")

if __name__ == "__main__":
    main()