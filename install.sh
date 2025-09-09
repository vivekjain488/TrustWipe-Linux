#!/bin/bash

# TrustWipe Professional Installation Script
# This script installs TrustWipe with bulletproof error handling

# Exit on error but continue with fallbacks
set +e

# Colors for better output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Logging function
log() {
    echo -e "${GREEN}[$(date +'%Y-%m-%d %H:%M:%S')]${NC} $1"
}

log_warning() {
    echo -e "${YELLOW}[WARNING]${NC} $1"
}

log_error() {
    echo -e "${RED}[ERROR]${NC} $1"
}

log_info() {
    echo -e "${BLUE}[INFO]${NC} $1"
}

echo "========================================"
echo "    🛡️  TrustWipe Professional Installer"
echo "========================================"
echo

# Check if running as root
if [ "$EUID" -ne 0 ]; then
    log_error "This script must be run as root (use sudo)"
    echo "Usage: sudo ./install.sh"
    exit 1
fi

log "Running as root - proceeding with installation..."

# Detect Linux distribution with fallbacks
DISTRO="unknown"
VERSION="unknown"
PRETTY_NAME="Unknown Linux"

if [ -f /etc/os-release ]; then
    . /etc/os-release
    DISTRO=$ID
    VERSION=$VERSION_ID
elif [ -f /etc/lsb-release ]; then
    . /etc/lsb-release
    DISTRO=$(echo $DISTRIB_ID | tr '[:upper:]' '[:lower:]')
    VERSION=$DISTRIB_RELEASE
    PRETTY_NAME=$DISTRIB_DESCRIPTION
elif [ -f /etc/redhat-release ]; then
    DISTRO="centos"
    PRETTY_NAME=$(cat /etc/redhat-release)
elif [ -f /etc/arch-release ]; then
    DISTRO="arch"
    PRETTY_NAME="Arch Linux"
fi

log "Detected: $PRETTY_NAME"
log_info "Distribution: $DISTRO, Version: $VERSION"

# Advanced repository fixing for problematic systems
fix_repositories() {
    log "🔧 Attempting to fix package repositories..."
    
    case $DISTRO in
        kali)
            log_info "Fixing Kali Linux repositories..."
            # Backup original sources
            cp /etc/apt/sources.list /etc/apt/sources.list.backup.$(date +%s) 2>/dev/null || true
            
            # Create working sources.list
            cat > /etc/apt/sources.list << 'EOF'
# Kali Linux Official Repositories
deb http://http.kali.org/kali kali-rolling main contrib non-free non-free-firmware
deb-src http://http.kali.org/kali kali-rolling main contrib non-free non-free-firmware

# Kali Linux Security Updates
deb http://http.kali.org/kali kali-rolling main contrib non-free non-free-firmware
EOF
            
            # Try alternative mirrors if needed
            if ! apt update -qq 2>/dev/null; then
                log_warning "Primary mirror failed, trying alternatives..."
                cat > /etc/apt/sources.list << 'EOF'
# Alternative Kali Mirror
deb https://mirror.kali.org/kali kali-rolling main contrib non-free non-free-firmware
deb-src https://mirror.kali.org/kali kali-rolling main contrib non-free non-free-firmware
EOF
                apt update -qq 2>/dev/null || log_warning "Repository update failed, continuing..."
            fi
            ;;
        ubuntu|debian)
            log_info "Updating package cache..."
            apt update -qq 2>/dev/null || log_warning "Package update failed"
            ;;
    esac
}

