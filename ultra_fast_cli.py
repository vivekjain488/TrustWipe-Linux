#!/usr/bin/env python3
"""
TrustWipe ULTRA-FAST CLI - Optimized for 5GB /dev/sdb
Lightning-fast command line interface with real-time speed monitoring
"""

import argparse
import sys
import os
import time

# Add current directory to Python path for imports
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

try:
    from ultra_fast_backend import UltraFastDataWiper, ultra_fast_wipe_sdb, benchmark_wipe_speed
except ImportError as e:
    print(f"❌ Import Error: {e}")
    print("Make sure ultra_fast_backend.py is in the same directory")
    sys.exit(1)

class UltraFastCLI:
    """Ultra-fast CLI for maximum performance wiping"""
    
    def __init__(self):
        self.colors = {
            'red': '\033[91m',
            'green': '\033[92m',
            'yellow': '\033[93m',
            'blue': '\033[94m',
            'magenta': '\033[95m',
            'cyan': '\033[96m',
            'white': '\033[97m',
            'bold': '\033[1m',
            'reset': '\033[0m'
        }
    
    def print_color(self, text, color='white', bold=False):
        """Print colored text"""
        color_code = self.colors.get(color, self.colors['white'])
        if bold:
            color_code += self.colors['bold']
        print(f"{color_code}{text}{self.colors['reset']}")
    
    def print_header(self):
        """Print ultra-fast header"""
        self.print_color("=" * 60, 'cyan', True)
        self.print_color("⚡ TrustWipe ULTRA-FAST CLI ⚡", 'yellow', True)
        self.print_color("5GB /dev/sdb Optimizer - Target: Under 30 seconds!", 'green', True)
        self.print_color("=" * 60, 'cyan', True)
        print()
    
    def parse_arguments(self):
        """Parse command line arguments"""
        parser = argparse.ArgumentParser(
            description='TrustWipe ULTRA-FAST CLI - Optimized for 5GB /dev/sdb',
            formatter_class=argparse.RawDescriptionHelpFormatter,
            epilog="""
ULTRA-FAST METHODS:
  lightning    ⚡ FASTEST - Memory buffer method (~15-20 seconds)
  zeros        💨 VERY FAST - Optimized DD with huge blocks (~25-30 seconds)  
  random       🧵 PARALLEL - Multi-threaded random wipe (~45-60 seconds)

EXAMPLES:
  # Lightning-fast wipe (FASTEST)
  sudo python3 ultra_fast_cli.py --method lightning
  
  # Ultra-fast zero wipe
  sudo python3 ultra_fast_cli.py --method zeros
  
  # Parallel random wipe (secure)
  sudo python3 ultra_fast_cli.py --method random
  
  # Speed benchmark all methods
  sudo python3 ultra_fast_cli.py --benchmark
  
  # Force mode (no confirmations)
  sudo python3 ultra_fast_cli.py --method lightning --force
            """)
        
        parser.add_argument(
            '--method', '-m',
            choices=['lightning', 'zeros', 'random'],
            default='lightning',
            help='Ultra-fast wiping method (default: lightning)'
        )
        
        parser.add_argument(
            '--device', '-d',
            default='/dev/sdb',
            help='Target device (default: /dev/sdb)'
        )
        
        parser.add_argument(
            '--benchmark', '-b',
            action='store_true',
            help='Run speed benchmark on all methods'
        )
        
        parser.add_argument(
            '--force', '-f',
            action='store_true',
            help='Skip confirmation (for automation)'
        )
        
        parser.add_argument(
            '--monitor', '-M',
            action='store_true',
            help='Show detailed performance monitoring'
        )
        
        return parser.parse_args()
    
    def check_root(self):
        """Check root privileges"""
        if os.geteuid() != 0:
            self.print_color("❌ ERROR: Ultra-fast wiping requires root privileges!", 'red', True)
            self.print_color("Please run: sudo python3 ultra_fast_cli.py", 'yellow')
            sys.exit(1)
    
    def check_device(self, device):
        """Check if device exists and get info"""
        if not os.path.exists(device):
            self.print_color(f"❌ ERROR: Device {device} does not exist!", 'red', True)
            return False
        
        try:
            # Get device size
            import subprocess
            result = subprocess.run(['blockdev', '--getsize64', device], 
                                  capture_output=True, text=True, check=True)
            size_bytes = int(result.stdout.strip())
            size_gb = size_bytes / (1024**3)
            
            self.print_color(f"📊 Device Info:", 'cyan', True)
            self.print_color(f"   Path: {device}", 'white')
            self.print_color(f"   Size: {size_gb:.2f} GB ({size_bytes:,} bytes)", 'white')
            
            if size_gb < 4 or size_gb > 6:
                self.print_color(f"⚠️  WARNING: Expected ~5GB, found {size_gb:.2f}GB", 'yellow')
            
            return True
            
        except Exception as e:
            self.print_color(f"❌ ERROR: Cannot access device {device}: {e}", 'red')
            return False
    
    def show_method_info(self, method):
        """Show information about selected method"""
        method_info = {
            'lightning': {
                'name': '⚡ LIGHTNING WIPE',
                'description': 'Memory buffer method - FASTEST possible',
                'speed': '~15-20 seconds for 5GB',
                'technique': 'Large memory buffer writes',
                'color': 'yellow'
            },
            'zeros': {
                'name': '💨 ULTRA-FAST ZEROS',
                'description': 'Optimized DD with massive blocks',
                'speed': '~25-30 seconds for 5GB', 
                'technique': '512MB block size + direct I/O',
                'color': 'green'
            },
            'random': {
                'name': '🧵 PARALLEL RANDOM',
                'description': 'Multi-threaded secure wipe',
                'speed': '~45-60 seconds for 5GB',
                'technique': '8 parallel threads + urandom',
                'color': 'magenta'
            }
        }
        
        info = method_info[method]
        self.print_color(f"🚀 Selected Method: {info['name']}", info['color'], True)
        self.print_color(f"   Description: {info['description']}", 'white')
        self.print_color(f"   Expected Speed: {info['speed']}", 'cyan')
        self.print_color(f"   Technique: {info['technique']}", 'white')
        print()
    
    def confirm_wipe(self, device, method):
        """Confirm wipe operation"""
        self.print_color("🚨 ULTRA-FAST WIPE CONFIRMATION", 'red', True)
        self.print_color(f"Target Device: {device}", 'white')
        self.print_color(f"Method: {method.upper()}", 'yellow')
        self.print_color(f"This will COMPLETELY DESTROY all data on {device}!", 'red', True)
        print()
        
        response = input("Type 'ULTRA-FAST' to confirm: ").strip()
        return response == 'ULTRA-FAST'
    
    def progress_callback(self, message, progress, bytes_written=0):
        """Advanced progress callback with speed monitoring"""
        if hasattr(self, 'start_time') and bytes_written > 0:
            elapsed = time.time() - self.start_time
            if elapsed > 0:
                speed_mbps = (bytes_written / (1024*1024)) / elapsed
                
                # Update peak speed
                if not hasattr(self, 'peak_speed'):
                    self.peak_speed = 0
                self.peak_speed = max(self.peak_speed, speed_mbps)
                
                # Calculate ETA
                if speed_mbps > 0:
                    remaining_bytes = (5 * 1024 * 1024 * 1024) - bytes_written
                    eta_seconds = remaining_bytes / (bytes_written / elapsed)
                else:
                    eta_seconds = 0
                
                # Create progress bar
                if progress is not None:
                    bar_length = 40
                    filled_length = int(bar_length * progress // 100)
                    bar = '█' * filled_length + '░' * (bar_length - filled_length)
                    
                    # Color-coded progress bar
                    if progress < 30:
                        bar_color = 'red'
                    elif progress < 70:
                        bar_color = 'yellow'
                    else:
                        bar_color = 'green'
                    
                    status_line = f"\r[{bar}] {progress:5.1f}% | {speed_mbps:6.1f} MB/s | Peak: {self.peak_speed:6.1f} MB/s | ETA: {eta_seconds:3.0f}s"
                    
                    # Print with color
                    color_codes = {'red': '91', 'yellow': '93', 'green': '92'}
                    color_code = color_codes[bar_color]
                    print(f"\033[{color_code}m{status_line}\033[0m", end='', flush=True)
        else:
            print(f"\n{message}")
    
    def run_ultra_fast_wipe(self, device, method):
        """Run the ultra-fast wipe"""
        self.print_color("🚀 STARTING ULTRA-FAST WIPE...", 'green', True)
        print()
        
        # Record start time
        self.start_time = time.time()
        self.peak_speed = 0
        
        # Show real-time performance
        self.print_color("📊 Real-time Performance Monitor:", 'cyan', True)
        print("Progress Bar | Speed | Peak Speed | ETA")
        print("-" * 60)
        
        # Execute ultra-fast wipe
        success = ultra_fast_wipe_sdb(method, self.progress_callback)
        
        print()  # New line after progress bar
        
        # Calculate final stats
        total_time = time.time() - self.start_time
        total_size_mb = 5 * 1024  # 5GB in MB
        avg_speed = total_size_mb / total_time if total_time > 0 else 0
        
        if success:
            self.print_color("🎉 ULTRA-FAST WIPE COMPLETED!", 'green', True)
            print()
            self.print_color("📊 PERFORMANCE STATISTICS:", 'cyan', True)
            self.print_color(f"   Total Time: {total_time:.2f} seconds", 'white')
            self.print_color(f"   Average Speed: {avg_speed:.1f} MB/s", 'green')
            self.print_color(f"   Peak Speed: {self.peak_speed:.1f} MB/s", 'yellow')
            self.print_color(f"   Data Wiped: {total_size_mb:.0f} MB", 'white')
            
            # Performance rating
            if total_time < 20:
                rating = "🏆 EXCEPTIONAL"
                rating_color = 'yellow'
            elif total_time < 30:
                rating = "🥇 EXCELLENT" 
                rating_color = 'green'
            elif total_time < 60:
                rating = "🥈 VERY GOOD"
                rating_color = 'cyan'
            else:
                rating = "🥉 GOOD"
                rating_color = 'white'
            
            self.print_color(f"   Performance: {rating}", rating_color, True)
            
        else:
            self.print_color("❌ ULTRA-FAST WIPE FAILED!", 'red', True)
            return False
        
        return True
    
    def run_benchmark(self, device):
        """Run comprehensive speed benchmark"""
        self.print_color("🏁 ULTRA-FAST SPEED BENCHMARK", 'yellow', True)
        self.print_color("Testing all methods on /dev/sdb...", 'white')
        print()
        
        try:
            results = benchmark_wipe_speed(device)
            
            print()
            self.print_color("🏆 BENCHMARK RESULTS", 'cyan', True)
            self.print_color("=" * 50, 'cyan')
            
            # Sort by speed (fastest first)
            sorted_results = sorted(results.items(), key=lambda x: x[1])
            
            for i, (method, time_taken) in enumerate(sorted_results, 1):
                speed_mbps = (5 * 1024) / time_taken  # 5GB in MB
                
                if i == 1:
                    medal = "🥇"
                    color = 'yellow'
                elif i == 2:
                    medal = "🥈"
                    color = 'white' 
                else:
                    medal = "🥉"
                    color = 'magenta'
                
                self.print_color(f"{medal} {method.upper():<12} {time_taken:6.1f}s @ {speed_mbps:6.1f} MB/s", color, True)
            
            # Show winner
            winner_method, winner_time = sorted_results[0]
            winner_speed = (5 * 1024) / winner_time
            
            print()
            self.print_color(f"🏆 FASTEST METHOD: {winner_method.upper()}", 'yellow', True)
            self.print_color(f"🚀 Best Time: {winner_time:.1f} seconds @ {winner_speed:.1f} MB/s", 'green', True)
            
        except Exception as e:
            self.print_color(f"❌ Benchmark failed: {e}", 'red', True)
    
    def run(self):
        """Main CLI execution"""
        args = self.parse_arguments()
        
        # Print header
        self.print_header()
        
        # Check root privileges
        self.check_root()
        
        # Check device
        if not self.check_device(args.device):
            sys.exit(1)
        
        print()
        
        # Run benchmark if requested
        if args.benchmark:
            self.run_benchmark(args.device)
            return
        
        # Show method info
        self.show_method_info(args.method)
        
        # Confirm operation unless force mode
        if not args.force:
            if not self.confirm_wipe(args.device, args.method):
                self.print_color("Operation cancelled by user", 'yellow')
                sys.exit(0)
        
        print()
        
        # Run ultra-fast wipe
        try:
            success = self.run_ultra_fast_wipe(args.device, args.method)
            
            if success:
                self.print_color("\n🎉 MISSION ACCOMPLISHED! 🎉", 'green', True)
            else:
                sys.exit(1)
                
        except KeyboardInterrupt:
            self.print_color("\n⏹️ Wipe interrupted by user", 'yellow')
            sys.exit(1)
        except Exception as e:
            self.print_color(f"\n❌ Error: {e}", 'red', True)
            sys.exit(1)

def main():
    """Main entry point"""
    try:
        cli = UltraFastCLI()
        cli.run()
    except KeyboardInterrupt:
        print("\n⏹️ Exiting Ultra-Fast CLI...")
        sys.exit(0)

if __name__ == "__main__":
    main()
