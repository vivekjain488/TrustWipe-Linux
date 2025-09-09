#!/bin/bash

echo "🔒 TrustWipe SAFE - Quick Setup"
echo "============================="
echo ""
echo "Making all SAFE files executable..."

# Make all Python files executable
chmod +x safe_trustwipe.py
chmod +x safe_backend.py
chmod +x safety_manager.py
chmod +x safe_cli.py
chmod +x certificate_generator.py

# Make installation script executable
chmod +x install_safe.sh

echo "✅ All files are now executable!"
echo ""
echo "🚀 Next Steps:"
echo "1. Run installation: sudo ./install_safe.sh"
echo "2. Launch GUI: sudo trustwipe-safe-gui"
echo "3. Or use CLI: sudo trustwipe-safe --help"
echo ""
echo "🛡️ SAFETY FEATURES:"
echo "• Cannot wipe system drives"
echo "• OS protection enabled"
echo "• Smart personal data detection"
echo "• Multiple safety confirmations"
echo ""
echo "⚠️  IMPORTANT: This SAFE version prevents OS destruction!"
echo "   Your Linux installation will always be protected."
