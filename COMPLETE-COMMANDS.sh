#!/bin/bash
# Master Setup & Run Script for TrustWipe Ultra-Fast
echo "🔥 TrustWipe Ultra-Fast: Complete Setup & Run Guide"
echo "=================================================="
echo ""

# Step 1: Basic Setup
echo "📦 STEP 1: Basic Setup (Run Once)"
echo "chmod +x *.sh"
echo "sudo apt update && sudo apt install -y python3 python3-pip python3-tk"
echo "sudo pip3 install psutil"
echo ""

# Step 2: Fix Line Endings
echo "🔧 STEP 2: Fix Line Endings (Run If Needed)"
echo "sudo apt install -y dos2unix"
echo "dos2unix *.py *.sh"
echo "chmod +x *.sh"
echo ""

# Step 3: Test System
echo "🧪 STEP 3: Quick Test"
echo "./test-now.sh"
echo ""

# Step 4: Usage Commands
echo "🚀 STEP 4: Usage Commands"
echo ""
echo "A. Ultra-Fast CLI (Recommended for 5GB):"
echo "   sudo ./run-ultra-cli.sh --method lightning --device /dev/sdb"
echo "   sudo ./run-ultra-cli.sh --benchmark  # Test performance"
echo ""
echo "B. GUI Version:"
echo "   sudo ./run-ultra-gui.sh  # Nice visual interface"
echo ""
echo "C. Manual Commands:"
echo "   sudo python3 ultra_fast_cli.py --method lightning --device /dev/sdb"
echo "   sudo python3 ultra_fast_gui.py"
echo ""

# Emergency Commands
echo "🆘 EMERGENCY: If Nothing Works"
echo ""
echo "1. One-Command Fix:"
echo "   chmod +x one-command-fix.sh && sudo ./one-command-fix.sh"
echo ""
echo "2. Complete Fix:"
echo "   chmod +x complete-linux-fix.sh && sudo ./complete-linux-fix.sh"
echo ""
echo "3. Manual Python Check:"
echo "   python3 -c \"import psutil, tkinter; print('✅ All dependencies OK')\""
echo ""

# Performance Tips
echo "⚡ PERFORMANCE TIPS for 5GB /dev/sdb:"
echo "• Lightning Method: 15-20 seconds"
echo "• Ultra Zeros: 25-30 seconds"
echo "• Use sudo for max speed"
echo "• Make sure /dev/sdb is unmounted first"
echo ""

echo "🎯 QUICK START (Copy & Paste):"
echo "chmod +x *.sh && ./test-now.sh && sudo ./run-ultra-cli.sh --method lightning --device /dev/sdb"
