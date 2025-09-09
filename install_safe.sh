#!/bin/bash

# TrustWipe SAFE Installation Script
# Installs the SAFE version that prevents OS destruction

set -e

echo "🔒 TrustWipe SAFE Installation"
echo "=============================="
echo ""
echo "This version includes CRITICAL SAFETY FEATURES:"
echo "• OS Protection: Cannot wipe system drives"
echo "• Smart Detection: Only removes personal data"
echo "• Safe Operations: Your Linux stays intact"
echo ""

# Check if running as root
if [ "$EUID" -ne 0 ]; then
    echo "❌ Error: This script must be run as root"
    echo "Please run: sudo ./install_safe.sh"
    exit 1
fi

echo "🔍 Checking system requirements..."

# Check Python version
if ! command -v python3 &> /dev/null; then
    echo "❌ Python 3 is not installed"
    echo "Installing Python 3..."
    
    if command -v apt &> /dev/null; then
        apt update && apt install -y python3 python3-pip python3-tk
    elif command -v yum &> /dev/null; then
        yum install -y python3 python3-pip python3-tkinter
    elif command -v pacman &> /dev/null; then
        pacman -S --noconfirm python python-pip tk
    else
        echo "❌ Unsupported package manager. Please install Python 3 manually."
        exit 1
    fi
fi

# Check Python version
PYTHON_VERSION=$(python3 -c "import sys; print(f'{sys.version_info.major}.{sys.version_info.minor}')")
echo "✅ Python $PYTHON_VERSION detected"

# Install Python dependencies
echo "📦 Installing Python dependencies..."

# Try pip install with different approaches
PACKAGES="psutil"

# Method 1: Try regular pip install
if pip3 install $PACKAGES &> /dev/null; then
    echo "✅ Dependencies installed via pip"
elif pip3 install --break-system-packages $PACKAGES &> /dev/null; then
    echo "✅ Dependencies installed via pip (break-system-packages)"
elif python3 -m pip install --user $PACKAGES &> /dev/null; then
    echo "✅ Dependencies installed via pip (user)"
else
    # Method 2: Try system packages
    echo "⚠️  Pip install failed, trying system packages..."
    
    if command -v apt &> /dev/null; then
        apt install -y python3-psutil python3-tk
    elif command -v yum &> /dev/null; then
        yum install -y python3-psutil python3-tkinter
    elif command -v pacman &> /dev/null; then
        pacman -S --noconfirm python-psutil tk
    else
        echo "❌ Could not install dependencies"
        exit 1
    fi
    
    echo "✅ Dependencies installed via system packages"
fi

# Create application directory
APP_DIR="/usr/local/bin/trustwipe-safe"
echo "📁 Creating application directory: $APP_DIR"
mkdir -p "$APP_DIR"

# Copy application files
echo "📋 Copying application files..."
cp safe_trustwipe.py "$APP_DIR/"
cp safe_backend.py "$APP_DIR/"
cp safety_manager.py "$APP_DIR/"
cp safe_cli.py "$APP_DIR/"
cp certificate_generator.py "$APP_DIR/"

