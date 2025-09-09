#!/bin/bash

# TrustWipe Simple Setup Script
# No-dependency installer that works on any Linux system

set -e

# Colors
RED='\033[0;31m'
GREEN='\033[0;32m' 
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m'

echo "========================================"
echo -e "    ${GREEN}🛡️  TrustWipe Simple Setup${NC}"
echo "========================================"
echo

# Check if running as root
if [ "$EUID" -ne 0 ]; then
    echo -e "${RED}❌ This script must be run as root${NC}"
    echo "Usage: sudo ./setup.sh"
    exit 1
fi

echo -e "${GREEN}✅ Running as root${NC}"

# Check Python 3
if ! command -v python3 &> /dev/null; then
    echo -e "${RED}❌ Python 3 is required but not found${NC}"
    echo "Please install Python 3 first:"
    echo "  Ubuntu/Debian: sudo apt install python3"
    echo "  CentOS/RHEL:   sudo yum install python3" 
    echo "  Arch:          sudo pacman -S python"
    exit 1
fi

PYTHON_VERSION=$(python3 --version)
echo -e "${GREEN}✅ Found: $PYTHON_VERSION${NC}"

# Create application directory
APP_DIR="/opt/trustwipe"
echo -e "${BLUE}📁 Creating application directory: $APP_DIR${NC}"
mkdir -p "$APP_DIR"
chmod 755 "$APP_DIR"

# Copy files
echo -e "${BLUE}📋 Installing application files...${NC}"
REQUIRED_FILES=("trustwipe.py" "backend.py" "certificate_generator.py" "cli.py")

for file in "${REQUIRED_FILES[@]}"; do
    if [ -f "$file" ]; then
        cp "$file" "$APP_DIR/"
        chmod 755 "$APP_DIR/$file"
        echo -e "${GREEN}✅ $file${NC}"
    else
        echo -e "${RED}❌ Missing: $file${NC}"
        exit 1
    fi
done

# Copy optional files
OPTIONAL_FILES=("README.md" "LICENSE" "CHANGELOG.md")
for file in "${OPTIONAL_FILES[@]}"; do
    if [ -f "$file" ]; then
        cp "$file" "$APP_DIR/"
        chmod 644 "$APP_DIR/$file"
        echo -e "${GREEN}✅ $file${NC}"
    fi
done

# Create certificate directory
echo -e "${BLUE}📜 Creating certificate directory...${NC}"
CERT_DIRS=("/boot/trustwipe-certificates" "/root/trustwipe-certificates" "/tmp/trustwipe-certificates")
CERT_DIR=""

for dir in "${CERT_DIRS[@]}"; do
    if mkdir -p "$dir" 2>/dev/null && [ -w "$dir" ]; then
        CERT_DIR="$dir"
        chmod 755 "$dir"
        echo -e "${GREEN}✅ Certificate directory: $CERT_DIR${NC}"
        break
    fi
done

if [ -z "$CERT_DIR" ]; then
    echo -e "${RED}❌ Could not create certificate directory${NC}"
    exit 1
fi

# Create launchers
echo -e "${BLUE}🚀 Creating launch scripts...${NC}"

# Main launcher
cat > /usr/local/bin/trustwipe << EOF
#!/bin/bash
if [ "\$EUID" -ne 0 ]; then
    echo "❌ TrustWipe requires root privileges"
    echo "Please run: sudo trustwipe"
    exit 1
fi
cd /opt/trustwipe
python3 trustwipe.py "\$@"
EOF

# CLI launcher
cat > /usr/local/bin/trustwipe-cli << EOF
#!/bin/bash
cd /opt/trustwipe
python3 cli.py "\$@"
EOF

chmod 755 /usr/local/bin/trustwipe
chmod 755 /usr/local/bin/trustwipe-cli

# Test installation
echo -e "${BLUE}🧪 Testing installation...${NC}"
cd "$APP_DIR"

if python3 -c "
try:
    with open('trustwipe.py', 'r') as f:
        if 'TrustWipeGUI' in f.read():
            print('✅ TrustWipe application validated')
        else:
            print('❌ Invalid application file')
            exit(1)
except Exception as e:
    print(f'❌ Error: {e}')
    exit(1)
"; then
    echo -e "${GREEN}✅ Installation validated${NC}"
else
    echo -e "${RED}❌ Installation validation failed${NC}"
    exit 1
fi

# Create uninstaller
cat > "$APP_DIR/uninstall.sh" << 'EOF'
#!/bin/bash
if [ "$EUID" -ne 0 ]; then
    echo "Run with: sudo $0"
    exit 1
fi
echo "Removing TrustWipe..."
rm -f /usr/local/bin/trustwipe /usr/local/bin/trustwipe-cli
rm -rf /opt/trustwipe
echo "✅ TrustWipe removed"
EOF

chmod 755 "$APP_DIR/uninstall.sh"

# Final summary
echo
echo "========================================"
echo -e "    ${GREEN}✅ Setup Complete!${NC}"
echo "========================================"
echo
echo -e "${BLUE}📍 Installation Location:${NC} $APP_DIR"
echo -e "${BLUE}📜 Certificate Directory:${NC} $CERT_DIR"
echo
echo -e "${GREEN}🚀 How to Use:${NC}"
echo "   GUI Mode:  sudo trustwipe"
echo "   CLI Mode:  trustwipe-cli --help"
echo "   Direct:    sudo python3 $APP_DIR/trustwipe.py"
echo
echo -e "${YELLOW}⚠️  Important:${NC}"
echo "   • Always run with sudo for disk operations"
echo "   • Data wiping is permanent and irreversible"
echo "   • Test with non-critical data first"
echo
echo -e "${GREEN}🎯 Quick Test:${NC}"
echo "   trustwipe-cli --list-devices"
echo
echo -e "${GREEN}🎉 TrustWipe is ready to use!${NC}"
