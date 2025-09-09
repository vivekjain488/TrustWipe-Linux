#!/bin/bash

# TrustWipe ULTRA-FAST Installation Script
# Optimized for 5GB /dev/sdb wiping in VMware environments

echo "⚡ TrustWipe ULTRA-FAST Installation ⚡"
echo "======================================"
echo ""
echo "🎯 Optimized for 5GB /dev/sdb in VMware Linux"
echo "🚀 Target: Wipe 5GB in under 30 seconds!"
echo ""

# Check if running as root
if [ "$EUID" -ne 0 ]; then
    echo "❌ Error: This script must be run as root"
    echo "Please run: sudo ./install_ultra_fast.sh"
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

PYTHON_VERSION=$(python3 -c "import sys; print(f'{sys.version_info.major}.{sys.version_info.minor}')")
echo "✅ Python $PYTHON_VERSION detected"

# Install Python dependencies for ultra-fast performance
echo "📦 Installing ultra-fast dependencies..."

PACKAGES="psutil"

# Try different installation methods
if pip3 install $PACKAGES &> /dev/null; then
    echo "✅ Dependencies installed via pip"
elif pip3 install --break-system-packages $PACKAGES &> /dev/null; then
    echo "✅ Dependencies installed via pip (break-system-packages)"
elif python3 -m pip install --user $PACKAGES &> /dev/null; then
    echo "✅ Dependencies installed via pip (user)"
else
    # Try system packages
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

# Install performance optimization tools
echo "🚀 Installing performance optimization tools..."

if command -v apt &> /dev/null; then
    apt install -y hdparm util-linux
elif command -v yum &> /dev/null; then
    yum install -y hdparm util-linux
elif command -v pacman &> /dev/null; then
    pacman -S --noconfirm hdparm util-linux
fi

# Create ultra-fast application directory
APP_DIR="/usr/local/bin/trustwipe-ultra-fast"
echo "📁 Creating ultra-fast application directory: $APP_DIR"
mkdir -p "$APP_DIR"

# Copy ultra-fast application files
echo "📋 Copying ultra-fast application files..."
cp ultra_fast_backend.py "$APP_DIR/"
cp ultra_fast_gui.py "$APP_DIR/"
cp ultra_fast_cli.py "$APP_DIR/"
cp certificate_generator.py "$APP_DIR/"

