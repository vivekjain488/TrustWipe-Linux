#!/bin/bash

# TrustWipe Build Script
# Creates a standalone executable package for TrustWipe

set -e

echo "========================================"
echo "      TrustWipe Build Script"
echo "========================================"
echo

# Check if running from the correct directory
if [[ ! -f "trustwipe.py" ]]; then
    echo "❌ Please run this script from the TrustWipe directory"
    exit 1
fi

# Create build directory
BUILD_DIR="build"
PACKAGE_DIR="trustwipe-package"

echo "🏗️  Creating build directories..."
rm -rf "$BUILD_DIR" "$PACKAGE_DIR"
mkdir -p "$BUILD_DIR" "$PACKAGE_DIR"

# Copy source files
echo "📋 Copying source files..."
cp *.py "$BUILD_DIR/"
cp *.md "$BUILD_DIR/"
cp *.sh "$BUILD_DIR/"

# Create the main executable script
echo "🔧 Creating executable wrapper..."
cat > "$BUILD_DIR/trustwipe" << 'EOF'
#!/bin/bash

# TrustWipe Executable Wrapper
# This script launches TrustWipe with proper environment setup

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"

# Check for root privileges
if [ "$EUID" -ne 0 ]; then
    echo "❌ TrustWipe requires root privileges"
    echo "Please run: sudo $0"
    exit 1
fi

# Check Python dependencies
python3 -c "import tkinter, psutil" 2>/dev/null || {
    echo "❌ Missing Python dependencies"
    echo "Please install: python3-tk python3-pip"
    echo "Then run: pip3 install psutil"
    exit 1
}

# Launch TrustWipe GUI
cd "$SCRIPT_DIR"
python3 trustwipe.py "$@"
EOF

chmod +x "$BUILD_DIR/trustwipe"

# Create CLI wrapper
echo "🔧 Creating CLI wrapper..."
cat > "$BUILD_DIR/trustwipe-cli" << 'EOF'
#!/bin/bash

# TrustWipe CLI Wrapper

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"

# Check for root privileges for wipe operations
if [[ "$*" == *"--wipe"* ]] && [ "$EUID" -ne 0 ]; then
    echo "❌ Wipe operations require root privileges"
    echo "Please run: sudo $0 $*"
    exit 1
fi

# Launch TrustWipe CLI
cd "$SCRIPT_DIR"
python3 cli.py "$@"
EOF

chmod +x "$BUILD_DIR/trustwipe-cli"

# Create package structure
echo "📦 Creating package structure..."
mkdir -p "$PACKAGE_DIR/bin"
mkdir -p "$PACKAGE_DIR/lib"
mkdir -p "$PACKAGE_DIR/doc"
mkdir -p "$PACKAGE_DIR/examples"

