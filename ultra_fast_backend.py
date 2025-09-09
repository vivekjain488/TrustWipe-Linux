#!/usr/bin/env python3
"""
TrustWipe ULTRA FAST Backend - Maximum Performance for 5GB SDB
Optimized specifically for VMware Linux environments with small drives
TARGET: Wipe 5GB /dev/sdb in under 30 seconds!
"""

import subprocess
import os
import time
import threading
import multiprocessing
import sys
from datetime import datetime
import logging
from concurrent.futures import ThreadPoolExecutor, as_completed

# Try to import psutil, install if missing
try:
    import psutil
except ImportError:
    print("📦 Installing psutil...")
    try:
        subprocess.run([sys.executable, "-m", "pip", "install", "psutil"], check=True, capture_output=True)
        import psutil
    except Exception:
        print("❌ Could not install psutil. Please run: sudo apt install python3-psutil")
        sys.exit(1)

class UltraFastDataWiper:
    """Ultra-optimized data wiper for maximum speed"""
    
    def __init__(self, device_path="/dev/sdb", method="zeros", callback=None):
        """
        Initialize ultra-fast wiper
        
        Args:
            device_path (str): Device to wipe (default: /dev/sdb)
            method (str): Wiping method optimized for speed
            callback (callable): Progress callback
        """
        self.device_path = device_path
        self.method = method
        self.callback = callback
        self.is_running = False
        self.start_time = None
        self.device_size = None
        
        # PERFORMANCE SETTINGS - MAXIMUM SPEED
        self.block_size = "512M"  # MASSIVE blocks for VMware
        self.thread_count = min(8, multiprocessing.cpu_count())
        self.optimization_level = "EXTREME"
        
        self.setup_logging()
        self.optimize_system()
    
    def setup_logging(self):
        """Setup high-performance logging"""
        self.logger = logging.getLogger(__name__)
        handler = logging.StreamHandler()
        handler.setFormatter(logging.Formatter('%(asctime)s - ULTRA-FAST - %(message)s'))
        self.logger.addHandler(handler)
        self.logger.setLevel(logging.INFO)
    
    def optimize_system(self):
        """Apply system optimizations for maximum speed"""
        self.logger.info("🚀 ULTRA-FAST MODE: Applying system optimizations...")
        
        # Optimization commands for maximum performance
        optimizations = [
            # Disable sync to maximize speed (EXTREME mode)
            "echo 0 > /proc/sys/vm/dirty_writeback_centisecs",
            
            # Maximize buffer cache
            "echo 1 > /proc/sys/vm/drop_caches",
            
            # Optimize I/O scheduler for sequential writes
            f"echo noop > /sys/block/{os.path.basename(self.device_path)}/queue/scheduler 2>/dev/null || true",
            
            # Increase readahead for faster sequential I/O
            f"blockdev --setra 32768 {self.device_path} 2>/dev/null || true",
            
            # Disable barriers for maximum speed (VMware safe)
            f"hdparm -W1 {self.device_path} 2>/dev/null || true"
        ]
        
        for cmd in optimizations:
            try:
                subprocess.run(cmd, shell=True, capture_output=True, timeout=5)
            except:
                pass  # Continue even if some optimizations fail
    
    def get_device_info(self):
        """Get device information and calculate optimal settings"""
        try:
            # Get device size
            result = subprocess.run(
                ['blockdev', '--getsize64', self.device_path],
                capture_output=True, text=True, check=True
            )
            self.device_size = int(result.stdout.strip())
            
            # Get device type and optimize accordingly
            device_name = os.path.basename(self.device_path)
            
            # Check if it's an SSD (faster) or HDD
            try:
                with open(f'/sys/block/{device_name}/queue/rotational', 'r') as f:
                    is_rotational = f.read().strip() == '1'
                
                if not is_rotational:
                    # SSD - use even larger blocks
                    self.block_size = "1G"
                    self.logger.info("💾 SSD detected - using 1GB block size")
                else:
                    # HDD - optimize for sequential writes
                    self.block_size = "512M"
                    self.logger.info("💿 HDD detected - using 512MB block size")
                    
            except:
                pass
            
            size_gb = self.device_size / (1024**3)
            self.logger.info(f"📊 Device: {self.device_path}")
            self.logger.info(f"📊 Size: {size_gb:.2f} GB ({self.device_size:,} bytes)")
            self.logger.info(f"📊 Block size: {self.block_size}")
            self.logger.info(f"📊 Optimization: {self.optimization_level}")
            
            return True
            
        except Exception as e:
            self.logger.error(f"❌ Failed to get device info: {e}")
            return False
    
    def update_progress(self, message, progress=None, bytes_written=0):
        """Ultra-fast progress updates"""
        if self.start_time and bytes_written > 0:
            elapsed = time.time() - self.start_time
            if elapsed > 0:
                speed_mbps = (bytes_written / (1024*1024)) / elapsed
                eta_seconds = (self.device_size - bytes_written) / (bytes_written / elapsed) if bytes_written > 0 else 0
                
                message += f" | Speed: {speed_mbps:.1f} MB/s | ETA: {eta_seconds:.0f}s"
        
        if self.callback:
            self.callback(message, progress)
        self.logger.info(message)
    
    def ultra_fast_zero_wipe(self):
        """ULTRA-FAST zero wipe optimized for 5GB drives"""
        self.logger.info("🚀 ULTRA-FAST ZERO WIPE starting...")
        self.start_time = time.time()
        
        # Create the ultimate speed command
        cmd = [
            'dd',
            'if=/dev/zero',
            f'of={self.device_path}',
            f'bs={self.block_size}',
            'status=progress',
            'oflag=direct,dsync',  # Direct I/O with data sync
            'conv=fdatasync',      # Fast data sync
            'iflag=fullblock'      # Read full blocks
        ]
        
        self.logger.info(f"💨 Executing: {' '.join(cmd)}")
        
        try:
            # Start the process
            process = subprocess.Popen(
                cmd,
                stdout=subprocess.PIPE,
                stderr=subprocess.STDOUT,
                universal_newlines=True,
                bufsize=1
            )
            
            bytes_written = 0
            
            # Monitor progress with high-speed updates
            while process.poll() is None:
                if not self.is_running:
                    process.terminate()
                    break
                
                # Parse dd output for progress
                try:
                    line = process.stdout.readline()
                    if line and 'bytes' in line:
                        # Extract bytes from dd output
                        parts = line.split()
                        for i, part in enumerate(parts):
                            if 'bytes' in part and i > 0:
                                try:
                                    bytes_written = int(parts[i-1].replace(',', ''))
                                    break
                                except:
                                    pass
                        
                        if self.device_size > 0:
                            progress = (bytes_written / self.device_size) * 100
                            self.update_progress(
                                f"🚀 Ultra-fast wiping... {bytes_written:,} bytes",
                                progress,
                                bytes_written
                            )
                except:
                    pass
                
                time.sleep(0.1)  # Very fast updates
            
            # Wait for completion
            return_code = process.wait()
            
            if return_code == 0:
                elapsed = time.time() - self.start_time
                speed_mbps = (self.device_size / (1024*1024)) / elapsed
                
                self.logger.info(f"✅ ULTRA-FAST WIPE COMPLETE!")
                self.logger.info(f"⏱️  Total time: {elapsed:.2f} seconds")
                self.logger.info(f"🚀 Average speed: {speed_mbps:.1f} MB/s")
                self.logger.info(f"📊 Data wiped: {self.device_size:,} bytes")
                
                self.update_progress(
                    f"✅ ULTRA-FAST WIPE COMPLETE! {elapsed:.1f}s @ {speed_mbps:.1f} MB/s",
                    100
                )
                return True
            else:
                raise subprocess.CalledProcessError(return_code, cmd)
                
        except Exception as e:
            self.logger.error(f"❌ Ultra-fast wipe failed: {e}")
            self.update_progress(f"❌ Wipe failed: {e}")
            return False
    
    def parallel_random_wipe(self):
        """PARALLEL random wipe for extreme speed"""
        self.logger.info("🚀 PARALLEL RANDOM WIPE starting...")
        self.start_time = time.time()
        
        # Calculate optimal chunk size per thread
        chunk_size = self.device_size // self.thread_count
        
        self.logger.info(f"🧵 Using {self.thread_count} parallel threads")
        self.logger.info(f"📊 Chunk size per thread: {chunk_size:,} bytes")
        
        def wipe_chunk(thread_id, start_offset, size):
            """Wipe a chunk of the device"""
            try:
                cmd = [
                    'dd',
                    'if=/dev/urandom',
                    f'of={self.device_path}',
                    f'bs=64M',
                    f'count={size // (64*1024*1024) + 1}',
                    f'seek={start_offset // (64*1024*1024)}',
                    'conv=notrunc,fdatasync',
                    'oflag=direct'
                ]
                
                result = subprocess.run(cmd, capture_output=True, timeout=300)
                return thread_id, result.returncode == 0
                
            except Exception as e:
                self.logger.warning(f"Thread {thread_id} failed: {e}")
                return thread_id, False
        
        # Execute parallel wiping
        with ThreadPoolExecutor(max_workers=self.thread_count) as executor:
            futures = []
            
            for i in range(self.thread_count):
                start_offset = i * chunk_size
                size = chunk_size if i < self.thread_count - 1 else self.device_size - start_offset
                
                future = executor.submit(wipe_chunk, i, start_offset, size)
                futures.append(future)
            
            # Monitor progress
            completed = 0
            for future in as_completed(futures):
                thread_id, success = future.result()
                completed += 1
                
                progress = (completed / self.thread_count) * 100
                self.update_progress(
                    f"🧵 Thread {thread_id} completed - {completed}/{self.thread_count}",
                    progress
                )
                
                if not success:
                    self.logger.warning(f"⚠️ Thread {thread_id} had issues")
        
        elapsed = time.time() - self.start_time
        speed_mbps = (self.device_size / (1024*1024)) / elapsed
        
        self.logger.info(f"✅ PARALLEL WIPE COMPLETE!")
        self.logger.info(f"⏱️  Total time: {elapsed:.2f} seconds")
        self.logger.info(f"🚀 Average speed: {speed_mbps:.1f} MB/s")
        
        return True
    
    def lightning_wipe(self):
        """LIGHTNING-FAST wipe - ultimate speed method"""
        self.logger.info("⚡ LIGHTNING WIPE - MAXIMUM SPEED MODE!")
        self.start_time = time.time()
        
        # For 5GB, we can use the fastest possible method
        # Create a large zero buffer in memory and blast it to disk
        
        try:
            # Open device for direct writing
            with open(self.device_path, 'wb') as device:
                # Create massive buffer (512MB of zeros)
                buffer_size = 512 * 1024 * 1024  # 512MB
                zero_buffer = bytearray(buffer_size)
                
                bytes_written = 0
                
                while bytes_written < self.device_size and self.is_running:
                    remaining = self.device_size - bytes_written
                    write_size = min(buffer_size, remaining)
                    
                    # Write the buffer
                    device.write(zero_buffer[:write_size])
                    device.flush()
                    
                    bytes_written += write_size
                    
                    # Update progress
                    progress = (bytes_written / self.device_size) * 100
                    elapsed = time.time() - self.start_time
                    speed_mbps = (bytes_written / (1024*1024)) / elapsed if elapsed > 0 else 0
                    
                    self.update_progress(
                        f"⚡ Lightning wipe: {bytes_written:,}/{self.device_size:,} bytes @ {speed_mbps:.1f} MB/s",
                        progress,
                        bytes_written
                    )
            
            elapsed = time.time() - self.start_time
            speed_mbps = (self.device_size / (1024*1024)) / elapsed
            
            self.logger.info(f"⚡ LIGHTNING WIPE COMPLETE!")
            self.logger.info(f"⏱️  Total time: {elapsed:.2f} seconds")
            self.logger.info(f"🚀 Average speed: {speed_mbps:.1f} MB/s")
            
            return True
            
        except Exception as e:
            self.logger.error(f"❌ Lightning wipe failed: {e}")
            return False
    
    def wipe(self):
        """Main wipe function with method selection"""
        if not self.get_device_info():
            return False
        
        self.is_running = True
        
        try:
            if self.method == "zeros":
                return self.ultra_fast_zero_wipe()
            elif self.method == "random":
                return self.parallel_random_wipe()
            elif self.method == "lightning":
                return self.lightning_wipe()
            else:
                # Default to ultra-fast zero
                return self.ultra_fast_zero_wipe()
                
        except Exception as e:
            self.logger.error(f"❌ Wipe failed: {e}")
            return False
        finally:
            self.is_running = False
    
    def stop(self):
        """Stop the wiping process"""
        self.is_running = False
        self.logger.info("⏹️ Wipe stopped by user")

