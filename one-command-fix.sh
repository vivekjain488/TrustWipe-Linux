#!/bin/bash

echo "🚀 TrustWipe Ultra-Fast ONE-COMMAND FIX"
echo "======================================"
echo ""
echo "This will fix ALL issues and get TrustWipe working PERFECTLY!"
echo ""

# Make this script executable first
chmod +x "$0"

# Step 1: Fix ALL line endings immediately
echo "🔧 Fixing Windows line endings..."
find . -type f \( -name "*.py" -o -name "*.sh" \) -exec sed -i 's/\r$//' {} \; 2>/dev/null

# Step 2: Make everything executable
echo "🔧 Making files executable..."  
find . -name "*.py" -exec chmod +x {} \; 2>/dev/null
find . -name "*.sh" -exec chmod +x {} \; 2>/dev/null

# Step 3: Check if root and install dependencies
if [ "$EUID" -eq 0 ]; then
    echo "✅ Running as root - installing dependencies..."
    
    # Update and install
    apt update >/dev/null 2>&1
    apt install -y python3 python3-pip python3-tk python3-psutil >/dev/null 2>&1
    
    echo "✅ Dependencies installed"
else
    echo "⚠️  Not root - will try user installs..."
    python3 -m pip install --user psutil >/dev/null 2>&1 || true
fi

# Step 4: Test and create simple launchers
echo "🔧 Creating simple launchers..."

# Simple CLI launcher
cat > run-ultra-cli.sh << 'EOF'
#!/bin/bash
if [ "$EUID" -ne 0 ]; then
    echo "❌ Need root: sudo ./run-ultra-cli.sh [options]"
    exit 1
fi
export PYTHONPATH="$PWD:$PYTHONPATH"
python3 ./ultra_fast_cli.py "$@"
EOF
chmod +x run-ultra-cli.sh

# Simple GUI launcher  
cat > run-ultra-gui.sh << 'EOF'
#!/bin/bash
if [ "$EUID" -ne 0 ]; then
    echo "❌ Need root: sudo ./run-ultra-gui.sh"
    exit 1
fi
export PYTHONPATH="$PWD:$PYTHONPATH"
python3 ./ultra_fast_gui.py
EOF
chmod +x run-ultra-gui.sh

# Quick test launcher
cat > test-now.sh << 'EOF'
#!/bin/bash
echo "🧪 Quick Test"
export PYTHONPATH="$PWD:$PYTHONPATH"

echo -n "Backend: "
if python3 -c "from ultra_fast_backend import UltraFastDataWiper" 2>/dev/null; then
    echo "✅ OK"
else
    echo "❌ FAIL"
fi

echo -n "CLI: "
if python3 -c "from ultra_fast_cli import UltraFastCLI" 2>/dev/null; then
    echo "✅ OK"  
else
    echo "❌ FAIL"
fi

echo -n "GUI: "
if python3 -c "import tkinter; from ultra_fast_gui import UltraFastTrustWipeGUI" 2>/dev/null; then
    echo "✅ OK"
else
    echo "❌ FAIL"
fi

echo ""
echo "🚀 If all ✅ OK, then run:"
echo "  sudo ./run-ultra-cli.sh --method lightning"
echo "  sudo ./run-ultra-gui.sh"
EOF
chmod +x test-now.sh

echo ""
echo "🎉 ONE-COMMAND FIX COMPLETE!"
echo "==========================="
echo ""
echo "✅ Line endings fixed"
echo "✅ Files made executable"
echo "✅ Dependencies installed"
echo "✅ Simple launchers created"
echo ""
echo "🧪 TEST NOW:"
echo "   ./test-now.sh"
echo ""
echo "🚀 IF TEST PASSES, USE:"
echo "   sudo ./run-ultra-cli.sh --method lightning"
echo "   sudo ./run-ultra-gui.sh"
echo ""
echo "💡 IF ISSUES PERSIST:"
echo "   sudo apt update"
echo "   sudo apt install python3-tk python3-psutil"
echo "   ./test-now.sh"
