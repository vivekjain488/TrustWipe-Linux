#!/bin/bash
# Quick Test Script
echo "🧪 TrustWipe Ultra-Fast Quick Test"
echo "================================="
export PYTHONPATH="$PWD:$PYTHONPATH"

echo -n "Testing Backend: "
if python3 -c "from ultra_fast_backend import UltraFastDataWiper" 2>/dev/null; then
    echo "✅ OK"
    BACKEND_OK=true
else
    echo "❌ FAIL"
    BACKEND_OK=false
fi

echo -n "Testing CLI: "
if python3 -c "from ultra_fast_cli import UltraFastCLI" 2>/dev/null; then
    echo "✅ OK"
    CLI_OK=true
else
    echo "❌ FAIL"
    CLI_OK=false
fi

echo -n "Testing GUI: "
if python3 -c "import tkinter; from ultra_fast_gui import UltraFastTrustWipeGUI" 2>/dev/null; then
    echo "✅ OK"
    GUI_OK=true
else
    echo "❌ FAIL"
    GUI_OK=false
fi

echo ""
if [ "$BACKEND_OK" = true ] && [ "$CLI_OK" = true ]; then
    echo "🎉 READY TO USE!"
    echo ""
    echo "🚀 COMMANDS:"
    echo "  sudo ./run-ultra-cli.sh --method lightning"
    echo "  sudo ./run-ultra-cli.sh --benchmark"
    if [ "$GUI_OK" = true ]; then
        echo "  sudo ./run-ultra-gui.sh"
    fi
else
    echo "❌ NEEDS FIXING - Run the setup commands below"
fi