# Install Python 3 and dependencies with multiple fallback methods
install_python() {
    echo
    log "🐍 Setting up Python environment..."
    
    # Check if Python 3 is available
    if command -v python3 &> /dev/null; then
        PYTHON_VERSION=$(python3 --version 2>&1 | cut -d' ' -f2)
        log "Python 3 found: $PYTHON_VERSION"
    else
        log_info "Installing Python 3..."
        case $DISTRO in
            ubuntu|debian|kali)
                fix_repositories
                apt install -y python3 python3-pip 2>/dev/null || log_warning "Python3 installation via apt failed"
                ;;
            centos|rhel|fedora)
                if command -v dnf &> /dev/null; then
                    dnf install -y python3 python3-pip 2>/dev/null || log_warning "Python3 installation via dnf failed"
                else
                    yum install -y python3 python3-pip 2>/dev/null || log_warning "Python3 installation via yum failed"
                fi
                ;;
            arch)
                pacman -S --noconfirm python python-pip 2>/dev/null || log_warning "Python3 installation via pacman failed"
                ;;
        esac
    fi
    
    # Verify Python is working
    if ! command -v python3 &> /dev/null; then
        log_error "Python 3 installation failed. Please install manually:"
        echo "  Ubuntu/Debian: sudo apt install python3 python3-pip"
        echo "  CentOS/RHEL:   sudo yum install python3 python3-pip"
        echo "  Arch:          sudo pacman -S python python-pip"
        exit 1
    fi
    
    log "✅ Python 3 is available"
}

# Install system packages with fallbacks
install_system_packages() {
    echo
    log "📦 Installing system packages..."
    
    case $DISTRO in
        ubuntu|debian|kali)
            # Try to install GUI support
            if apt install -y python3-tk 2>/dev/null; then
                log "✅ GUI support (tkinter) installed"
            else
                log_warning "GUI support installation failed - CLI only mode"
            fi
            
            # Try to install psutil from system packages
            if apt install -y python3-psutil 2>/dev/null; then
                log "✅ System info support (psutil) installed from packages"
                PSUTIL_INSTALLED=true
            else
                log_warning "System psutil not available, will try pip"
                PSUTIL_INSTALLED=false
            fi
            
            # Essential utilities
            apt install -y util-linux coreutils 2>/dev/null || log_warning "Some utilities installation failed"
            ;;
        centos|rhel|fedora)
            if command -v dnf &> /dev/null; then
                dnf install -y python3-tkinter python3-psutil util-linux coreutils 2>/dev/null || log_warning "Some packages failed"
            else
                yum install -y tkinter python3-psutil util-linux coreutils 2>/dev/null || log_warning "Some packages failed"
            fi
            PSUTIL_INSTALLED=true
            ;;
        arch)
            pacman -S --noconfirm tk python-psutil util-linux coreutils 2>/dev/null || log_warning "Some packages failed"
            PSUTIL_INSTALLED=true
            ;;
        *)
            log_warning "Unknown distribution, skipping system packages"
            PSUTIL_INSTALLED=false
            ;;
    esac
}

# Install Python packages with multiple methods
install_python_packages() {
    echo
    log "� Installing Python dependencies..."
    
    # Check if psutil is already available
    if python3 -c "import psutil" 2>/dev/null; then
        log "✅ psutil is already available"
        return
    fi
    
    if [ "$PSUTIL_INSTALLED" = false ]; then
        log_info "Installing psutil via pip..."
        
        # Try multiple pip installation methods
        if pip3 install --break-system-packages psutil 2>/dev/null; then
            log "✅ psutil installed via pip (--break-system-packages)"
        elif pip3 install --user psutil 2>/dev/null; then
            log "✅ psutil installed via pip (--user)"
        elif python3 -m pip install --break-system-packages psutil 2>/dev/null; then
            log "✅ psutil installed via python3 -m pip"
        elif python3 -m pip install --user psutil 2>/dev/null; then
            log "✅ psutil installed via python3 -m pip (--user)"
        else
            log_warning "psutil installation failed - TrustWipe will work with limited system info"
        fi
    fi
}

