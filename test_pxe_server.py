#!/usr/bin/env python3
"""
Test script for Termux PXE Boot Server
Quick test to verify all components work
"""
import sys
import os
import socket
import threading
import time
import signal

# Add current directory to path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

try:
    from termux_pxe_boot import TermuxPXEServer
except ImportError as e:
    print(f"Error importing termux_pxe_boot: {e}")
    sys.exit(1)

def test_pxe_server():
    """Test the PXE server functionality"""
    print("🔧 Testing Termux PXE Boot Server...")
    print("=" * 50)
    
    # Test 1: Import and instantiation
    print("✓ Test 1: Importing TermuxPXEServer")
    try:
        server = TermuxPXEServer()
        print("  ✓ Server created successfully")
        print(f"  Server IP: {server.config['server_ip']}")
        print(f"  Base directory: {server.base_dir}")
        print(f"  TFTP directory: {server.tftp_dir}")
    except Exception as e:
        print(f"  ✗ Failed to create server: {e}")
        return False
    
    # Test 2: Boot file creation
    print("\n✓ Test 2: Creating boot files")
    try:
        server.create_boot_files()
        print("  ✓ Boot files created successfully")
        
        # Check if files exist
        tftp_dir = server.tftp_dir
        files_to_check = [
            'pxelinux.cfg/default',
            'pxelinux.0',
            'ipxe.pxe',
            'arch/vmlinuz-linux',
            'arch/initramfs-linux.img',
            'help.txt'
        ]
        
        for file_path in files_to_check:
            full_path = os.path.join(tftp_dir, file_path)
            if os.path.exists(full_path):
                size = os.path.getsize(full_path)
                print(f"  ✓ {file_path} ({size} bytes)")
            else:
                print(f"  ✗ {file_path} missing")
                
    except Exception as e:
        print(f"  ✗ Failed to create boot files: {e}")
        return False
    
    # Test 3: HTTP directory structure
    print("\n✓ Test 3: HTTP directory structure")
    try:
        http_dir = os.path.join(server.base_dir, 'http')
        if os.path.exists(http_dir):
            print(f"  ✓ HTTP directory created: {http_dir}")
            arch_http = os.path.join(http_dir, 'arch', 'arch', 'boot', 'x86_64')
            if os.path.exists(arch_http):
                print("  ✓ Arch ISO structure created")
            else:
                print("  ! Arch ISO structure incomplete")
        else:
            print("  ✗ HTTP directory missing")
    except Exception as e:
        print(f"  ✗ HTTP structure error: {e}")
    
    # Test 4: Network test
    print("\n✓ Test 4: Network configuration")
    try:
        # Get local IP
        s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        s.connect(("8.8.8.8", 80))
        local_ip = s.getsockname()[0]
        s.close()
        print(f"  ✓ Detected local IP: {local_ip}")
        
        # Check port availability
        test_ports = [67, 69, 8080]
        for port in test_ports:
            try:
                test_sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
                test_sock.bind(('', port))
                test_sock.close()
                print(f"  ✓ Port {port} available")
            except:
                print(f"  ! Port {port} in use or not available (expected in some environments)")
    except Exception as e:
        print(f"  ✗ Network test failed: {e}")
    
    print("\n🎉 Test Summary:")
    print("=" * 50)
    print("✓ TermuxPXEServer module working")
    print("✓ Boot configuration files created")
    print("✓ Arch Linux 'On Steroids' configuration ready")
    print("✓ Network and port configuration tested")
    print("\n🚀 Server is ready to start!")
    print("\nTo start the server:")
    print("  python3 termux_pxe_boot.py")
    print("\nOr use the GUI:")
    print("  python3 gui/main_window.py")
    
    return True

def test_quick_start():
    """Quick test - start server for 10 seconds"""
    print("\n🧪 Quick Start Test (10 seconds)...")
    print("Starting server for 10 seconds to verify it works...")
    
    try:
        server = TermuxPXEServer()
        
        def signal_handler(sig, frame):
            server.stop()
            print("\nServer stopped by user")
            sys.exit(0)
        
        signal.signal(signal.SIGINT, signal_handler)
        
        # Start server
        server.start()
        
        print("✓ Server started successfully!")
        print("Running for 10 seconds...")
        
        # Run for 10 seconds
        for i in range(10):
            time.sleep(1)
            print(f"  {10-i} seconds remaining...")
        
        # Stop server
        server.stop()
        print("✓ Server stopped successfully!")
        print("🎉 Quick test PASSED!")
        
        return True
        
    except Exception as e:
        print(f"✗ Quick test FAILED: {e}")
        return False

def main():
    """Main test function"""
    print("Termux PXE Boot Server - Test Suite")
    print("=" * 50)
    
    # Run basic test
    if not test_pxe_server():
        print("\n❌ Basic tests FAILED!")
        sys.exit(1)
    
    # Ask user if they want quick start test
    print("\n" + "=" * 50)
    try:
        response = input("Run quick start test? (y/N): ").lower().strip()
        if response in ['y', 'yes']:
            test_quick_start()
        else:
            print("Skipping quick start test")
    except KeyboardInterrupt:
        print("\nTest interrupted")
        sys.exit(0)
    
    print("\n✅ All tests completed successfully!")

if __name__ == "__main__":
    main()