#!/usr/bin/env python3
"""
TrustWipe Safety Manager
Prevents accidental OS wiping and focuses on personal data removal
"""

import os
import subprocess
import psutil
import re
from pathlib import Path

class SafetyManager:
    """Manages safety checks to prevent OS destruction"""
    
    def __init__(self):
        self.system_paths = [
            '/boot', '/bin', '/sbin', '/usr', '/etc', '/lib', '/lib64',
            '/sys', '/proc', '/dev', '/run', '/var/lib', '/opt'
        ]
        self.safe_personal_paths = [
            '/home', '/tmp', '/var/tmp', '/media', '/mnt',
            '/home/*/.cache', '/home/*/.local', '/home/*/Downloads',
            '/home/*/Documents', '/home/*/Pictures', '/home/*/Videos'
        ]
    
    def is_system_drive(self, device_path):
        """Check if device contains the operating system"""
        try:
            # Check if root filesystem is on this device
            result = subprocess.run(['df', '/'], capture_output=True, text=True)
            root_device = result.stdout.split('\n')[1].split()[0]
            
            # Extract base device name (remove partition numbers)
            root_base = re.sub(r'\d+$', '', root_device.replace('/dev/', ''))
            device_base = re.sub(r'\d+$', '', device_path.replace('/dev/', ''))
            
            if root_base == device_base:
                return True, f"Device {device_path} contains the root filesystem"
            
            # Check if boot partition is on this device
            result = subprocess.run(['df', '/boot'], capture_output=True, text=True)
            if result.returncode == 0:
                boot_device = result.stdout.split('\n')[1].split()[0]
                boot_base = re.sub(r'\d+$', '', boot_device.replace('/dev/', ''))
                if boot_base == device_base:
                    return True, f"Device {device_path} contains the boot partition"
            
            return False, "Device appears to be safe"
            
        except Exception as e:
            return True, f"Cannot verify device safety: {e}"
    
    def get_mounted_partitions(self, device_path):
        """Get all mounted partitions on a device"""
        mounted = []
        try:
            device_base = device_path.replace('/dev/', '')
            
            for partition in psutil.disk_partitions():
                if device_base in partition.device:
                    mounted.append({
                        'device': partition.device,
                        'mountpoint': partition.mountpoint,
                        'fstype': partition.fstype
                    })
            
            return mounted
        except Exception as e:
            return []
    
    def is_safe_for_wiping(self, device_path):
        """Comprehensive safety check for device wiping"""
        checks = {
            'is_system_drive': False,
            'has_mounted_system': False,
            'has_important_data': False,
            'warnings': []
        }
        
        # Check if it's the system drive
        is_sys, sys_msg = self.is_system_drive(device_path)
        if is_sys:
            checks['is_system_drive'] = True
            checks['warnings'].append(f"🚨 SYSTEM DRIVE: {sys_msg}")
        
        # Check mounted partitions
        mounted = self.get_mounted_partitions(device_path)
        for mount in mounted:
            mountpoint = mount['mountpoint']
            
            # Check for system mountpoints
            if mountpoint in ['/', '/boot', '/usr', '/var', '/etc']:
                checks['has_mounted_system'] = True
                checks['warnings'].append(f"🚨 SYSTEM MOUNT: {mount['device']} mounted at {mountpoint}")
            
            # Check for important data
            if mountpoint.startswith('/home'):
                checks['has_important_data'] = True
                checks['warnings'].append(f"⚠️  USER DATA: {mount['device']} contains user data at {mountpoint}")
        
        # Overall safety assessment
        checks['safe'] = not (checks['is_system_drive'] or checks['has_mounted_system'])
        
        return checks