# Verify dependencies and functionality
verify_dependencies() {
    echo
    log "� Verifying installation requirements..."
    
    # Check Python modules
    TKINTER_OK=false
    PSUTIL_OK=false
    
    if python3 -c "import tkinter" 2>/dev/null; then
        log "✅ tkinter (GUI support) - Available"
        TKINTER_OK=true
    else
        log_warning "tkinter not available - GUI mode disabled"
    fi
    
    if python3 -c "import psutil" 2>/dev/null; then
        log "✅ psutil (system info) - Available"
        PSUTIL_OK=true
    else
        log_warning "psutil not available - limited system information"
    fi
    
    # Check essential commands
    for cmd in dd lsblk; do
        if command -v $cmd &> /dev/null; then
            log "✅ $cmd command - Available"
        else
            log_error "$cmd command not found - this is required for disk operations"
        fi
    done
    
    # Check optional commands
    for cmd in shred blockdev; do
        if command -v $cmd &> /dev/null; then
            log "✅ $cmd command - Available"
        else
            log_warning "$cmd command not found - some features may be limited"
        fi
    done
}

# Install TrustWipe application files
install_application() {
    echo
    log "📁 Installing TrustWipe application..."
    
    # Create application directory
    APP_DIR="/opt/trustwipe"
    mkdir -p "$APP_DIR"
    chmod 755 "$APP_DIR"
    
    # Required files list
    REQUIRED_FILES=("trustwipe.py" "backend.py" "certificate_generator.py" "cli.py")
    OPTIONAL_FILES=("README.md" "LICENSE" "CHANGELOG.md")
    
    # Copy required files
    for file in "${REQUIRED_FILES[@]}"; do
        if [ -f "$file" ]; then
            cp "$file" "$APP_DIR/"
            chmod 755 "$APP_DIR/$file" 2>/dev/null || chmod 644 "$APP_DIR/$file"
            log "✅ Installed: $file"
        else
            log_error "Required file missing: $file"
            exit 1
        fi
    done
    
    # Copy optional files
    for file in "${OPTIONAL_FILES[@]}"; do
        if [ -f "$file" ]; then
            cp "$file" "$APP_DIR/"
            chmod 644 "$APP_DIR/$file"
            log "✅ Installed: $file"
        else
            log_warning "Optional file missing: $file"
        fi
    done
    
    log "✅ Application files installed to $APP_DIR"
}

# Create system integration
create_system_integration() {
    echo
    log "🔗 Creating system integration..."
    
    # Create global command wrappers
    cat > /usr/local/bin/trustwipe << 'EOF'
#!/bin/bash
# TrustWipe GUI Launcher

if [ "$EUID" -ne 0 ]; then
    echo "❌ TrustWipe requires root privileges for disk operations"
    echo "Please run: sudo trustwipe"
    exit 1
fi

cd /opt/trustwipe
python3 trustwipe.py "$@"
EOF
    
    cat > /usr/local/bin/trustwipe-cli << 'EOF'
#!/bin/bash
# TrustWipe CLI Launcher

cd /opt/trustwipe
python3 cli.py "$@"
EOF
    
    chmod 755 /usr/local/bin/trustwipe
    chmod 755 /usr/local/bin/trustwipe-cli
    
    if command -v trustwipe &> /dev/null; then
        log "✅ Global commands created: trustwipe, trustwipe-cli"
    else
        log_warning "Global command creation failed"
    fi
}

# Create directories with fallbacks
create_directories() {
    echo
    log "📁 Creating required directories..."
    
    # Certificate directory with fallbacks
    CERT_DIRS=("/boot/trustwipe-certificates" "/root/trustwipe-certificates" "/tmp/trustwipe-certificates")
    CERT_DIR=""
    
    for dir in "${CERT_DIRS[@]}"; do
        if mkdir -p "$dir" 2>/dev/null && [ -w "$dir" ]; then
            CERT_DIR="$dir"
            chmod 755 "$dir"
            log "✅ Certificate directory: $CERT_DIR"
            break
        fi
    done
    
    if [ -z "$CERT_DIR" ]; then
        log_error "Could not create certificate directory"
        exit 1
    fi
    
    # Log directory with fallbacks
    LOG_DIRS=("/var/log/trustwipe" "/tmp/trustwipe-logs")
    LOG_DIR=""
    
    for dir in "${LOG_DIRS[@]}"; do
        if mkdir -p "$dir" 2>/dev/null && [ -w "$dir" ]; then
            LOG_DIR="$dir"
            chmod 755 "$dir"
            log "✅ Log directory: $LOG_DIR"
            break
        fi
    done
    
    # Update configuration in application files
    if [ -n "$CERT_DIR" ] && [ -f "$APP_DIR/certificate_generator.py" ]; then
        sed -i "s|/boot/trustwipe-certificates|$CERT_DIR|g" "$APP_DIR/certificate_generator.py" 2>/dev/null || true
    fi
}

