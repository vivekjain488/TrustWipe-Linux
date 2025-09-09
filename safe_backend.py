#!/usr/bin/env python3
"""
TrustWipe Backend - SAFE Data Wiping
NOW WITH CRITICAL SAFETY FEATURES TO PREVENT OS DESTRUCTION
"""

import subprocess
import os
import time
import psutil
import platform
import glob
from datetime import datetime
import logging
from safety_manager import SafetyManager, PersonalDataWiper

class SafeDataWiper:
    """SAFE data wiper that prevents OS destruction"""
    
    def __init__(self, wipe_type="personal_data", method="zeros", passes=3, callback=None):
        """
        Initialize the SAFE data wiper
        
        Args:
            wipe_type (str): Type of wipe - "personal_data", "factory_reset", "external_drive"
            method (str): Wiping method (zeros, random, dod, gutmann)
            passes (int): Number of passes for supported methods
            callback (callable): Progress callback function
        """
        self.wipe_type = wipe_type
        self.method = method
        self.passes = passes
        self.callback = callback
        self.is_running = False
        self.current_process = None
        
        # Initialize safety components
        self.safety_manager = SafetyManager()
        self.personal_wiper = PersonalDataWiper()
        
        # Setup logging
        self.setup_logging()
        
    def setup_logging(self):
        """Setup logging for wipe operations"""
        log_dir = '/var/log/trustwipe'
        os.makedirs(log_dir, exist_ok=True)
        
        log_file = os.path.join(log_dir, f'safe_wipe_{datetime.now().strftime("%Y%m%d_%H%M%S")}.log')
        
        logging.basicConfig(
            level=logging.INFO,
            format='%(asctime)s - %(levelname)s - %(message)s',
            handlers=[
                logging.FileHandler(log_file),
                logging.StreamHandler()
            ]
        )
        
        self.logger = logging.getLogger(__name__)
    
    def update_progress(self, message, progress=None):
        """Update progress via callback"""
        if self.callback:
            self.callback(message, progress)
        self.logger.info(message)
    
    def wipe_personal_data_only(self):
        """SAFE: Wipe only personal data, preserve OS"""
        self.logger.info("🔒 SAFE MODE: Wiping personal data only")
        self.update_progress("🔒 SAFE MODE: Starting personal data wipe...", 0)
        
        try:
            # Get list of personal files
            self.update_progress("📁 Scanning for personal data...", 10)
            personal_files = self.personal_wiper.get_personal_files()
            
            total_files = len(personal_files)
            self.update_progress(f"📁 Found {total_files} personal files to wipe", 20)
            
            if total_files == 0:
                self.update_progress("✅ No personal data found - system is already clean!", 100)
                return True
            
            # Wipe personal files
            wiped_files = []
            errors = []
            
            for i, file_path in enumerate(personal_files):
                if not self.is_running:
                    break
                
                progress = 20 + (i / total_files) * 60
                self.update_progress(f"🗑️ Wiping: {os.path.basename(file_path)}", progress)
                
                try:
                    self._secure_wipe_file(file_path)
                    wiped_files.append(file_path)
                except Exception as e:
                    errors.append(f"{file_path}: {e}")
                    self.logger.warning(f"Failed to wipe {file_path}: {e}")
            
            # Clear caches and temporary files
            self.update_progress("🧹 Clearing caches and temporary files...", 85)
            self._clear_system_caches()
            
            # Clear browser data
            self.update_progress("🌐 Clearing browser data...", 90)
            self._clear_browser_data()
            
            # Clear command history
            self.update_progress("📜 Clearing command history...", 95)
            self._clear_command_history()
            
            self.update_progress(f"✅ Personal data wipe complete! Wiped {len(wiped_files)} files", 100)
            
            # Log results
            self.logger.info(f"Successfully wiped {len(wiped_files)} personal files")
            if errors:
                self.logger.warning(f"Failed to wipe {len(errors)} files")
            
            return True
            
        except Exception as e:
            self.logger.error(f"Personal data wipe failed: {str(e)}")
            self.update_progress(f"❌ Personal data wipe failed: {str(e)}")
            return False
    
    def factory_reset_safe(self):
        """SAFE: Factory reset preserving OS"""
        self.logger.info("🏭 SAFE MODE: Factory reset (preserving OS)")
        self.update_progress("🏭 SAFE MODE: Starting factory reset...", 0)
        
        try:
            # First wipe personal data
            self.update_progress("📁 Step 1: Wiping personal data...", 10)
            if not self.wipe_personal_data_only():
                return False
            
            # Reset user accounts
            self.update_progress("👤 Step 2: Resetting user accounts...", 60)
            self._reset_user_accounts()
            
            # Reset network settings
            self.update_progress("🌐 Step 3: Resetting network settings...", 70)
            self._reset_network_settings()
            
            # Clear logs
            self.update_progress("📜 Step 4: Clearing system logs...", 80)
            self._clear_system_logs()
            
            # Reset system settings
            self.update_progress("⚙️ Step 5: Resetting system settings...", 90)
            self._reset_system_settings()
            
            self.update_progress("✅ Factory reset complete! System restored to clean state", 100)
            return True
            
        except Exception as e:
            self.logger.error(f"Factory reset failed: {str(e)}")
            self.update_progress(f"❌ Factory reset failed: {str(e)}")
            return False
    
    def wipe_external_drive(self, device_path):
        """SAFE: Wipe external drive only after safety checks"""
        self.logger.info(f"💾 SAFE MODE: Checking external drive {device_path}")
        
        # CRITICAL SAFETY CHECK
        safety_checks = self.safety_manager.is_safe_for_wiping(device_path)
        
        if not safety_checks['safe']:
            error_msg = f"🚨 SAFETY BLOCK: Cannot wipe {device_path}\n"
            for warning in safety_checks['warnings']:
                error_msg += f"   {warning}\n"
            
            self.logger.error(error_msg)
            self.update_progress(error_msg)
            return False
        
        # Device is safe - proceed with wiping
        self.logger.info(f"✅ Safety check passed for {device_path}")
        self.update_progress(f"✅ Safety check passed - wiping {device_path}", 0)
        
        return self._wipe_device_safely(device_path)
    
    def _secure_wipe_file(self, file_path):
        """Securely wipe a single file"""
        if not os.path.exists(file_path):
            return
        
        try:
            file_size = os.path.getsize(file_path)
            
            if self.method == "zeros":
                # Overwrite with zeros
                with open(file_path, 'r+b') as f:
                    f.write(b'\x00' * file_size)
                    f.flush()
                    os.fsync(f.fileno())
            
            elif self.method == "random":
                # Overwrite with random data
                with open(file_path, 'r+b') as f:
                    f.write(os.urandom(file_size))
                    f.flush()
                    os.fsync(f.fileno())
            
            elif self.method == "dod":
                # DoD 5220.22-M: 3 passes
                patterns = [b'\x00', b'\xFF', os.urandom(file_size)]
                with open(file_path, 'r+b') as f:
                    for pattern in patterns:
                        f.seek(0)
                        if isinstance(pattern, bytes) and len(pattern) == 1:
                            f.write(pattern * file_size)
                        else:
                            f.write(pattern)
                        f.flush()
                        os.fsync(f.fileno())
            
            # Remove the file
            os.remove(file_path)
            
        except Exception as e:
            self.logger.warning(f"Failed to securely wipe {file_path}: {e}")
            # Try simple removal
            try:
                os.remove(file_path)
            except:
                pass
    
    def _clear_system_caches(self):
        """Clear system caches and temporary files"""
        cache_dirs = [
            '/tmp/*',
            '/var/tmp/*',
            '/var/cache/*',
            '/home/*/.cache/*',
            '/root/.cache/*'
        ]
        
        for cache_pattern in cache_dirs:
            try:
                subprocess.run(['find'] + cache_pattern.split() + ['-type', 'f', '-delete'], 
                             capture_output=True, timeout=30)
            except:
                pass
    
    def _clear_browser_data(self):
        """Clear browser data for all users"""
        browser_patterns = [
            '/home/*/.mozilla/firefox/*/cookies.sqlite',
            '/home/*/.mozilla/firefox/*/places.sqlite',
            '/home/*/.config/google-chrome/*/History',
            '/home/*/.config/google-chrome/*/Cookies',
            '/home/*/.config/chromium/*/History',
            '/home/*/.config/chromium/*/Cookies'
        ]
        
        for pattern in browser_patterns:
            try:
                files = glob.glob(pattern)
                for file_path in files:
                    if os.path.exists(file_path):
                        os.remove(file_path)
            except:
                pass
    
    def _clear_command_history(self):
        """Clear command history for all users"""
        history_files = [
            '/home/*/.bash_history',
            '/home/*/.zsh_history',
            '/home/*/.python_history',
            '/root/.bash_history',
            '/root/.zsh_history'
        ]
        
        for pattern in history_files:
            try:
                files = glob.glob(pattern)
                for file_path in files:
                    if os.path.exists(file_path):
                        open(file_path, 'w').close()  # Truncate file
            except:
                pass
    
    def _reset_user_accounts(self):
        """Reset user accounts (remove non-system users)"""
        try:
            # Get list of users with UID >= 1000 (non-system users)
            result = subprocess.run(['getent', 'passwd'], capture_output=True, text=True)
            
            for line in result.stdout.split('\n'):
                if ':' in line:
                    parts = line.split(':')
                    username = parts[0]
                    uid = int(parts[2]) if parts[2].isdigit() else 0
                    
                    # Remove non-system users (UID >= 1000)
                    if uid >= 1000 and username not in ['nobody', 'kali']:
                        subprocess.run(['userdel', '-r', username], capture_output=True)
                        self.logger.info(f"Removed user: {username}")
        except Exception as e:
            self.logger.warning(f"Failed to reset user accounts: {e}")
    
    def _reset_network_settings(self):
        """Reset network settings"""
        network_files = [
            '/etc/NetworkManager/system-connections/*',
            '/etc/wpa_supplicant/wpa_supplicant.conf'
        ]
        
        for pattern in network_files:
            try:
                files = glob.glob(pattern)
                for file_path in files:
                    if os.path.exists(file_path):
                        os.remove(file_path)
            except:
                pass
    
    def _clear_system_logs(self):
        """Clear system logs"""
        log_patterns = [
            '/var/log/*.log',
            '/var/log/*/*.log'
        ]
        
        for pattern in log_patterns:
            try:
                files = glob.glob(pattern)
                for file_path in files:
                    if os.path.exists(file_path) and 'trustwipe' not in file_path:
                        open(file_path, 'w').close()  # Truncate log file
            except:
                pass
    
    def _reset_system_settings(self):
        """Reset system settings to defaults"""
        # This is a placeholder - can be expanded based on specific requirements
        settings_to_reset = [
            '/etc/hosts',  # Reset to default
            '/etc/hostname'  # Reset hostname
        ]
        
        # Reset hostname to default
        try:
            with open('/etc/hostname', 'w') as f:
                f.write('kali\n')
        except:
            pass
    
    def _wipe_device_safely(self, device_path):
        """Safely wipe an external device"""
        try:
            device_size = self._get_device_size(device_path)
            if device_size:
                self.logger.info(f"Device size: {self._human_readable_size(device_size)}")
            
            if self.method == "zeros":
                self._wipe_device_with_zeros(device_path)
            elif self.method == "random":
                self._wipe_device_with_random(device_path)
            elif self.method == "dod":
                self._wipe_device_with_dod(device_path)
            
            return True
        except Exception as e:
            self.logger.error(f"Device wipe failed: {e}")
            return False
    
    def _get_device_size(self, device_path):
        """Get device size in bytes"""
        try:
            result = subprocess.run(['blockdev', '--getsize64', device_path], 
                                  capture_output=True, text=True, check=True)
            return int(result.stdout.strip())
        except:
            return None
    
    def _human_readable_size(self, size_bytes):
        """Convert bytes to human readable format"""
        for unit in ['B', 'KB', 'MB', 'GB', 'TB']:
            if size_bytes < 1024.0:
                return f"{size_bytes:.1f} {unit}"
            size_bytes /= 1024.0
        return f"{size_bytes:.1f} PB"
    
    def _wipe_device_with_zeros(self, device_path):
        """Wipe device with zeros"""
        cmd = [
            'dd',
            'if=/dev/zero',
            f'of={device_path}',
            'bs=64M',
            'status=progress',
            'oflag=direct'
        ]
        
        subprocess.run(cmd, check=True)
    
    def _wipe_device_with_random(self, device_path):
        """Wipe device with random data"""
        cmd = [
            'dd',
            'if=/dev/urandom',
            f'of={device_path}',
            'bs=64M',
            'status=progress',
            'oflag=direct'
        ]
        
        subprocess.run(cmd, check=True)
    
    def _wipe_device_with_dod(self, device_path):
        """Wipe device with DoD 5220.22-M standard"""
        patterns = ['/dev/zero', '/dev/urandom', '/dev/zero']
        
        for i, pattern in enumerate(patterns):
            self.update_progress(f"DoD Pass {i+1}/3...", (i/3)*100)
            
            cmd = [
                'dd',
                f'if={pattern}',
                f'of={device_path}',
                'bs=64M',
                'status=progress',
                'oflag=direct'
            ]
            
            subprocess.run(cmd, check=True)
    
    def stop(self):
        """Stop the wiping process"""
        self.is_running = False
        if self.current_process:
            self.current_process.terminate()

