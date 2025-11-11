"""
Configuration Management for Termux PXE Boot
Cross-platform compatible settings and preferences
"""
import json
import os
from pathlib import Path

class Settings:
    def __init__(self):
        # Cross-platform config directory detection
        import platform
        system = platform.system()
        
        if system == "Linux" and os.path.exists("/data/data/com.termux/files/home"):
            # Termux on Android
            self.config_dir = os.path.expanduser("~/.termux_pxe_boot")
        elif system == "Darwin":  # macOS
            self.config_dir = os.path.expanduser("~/Library/Application Support/termux-pxe-boot")
        elif system == "Windows":
            self.config_dir = os.path.join(os.path.expandvars("%APPDATA%"), "termux-pxe-boot")
        else:  # Default Linux/Unix
            self.config_dir = os.path.expanduser("~/.config/termux-pxe-boot")
            
        self.config_file = os.path.join(self.config_dir, "config.json")
        self.default_config = {
            # Network settings
            "interface": "",
            "pxe_ip": "192.168.1.100",
            "network": "192.168.1.0/24",
            "dhcp_range_start": "192.168.1.50",
            "dhcp_range_end": "192.168.1.200",
            
            # Arch Linux customization
            "ui_theme": "Kali Dark",
            "performance": "Maximum",
            "tools": "Kali Tools + Performance",
            "desktop_env": "i3",  # i3, awesome, openbox, etc.
            "terminal": "kitty",  # kitty, alacritty, urxvt, etc.
            "shell": "zsh",      # zsh, bash, fish, etc.
            
            # Performance optimizations
            "kernel_tuning": True,
            "memory_optimization": True,
            "cpu_governor": "performance",
            "io_scheduler": "noop",
            "swap_size": 2,  # GB
            
            # Security settings
            "firewall_enabled": True,
            "selinux_enforcing": False,
            "service_hardening": True,
            
            # GUI preferences
            "terminal_colors": "solarized-dark",
            "font_family": "JetBrains Mono",
            "font_size": 12,
            "animation_enabled": True,
            "transparency": 0.1,
            
            # Network boot settings
            "tftp_port": 69,
            "dhcp_port": 67,
            "boot_timeout": 30,
            "auto_install": True,
            
            # Development tools
            "git_enabled": True,
            "vim_config": True,
            "zsh_plugins": ["git", "sudo", "docker", "python"],
            "pacman_mirrors": "auto",  # auto, us, eu, asia, etc.
            
            # Kali-style features
            "kali_aliases": True,
            "kali_scripts": True,
            "screenshot_tool": "scrot",
            "network_scanner": "nmap",
            "password_cracker": "hashcat"
        }
        
        # Performance profiles
        self.performance_profiles = {
            "Balanced": {
                "cpu_governor": "balanced",
                "kernel_tuning": True,
                "memory_optimization": False,
                "animation_enabled": True,
                "transparency": 0.2
            },
            "Maximum": {
                "cpu_governor": "performance",
                "kernel_tuning": True,
                "memory_optimization": True,
                "animation_enabled": False,
                "transparency": 0.0
            },
            "Gaming": {
                "cpu_governor": "performance",
                "kernel_tuning": True,
                "memory_optimization": True,
                "io_scheduler": "noop",
                "animation_enabled": False,
                "transparency": 0.0
            },
            "Minimal": {
                "cpu_governor": "powersave",
                "kernel_tuning": False,
                "memory_optimization": False,
                "animation_enabled": False,
                "transparency": 0.0,
                "swap_size": 0
            }
        }
        
        # Theme configurations
        self.theme_configs = {
            "Kali Dark": {
                "colors": {
                    "primary": "#00ff00",
                    "background": "#1a1a1a",
                    "secondary": "#2d2d2d",
                    "text": "#00ff00",
                    "accent": "#00aa00"
                },
                "terminal": "solarized-dark",
                "wallpaper": "kali-dark.jpg"
            },
            "Cyberpunk": {
                "colors": {
                    "primary": "#ff00ff",
                    "background": "#0a0a0a",
                    "secondary": "#1a0a1a",
                    "text": "#ff00ff",
                    "accent": "#aa00aa"
                },
                "terminal": "cyberpunk",
                "wallpaper": "cyberpunk-rain.jpg"
            },
            "Matrix": {
                "colors": {
                    "primary": "#00ff41",
                    "background": "#000000",
                    "secondary": "#001100",
                    "text": "#00ff41",
                    "accent": "#008800"
                },
                "terminal": "matrix",
                "wallpaper": "matrix-green.jpg"
            },
            "Neon Green": {
                "colors": {
                    "primary": "#00ff00",
                    "background": "#000000",
                    "secondary": "#0a0a0a",
                    "text": "#00ff00",
                    "accent": "#00aa00"
                },
                "terminal": "neon-green",
                "wallpaper": "neon-grid.jpg"
            }
        }
        
        # Tool packages
        self.tool_packages = {
            "Kali Tools + Performance": {
                "base": ["base", "base-devel"],
                "desktop": ["i3-wm", "polybar", "rofi", "dmenu"],
                "terminal": ["kitty", "zsh", "oh-my-zsh"],
                "fonts": ["ttf-dejavu", "ttf-ubuntu-font-family", "ttf-droid"],
                "kali_tools": ["nmap", "wireshark-qt", "metasploit", "burpsuite", "sqlmap"],
                "performance": ["htop", "iotop", "nethogs", "lm_sensors", "tuned"],
                "network": ["wireless_tools", "wpa_supplicant", "NetworkManager"],
                "development": ["git", "vim", "python", "nodejs", "go"],
                "media": ["mpv", "imagemagick", "ffmpeg"],
                "utilities": ["unzip", "p7zip", "tree", "jq"]
            },
            "Full Kali Suite": {
                "base": ["base", "base-devel"],
                "kali_complete": [
                    "nmap", "wireshark-qt", "metasploit", "burpsuite", "sqlmap",
                    "hashcat", "john", "hydra", "aircrack-ng", "recon-ng",
                    "dirb", "nikto", "masscan", "zmap", "gobuster",
                    "beef-xss", "commix", "xsser", "wapiti", "dirbuster"
                ],
                "development": ["git", "vim", "python", "ruby", "perl", "go"],
                "forensics": ["volatility", "binwalk", "exiftool", "foremost"],
                "reverse": ["radare2", "gdb", "objdump", "hexdump"]
            },
            "Pentesting Essentials": {
                "base": ["base", "base-devel"],
                "essential": [
                    "nmap", "wireshark-qt", "ncat", "telnet", "ftp",
                    "curl", "wget", "openssl", "ssh", "git",
                    "vim", "python", "bash", "sed", "awk"
                ]
            },
            "Custom Selection": {
                # Empty by default, user will specify
            }
        }
        
        self.load_config()
        
    def load_config(self):
        """Load configuration from file"""
        try:
            if os.path.exists(self.config_file):
                with open(self.config_file, 'r') as f:
                    self.config = json.load(f)
            else:
                self.config = self.default_config.copy()
                self.save_config()
        except Exception as e:
            print(f"Error loading config: {e}")
            self.config = self.default_config.copy()
            
    def save_config(self, config_dict=None):
        """Save configuration to file"""
        try:
            # Create config directory if it doesn't exist
            os.makedirs(self.config_dir, exist_ok=True)
            
            if config_dict:
                self.config.update(config_dict)
                
            with open(self.config_file, 'w') as f:
                json.dump(self.config, f, indent=2)
                
            return True
        except Exception as e:
            print(f"Error saving config: {e}")
            return False
            
    def get(self, key, default=None):
        """Get a configuration value"""
        return self.config.get(key, default)
        
    def set(self, key, value):
        """Set a configuration value"""
        self.config[key] = value
        
    def get_performance_profile(self, profile_name):
        """Get performance profile settings"""
        return self.performance_profiles.get(profile_name, {})
        
    def get_theme_config(self, theme_name):
        """Get theme configuration"""
        return self.theme_configs.get(theme_name, {})
        
    def get_tool_package(self, package_name):
        """Get tool package configuration"""
        return self.tool_packages.get(package_name, {})
        
    def validate_config(self, config):
        """Validate configuration values"""
        errors = []
        
        # Validate network settings
        if not config.get('pxe_ip'):
            errors.append("PXE IP is required")
        if not config.get('interface'):
            errors.append("Network interface is required")
            
        # Validate performance settings
        if config.get('swap_size', 0) < 0:
            errors.append("Swap size must be non-negative")
        if config.get('font_size', 12) < 8 or config.get('font_size', 12) > 72:
            errors.append("Font size must be between 8 and 72")
            
        # Validate port numbers
        if config.get('tftp_port', 69) < 1024 or config.get('tftp_port', 69) > 65535:
            errors.append("TFTP port must be between 1024 and 65535")
        if config.get('dhcp_port', 67) < 1024 or config.get('dhcp_port', 67) > 65535:
            errors.append("DHCP port must be between 1024 and 65535")
            
        return errors
        
    def reset_to_defaults(self):
        """Reset configuration to default values"""
        self.config = self.default_config.copy()
        return self.save_config()
        
    def export_config(self, filepath):
        """Export configuration to a file"""
        try:
            with open(filepath, 'w') as f:
                json.dump(self.config, f, indent=2)
            return True
        except Exception as e:
            print(f"Error exporting config: {e}")
            return False
            
    def import_config(self, filepath):
        """Import configuration from a file"""
        try:
            with open(filepath, 'r') as f:
                imported_config = json.load(f)
                
            # Validate imported config
            errors = self.validate_config(imported_config)
            if errors:
                raise ValueError(f"Invalid configuration: {', '.join(errors)}")
                
            self.config.update(imported_config)
            return self.save_config()
            
        except Exception as e:
            print(f"Error importing config: {e}")
            return False
