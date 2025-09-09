#!/bin/bash

# TrustWipe Deployment Package Creator
# Creates a complete deployment package with all working files

echo "========================================"
echo "  🛡️  TrustWipe Deployment Creator"
echo "========================================"
echo

# Create deployment directory
DEPLOY_DIR="trustwipe-deployment-$(date +%Y%m%d-%H%M%S)"
echo "📦 Creating deployment package: $DEPLOY_DIR"
mkdir -p "$DEPLOY_DIR"

# Copy all essential files
echo "📋 Copying application files..."

# Core Python files
CORE_FILES=(
    "trustwipe.py"
    "backend.py" 
    "certificate_generator.py"
    "cli.py"
)

for file in "${CORE_FILES[@]}"; do
    if [ -f "$file" ]; then
        cp "$file" "$DEPLOY_DIR/"
        echo "✅ $file"
    else
        echo "❌ Missing: $file"
        exit 1
    fi
done

# Installation scripts
INSTALL_FILES=(
    "setup.sh"
    "install.sh"
)

for file in "${INSTALL_FILES[@]}"; do
    if [ -f "$file" ]; then
        cp "$file" "$DEPLOY_DIR/"
        chmod +x "$DEPLOY_DIR/$file"
        echo "✅ $file"
    fi
done

# Documentation files
DOC_FILES=(
    "README.md"
    "CHANGELOG.md"
    "LICENSE"
)

for file in "${DOC_FILES[@]}"; do
    if [ -f "$file" ]; then
        cp "$file" "$DEPLOY_DIR/"
        echo "✅ $file"
    fi
done

# Create quick start guide
cat > "$DEPLOY_DIR/QUICK_START.md" << 'EOF'
# TrustWipe Quick Start Guide

## Installation

### Method 1: Simple Setup (Recommended)
```bash
sudo ./setup.sh
```

### Method 2: Full Installer
```bash
sudo ./install.sh
```

## Usage

### GUI Mode
```bash
sudo trustwipe
```

### CLI Mode
```bash
# List available devices
trustwipe-cli --list-devices

# Wipe a device (example)
sudo trustwipe-cli --device /dev/sdb --algorithm zeros --passes 1

# Show help
trustwipe-cli --help
```

## Important Notes

- **Always run with sudo** for disk operations
- **Data wiping is permanent and irreversible**
- **Test with non-critical data first**
- Certificates are saved to `/boot/trustwipe-certificates/`
- Compatible with all Linux distributions including Kali Linux

## Features

- Professional GUI interface
- Command-line interface for automation
- Multiple wiping algorithms (zeros, random, DoD, Gutmann)
- Professional certificates with verification
- Progress monitoring and logging
- System integration
- VMware compatible

## Support

If you encounter any issues:
1. Check that Python 3 is installed
2. Ensure you're running as root/sudo
3. Verify device permissions
4. Check system logs for errors

**Made with ❤️ for secure data destruction**
EOF

# Create version info
cat > "$DEPLOY_DIR/VERSION" << EOF
TrustWipe v2.0
Build Date: $(date)
Platform: Linux (Universal)
Python: 3.6+
Status: Production Ready
EOF

# Create deployment verification script
cat > "$DEPLOY_DIR/verify.sh" << 'EOF'
#!/bin/bash

echo "🔍 Verifying TrustWipe deployment package..."

REQUIRED_FILES=(
    "trustwipe.py"
    "backend.py"
    "certificate_generator.py"
    "cli.py" 
    "setup.sh"
)

ALL_GOOD=true

for file in "${REQUIRED_FILES[@]}"; do
    if [ -f "$file" ]; then
        echo "✅ $file"
    else
        echo "❌ Missing: $file"
        ALL_GOOD=false
    fi
done

if $ALL_GOOD; then
    echo
    echo "✅ Package verification successful!"
    echo "📦 Ready for deployment"
    echo
    echo "Next steps:"
    echo "1. Transfer this package to your Linux system"
    echo "2. Run: sudo ./setup.sh"
    echo "3. Use: sudo trustwipe"
else
    echo
    echo "❌ Package verification failed!"
    echo "Some required files are missing."
    exit 1
fi
EOF

chmod +x "$DEPLOY_DIR/verify.sh"

echo
echo "📁 Created deployment package: $DEPLOY_DIR"
echo
echo "📋 Package contents:"
ls -la "$DEPLOY_DIR"
echo
echo "✅ Deployment package ready!"
echo
echo "🚀 To deploy on Linux:"
echo "   1. Transfer the '$DEPLOY_DIR' folder to your Linux system"
echo "   2. cd $DEPLOY_DIR"
echo "   3. ./verify.sh"
echo "   4. sudo ./setup.sh"
echo "   5. sudo trustwipe"
echo
