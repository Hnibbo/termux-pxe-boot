"""
Arch Linux Customizer for Termux PXE Boot
Creates Kali-like UI and performance optimizations for Arch Linux installations
"""
import os
import shutil
import subprocess
from pathlib import Path

class ArchCustomizer:
    def __init__(self, settings=None, logger=None):
        self.settings = settings
        self.logger = logger
        self.assets_dir = "/data/data/com.termux/files/home/pxe_assets"
        self.customizer_dir = os.path.join(self.assets_dir, "customizer")
        self.motd_dir = os.path.join(self.customizer_dir, "motd")
        self.config_dir = os.path.join(self.customizer_dir, "configs")
        self.scripts_dir = os.path.join(self.customizer_dir, "scripts")
        self.themes_dir = os.path.join(self.customizer_dir, "themes")
        self.performance_dir = os.path.join(self.customizer_dir, "performance")
        
        # Create directory structure
        self._create_directory_structure()
        
    def _create_directory_structure(self):
        """Create the directory structure for customizations"""
        directories = [
            self.customizer_dir,
            self.motd_dir,
            self.config_dir,
            self.scripts_dir,
            self.themes_dir,
            self.performance_dir,
            os.path.join(self.config_dir, "i3"),
            os.path.join(self.config_dir, "zsh"),
            os.path.join(self.config_dir, "vim"),
            os.path.join(self.config_dir, "terminal"),
            os.path.join(self.themes_dir, "gtk"),
            os.path.join(self.themes_dir, "icons"),
            os.path.join(self.performance_dir, "kernel"),
            os.path.join(self.performance_dir, "services")
        ]
        
        for directory in directories:
            os.makedirs(directory, exist_ok=True)
            
        self.logger.info("Customizer directory structure created")
        
    def create_enhanced_motd(self, theme="Kali Dark"):
        """Create enhanced message of the day with themed graphics"""
        if theme == "Kali Dark":
            motd_content = '''╔══════════════════════════════════════════════════════════════════════════════╗
║                    🐧 ARCH LINUX ENHANCED PERFORMANCE EDITION                ║
║                     Powered by Termux PXE Boot System                       ║
║              🔥 Optimized for Maximum Performance 🔥                        ║
╚══════════════════════════════════════════════════════════════════════════════╝

⚡ System Status: Enhanced Performance Mode
🎯 Kali Tools: Pre-installed and Ready
🚀 Network: PXE Boot Compatible
🛡️  Security: Hardened Configuration

Welcome to your custom Arch Linux installation!
'''
        elif theme == "Cyberpunk":
            motd_content = '''╔══════════════════════════════════════════════════════════════════════════════╗
║                 🌈 CYBERPUNK ARCH LINUX PERFORMANCE EDITION 🌈                ║
║                    Powered by Termux PXE Boot System                        ║
║              ⚡ NEON OPTIMIZED FOR MAXIMUM POWER ⚡                          ║
╚══════════════════════════════════════════════════════════════════════════════╝

🌃 System Status: Cyberpunk Performance Mode
🎯 Cyber Tools: Neon Enhanced and Ready
🚀 Network: Quantum PXE Boot
🛡️  Security: Digital Armor Activated

Enter the matrix... Welcome to Cyberpunk Linux!
'''
        elif theme == "Matrix":
            motd_content = '''╔══════════════════════════════════════════════════════════════════════════════╗
║                  🟢 MATRIX ARCH LINUX - CHOOSE THE PILL 🟢                   ║
║                    Powered by Termux PXE Boot System                        ║
║              ⚡ CODE IS PERFORMANCE - NO BUGS ⚡                             ║
╚══════════════════════════════════════════════════════════════════════════════╝

🟢 System Status: Matrix Performance Enabled
🎯 Tools: The Matrix Is Loaded
🚀 Network: Following The White Rabbit
🛡️  Security: Bulletproof in the Matrix

Follow the white rabbit... Welcome to the Matrix!
'''
        else:  # Neon Green
            motd_content = '''╔══════════════════════════════════════════════════════════════════════════════╗
║              ⚡ NEON GREEN ARCH LINUX - PERFORMANCE EDITION ⚡                ║
║                    Powered by Termux PXE Boot System                        ║
║              🔥 MAXIMUM PERFORMANCE - ZERO COMPROMISE 🔥                    ║
╚══════════════════════════════════════════════════════════════════════════════╝

🟢 System Status: Neon Green Performance Mode
🎯 Tools: Bright and Shining
🚀 Network: Lightning Fast
🛡️  Security: Neon Shield Active

Light up your system! Welcome to Neon Green Linux!
'''
            
        motd_path = os.path.join(self.motd_dir, "enhanced_motd")
        with open(motd_path, 'w') as f:
            f.write(motd_content)
            
        self.logger.info(f"Enhanced MOTD created for theme: {theme}")
        return motd_path
        
    def create_i3_config(self, theme="Kali Dark"):
        """Create i3 window manager configuration with themed styling"""
        i3_config = '''# i3 Configuration
# Generated by Termux PXE Boot
# Arch Linux Enhanced Performance Edition

# Key bindings
set $mod Mod4

# Font for window titles
font pango: JetBrains Mono 10

# Colors for {theme} theme
client.focused          #00ff00 #00ff00 #1a1a1a #00ff00
client.focused_inactive #2d2d2d #2d2d2d #888888 #292929
client.unfocused        #2d2d2d #2d2d2d #888888 #292929
client.urgent           #ff0000 #ff0000 #ffffff #ff0000

# Start XDG autostart
exec --no-startup-id dex --autostart --environment i3

# Gaps settings
gaps inner 5
gaps outer 5

# Workspace settings
workspace_layout default

# Border style for new windows
new_window 1pixel

# Default workspace
workspace 1 output HDMI-1

# Background
exec_always feh --bg-scale /usr/share/backgrounds/default.jpg

# Terminal
bindsym $mod+Return exec kitty

# Kill focused window
bindsym $mod+Shift+q kill

# Start rofi (drun)
bindsym $mod+d exec rofi -show drun

# Start terminal
bindsym $mod+Return exec kitty

# Volume controls
bindsym XF86AudioRaiseVolume exec amixer set Master 5%+
bindsym XF86AudioLowerVolume exec amixer set Master 5%-
bindsym XF86AudioMute exec amixer set Master toggle

# Brightness controls
bindsym XF86MonBrightnessUp exec brightnessctl set 10%+
bindsym XF86MonBrightnessDown exec brightnessctl set 10%-

# Screenshot
bindsym Print exec scrot '%Y-%m-%d-%H-%M-$wx$hx.png'
bindsym $mod+Print exec scrot -u '%Y-%m-%d-%H-%M-$wx$hx.png'

# Reload config
bindsym $mod+Shift+c reload

# Restart i3
bindsym $mod+Shift+r restart

# Exit i3
bindsym $mod+Shift+e exec "i3-nagbar -t warning -m 'Exit i3?' -b 'Yes, exit i3' 'i3-msg exit'"

# Floating toggle
floating_modifier $mod

# Move between windows
bindsym $mod+Left focus left
bindsym $mod+Down focus down
bindsym $mod+Up focus up
bindsym $mod+Right focus right

# Move windows
bindsym $mod+Shift+Left move left
bindsym $mod+Shift+Down move down
bindsym $mod+Shift+Up move up
bindsym $mod+Shift+Right move right

# Resize windows
bindsym $mod+r mode "resize"
mode "resize" {
    bindsym Left resize shrink width 10 px or 10 ppt
    bindsym Down resize grow height 10 px or 10 ppt
    bindsym Up resize shrink height 10 px or 10 ppt
    bindsym Right resize grow width 10 px or 10 ppt
    bindsym Return mode "default"
    bindsym Escape mode "default"
}

# Start i3bar
bar {
    status_command i3status
    colors {
        background #1a1a1a
        statusline #00ff00
        focused_workspace #00ff00 #00ff00 #1a1a1a
        active_workspace #2d2d2d #2d2d2d #00ff00
        inactive_workspace #2d2d2d #2d2d2d #888888
        urgent_workspace #ff0000 #ff0000 #ffffff
    }
}

# Kali-specific bindings
# Network scanning
bindsym $mod+n exec nmap 192.168.1.0/24
# Port scanning
bindsym $mod+p exec nmap -sV -O $(hostname -I | awk '{print $1}')
# System info
bindsym $mod+i exec htop
# File manager
bindsym $mod+e exec ranger

# Auto-start services
exec_always polybar
exec_always network-manager-applet
exec_always feh --bg-scale /usr/share/backgrounds/default.jpg
        '''.format(theme=theme)
        
        i3_config_path = os.path.join(self.config_dir, "i3", "config")
        with open(i3_config_path, 'w') as f:
            f.write(i3_config)
            
        self.logger.info("i3 configuration created")
        return i3_config_path
        
    def create_zsh_config(self, theme="Kali Dark"):
        """Create ZSH configuration with Kali-like aliases and themes"""
        zsh_config = '''# ZSH Configuration
# Generated by Termux PXE Boot
# Arch Linux Enhanced Performance Edition

# Path to oh-my-zsh
ZSH="$HOME/.oh-my-zsh"

# Theme
ZSH_THEME="agnoster"

# Oh-my-zsh plugins
plugins=(
    git
    sudo
    docker
    python
    pip
    colored-man-pages
    zsh-autosuggestions
    zsh-syntax-highlighting
)

# Environment variables
export EDITOR="vim"
export VISUAL="vim"
export TERM="xterm-256color"

# Aliases for Kali-like experience
alias ..='cd ..'
alias ...='cd ../..'
alias ls='ls --color=auto'
alias ll='ls -la --color=auto'
alias l='ls --color=auto -la'
alias la='ls -la --color=auto'
alias grep='grep --color=auto'
alias fgrep='fgrep --color=auto'
alias egrep='egrep --color=auto'
alias diff='colordiff'
alias tailf='tail -f'

# Kali-style aliases
alias kali-update='sudo pacman -Syu'
alias kali-upgrade='sudo pacman -Syyu'
alias kali-clean='sudo pacman -Scc'
alias kali-install='sudo pacman -S'
alias kali-remove='sudo pacman -Rns'
alias kali-search='sudo pacman -Ss'
alias kali-info='sudo pacman -Si'
alias kali-orphans='sudo pacman -Rns $(pacman -Qqdt)'

# System control aliases
alias restart='sudo reboot'
alias shutdown='sudo poweroff'
alias hibernate='sudo systemctl hibernate'
alias suspend='sudo systemctl suspend'
alias status='systemctl status'
alias services='systemctl list-units --type=service --state=running'

# Network aliases
alias netstat='ss -tuln'
alias ports='ss -tuln'
alias ipinfo='ip addr show'
alias myip='curl -s ifconfig.me'
alias whois='whois $(myip)'

# Security and penetration testing
alias nmap-scan='nmap -sS -O -A'
alias port-scan='nmap -sV -sC'
alias network-scan='nmap -sn 192.168.1.0/24'
alias vulnerability-scan='nikto -h http://localhost'

# Performance monitoring
alias cpuinfo='lscpu'
alias meminfo='free -h'
alias diskinfo='df -h'
alias topproc='ps aux --sort=-%mem | head -10'
alias networkio='nethogs -d 1'

# Development aliases
alias py='python3'
alias pip-upgrade='pip install --upgrade pip'
alias git-sync='git fetch origin && git merge origin/main'
alias git-push='git push origin main'
alias git-pull='git pull origin main'

# Quick editing
alias v='vim'
alias sv='sudo vim'
alias nano='micro'
alias edit-zsh='v ~/.zshrc'
alias reload-zsh='source ~/.zshrc'

# Entertainment and extras
alias matrix='cmatrix -a -b -C green -s 60'
alias cowsay='cowsay -f tux'
alias figlet-banner='figlet'
alias ascii-art='toilet --gay'

# Function definitions
kali-help() {
    echo "🐧 Kali-Style Commands Available:"
    echo "k-...     = Kali command shortcuts"
    echo "net-...   = Network commands"
    echo "sys-...   = System commands"
    echo "dev-...   = Development commands"
    echo ""
    echo "Type 'alias' to see all available aliases"
}

# Function to show system information
sys-info() {
    echo "🖥️  System Information:"
    echo "OS: $(uname -o)"
    echo "Kernel: $(uname -r)"
    echo "Uptime: $(uptime -p)"
    echo "Memory: $(free -h | grep Mem | awk '{print $2}') total"
    echo "CPU: $(lscpu | grep "Model name" | cut -d: -f2 | xargs)"
    echo "Disk: $(df -h / | tail -1 | awk '{print $2}') total"
}

# Function for network scanning
net-scan() {
    if [ $# -eq 0 ]; then
        nmap -sn 192.168.1.0/24
    else
        nmap -sn $1
    fi
}

# Load oh-my-zsh
source $ZSH/oh-my-zsh.sh

# Custom prompt
export PS1='%F{green}%n@%m%f %F{blue}%1~%f %# '

# Case-insensitive completion
zstyle ':completion:*' matcher-list 'm:{a-zA-Z}={A-Za-z}'

# Enable color for man pages
export MANPAGER='most'

# History settings
HISTSIZE=10000
SAVEHIST=10000
HISTFILE=~/.zsh_history

# Load auto-suggestions
source /usr/share/zsh/plugins/zsh-autosuggestions/zsh-autosuggestions.zsh 2>/dev/null
source /usr/share/zsh/plugins/zsh-syntax-highlighting/zsh-syntax-highlighting.zsh 2>/dev/null
        '''
        
        zsh_config_path = os.path.join(self.config_dir, "zsh", "zshrc")
        with open(zsh_config_path, 'w') as f:
            f.write(zsh_config)
            
        self.logger.info("ZSH configuration created")
        return zsh_config_path
        
    def create_vim_config(self, theme="Kali Dark"):
        """Create Vim configuration with programming enhancements"""
        vim_config = '''" Vim Configuration
" Generated by Termux PXE Boot
" Arch Linux Enhanced Performance Edition

" Basic settings
set nocompatible
syntax on
filetype plugin indent on

" Display settings
set number
set relativenumber
set cursorline
set cursorcolumn
set showcmd
set ruler
set laststatus=2
set wildmenu
set showmatch

" Indentation
set tabstop=4
set shiftwidth=4
set expandtab
set smarttab
set autoindent
set smartindent

" Search settings
set incsearch
set hlsearch
set ignorecase
set smartcase
set gdefault

" Clipboard
set clipboard=unnamedplus

" Encoding
set encoding=utf-8
set fileencoding=utf-8

" Backup and swap files
set backup
set backupdir=~/.vim/backup
set directory=~/.vim/swp
set undofile
set undodir=~/.vim/undo

" Color scheme
colorscheme desert
set background=dark

" Key mappings
" Leader key
let mapleader = ","

" Navigation
nnoremap <C-h> <C-w>h
nnoremap <C-j> <C-w>j
nnoremap <C-k> <C-w>k
nnoremap <C-l> <C-w>l

" Split navigation
nnoremap <C-Left> <C-w>h
nnoremap <C-Down> <C-w>j
nnoremap <C-Up> <C-w>k
nnoremap <C-Right> <C-w>l

" Split commands
nnoremap <Leader>v :vsplit<CR>
nnoremap <Leader>h :split<CR>

" File operations
nnoremap <Leader>s :w<CR>
nnoremap <Leader>q :q<CR>
nnoremap <Leader>wq :wq<CR>
nnoremap <Leader>w :w<CR>
nnoremap <Leader>q! :q!<CR>

" Tab management
nnoremap <Leader>tn :tabnew<CR>
nnoremap <Leader>tc :tabclose<CR>
nnoremap <Leader>to :tabonly<CR>
nnoremap <Leader>tp :tabprev<CR>
nnoremap <Leader>tn :tabnext<CR>

" Code folding
set foldmethod=indent
set foldlevel=99
nnoremap <space> za

" Buffer navigation
nnoremap <Leader>bn :bnext<CR>
nnoremap <Leader>bp :bprevious<CR>
nnoremap <Leader>bd :bdelete<CR>

" Visual mode improvements
vnoremap < <gv
vnoremap > >gv

" Copy/paste
vnoremap <Leader>y "+y
nnoremap <Leader>p "+p
nnoremap <Leader>P "+P

" Terminal shortcuts
nnoremap <Leader>tt :terminal<CR>

" File explorer
nnoremap <Leader>e :Vexplore<CR>

" Comment/uncomment
vnoremap <Leader>/ :s/^/\/\//g<CR>:noh<CR>
vnoremap <Leader>\\ :s/^\/\///g<CR>:noh<CR>

" Quick run
nnoremap <Leader>r :!%:p<CR>

" Clear search
nnoremap <Leader>c :nohlsearch<CR>

" Kali-specific shortcuts
nnoremap <Leader>ka :!echo "Kali Mode Activated!"<CR>
nnoremap <Leader>kn :!nmap -sV -O $(echo $IP)<CR>
nnoremap <Leader>ks :!sudo systemctl status<CR>

" Plugin settings (if vim-plug is available)
if empty(glob('~/.vim/autoload/plug.vim'))
  silent !curl -fLo ~/.vim/autoload/plug.vim --create-dirs
    \ https://raw.githubusercontent.com/junegunn/vim-plug/master/plug.vim
  autocmd VimEnter * PlugInstall --sync | source $MYVIMRC
endif

" Plugin declarations
call plug#begin('~/.vim/plugged')

" Essential plugins
Plug 'tpope/vim-fugitive'        " Git wrapper
Plug 'tpope/vim-surround'        " Surround text objects
Plug 'tpope/vim-repeat'          " Repeat plugin commands
Plug 'jiangmiao/auto-pairs'      " Auto pairs for brackets
Plug 'dense-analysis/ale'        " Linting
Plug 'vim-airline/vim-airline'  " Status line
Plug 'vim-airline/vim-airline-themes' " Airline themes
Plug 'morhetz/gruvbox'          " Gruvbox color scheme
Plug 'dracula/vim'              " Dracula color scheme
Plug 'arcticicestudio/nord-vim' " Nord color scheme

" Programming language support
Plug 'fatih/vim-go'             " Go support
Plug 'davidhalter/jedi-vim'     " Python support
Plug 'pangloss/vim-javascript'  " JavaScript support
Plug 'posva/vim-vue'            " Vue.js support
Plug 'stephpy/vim-yaml'         " YAML support
Plug 'zhimsel/vim-stay'         " Keep cursor position

" Call plug#end()

" Airline configuration
let g:airline_theme='dark'
let g:airline_powerline_fonts=1

" Auto-pairs settings
let g:AutoPairsMapSpace=0

" ALE settings
let g:ale_linters = {
\   'python': ['flake8', 'pylint'],
\   'javascript': ['eslint'],
\   'go': ['go', 'golint']
\}
let g:ale_fixers = {
\   'python': ['black', 'isort'],
\   'javascript': ['prettier'],
\   'go': ['gofmt']
\}

" Python specific settings
autocmd FileType python setlocal shiftwidth=4 tabstop=4
autocmd FileType python setlocal number
autocmd FileType python setlocal relativenumber

" Go specific settings
autocmd FileType go setlocal shiftwidth=4 tabstop=4
autocmd FileType go setlocal number
autocmd FileType go setlocal relativenumber

" Custom commands
command! -nargs=0 Swap :call Swap()
function! Swap()
    if expand('%:e') == 'py'
        s/\.py$/.py.bak/
    elseif expand('%:e') == 'js'
        s/\.js$/.js.bak/
    endif
endfunction

" Quick file templates
autocmd BufNewFile *.py 0r ~/.vim/templates/python.py
autocmd BufNewFile *.sh 0r ~/.vim/templates/shell.sh
autocmd BufNewFile *.js 0r ~/.vim/templates/javascript.js

" Performance settings
set lazyredraw
set ttyfast
set ttyscroll=3

" Remember folds
autocmd BufWinLeave * mkview
autocmd BufWinEnter * silent loadview

" Word completion
set completeopt=menuone,menu,longest,preview

" Recalculate screen size when resizing
au VimResized * :wincmd =

" Highlight current line
set cursorline
hi CursorLine ctermbg=darkgray

" Set working directory to file location
autocmd BufEnter * cd %:p:h

" Auto save and load sessions
autocmd VimLeave * mksession! ~/.vim/session.vim
autocmd VimEnter * silent source ~/.vim/session.vim
        '''
        
        vim_config_path = os.path.join(self.config_dir, "vim", "vimrc")
        with open(vim_config_path, 'w') as f:
            f.write(vim_config)
            
        self.logger.info("Vim configuration created")
        return vim_config_path
        
    def create_performance_configs(self, profile="Maximum"):
        """Create performance optimization configurations"""
        configs = {}
        
        # Kernel tuning
        kernel_sysctl = '''# Kernel performance tuning
# Generated by Termux PXE Boot

# Network performance
net.core.rmem_max = 134217728
net.core.wmem_max = 134217728
net.core.netdev_max_backlog = 5000
net.ipv4.tcp_rmem = 4096 65536 134217728
net.ipv4.tcp_wmem = 4096 65536 134217728
net.ipv4.tcp_congestion_control = bbr

# Memory management
vm.swappiness = 10
vm.dirty_ratio = 3
vm.dirty_background_ratio = 2
vm.vfs_cache_pressure = 50
vm.dirty_expire_centisecs = 3000
vm.dirty_writeback_centisecs = 500

# I/O scheduler
block.sda.scheduler = noop

# CPU scheduling
kernel.sched_migration_cost_ns = 5000000
kernel.sched_min_granularity_ns = 15000000
kernel.sched_wakeup_granularity_ns = 2000000

# File system
fs.file-max = 2097152
fs.inotify.max_user_watches = 524288
        '''
        
        kernel_config_path = os.path.join(self.performance_dir, "kernel", "sysctl.conf")
        with open(kernel_config_path, 'w') as f:
            f.write(kernel_sysctl)
        configs['kernel'] = kernel_config_path
        
        # Service optimization
        service_optimization = '''# Systemd service optimization
# Generated by Termux PXE Boot

[Unit]
Description=Performance Optimization Service
After=network.target

[Service]
Type=oneshot
RemainAfterExit=yes
ExecStart=/usr/bin/systemctl set-default multi-user.target
ExecStart=/usr/bin/systemctl enable NetworkManager
ExecStart=/usr/bin/systemctl disable bluetooth
ExecStart=/usr/bin/systemctl disable cups
ExecStart=/usr/bin/systemctl disable avahi-daemon
ExecStart=/usr/bin/systemctl disable ModemManager

[Install]
WantedBy=multi-user.target
        '''
        
        service_config_path = os.path.join(self.performance_dir, "services", "optimization.service")
        with open(service_config_path, 'w') as f:
            f.write(service_optimization)
        configs['service'] = service_config_path
        
        self.logger.info("Performance configurations created")
        return configs
        
    def create_pacman_optimization(self):
        """Create pacman mirrorlist and configuration for optimal performance"""
        pacman_config = '''# Pacman configuration
# Generated by Termux PXE Boot

# System architecture
Architecture = auto

# Color output
Color
ILoveCandy

# Verbose package lists
VerbosePkgLists

# Parallel downloads
ParallelDownloads = 8

# Display progress bar and current action
EnableSysLog

# Check space
CheckSpace

# Database sync
Refresh

# Architecture
Architecture = x86_64

# Include configuration
Include = /etc/pacman.d/mirrorlist

# SigLevel
SigLevel = Never
LocalFileSigLevel = Optional

# Options
HoldPkg = pacman glibc
CacheDir = /var/cache/pacman/pkg
LogFile = /var/log/pacman.log
GPGDir = /etc/pacman.d/gnupg/
ConfigFile = /etc/pacman.conf
RootDir = /
        '''
        
        mirrorlist = '''# Mirrorlist
# Generated by Termux PXE Boot
# Optimized for performance

Server = https://mirrors.kernel.org/archlinux/$repo/os/$arch
Server = https://archlinux.bridge.de/archlinux/$repo/os/$arch
Server = https://mirror.zerobyte.com.au/archlinux/$repo/os/$arch
Server = https://mirror.f4st.host/archlinux/$repo/os/$arch
Server = https://archlinux.thaller.ws/$repo/os/$arch
        '''
        
        pacman_config_path = os.path.join(self.config_dir, "pacman", "pacman.conf")
        pacman_dir = os.path.dirname(pacman_config_path)
        os.makedirs(pacman_dir, exist_ok=True)
        with open(pacman_config_path, 'w') as f:
            f.write(pacman_config)
            
        mirrorlist_path = os.path.join(pacman_dir, "mirrorlist")
        with open(mirrorlist_path, 'w') as f:
            f.write(mirrorlist)
            
        self.logger.info("Pacman optimization files created")
        return {
            'config': pacman_config_path,
            'mirrorlist': mirrorlist_path
        }
        
    def create_bashrc_enhancement(self, theme="Kali Dark"):
        """Create enhanced .bashrc with performance and styling"""
        bashrc_content = '''# Enhanced .bashrc
# Generated by Termux PXE Boot
# Arch Linux Enhanced Performance Edition

# System information function
sysinfo() {
    echo "🖥️  System Status:"
    echo "OS: $(uname -o)"
    echo "Kernel: $(uname -r)"
    echo "Uptime: $(uptime -p)"
    echo "Load: $(uptime | awk -F'load average:' '{ print $2 }')"
    echo "Memory: $(free -h | grep Mem | awk '{print $2}') total, $(free -h | grep Mem | awk '{print $3}') used"
    echo "Disk: $(df -h / | tail -1 | awk '{print $2}') total, $(df -h / | tail -1 | awk '{print $3}') used"
    echo "Temperature: $(sensors | grep 'Core 0' | awk '{print $3}')"
}

# Network information function
netinfo() {
    echo "🌐 Network Status:"
    echo "IP Address: $(curl -s ifconfig.me)"
    echo "External IP: $(curl -s ipinfo.io/ip)"
    echo "Location: $(curl -s ipinfo.io/$(curl -s ifconfig.me)/city 2>/dev/null) - $(curl -s ipinfo.io/$(curl -s ifconfig.me)/country 2>/dev/null)"
    echo "ISP: $(curl -s ipinfo.io/$(curl -s ifconfig.me)/org 2>/dev/null)"
}

# Quick system monitor
monitor() {
    echo "📊 System Monitor:"
    top -bn1 | head -5
    echo ""
    free -h
}

# Kali-style color prompt
if [[ ${EUID} == 0 ]]; then
    PS1="\[\033[01;31m\]\h\[\033[01;34m\] \w \$\[\033[00m\] "
else
    PS1="\[\033[01;32m\]\u@\h\[\033[01;34m\] \w \$\[\033[00m\] "
fi

# Disable the bell
if [[ $PS1 && -f /usr/share/bash-completion/bash_completion ]]; then
    . /usr/share/bash-completion/bash_completion
fi

# Command history
export HISTSIZE=10000
export HISTFILESIZE=20000
export HISTCONTROL=ignoredups:erasedups
export HISTTIMEFORMAT="[%F %T] "
export PROMPT_COMMAND='history -a'

# Color support
alias grep='grep --color=auto'
alias fgrep='fgrep --color=auto'
alias egrep='egrep --color=auto'
alias ls='ls --color=auto'
alias ll='ls -la --color=auto'
alias la='ls -A --color=auto'
alias l='ls -CF --color=auto'

# Kali command shortcuts
alias kali-update='sudo pacman -Syu'
alias kali-upgrade='sudo pacman -Syyu'
alias kali-clean='sudo pacman -Scc'
alias kali-install='sudo pacman -S'
alias kali-remove='sudo pacman -Rns'
alias kali-search='sudo pacman -Ss'
alias kali-info='sudo pacman -Si'

# System control
alias restart='sudo reboot'
alias shutdown='sudo poweroff'
alias hibernate='sudo systemctl hibernate'
alias suspend='sudo systemctl suspend'

# Network commands
alias ports='ss -tuln'
alias myip='curl -s ifconfig.me'
alias netstat='ss -tuln'

# Performance monitoring
alias cpu='lscpu'
alias mem='free -h'
alias disk='df -h'
alias topproc='ps aux --sort=-%mem | head -10'

# Development shortcuts
alias py='python3'
alias pipup='pip install --upgrade pip'
alias gitsync='git fetch origin && git merge origin/main'
alias gitpush='git push origin main'
alias gitpull='git pull origin main'

# Security and network scanning
alias nmap-scan='nmap -sS -O -A'
alias port-scan='nmap -sV -sC'
alias network-scan='nmap -sn 192.168.1.0/24'
alias vuln-scan='nikto -h http://localhost'

# Quick text editing
alias v='vim'
alias nano='micro'
alias edit-bash='v ~/.bashrc'
alias reload-bash='source ~/.bashrc'

# Fun commands
alias matrix='cmatrix -a -b -C green -s 60'
alias cowsay='cowsay -f tux'
alias figlet='toilet --gay'

# Function to show help
kali-help() {
    echo "🐧 Available Kali-style commands:"
    echo "k-...     : Kali system commands"
    echo "net-...   : Network commands"
    echo "sys-...   : System monitoring"
    echo "dev-...   : Development tools"
    echo ""
    echo "Type 'alias' to see all available shortcuts"
}

# Welcome message
echo "⚡ Welcome to Arch Linux Enhanced Performance Edition!"
echo "Type 'sysinfo' for system information"
echo "Type 'netinfo' for network information"
echo "Type 'kali-help' for command help"
        '''
        
        bashrc_path = os.path.join(self.config_dir, "bash", "bashrc")
        bash_dir = os.path.dirname(bashrc_path)
        os.makedirs(bash_dir, exist_ok=True)
        with open(bashrc_path, 'w') as f:
            f.write(bashrc_content)
            
        self.logger.info("Enhanced bashrc created")
        return bashrc_path
        
    def create_all_customizations(self, theme="Kali Dark", performance="Maximum"):
        """Create all customization files for a complete installation"""
        try:
            results = {}
            
            # Create all customization files
            results['motd'] = self.create_enhanced_motd(theme)
            results['i3_config'] = self.create_i3_config(theme)
            results['zsh_config'] = self.create_zsh_config(theme)
            results['vim_config'] = self.create_vim_config(theme)
            results['bashrc'] = self.create_bashrc_enhancement(theme)
            results['performance'] = self.create_performance_configs(performance)
            results['pacman'] = self.create_pacman_optimization()
            
            self.logger.info(f"All customizations created for theme '{theme}' and performance '{performance}'")
            return results
            
        except Exception as e:
            self.logger.error(f"Error creating customizations: {e}")
            return NoneArch Linux Customizer for Termux PXE Boot
