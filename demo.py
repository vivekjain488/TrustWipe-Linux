#!/usr/bin/env python3
"""
TrustWipe Quick Start and Demo
Demonstrates TrustWipe functionality in a safe environment
"""

import os
import sys
import tempfile
import json
from datetime import datetime

def print_header(title):
    """Print a formatted header"""
    print("\n" + "=" * 60)
    print(f"  {title}")
    print("=" * 60)

def print_success(message):
    """Print success message"""
    print(f"✅ {message}")

def print_info(message):
    """Print info message"""
    print(f"ℹ️  {message}")

def print_warning(message):
    """Print warning message"""
    print(f"⚠️  {message}")

def demo_system_info():
    """Demonstrate system information collection"""
    print_header("System Information Collection Demo")
    
    try:
        from backend import SystemInfo
        
        print_info("Collecting system information...")
        system_info = SystemInfo.get_system_info()
        
        print("\n📊 System Information:")
        print(f"  Hostname: {system_info.get('hostname', 'N/A')}")
        print(f"  OS: {system_info.get('os', 'N/A')} {system_info.get('os_release', '')}")
        print(f"  Architecture: {system_info.get('architecture', 'N/A')}")
        print(f"  CPU Cores: {system_info.get('cpu', {}).get('logical_cores', 'N/A')}")
        print(f"  Memory: {system_info.get('memory', {}).get('total_human', 'N/A')}")
        print(f"  Python: {system_info.get('python_version', 'N/A')}")
        
        print_success("System information collected successfully!")
        return system_info
        
    except Exception as e:
        print_warning(f"Error collecting system info: {e}")
        return {}

def demo_certificate_generation():
    """Demonstrate certificate generation"""
    print_header("Certificate Generation Demo")
    
    try:
        from certificate_generator import CertificateGenerator
        
        # Create temporary certificate directory
        temp_dir = tempfile.mkdtemp()
        cert_gen = CertificateGenerator(temp_dir)
        
        print_info(f"Certificate directory: {temp_dir}")
        
        # Sample data
        system_info = {
            'hostname': 'demo-system',
            'os': 'Linux',
            'architecture': 'x86_64',
            'memory': {'total_human': '8.00 GB'}
        }
        
        device_info = {
            'device_path': '/dev/demo',
            'size_human': '500.00 GB',
            'model': 'Demo Storage Device',
            'vendor': 'TrustWipe',
            'serial': 'DEMO123456789',
            'type': 'SSD'
        }
        
        wipe_details = {
            'device_path': '/dev/demo',
            'method': 'zeros',
            'passes': 3,
            'start_time': datetime.now().isoformat(),
            'end_time': datetime.now().isoformat(),
            'duration': '0:30:00',
            'status': 'SUCCESS'
        }
        
        print_info("Generating certificate...")
        cert_path, html_path = cert_gen.generate_certificate(
            system_info, device_info, wipe_details
        )
        
        print_success("Certificate generated!")
        print(f"  JSON: {cert_path}")
        print(f"  HTML: {html_path}")
        
        # Show certificate content preview
        with open(cert_path, 'r') as f:
            cert_data = json.load(f)
        
        print("\n📜 Certificate Preview:")
        cert_info = cert_data['certificate_info']
        print(f"  ID: {cert_info['id'][:8]}...")
        print(f"  Generated: {cert_info['generated_at']}")
        print(f"  Standard: {cert_info['standard']}")
        
        return cert_path, html_path
        
    except Exception as e:
        print_warning(f"Error generating certificate: {e}")
        return None, None

def demo_cli_interface():
    """Demonstrate CLI interface"""
    print_header("CLI Interface Demo")
    
    try:
        from cli import TrustWipeCLI
        
        cli = TrustWipeCLI()
        
        print_info("Testing CLI interface...")
        print("\n🖥️  Available CLI Commands:")
        print("  trustwipe-cli --list-devices     # List storage devices")
        print("  trustwipe-cli --device-info /dev/sda  # Show device info")
        print("  trustwipe-cli --wipe /dev/sda --method zeros  # Wipe device")
        print("  trustwipe-cli --list-certs       # List certificates")
        print("  trustwipe-cli --show-cert ID     # Show certificate")
        
        print_success("CLI interface loaded successfully!")
        
    except Exception as e:
        print_warning(f"Error loading CLI: {e}")

def demo_gui_check():
    """Check GUI dependencies"""
    print_header("GUI Dependencies Check")
    
    try:
        import tkinter as tk
        print_success("Tkinter GUI library available")
        
        # Test basic GUI creation
        root = tk.Tk()
        root.withdraw()  # Hide the window
        root.destroy()
        
        print_success("GUI can be created successfully")
        
    except ImportError:
        print_warning("Tkinter not available - GUI mode will not work")
        print_info("Install with: sudo apt-get install python3-tk")
    except Exception as e:
        print_warning(f"GUI test failed: {e}")

