# TrustWipe - Secure Data Wiping Tool

A comprehensive Linux data wiping application with GUI frontend and Python backend that securely erases data and generates certificates.

## Features

- 🔒 Secure data wiping using `dd` and `shred` commands
- 🖥️ User-friendly GUI interface built with Tkinter
- 📜 Certificate generation after successful data wiping
- 🛡️ Multiple wiping algorithms (zeros, random, DoD patterns)
- 📊 Real-time progress monitoring
- 🔍 System information collection
- 💾 Certificate stored in persistent location (/boot or /root)

## Requirements

- Linux OS (tested on Ubuntu, CentOS, Debian)
- Python 3.6+
- Root privileges for disk operations
- tkinter for GUI (usually pre-installed)

## Installation

```bash
# Clone the repository
git clone https://github.com/your-repo/TrustWipe-Linux
cd TrustWipe-Linux

# Make the installer executable
chmod +x install.sh
sudo ./install.sh

# Or run directly
chmod +x trustwipe.py
sudo python3 trustwipe.py
```

## Usage

1. Run with root privileges: `sudo python3 trustwipe.py`
2. Select the drive/partition to wipe
3. Choose wiping algorithm
4. Confirm the operation
5. Monitor progress
6. Certificate will be generated in `/boot/trustwipe-certificates/`

## Safety Features

- Multiple confirmation dialogs
- Drive information display
- Progress monitoring
- Error handling and logging
- Certificate generation for audit trail

## Certificate Details

After successful wiping, a certificate is generated containing:
- System information (OS, kernel, hardware)
- Timestamp of operation
- Drive details
- Wiping algorithm used
- Digital signature (optional)

## Warning

⚠️ **DESTRUCTIVE OPERATION**: This tool permanently erases data. Use with extreme caution!
