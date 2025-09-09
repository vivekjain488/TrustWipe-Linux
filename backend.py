#!/usr/bin/env python3
"""
TrustWipe Backend - Core wiping functionality
Handles the actual data wiping operations using dd and shred commands
"""

import subprocess
import os
import time
import psutil
import platform
from datetime import datetime
import logging

class DataWiper:
    def __init__(self, device_path, method="zeros", passes=3, callback=None):
        """
        Initialize the data wiper
        
        Args:
            device_path (str): Path to the device to wipe (e.g., /dev/sda)
            method (str): Wiping method (zeros, random, dod, gutmann)
            passes (int): Number of passes for supported methods
            callback (callable): Progress callback function
        """
        self.device_path = device_path
        self.method = method
        self.passes = passes
        self.callback = callback
        self.is_running = False
        self.current_process = None
        
        # Setup logging
        self.setup_logging()
        
    def setup_logging(self):
        """Setup logging for wipe operations"""
        log_dir = '/var/log/trustwipe'
        os.makedirs(log_dir, exist_ok=True)
        
        log_file = os.path.join(log_dir, f'wipe_{datetime.now().strftime("%Y%m%d_%H%M%S")}.log')
        
        logging.basicConfig(
            level=logging.INFO,
            format='%(asctime)s - %(levelname)s - %(message)s',
            handlers=[
                logging.FileHandler(log_file),
                logging.StreamHandler()
            ]
        )
        
        self.logger = logging.getLogger(__name__)
    
    def validate_device(self):
        """Validate that the device exists and is accessible"""
        if not os.path.exists(self.device_path):
            raise ValueError(f"Device {self.device_path} does not exist")
        
        if not os.access(self.device_path, os.R_OK | os.W_OK):
            raise PermissionError(f"No read/write access to {self.device_path}")
        
        # Check if device is mounted
        mounted_devices = []
        try:
            for partition in psutil.disk_partitions():
                if self.device_path in partition.device:
                    mounted_devices.append(partition.mountpoint)
        except:
            pass
        
        if mounted_devices:
            raise ValueError(f"Device {self.device_path} has mounted partitions: {mounted_devices}")
    
    def get_device_size(self):
        """Get the size of the device in bytes"""
        try:
            result = subprocess.run(
                ['blockdev', '--getsize64', self.device_path],
                capture_output=True,
                text=True,
                check=True
            )
            return int(result.stdout.strip())
        except subprocess.CalledProcessError:
            return None
    
    def update_progress(self, message, progress=None):
        """Update progress via callback"""
        if self.callback:
            self.callback(message, progress)
        self.logger.info(message)
    
    def wipe(self):
        """Main wipe function that delegates to specific methods"""
        self.logger.info(f"Starting wipe of {self.device_path} using method: {self.method}")
        
        # Validate device before starting
        self.validate_device()
        
        device_size = self.get_device_size()
        if device_size:
            self.logger.info(f"Device size: {self.human_readable_size(device_size)}")
        
        self.is_running = True
        start_time = time.time()
        
        try:
            if self.method == "zeros":
                self._wipe_with_zeros()
            elif self.method == "random":
                self._wipe_with_random()
            elif self.method == "dod":
                self._wipe_with_dod()
            elif self.method == "gutmann":
                self._wipe_with_gutmann()
            else:
                raise ValueError(f"Unknown wiping method: {self.method}")
            
            end_time = time.time()
            duration = end_time - start_time
            
            self.logger.info(f"Wipe completed successfully in {duration:.2f} seconds")
            self.update_progress("Wipe completed successfully!", 100)
            
            return True
            
        except Exception as e:
            self.logger.error(f"Wipe failed: {str(e)}")
            self.update_progress(f"Wipe failed: {str(e)}")
            raise
        finally:
            self.is_running = False
    
    def _wipe_with_zeros(self):
        """Wipe device with zeros using dd - OPTIMIZED FOR SPEED"""
        for pass_num in range(self.passes):
            if not self.is_running:
                break
            
            self.update_progress(f"Pass {pass_num + 1}/{self.passes}: Writing zeros (optimized)...")
            
            # SPEED OPTIMIZATIONS:
            cmd = [
                'dd',
                'if=/dev/zero',
                f'of={self.device_path}',
                'bs=64M',           # Much larger block size for speed
                'status=progress',
                'oflag=direct',     # Direct I/O bypasses buffer cache
                'conv=fdatasync'    # Ensure data is written to disk
            ]
            
            self._run_command(cmd, f"zero pass {pass_num + 1}")
    
    def _wipe_with_random(self):
        """Wipe device with random data using dd - OPTIMIZED FOR SPEED"""
        for pass_num in range(self.passes):
            if not self.is_running:
                break
            
            self.update_progress(f"Pass {pass_num + 1}/{self.passes}: Writing random data (optimized)...")
            
            # SPEED OPTIMIZATIONS:
            cmd = [
                'dd',
                'if=/dev/urandom',
                f'of={self.device_path}',
                'bs=32M',           # Large block size (smaller than zeros due to urandom overhead)
                'status=progress',
                'oflag=direct',     # Direct I/O for speed
                'conv=fdatasync'
            ]
            
            self._run_command(cmd, f"random pass {pass_num + 1}")
    
    def _wipe_with_dod(self):
        """Wipe device using DoD 5220.22-M standard (3 passes)"""
        patterns = [
            ('zeros', '/dev/zero'),
            ('ones', None),  # We'll create a ones file
            ('random', '/dev/urandom')
        ]
        
        # Create ones pattern file
        ones_file = '/tmp/ones_pattern'
        try:
            with open(ones_file, 'wb') as f:
                f.write(b'\xFF' * (1024 * 1024))  # 1MB of 0xFF
        except Exception as e:
            self.logger.error(f"Failed to create ones pattern file: {e}")
            raise
        
        try:
            for pass_num, (pattern_name, source) in enumerate(patterns):
                if not self.is_running:
                    break
                
                self.update_progress(f"DoD Pass {pass_num + 1}/3: {pattern_name}...")
                
                if source is None:  # ones pattern
                    source = ones_file
                
                cmd = [
                    'dd',
                    f'if={source}',
                    f'of={self.device_path}',
                    'bs=1M',
                    'status=progress',
                    'conv=fdatasync'
                ]
                
                self._run_command(cmd, f"DoD pass {pass_num + 1} ({pattern_name})")
        
        finally:
            # Clean up ones file
            try:
                os.unlink(ones_file)
            except:
                pass
    
    def _wipe_with_gutmann(self):
        """Wipe device using Gutmann method (35 passes) via shred"""
        self.update_progress("Starting Gutmann 35-pass wipe...")
        
        cmd = [
            'shred',
            '-v',
            '-n', '35',
            '-z',
            self.device_path
        ]
        
        self._run_command(cmd, "Gutmann 35-pass wipe")
    
    def _run_command(self, cmd, description):
        """Run a command and handle output with REAL-TIME PROGRESS"""
        self.logger.info(f"Running command: {' '.join(cmd)}")
        
        try:
            self.current_process = subprocess.Popen(
                cmd,
                stdout=subprocess.PIPE,
                stderr=subprocess.STDOUT,  # Combine stderr with stdout for dd progress
                text=True,
                bufsize=0,  # Unbuffered for real-time output
                universal_newlines=True
            )
            
            # Monitor progress with REAL-TIME OUTPUT
            output_lines = []
            while self.current_process.poll() is None:
                if not self.is_running:
                    self.current_process.terminate()
                    break
                
                # Read output line by line for progress updates
                line = self.current_process.stdout.readline()
                if line:
                    line = line.strip()
                    output_lines.append(line)
                    
                    # Parse dd progress output
                    if 'bytes' in line and ('copied' in line or 'transferred' in line):
                        self.update_progress(f"{description}: {line}")
                        self.logger.info(f"Progress: {line}")
                    elif 'records in' in line or 'records out' in line:
                        self.logger.info(f"DD Status: {line}")
                
                time.sleep(0.1)  # Much faster polling
            
            # Get final result
            stdout, stderr = self.current_process.communicate()
            
            if self.current_process.returncode != 0:
                error_msg = f"Command failed: {stderr or 'Unknown error'}"
                self.logger.error(error_msg)
                raise subprocess.CalledProcessError(
                    self.current_process.returncode, 
                    cmd, 
                    stdout, 
                    stderr
                )
            
            self.logger.info(f"Command completed successfully: {description}")
            
        except Exception as e:
            self.logger.error(f"Command execution failed: {e}")
            raise
        finally:
            self.current_process = None
    
    def stop(self):
        """Stop the current wiping operation"""
        self.logger.info("Stop requested")
        self.is_running = False
        
        if self.current_process:
            self.logger.info("Terminating current process")
            self.current_process.terminate()
            
            # Give it a moment to terminate gracefully
            time.sleep(2)
            
            if self.current_process.poll() is None:
                self.logger.warning("Force killing process")
                self.current_process.kill()
    
    @staticmethod
    def human_readable_size(size_bytes):
        """Convert bytes to human readable format"""
        for unit in ['B', 'KB', 'MB', 'GB', 'TB', 'PB']:
            if size_bytes < 1024.0:
                return f"{size_bytes:.2f} {unit}"
            size_bytes /= 1024.0
        return f"{size_bytes:.2f} EB"

