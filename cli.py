#!/usr/bin/env python3
"""
TrustWipe Command Line Interface
Alternative CLI interface for TrustWipe when GUI is not available
"""

import argparse
import sys
import os
import json
from datetime import datetime
import signal
import threading

# Import our modules
from backend import DataWiper, SystemInfo
from certificate_generator import CertificateGenerator

class TrustWipeCLI:
    def __init__(self):
        self.wiper = None
        self.interrupted = False
        
        # Set up signal handlers
        signal.signal(signal.SIGINT, self.signal_handler)
        signal.signal(signal.SIGTERM, self.signal_handler)
    
    def signal_handler(self, signum, frame):
        """Handle interrupt signals"""
        print("\n\n🛑 Interrupt signal received. Stopping wipe operation...")
        self.interrupted = True
        if self.wiper:
            self.wiper.stop()
        sys.exit(1)
    
    def progress_callback(self, message, progress=None):
        """Progress callback for wiping operations"""
        if progress is not None:
            print(f"📊 Progress: {message} ({progress}%)")
        else:
            print(f"📊 {message}")
    
    def list_devices(self):
        """List available storage devices"""
        print("🔍 Available storage devices:")
        print("=" * 50)
        
        try:
            import subprocess
            result = subprocess.run(['lsblk', '-d', '-o', 'NAME,SIZE,TYPE,MODEL'], 
                                  capture_output=True, text=True)
            
            if result.returncode == 0:
                lines = result.stdout.strip().split('\n')
                print(lines[0])  # Header
                print("-" * 50)
                
                devices = []
                for line in lines[1:]:
                    if line.strip():
                        parts = line.split()
                        if len(parts) >= 3 and parts[2] == 'disk':
                            device_path = f"/dev/{parts[0]}"
                            devices.append(device_path)
                            print(line)
                
                print(f"\n📋 Found {len(devices)} storage devices")
                return devices
            else:
                print("❌ Failed to list devices")
                return []
                
        except Exception as e:
            print(f"❌ Error listing devices: {e}")
            return []
    
    def show_device_info(self, device_path):
        """Show detailed information about a device"""
        print(f"📊 Device Information: {device_path}")
        print("=" * 50)
        
        try:
            device_info = SystemInfo.get_device_info(device_path)
            
            for key, value in device_info.items():
                if key != 'error':
                    formatted_key = key.replace('_', ' ').title()
                    print(f"{formatted_key:20}: {value}")
            
            if 'error' in device_info:
                print(f"⚠️  Error: {device_info['error']}")
        
        except Exception as e:
            print(f"❌ Error getting device info: {e}")
    
    def wipe_device(self, device_path, method, passes, force=False):
        """Wipe a device"""
        if not os.path.exists(device_path):
            print(f"❌ Device {device_path} does not exist")
            return False
        
        if os.geteuid() != 0:
            print("❌ This operation requires root privileges. Run with sudo.")
            return False
        
        # Show device information
        print(f"\n📋 Target Device: {device_path}")
        self.show_device_info(device_path)
        print()
        
        # Confirmation
        if not force:
            print("⚠️  WARNING: This will permanently erase ALL data on the device!")
            print(f"   Device: {device_path}")
            print(f"   Method: {method}")
            print(f"   Passes: {passes}")
            print()
            
            confirm = input("Type 'YES' to confirm deletion: ")
            if confirm != 'YES':
                print("❌ Operation cancelled")
                return False
            
            # Second confirmation
            device_name = device_path.split('/')[-1].upper()
            confirm2 = input(f"Type 'WIPE {device_name}' to proceed: ")
            expected = f"WIPE {device_name}"
            if confirm2 != expected:
                print("❌ Confirmation failed. Operation cancelled")
                return False
        
        # Start wiping
        print(f"\n🚀 Starting wipe operation...")
        print(f"   Started: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        print()
        
        try:
            # Collect system info before wiping
            system_info = SystemInfo.get_system_info()
            device_info = SystemInfo.get_device_info(device_path)
            
            start_time = datetime.now()
            
            # Create wiper and start
            self.wiper = DataWiper(device_path, method, passes, self.progress_callback)
            success = self.wiper.wipe()
            
            end_time = datetime.now()
            duration = end_time - start_time
            
            if success and not self.interrupted:
                print(f"\n✅ Wipe completed successfully!")
                print(f"   Duration: {duration}")
                
                # Generate certificate
                wipe_details = {
                    'device_path': device_path,
                    'method': method,
                    'passes': passes,
                    'start_time': start_time.isoformat(),
                    'end_time': end_time.isoformat(),
                    'duration': str(duration),
                    'status': 'SUCCESS'
                }
                
                cert_gen = CertificateGenerator()
                cert_path, html_path = cert_gen.generate_certificate(
                    system_info, device_info, wipe_details
                )
                
                print(f"\n📜 Certificate generated:")
                print(f"   JSON: {cert_path}")
                print(f"   HTML: {html_path}")
                
                return True
            else:
                print(f"\n❌ Wipe operation failed or was interrupted")
                return False
        
        except Exception as e:
            print(f"\n❌ Wipe failed: {e}")
            return False
    
    def list_certificates(self):
        """List all certificates"""
        cert_gen = CertificateGenerator()
        certificates = cert_gen.list_certificates()
        
        if not certificates:
            print("📜 No certificates found")
            return
        
        print(f"📜 Found {len(certificates)} certificates:")
        print("=" * 80)
        print(f"{'ID':<8} {'Date':<20} {'Device':<15} {'Method':<10} {'Status':<10}")
        print("-" * 80)
        
        for cert in certificates:
            cert_id = cert['certificate_id'][:8] if cert['certificate_id'] != 'Unknown' else 'Unknown'
            date = cert['generated_at'][:19] if cert['generated_at'] != 'Unknown' else 'Unknown'
            device = cert['device'].split('/')[-1] if cert['device'] != 'Unknown' else 'Unknown'
            method = cert['method'].upper() if cert['method'] != 'Unknown' else 'Unknown'
            status = cert['status'] if cert['status'] != 'Unknown' else 'Unknown'
            
            print(f"{cert_id:<8} {date:<20} {device:<15} {method:<10} {status:<10}")
        
        print(f"\nCertificate directory: {cert_gen.cert_dir}")
    
    def show_certificate(self, cert_id):
        """Show detailed certificate information"""
        cert_gen = CertificateGenerator()
        certificates = cert_gen.list_certificates()
        
        # Find certificate by ID (partial match)
        cert = None
        for c in certificates:
            if c['certificate_id'].startswith(cert_id):
                cert = c
                break
        
        if not cert:
            print(f"❌ Certificate not found: {cert_id}")
            return
        
        # Load and display certificate
        try:
            with open(cert['path'], 'r') as f:
                cert_data = json.load(f)
            
            print(f"📜 Certificate Details")
            print("=" * 50)
            
            # Certificate info
            cert_info = cert_data.get('certificate_info', {})
            print(f"ID: {cert_info.get('id', 'N/A')}")
            print(f"Generated: {cert_info.get('generated_at', 'N/A')}")
            print(f"Version: {cert_info.get('version', 'N/A')}")
            print()
            
            # Wipe details
            wipe_details = cert_data.get('wipe_details', {})
            print("Wipe Details:")
            print(f"  Device: {wipe_details.get('device_path', 'N/A')}")
            print(f"  Method: {wipe_details.get('method', 'N/A')}")
            print(f"  Passes: {wipe_details.get('passes', 'N/A')}")
            print(f"  Duration: {wipe_details.get('duration', 'N/A')}")
            print(f"  Status: {wipe_details.get('status', 'N/A')}")
            print()
            
            # System info
            system_info = cert_data.get('system_info', {})
            print("System Information:")
            print(f"  Hostname: {system_info.get('hostname', 'N/A')}")
            print(f"  OS: {system_info.get('os', 'N/A')} {system_info.get('os_release', '')}")
            print(f"  Architecture: {system_info.get('architecture', 'N/A')}")
            print()
            
            # Verification
            verification = cert_data.get('verification', {})
            print("Verification:")
            print(f"  Algorithm: {verification.get('algorithm', 'N/A')}")
            print(f"  Checksum: {verification.get('checksum', 'N/A')[:32]}...")
            print()
            
            print(f"Files:")
            print(f"  JSON: {cert['path']}")
            print(f"  HTML: {cert['html_path']}")
            
        except Exception as e:
            print(f"❌ Error reading certificate: {e}")

def main():
    """Main CLI function"""
    parser = argparse.ArgumentParser(
        description="TrustWipe - Secure Data Wiping Tool (CLI)",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  trustwipe-cli --list-devices                    # List available devices
  trustwipe-cli --device-info /dev/sdb            # Show device information
  trustwipe-cli --wipe /dev/sdb --method zeros    # Wipe device with zeros
  trustwipe-cli --list-certs                      # List certificates
  trustwipe-cli --show-cert 12345678              # Show certificate details

Wiping Methods:
  zeros     - Overwrite with zeros (fastest)
  random    - Overwrite with random data (secure)
  dod       - DoD 5220.22-M standard (3 passes)
  gutmann   - Gutmann method (35 passes, most secure)

WARNING: Data wiping is irreversible. Use with extreme caution!
        """
    )
    
    # Device operations
    parser.add_argument('--list-devices', action='store_true',
                       help='List available storage devices')
    
    parser.add_argument('--device-info', metavar='DEVICE',
                       help='Show information about a device')
    
    parser.add_argument('--wipe', metavar='DEVICE',
                       help='Wipe the specified device')
    
    parser.add_argument('--method', choices=['zeros', 'random', 'dod', 'gutmann'],
                       default='zeros', help='Wiping method (default: zeros)')
    
    parser.add_argument('--passes', type=int, default=3,
                       help='Number of passes (default: 3, ignored for gutmann)')
    
    parser.add_argument('--force', action='store_true',
                       help='Force wipe without confirmation prompts (USE WITH CAUTION!)')
    
    # Certificate operations
    parser.add_argument('--list-certs', action='store_true',
                       help='List all certificates')
    
    parser.add_argument('--show-cert', metavar='CERT_ID',
                       help='Show certificate details (partial ID match)')
    
    # Version
    parser.add_argument('--version', action='version', version='TrustWipe CLI 1.0')
    
    args = parser.parse_args()
    
    # Create CLI instance
    cli = TrustWipeCLI()
    
    # Handle arguments
    if args.list_devices:
        cli.list_devices()
    
    elif args.device_info:
        cli.show_device_info(args.device_info)
    
    elif args.wipe:
        success = cli.wipe_device(args.wipe, args.method, args.passes, args.force)
        sys.exit(0 if success else 1)
    
    elif args.list_certs:
        cli.list_certificates()
    
    elif args.show_cert:
        cli.show_certificate(args.show_cert)
    
    else:
        parser.print_help()

if __name__ == "__main__":
    main()