# Make files executable
chmod +x "$APP_DIR"/*.py

# Create ultra-fast command links
echo "🔗 Creating ultra-fast command links..."
ln -sf "$APP_DIR/ultra_fast_gui.py" /usr/local/bin/trustwipe-ultra-gui
ln -sf "$APP_DIR/ultra_fast_cli.py" /usr/local/bin/trustwipe-ultra
ln -sf "$APP_DIR/ultra_fast_cli.py" /usr/local/bin/trustwipe-ultra-cli

# Create desktop entry for ultra-fast GUI
echo "🖥️ Creating ultra-fast desktop entry..."
cat > /usr/share/applications/trustwipe-ultra-fast.desktop << EOF
[Desktop Entry]
Version=1.0
Type=Application
Name=TrustWipe ULTRA-FAST
Comment=Ultra-Fast 5GB SDB Wiper - Under 30 seconds!
Exec=sudo /usr/local/bin/trustwipe-ultra-gui
Icon=drive-harddisk
Terminal=false
Categories=System;Security;
Keywords=wipe;fast;secure;delete;ultra;speed;
EOF

# Create system optimization script
echo "⚙️ Creating system optimization script..."
cat > /usr/local/bin/trustwipe-optimize-system << 'EOF'
#!/bin/bash
# TrustWipe Ultra-Fast System Optimization

echo "🚀 Optimizing system for ultra-fast wiping..."

# Set I/O scheduler to noop for maximum sequential write performance
for disk in /sys/block/sd*; do
    if [ -f "$disk/queue/scheduler" ]; then
        echo noop > "$disk/queue/scheduler" 2>/dev/null || true
    fi
done

# Increase readahead for better sequential I/O
for device in /dev/sd?; do
    if [ -b "$device" ]; then
        blockdev --setra 32768 "$device" 2>/dev/null || true
    fi
done

# Optimize VM settings for performance
echo 0 > /proc/sys/vm/dirty_writeback_centisecs 2>/dev/null || true
echo 1 > /proc/sys/vm/drop_caches 2>/dev/null || true

# Enable write cache on drives (VMware safe)
for device in /dev/sd?; do
    if [ -b "$device" ]; then
        hdparm -W1 "$device" 2>/dev/null || true
    fi
done

echo "✅ System optimized for ultra-fast performance!"
EOF

chmod +x /usr/local/bin/trustwipe-optimize-system

# Create ultra-fast benchmark script
echo "🏁 Creating benchmark script..."
cat > /usr/local/bin/trustwipe-benchmark << 'EOF'
#!/bin/bash
# TrustWipe Ultra-Fast Benchmark

echo "🏁 TrustWipe Ultra-Fast Benchmark"
echo "=================================="
echo ""

if [ "$EUID" -ne 0 ]; then
    echo "❌ Error: Benchmark requires root privileges"
    echo "Please run: sudo trustwipe-benchmark"
    exit 1
fi

# Optimize system first
trustwipe-optimize-system

echo "🚀 Running ultra-fast benchmark on /dev/sdb..."
echo ""

trustwipe-ultra --benchmark --device /dev/sdb
EOF

chmod +x /usr/local/bin/trustwipe-benchmark

# Create log directory
mkdir -p /var/log/trustwipe-ultra
chmod 755 /var/log/trustwipe-ultra

# Create man page for ultra-fast version
echo "📖 Creating ultra-fast man page..."
mkdir -p /usr/local/man/man1

cat > /usr/local/man/man1/trustwipe-ultra.1 << 'EOF'
.TH TRUSTWIPE-ULTRA 1 "2024" "TrustWipe ULTRA-FAST" "User Commands"
.SH NAME
trustwipe-ultra \- ultra-fast 5GB drive wiper optimized for VMware
.SH SYNOPSIS
.B trustwipe-ultra
[\fIOPTION\fR]...
.SH DESCRIPTION
TrustWipe ULTRA-FAST is an optimized data wiping tool designed specifically for 5GB drives in VMware environments, targeting completion times under 30 seconds.
.SH PERFORMANCE
.TP
.B Lightning Method
Memory buffer technique - 15-20 seconds for 5GB
.TP
.B Ultra-Fast Zeros
Optimized DD with 512MB blocks - 25-30 seconds for 5GB
.TP
.B Parallel Random
Multi-threaded secure wipe - 45-60 seconds for 5GB
.SH OPTIONS
.TP
.BR \-m ", " \-\-method " " \fIMETHOD\fR
Ultra-fast method: lightning, zeros, random
.TP
.BR \-d ", " \-\-device " " \fIDEVICE\fR
Target device (default: /dev/sdb)
.TP
.BR \-b ", " \-\-benchmark
Run speed benchmark on all methods
.TP
.BR \-f ", " \-\-force
Skip confirmation prompts
.TP
.BR \-M ", " \-\-monitor
Show detailed performance monitoring
.SH EXAMPLES
.TP
Lightning-fast wipe (FASTEST):
.B sudo trustwipe-ultra --method lightning
.TP
Ultra-fast zero wipe:
.B sudo trustwipe-ultra --method zeros
.TP
Speed benchmark:
.B sudo trustwipe-ultra --benchmark
.SH FILES
.TP
.I /var/log/trustwipe-ultra/
Ultra-fast log files directory
.TP
.I /usr/local/bin/trustwipe-ultra
Main ultra-fast executable
.SH AUTHOR
TrustWipe Ultra-Fast Development Team
.SH SEE ALSO
.BR dd (1),
.BR hdparm (8)
EOF

# Test ultra-fast installation
echo "🧪 Testing ultra-fast installation..."

if python3 -c "import sys; sys.path.insert(0, '$APP_DIR'); from ultra_fast_backend import UltraFastDataWiper; print('✅ Ultra-fast backend works')" 2>/dev/null; then
    echo "✅ Ultra-fast backend test passed"
else
    echo "❌ Ultra-fast backend test failed"
    exit 1
fi

# Apply initial system optimizations
echo "🚀 Applying initial system optimizations..."
trustwipe-optimize-system

echo ""
echo "⚡ TrustWipe ULTRA-FAST Installation Complete! ⚡"
echo "==============================================="
echo ""
echo "🎯 ULTRA-FAST PERFORMANCE TARGETS:"
echo "• Lightning Method: 15-20 seconds for 5GB"
echo "• Ultra-Fast Zeros: 25-30 seconds for 5GB" 
echo "• Parallel Random: 45-60 seconds for 5GB"
echo ""
echo "🚀 USAGE:"
echo "• Ultra-Fast GUI: sudo trustwipe-ultra-gui"
echo "• Ultra-Fast CLI: sudo trustwipe-ultra --help"
echo "• Speed Benchmark: sudo trustwipe-benchmark"
echo "• System Optimize: sudo trustwipe-optimize-system"
echo ""
echo "🔍 EXAMPLES:"
echo "• Lightning wipe: sudo trustwipe-ultra --method lightning"
echo "• Benchmark all: sudo trustwipe-ultra --benchmark"
echo "• Force mode: sudo trustwipe-ultra --method lightning --force"
echo ""
echo "⚠️  IMPORTANT:"
echo "• Always run with sudo for maximum performance"
echo "• System automatically optimized for speed"
echo "• Designed specifically for /dev/sdb (5GB)"
echo ""
echo "📊 PERFORMANCE MONITORING:"
echo "• Real-time speed display"
echo "• Peak performance tracking"
echo "• ETA calculations"
echo "• Performance ratings"
echo ""
echo "🏆 Ready for ULTRA-FAST 5GB wiping in under 30 seconds!"
