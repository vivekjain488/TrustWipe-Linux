#!/bin/bash
# TrustWipe Ultra-Fast CLI Launcher
if [ "$EUID" -ne 0 ]; then
    echo "❌ Need root privileges: sudo ./run-ultra-cli.sh [options]"
    exit 1
fi
export PYTHONPATH="$PWD:$PYTHONPATH"
python3 ./ultra_fast_cli.py "$@"