# Copy files to package
cp "$BUILD_DIR/trustwipe" "$PACKAGE_DIR/bin/"
cp "$BUILD_DIR/trustwipe-cli" "$PACKAGE_DIR/bin/"
cp "$BUILD_DIR"/*.py "$PACKAGE_DIR/lib/"
cp "$BUILD_DIR/README.md" "$PACKAGE_DIR/doc/"
cp "$BUILD_DIR/install.sh" "$PACKAGE_DIR/"

# Create package installer
echo "🔧 Creating package installer..."
cat > "$PACKAGE_DIR/install-package.sh" << 'EOF'
#!/bin/bash

# TrustWipe Package Installer

set -e

echo "========================================"
echo "    TrustWipe Package Installer"
echo "========================================"
echo

# Check if running as root
if [ "$EUID" -ne 0 ]; then
    echo "❌ This installer must be run as root (use sudo)"
    exit 1
fi

INSTALL_DIR="/opt/trustwipe"

echo "📁 Installing TrustWipe to $INSTALL_DIR..."

# Create installation directory
mkdir -p "$INSTALL_DIR"

# Copy files
cp -r lib/* "$INSTALL_DIR/"
cp -r doc/* "$INSTALL_DIR/"
chmod 755 "$INSTALL_DIR"/*.py

# Install executables
cp bin/trustwipe /usr/local/bin/
cp bin/trustwipe-cli /usr/local/bin/
chmod 755 /usr/local/bin/trustwipe
chmod 755 /usr/local/bin/trustwipe-cli

# Update executable paths
sed -i "s|SCRIPT_DIR=.*|SCRIPT_DIR=\"$INSTALL_DIR\"|" /usr/local/bin/trustwipe
sed -i "s|SCRIPT_DIR=.*|SCRIPT_DIR=\"$INSTALL_DIR\"|" /usr/local/bin/trustwipe-cli

# Create certificate directory
mkdir -p /boot/trustwipe-certificates
chmod 755 /boot/trustwipe-certificates

# Create log directory
mkdir -p /var/log/trustwipe
chmod 755 /var/log/trustwipe

echo "✅ Installation complete!"
echo
echo "Usage:"
echo "  GUI Mode: sudo trustwipe"
echo "  CLI Mode: trustwipe-cli --help"
echo
EOF

chmod +x "$PACKAGE_DIR/install-package.sh"

# Create example scripts
echo "📝 Creating example scripts..."
cat > "$PACKAGE_DIR/examples/wipe-usb.sh" << 'EOF'
#!/bin/bash

# Example: Wipe USB drive with zeros (safe and fast)
# Usage: sudo ./wipe-usb.sh /dev/sdX

if [ "$#" -ne 1 ]; then
    echo "Usage: sudo $0 /dev/sdX"
    echo "Example: sudo $0 /dev/sdb"
    exit 1
fi

DEVICE="$1"

echo "🔍 Device info for $DEVICE:"
trustwipe-cli --device-info "$DEVICE"

echo
echo "⚠️  About to wipe $DEVICE with zeros (1 pass)"
read -p "Continue? [y/N]: " -n 1 -r
echo

if [[ $REPLY =~ ^[Yy]$ ]]; then
    trustwipe-cli --wipe "$DEVICE" --method zeros --passes 1
else
    echo "Operation cancelled"
fi
EOF

cat > "$PACKAGE_DIR/examples/secure-wipe.sh" << 'EOF'
#!/bin/bash

# Example: Secure wipe with DoD standard
# Usage: sudo ./secure-wipe.sh /dev/sdX

if [ "$#" -ne 1 ]; then
    echo "Usage: sudo $0 /dev/sdX"
    echo "Example: sudo $0 /dev/sdb"
    exit 1
fi

DEVICE="$1"

echo "🔍 Device info for $DEVICE:"
trustwipe-cli --device-info "$DEVICE"

echo
echo "⚠️  About to wipe $DEVICE with DoD 5220.22-M standard (3 passes)"
echo "This will take significantly longer than a simple zero wipe!"
read -p "Continue? [y/N]: " -n 1 -r
echo

if [[ $REPLY =~ ^[Yy]$ ]]; then
    trustwipe-cli --wipe "$DEVICE" --method dod
else
    echo "Operation cancelled"
fi
EOF

chmod +x "$PACKAGE_DIR/examples"/*.sh

# Create documentation
echo "📚 Creating documentation..."
cat > "$PACKAGE_DIR/doc/USAGE.md" << 'EOF'
# TrustWipe Usage Guide

## GUI Mode

Launch TrustWipe with a graphical interface:

```bash
sudo trustwipe
```

## CLI Mode

Use TrustWipe from the command line:

```bash
# List available devices
trustwipe-cli --list-devices

# Show device information
trustwipe-cli --device-info /dev/sdb

# Wipe device with zeros (fast)
sudo trustwipe-cli --wipe /dev/sdb --method zeros

# Secure wipe with DoD standard
sudo trustwipe-cli --wipe /dev/sdb --method dod

# Maximum security wipe (35 passes)
sudo trustwipe-cli --wipe /dev/sdb --method gutmann

# List certificates
trustwipe-cli --list-certs

# Show certificate details
trustwipe-cli --show-cert 12345678
```

## Wiping Methods

- **zeros**: Fast wipe with zeros (good for SSDs)
- **random**: Secure wipe with random data
- **dod**: DoD 5220.22-M standard (3 passes)
- **gutmann**: Gutmann method (35 passes, maximum security)

## Safety Features

- Multiple confirmation prompts
- Device information display
- Progress monitoring
- Certificate generation
- Error logging

## Certificate Storage

Certificates are stored in `/boot/trustwipe-certificates/` and contain:
- System information
- Device details
- Wipe parameters
- Timestamps
- Verification checksums
EOF

# Create package info
echo "📋 Creating package information..."
cat > "$PACKAGE_DIR/PACKAGE-INFO.txt" << EOF
TrustWipe Portable Package
==========================

Version: 1.0
Build Date: $(date)
Build Host: $(hostname)
Platform: $(uname -a)

Contents:
- bin/trustwipe         - GUI executable
- bin/trustwipe-cli     - CLI executable  
- lib/*.py             - Python modules
- doc/                 - Documentation
- examples/            - Example scripts
- install-package.sh   - Package installer

Installation:
sudo ./install-package.sh

Manual Usage (without installation):
sudo bin/trustwipe
bin/trustwipe-cli --help

Requirements:
- Linux operating system
- Python 3.6+
- python3-tk (for GUI)
- psutil Python package
- Root privileges for wiping operations

Built with TrustWipe Build System
EOF

# Create tarball
echo "📦 Creating distribution package..."
cd "$PACKAGE_DIR"
tar -czf "../trustwipe-linux-$(date +%Y%m%d).tar.gz" .
cd ..

# Create installer script
echo "🔧 Creating standalone installer..."
cat > "trustwipe-installer.sh" << 'EOF'
#!/bin/bash

# TrustWipe Standalone Installer
# This script downloads and installs TrustWipe

set -e

echo "========================================"
echo "    TrustWipe Standalone Installer"
echo "========================================"
echo

# Check if running as root
if [ "$EUID" -ne 0 ]; then
    echo "❌ This installer must be run as root (use sudo)"
    exit 1
fi

# Create temporary directory
TEMP_DIR=$(mktemp -d)
cd "$TEMP_DIR"

# Check if package exists locally
if [ -f "../trustwipe-linux-*.tar.gz" ]; then
    echo "📋 Using local package..."
    cp ../trustwipe-linux-*.tar.gz ./package.tar.gz
else
    echo "❌ Package not found. Please run from the build directory."
    exit 1
fi

# Extract package
echo "📦 Extracting package..."
tar -xzf package.tar.gz

# Run installer
echo "🚀 Running installer..."
./install-package.sh

# Cleanup
cd /
rm -rf "$TEMP_DIR"

echo "🎉 TrustWipe installation complete!"
EOF

chmod +x "trustwipe-installer.sh"

# Display build summary
echo
echo "========================================"
echo "    ✅ Build Complete!"
echo "========================================"
echo
echo "📦 Package created: trustwipe-linux-$(date +%Y%m%d).tar.gz"
echo "🔧 Standalone installer: trustwipe-installer.sh"
echo
echo "Distribution contents:"
echo "  • GUI and CLI executables"
echo "  • Python source code"  
echo "  • Documentation and examples"
echo "  • Automated installer"
echo
echo "Installation options:"
echo "  1. Run: sudo ./trustwipe-installer.sh"
echo "  2. Extract package and run: sudo ./install-package.sh"
echo "  3. Use portable: sudo $PACKAGE_DIR/bin/trustwipe"
echo
echo "📁 Build files in: $BUILD_DIR/"
echo "📁 Package files in: $PACKAGE_DIR/"
echo
echo "Ready for distribution! 🚀"