Creates Kali-like UI and performance optimizations for Arch Linux installations
"""
import os
import shutil
import subprocess
from pathlib import Path

class ArchCustomizer:
    def __init__(self, settings=None, logger=None):
        self.settings = settings
        self.logger = logger
        self.assets_dir = "/data/data/com.termux/files/home/pxe_assets"
        self.customizer_dir = os.path.join(self.assets_dir, "customizer")
        self.motd_dir = os.path.join(self.customizer_dir, "motd")
        self.config_dir = os.path.join(self.customizer_dir, "configs")
        self.scripts_dir = os.path.join(self.customizer_dir, "scripts")
        self.themes_dir = os.path.join(self.customizer_dir, "themes")
        self.performance_dir = os.path.join(self.customizer_dir, "performance")
        
        # Create directory structure
        self._create_directory_structure()
        
    def _create_directory_structure(self):
        """Create the directory structure for customizations"""
        directories = [
            self.customizer_dir,
            self.motd_dir,
            self.config_dir,
            self.scripts_dir,
            self.themes_dir,
            self.performance_dir,
            os.path.join(self.config_dir, "i3"),
            os.path.join(self.config_dir, "zsh"),
            os.path.join(self.config_dir, "vim"),
            os.path.join(self.config_dir, "terminal"),
            os.path.join(self.themes_dir, "gtk"),
            os.path.join(self.themes_dir, "icons"),
            os.path.join(self.performance_dir, "kernel"),
            os.path.join(self.performance_dir, "services")
        ]
        
        for directory in directories:
            os.makedirs(directory, exist_ok=True)
            
        self.logger.info("Customizer directory structure created")
        
    def create_enhanced_motd(self, theme="Kali Dark"):
        """Create enhanced message of the day with themed graphics"""
        if theme == "Kali Dark":
            motd_content = '''╔══════════════════════════════════════════════════════════════════════════════╗
║                    🐧 ARCH LINUX ENHANCED PERFORMANCE EDITION                ║
║                     Powered by Termux PXE Boot System                       ║
║              🔥 Optimized for Maximum Performance 🔥                        ║
╚══════════════════════════════════════════════════════════════════════════════╝

⚡ System Status: Enhanced Performance Mode
🎯 Kali Tools: Pre-installed and Ready
🚀 Network: PXE Boot Compatible
🛡️  Security: Hardened Configuration

Welcome to your custom Arch Linux installation!
'''
        elif theme == "Cyberpunk":
            motd_content = '''╔══════════════════════════════════════════════════════════════════════════════╗
║                 🌈 CYBERPUNK ARCH LINUX PERFORMANCE EDITION 🌈                ║
║                    Powered by Termux PXE Boot System                        ║
║              ⚡ NEON OPTIMIZED FOR MAXIMUM POWER ⚡                          ║
╚══════════════════════════════════════════════════════════════════════════════╝

🌃 System Status: Cyberpunk Performance Mode
🎯 Cyber Tools: Neon Enhanced and Ready
🚀 Network: Quantum PXE Boot
🛡️  Security: Digital Armor Activated

Enter the matrix... Welcome to Cyberpunk Linux!
'''
        elif theme == "Matrix":
            motd_content = '''╔══════════════════════════════════════════════════════════════════════════════╗
║                  🟢 MATRIX ARCH LINUX - CHOOSE THE PILL 🟢                   ║
║                    Powered by Termux PXE Boot System                        ║
║              ⚡ CODE IS PERFORMANCE - NO BUGS ⚡                             ║
╚══════════════════════════════════════════════════════════════════════════════╝

🟢 System Status: Matrix Performance Enabled
🎯 Tools: The Matrix Is Loaded
🚀 Network: Following The White Rabbit
🛡️  Security: Bulletproof in the Matrix

Follow the white rabbit... Welcome to the Matrix!
'''
        else:  # Neon Green
            motd_content = '''╔══════════════════════════════════════════════════════════════════════════════╗
║              ⚡ NEON GREEN ARCH LINUX - PERFORMANCE EDITION ⚡                ║
║                    Powered by Termux PXE Boot System                        ║
║              🔥 MAXIMUM PERFORMANCE - ZERO COMPROMISE 🔥                    ║
╚══════════════════════════════════════════════════════════════════════════════╝

🟢 System Status: Neon Green Performance Mode
🎯 Tools: Bright and Shining
🚀 Network: Lightning Fast
🛡️  Security: Neon Shield Active

Light up your system! Welcome to Neon Green Linux!
'''
            
        motd_path = os.path.join(self.motd_dir, "enhanced_motd")
        with open(motd_path, 'w') as f:
            f.write(motd_content)
            
        self.logger.info(f"Enhanced MOTD created for theme: {theme}")
        return motd_path
        
    def create_i3_config(self, theme="Kali Dark"):
        """Create i3 window manager configuration with themed styling"""
        i3_config = '''# i3 Configuration
# Generated by Termux PXE Boot
# Arch Linux Enhanced Performance Edition

# Key bindings
set $mod Mod4

# Font for window titles
font pango: JetBrains Mono 10

# Colors for {theme} theme
client.focused          #00ff00 #00ff00 #1a1a1a #00ff00
client.focused_inactive #2d2d2d #2d2d2d #888888 #292929
client.unfocused        #2d2d2d #2d2d2d #888888 #292929
client.urgent           #ff0000 #ff0000 #ffffff #ff0000

# Start XDG autostart
exec --no-startup-id dex --autostart --environment i3

# Gaps settings
gaps inner 5
gaps outer 5

# Workspace settings
workspace_layout default

# Border style for new windows
new_window 1pixel

# Default workspace
workspace 1 output HDMI-1

# Background
exec_always feh --bg-scale /usr/share/backgrounds/default.jpg

# Terminal
bindsym $mod+Return exec kitty

# Kill focused window
bindsym $mod+Shift+q kill

# Start rofi (drun)
bindsym $mod+d exec rofi -show drun

# Start terminal
bindsym $mod+Return exec kitty

# Volume controls
bindsym XF86AudioRaiseVolume exec amixer set Master 5%+
bindsym XF86AudioLowerVolume exec amixer set Master 5%-
bindsym XF86AudioMute exec amixer set Master toggle

# Brightness controls
bindsym XF86MonBrightnessUp exec brightnessctl set 10%+
bindsym XF86MonBrightnessDown exec brightnessctl set 10%-

# Screenshot
bindsym Print exec scrot '%Y-%m-%d-%H-%M-$wx$hx.png'
bindsym $mod+Print exec scrot -u '%Y-%m-%d-%H-%M-$wx$hx.png'

# Reload config
bindsym $mod+Shift+c reload

# Restart i3
bindsym $mod+Shift+r restart

# Exit i3
bindsym $mod+Shift+e exec "i3-nagbar -t warning -m 'Exit i3?' -b 'Yes, exit i3' 'i3-msg exit'"

# Floating toggle
floating_modifier $mod

# Move between windows
bindsym $mod+Left focus left
bindsym $mod+Down focus down
bindsym $mod+Up focus up
bindsym $mod+Right focus right

# Move windows
bindsym $mod+Shift+Left move left
bindsym $mod+Shift+Down move down
bindsym $mod+Shift+Up move up
bindsym $mod+Shift+Right move right

# Resize windows
bindsym $mod+r mode "resize"
mode "resize" {
    bindsym Left resize shrink width 10 px or 10 ppt
    bindsym Down resize grow height 10 px or 10 ppt
    bindsym Up resize shrink height 10 px or 10 ppt
    bindsym Right resize grow width 10 px or 10 ppt
    bindsym Return mode "default"
    bindsym Escape mode "default"
}

# Start i3bar
bar {
    status_command i3status
    colors {
        background #1a1a1a
        statusline #00ff00
        focused_workspace #00ff00 #00ff00 #1a1a1a
        active_workspace #2d2d2d #2d2d2d #00ff00
        inactive_workspace #2d2d2d #2d2d2d #888888
        urgent_workspace #ff0000 #ff0000 #ffffff
    }
}

# Kali-specific bindings
# Network scanning
bindsym $mod+n exec nmap 192.168.1.0/24
# Port scanning
bindsym $mod+p exec nmap -sV -O $(hostname -I | awk '{print $1}')
# System info
bindsym $mod+i exec htop
# File manager
bindsym $mod+e exec ranger

# Auto-start services
exec_always polybar
exec_always network-manager-applet
exec_always feh --bg-scale /usr/share/backgrounds/default.jpg
        '''.format(theme=theme)
        
        i3_config_path = os.path.join(self.config_dir, "i3", "config")
        with open(i3_config_path, 'w') as f:
            f.write(i3_config)
            
        self.logger.info("i3 configuration created")
        return i3_config_path
        
    def create_zsh_config(self, theme="Kali Dark"):
        """Create ZSH configuration with Kali-like aliases and themes"""
        zsh_config = '''# ZSH Configuration
# Generated by Termux PXE Boot
# Arch Linux Enhanced Performance Edition

# Path to oh-my-zsh
ZSH="$HOME/.oh-my-zsh"

# Theme
ZSH_THEME="agnoster"

# Oh-my-zsh plugins
plugins=(
    git
    sudo
    docker
    python
    pip
    colored-man-pages
    zsh-autosuggestions
    zsh-syntax-highlighting
)

# Environment variables
export EDITOR="vim"
export VISUAL="vim"
export TERM="xterm-256color"

# Aliases for Kali-like experience
alias ..='cd ..'
alias ...='cd ../..'
alias ls='ls --color=auto'
alias ll='ls -la --color=auto'
alias l='ls --color=auto -la'
alias la='ls -la --color=auto'
alias grep='grep --color=auto'
alias fgrep='fgrep --color=auto'
alias egrep='egrep --color=auto'
alias diff='colordiff'
alias tailf='tail -f'

# Kali-style aliases
alias kali-update='sudo pacman -Syu'
alias kali-upgrade='sudo pacman -Syyu'
alias kali-clean='sudo pacman -Scc'
alias kali-install='sudo pacman -S'
alias kali-remove='sudo pacman -Rns'
alias kali-search='sudo pacman -Ss'
alias kali-info='sudo pacman -Si'
alias kali-orphans='sudo pacman -Rns $(pacman -Qqdt)'

# System control aliases
alias restart='sudo reboot'
alias shutdown='sudo poweroff'
alias hibernate='sudo systemctl hibernate'
alias suspend='sudo systemctl suspend'
alias status='systemctl status'
alias services='systemctl list-units --type=service --state=running'

# Network aliases
alias netstat='ss -tuln'
alias ports='ss -tuln'
alias ipinfo='ip addr show'
alias myip='curl -s ifconfig.me'
alias whois='whois $(myip)'

# Security and penetration testing
alias nmap-scan='nmap -sS -O -A'
alias port-scan='nmap -sV -sC'
alias network-scan='nmap -sn 192.168.1.0/24'
alias vulnerability-scan='nikto -h http://localhost'

# Performance monitoring
alias cpuinfo='lscpu'
alias meminfo='free -h'
alias diskinfo='df -h'
alias topproc='ps aux --sort=-%mem | head -10'
alias networkio='nethogs -d 1'

# Development aliases
alias py='python3'
alias pip-upgrade='pip install --upgrade pip'
alias git-sync='git fetch origin && git merge origin/main'
alias git-push='git push origin main'
alias git-pull='git pull origin main'

# Quick editing
alias v='vim'
alias sv='sudo vim'
alias nano='micro'
alias edit-zsh='v ~/.zshrc'
alias reload-zsh='source ~/.zshrc'

# Entertainment and extras
alias matrix='cmatrix -a -b -C green -s 60'
alias cowsay='cowsay -f tux'
alias figlet-banner='figlet'
alias ascii-art='toilet --gay'

# Function definitions
kali-help() {
    echo "🐧 Kali-Style Commands Available:"
    echo "k-...     = Kali command shortcuts"
    echo "net-...   = Network commands"
    echo "sys-...   = System commands"
    echo "dev-...   = Development commands"
    echo ""
    echo "Type 'alias' to see all available aliases"
}

# Function to show system information
sys-info() {
    echo "🖥️  System Information:"
    echo "OS: $(uname -o)"
    echo "Kernel: $(uname -r)"
    echo "Uptime: $(uptime -p)"
    echo "Memory: $(free -h | grep Mem | awk '{print $2}') total"
    echo "CPU: $(lscpu | grep "Model name" | cut -d: -f2 | xargs)"
    echo "Disk: $(df -h / | tail -1 | awk '{print $2}') total"
}

# Function for network scanning
net-scan() {
    if [ $# -eq 0 ]; then
        nmap -sn 192.168.1.0/24
    else
        nmap -sn $1
    fi
}

# Load oh-my-zsh
source $ZSH/oh-my-zsh.sh

# Custom prompt
export PS1='%F{green}%n@%m%f %F{blue}%1~%f %# '

# Case-insensitive completion
zstyle ':completion:*' matcher-list 'm:{a-zA-Z}={A-Za-z}'

# Enable color for man pages
export MANPAGER='most'

# History settings
HISTSIZE=10000
SAVEHIST=10000
HISTFILE=~/.zsh_history

# Load auto-suggestions
source /usr/share/zsh/plugins/zsh-autosuggestions/zsh-autosuggestions.zsh 2>/dev/null
source /usr/share/zsh/plugins/zsh-syntax-highlighting/zsh-syntax-highlighting.zsh 2>/dev/null
        '''
        
        zsh_config_path = os.path.join(self.config_dir, "zsh", "zshrc")
        with open(zsh_config_path, 'w') as f:
            f.write(zsh_config)
            
        self.logger.info("ZSH configuration created")
        return zsh_config_path
        
    def create_vim_config(self, theme="Kali Dark"):
        """Create Vim configuration with programming enhancements"""
        vim_config = '''" Vim Configuration
" Generated by Termux PXE Boot
" Arch Linux Enhanced Performance Edition

" Basic settings
set nocompatible
syntax on
filetype plugin indent on

" Display settings
set number
set relativenumber
set cursorline
set cursorcolumn
set showcmd
set ruler
set laststatus=2
set wildmenu
set showmatch

" Indentation
set tabstop=4
set shiftwidth=4
set expandtab
set smarttab
set autoindent
set smartindent

" Search settings
set incsearch
set hlsearch
set ignorecase
set smartcase
set gdefault

" Clipboard
set clipboard=unnamedplus

" Encoding
set encoding=utf-8
set fileencoding=utf-8

" Backup and swap files
set backup
set backupdir=~/.vim/backup
set directory=~/.vim/swp
set undofile
set undodir=~/.vim/undo

" Color scheme
colorscheme desert
set background=dark

" Key mappings
" Leader key
let mapleader = ","

" Navigation
nnoremap <C-h> <C-w>h
nnoremap <C-j> <C-w>j
nnoremap <C-k> <C-w>k
nnoremap <C-l> <C-w>l

" Split navigation
nnoremap <C-Left> <C-w>h
nnoremap <C-Down> <C-w>j
nnoremap <C-Up> <C-w>k
nnoremap <C-Right> <C-w>l

" Split commands
nnoremap <Leader>v :vsplit<CR>
nnoremap <Leader>h :split<CR>

" File operations
nnoremap <Leader>s :w<CR>
nnoremap <Leader>q :q<CR>
nnoremap <Leader>wq :wq<CR>
nnoremap <Leader>w :w<CR>
nnoremap <Leader>q! :q!<CR>

" Tab management
nnoremap <Leader>tn :tabnew<CR>
nnoremap <Leader>tc :tabclose<CR>
nnoremap <Leader>to :tabonly<CR>
nnoremap <Leader>tp :tabprev<CR>
nnoremap <Leader>tn :tabnext<CR>

" Code folding
set foldmethod=indent
set foldlevel=99
nnoremap <space> za

" Buffer navigation
nnoremap <Leader>bn :bnext<CR>
nnoremap <Leader>bp :bprevious<CR>
nnoremap <Leader>bd :bdelete<CR>

" Visual mode improvements
vnoremap < <gv
vnoremap > >gv

" Copy/paste
vnoremap <Leader>y "+y
nnoremap <Leader>p "+p
nnoremap <Leader>P "+P

" Terminal shortcuts
nnoremap <Leader>tt :terminal<CR>

" File explorer
nnoremap <Leader>e :Vexplore<CR>

" Comment/uncomment
vnoremap <Leader>/ :s/^/\/\//g<CR>:noh<CR>
vnoremap <Leader>\\ :s/^\/\///g<CR>:noh<CR>

" Quick run
nnoremap <Leader>r :!%:p<CR>

" Clear search
nnoremap <Leader>c :nohlsearch<CR>

" Kali-specific shortcuts
nnoremap <Leader>ka :!echo "Kali Mode Activated!"<CR>
nnoremap <Leader>kn :!nmap -sV -O $(echo $IP)<CR>
nnoremap <Leader>ks :!sudo systemctl status<CR>

" Plugin settings (if vim-plug is available)
if empty(glob('~/.vim/autoload/plug.vim'))
  silent !curl -fLo ~/.vim/autoload/plug.vim --create-dirs
    \ https://raw.githubusercontent.com/junegunn/vim-plug/master/plug.vim
  autocmd VimEnter * PlugInstall --sync | source $MYVIMRC
endif

" Plugin declarations
call plug#begin('~/.vim/plugged')

" Essential plugins
Plug 'tpope/vim-fugitive'        " Git wrapper
Plug 'tpope/vim-surround'        " Surround text objects
Plug 'tpope/vim-repeat'          " Repeat plugin commands
Plug 'jiangmiao/auto-pairs'      " Auto pairs for brackets
Plug 'dense-analysis/ale'        " Linting
Plug 'vim-airline/vim-airline'  " Status line
Plug 'vim-airline/vim-airline-themes' " Airline themes
Plug 'morhetz/gruvbox'          " Gruvbox color scheme
Plug 'dracula/vim'              " Dracula color scheme
Plug 'arcticicestudio/nord-vim' " Nord color scheme

" Programming language support
Plug 'fatih/vim-go'             " Go support
Plug 'davidhalter/jedi-vim'     " Python support
Plug 'pangloss/vim-javascript'  " JavaScript support
Plug 'posva/vim-vue'            " Vue.js support
Plug 'stephpy/vim-yaml'         " YAML support
Plug 'zhimsel/vim-stay'         " Keep cursor position

" Call plug#end()

" Airline configuration
let g:airline_theme='dark'
let g:airline_powerline_fonts=1

" Auto-pairs settings
let g:AutoPairsMapSpace=0

" ALE settings
let g:ale_linters = {
\   'python': ['flake8', 'pylint'],
\   'javascript': ['eslint'],
\   'go': ['go', 'golint']
\}
let g:ale_fixers = {
\   'python': ['black', 'isort'],
\   'javascript': ['prettier'],
\   'go': ['gofmt']
\}

" Python specific settings
autocmd FileType python setlocal shiftwidth=4 tabstop=4
autocmd FileType python setlocal number
autocmd FileType python setlocal relativenumber

" Go specific settings
autocmd FileType go setlocal shiftwidth=4 tabstop=4
autocmd FileType go setlocal number
autocmd FileType go setlocal relativenumber

" Custom commands
command! -nargs=0 Swap :call Swap()
function! Swap()
    if expand('%:e') == 'py'
        s/\.py$/.py.bak/
    elseif expand('%:e') == 'js'
        s/\.js$/.js.bak/
    endif
endfunction

" Quick file templates
autocmd BufNewFile *.py 0r ~/.vim/templates/python.py
autocmd BufNewFile *.sh 0r ~/.vim/templates/shell.sh
autocmd BufNewFile *.js 0r ~/.vim/templates/javascript.js

" Performance settings
set lazyredraw
set ttyfast
set ttyscroll=3

" Remember folds
autocmd BufWinLeave * mkview
autocmd BufWinEnter * silent loadview

" Word completion
set completeopt=menuone,menu,longest,preview

" Recalculate screen size when resizing
au VimResized * :wincmd =

" Highlight current line
set cursorline
hi CursorLine ctermbg=darkgray

" Set working directory to file location
autocmd BufEnter * cd %:p:h

" Auto save and load sessions
autocmd VimLeave * mksession! ~/.vim/session.vim
autocmd VimEnter * silent source ~/.vim/session.vim
        '''
        
        vim_config_path = os.path.join(self.config_dir, "vim", "vimrc")
        with open(vim_config_path, 'w') as f:
            f.write(vim_config)
            
        self.logger.info("Vim configuration created")
        return vim_config_path
        
    def create_performance_configs(self, profile="Maximum"):
        """Create performance optimization configurations"""
        configs = {}
        
        # Kernel tuning
        kernel_sysctl = '''# Kernel performance tuning
# Generated by Termux PXE Boot

# Network performance
net.core.rmem_max = 134217728
net.core.wmem_max = 134217728
net.core.netdev_max_backlog = 5000
net.ipv4.tcp_rmem = 4096 65536 134217728
net.ipv4.tcp_wmem = 4096 65536 134217728
net.ipv4.tcp_congestion_control = bbr

# Memory management
vm.swappiness = 10
vm.dirty_ratio = 3
vm.dirty_background_ratio = 2
vm.vfs_cache_pressure = 50
vm.dirty_expire_centisecs = 3000
vm.dirty_writeback_centisecs = 500

# I/O scheduler
block.sda.scheduler = noop

# CPU scheduling
kernel.sched_migration_cost_ns = 5000000
kernel.sched_min_granularity_ns = 15000000
kernel.sched_wakeup_granularity_ns = 2000000

# File system
fs.file-max = 2097152
fs.inotify.max_user_watches = 524288
        '''
        
        kernel_config_path = os.path.join(self.performance_dir, "kernel", "sysctl.conf")
        with open(kernel_config_path, 'w') as f:
            f.write(kernel_sysctl)
        configs['kernel'] = kernel_config_path
        
        # Service optimization
        service_optimization = '''# Systemd service optimization
# Generated by Termux PXE Boot

[Unit]
Description=Performance Optimization Service
After=network.target

[Service]
Type=oneshot
RemainAfterExit=yes
ExecStart=/usr/bin/systemctl set-default multi-user.target
ExecStart=/usr/bin/systemctl enable NetworkManager
ExecStart=/usr/bin/systemctl disable bluetooth
ExecStart=/usr/bin/systemctl disable cups
ExecStart=/usr/bin/systemctl disable avahi-daemon
ExecStart=/usr/bin/systemctl disable ModemManager

[Install]
WantedBy=multi-user.target
        '''
        
        service_config_path = os.path.join(self.performance_dir, "services", "optimization.service")
        with open(service_config_path, 'w') as f:
            f.write(service_optimization)
        configs['service'] = service_config_path
        
        self.logger.info("Performance configurations created")
        return configs
        
    def create_pacman_optimization(self):
        """Create pacman mirrorlist and configuration for optimal performance"""
        pacman_config = '''# Pacman configuration
# Generated by Termux PXE Boot

# System architecture
Architecture = auto

# Color output
Color
ILoveCandy

# Verbose package lists
VerbosePkgLists

# Parallel downloads
ParallelDownloads = 8

# Display progress bar and current action
EnableSysLog

# Check space
CheckSpace

# Database sync
Refresh

# Architecture
Architecture = x86_64

# Include configuration
Include = /etc/pacman.d/mirrorlist

# SigLevel
SigLevel = Never
LocalFileSigLevel = Optional

# Options
HoldPkg = pacman glibc
CacheDir = /var/cache/pacman/pkg
LogFile = /var/log/pacman.log
GPGDir = /etc/pacman.d/gnupg/
ConfigFile = /etc/pacman.conf
RootDir = /
        '''
        
        mirrorlist = '''# Mirrorlist
# Generated by Termux PXE Boot
# Optimized for performance

Server = https://mirrors.kernel.org/archlinux/$repo/os/$arch
Server = https://archlinux.bridge.de/archlinux/$repo/os/$arch
Server = https://mirror.zerobyte.com.au/archlinux/$repo/os/$arch
Server = https://mirror.f4st.host/archlinux/$repo/os/$arch
Server = https://archlinux.thaller.ws/$repo/os/$arch
        '''
        
        pacman_config_path = os.path.join(self.config_dir, "pacman", "pacman.conf")
        pacman_dir = os.path.dirname(pacman_config_path)
        os.makedirs(pacman_dir, exist_ok=True)
        with open(pacman_config_path, 'w') as f:
            f.write(pacman_config)
            
        mirrorlist_path = os.path.join(pacman_dir, "mirrorlist")
        with open(mirrorlist_path, 'w') as f:
            f.write(mirrorlist)
            
        self.logger.info("Pacman optimization files created")
        return {
            'config': pacman_config_path,
            'mirrorlist': mirrorlist_path
        }
        
    def create_bashrc_enhancement(self, theme="Kali Dark"):
        """Create enhanced .bashrc with performance and styling"""
        bashrc_content = '''# Enhanced .bashrc
# Generated by Termux PXE Boot
# Arch Linux Enhanced Performance Edition

# System information function
sysinfo() {
    echo "🖥️  System Status:"
    echo "OS: $(uname -o)"
    echo "Kernel: $(uname -r)"
    echo "Uptime: $(uptime -p)"
    echo "Load: $(uptime | awk -F'load average:' '{ print $2 }')"
    echo "Memory: $(free -h | grep Mem | awk '{print $2}') total, $(free -h | grep Mem | awk '{print $3}') used"
    echo "Disk: $(df -h / | tail -1 | awk '{print $2}') total, $(df -h / | tail -1 | awk '{print $3}') used"
    echo "Temperature: $(sensors | grep 'Core 0' | awk '{print $3}')"
}

# Network information function
netinfo() {
    echo "🌐 Network Status:"
    echo "IP Address: $(curl -s ifconfig.me)"
    echo "External IP: $(curl -s ipinfo.io/ip)"
    echo "Location: $(curl -s ipinfo.io/$(curl -s ifconfig.me)/city 2>/dev/null) - $(curl -s ipinfo.io/$(curl -s ifconfig.me)/country 2>/dev/null)"
    echo "ISP: $(curl -s ipinfo.io/$(curl -s ifconfig.me)/org 2>/dev/null)"
}

# Quick system monitor
monitor() {
    echo "📊 System Monitor:"
    top -bn1 | head -5
    echo ""
    free -h
}

# Kali-style color prompt
if [[ ${EUID} == 0 ]]; then
    PS1="\[\033[01;31m\]\h\[\033[01;34m\] \w \$\[\033[00m\] "
else
    PS1="\[\033[01;32m\]\u@\h\[\033[01;34m\] \w \$\[\033[00m\] "
fi

# Disable the bell
if [[ $PS1 && -f /usr/share/bash-completion/bash_completion ]]; then
    . /usr/share/bash-completion/bash_completion
fi

# Command history
export HISTSIZE=10000
export HISTFILESIZE=20000
export HISTCONTROL=ignoredups:erasedups
export HISTTIMEFORMAT="[%F %T] "
export PROMPT_COMMAND='history -a'

# Color support
alias grep='grep --color=auto'
alias fgrep='fgrep --color=auto'
alias egrep='egrep --color=auto'
alias ls='ls --color=auto'
alias ll='ls -la --color=auto'
alias la='ls -A --color=auto'
alias l='ls -CF --color=auto'

# Kali command shortcuts
alias kali-update='sudo pacman -Syu'
alias kali-upgrade='sudo pacman -Syyu'
alias kali-clean='sudo pacman -Scc'
alias kali-install='sudo pacman -S'
alias kali-remove='sudo pacman -Rns'
alias kali-search='sudo pacman -Ss'
alias kali-info='sudo pacman -Si'

# System control
alias restart='sudo reboot'
alias shutdown='sudo poweroff'
alias hibernate='sudo systemctl hibernate'
alias suspend='sudo systemctl suspend'

# Network commands
alias ports='ss -tuln'
alias myip='curl -s ifconfig.me'
alias netstat='ss -tuln'

# Performance monitoring
alias cpu='lscpu'
alias mem='free -h'
alias disk='df -h'
alias topproc='ps aux --sort=-%mem | head -10'

# Development shortcuts
alias py='python3'
alias pipup='pip install --upgrade pip'
alias gitsync='git fetch origin && git merge origin/main'
alias gitpush='git push origin main'
alias gitpull='git pull origin main'

# Security and network scanning
alias nmap-scan='nmap -sS -O -A'
alias port-scan='nmap -sV -sC'
alias network-scan='nmap -sn 192.168.1.0/24'
alias vuln-scan='nikto -h http://localhost'

# Quick text editing
alias v='vim'
alias nano='micro'
alias edit-bash='v ~/.bashrc'
alias reload-bash='source ~/.bashrc'

# Fun commands
alias matrix='cmatrix -a -b -C green -s 60'
alias cowsay='cowsay -f tux'
alias figlet='toilet --gay'

# Function to show help
kali-help() {
    echo "🐧 Available Kali-style commands:"
    echo "k-...     : Kali system commands"
    echo "net-...   : Network commands"
    echo "sys-...   : System monitoring"
    echo "dev-...   : Development tools"
    echo ""
    echo "Type 'alias' to see all available shortcuts"
}

# Welcome message
echo "⚡ Welcome to Arch Linux Enhanced Performance Edition!"
echo "Type 'sysinfo' for system information"
echo "Type 'netinfo' for network information"
echo "Type 'kali-help' for command help"
        '''
        
        bashrc_path = os.path.join(self.config_dir, "bash", "bashrc")
        bash_dir = os.path.dirname(bashrc_path)
        os.makedirs(bash_dir, exist_ok=True)
        with open(bashrc_path, 'w') as f:
            f.write(bashrc_content)
            
        self.logger.info("Enhanced bashrc created")
        return bashrc_path
        
    def create_all_customizations(self, theme="Kali Dark", performance="Maximum"):
        """Create all customization files for a complete installation"""
        try:
            results = {}
            
            # Create all customization files
            results['motd'] = self.create_enhanced_motd(theme)
            results['i3_config'] = self.create_i3_config(theme)
            results['zsh_config'] = self.create_zsh_config(theme)
            results['vim_config'] = self.create_vim_config(theme)
            results['bashrc'] = self.create_bashrc_enhancement(theme)
            results['performance'] = self.create_performance_configs(performance)
            results['pacman'] = self.create_pacman_optimization()
            
            self.logger.info(f"All customizations created for theme '{theme}' and performance '{performance}'")
            return results
            
        except Exception as e:
            self.logger.error(f"Error creating customizations: {e}")
            return None