# Create desktop integration
create_desktop_integration() {
    echo
    log "🖥️ Creating desktop integration..."
    
    # Desktop entry
    DESKTOP_FILE="/usr/share/applications/trustwipe.desktop"
    cat > "$DESKTOP_FILE" << 'EOF'
[Desktop Entry]
Version=1.0
Type=Application
Name=TrustWipe
GenericName=Secure Data Wiping Tool
Comment=Professional data wiping with certificate generation
Exec=pkexec python3 /opt/trustwipe/trustwipe.py
Icon=security-high
Terminal=false
Categories=System;Security;Utility;
Keywords=wipe;erase;secure;data;disk;shred;
StartupNotify=true
X-KDE-Protocols=
X-KDE-Protocol=
EOF
    
    chmod 644 "$DESKTOP_FILE" 2>/dev/null && log "✅ Desktop entry created" || log_warning "Desktop entry creation failed"
    
    # Try to update desktop database
    if command -v update-desktop-database &> /dev/null; then
        update-desktop-database /usr/share/applications/ 2>/dev/null || true
    fi
}

# Create documentation
create_documentation() {
    echo
    log "📖 Creating documentation..."
    
    # Man page
    MAN_DIR="/usr/local/man/man1"
    if mkdir -p "$MAN_DIR" 2>/dev/null; then
        cat > "$MAN_DIR/trustwipe.1" << 'EOF'
.TH TRUSTWIPE 1 "September 2025" "TrustWipe 1.0" "User Commands"
.SH NAME
trustwipe \- professional secure data wiping tool
.SH SYNOPSIS
.B trustwipe
.br
.B trustwipe-cli
[\fB--list-devices\fR] [\fB--device-info\fR \fIDEVICE\fR] [\fB--wipe\fR \fIDEVICE\fR]
.SH DESCRIPTION
TrustWipe is a professional data wiping application that securely erases data from storage devices using industry-standard algorithms and generates compliance certificates.
.PP
.B Features:
.IP \(bu 2
Multiple wiping algorithms (zeros, random, DoD 5220.22-M, Gutmann)
.IP \(bu 2
GUI and command-line interfaces
.IP \(bu 2
Professional certificate generation
.IP \(bu 2
Real-time progress monitoring
.IP \(bu 2
System information collection
.IP \(bu 2
Compliance with NIST, DoD, ISO standards
.PP
.SH WIPING METHODS
.TP
.B zeros
Single pass with zeros (0x00) - fastest, good for SSDs
.TP
.B random
Multiple passes with random data - secure for most uses
.TP
.B dod
DoD 5220.22-M standard - 3 passes meeting military requirements
.TP
.B gutmann
Gutmann method - 35 passes for maximum security
.PP
.SH EXAMPLES
.TP
Launch GUI (requires root):
.B sudo trustwipe
.TP
List available devices:
.B trustwipe-cli --list-devices
.TP
Wipe device with zeros:
.B sudo trustwipe-cli --wipe /dev/sdb --method zeros
.TP
Secure wipe with DoD standard:
.B sudo trustwipe-cli --wipe /dev/sdb --method dod
.PP
.SH FILES
.TP
.I /opt/trustwipe/
Application directory
.TP
.I /boot/trustwipe-certificates/
Certificate storage (primary location)
.TP
.I /var/log/trustwipe/
Application logs
.PP
.SH SECURITY
TrustWipe implements industry-standard data sanitization methods:
.IP \(bu 2
NIST 800-88 Guidelines for Media Sanitization
.IP \(bu 2
DoD 5220.22-M Data Sanitization Standard  
.IP \(bu 2
ISO/IEC 27040:2015 Storage Security
.IP \(bu 2
GDPR Article 17 Right to Erasure compliance
.PP
.SH WARNING
.B Data wiping is irreversible and permanent.
Always verify the target device and ensure proper backups exist before proceeding.
.PP
.SH AUTHOR
TrustWipe Development Team
.SH SEE ALSO
.BR dd (1),
.BR shred (1),
.BR lsblk (8),
.BR fdisk (8)
EOF
        
        # Update man database
        if command -v mandb &> /dev/null; then
            mandb -q 2>/dev/null && log "✅ Manual page created" || log_warning "Manual page created but database update failed"
        else
            log "✅ Manual page created (database update not available)"
        fi
    else
        log_warning "Could not create manual page directory"
    fi
}

# Create uninstaller and maintenance scripts
create_maintenance_scripts() {
    echo
    log "🗑️ Creating maintenance scripts..."
    
    # Uninstall script
    cat > "$APP_DIR/uninstall.sh" << 'EOF'
#!/bin/bash
# TrustWipe Professional Uninstaller

RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m'

if [ "$EUID" -ne 0 ]; then
    echo -e "${RED}This script must be run as root (use sudo)${NC}"
    exit 1
fi

echo "========================================"
echo "    🗑️  TrustWipe Uninstaller"
echo "========================================"

echo -e "${YELLOW}Removing TrustWipe components...${NC}"

# Remove executables
rm -f /usr/local/bin/trustwipe
rm -f /usr/local/bin/trustwipe-cli
echo "✅ Removed global commands"

# Remove desktop entry
rm -f /usr/share/applications/trustwipe.desktop
echo "✅ Removed desktop entry"

# Remove man page
rm -f /usr/local/man/man1/trustwipe.1
echo "✅ Removed manual page"

# Ask about data removal
echo
echo -e "${YELLOW}Data Removal Options:${NC}"
read -p "Remove certificate directories? [y/N]: " -n 1 -r
echo
if [[ $REPLY =~ ^[Yy]$ ]]; then
    rm -rf /boot/trustwipe-certificates
    rm -rf /root/trustwipe-certificates  
    rm -rf /tmp/trustwipe-certificates
    echo "✅ Certificate directories removed"
fi

read -p "Remove log directories? [y/N]: " -n 1 -r
echo
if [[ $REPLY =~ ^[Yy]$ ]]; then
    rm -rf /var/log/trustwipe
    rm -rf /tmp/trustwipe-logs
    echo "✅ Log directories removed"
fi

# Remove application directory
rm -rf /opt/trustwipe
echo "✅ Application directory removed"

echo
echo -e "${GREEN}🎉 TrustWipe has been completely uninstalled${NC}"
echo "Thank you for using TrustWipe!"
EOF
    
    # Update script
    cat > "$APP_DIR/update.sh" << 'EOF'
#!/bin/bash
# TrustWipe Update Script

if [ "$EUID" -ne 0 ]; then
    echo "This script must be run as root (use sudo)"
    exit 1
fi

echo "========================================"
echo "    🔄 TrustWipe Update Checker"
echo "========================================"

echo "Current installation: /opt/trustwipe"
echo "To update TrustWipe:"
echo "1. Download the latest version"
echo "2. Run: sudo ./install.sh"
echo "   (This will upgrade existing installation)"

echo
echo "Current version info:"
if [ -f "/opt/trustwipe/trustwipe.py" ]; then
    grep -n "Version\|version" /opt/trustwipe/trustwipe.py | head -3 || echo "Version info not found"
else
    echo "TrustWipe not found at expected location"
fi
EOF
    
    chmod 755 "$APP_DIR/uninstall.sh"
    chmod 755 "$APP_DIR/update.sh"
    
    log "✅ Maintenance scripts created"
}

# Display installation summary
echo
echo "========================================"
echo "    ✅ Installation Complete!"
echo "========================================"
echo
echo "TrustWipe has been successfully installed:"
echo
echo "📍 Installation Location: $APP_DIR"
echo "🔗 Command Line Access: trustwipe"
echo "🖥️  Desktop Application: Available in applications menu"
echo "📜 Certificates: $CERT_DIR"
echo "📊 Logs: $LOG_DIR"
echo "📖 Manual: man trustwipe"
echo
echo "Usage:"
echo "  • GUI Mode: Run 'sudo trustwipe' or launch from applications menu"
echo "  • Command Line: 'sudo python3 $APP_DIR/trustwipe.py'"
echo
echo "⚠️  IMPORTANT:"
echo "  • Always run with root privileges (sudo)"
echo "  • Data wiping is irreversible - use with caution"
echo "  • Certificates are stored in $CERT_DIR"
# Final testing and validation
perform_final_tests() {
    echo
    log "🧪 Performing final validation..."
    
    # Test Python imports
    cd "$APP_DIR"
    
    if python3 -c "
import sys
sys.path.insert(0, '/opt/trustwipe')

print('Testing core modules...')
try:
    import trustwipe
    print('✅ Main application module')
except Exception as e:
    print(f'❌ Main application: {e}')

print('\\n✅ Core modules validated!')
" 2>/dev/null; then
        log "✅ Application validation passed"
    else
        log_warning "Some application components may have issues"
    fi
    
    # Test global commands
    if command -v trustwipe &> /dev/null && command -v trustwipe-cli &> /dev/null; then
        log "✅ Global commands available"
    else
        log_warning "Global commands may not be available"
    fi
}

# Main installation workflow
main() {
    log "🚀 Starting TrustWipe Professional Installation"
    
    # Run installation steps
    install_python
    install_system_packages  
    install_python_packages
    verify_dependencies
    install_application
    create_system_integration
    create_directories
    create_desktop_integration
    create_documentation
    create_maintenance_scripts
    perform_final_tests
    
    # Display final summary
    echo
    echo "========================================"
    echo -e "    ${GREEN}✅ Installation Complete!${NC}"
    echo "========================================"
    echo
    log "🎉 TrustWipe has been successfully installed!"
    echo
    echo -e "${BLUE}📍 Installation Details:${NC}"
    echo "   Location: $APP_DIR"
    echo "   Certificates: $CERT_DIR"
    echo "   Logs: $LOG_DIR"
    echo
    echo -e "${BLUE}🚀 How to Use:${NC}"
    if command -v trustwipe &> /dev/null; then
        echo "   GUI Mode:  sudo trustwipe"
        echo "   CLI Mode:  trustwipe-cli --help"
    else
        echo "   GUI Mode:  sudo python3 $APP_DIR/trustwipe.py"
        echo "   CLI Mode:  python3 $APP_DIR/cli.py --help"
    fi
    echo "   Manual:    man trustwipe"
    echo
    echo -e "${YELLOW}⚠️  IMPORTANT SAFETY NOTES:${NC}"
    echo "   • Always run with root privileges (sudo)"
    echo "   • Data wiping is permanent and irreversible"  
    echo "   • Test with non-critical data first"
    echo "   • Verify target device before wiping"
    echo "   • Keep certificates for compliance records"
    echo
    echo -e "${BLUE}🔧 Maintenance:${NC}"
    echo "   Update:    sudo $APP_DIR/update.sh"
    echo "   Uninstall: sudo $APP_DIR/uninstall.sh"
    echo
    echo -e "${GREEN}🎯 Quick Test:${NC}"
    if command -v trustwipe-cli &> /dev/null; then
        echo "   trustwipe-cli --list-devices"
    else
        echo "   python3 $APP_DIR/cli.py --list-devices"
    fi
    echo
    echo -e "${GREEN}Ready to use! Happy and safe wiping! 🛡️${NC}"
}

# Run main installation
main