class PersonalDataWiper:
    """Safely wipes only personal data, preserving OS"""
    
    def __init__(self):
        self.personal_data_locations = [
            '/home/*/Documents',
            '/home/*/Downloads', 
            '/home/*/Pictures',
            '/home/*/Videos',
            '/home/*/Music',
            '/home/*/Desktop',
            '/home/*/.cache',
            '/home/*/.local/share',
            '/home/*/.config/chromium',
            '/home/*/.mozilla',
            '/home/*/.thunderbird',
            '/tmp/*',
            '/var/tmp/*',
            '/var/log/user.log*',
            '/var/spool/mail/*'
        ]
        
        self.browser_data_locations = [
            '/home/*/.config/google-chrome',
            '/home/*/.config/chromium', 
            '/home/*/.mozilla/firefox',
            '/home/*/.config/opera',
            '/home/*/.cache/mozilla',
            '/home/*/.cache/google-chrome',
            '/home/*/.cache/chromium'
        ]
    
    def get_personal_files(self):
        """Get list of all personal data files"""
        files_to_wipe = []
        
        for pattern in self.personal_data_locations:
            try:
                matches = subprocess.run(['find', '/', '-path', pattern, '-type', 'f'], 
                                      capture_output=True, text=True)
                if matches.returncode == 0:
                    files_to_wipe.extend(matches.stdout.strip().split('\n'))
            except Exception:
                continue
        
        return [f for f in files_to_wipe if f and os.path.exists(f)]
    
    def wipe_personal_data(self, method='zeros', passes=3):
        """Wipe only personal data files"""
        files = self.get_personal_files()
        
        wiped_files = []
        errors = []
        
        for file_path in files:
            try:
                if method == 'zeros':
                    # Overwrite file with zeros
                    with open(file_path, 'r+b') as f:
                        size = os.path.getsize(file_path)
                        f.write(b'\x00' * size)
                        f.flush()
                        os.fsync(f.fileno())
                
                # Remove the file
                os.remove(file_path)
                wiped_files.append(file_path)
                
            except Exception as e:
                errors.append(f"{file_path}: {e}")
        
        return wiped_files, errors
    
    def factory_reset_user_data(self):
        """Reset system to factory state while preserving OS"""
        actions_taken = []
        
        # 1. Remove user accounts (except root and system users)
        try:
            users = subprocess.run(['cat', '/etc/passwd'], capture_output=True, text=True)
            for line in users.stdout.split('\n'):
                if ':' in line:
                    parts = line.split(':')
                    username = parts[0]
                    uid = int(parts[2]) if parts[2].isdigit() else 0
                    
                    # Remove non-system users (UID >= 1000)
                    if uid >= 1000 and username not in ['nobody']:
                        subprocess.run(['userdel', '-r', username], capture_output=True)
                        actions_taken.append(f"Removed user: {username}")
        except Exception as e:
            actions_taken.append(f"Error removing users: {e}")
        
        # 2. Clear temporary files
        temp_dirs = ['/tmp', '/var/tmp', '/var/cache']
        for temp_dir in temp_dirs:
            try:
                subprocess.run(['find', temp_dir, '-type', 'f', '-delete'], capture_output=True)
                actions_taken.append(f"Cleared: {temp_dir}")
            except Exception:
                pass
        
        # 3. Clear log files
        try:
            subprocess.run(['find', '/var/log', '-name', '*.log', '-exec', 'truncate', '-s', '0', '{}', ';'], 
                         capture_output=True)
            actions_taken.append("Cleared log files")
        except Exception:
            pass
        
        # 4. Reset network settings
        try:
            network_files = [
                '/etc/NetworkManager/system-connections/*',
                '/etc/wpa_supplicant/*'
            ]
            for pattern in network_files:
                subprocess.run(['rm', '-f'] + pattern.split(), capture_output=True)
            actions_taken.append("Reset network settings")
        except Exception:
            pass
        
        return actions_taken

# Update the main safety check
def perform_safety_check(device_path):
    """Perform comprehensive safety check before any operation"""
    safety = SafetyManager()
    checks = safety.is_safe_for_wiping(device_path)
    
    print("🔒 SAFETY CHECK RESULTS:")
    print("=" * 50)
    
    if checks['safe']:
        print("✅ DEVICE IS SAFE FOR WIPING")
    else:
        print("🚨 DANGER! DEVICE IS NOT SAFE!")
    
    for warning in checks['warnings']:
        print(f"   {warning}")
    
    print()
    return checks['safe']

if __name__ == "__main__":
    # Test safety checks
    import sys
    
    if len(sys.argv) > 1:
        device = sys.argv[1]
        safe = perform_safety_check(device)
        
        if not safe:
            print("🚨 WIPING BLOCKED FOR SAFETY!")
        else:
            print("✅ Safe to proceed with wiping")
    else:
        print("Usage: python3 safety_manager.py /dev/sdX")