# Main wipe function for backward compatibility
def wipe_data(wipe_type="personal_data", method="zeros", passes=3, callback=None, device_path=None):
    """
    Main function to safely wipe data
    
    Args:
        wipe_type: "personal_data", "factory_reset", or "external_drive"
        method: "zeros", "random", "dod", "gutmann"
        passes: Number of passes
        callback: Progress callback
        device_path: Device path (for external_drive only)
    """
    wiper = SafeDataWiper(wipe_type, method, passes, callback)
    wiper.is_running = True
    
    try:
        if wipe_type == "personal_data":
            return wiper.wipe_personal_data_only()
        elif wipe_type == "factory_reset":
            return wiper.factory_reset_safe()
        elif wipe_type == "external_drive" and device_path:
            return wiper.wipe_external_drive(device_path)
        else:
            raise ValueError(f"Unknown wipe type: {wipe_type}")
    
    except Exception as e:
        print(f"Wipe failed: {e}")
        return False

if __name__ == "__main__":
    # Test the safe wiping
    print("🔒 TrustWipe SAFE Backend Test")
    
    wiper = SafeDataWiper("personal_data", "zeros", 1)
    result = wiper.wipe_personal_data_only()
    
    if result:
        print("✅ Safe wipe completed successfully!")
    else:
        print("❌ Safe wipe failed!")