# Make files executable
chmod +x "$APP_DIR"/*.py

# Create symbolic links for easy access
echo "🔗 Creating command links..."
ln -sf "$APP_DIR/safe_trustwipe.py" /usr/local/bin/trustwipe-safe-gui
ln -sf "$APP_DIR/safe_cli.py" /usr/local/bin/trustwipe-safe
ln -sf "$APP_DIR/safe_cli.py" /usr/local/bin/trustwipe-safe-cli

# Create desktop entry for GUI
echo "🖥️ Creating desktop entry..."
cat > /usr/share/applications/trustwipe-safe.desktop << EOF
[Desktop Entry]
Version=1.0
Type=Application
Name=TrustWipe SAFE
Comment=Secure Personal Data Wiping Tool with OS Protection
Exec=sudo /usr/local/bin/trustwipe-safe-gui
Icon=security-high
Terminal=false
Categories=System;Security;
Keywords=wipe;secure;delete;data;privacy;safe;
EOF

# Create log directory
mkdir -p /var/log/trustwipe
chmod 755 /var/log/trustwipe

# Create man page
echo "📖 Creating man page..."
mkdir -p /usr/local/man/man1

cat > /usr/local/man/man1/trustwipe-safe.1 << 'EOF'
.TH TRUSTWIPE-SAFE 1 "2024" "TrustWipe SAFE" "User Commands"
.SH NAME
trustwipe-safe \- secure personal data wiping tool with OS protection
.SH SYNOPSIS
.B trustwipe-safe
[\fIOPTION\fR]...
.SH DESCRIPTION
TrustWipe SAFE is a secure data wiping tool that focuses on personal data removal while providing critical safety features to prevent operating system destruction.
.SH SAFETY FEATURES
.TP
.B OS Protection
Cannot wipe system drives containing the operating system
.TP
.B Smart Detection
Automatically identifies and removes only personal data
.TP
.B Safe Operations
Preserves Linux installation and system files
.SH OPTIONS
.TP
.BR \-t ", " \-\-type " " \fITYPE\fR
Wipe type: personal-data, factory-reset, external-drive
.TP
.BR \-m ", " \-\-method " " \fIMETHOD\fR
Wiping method: zeros, random, dod
.TP
.BR \-d ", " \-\-device " " \fIDEVICE\fR
Device path for external drive wipe
.TP
.BR \-f ", " \-\-force
Skip confirmation prompts
.TP
.BR \-c ", " \-\-certificate
Generate certificate after wipe
.TP
.BR \-\-list\-devices
List all devices with safety status
.SH EXAMPLES
.TP
Wipe personal data only:
.B trustwipe-safe --type personal-data --method zeros
.TP
Factory reset while preserving OS:
.B trustwipe-safe --type factory-reset --method dod
.TP
Wipe external drive safely:
.B trustwipe-safe --type external-drive --device /dev/sdb
.SH FILES
.TP
.I /var/log/trustwipe/
Log files directory
.TP
.I /usr/local/bin/trustwipe-safe
Main executable
.SH AUTHOR
TrustWipe Development Team
.SH SEE ALSO
.BR dd (1),
.BR shred (1)
EOF

# Test installation
echo "🧪 Testing installation..."

if python3 -c "import sys; sys.path.insert(0, '$APP_DIR'); from safety_manager import SafetyManager; print('✅ Safety manager works')" 2>/dev/null; then
    echo "✅ Safety manager test passed"
else
    echo "❌ Safety manager test failed"
    exit 1
fi

if python3 -c "import sys; sys.path.insert(0, '$APP_DIR'); from safe_backend import SafeDataWiper; print('✅ Safe backend works')" 2>/dev/null; then
    echo "✅ Safe backend test passed"
else
    echo "❌ Safe backend test failed"
    exit 1
fi

echo ""
echo "🎉 TrustWipe SAFE Installation Complete!"
echo "======================================"
echo ""
echo "🔒 SAFETY FEATURES ACTIVE:"
echo "• OS Protection: Cannot wipe system drives"
echo "• Smart Detection: Only removes personal data"
echo "• Safe Operations: Your Linux stays intact"
echo ""
echo "📱 Usage:"
echo "• GUI Application: trustwipe-safe-gui"
echo "• Command Line: trustwipe-safe --help"
echo "• List devices: trustwipe-safe --list-devices"
echo ""
echo "🔍 Examples:"
echo "• Wipe personal data: sudo trustwipe-safe --type personal-data"
echo "• Factory reset: sudo trustwipe-safe --type factory-reset"
echo "• Check devices: sudo trustwipe-safe --list-devices"
echo ""
echo "⚠️  IMPORTANT: Always run with sudo for proper permissions"
echo ""
echo "📜 Generate certificates with --certificate flag"
echo "📁 Files installed in: $APP_DIR"
echo "📝 Logs stored in: /var/log/trustwipe/"
echo ""
echo "🛡️ Your system is now protected from accidental OS wiping!"
