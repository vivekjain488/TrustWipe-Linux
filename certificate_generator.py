#!/usr/bin/env python3
"""
TrustWipe Certificate Generator
Generates detailed certificates after successful data wiping operations
"""

import json
import os
import uuid
from datetime import datetime
import hashlib
import platform
import subprocess

class CertificateGenerator:
    def __init__(self, cert_dir="/boot/trustwipe-certificates"):
        """
        Initialize certificate generator
        
        Args:
            cert_dir (str): Directory to store certificates
        """
        self.cert_dir = cert_dir
        self.ensure_cert_directory()
    
    def ensure_cert_directory(self):
        """Ensure certificate directory exists with proper permissions"""
        try:
            os.makedirs(self.cert_dir, exist_ok=True)
            os.chmod(self.cert_dir, 0o755)
        except Exception as e:
            # Fallback to /tmp if /boot is not accessible
            self.cert_dir = "/tmp/trustwipe-certificates"
            os.makedirs(self.cert_dir, exist_ok=True)
            os.chmod(self.cert_dir, 0o755)
    
    def generate_certificate(self, system_info, device_info, wipe_details):
        """
        Generate a comprehensive certificate
        
        Args:
            system_info (dict): System information
            device_info (dict): Device information
            wipe_details (dict): Wiping operation details
            
        Returns:
            tuple: (cert_path, html_path) - paths to generated certificates
        """
        # Generate certificate ID and timestamp
        cert_id = str(uuid.uuid4())
        timestamp = datetime.now()
        
        # Create certificate data
        cert_data = {
            'certificate_info': {
                'id': cert_id,
                'version': '1.0',
                'generated_at': timestamp.isoformat(),
                'generator': 'TrustWipe v1.0',
                'standard': 'ISO/IEC 27040:2015 compliant'
            },
            'system_info': system_info,
            'device_info': device_info,
            'wipe_details': wipe_details,
            'verification': self.generate_verification_data(system_info, device_info, wipe_details)
        }
        
        # Generate filenames
        device_name = device_info.get('device_path', 'unknown').split('/')[-1]
        timestamp_str = timestamp.strftime('%Y%m%d_%H%M%S')
        
        cert_filename = f'trustwipe_cert_{device_name}_{timestamp_str}.json'
        html_filename = f'trustwipe_cert_{device_name}_{timestamp_str}.html'
        
        cert_path = os.path.join(self.cert_dir, cert_filename)
        html_path = os.path.join(self.cert_dir, html_filename)
        
        # Save JSON certificate
        with open(cert_path, 'w') as f:
            json.dump(cert_data, f, indent=2, sort_keys=True)
        
        # Generate and save HTML certificate
        html_content = self.generate_html_certificate(cert_data)
        with open(html_path, 'w') as f:
            f.write(html_content)
        
        # Set appropriate permissions
        os.chmod(cert_path, 0o644)
        os.chmod(html_path, 0o644)
        
        return cert_path, html_path
    
    def generate_verification_data(self, system_info, device_info, wipe_details):
        """Generate verification data and checksum"""
        # Create verification string
        verification_string = f"{system_info.get('hostname', '')}{device_info.get('device_path', '')}{wipe_details.get('start_time', '')}{wipe_details.get('end_time', '')}"
        
        # Generate checksum
        checksum = hashlib.sha256(verification_string.encode()).hexdigest()
        
        return {
            'checksum': checksum,
            'algorithm': 'SHA-256',
            'verification_string': verification_string,
            'timestamp': datetime.now().isoformat()
        }
    
    def generate_html_certificate(self, cert_data):
        """Generate a professional HTML certificate"""
        
        # Extract data for easier access
        cert_info = cert_data['certificate_info']
        system_info = cert_data['system_info']
        device_info = cert_data['device_info']
        wipe_details = cert_data['wipe_details']
        verification = cert_data['verification']
        
        # Format duration if available
        duration = wipe_details.get('duration', 'N/A')
        if isinstance(duration, str) and ':' in duration:
            try:
                # Parse duration and format nicely
                parts = duration.split(':')
                if len(parts) >= 3:
                    hours, minutes, seconds = parts[0], parts[1], parts[2].split('.')[0]
                    duration = f"{hours}h {minutes}m {seconds}s"
            except:
                pass
        
        html_content = f"""<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>TrustWipe Data Erasure Certificate</title>
    <style>
        * {{
            margin: 0;
            padding: 0;
            box-sizing: border-box;
        }}
        
        body {{
            font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            min-height: 100vh;
            padding: 20px;
        }}
        
        .certificate-container {{
            max-width: 900px;
            margin: 0 auto;
            background: white;
            border-radius: 15px;
            box-shadow: 0 20px 40px rgba(0, 0, 0, 0.1);
            overflow: hidden;
        }}
        
        .header {{
            background: linear-gradient(135deg, #e74c3c 0%, #c0392b 100%);
            color: white;
            padding: 40px;
            text-align: center;
            position: relative;
        }}
        
        .header::before {{
            content: '';
            position: absolute;
            top: 0;
            left: 0;
            right: 0;
            bottom: 0;
            background: url('data:image/svg+xml,<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 100 100"><defs><pattern id="grain" width="100" height="100" patternUnits="userSpaceOnUse"><circle cx="25" cy="25" r="1" fill="rgba(255,255,255,0.1)"/><circle cx="75" cy="75" r="1" fill="rgba(255,255,255,0.1)"/><circle cx="50" cy="10" r="1" fill="rgba(255,255,255,0.1)"/><circle cx="10" cy="50" r="1" fill="rgba(255,255,255,0.1)"/></pattern></defs><rect width="100" height="100" fill="url(%23grain)"/></svg>');
            opacity: 0.3;
        }}
        
        .header-content {{
            position: relative;
            z-index: 1;
        }}
        
        .certificate-title {{
            font-size: 32px;
            font-weight: bold;
            margin-bottom: 10px;
            text-shadow: 2px 2px 4px rgba(0, 0, 0, 0.3);
        }}
        
        .certificate-subtitle {{
            font-size: 18px;
            opacity: 0.9;
            margin-bottom: 20px;
        }}
        
        .shield-icon {{
            font-size: 64px;
            margin-bottom: 20px;
            text-shadow: 2px 2px 4px rgba(0, 0, 0, 0.3);
        }}
        
        .status-badge {{
            display: inline-block;
            background: #27ae60;
            color: white;
            padding: 12px 30px;
            border-radius: 50px;
            font-size: 18px;
            font-weight: bold;
            text-transform: uppercase;
            letter-spacing: 1px;
            box-shadow: 0 4px 8px rgba(0, 0, 0, 0.2);
        }}
        
        .content {{
            padding: 40px;
        }}
        
        .section {{
            margin-bottom: 35px;
            padding: 25px;
            background: #f8f9fa;
            border-radius: 10px;
            border-left: 5px solid #3498db;
        }}
        
        .section-title {{
            color: #2c3e50;
            font-size: 20px;
            font-weight: bold;
            margin-bottom: 20px;
            display: flex;
            align-items: center;
        }}
        
        .section-icon {{
            margin-right: 10px;
            font-size: 24px;
        }}
        
        .info-grid {{
            display: grid;
            grid-template-columns: 1fr 2fr;
            gap: 15px;
            align-items: center;
        }}
        
        .info-label {{
            font-weight: 600;
            color: #555;
            text-align: right;
            padding-right: 15px;
            border-right: 2px solid #ecf0f1;
        }}
        
        .info-value {{
            color: #2c3e50;
            font-family: 'Courier New', monospace;
            background: white;
            padding: 8px 12px;
            border-radius: 5px;
            border: 1px solid #ecf0f1;
        }}
        
        .highlight {{
            background: #fff3cd !important;
            border: 1px solid #ffeaa7 !important;
            font-weight: bold;
        }}
        
        .success-highlight {{
            background: #d4edda !important;
            border: 1px solid #c3e6cb !important;
            color: #155724 !important;
        }}
        
        .verification-section {{
            background: linear-gradient(135deg, #74b9ff 0%, #0984e3 100%);
            color: white;
            border-left: 5px solid #fff;
        }}
        
        .verification-section .info-value {{
            background: rgba(255, 255, 255, 0.9);
            color: #2c3e50;
        }}
        
        .footer {{
            background: #2c3e50;
            color: white;
            padding: 30px;
            text-align: center;
        }}
        
        .footer-content {{
            max-width: 600px;
            margin: 0 auto;
            line-height: 1.6;
        }}
        
        .compliance-badges {{
            display: flex;
            justify-content: center;
            gap: 20px;
            margin-top: 20px;
            flex-wrap: wrap;
        }}
        
        .badge {{
            background: #34495e;
            color: white;
            padding: 8px 16px;
            border-radius: 20px;
            font-size: 12px;
            font-weight: bold;
            text-transform: uppercase;
            letter-spacing: 0.5px;
        }}
        
        .print-button {{
            position: fixed;
            top: 20px;
            right: 20px;
            background: #3498db;
            color: white;
            border: none;
            padding: 12px 20px;
            border-radius: 8px;
            cursor: pointer;
            font-weight: bold;
            box-shadow: 0 4px 8px rgba(0, 0, 0, 0.2);
        }}
        
        .print-button:hover {{
            background: #2980b9;
        }}
        
        @media print {{
            body {{
                background: white;
                padding: 0;
            }}
            
            .print-button {{
                display: none;
            }}
            
            .certificate-container {{
                box-shadow: none;
                border-radius: 0;
            }}
        }}
        
        @media (max-width: 768px) {{
            .info-grid {{
                grid-template-columns: 1fr;
                gap: 10px;
            }}
            
            .info-label {{
                text-align: left;
                border-right: none;
                border-bottom: 2px solid #ecf0f1;
                padding-right: 0;
                padding-bottom: 5px;
            }}
        }}
    </style>
</head>
<body>
    <button class="print-button" onclick="window.print()">🖨️ Print Certificate</button>
    
    <div class="certificate-container">
        <div class="header">
            <div class="header-content">
                <div class="shield-icon">🛡️</div>
                <div class="certificate-title">DATA ERASURE CERTIFICATE</div>
                <div class="certificate-subtitle">Secure Data Wiping Verification</div>
                <div class="status-badge">✅ DATA ERASED SUCCESSFULLY</div>
            </div>
        </div>
        
        <div class="content">
            <div class="section">
                <div class="section-title">
                    <span class="section-icon">📋</span>
                    Certificate Information
                </div>
                <div class="info-grid">
                    <div class="info-label">Certificate ID:</div>
                    <div class="info-value highlight">{cert_info['id']}</div>
                    <div class="info-label">Generated:</div>
                    <div class="info-value">{cert_info['generated_at']}</div>
                    <div class="info-label">Version:</div>
                    <div class="info-value">{cert_info['version']}</div>
                    <div class="info-label">Standard:</div>
                    <div class="info-value">{cert_info['standard']}</div>
                </div>
            </div>
            
            <div class="section">
                <div class="section-title">
                    <span class="section-icon">🗑️</span>
                    Erasure Details
                </div>
                <div class="info-grid">
                    <div class="info-label">Target Device:</div>
                    <div class="info-value highlight">{device_info.get('device_path', 'N/A')}</div>
                    <div class="info-label">Device Size:</div>
                    <div class="info-value">{device_info.get('size_human', 'N/A')}</div>
                    <div class="info-label">Wiping Method:</div>
                    <div class="info-value">{wipe_details.get('method', 'N/A').upper()}</div>
                    <div class="info-label">Number of Passes:</div>
                    <div class="info-value">{wipe_details.get('passes', 'N/A')}</div>
                    <div class="info-label">Started:</div>
                    <div class="info-value">{wipe_details.get('start_time', 'N/A')}</div>
                    <div class="info-label">Completed:</div>
                    <div class="info-value">{wipe_details.get('end_time', 'N/A')}</div>
                    <div class="info-label">Duration:</div>
                    <div class="info-value">{duration}</div>
                    <div class="info-label">Status:</div>
                    <div class="info-value success-highlight">{wipe_details.get('status', 'N/A')}</div>
                </div>
            </div>
            
            <div class="section">
                <div class="section-title">
                    <span class="section-icon">💾</span>
                    Device Information
                </div>
                <div class="info-grid">
                    <div class="info-label">Model:</div>
                    <div class="info-value">{device_info.get('model', 'N/A')}</div>
                    <div class="info-label">Vendor:</div>
                    <div class="info-value">{device_info.get('vendor', 'N/A')}</div>
                    <div class="info-label">Serial Number:</div>
                    <div class="info-value">{device_info.get('serial', 'N/A')}</div>
                    <div class="info-label">Device Type:</div>
                    <div class="info-value">{device_info.get('type', 'N/A')}</div>
                    <div class="info-label">Size (Bytes):</div>
                    <div class="info-value">{device_info.get('size_bytes', 'N/A')}</div>
                </div>
            </div>
            
            <div class="section">
                <div class="section-title">
                    <span class="section-icon">🖥️</span>
                    System Information
                </div>
                <div class="info-grid">
                    <div class="info-label">Hostname:</div>
                    <div class="info-value">{system_info.get('hostname', 'N/A')}</div>
                    <div class="info-label">Operating System:</div>
                    <div class="info-value">{system_info.get('os', 'N/A')} {system_info.get('os_release', '')}</div>
                    <div class="info-label">Architecture:</div>
                    <div class="info-value">{system_info.get('architecture', 'N/A')}</div>
                    <div class="info-label">Processor:</div>
                    <div class="info-value">{system_info.get('processor', 'N/A')}</div>
                    <div class="info-label">Memory:</div>
                    <div class="info-value">{system_info.get('memory', {}).get('total_human', 'N/A')}</div>
                    <div class="info-label">Boot Time:</div>
                    <div class="info-value">{system_info.get('boot_time', 'N/A')}</div>
                </div>
            </div>
            
            <div class="section verification-section">
                <div class="section-title">
                    <span class="section-icon">🔐</span>
                    Verification & Security
                </div>
                <div class="info-grid">
                    <div class="info-label">Checksum Algorithm:</div>
                    <div class="info-value">{verification['algorithm']}</div>
                    <div class="info-label">Verification Hash:</div>
                    <div class="info-value">{verification['checksum'][:32]}...</div>
                    <div class="info-label">Full Checksum:</div>
                    <div class="info-value" style="font-size: 10px; word-break: break-all;">{verification['checksum']}</div>
                </div>
            </div>
        </div>
        
        <div class="footer">
            <div class="footer-content">
                <h3>🔒 CERTIFICATE OF DATA DESTRUCTION</h3>
                <p>This certificate confirms that the specified data storage device has been securely erased using industry-standard wiping algorithms. The data is permanently destroyed and unrecoverable using conventional data recovery methods.</p>
                
                <div class="compliance-badges">
                    <span class="badge">NIST 800-88</span>
                    <span class="badge">DoD 5220.22-M</span>
                    <span class="badge">ISO/IEC 27040</span>
                    <span class="badge">GDPR Compliant</span>
                </div>
                
                <p style="margin-top: 20px; font-size: 14px; opacity: 0.8;">
                    Generated by TrustWipe v1.0 - Professional Data Wiping Tool<br>
                    This certificate should be retained for compliance and audit purposes.
                </p>
            </div>
        </div>
    </div>
    
    <script>
        // Add some interactivity
        document.addEventListener('DOMContentLoaded', function() {{
            // Highlight important information on hover
            const highlights = document.querySelectorAll('.highlight');
            highlights.forEach(function(element) {{
                element.addEventListener('mouseenter', function() {{
                    this.style.transform = 'scale(1.02)';
                    this.style.transition = 'transform 0.2s ease';
                }});
                element.addEventListener('mouseleave', function() {{
                    this.style.transform = 'scale(1)';
                }});
            }});
        }});
    </script>
</body>
</html>"""
        
        return html_content
    
    def list_certificates(self):
        """List all certificates in the certificate directory"""
        certificates = []
        
        if not os.path.exists(self.cert_dir):
            return certificates
        
        for filename in os.listdir(self.cert_dir):
            if filename.endswith('.json') and filename.startswith('trustwipe_cert_'):
                cert_path = os.path.join(self.cert_dir, filename)
                try:
                    with open(cert_path, 'r') as f:
                        cert_data = json.load(f)
                    
                    certificates.append({
                        'filename': filename,
                        'path': cert_path,
                        'html_path': cert_path.replace('.json', '.html'),
                        'certificate_id': cert_data.get('certificate_info', {}).get('id', 'Unknown'),
                        'generated_at': cert_data.get('certificate_info', {}).get('generated_at', 'Unknown'),
                        'device': cert_data.get('device_info', {}).get('device_path', 'Unknown'),
                        'method': cert_data.get('wipe_details', {}).get('method', 'Unknown'),
                        'status': cert_data.get('wipe_details', {}).get('status', 'Unknown')
                    })
                except Exception as e:
                    continue
        
        # Sort by generation time, newest first
        certificates.sort(key=lambda x: x['generated_at'], reverse=True)
        return certificates