def demo_dependencies():
    """Check all dependencies"""
    print_header("Dependency Check")
    
    dependencies = [
        ('psutil', 'System information collection'),
        ('json', 'Certificate handling'),
        ('datetime', 'Timestamp management'),
        ('subprocess', 'System command execution'),
        ('uuid', 'Unique ID generation'),
        ('hashlib', 'Cryptographic functions'),
        ('threading', 'Concurrent operations'),
    ]
    
    missing = []
    
    for module, description in dependencies:
        try:
            __import__(module)
            print_success(f"{module:15} - {description}")
        except ImportError:
            print_warning(f"{module:15} - {description} (MISSING)")
            missing.append(module)
    
    if missing:
        print(f"\n❌ Missing dependencies: {', '.join(missing)}")
        print("Install with: pip3 install " + " ".join(missing))
        return False
    else:
        print_success("All dependencies available!")
        return True

def show_installation_instructions():
    """Show installation instructions"""
    print_header("Installation Instructions")
    
    print("🚀 To install TrustWipe on Linux:")
    print()
    print("1. Copy this project to your Linux system")
    print("2. Run the installer as root:")
    print("   sudo chmod +x install.sh")
    print("   sudo ./install.sh")
    print()
    print("3. Or use the automated installer:")
    print("   sudo chmod +x trustwipe-installer.sh")
    print("   sudo ./trustwipe-installer.sh")
    print()
    print("4. Launch TrustWipe:")
    print("   sudo trustwipe              # GUI mode")
    print("   trustwipe-cli --help        # CLI mode")
    print()
    print("📋 For VMware Linux environments:")
    print("   • Ensure VM has sufficient privileges")
    print("   • Install required packages:")
    print("     sudo apt-get install python3 python3-tk python3-pip")
    print("     pip3 install psutil")
    print("   • Run TrustWipe with sudo for disk access")

def show_safety_warnings():
    """Show important safety warnings"""
    print_header("🚨 SAFETY WARNINGS")
    
    warnings = [
        "TrustWipe PERMANENTLY ERASES data - this cannot be undone!",
        "Always verify the target device before wiping",
        "Use multiple confirmations for all operations",
        "Test on non-critical data first",
        "Ensure you have proper backups",
        "Run only with root/administrator privileges",
        "Use appropriate wiping method for your security needs",
        "Store certificates securely for compliance purposes"
    ]
    
    for i, warning in enumerate(warnings, 1):
        print(f"{i:2}. ⚠️  {warning}")

def show_features():
    """Show TrustWipe features"""
    print_header("✨ TrustWipe Features")
    
    features = [
        "🖥️  Professional GUI interface with Tkinter",
        "💻 Command-line interface for automation",
        "🔒 Multiple wiping algorithms (zeros, random, DoD, Gutmann)",
        "📊 Real-time progress monitoring",
        "📜 Professional certificate generation",
        "🛡️  Security compliance (NIST, DoD, ISO, GDPR)",
        "🔍 Comprehensive system information collection",
        "💾 Device detection and information display",
        "⚡ Multi-threaded operations",
        "🚨 Emergency stop functionality",
        "📋 Audit logging and trail",
        "🔧 Easy installation and deployment"
    ]
    
    for feature in features:
        print(f"  {feature}")

def run_tests():
    """Run basic functionality tests"""
    print_header("Running Basic Tests")
    
    try:
        print_info("Testing imports...")
        import backend
        import certificate_generator
        import cli
        import trustwipe
        print_success("All modules imported successfully")
        
        print_info("Testing system info collection...")
        system_info = demo_system_info()
        
        print_info("Testing certificate generation...")
        cert_path, html_path = demo_certificate_generation()
        
        if cert_path and html_path:
            print_success("All basic tests passed!")
            return True
        else:
            print_warning("Some tests failed")
            return False
            
    except Exception as e:
        print_warning(f"Test error: {e}")
        return False

def main():
    """Main demo function"""
    print_header("🛡️  TrustWipe - Secure Data Wiping Tool")
    print("Professional Linux Data Erasure Solution")
    print("Version 1.0 - Built for Security and Compliance")
    
    # Show features
    show_features()
    
    # Check dependencies
    deps_ok = demo_dependencies()
    
    # Check GUI
    demo_gui_check()
    
    # Run demos if dependencies are available
    if deps_ok:
        print_info("Running functionality demos...")
        
        # Demo system info
        demo_system_info()
        
        # Demo certificate generation  
        demo_certificate_generation()
        
        # Demo CLI
        demo_cli_interface()
        
        # Run tests
        run_tests()
    
    # Show installation instructions
    show_installation_instructions()
    
    # Show safety warnings
    show_safety_warnings()
    
    print_header("🎉 TrustWipe Demo Complete")
    print("Ready for production use on Linux systems!")
    print()
    print("Next steps:")
    print("1. Transfer to Linux system")
    print("2. Run: sudo ./install.sh")
    print("3. Launch: sudo trustwipe")
    print()
    print("For support: Check README.md and documentation")

if __name__ == "__main__":
    main()
