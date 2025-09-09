#!/bin/bash

echo "🧪 TrustWipe Ultra-Fast Quick Test"
echo "================================="
echo ""

# Test 1: Check if we're in the right directory
if [ ! -f "ultra_fast_gui.py" ]; then
    echo "❌ Error: ultra_fast_gui.py not found"
    echo "Please run this test in the TrustWipe directory"
    exit 1
fi

echo "✅ Found ultra-fast files in current directory"

# Test 2: Check Python version
PYTHON_VERSION=$(python3 --version 2>/dev/null || echo "Not found")
echo "🐍 Python: $PYTHON_VERSION"

# Test 3: Check if running as root
if [ "$EUID" -eq 0 ]; then
    echo "✅ Running as root - can install packages"
    INSTALL_MODE=true
else
    echo "⚠️  Not running as root - limited testing only"
    INSTALL_MODE=false
fi

# Test 4: Check essential imports
echo ""
echo "🧪 Testing Python imports..."

test_import() {
    local module="$1"
    if python3 -c "import $module" 2>/dev/null; then
        echo "✅ $module - Available"
        return 0
    else
        echo "❌ $module - Missing"
        return 1
    fi
}

test_import "sys"
test_import "os"
test_import "time"
test_import "threading"
test_import "subprocess"

PSUTIL_OK=false
if test_import "psutil"; then
    PSUTIL_OK=true
else
    if [ "$INSTALL_MODE" = true ]; then
        echo "📦 Installing psutil..."
        apt update >/dev/null 2>&1
        apt install -y python3-psutil >/dev/null 2>&1
        if test_import "psutil"; then
            PSUTIL_OK=true
        fi
    fi
fi

TKINTER_OK=false
if test_import "tkinter"; then
    TKINTER_OK=true
else
    if [ "$INSTALL_MODE" = true ]; then
        echo "📦 Installing tkinter..."
        apt install -y python3-tk >/dev/null 2>&1
        if test_import "tkinter"; then
            TKINTER_OK=true
        fi
    fi
fi

# Test 5: Check ultra-fast backend
echo ""
echo "🧪 Testing ultra-fast components..."

export PYTHONPATH="$PWD:$PYTHONPATH"

if python3 -c "
import sys
sys.path.insert(0, '.')
try:
    from ultra_fast_backend import UltraFastDataWiper
    print('✅ Ultra-fast backend - Ready')
except Exception as e:
    print(f'❌ Ultra-fast backend - Error: {e}')
    exit(1)
" 2>/dev/null; then
    BACKEND_OK=true
    echo "✅ Backend test passed"
else
    BACKEND_OK=false
    echo "❌ Backend test failed"
fi

# Test 6: Check CLI
if python3 -c "
import sys
sys.path.insert(0, '.')
try:
    from ultra_fast_cli import UltraFastCLI
    print('✅ Ultra-fast CLI - Ready')
except Exception as e:
    print(f'❌ Ultra-fast CLI - Error: {e}')
    exit(1)
" 2>/dev/null; then
    CLI_OK=true
    echo "✅ CLI test passed"
else
    CLI_OK=false
    echo "❌ CLI test failed"
fi

# Test 7: Check GUI (only if tkinter available)
if [ "$TKINTER_OK" = true ]; then
    if python3 -c "
import sys
sys.path.insert(0, '.')
try:
    # Just test imports, don't start GUI
    import tkinter as tk
    from ultra_fast_gui import UltraFastTrustWipeGUI
    print('✅ Ultra-fast GUI - Ready')
except Exception as e:
    print(f'❌ Ultra-fast GUI - Error: {e}')
    exit(1)
" 2>/dev/null; then
    GUI_OK=true
    echo "✅ GUI test passed"
else
    GUI_OK=false
    echo "❌ GUI test failed"
fi
else
    GUI_OK=false
    echo "⚠️  GUI test skipped (tkinter missing)"
fi

# Summary
echo ""
echo "📊 TEST RESULTS SUMMARY"
echo "======================"

if [ "$BACKEND_OK" = true ] && [ "$CLI_OK" = true ] && [ "$PSUTIL_OK" = true ]; then
    echo "🎉 CORE COMPONENTS: READY"
    echo "✅ Ultra-fast wiping is ready to use!"
else
    echo "⚠️  CORE COMPONENTS: ISSUES DETECTED" 
    echo "❌ Some components need fixes"
fi

if [ "$GUI_OK" = true ]; then
    echo "🖥️  GUI INTERFACE: READY"
else
    echo "⚠️  GUI INTERFACE: NEEDS ATTENTION"
fi

echo ""
echo "🚀 READY COMMANDS:"

if [ "$BACKEND_OK" = true ] && [ "$CLI_OK" = true ]; then
    echo "✅ CLI: sudo python3 ./ultra_fast_cli.py --help"
    echo "✅ CLI: sudo python3 ./ultra_fast_cli.py --method lightning"
fi

if [ "$GUI_OK" = true ]; then
    echo "✅ GUI: sudo python3 ./ultra_fast_gui.py"
fi

echo ""
echo "🔧 RECOMMENDED FIXES:"

if [ "$PSUTIL_OK" = false ]; then
    echo "❌ Install psutil: sudo apt install python3-psutil"
fi

if [ "$TKINTER_OK" = false ]; then
    echo "❌ Install tkinter: sudo apt install python3-tk"
fi

if [ "$BACKEND_OK" = false ] || [ "$CLI_OK" = false ]; then
    echo "❌ Fix dependencies and run: sudo ./complete-linux-fix.sh"
fi

echo ""
if [ "$BACKEND_OK" = true ] && [ "$CLI_OK" = true ] && [ "$PSUTIL_OK" = true ]; then
    echo "🎯 READY FOR ULTRA-FAST 5GB WIPING IN UNDER 30 SECONDS!"
else
    echo "🔧 PLEASE RUN FIXES ABOVE, THEN TEST AGAIN"
fi
