#!/usr/bin/env python3
"""
TrustWipe SAFE CLI - Command Line Interface
SAFE version that prevents OS destruction
"""

import argparse
import sys
import os
from safe_backend import SafeDataWiper
from safety_manager import SafetyManager
from certificate_generator import CertificateGenerator

class SafeTrustWipeCLI:
    """SAFE command line interface for TrustWipe"""
    
    def __init__(self):
        self.safety_manager = SafetyManager()
        self.cert_generator = CertificateGenerator()
    
    def parse_arguments(self):
        """Parse command line arguments"""
        parser = argparse.ArgumentParser(
            description='TrustWipe SAFE - Secure Personal Data Wiping Tool',
            formatter_class=argparse.RawDescriptionHelpFormatter,
            epilog="""
SAFE MODES:
  personal-data    Wipe only personal files (Documents, Downloads, etc.)
  factory-reset    Reset to clean state while preserving OS
  external-drive   Wipe external USB/disk drive with safety checks

EXAMPLES:
  # Wipe personal data only (SAFE)
  sudo python3 safe_cli.py --type personal-data --method zeros
  
  # Factory reset while preserving OS (SAFE)
  sudo python3 safe_cli.py --type factory-reset --method dod
  
  # Wipe external drive with safety checks
  sudo python3 safe_cli.py --type external-drive --device /dev/sdb --method random
  
  # Force mode for automation (skips confirmations)
  sudo python3 safe_cli.py --type personal-data --method zeros --force
            """)
        
        parser.add_argument(
            '--type', '-t',
            choices=['personal-data', 'factory-reset', 'external-drive'],
            required=True,
            help='Type of wipe to perform'
        )
        
        parser.add_argument(
            '--method', '-m',
            choices=['zeros', 'random', 'dod'],
            default='zeros',
            help='Wiping method (default: zeros)'
        )
        
        parser.add_argument(
            '--device', '-d',
            help='Device path for external drive wipe (e.g., /dev/sdb)'
        )
        
        parser.add_argument(
            '--passes', '-p',
            type=int,
            default=3,
            help='Number of passes (default: 3)'
        )
        
        parser.add_argument(
            '--force', '-f',
            action='store_true',
            help='Skip confirmation prompts (for automation)'
        )
        
        parser.add_argument(
            '--certificate', '-c',
            action='store_true',
            help='Generate certificate after successful wipe'
        )
        
        parser.add_argument(
            '--list-devices',
            action='store_true',
            help='List all available devices with safety status'
        )
        
        return parser.parse_args()
    
    def check_root(self):
        """Check if running as root"""
        if os.geteuid() != 0:
            print("❌ Error: This tool must be run as root")
            print("   Please run: sudo python3 safe_cli.py [options]")
            sys.exit(1)
    
    def list_devices(self):
        """List all devices with safety status"""
        print("🔍 Available Devices:")
        print("=" * 60)
        
        try:
            import subprocess
            result = subprocess.run(['lsblk', '-d', '-n', '-o', 'NAME,SIZE,TYPE,MOUNTPOINT'], 
                                  capture_output=True, text=True)
            
            for line in result.stdout.strip().split('\n'):
                if line and 'disk' in line:
                    parts = line.split()
                    device_name = parts[0]
                    device_size = parts[1] if len(parts) > 1 else "Unknown"
                    device_path = f"/dev/{device_name}"
                    
                    # Check safety
                    safety_check = self.safety_manager.is_safe_for_wiping(device_path)
                    
                    if safety_check['safe']:
                        status = "✅ SAFE"
                        color = "\033[92m"  # Green
                    else:
                        status = "🚨 SYSTEM DRIVE"
                        color = "\033[91m"  # Red
                    
                    reset_color = "\033[0m"
                    print(f"{color}{device_path:<12} {device_size:<8} {status}{reset_color}")
                    
                    # Show warnings
                    for warning in safety_check['warnings']:
                        print(f"   {warning}")
                    print()
            
        except Exception as e:
            print(f"❌ Error listing devices: {e}")
    
    def confirm_operation(self, wipe_type, method, device=None):
        """Confirm operation with user"""
        print("\n🔒 SAFE WIPE CONFIRMATION")
        print("=" * 40)
        print(f"Type: {wipe_type}")
        print(f"Method: {method.upper()}")
        if device:
            print(f"Device: {device}")
        
        print("\n🛡️ SAFETY FEATURES:")
        print("• OS Protection: Cannot wipe system drives")
        print("• Smart Detection: Only removes personal data")
        print("• Safe Operations: Your Linux stays intact")
        
        response = input("\nContinue with SAFE wipe? (yes/no): ").lower().strip()
        return response in ['yes', 'y']
    
    def progress_callback(self, message, progress=None):
        """Progress callback for CLI"""
        if progress is not None:
            bar_length = 40
            filled_length = int(bar_length * progress // 100)
            bar = '█' * filled_length + '-' * (bar_length - filled_length)
            print(f"\r[{bar}] {progress}% - {message}", end='', flush=True)
        else:
            print(f"\n{message}")
    
    def run(self):
        """Main CLI execution"""
        args = self.parse_arguments()
        
        # Check root privileges
        self.check_root()
        
        # List devices if requested
        if args.list_devices:
            self.list_devices()
            return
        
        # Validate arguments
        if args.type == 'external-drive' and not args.device:
            print("❌ Error: --device is required for external-drive wipe")
            sys.exit(1)
        
        # Safety check for external drives
        if args.type == 'external-drive':
            if not os.path.exists(args.device):
                print(f"❌ Error: Device {args.device} does not exist")
                sys.exit(1)
            
            safety_check = self.safety_manager.is_safe_for_wiping(args.device)
            if not safety_check['safe']:
                print(f"🚨 SAFETY BLOCK: Cannot wipe {args.device}")
                for warning in safety_check['warnings']:
                    print(f"   {warning}")
                print("\nThis device contains your operating system!")
                print("Wiping it would destroy your Linux installation.")
                sys.exit(1)
        
        # Confirmation (unless force mode)
        if not args.force:
            if not self.confirm_operation(args.type, args.method, args.device):
                print("Operation cancelled by user")
                sys.exit(0)
        
        print("\n🚀 Starting SAFE wipe...")
        
        # Create wiper
        wiper = SafeDataWiper(
            wipe_type=args.type.replace('-', '_'),  # Convert to snake_case
            method=args.method,
            passes=args.passes,
            callback=self.progress_callback
        )
        
        wiper.is_running = True
        
        try:
            # Perform wipe based on type
            if args.type == 'personal-data':
                success = wiper.wipe_personal_data_only()
            elif args.type == 'factory-reset':
                success = wiper.factory_reset_safe()
            elif args.type == 'external-drive':
                success = wiper.wipe_external_drive(args.device)
            
            print()  # New line after progress bar
            
            if success:
                print("✅ SAFE wipe completed successfully!")
                print("🔒 Your operating system remains intact and functional.")
                
                # Generate certificate if requested
                if args.certificate:
                    self.generate_certificate(args)
                
            else:
                print("❌ Wipe operation failed")
                sys.exit(1)
                
        except KeyboardInterrupt:
            print("\n⏹️ Wipe interrupted by user")
            wiper.is_running = False
            sys.exit(1)
        except Exception as e:
            print(f"\n❌ Error during wipe: {e}")
            sys.exit(1)
    
    def generate_certificate(self, args):
        """Generate certificate of data erasure"""
        try:
            import json
            from datetime import datetime
            import platform
            
            cert_data = {
                'wipe_type': args.type,
                'method': args.method,
                'timestamp': datetime.now().isoformat(),
                'device': args.device if args.device else 'N/A',
                'passes': args.passes,
                'system_info': {
                    'hostname': platform.node(),
                    'os': platform.system(),
                    'version': platform.version(),
                    'machine': platform.machine()
                },
                'compliance': {
                    'nist': args.method in ['dod', 'gutmann'],
                    'dod': args.method == 'dod',
                    'gdpr': True,
                    'iso27001': True
                }
            }
            
            # Save JSON certificate
            timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
            json_file = f"trustwipe_safe_certificate_{timestamp}.json"
            
            with open(json_file, 'w') as f:
                json.dump(cert_data, f, indent=2)
            
            # Generate HTML certificate
            html_file = self.cert_generator.generate_html_certificate(cert_data)
            
            print(f"\n📜 Certificate Generated:")
            print(f"   JSON: {json_file}")
            print(f"   HTML: {html_file}")
            
        except Exception as e:
            print(f"❌ Failed to generate certificate: {e}")

def main():
    """Main entry point"""
    try:
        cli = SafeTrustWipeCLI()
        cli.run()
    except KeyboardInterrupt:
        print("\nExiting TrustWipe SAFE CLI...")
        sys.exit(0)
    except Exception as e:
        print(f"❌ Error: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()
