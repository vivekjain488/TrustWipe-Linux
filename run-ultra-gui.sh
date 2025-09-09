#!/bin/bash
# TrustWipe Ultra-Fast GUI Launcher
if [ "$EUID" -ne 0 ]; then
    echo "❌ Need root privileges: sudo ./run-ultra-gui.sh"
    exit 1
fi
export PYTHONPATH="$PWD:$PYTHONPATH"
echo "⚡ Starting TrustWipe Ultra-Fast GUI..."
python3 ./ultra_fast_gui.py