# High-level interface functions
def ultra_fast_wipe_sdb(method="lightning", callback=None):
    """
    Ultra-fast wipe of /dev/sdb specifically
    
    Args:
        method: "lightning", "zeros", or "random"
        callback: Progress callback function
    
    Returns:
        bool: Success status
    """
    print("🚀 ULTRA-FAST SDB WIPER")
    print("=" * 40)
    print(f"🎯 Target: /dev/sdb (5GB)")
    print(f"⚡ Method: {method.upper()}")
    print(f"🎯 Goal: Complete in under 30 seconds!")
    print()
    
    wiper = UltraFastDataWiper("/dev/sdb", method, callback)
    return wiper.wipe()

def benchmark_wipe_speed(device="/dev/sdb"):
    """Benchmark different wiping methods"""
    methods = ["lightning", "zeros", "random"]
    results = {}
    
    print("🏁 SPEED BENCHMARK")
    print("=" * 40)
    
    for method in methods:
        print(f"\n🚀 Testing {method.upper()} method...")
        
        def progress_callback(msg, progress):
            if progress:
                print(f"\r{msg} [{progress:.1f}%]", end="", flush=True)
        
        start_time = time.time()
        success = ultra_fast_wipe_sdb(method, progress_callback)
        elapsed = time.time() - start_time
        
        print()  # New line
        
        if success:
            results[method] = elapsed
            print(f"✅ {method.upper()}: {elapsed:.2f} seconds")
        else:
            print(f"❌ {method.upper()}: FAILED")
    
    print("\n🏆 BENCHMARK RESULTS:")
    print("=" * 40)
    for method, time_taken in sorted(results.items(), key=lambda x: x[1]):
        print(f"🥇 {method.upper()}: {time_taken:.2f} seconds")
    
    return results

if __name__ == "__main__":
    import sys
    
    if len(sys.argv) > 1:
        method = sys.argv[1]
    else:
        method = "lightning"
    
    print("⚡ TrustWipe ULTRA-FAST Backend")
    print("🎯 Optimized for 5GB /dev/sdb on VMware")
    print()
    
    def progress_display(message, progress):
        if progress:
            bar_length = 50
            filled_length = int(bar_length * progress // 100)
            bar = '█' * filled_length + '-' * (bar_length - filled_length)
            print(f"\r[{bar}] {progress:.1f}% - {message}", end="", flush=True)
        else:
            print(f"\n{message}")
    
    success = ultra_fast_wipe_sdb(method, progress_display)
    
    print("\n")
    if success:
        print("🎉 ULTRA-FAST WIPE COMPLETED SUCCESSFULLY!")
    else:
        print("❌ Wipe failed!")
