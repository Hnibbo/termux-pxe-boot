"""
Main GUI Window for Termux PXE Boot
Integrated with working termux_pxe_boot.py
"""
import tkinter as tk
from tkinter import ttk, messagebox, scrolledtext
import threading
import os
import sys
import time
from datetime import datetime
from pathlib import Path

# Add parent directory to Python path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# Import the working PXE server
try:
    from termux_pxe_boot import TermuxPXEServer
    PXE_AVAILABLE = True
except ImportError as e:
    print(f"Warning: Could not import termux_pxe_boot: {e}")
    PXE_AVAILABLE = False

class PXEGUI:
    def __init__(self):
        self.root = tk.Tk()
        self.root.title("Termux PXE Boot Server - Steroid Edition")
        self.root.geometry("900x700")
        self.root.configure(bg='#0a0a0a')
        
        # Server instance
        self.pxe_server = None
        self.server_running = False
        
        # Server logs
        self.log_buffer = deque(maxlen=1000)
        
        # Create GUI
        self.setup_styles()
        self.create_interface()
        self.center_window()
        
        # Start background tasks
        self.update_server_status()
        
    def setup_styles(self):
        """Setup dark theme styling"""
        self.colors = {
            'bg': '#0a0a0a',
            'fg': '#00ff00',
            'secondary': '#1a1a1a',
            'accent': '#00aa00',
            'warning': '#ffaa00',
            'error': '#ff4444',
            'success': '#00ff88'
        }
        
        # Configure root
        self.root.configure(bg=self.colors['bg'])
        
    def create_interface(self):
        """Create the main interface"""
        # Main container
        main_container = tk.Frame(self.root, bg=self.colors['bg'])
        main_container.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        # Title section
        self.create_title_section(main_container)
        
        # Control panel
        self.create_control_panel(main_container)
        
        # Status section
        self.create_status_section(main_container)
        
        # Log section
        self.create_log_section(main_container)
        
        # Boot instructions
        self.create_instructions_section(main_container)
        
    def create_title_section(self, parent):
        """Create the title section"""
        title_frame = tk.Frame(parent, bg=self.colors['bg'])
        title_frame.pack(fill=tk.X, pady=(0, 15))
        
        # Main title
        title_label = tk.Label(
            title_frame,
            text="⚡ TERMUX PXE BOOT - STEROID EDITION ⚡",
            bg=self.colors['bg'],
            fg=self.colors['fg'],
            font=('Courier', 18, 'bold')
        )
        title_label.pack()
        
        # Subtitle
        subtitle_label = tk.Label(
            title_frame,
            text="Complete Network Boot Server with Arch Linux Support",
            bg=self.colors['bg'],
            fg=self.colors['fg'],
            font=('Courier', 10)
        )
        subtitle_label.pack()
        
        # Platform info
        platform_info = f"Platform: {self.get_platform()} | Python: {sys.version.split()[0]}"
        info_label = tk.Label(
            title_frame,
            text=platform_info,
            bg=self.colors['bg'],
            fg=self.colors['fg'],
            font=('Courier', 8)
        )
        info_label.pack()
        
    def get_platform(self):
        """Detect platform"""
        system = sys.platform
        if system == "linux":
            if os.path.exists("/data/data/com.termux/files/home"):
                return "Termux (Android)"
            else:
                return "Linux"
        elif system == "darwin":
            return "macOS"
        elif system == "win32":
            return "Windows"
        else:
            return system
            
    def create_control_panel(self, parent):
        """Create control panel"""
        control_frame = tk.LabelFrame(
            parent, 
            text="Server Control", 
            bg=self.colors['bg'],
            fg=self.colors['fg'],
            font=('Courier', 12, 'bold')
        )
        control_frame.pack(fill=tk.X, pady=10)
        
        # Buttons
        buttons_frame = tk.Frame(control_frame, bg=self.colors['bg'])
        buttons_frame.pack(pady=10)
        
        # Start button
        self.start_button = tk.Button(
            buttons_frame,
            text="🚀 START PXE SERVER",
            command=self.start_server,
            bg=self.colors['success'],
            fg='black',
            font=('Courier', 12, 'bold'),
            padx=20,
            pady=10
        )
        self.start_button.pack(side=tk.LEFT, padx=5)
        
        # Stop button
        self.stop_button = tk.Button(
            buttons_frame,
            text="⏹️ STOP SERVER",
            command=self.stop_server,
            bg=self.colors['error'],
            fg='white',
            font=('Courier', 12, 'bold'),
            padx=20,
            pady=10,
            state=tk.DISABLED
        )
        self.stop_button.pack(side=tk.LEFT, padx=5)
        
        # Status
        self.status_label = tk.Label(
            buttons_frame,
            text="● STOPPED",
            bg=self.colors['bg'],
            fg=self.colors['error'],
            font=('Courier', 12, 'bold')
        )
        self.status_label.pack(side=tk.LEFT, padx=20)
        
    def create_status_section(self, parent):
        """Create status section"""
        status_frame = tk.LabelFrame(
            parent, 
            text="Server Information", 
            bg=self.colors['bg'],
            fg=self.colors['fg'],
            font=('Courier', 12, 'bold')
        )
        status_frame.pack(fill=tk.BOTH, expand=True, pady=10)
        
        # Information display
        self.status_text = scrolledtext.ScrolledText(
            status_frame,
            height=8,
            bg=self.colors['secondary'],
            fg=self.colors['fg'],
            font=('Courier', 9),
            wrap=tk.WORD
        )
        self.status_text.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        # Initialize status
        self.update_status_display()
        
    def create_log_section(self, parent):
        """Create log section"""
        log_frame = tk.LabelFrame(
            parent, 
            text="Server Logs", 
            bg=self.colors['bg'],
            fg=self.colors['fg'],
            font=('Courier', 12, 'bold')
        )
        log_frame.pack(fill=tk.BOTH, expand=True, pady=10)
        
        # Log display
        self.log_text = scrolledtext.ScrolledText(
            log_frame,
            height=6,
            bg=self.colors['secondary'],
            fg=self.colors['fg'],
            font=('Courier', 8),
            wrap=tk.WORD
        )
        self.log_text.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
    def create_instructions_section(self, parent):
        """Create instructions section"""
        instructions_frame = tk.LabelFrame(
            parent, 
            text="Boot Instructions", 
            bg=self.colors['bg'],
            fg=self.colors['fg'],
            font=('Courier', 12, 'bold')
        )
        instructions_frame.pack(fill=tk.X, pady=10)
        
        instructions_text = """🖥️ PXE BOOT INSTRUCTIONS:
        
1. Start the PXE server (green button above)
2. Ensure target PC is on same network
3. Enter BIOS/UEFI (F2, F12, Del keys)
4. Enable Network Boot / PXE Boot
5. Set Network Boot as first priority
6. Save and reboot target PC
7. PC will connect to our PXE server

⚠️ IMPORTANT:
• No other DHCP servers should be running
• Network must be the same subnet
• Server IP is auto-detected"""
        
        instructions_label = tk.Label(
            instructions_frame,
            text=instructions_text,
            bg=self.colors['bg'],
            fg=self.colors['fg'],
            font=('Courier', 9),
            justify=tk.LEFT,
            anchor='w'
        )
        instructions_label.pack(padx=10, pady=10)
        
    def center_window(self):
        """Center the window"""
        self.root.update_idletasks()
        width = self.root.winfo_width()
        height = self.root.winfo_height()
        x = (self.root.winfo_screenwidth() // 2) - (width // 2)
        y = (self.root.winfo_screenheight() // 2) - (height // 2)
        self.root.geometry(f'{width}x{height}+{x}+{y}')
        
    def start_server(self):
        """Start the PXE server"""
        if not PXE_AVAILABLE:
            messagebox.showerror("Error", "PXE server module not available!")
            return
            
        if self.server_running:
            return
            
        def server_thread():
            try:
                self.add_log("Starting PXE server...")
                self.add_log("=" * 50)
                
                # Create server
                self.pxe_server = TermuxPXEServer()
                self.server_running = True
                
                # Update UI
                self.root.after(0, self.on_server_started)
                self.root.after(0, self.start_server_logs)
                
                # Start server
                self.pxe_server.start()
                
                # Keep running
                while self.server_running:
                    time.sleep(1)
                    
            except Exception as e:
                self.add_log(f"Server error: {e}")
                self.root.after(0, self.on_server_stopped)
                
        # Start server thread
        threading.Thread(target=server_thread, daemon=True).start()
        
    def stop_server(self):
        """Stop the PXE server"""
        if not self.server_running:
            return
            
        self.server_running = False
        
        if self.pxe_server:
            self.pxe_server.stop()
            
        self.on_server_stopped()
        
    def on_server_started(self):
        """Called when server starts"""
        self.start_button.config(state=tk.DISABLED)
        self.stop_button.config(state=tk.NORMAL)
        self.status_label.config(text="● RUNNING", fg=self.colors['success'])
        self.add_log("Server started successfully!")
        self.add_log("Ready to accept PXE boot requests")
        
    def on_server_stopped(self):
        """Called when server stops"""
        self.start_button.config(state=tk.NORMAL)
        self.stop_button.config(state=tk.DISABLED)
        self.status_label.config(text="● STOPPED", fg=self.colors['error'])
        self.add_log("Server stopped")
        
    def start_server_logs(self):
        """Start monitoring server logs"""
        def log_monitor():
            while self.server_running:
                time.sleep(2)
                self.root.after(0, self.update_status_display)
                
        threading.Thread(target=log_monitor, daemon=True).start()
        
    def add_log(self, message):
        """Add message to log"""
        timestamp = datetime.now().strftime("%H:%M:%S")
        log_message = f"[{timestamp}] {message}"
        self.log_buffer.append(log_message)
        
        # Update log display
        self.root.after(0, self.update_log_display)
        
    def update_log_display(self):
        """Update log display"""
        if hasattr(self, 'log_text'):
            self.log_text.config(state=tk.NORMAL)
            self.log_text.delete(1.0, tk.END)
            
            # Show last 50 log entries
            for log_entry in list(self.log_buffer)[-50:]:
                self.log_text.insert(tk.END, log_entry + "\n")
                
            self.log_text.config(state=tk.DISABLED)
            self.log_text.see(tk.END)
            
    def update_status_display(self):
        """Update status display"""
        if hasattr(self, 'status_text'):
            status_info = f"""Server Status: {"RUNNING" if self.server_running else "STOPPED"}
Platform: {self.get_platform()}
Python: {sys.version.split()[0]}

Network Information:
{self.get_network_info()}

PXE Server Ready:
{"Yes" if self.server_running else "No - Click START to begin"}

Files Created:
{self.get_boot_files_info()}

Usage:
1. Click START to run PXE server
2. Configure target PC for network boot
3. Monitor logs for PXE requests
4. Click STOP when done

This server creates:
• DHCP server for IP assignment
• TFTP server for boot file transfer
• PXE configuration for boot menu
• Arch Linux "on steroids" boot support
            """
            
            self.status_text.config(state=tk.NORMAL)
            self.status_text.delete(1.0, tk.END)
            self.status_text.insert(1.0, status_info)
            self.status_text.config(state=tk.DISABLED)
            
    def get_network_info(self):
        """Get network interface information"""
        try:
            import socket
            
            # Get local IP
            s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
            s.connect(("8.8.8.8", 80))
            local_ip = s.getsockname()[0]
            s.close()
            
            return f"  Local IP: {local_ip}\n  Subnet: 192.168.1.0/24\n  DHCP Range: 192.168.1.50-200"
        except Exception as e:
            return f"  Error getting network info: {e}"
            
    def get_boot_files_info(self):
        """Get boot files information"""
        try:
            if hasattr(self, 'pxe_server') and self.pxe_server:
                base_dir = self.pxe_server.base_dir
                tftp_dir = self.pxe_server.tftp_dir
                
                files = []
                for root, dirs, filenames in os.walk(tftp_dir):
                    for filename in filenames:
                        if filename != '.gitkeep':
                            rel_path = os.path.relpath(os.path.join(root, filename), tftp_dir)
                            files.append(f"  {rel_path}")
                            
                return '\n'.join(files) if files else "  No files created yet"
            else:
                return "  Files will be created when server starts"
        except Exception as e:
            return f"  Error: {e}"
            
    def update_server_status(self):
        """Update server status periodically"""
        self.update_status_display()
        
        # Schedule next update
        if self.server_running:
            self.root.after(3000, self.update_server_status)  # Every 3 seconds
        else:
            self.root.after(5000, self.update_server_status)  # Every 5 seconds when stopped
            
    def run(self):
        """Run the GUI"""
        try:
            # Handle window close
            def on_closing():
                if self.server_running:
                    self.stop_server()
                self.root.destroy()
                
            self.root.protocol("WM_DELETE_WINDOW", on_closing)
            
            # Start GUI
            self.root.mainloop()
            
        except KeyboardInterrupt:
            self.stop_server()
        except Exception as e:
            print(f"GUI error: {e}")

if __name__ == "__main__":
    app = PXEGUI()
    app.run()