class SystemInfo:
    """Collect comprehensive system information"""
    
    @staticmethod
    def get_system_info():
        """Get detailed system information"""
        info = {}
        
        try:
            info.update({
                'timestamp': datetime.now().isoformat(),
                'hostname': platform.node(),
                'os': platform.system(),
                'os_release': platform.release(),
                'os_version': platform.version(),
                'architecture': platform.machine(),
                'processor': platform.processor(),
                'python_version': platform.python_version(),
            })
            
            # CPU information
            info['cpu'] = {
                'physical_cores': psutil.cpu_count(logical=False),
                'logical_cores': psutil.cpu_count(logical=True),
                'max_frequency': psutil.cpu_freq().max if psutil.cpu_freq() else None,
                'current_frequency': psutil.cpu_freq().current if psutil.cpu_freq() else None,
            }
            
            # Memory information
            memory = psutil.virtual_memory()
            info['memory'] = {
                'total': memory.total,
                'available': memory.available,
                'used': memory.used,
                'percentage': memory.percent,
                'total_human': DataWiper.human_readable_size(memory.total),
                'available_human': DataWiper.human_readable_size(memory.available),
            }
            
            # Disk information
            info['disks'] = []
            for partition in psutil.disk_partitions():
                try:
                    partition_usage = psutil.disk_usage(partition.mountpoint)
                    info['disks'].append({
                        'device': partition.device,
                        'mountpoint': partition.mountpoint,
                        'fstype': partition.fstype,
                        'total': partition_usage.total,
                        'used': partition_usage.used,
                        'free': partition_usage.free,
                        'percentage': partition_usage.percent,
                        'total_human': DataWiper.human_readable_size(partition_usage.total),
                    })
                except PermissionError:
                    continue
            
            # Boot time
            boot_time = datetime.fromtimestamp(psutil.boot_time())
            info['boot_time'] = boot_time.isoformat()
            info['uptime'] = str(datetime.now() - boot_time)
            
            # Network interfaces
            info['network'] = {}
            for interface, addresses in psutil.net_if_addrs().items():
                info['network'][interface] = []
                for addr in addresses:
                    info['network'][interface].append({
                        'family': str(addr.family),
                        'address': addr.address,
                        'netmask': addr.netmask,
                        'broadcast': addr.broadcast,
                    })
            
        except Exception as e:
            info['error'] = str(e)
        
        return info
    
    @staticmethod
    def get_device_info(device_path):
        """Get detailed information about a storage device"""
        info = {'device_path': device_path}
        
        try:
            device_name = device_path.split('/')[-1]
            
            # Device size
            try:
                result = subprocess.run(
                    ['blockdev', '--getsize64', device_path],
                    capture_output=True,
                    text=True,
                    check=True
                )
                size_bytes = int(result.stdout.strip())
                info['size_bytes'] = size_bytes
                info['size_human'] = DataWiper.human_readable_size(size_bytes)
            except:
                pass
            
            # Device model
            try:
                with open(f'/sys/block/{device_name}/device/model', 'r') as f:
                    info['model'] = f.read().strip()
            except:
                pass
            
            # Device vendor
            try:
                with open(f'/sys/block/{device_name}/device/vendor', 'r') as f:
                    info['vendor'] = f.read().strip()
            except:
                pass
            
            # Device serial number
            try:
                with open(f'/sys/block/{device_name}/device/serial', 'r') as f:
                    info['serial'] = f.read().strip()
            except:
                pass
            
            # Device type (SSD/HDD)
            try:
                with open(f'/sys/block/{device_name}/queue/rotational', 'r') as f:
                    rotational = f.read().strip()
                    info['type'] = "HDD" if rotational == "1" else "SSD"
            except:
                pass
            
            # Partition information
            try:
                result = subprocess.run(
                    ['lsblk', '-J', device_path],
                    capture_output=True,
                    text=True,
                    check=True
                )
                import json
                lsblk_data = json.loads(result.stdout)
                info['partitions'] = lsblk_data['blockdevices']
            except:
                pass
            
        except Exception as e:
            info['error'] = str(e)
        
        return info

if __name__ == "__main__":
    # Test the backend functionality
    import sys
    
    if len(sys.argv) < 2:
        print("Usage: python3 backend.py <device_path> [method] [passes]")
        sys.exit(1)
    
    device = sys.argv[1]
    method = sys.argv[2] if len(sys.argv) > 2 else "zeros"
    passes = int(sys.argv[3]) if len(sys.argv) > 3 else 1
    
    def progress_callback(message, progress=None):
        print(f"Progress: {message}")
        if progress is not None:
            print(f"  -> {progress}%")
    
    try:
        wiper = DataWiper(device, method, passes, progress_callback)
        wiper.wipe()
        print("Wipe completed successfully!")
    except Exception as e:
        print(f"Wipe failed: {e}")
        sys.exit(1)
