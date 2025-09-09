# TrustWipe - VMware Linux Setup Guide

## 🚀 Quick Start for VMware Linux

This guide will help you set up and use TrustWipe on your VMware Linux environment.

### Step 1: Transfer Files to Linux

1. **Copy the entire TrustWipe-Linux folder** to your VMware Linux system
2. You can use:
   - Shared folders between Windows host and Linux guest
   - SCP/SFTP transfer
   - USB drive or CD/DVD
   - Network file sharing

### Step 2: Install TrustWipe

Open terminal in your Linux VM and run:

```bash
# Navigate to TrustWipe directory
cd /path/to/TrustWipe-Linux

# Make scripts executable
chmod +x *.sh

# Run the installer (requires root)
sudo ./install.sh
```

The installer will:
- Install Python dependencies
- Set up system utilities
- Create application directories
- Install executables globally
- Set up certificate storage
- Create desktop entries

### Step 3: Launch TrustWipe

#### GUI Mode (Recommended)
```bash
sudo trustwipe
```

#### CLI Mode
```bash
# Show help
trustwipe-cli --help

# List available devices
trustwipe-cli --list-devices

# Show device information
trustwipe-cli --device-info /dev/sdb

# Wipe device (DESTRUCTIVE!)
sudo trustwipe-cli --wipe /dev/sdb --method zeros
```

## 🔧 VMware-Specific Considerations

### Virtual Disk Setup
1. **Add a test virtual disk** to your VM for safe testing
2. **Use small test disks** (1-5 GB) for initial testing
3. **Never test on your main system disk** (/dev/sda)

### VM Configuration
- Ensure VM has sufficient RAM (2GB+ recommended)
- Grant necessary privileges to the VM
- Enable disk operations in VMware settings

### Safety in VMware
- **Take VM snapshots** before testing
- **Use dedicated test VMs** for destructive operations
- **Test with disposable virtual disks** first

## 📋 Testing Procedure

### 1. Create Test Environment
```bash
# Create a test file (simulate a small disk)
sudo dd if=/dev/zero of=/tmp/test_disk bs=1M count=100
# Creates 100MB test file

# Create loop device
sudo losetup /dev/loop0 /tmp/test_disk
```

### 2. Test TrustWipe
```bash
# Test with the loop device (safe)
sudo trustwipe-cli --device-info /dev/loop0
sudo trustwipe-cli --wipe /dev/loop0 --method zeros --passes 1
```

### 3. Cleanup
```bash
# Remove loop device
sudo losetup -d /dev/loop0
rm /tmp/test_disk
```

## 🛡️ Production Usage

### Adding Virtual Disks for Wiping
1. **Power off** the VM
2. **Add new virtual disk** in VMware settings
3. **Power on** the VM
4. **Identify the new disk** using `lsblk` or `fdisk -l`
5. **Wipe the disk** using TrustWipe

### Example: Wiping a USB Drive in VM
```bash
# Insert USB drive and pass through to VM
# Identify the device
lsblk

# Show device information
trustwipe-cli --device-info /dev/sdc

# Wipe with multiple confirmations
sudo trustwipe-cli --wipe /dev/sdc --method dod
```

## 📜 Certificate Management

### Certificate Locations
- Primary: `/boot/trustwipe-certificates/`
- Fallback: `/tmp/trustwipe-certificates/`

### Viewing Certificates
```bash
# List all certificates
trustwipe-cli --list-certs

# Show specific certificate
trustwipe-cli --show-cert 12345678

# Open certificate directory
sudo nautilus /boot/trustwipe-certificates/
```

### Certificate Backup
```bash
# Backup certificates
sudo tar -czf certificates-backup.tar.gz /boot/trustwipe-certificates/

# Copy to shared folder or external storage
cp certificates-backup.tar.gz /mnt/shared/
```

## 🔍 Troubleshooting

### Common Issues

#### Permission Denied
```bash
# Ensure running as root
sudo trustwipe
sudo trustwipe-cli --wipe /dev/sdb
```

#### Python Dependencies Missing
```bash
# Install missing packages
sudo apt-get update
sudo apt-get install python3 python3-tk python3-pip
pip3 install psutil
```

#### GUI Not Working
```bash
# Check X11 forwarding (if using SSH)
ssh -X user@linux-vm

# Install GUI packages
sudo apt-get install python3-tk

# Test GUI availability
python3 -c "import tkinter; tkinter.Tk()"
```

#### Device Not Found
```bash
# List all block devices
lsblk -a

# Check device permissions
ls -la /dev/sd*

# Refresh device list
sudo partprobe
```

### Log Files
Check logs for debugging:
```bash
# Application logs
sudo tail -f /var/log/trustwipe/wipe_*.log

# System logs
sudo journalctl -f -u trustwipe
```

## ⚠️ Safety Checklist

Before wiping ANY device:

- [ ] **Verify target device** with `lsblk` and `fdisk -l`
- [ ] **Confirm device is unmounted** 
- [ ] **Check device contents** are disposable
- [ ] **Have backups** of any important data
- [ ] **Test with non-critical device** first
- [ ] **Take VM snapshot** if testing in VMware
- [ ] **Use correct wiping method** for your needs
- [ ] **Allow sufficient time** for operation
- [ ] **Monitor progress** during operation

## 🎯 Quick Commands Reference

```bash
# Installation
sudo ./install.sh

# GUI Launch
sudo trustwipe

# Device Discovery
trustwipe-cli --list-devices
trustwipe-cli --device-info /dev/sdb

# Wiping Operations
sudo trustwipe-cli --wipe /dev/sdb --method zeros    # Fast
sudo trustwipe-cli --wipe /dev/sdb --method random   # Secure
sudo trustwipe-cli --wipe /dev/sdb --method dod      # Military
sudo trustwipe-cli --wipe /dev/sdb --method gutmann  # Maximum

# Certificate Management
trustwipe-cli --list-certs
trustwipe-cli --show-cert 12345678

# Testing
python3 demo.py
python3 test_trustwipe.py

# Uninstall
sudo /opt/trustwipe/uninstall.sh
```

## 📞 Support

If you encounter issues:

1. **Check logs**: `/var/log/trustwipe/`
2. **Run tests**: `python3 test_trustwipe.py`
3. **Check demo**: `python3 demo.py`
4. **Verify setup**: Run installer again
5. **Review documentation**: `README.md`, `SECURITY.md`

## 🏁 You're Ready!

TrustWipe is now installed and ready to use on your VMware Linux system. Remember to:

- **Always test with non-critical data first**
- **Verify target devices carefully**
- **Keep certificates for compliance**
- **Use appropriate security levels**

**Happy and Safe Wiping! 🛡️**
