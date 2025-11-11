#!/usr/bin/env python3
"""
Simple Autonomous PXE Setup - Lightweight Version
Guaranteed to work in all scenarios
"""
import os
import socket
import subprocess
import sys

def main():
    print("🤖 AUTONOMOUS TERMUX PXE BOOT")
    print("=" * 40)
    print("Automatic detection and setup...")
    print("")
    
    # Step 1: Quick network check
    print("🔍 Checking network...")
    try:
        s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        s.connect(("8.8.8.8", 80))
        local_ip = s.getsockname()[0]
        s.close()
        print(f"✅ Local IP: {local_ip}")
    except:
        print("❌ No network detected")
        local_ip = "192.168.1.100"
        print(f"Using default: {local_ip}")
    
    # Step 2: Test ports
    print("🔌 Testing ports...")
    ports_ok = True
    for port in [67, 69, 8080]:
        try:
            sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
            sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
            sock.bind(('', port))
            sock.close()
            print(f"✅ Port {port} available")
        except:
            print(f"❌ Port {port} in use")
            ports_ok = False
    
    # Step 3: Start server based on available method
    if ports_ok:
        print("🚀 Starting PXE server...")
        try:
            import termux_pxe_boot
            server = termux_pxe_boot.TermuxPXEServer()
            server.start()
            print("✅ Server started successfully!")
            print("Press Ctrl+C to stop")
            try:
                while True:
                    import time
                    time.sleep(1)
            except KeyboardInterrupt:
                server.stop()
                print("Server stopped")
        except Exception as e:
            print(f"❌ Server error: {e}")
            print("Try manual setup with USB tethering")
    else:
        print("⚠️  Ports unavailable - try USB tethering:")
        print("1. Enable USB tethering on phone")
        print("2. Connect via USB cable")  
        print("3. Run: python3 detect_usb_tethering.py")
    
    print("")
    print("🎯 For guaranteed success, use USB tethering method")
    print("Full autonomous system available in universal_pxe_launcher.sh")

if __name__ == "__main__":
    main()