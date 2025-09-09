#!/bin/bash

# TrustWipe Hackathon Demo Script
# Creates small virtual disks for fast demonstration

echo "========================================"
echo "    TrustWipe Hackathon Demo Setup"
echo "========================================"
echo

if [ "$EUID" -ne 0 ]; then
    echo "❌ This demo script must be run as root (use sudo)"
    exit 1
fi

# Clean up any existing demo setup
echo "🧹 Cleaning up previous demo setup..."
for i in {0..9}; do
    losetup -d /dev/loop$i 2>/dev/null || true
done
rm -f /tmp/demo_*.img

echo "🚀 Creating demo environment..."

# Create different sized virtual disks for different demos
echo "📱 Creating small demo disk (100MB) - for quick zeros demo..."
dd if=/dev/zero of=/tmp/demo_small.img bs=1M count=100 status=progress

echo "💿 Creating medium demo disk (500MB) - for random data demo..."
dd if=/dev/zero of=/tmp/demo_medium.img bs=1M count=500 status=progress

echo "💾 Creating large demo disk (1GB) - for DoD method demo..."
dd if=/dev/zero of=/tmp/demo_large.img bs=1M count=1024 status=progress

# Set up loop devices
echo "🔧 Setting up loop devices..."
losetup /dev/loop1 /tmp/demo_small.img
losetup /dev/loop2 /tmp/demo_medium.img
losetup /dev/loop3 /tmp/demo_large.img

echo "✅ Demo environment created!"
echo
echo "========================================"
echo "    Demo Scenarios Ready"
echo "========================================"
echo
echo "🎯 Available demo scenarios:"
echo
echo "1. 📱 QUICK DEMO (30 seconds):"
echo "   Device: /dev/loop1 (100MB)"
echo "   Command: sudo trustwipe-cli --wipe /dev/loop1 --method zeros"
echo "   Use case: Show basic wiping functionality"
echo
echo "2. 🔒 SECURITY DEMO (2 minutes):"
echo "   Device: /dev/loop2 (500MB)"
echo "   Command: sudo trustwipe-cli --wipe /dev/loop2 --method random"
echo "   Use case: Show secure random data wiping"
echo
echo "3. 🛡️ MILITARY GRADE DEMO (3 minutes):"
echo "   Device: /dev/loop3 (1GB)"
echo "   Command: sudo trustwipe-cli --wipe /dev/loop3 --method dod"
echo "   Use case: Show DoD 5220.22-M compliance"
echo
echo "4. 🖥️ GUI DEMO:"
echo "   Command: sudo trustwipe"
echo "   Use case: Show professional interface"
echo
echo "📊 Device information:"
lsblk | grep loop

echo
echo "📋 Current demo devices:"
echo "  /dev/loop1 → 100MB (Quick demo)"
echo "  /dev/loop2 → 500MB (Security demo)"  
echo "  /dev/loop3 → 1GB (Military demo)"
echo
echo "🎬 Ready for demonstration!"
echo
echo "⚠️  Remember: Always show device info first:"
echo "   trustwipe-cli --device-info /dev/loop1"
echo
echo "🧹 To cleanup after demo:"
echo "   sudo $0 cleanup"

# If cleanup argument provided
if [ "$1" = "cleanup" ]; then
    echo
    echo "🧹 Cleaning up demo environment..."
    
    for i in {1..3}; do
        losetup -d /dev/loop$i 2>/dev/null && echo "✅ Removed /dev/loop$i" || true
    done
    
    rm -f /tmp/demo_*.img && echo "✅ Removed demo files"
    
    echo "✅ Demo cleanup complete!"
fi