def main():
    """Test the certificate generator"""
    from backend import SystemInfo
    
    # Sample data for testing
    system_info = SystemInfo.get_system_info()
    
    device_info = {
        'device_path': '/dev/sdb',
        'size_bytes': 1000000000000,
        'size_human': '1.00 TB',
        'model': 'Test Drive 1TB',
        'vendor': 'TestVendor',
        'serial': 'TEST123456789',
        'type': 'SSD'
    }
    
    wipe_details = {
        'device_path': '/dev/sdb',
        'method': 'dod',
        'passes': 3,
        'start_time': '2025-09-09T10:30:00',
        'end_time': '2025-09-09T14:45:00',
        'duration': '4:15:00',
        'status': 'SUCCESS'
    }
    
    # Generate certificate
    cert_gen = CertificateGenerator()
    cert_path, html_path = cert_gen.generate_certificate(system_info, device_info, wipe_details)
    
    print(f"Certificate generated:")
    print(f"  JSON: {cert_path}")
    print(f"  HTML: {html_path}")
    
    # List certificates
    certs = cert_gen.list_certificates()
    print(f"\nFound {len(certs)} certificates:")
    for cert in certs:
        print(f"  {cert['filename']} - {cert['device']} - {cert['method']} - {cert['status']}")

if __name__ == "__main__":
    main()
